"""Read-only recording hook for the covariate_labels generator (irw#1775).

`harvest.py` puts this directory on PYTHONPATH when it runs a `data/` script,
so Python imports it before the script starts. It changes nothing the script
computes. It records, as JSON lines in $COVLAB_LOG:

* ``read``: every SPSS/Stata/SAS file the script opens through pyreadstat or
  ``pandas.read_spss``/``read_stata``, with each column's value labels and,
  for labelled columns, how many source rows carry each code. The counts are
  what lets ``build.py`` notice a covariate the script recoded before shipping
  (a 1/2 swap leaves the shipped values inside the labelled codes, but moves
  the counts).
* ``write``: every DataFrame the script writes with ``to_csv``, with each
  ``cov_*`` column's dtype, its distinct values, and how many distinct ``id``s
  carry each value (row counts when there is no ``id`` column).

It also refuses to import ``redivis`` and ``red_up``: a script run under the
harvest must never be able to upload anything.

Adapted from the 2026-09-27 survey hook in irw/oneoff/1775-value-labels/.
"""
import importlib.abc
import json
import os
import sys

LOG = os.environ.get("COVLAB_LOG")
MAX_VALUES = 500  # a covariate with more distinct values than this is not a coded categorical


def _emit(rec):
    if not LOG:
        return
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
    except Exception:
        pass


def norm(v):
    """Codes as strings, the same way build.py does: 1.0 -> "1"."""
    s = str(v).strip()
    try:
        f = float(s)
        if f == int(f):
            return str(int(f))
        return s
    except (ValueError, OverflowError):
        return s


# --- block uploads ---------------------------------------------------------
class _NoUpload(importlib.abc.MetaPathFinder):
    BLOCKED = ("redivis", "red_up")

    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in self.BLOCKED:
            _emit({"ev": "blocked_import", "module": name})
            raise ImportError(f"{name} is blocked while harvesting covariate labels (irw#1775)")
        return None


sys.meta_path.insert(0, _NoUpload())


# --- source reads ----------------------------------------------------------
def _labels(meta):
    vvl = getattr(meta, "variable_value_labels", {}) or {}
    return {col: {norm(a): str(b) for a, b in lv.items()} for col, lv in vvl.items()}


def _counts(df, labels):
    """Rows per code for each labelled column. Values that come back already
    formatted (label strings, from apply_value_formats or pandas'
    convert_categoricals) are mapped back to their code."""
    out = {}
    if df is None:
        return out
    for col, lv in labels.items():
        if col not in getattr(df, "columns", []):
            continue
        try:
            inv = {}
            for code, lab in lv.items():
                inv.setdefault(lab, code)
            vc = df[col].dropna().astype(object).value_counts()
            c = {}
            for v, n in vc.items():
                k = inv.get(str(v), norm(v)) if isinstance(v, str) else norm(v)
                c[k] = c.get(k, 0) + int(n)
            out[col] = c
        except Exception as e:
            _emit({"ev": "hook_error", "where": "counts", "col": col, "err": repr(e)})
    return out


def _record(kind, path, meta, df):
    try:
        labels = _labels(meta)
        cols = list(getattr(meta, "column_names", None) or getattr(df, "columns", []) or [])
        _emit({"ev": "read", "kind": kind, "path": str(path), "columns": [str(c) for c in cols],
               "value_labels": labels, "counts": _counts(df, labels)})
    except Exception as e:  # never break the script
        _emit({"ev": "hook_error", "where": kind, "err": repr(e)})


_ORIG = {}
try:
    import pyreadstat as _prs

    for _name in ("read_sav", "read_dta", "read_por", "read_sas7bdat", "read_xport"):
        _orig = getattr(_prs, _name, None)
        if _orig is None:
            continue
        _ORIG[_name] = _orig

        def _wrap(*a, _orig=_orig, _name=_name, **k):
            out = _orig(*a, **k)
            if isinstance(out, tuple) and len(out) == 2:
                _record(_name, a[0] if a else k.get("filename_path"), out[1], out[0])
            return out

        setattr(_prs, _name, _wrap)
except Exception:
    pass


