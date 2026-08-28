"""
irw_triage.py
=============
Takes a candidate dataset and runs it through:
  1. DOWNLOAD     - fetch the data file from a URL (csv/tsv/xlsx/sav/dta/sas7bdat/RData/rds)
  2. COERCE       - make a BEST-GUESS mapping into IRW long format (id/item/resp)
  3. QC           - run checks mirroring the official IRW data standard, plus
                    the IRW's own density metric
  4. FLAG         - route to 'good'  OR  'human_assistance', with reasons

IMPORTANT — read this before trusting the output
-------------------------------------------------
Step 2 (coercion) is a HEURISTIC GUESS, not a solver. Deciding what counts as
the person, the item, and the response is genuine human judgment for most real
datasets. This tool's job is therefore NOT to be right every time — it's to:
   * fully handle the easy, unambiguous cases, and
   * for everything else, say *exactly* what it couldn't decide,
     so a human can resolve it in seconds instead of starting cold.
A 'human_assistance' flag is the normal, expected outcome — not a failure.

IRW standard (the checks below mirror this):
  required : id, item, resp   (resp numeric & at least ordinal)
  resp      consistently coded within an item; no imputed values
  treat     0/1 if data come from an RCT
  rt        response time in seconds
  date      longitudinal timing in Unix seconds
  multiple scales -> must be split into separate files
"""

from __future__ import annotations

import io
import os
import collections
import re
from dataclasses import dataclass, field
from math import sqrt

import requests
import pandas as pd

UA = {"User-Agent": "irw-triage/1.0 (research)"}


# ---------------------------------------------------------------------------
# Dependency preflight
# ---------------------------------------------------------------------------
# load_table() dispatches on file extension into pandas readers that are
# themselves thin wrappers around optional third-party packages. If one of
# those is missing, pandas raises ImportError *per file*, which the callers
# record as a per-row `download_failed` — indistinguishable, in the output
# CSV, from a dead URL. The rows then get written to the seen-DOIs/seen-keys
# ledgers, so the false negative becomes permanent.
#
# This has bitten the scheduled cloud runs repeatedly (2026-08-24 repos run;
# 2026-08-25 PLOS run lost 10 of 12 candidates this way, one of them a strong
# multi-scale dataset). So: fail loudly at startup instead of quietly per row.
# Every entry point calls preflight_deps() as the first thing in main().

# module name -> what it lets us read
OPTIONAL_READERS = {
    "openpyxl":   ".xlsx",
    "pyreadstat": ".sav / .sas7bdat",
    "pyreadr":    ".RData / .rds",
}


def preflight_deps(required=None, autoinstall=True):
    """Abort the run if a table-reader dependency is missing.

    Tries a `pip install --user` first (cloud sandboxes start bare), then
    re-checks. Raises SystemExit rather than returning False: a run that
    cannot read half the formats it will encounter should not proceed to
    write verdicts into the seen-keys ledgers.
    """
    import importlib
    import subprocess
    import sys

    names = list(required or OPTIONAL_READERS)

    def missing():
        out = []
        for n in names:
            try:
                importlib.import_module(n)
            except ImportError:
                out.append(n)
        return out

    gone = missing()
    if gone and autoinstall:
        print(f"[preflight] missing table readers: {', '.join(gone)} — installing",
              flush=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user",
             "--break-system-packages", *gone],
            check=False)
        importlib.invalidate_caches()
        gone = missing()

    if gone:
        detail = "\n".join(f"    {n:<12} needed for {OPTIONAL_READERS.get(n, '?')}"
                            for n in gone)
        raise SystemExit(
            "[preflight] ABORTING — cannot read all supported table formats.\n"
            f"{detail}\n"
            "    Install with:\n"
            "      pip3 install --user --break-system-packages "
            + " ".join(gone) + "\n"
            "    Running without these silently flags readable files as\n"
            "    `download_failed` and burns their DOIs in the seen-keys ledger."
        )

IRW_REQUIRED = ["id", "item", "resp"]

PERSON_LEVEL_COLS = {"wave", "treat"}
ITEM_LEVEL_PREFIXES = ("itemcov_", "qmatrix", "item_family", "rater")

# Flat sample-size floor: fewer than this many distinct respondents and the
# candidate is skipped outright, no human adjudication (there used to be a
# 50-99 "ask first" band; it was retired 2026-08-12). Enforced here so a
# too-small dataset can never reach the `good` pile in the first place.
MIN_PARTICIPANTS = 100

# Item labels that name a computed quantity rather than a question asked.
# A file whose "items" are all composites is a summary table, not raw
# item-response data -- the failure mode behind the wingenbach_2018
# retraction and 2 of the 3 false-positive `good` rows in PR #1625.
_COMPOSITE_TOKENS = {
    "total", "totals", "composite", "subscale", "subscales", "overall",
    "average", "averages", "avg", "mean", "sum", "index", "score", "scores",
}
# Whole-label pre/post markers (optionally with a short subscale suffix, e.g.
# "pre-A", "post_F"). Matched only against the ENTIRE label: a genuine raw
# item at a pre-wave is usually "pre_anxiety_3", which must not trip this.
_PREPOST_LABEL = re.compile(
    r"^(pre|post|baseline|follow[-_ ]?up)[-_ ]?[a-z0-9]{0,2}$", re.I)


def _looks_composite(label) -> bool:
    """Does this item label name a computed score rather than a question?"""
    s = str(label).strip()
    if not s:
        return False
    if _PREPOST_LABEL.match(s):
        return True
    # Token-wise, so "meaning_1" doesn't match on "mean" and "scoreboard_2"
    # doesn't match on "score".
    tokens = {t.lower() for t in re.split(r"[^A-Za-z0-9]+", s) if t}
    return bool(tokens & _COMPOSITE_TOKENS)
RESPONSE_LEVEL_COLS = {"rt", "date"}


