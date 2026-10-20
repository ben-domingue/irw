#!/usr/bin/env python3
# Source: https://zenodo.org/records/19807325
# DOI: 10.5281/zenodo.19807325
# Data: Dataset_IPV_Dynamics.csv (Zenodo record 19807325)
# License: CC BY 4.0 (verified on the Zenodo record page / API: license id cc-by-4.0)
# Reference: Rodriguez-Villagra, O. A., & Huepe, D. (2026). Unlocking the Interplay of
#   Interoceptive Awareness, Anxiety, and Perspective-Taking: Insights into Intimate
#   Partner Violence Dynamics in General Population. Zenodo.
# Item text: not shipped. The deposit is a bare numeric CSV -- there are no SPSS/Stata
#   variable labels and no value labels (the only file beside it is a jamovi .omv of the
#   analysis). Column names are positional codes (iri03, sta_ie01, intero01, etc01), so the
#   wording would have to come from the published Spanish instruments (IRI perspective-taking
#   subscale, STAI state form, MAIA-style interoceptive awareness, Conflict Tactics Scale),
#   each a third-party scale the deposit's CC BY does not cover. Checked: column headers
#   (positional), and the deposit's file list (no codebook or questionnaire file).
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "stage_2026-10-20_s2"))
CACHE = Path(os.environ.get("IRW_CACHE", "/tmp/irw_cache_s2"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch(url: str, name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / name
    if not p.exists():
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=600) as r, open(p, "wb") as f:
            f.write(r.read())
    return p


def screen_pii(d: pd.DataFrame) -> None:
    """Print every string column and its sample values; assert the denominator is non-zero."""
    txt = [c for c in d.columns if pd.api.types.is_string_dtype(d[c])]
    print(f"  [pii] string columns examined: {len(txt)} of {d.shape[1]}")
    assert len(txt) > 0 or d.select_dtypes("object").empty, "PII screen selected no columns"
    for c in txt:
        vals = d[c].dropna().astype(str).unique()[:8]
        print(f"  [pii] {c!r}: {list(vals)}")


def emit(tables: dict) -> None:
    """name -> (long frame, permitted_values or None). QC, upload-profile validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names), f"duplicate output names: {names}"
    assert max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def pvals(items, valid, rename: dict | None = None) -> dict:
    """permitted_values keyed by the shipped item code."""
    vs = sorted(float(v) for v in valid)
    return {(rename or {}).get(c, c): list(vs) for c in items}


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    """Melt `items` to long, drop missing, keep only codes in `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items,
               var_name="item", value_name="resp")
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
    t = t.dropna(subset=["resp"])
    if valid is not None:
        keep = t["resp"].isin(valid)
        if not keep.all():
            print(f"    dropped {int((~keep).sum())} resp outside {sorted(valid)[:1]}.."
                  f"{sorted(valid)[-1:]}")
        t = t[keep]
    order = (["id", "item", "resp"]
             + [c for c in ("wave", "treat", "rt", "date") if c in t.columns]
             + covs)
    return t[order].reset_index(drop=True)

URL = ("https://zenodo.org/api/records/19807325/files/"
       "Dataset_IPV_Dynamics.csv/content")

# Blocks of raw per-item responses. The file also carries, and this script skips:
#   iri03_inv, iri15_inv           -- reverse-scored copies of iri03 / iri15
#   iri_toma_perspect              -- IRI perspective-taking total
#   total_sta_ie, intero_total     -- scale totals
#   agresion_total                 -- aggression total
#   parc_*                         -- partial/subscale scores computed across items
BLOCKS = {
    "rodriguezvillagra_2026_iri_pt": (
        ["iri03", "iri08", "iri11", "iri15", "iri21", "iri25", "iri28"],
        range(0, 5)),
    "rodriguezvillagra_2026_anxiety": (
        [f"sta_ie{i:02d}" for i in range(1, 21)], range(0, 4)),
    "rodriguezvillagra_2026_interocept": (
        [f"intero{i:02d}" for i in range(1, 33)], range(0, 6)),
    "rodriguezvillagra_2026_conflict": (
        [f"etc{i:02d}" for i in range(1, 41)], range(0, 7)),
}
SKIPPED = {
    "iri03_inv": "reverse-scored copy of iri03",
    "iri15_inv": "reverse-scored copy of iri15",
    "iri_toma_perspect": "IRI perspective-taking total (composite)",
    "total_sta_ie": "state-anxiety total (composite)",
    "intero_total": "interoceptive awareness total (composite)",
    "agresion_total": "aggression total (composite)",
}


def convert() -> None:
    d = pd.read_csv(fetch(URL, "zenodo_19807325_ipv.csv"))
    screen_pii(d)

    # No person identifier in the source; the file is one row per respondent.
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    assert d["id"].nunique() == len(d)
    print(f"  respondents={d['id'].nunique()}")

    used = set()
    tables = {}
    for name, (items, valid) in BLOCKS.items():
        missing = [c for c in items if c not in d.columns]
        assert not missing, missing
        used.update(items)
        tables[name] = (long(d, items, [], valid=set(float(v) for v in valid)),
                        pvals(items, valid))

    # Balance the books: every source column is shipped or skipped for a printed reason.
    for c in d.columns:
        if c == "id" or c in used:
            continue
        if c in SKIPPED:
            print(f"  [skip] {c}: {SKIPPED[c]}")
        elif c.startswith("parc_"):
            print(f"  [skip] {c}: partial/subscale score computed across items (composite)")
        else:
            raise AssertionError(f"unaccounted source column: {c}")
    assert used | set(SKIPPED) | {c for c in d.columns if c.startswith("parc_")} | {"id"} \
        == set(d.columns)

    emit(tables)


if __name__ == "__main__":
    convert()