def _meta_only(path, reader, data=None):
    """Metadata through the unwrapped pyreadstat reader (no double logging).
    File-like sources are passed as `data`, the bytes captured before the
    script's own reader consumed the buffer, and go through a temp file."""
    orig = _ORIG.get(reader)
    if orig is None:
        return None
    if isinstance(path, (str, os.PathLike)):
        return orig(str(path), metadataonly=True)[1]
    if data is None:
        raise ValueError("buffer source with no captured bytes")
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav" if reader == "read_sav" else ".dta",
                                     delete=False) as fh:
        fh.write(data)
    try:
        return orig(fh.name, metadataonly=True)[1]
    finally:
        os.unlink(fh.name)


try:
    import pandas as _pd

    class _Meta:
        def __init__(self, labels, columns):
            self.variable_value_labels = labels
            self.column_names = columns

    def _stata_meta_pandas(src):
        """Value labels through pandas' own Stata reader, for files pyreadstat
        cannot open (older .dta format versions)."""
        import io
        with _pd.io.stata.StataReader(io.BytesIO(src) if isinstance(src, bytes) else src) as rd:
            sets = rd.value_labels()
            rd._ensure_open() if hasattr(rd, "_ensure_open") else None
            lbl = dict(zip(rd._varlist, rd._lbllist))
        return _Meta({v: sets[n] for v, n in lbl.items() if n and n in sets}, list(lbl))

    def _pandas_wrap(orig, reader):
        def inner(path, *a, **k):
            raw = None
            if hasattr(path, "read") and hasattr(path, "tell"):
                try:
                    pos = path.tell()
                    raw = path.read()
                    path.seek(pos)
                except Exception:
                    raw = None
            df = orig(path, *a, **k)
            try:
                if hasattr(df, "columns"):  # not an iterator/chunked reader
                    try:
                        meta = _meta_only(path, reader, raw)
                    except Exception as e:
                        if reader != "read_dta":
                            raise
                        _emit({"ev": "hook_note", "where": "pyreadstat", "err": repr(e)})
                        meta = _stata_meta_pandas(raw if raw is not None else str(path))
                    _record("pandas." + reader, path if isinstance(path, (str, os.PathLike)) else "<buffer>",
                            meta, df)
            except Exception as e:
                _emit({"ev": "hook_error", "where": "pandas." + reader, "err": repr(e)})
            return df
        return inner

    # pandas.read_spss is not wrapped: it calls pyreadstat.read_sav, which is
    # already wrapped above, and logging it twice would double the counts.
    _pd.read_stata = _pandas_wrap(_pd.read_stata, "read_dta")

    # --- table writes ------------------------------------------------------
    _orig_to_csv = _pd.DataFrame.to_csv

    def _to_csv(self, path_or_buf=None, *a, **k):
        try:
            covs = {}
            has_id = "id" in self.columns
            for c in self.columns:
                if not str(c).startswith("cov_"):
                    continue
                s = self[c]
                u = s.dropna().unique()
                rec = {"dtype": str(s.dtype), "n_unique": int(len(u))}
                if len(u) <= MAX_VALUES:
                    rec["values"] = sorted({norm(x) for x in u})
                    if has_id:
                        d = self[["id", c]].dropna().drop_duplicates()
                        vc = d[c].map(norm).value_counts()
                        rec["count_basis"] = "ids"
                    else:
                        vc = s.dropna().map(norm).value_counts()
                        rec["count_basis"] = "rows"
                    rec["counts"] = {str(k2): int(n) for k2, n in vc.items()}
                covs[c] = rec
            _emit({"ev": "write", "path": str(path_or_buf), "ncol": len(self.columns),
                   "has_item": "item" in self.columns, "covs": covs})
        except Exception as e:
            _emit({"ev": "hook_error", "where": "to_csv", "err": repr(e)})
        return _orig_to_csv(self, path_or_buf, *a, **k)

    _pd.DataFrame.to_csv = _to_csv
except Exception:
    pass


# Force IPv4: on Ben's machine IPv6 connects stall ~10s per address.
try:
    import socket as _socket

    _orig_gai = _socket.getaddrinfo

    def _gai4(host, port, family=0, *a, **k):
        return _orig_gai(host, port, _socket.AF_INET, *a, **k)

    _socket.getaddrinfo = _gai4
except Exception:
    pass