# ---------------------------------------------------------------------------
# 1. DOWNLOAD
# ---------------------------------------------------------------------------

def download(url: str, dest_dir: str = "downloads") -> str:
    """Fetch a data file to disk. Returns the local path."""
    os.makedirs(dest_dir, exist_ok=True)
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    name = url.split("/")[-1].split("?")[0] or "dataset"
    path = os.path.join(dest_dir, name)
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def _looks_header_offset(df: pd.DataFrame) -> bool:
    """True if the header row looks wrong rather than the data. pandas fills
    every blank/duplicate header cell with 'Unnamed: N' — a strong, specific
    signal that a banner/title row (common in Qualtrics and journal
    supplementary-material exports) got read as the column names instead of
    the real header a row or two below it."""
    if df.shape[1] == 0:
        return False
    unnamed = sum(1 for c in df.columns if str(c).startswith("Unnamed:"))
    return unnamed / df.shape[1] > 0.5


def load_table(path_or_bytes, filename: str = "") -> pd.DataFrame:
    """Read csv/tsv/xlsx/sav/dta/sas7bdat/RData/rds into a DataFrame from a
    path or raw bytes.

    Column labels are coerced to str on the way out. A spreadsheet whose
    header row is bare numbers (1, 2, 3 ... -- common for item grids)
    hands pandas an integer Index, and every downstream `c.lower()` /
    `c.startswith()` in this module then dies with "'int' object has no
    attribute 'lower'", which process_one records as a bare `error`
    against a perfectly readable file."""
    return _stringify_columns(_load_table(path_or_bytes, filename))


def _stringify_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is not None and not all(isinstance(c, str) for c in df.columns):
        df = df.rename(columns=str)
    return df


def _load_table(path_or_bytes, filename: str = "") -> pd.DataFrame:
    name = (filename or str(path_or_bytes)).lower()

    def _src():
        # A BytesIO is consumed by one read; rebuild it fresh for each retry.
        # A path string can just be reopened by pandas each time.
        if isinstance(path_or_bytes, (bytes, bytearray)):
            return io.BytesIO(path_or_bytes)
        return path_or_bytes

    def _read_tabular(header):
        if name.endswith((".xlsx", ".xls")):
            return pd.read_excel(_src(), header=header)
        if name.endswith((".tsv", ".tab")):
            try:
                return pd.read_csv(_src(), sep="\t", header=header)
            except UnicodeDecodeError:
                # Some Dataverse/OSF exports (esp. non-English deposits) are
                # Latin-1/cp1252, not UTF-8 -- fall back rather than fail
                # outright (confirmed real case: 10.7910/DVN/33EY6I).
                return pd.read_csv(_src(), sep="\t", header=header, encoding="latin-1")
        try:
            return pd.read_csv(_src(), header=header)
        except UnicodeDecodeError:
            return pd.read_csv(_src(), header=header, encoding="latin-1")

    if name.endswith(".sav"):
        # pandas.read_spss (via pyreadstat) accepts a file-like object directly.
        #
        # convert_categoricals=False is essential, not cosmetic. Both read_spss
        # and read_stata default it to True, which replaces every labelled
        # numeric variable with its label string -- so a 0-5 CAPQ item comes
        # back as "no" / "yes, but only once or a very minor problem". The
        # column is then non-numeric, `resp` fails the ordinal checks, and the
        # candidate lands in human_assistance, typically with the reason "item
        # columns appear to hold text-coded Likert responses rather than
        # numeric codes" -- which reads like a property of the data but is
        # entirely an artifact of this argument. Measured 2026-08-25: 108
        # .sav/.dta candidates sat in worth_retrying/human_assistance across
        # the run outputs, 16 of them with exactly that reason. SPSS/Stata
        # deposits are most of the psychology data this pipeline sees, so the
        # default was a systematic false-negative source.
        #
        # Nothing is lost: triage never reads the labels, and a processing
        # script opens the file itself (pyreadstat.read_sav) when it wants the
        # item stems. Genuine string variables are unaffected -- only labelled
        # numerics change.
        try:
            return pd.read_spss(_src(), convert_categoricals=False)
        except Exception as e:
            # pyreadstat trusts the .sav header's declared encoding. Files
            # written by localised SPSS builds routinely declare one they do
            # not honour, and the read dies with "Unable to convert string to
            # the requested encoding (invalid byte sequence)". The file is
            # fine and fully downloaded -- but the exception propagates to
            # process_one(), which records it as `download_failed`, i.e. a
            # verdict that reads like a dead URL. 19 of the 28 download_failed
            # rows in the 2026-08-27 tier-A run were this, all Spanish- or
            # Turkish-language deposits, every one of them a real instrument.
            if "encoding" not in str(e).lower():
                raise
            import pyreadstat, tempfile, os as _os
            data = _src()
            raw = data.read() if hasattr(data, "read") else open(data, "rb").read()
            tmp = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
            try:
                tmp.write(raw); tmp.close()
                for enc in ("latin1", "cp1252", "utf-8"):
                    try:
                        df, _meta = pyreadstat.read_sav(
                            tmp.name, apply_value_formats=False, encoding=enc)
                        return df
                    except Exception:
                        continue
                raise
            finally:
                _os.unlink(tmp.name)
    if name.endswith(".dta"):
        return pd.read_stata(_src(), convert_categoricals=False)
    if name.endswith(".sas7bdat"):
        return pd.read_sas(_src(), format="sas7bdat")
    if name.endswith((".rdata", ".rda", ".rds")):
        # pyreadr needs a real filesystem path, not a file-like object --
        # spill bytes to a temp file, read, and clean up either way.
        import pyreadr
        import tempfile
        src = _src()
        suffix = ".rds" if name.endswith(".rds") else ".RData"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(src.read() if hasattr(src, "read") else open(src, "rb").read())
            tmp_path = tmp.name
        try:
            result = pyreadr.read_r(tmp_path)
            # .rds -> single unnamed object (key None); .RData -> one or more
            # named objects. Take the first/only one either way.
            return next(iter(result.values()))
        finally:
            os.unlink(tmp_path)

    # csv/tsv/xlsx/xls (or an unrecognized extension, which falls back to
    # plain csv): if the default header=0 read looks offset, retry a few
    # header rows down before accepting a table that's mostly unusable.
    # Only fires when the default read already looks broken, so it can only
    # recover otherwise-unresolved files, never change a working read.
    df = _read_tabular(header=0)
    if _looks_header_offset(df):
        for k in range(1, 5):
            try:
                candidate = _read_tabular(header=k)
            except Exception:
                continue
            if not _looks_header_offset(candidate):
                print(f"    [load_table] header row looked offset (mostly "
                      f"'Unnamed:' columns) — re-read {filename or ''} with "
                      f"header={k}", flush=True)
                return candidate
    return df


