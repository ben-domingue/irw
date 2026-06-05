"""
irw_triage.py
=============
Takes a candidate dataset and runs it through:
  1. DOWNLOAD     - fetch the data file from a URL (csv/tsv/xlsx)
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
import re
from dataclasses import dataclass, field
from math import sqrt

import requests
import pandas as pd

UA = {"User-Agent": "irw-triage/1.0 (research)"}

IRW_REQUIRED = ["id", "item", "resp"]


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


def load_table(path_or_bytes, filename: str = "") -> pd.DataFrame:
    """Read csv/tsv/xlsx into a DataFrame from a path or raw bytes."""
    name = (filename or str(path_or_bytes)).lower()
    if isinstance(path_or_bytes, (bytes, bytearray)):
        src = io.BytesIO(path_or_bytes)
    else:
        src = path_or_bytes
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(src)
    if name.endswith(".tsv"):
        return pd.read_csv(src, sep="\t")
    return pd.read_csv(src)


# ---------------------------------------------------------------------------
# 2. COERCE  (heuristic best-guess -> IRW long format)
# ---------------------------------------------------------------------------

@dataclass
class Coercion:
    df: pd.DataFrame | None
    confidence: str            # "high" | "low"
    method: str                # how the guess was made
    notes: list = field(default_factory=list)


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


def coerce_to_irw(df: pd.DataFrame) -> Coercion:
    cols = {c.lower(): c for c in df.columns}

    # Case A: already in IRW long format -> trust it.
    if all(k in cols for k in IRW_REQUIRED):
        out = df.rename(columns={cols["id"]: "id", cols["item"]: "item",
                                 cols["resp"]: "resp"})
        return Coercion(out, "high", "already-long",
                        ["File already has id/item/resp columns."])

    # Case B: wide matrix (person rows x item columns) -> melt.
    n = len(df)
    # candidate id column: first column that looks like an identifier
    id_col = None
    for c in df.columns:
        if _looks_like_id(df[c], n) and not pd.api.types.is_float_dtype(df[c]):
            id_col = c
            break
    if id_col is None:
        id_col = df.columns[0]  # fall back to first column

    item_cols = [c for c in df.columns if c != id_col and _ordinalish(df[c])]

    notes = []
    if len(item_cols) >= 2:
        long = df.melt(id_vars=[id_col], value_vars=item_cols,
                       var_name="item", value_name="resp")
        long = long.rename(columns={id_col: "id"})
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        # Was the id guess shaky? Then confidence is low.
        confident = _looks_like_id(df[id_col], n)
        notes.append(f"Guessed person column: '{id_col}'.")
        notes.append(f"Guessed {len(item_cols)} item columns: "
                     f"{item_cols[:6]}{'...' if len(item_cols) > 6 else ''}.")
        # Heuristic can't verify responses are *consistently* coded / ordinal.
        notes.append("VERIFY: are responses ordinal & consistently coded "
                     "(higher = stronger) within each item?")
        return Coercion(long, "high" if confident else "low",
                        "wide-to-long", notes)

    # Case C: can't tell -> hand off.
    notes.append("Could not confidently identify item columns.")
    notes.append(f"Columns present: {list(df.columns)}")
    return Coercion(None, "low", "unresolved", notes)


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


def run_qc(df: pd.DataFrame) -> list:
    """QC checks. The first block is ported directly from the IRW's official
    validate_irw.R (statuses: pass=OK, warn=NOTE, fail=ERROR). The second block
    is extra heuristics we add on top, clearly labelled."""
    checks = []

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

    # treat column should be 0/1 if present
    if "treat" in df.columns:
        bad = set(pd.unique(df["treat"].dropna())) - {0, 1}
        if bad:
            checks.append(Check("treat_binary*", "warn",
                                f"treat has non-0/1 values {sorted(bad)[:5]}"))

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

    is_ir = not hard and len(soft) < 2
    if hard:
        reasons += hard
    if len(soft) >= 2:
        reasons += soft
    return is_ir, reasons


def triage_dataset(df_raw: pd.DataFrame) -> Triage:
    coerce = coerce_to_irw(df_raw)
    reasons = []

    if coerce.df is None:
        reasons.append("Automatic IRW formatting failed — needs a human to map "
                       "columns to id/item/resp.")
        return Triage("human_assistance", reasons + coerce.notes,
                      coerce, [], None)

    checks = run_qc(coerce.df)
    meta = irw_metadata(coerce.df)

    # Content gate: does this even look like item-response data?
    is_ir, ir_reasons = looks_like_item_response(coerce.df)
    if not is_ir:
        reasons.append("Does NOT look like item-response data — not a candidate "
                       "for IRW.")
        return Triage("not_item_response", reasons + ir_reasons,
                      coerce, checks, meta)

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
    #   only soft NOTEs             -> still 'good', notes listed for a glance
    if fails:
        flag = "human_assistance"
    elif coerce.confidence == "low":
        flag = "human_assistance"
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