# ---------------------------------------------------------------------------
# 2. COERCE  (heuristic best-guess -> IRW long format)
# ---------------------------------------------------------------------------

@dataclass
class Coercion:
    df: pd.DataFrame | None
    confidence: str            # "high" | "low"
    method: str                # how the guess was made
    notes: list = field(default_factory=list)
    original_cols: list = field(default_factory=list)  # wide source columns, for QC


def _looks_like_id(series: pd.Series, n_rows: int) -> bool:
    """A person-id column: many distinct values relative to rows."""
    nun = series.nunique(dropna=True)
    return nun >= max(2, 0.5 * n_rows)


def _ordinalish(series: pd.Series) -> bool:
    """Numeric with a smallish set of distinct values, or clearly continuous."""
    s = pd.to_numeric(series, errors="coerce")
    if s.notna().mean() < 0.8:        # mostly non-numeric -> not a clean resp
        return False
    return True


def _textish_likert(series: pd.Series, n_rows: int) -> bool:
    """A column of a few short, repeated text categories -- looks like a
    Likert scale stored as text labels (e.g. 'Strongly Agree') rather than
    numeric codes. Detection only, never auto-recoded: the category set and
    scale direction need a human to confirm against the source instrument,
    the same verification datastandard.md already requires for numeric
    resp columns."""
    s = series.dropna().astype(str).str.strip()
    if len(s) < max(2, 0.5 * n_rows):
        return False
    nun = s.nunique()
    if nun < 2 or nun > 12:            # a real Likert scale has few categories
        return False
    return s.str.len().mean() <= 40    # short labels, not free-text/prose


def coerce_to_irw(df: pd.DataFrame) -> Coercion:
    cols = {c.lower(): c for c in df.columns}
    orig_cols = list(df.columns)

    # Case A: already in IRW long format -> trust it.
    if all(k in cols for k in IRW_REQUIRED):
        out = df.rename(columns={cols["id"]: "id", cols["item"]: "item",
                                 cols["resp"]: "resp"})
        return Coercion(out, "high", "already-long",
                        ["File already has id/item/resp columns."], orig_cols)

    # Case B: wide matrix (person rows x item columns) -> melt.
    n = len(df)
    notes = []

    # Candidate id column: first that looks like an identifier.
    id_col = None
    id_fallback = False
    for c in df.columns:
        if _looks_like_id(df[c], n) and not pd.api.types.is_float_dtype(df[c]):
            id_col = c
            break
    if id_col is None:
        # No identifier column. In a wide person x item export that is normal
        # and it does NOT mean the id is the first column -- taking column 0
        # grabs a real variable (typically the first demographic) and collapses
        # every respondent onto its handful of values. Seen live on
        # 10.17632/fkyw9v8yj2 (2026-08-25): 287 respondents x a 10-item RSES,
        # first column is gender, so triage reported "Only 2 distinct
        # respondents" and skipped it as below_min_n. The shape itself carries
        # the identity -- one row is one respondent -- so synthesise the id
        # from row position and leave every real column available to be an item
        # or covariate.
        df = df.copy()
        id_col = "__row_id__"
        df[id_col] = range(1, n + 1)
        id_fallback = True
        notes.append(
            "No column met the id heuristic (≥50% unique, non-float); used the "
            "row position as the person id (one row = one respondent) and kept "
            "every source column available as an item or covariate — verify "
            "the file really is one row per person."
        )

    # Detect trial_* columns — signals trials-based data that can't be melted.
    trial_cols = [c for c in df.columns if c.lower().startswith("trial_")]
    if trial_cols:
        notes.append(
            f"Detected trial_* columns ({trial_cols[:4]}). This may be "
            "trials-based data (IRW standard §Trials). The item column will be "
            "uninformative; trial_ columns carry the probe information. "
            "Manual mapping required."
        )
        return Coercion(None, "low", "unresolved", notes, orig_cols)

    # Classify non-id columns by their role in the melt.
    person_cols = [c for c in df.columns
                   if c != id_col
                   and (c in PERSON_LEVEL_COLS or c.startswith("cov_"))]
    item_level_cols = [c for c in df.columns
                       if any(c.startswith(p) for p in ITEM_LEVEL_PREFIXES)]
    response_level_present = [c for c in df.columns if c in RESPONSE_LEVEL_COLS]

    # Option A: bail out if response-level columns exist in a wide file —
    # one rt/date value per person is structurally ambiguous after melting.
    if response_level_present:
        notes.append(
            f"Wide source file contains response-level column(s) "
            f"{response_level_present} — cannot safely melt. "
            "Manual mapping required."
        )
        return Coercion(None, "low", "unresolved", notes, orig_cols)

    protected = set([id_col] + person_cols)
    excluded_from_items = protected | set(item_level_cols)
    item_cols = [c for c in df.columns
                 if c not in excluded_from_items and _ordinalish(df[c])]

    if len(item_cols) >= 2:
        long = df.melt(id_vars=[id_col] + person_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long = long.rename(columns={id_col: "id"})
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        if person_cols:
            notes.append(
                f"Protected person-level columns (carried through melt): "
                f"{person_cols}."
            )
        if item_level_cols:
            notes.append(
                f"Item-level columns excluded from melt (verify alignment): "
                f"{item_level_cols}."
            )
        notes.append(f"Guessed person column: '{id_col}'.")
        notes.append(f"Guessed {len(item_cols)} item columns: "
                     f"{item_cols[:6]}{'...' if len(item_cols) > 6 else ''}.")
        notes.append("VERIFY: are responses ordinal & consistently coded "
                     "(higher = stronger) within each item?")

        # P0 fix #2: fallback forces low confidence regardless of heuristic result.
        if id_fallback:
            confidence = "low"   # row-position id is a guess about the shape
        else:
            confidence = "high" if _looks_like_id(df[id_col], n) else "low"
        return Coercion(long, confidence, "wide-to-long", notes, orig_cols)

    # Case C: can't tell -> hand off. Before giving up, check whether the
    # excluded columns look like a text-coded Likert scale (e.g. "Strongly
    # Agree") rather than junk -- _ordinalish() only recognizes numeric-
    # coercible columns, so a real, well-formed instrument stored as text
    # labels reads the same as noise to it. This is a positive signal, not
    # noise: flag it explicitly (detection only, no auto-recode -- see
    # _textish_likert's docstring) so a human finds it fast instead of
    # re-discovering it from scratch.
    non_excluded = [c for c in df.columns if c not in excluded_from_items]
    textish = [c for c in non_excluded if _textish_likert(df[c], n)]
    if len(textish) >= 2:
        notes.append(
            f"Could not confidently identify NUMERIC item columns, but "
            f"{len(textish)} column(s) look like text-coded Likert items "
            f"(e.g. {textish[:3]}) rather than numeric codes. Needs a human "
            "to confirm the category set/order and recode to numeric."
        )
        notes.append(f"Columns present: {list(df.columns)}")
        return Coercion(None, "low", "text_likert_candidate", notes, orig_cols)

    notes.append("Could not confidently identify item columns.")
    notes.append(f"Columns present: {list(df.columns)}")
    return Coercion(None, "low", "unresolved", notes, orig_cols)


# ---------------------------------------------------------------------------
# 3. QC  (mirrors IRW standard + IRW's own density metric)
# ---------------------------------------------------------------------------

def irw_metadata(df: pd.DataFrame) -> dict:
    """The IRW's own metadata/density computation, ported from their R/Python."""
    d = df.loc[~df["resp"].isna()].copy()
    d["resp"] = pd.to_numeric(d["resp"], errors="coerce")
    n_resp = len(d)
    n_part = d["id"].nunique()
    n_item = d["item"].nunique()
    # response frequency distribution — the professor's table(df$resp)
    resp_counts = d["resp"].value_counts().sort_index()
    resp_table = {str(k): int(v) for k, v in resp_counts.head(20).items()}
    return {
        "n_responses": n_resp,
        "n_categories": int(d["resp"].nunique()),
        "n_participants": n_part,
        "n_items": n_item,
        "responses_per_participant": round(n_resp / n_part, 2) if n_part else 0,
        "responses_per_item": round(n_resp / n_item, 2) if n_item else 0,
        "density": round((sqrt(n_resp) / n_part) * (sqrt(n_resp) / n_item), 4)
                   if n_part and n_item else 0,
        "resp_distribution": resp_table,
    }


@dataclass
class Check:
    name: str
    status: str    # "pass" | "warn" | "fail"
    detail: str


def run_qc(df: pd.DataFrame, coercion_method: str = "",
           original_cols: list = None) -> list:
    """QC checks. The first block is ported directly from the IRW's official
    validate_irw.R (statuses: pass=OK, warn=NOTE, fail=ERROR). The second block
    is extra heuristics we add on top, clearly labelled."""
    checks = []
    original_cols = original_cols or []

    # ===== ported from validate_irw.R =====================================

    # required columns (ERROR if missing)
    missing = [c for c in IRW_REQUIRED if c not in df.columns]
    if missing:
        checks.append(Check("required_columns", "fail",
                            f"missing required columns: {', '.join(missing)}"))
        return checks  # nothing else is meaningful without these
    checks.append(Check("required_columns", "pass", "id/item/resp present"))

    # NAs in required columns: all-NA = ERROR, some-NA = NOTE
    for col in IRW_REQUIRED:
        n_na = df[col].isna().sum()
        if n_na == len(df):
            checks.append(Check(f"{col}_na", "fail", f"{col} is entirely NA"))
        elif n_na > 0:
            checks.append(Check(f"{col}_na", "warn", f"{col} has {n_na} NAs"))

    # resp must be numeric (ERROR)
    resp_num = pd.to_numeric(df["resp"], errors="coerce")
    if resp_num.notna().mean() < 0.99:
        checks.append(Check("resp_numeric", "fail",
                            f"resp is not numeric (only "
                            f"{resp_num.notna().mean():.0%} parse as numbers)"))
    else:
        checks.append(Check("resp_numeric", "pass", "resp is numeric"))

    # duplicate id+item: ERROR if no longitudinal column, else NOTE
    longitudinal = [c for c in ("wave", "timepoint", "date") if c in df.columns]
    dups = df.duplicated(subset=["id", "item"]).sum()
    if dups > 0 and not longitudinal:
        checks.append(Check("dup_id_item", "fail",
                            f"{dups} duplicate id+item rows with no "
                            "wave/timepoint/date column"))
    elif dups > 0:
        checks.append(Check("dup_id_item", "warn",
                            f"{dups} duplicate id+item rows "
                            f"(longitudinal column {longitudinal} present — likely ok)"))
    else:
        checks.append(Check("dup_id_item", "pass", "id+item rows unique"))

    # covariate naming: extra columns without a recognized name/prefix = NOTE.
    # (Broadened from validate_irw.R's narrow list to the full documented
    #  standard, so legitimate columns like item_family/treat aren't flagged.)
    known = {"id", "item", "resp", "rt", "date", "wave", "timepoint",
             "treat", "rater", "item_family"}
    known_prefix = ("cov_", "itemcov_", "qmatrix", "trial_")
    unprefixed = [c for c in df.columns
                  if c not in known and not c.startswith(known_prefix)]
    if unprefixed:
        checks.append(Check("cov_prefix", "warn",
                            f"unrecognized columns (prefix with cov_ if "
                            f"covariates): {', '.join(unprefixed)}"))

    # ===== extra heuristics (beyond the official validator) ===============

    # resp scale sanity — flag a resp that looks continuous/mis-parsed
    ncat = resp_num.nunique()
    if ncat <= 1:
        checks.append(Check("resp_variation*", "fail",
                            "resp has no variation (1 unique value)"))
    elif ncat > 50:
        checks.append(Check("resp_ordinal*", "warn",
                            f"{ncat} distinct resp values — confirm continuous, "
                            "not mis-parsed"))

    # P1 #3: resp coding direction — can't auto-verify; always warn after melt.
    if coercion_method == "wide-to-long":
        checks.append(Check(
            "resp_direction*", "warn",
            "Cannot auto-verify: within each item, higher resp values must "
            "indicate more of the construct (IRW standard). Confirm no "
            "unreversed items."
        ))

    # P1 #4: imputed values — column name signals and mean-imputation signature.
    if original_cols:
        imputed_signals = [c for c in original_cols
                           if re.search(r"_imp(?:uted)?$|_filled$|_flag$", c,
                                        re.I)]
        if imputed_signals:
            checks.append(Check("imputed_values*", "warn",
                                f"Columns suggest imputed values may be present: "
                                f"{imputed_signals}. IRW requires their removal."))
    # Mean-imputation signature: any item where one value accounts for >60% of rows.
    if resp_num.notna().any():
        by_item = df.groupby("item")["resp"]
        for item_name, grp in by_item:
            vc = grp.value_counts(normalize=True)
            if not vc.empty and vc.iloc[0] > 0.60:
                checks.append(Check("imputed_values*", "warn",
                                    f"Item '{item_name}' has one resp value "
                                    f"accounting for {vc.iloc[0]:.0%} of responses "
                                    "— possible mean imputation."))
                break  # one warning is enough

    # P1 #5: date column validation.
    if "date" in df.columns:
        d = pd.to_numeric(df["date"], errors="coerce")
        if d.isna().mean() > 0.1:
            checks.append(Check("date_numeric*", "warn",
                                "date column is not numeric — IRW requires Unix "
                                "seconds (or seconds since first observation)"))
        elif d.notna().any() and d.max() < 1e8:
            checks.append(Check("date_range*", "warn",
                                f"date max={d.max():.0f} — looks too small for "
                                "Unix seconds; verify units"))

    # P1 #6: rt column validation.
    if "rt" in df.columns:
        rt = pd.to_numeric(df["rt"], errors="coerce")
        if rt.isna().mean() > 0.1:
            checks.append(Check("rt_numeric*", "warn",
                                "rt column is not numeric"))
        elif rt.notna().any():
            if rt.median() > 60000:
                checks.append(Check("rt_units*", "warn",
                                    f"rt median={rt.median():.0f} — likely "
                                    "milliseconds, not seconds (IRW requires "
                                    "seconds)"))
            if (rt < 0).any():
                checks.append(Check("rt_negative*", "warn",
                                    "rt has negative values"))

    # treat column should be 0/1 if present
    if "treat" in df.columns:
        bad = set(pd.unique(df["treat"].dropna())) - {0, 1}
        if bad:
            checks.append(Check("treat_binary*", "warn",
                                f"treat has non-0/1 values {sorted(bad)[:5]}"))

    # P2 #7: item-level columns dropped during melt — remind user to verify.
    if original_cols and coercion_method == "wide-to-long":
        item_level_found = [c for c in original_cols
                            if any(c.startswith(p) for p in ITEM_LEVEL_PREFIXES)]
        if item_level_found:
            checks.append(Check("item_level_cols*", "warn",
                                f"Item-level columns {item_level_found} were "
                                "excluded from the melt — verify they are "
                                "correctly aligned after conversion."))

    # P2 #7: multi-scale detection — distinct item-name prefixes suggest separate
    # scales that must be split into separate files.
    if "item" in df.columns:
        prefixes = [re.split(r"[\d_]", str(i))[0].lower()
                    for i in df["item"].unique() if str(i)]
        prefix_counts = pd.Series(prefixes).value_counts()
        dominant = prefix_counts[prefix_counts >= 3]
        if len(dominant) >= 2:
            checks.append(Check("multi_scale*", "warn",
                                f"Item names suggest {len(dominant)} subscales "
                                f"({list(dominant.index)[:4]}) — IRW requires "
                                "separate files per scale."))

    # Response-scale homogeneity. The existing multi_scale* check reads item
    # *names*; this one reads the responses themselves, which is what actually
    # catches a mailing that bundled several instruments. Two distinct
    # failures fall out of the same per-item range profile:
    #   * a substantial minority of items on a different range  -> two scales
    #     in one table, which breaks "one file per scale" and leaves `resp`
    #     meaning different things in different rows;
    #   * one or two isolated items off the modal range -> almost always not
    #     an item at all (an administrative or count column swept in).
    # Both were live defects in the 2026-08-26 Eugene-Springfield build:
    # `sdv` spanned 1-5, 1-7, 1-8 and 1-9 at once, and `submiss` -- a
    # missing-response count, 94.8% zero -- was the only column in the HPQ
    # outside its 1-5 scale.
    if {"item", "resp"}.issubset(df.columns):
        rng = df.dropna(subset=["resp"]).groupby("item")["resp"].agg(["min", "max"])
        if len(rng) >= 3:
            profile = collections.Counter(zip(rng["min"], rng["max"]))
            (modal, modal_n), = profile.most_common(1)
            off = rng[(rng["min"] != modal[0]) | (rng["max"] != modal[1])]
            # Only a range that *exceeds* the modal one is evidence of a
            # different scale; an item nobody answered at the ceiling simply
            # has a lower observed max.
            over = off[(off["max"] > modal[1]) | (off["min"] < modal[0])]
            share = len(over) / len(rng)
            if share >= 0.15:
                other = collections.Counter(zip(over["min"], over["max"]))
                checks.append(Check("resp_scale_mixed", "fail",
                    f"items span more than one response scale: "
                    f"{modal_n} on {modal[0]}-{modal[1]} and {len(over)} on "
                    f"{[f'{a}-{b}' for a, b in list(other)[:3]]}. IRW requires "
                    "one file per scale; split before submitting."))
            elif len(over):
                checks.append(Check("item_scale_outlier", "warn",
                    f"{len(over)} item(s) fall outside the table's "
                    f"{modal[0]}-{modal[1]} scale: {list(over.index)[:4]}. An "
                    "isolated out-of-range column is usually not an item -- "
                    "check for an administrative or count field."))

    # Composite columns masquerading as items. A summary table melts into a
    # perfectly well-formed id/item/resp frame and passes every structural
    # check above -- the only tell is what the items are NAMED.
    if "item" in df.columns:
        labels = [i for i in df["item"].unique() if str(i).strip()]
        comp = [i for i in labels if _looks_composite(i)]
        if labels and len(comp) == len(labels):
            checks.append(Check("composite_items*", "fail",
                                f"every item label names a computed score "
                                f"({[str(c) for c in comp[:4]]}) — this looks "
                                "like a summary/aggregate table, not raw "
                                "item-level responses"))
        elif comp:
            checks.append(Check("composite_items*", "warn",
                                f"{len(comp)}/{len(labels)} item labels name "
                                f"computed scores ({[str(c) for c in comp[:4]]}) "
                                "— drop them, or confirm they are real items"))

    # IRW's own density signal — very sparse data is worth a look
    meta = irw_metadata(df)
    if meta["density"] < 0.01:
        checks.append(Check("density*", "warn",
                            f"very sparse (density={meta['density']}); fine for "
                            "adaptive/booklet designs, else verify"))

    return checks


# ---------------------------------------------------------------------------
# 4. FLAG  (combine coercion confidence + QC into one decision)
# ---------------------------------------------------------------------------

@dataclass
class Triage:
    flag: str           # "good" | "human_assistance"
    reasons: list
    coercion: Coercion
    checks: list
    metadata: dict | None


STAT_TERMS = re.compile(
    r"\b(?:chi|χ²|χ2|df|p[\s-]?value|effect size|std\.?\s?err|"
    r"mean|median|sd|std dev|variance|ci\b|confidence interval|"
    r"f[\s-]?statistic|t[\s-]?statistic|coefficient|odds ratio|r²|r2)\b",
    re.IGNORECASE)
HTML_TAG = re.compile(r"<[a-zA-Z/][^>]*>")


def looks_like_item_response(df: pd.DataFrame) -> tuple:
    """Content gate: is this ACTUALLY item-response data, or just shaped like it?

    Distinguishes genuine person×item response data from things that melt into
    the same 3 columns but aren't responses — most commonly statistical results
    tables scraped from papers. Returns (is_item_response, reasons)."""
    reasons = []
    hard, soft = [], []

    ids = df["id"].astype(str)
    items = df["item"].astype(str)
    resp = pd.to_numeric(df["resp"], errors="coerce")

    # --- HARD signals: any one of these means it's not response data ---
    # HTML/XML markup in cells -> scraped table content, not raw data
    if ids.str.contains(HTML_TAG, na=False).any() or \
       items.str.contains(HTML_TAG, na=False).any():
        hard.append("cells contain HTML/XML markup (looks like a scraped table)")

    # IDs read like prose, not identifiers
    if ids.str.len().mean() > 25:
        hard.append(f"id values are long text (avg {ids.str.len().mean():.0f} "
                    "chars), not identifiers")

    # 'items' are named after statistics
    stat_items = items[items.str.contains(STAT_TERMS, na=False)].unique()
    if len(stat_items) >= max(1, 0.5 * df["item"].nunique()):
        hard.append(f"item names are statistical terms (e.g. {list(stat_items)[:3]})")

    # --- SOFT signals: need two or more together ---
    n_persons = df["id"].nunique()
    n_items = df["item"].nunique()
    if n_persons < 10:
        soft.append(f"only {n_persons} distinct ids (too few to be respondents)")
    if n_items < 2:
        soft.append(f"only {n_items} distinct item(s) — not cross-classified")
    if len(resp) and resp.nunique() / len(resp) > 0.6:
        soft.append(f"{resp.nunique()/len(resp):.0%} of responses are unique "
                    "(real items reuse a small scale; this looks like a results table)")
    # Non-integer resp values signal continuous measurements (loadings, correlations,
    # proportions) rather than ordinal item responses, which are almost always integers.
    if resp.notna().any():
        non_int_frac = (resp.dropna() % 1 != 0).mean()
        if non_int_frac > 0.5:
            soft.append(f"{non_int_frac:.0%} of resp values are non-integer — "
                        "ordinal item responses are almost always integer-valued")

    is_ir = not hard and len(soft) < 2
    if hard:
        reasons += hard
    if len(soft) >= 2:
        reasons += soft
    return is_ir, reasons


# ---------------------------------------------------------------------------
# PII screen
# ---------------------------------------------------------------------------
# The pipeline's rule is that a raw source file containing real names, emails,
# birthdates, addresses, phone numbers or national IDs *anywhere* is a
# whole-candidate skip, not a drop-the-column fix (SKILL.md Step 4, memory
# feedback_pii_skip_entirely). Nothing enforced that at triage time, so such a
# file could -- and did -- come back flagged `good`: both "Questionnaire
# Response — Doomscrolling" deposits (figshare 29857874 / 28979105, 2026-08-25)
# scored `good` with a `Respondent's Name (Real Name/Initial)` column of actual
# given names sitting in the raw header. Raw Google Forms exports are the
# recurring shape.
#
# Matched against the RAW header, because the coercion step usually drops these
# columns before anything else looks at them.
#
# Deliberately conservative about `name`: a bare "name" matches "item name",
# "scale name", "variable name", so a person-qualifier is required. Likewise
# only a full date of birth counts -- a `birthyr`/`birth year` column is a
# legitimate covariate, not PII.
# Two tiers, because Google Forms exports use the full item stem as the column
# label. "I often spend hours using my phone before bed" is an item, not a
# phone-number field -- so the contact-detail patterns only fire on labels that
# actually read like a form field (<=5 words), while the patterns that never
# occur inside an item stem fire at any length.
_RE_PII_STRONG = re.compile(
    r"(?:"
    # a person-qualified name -- never a bare "name", which matches "item
    # name" / "variable name" / "filename"
    r"(?:respondent|participant|student|patient|employee|subject|customer|"
    r"your|full|first|last|real|given|maiden)[\s_\-]*'?s?[\s_\-]*names?\b"
    r"|\bnames?[\s_\-]*of[\s_\-]*(?:the[\s_\-]*)?"
    r"(?:respondent|participant|student|patient|child|parent)"
    r"|\bsurnames?\b(?![\s_\-]*of\b)"
    r"|\bdate[\s_\-]*of[\s_\-]*birth\b|\bbirth[\s_\-]*date\b|\bbirthday\b|\bdob\b"
    r"|\bip[\s_\-]*address\b"
    # a column labelled exactly "IP" (or ip_addr) in a survey export is the
    # respondent's address -- 10.7910/dvn/l6g8ul (2026-08-25) stored them
    # geolocated, e.g. "112.96.199.12(guangdong-guangzhou)". Anchored to the
    # whole label so it cannot fire inside an unrelated abbreviation.
    r"|^ip$|^ip[\s_\-]?addr(?:ess)?$"
    r"|\bpassport[\s_\-]*(?:no|number)?\b|\bsocial[\s_\-]*security\b|\bssn\b"
    r"|\bnational[\s_\-]*id\b"
    r"|\bnombre[\s_\-]*(?:completo|del[\s_\-]*(?:participante|encuestado))\b"
    r"|\bapellidos?\b|姓名|氏名|이름"
    # national identity numbers, non-English. 身份证(号) is the PRC resident ID
    # card -- seen alongside pupil and parent names in a school survey
    # (10.7910/dvn/7cyiqg, 2026-08-25).
    r"|身份证|身分證|주민등록번호|マイナンバー"
    r"|\bcpf\b|\bcurp\b|\bnric\b|\bnik\b[\s_\-]*(?:ktp)?"
    r")",
    re.IGNORECASE)

_RE_PII_WEAK = re.compile(
    r"(?:"
    r"\be[\s_\-]?mail\b|\bcorreo[\s_\-]*electr|\bcourriel\b"
    # Trailing \b is deliberately optional before "num"/"no": SPSS strips
    # spaces out of variable names, so "Phone Number" arrives as
    # "PhoneNumberNomborTelefon" and a trailing \b never fires
    # (10.7910/dvn/llppie, 2026-08-25 -- real phone numbers and a full
    # block/floor/house address, missed on the first pass because of this).
    r"|\b(?:tele)?phone(?:[\s_\-]*(?:no\b|num)|\b)"
    r"|\bmobile[\s_\-]*(?:no\b|num)|\bcontact[\s_\-]*(?:no\b|num|details\b)"
    r"|\b(?:home|street|postal|mailing|residential)[\s_\-]*address\b"
    r"|\b(?:house|block|floor|apartment|flat)[\s_\-]*(?:no\b|num)"
    r")",
    re.IGNORECASE)

# Columns whose *label* is too generic to judge ("name" matches "item name",
# "variable_name", "filename") but whose *contents* settle it. A bare NAME
# column holding 259 distinct short alphabetic strings over 278 rows is a
# roster of people, not metadata -- 10.17632/6rbv3fbz8d (2026-08-25) stored
# respondents' given names exactly that way and the header-only screen let it
# through.
_RE_BARE_NAME_LABEL = re.compile(
    r"^(?:name|names|nombre|nome|nom|navn|namn|isim|ad|ime)$", re.IGNORECASE)


def _looks_like_person_names(series) -> bool:
    """True when a column's values read as a list of personal names."""
    v = series.dropna().astype(str).str.strip()
    v = v[v != ""]
    if len(v) < 20:
        return False
    # Mostly short, alphabetic, and nearly all distinct.
    alpha = v.str.match(r"^[A-Za-zÀ-ɏ][A-Za-zÀ-ɏ .'-]{0,40}$")
    if alpha.mean() < 0.8:
        return False
    if v.str.len().mean() > 30:
        return False
    # A roster is high-cardinality in absolute terms; a categorical column
    # ("Control"/"Treatment", a 6-level profession) is not, however long the
    # file is. The ratio alone was too tight -- a roster with common repeated
    # first names sits well under half.
    if v.nunique() < 15 or v.nunique() / len(v) < 0.3:
        return False
    # Guard against a free-text answer column: real names are 1-4 tokens.
    return v.str.split().str.len().mean() <= 4


_MAX_WEAK_WORDS = 5
# Second guard for the weak tier. The word-count test alone does not survive
# SPSS name mangling: a stripped item stem ("Ioftenfeelanxiouscheckingmyemail")
# is also one "word". A real field label stays short; an item stem does not.
_MAX_WEAK_CHARS = 60


def screen_for_pii(columns, df=None) -> list[str]:
    """Return the raw column labels that look like direct identifiers.

    Pass `df` to additionally content-check generically-named columns -- a
    bare `NAME` cannot be judged from its label alone, only from what is in
    it."""
    hits = []
    for c in columns:
        label = str(c)
        if _RE_PII_STRONG.search(label):
            hits.append(label)
        elif (_RE_PII_WEAK.search(label)
              and len(label.split()) <= _MAX_WEAK_WORDS
              and len(label) <= _MAX_WEAK_CHARS):
            hits.append(label)
        elif (df is not None and _RE_BARE_NAME_LABEL.match(label.strip())
              and _looks_like_person_names(df[c])):
            hits.append(label)
    return hits


def triage_dataset(df_raw: pd.DataFrame) -> Triage:
    coerce = coerce_to_irw(df_raw)
    reasons = []

    # PII first: it disqualifies the whole candidate regardless of how well
    # the file parses, so it must beat every other verdict including `good`.
    pii = screen_for_pii(df_raw.columns, df_raw)
    if pii:
        reasons.append(
            "Raw file has column(s) that look like direct identifiers: "
            + ", ".join(repr(c) for c in pii[:5])
            + ". Per the pipeline's PII rule this is a whole-candidate skip, "
              "not a drop-the-column fix. Confirm the column really holds "
              "personal data before overriding.")
        return Triage("pii_suspected", reasons, coerce, [], None)

    if coerce.df is None:
        reasons.append("Automatic IRW formatting failed — needs a human to map "
                       "columns to id/item/resp.")
        return Triage("human_assistance", reasons + coerce.notes,
                      coerce, [], None)

    checks = run_qc(coerce.df, coerce.method, coerce.original_cols)
    meta = irw_metadata(coerce.df)

    # Content gate: does this even look like item-response data?
    is_ir, ir_reasons = looks_like_item_response(coerce.df)
    if not is_ir:
        reasons.append("Does NOT look like item-response data — not a candidate "
                       "for IRW.")
        return Triage("not_item_response", reasons + ir_reasons,
                      coerce, checks, meta)

    # Sample-size floor. Its own terminal flag rather than a QC failure: N is
    # not something a human can adjudicate or a script can fix, so routing it
    # to human_assistance would just spend review time re-deriving "too small".
    # Checked after the content gate so a not_item_response file is still
    # reported as such (the more useful diagnosis) rather than as too small.
    if meta["n_participants"] < MIN_PARTICIPANTS:
        reasons.append(f"Only {meta['n_participants']} distinct respondents — "
                       f"below the IRW floor of {MIN_PARTICIPANTS}. Skip; no "
                       "human review needed.")
        return Triage("below_min_n", reasons, coerce, checks, meta)

    fails = [c for c in checks if c.status == "fail"]
    warns = [c for c in checks if c.status == "warn"]

    if fails:
        reasons.append("QC failed on: " + ", ".join(c.name for c in fails))
    if coerce.confidence == "low":
        reasons.append("Column mapping was a low-confidence guess.")
    if warns:
        reasons.append("QC warnings to review: " + ", ".join(c.name for c in warns))

    # Decision (matching the validator's ERROR vs NOTE semantics):
    #   hard ERROR or shaky mapping -> needs a human
    #   resp_ordinal* on wide-to-long -> needs a human (likely aggregate scores)
    #   only soft NOTEs             -> still 'good', notes listed for a glance
    ordinal_warn = any(c.name == "resp_ordinal*" for c in warns)
    if fails:
        flag = "human_assistance"
    elif coerce.confidence == "low":
        flag = "human_assistance"
    elif ordinal_warn and coerce.method == "wide-to-long":
        flag = "human_assistance"
        reasons.insert(0, "resp has >50 unique values after wide-to-long melt — "
                          "likely continuous/aggregate data, not ordinal item responses.")
    else:
        flag = "good"
        if warns:
            reasons.insert(0, f"Passed (no errors); {len(warns)} note(s) "
                              "to glance at before submitting.")
        else:
            reasons.insert(0, "Confident mapping, all checks clean.")

    return Triage(flag, reasons, coerce, checks, meta)


def print_report(t: Triage, title: str = "dataset"):
    print(f"\n{'='*64}\n{title}\nFLAG: {t.flag.upper()}\n{'='*64}")
    for r in t.reasons:
        print(f"  • {r}")
    if t.checks:
        print("\n  QC checks:")
        for c in t.checks:
            mark = {"pass": "✓", "warn": "!", "fail": "✗"}[c.status]
            print(f"    [{mark}] {c.name}: {c.detail}")
    if t.metadata:
        print("\n  IRW metadata:")
        for k, v in t.metadata.items():
            print(f"    {k}: {v}")
    if t.coercion.notes:
        print("\n  Mapping notes:")
        for nzz in t.coercion.notes:
            print(f"    - {nzz}")


# ---------------------------------------------------------------------------
# CLI: triage a local file, or a URL to download first
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python irw_triage.py <file-or-url>")
        sys.exit(0)
    target = sys.argv[1]
    if target.startswith("http"):
        target = download(target)
    raw = load_table(target, filename=target)
    result = triage_dataset(raw)
    print_report(result, title=os.path.basename(target))
    if result.coercion.df is not None:
        out = "irw_formatted_" + re.sub(r"\W+", "_", os.path.basename(target)) + ".csv"
        result.coercion.df.to_csv(out, index=False)
        print(f"\nBest-guess IRW-format data written to: {out}")
        print("Review it before any submission.")
