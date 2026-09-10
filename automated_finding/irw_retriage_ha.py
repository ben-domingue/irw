"""
irw_retriage_ha.py
==================
Post-hoc refinement of the human_assistance cases in irw_triage_new.csv.

Uses metadata and reason-text patterns (no re-download required) to sub-classify
the 376 human_assistance rows into actionable buckets, reducing the manual review
burden and surfacing datasets that are genuinely worth a second look.

Refined flags
-------------
not_item_response   -- clear evidence the file is not person×item response data
wrong_file_selected -- correct dataset, but the batch script grabbed the wrong file
                       (e.g. a codebook instead of the data matrix)
recoverable_format  -- data likely good but file needs re-reading (wrong delimiter,
                       multi-sheet Excel, one questionnaire holding several
                       instruments that need splitting per scale, etc.)
aggregate_continuous -- responses appear continuous/aggregate rather than ordinal
worth_retrying       -- plausible longitudinal or mapping issue; worth a second download
human_review         -- genuinely ambiguous; needs eyes on the raw file

Output
------
irw_retriage_ha.csv  -- original columns + refined_flag + refined_reason
human_review/human_review_<source>_<date>.csv
                     -- the human_review rows, copied into the permanent
                        archive that discovery runs read for exclusions.
                        Suppress with --no-archive.
"""

from __future__ import annotations

import re
import pandas as pd
from irw_discover_updated import in_runs_dir, resolve_in_path

# ---------------------------------------------------------------------------
# Pattern helpers
# ---------------------------------------------------------------------------

HTML_TAG = re.compile(r"<[a-zA-Z/][^>]{0,50}>")

DICT_COL_PATTERNS = re.compile(
    r"\b(variable\s+name|variable\s+label|measurement\s+level|response\s+categor"
    r"|codebook|column\s*width|spss|value\s+label|generated\s+variable)\b",
    re.IGNORECASE,
)

REVIEW_COL_PATTERNS = re.compile(
    r"\b(study\s+type|key\s+finding|theme|access|main\s+focus|participants\b.*\bfindings)\b",
    re.IGNORECASE,
)

ITEM_LIKE = re.compile(
    r"\b(item|q\d+|i\d+|[a-z]{1,4}\d{1,3}r?|[a-z]{2,8}\d{0,3}_\d{1,3}|subject|respond|id)\b",
    re.IGNORECASE,
)


def _has_html(text: str) -> bool:
    return bool(HTML_TAG.search(str(text or "")))


def _cols_from_reasons(reasons: str) -> list[str]:
    """Extract column name list from a 'Columns present: [...]' reason string.

    Also handles truncated lists (the batch script caps reasons at 400 chars,
    so the closing ] is often missing).
    """
    import ast
    # Try complete list first
    m = re.search(r"Columns present:\s*(\[.*?\])", reasons, re.DOTALL)
    if m:
        try:
            return ast.literal_eval(m.group(1))
        except Exception:
            pass
    # Truncated list: grab everything after 'Columns present: ['
    m2 = re.search(r"Columns present:\s*\[(.+)$", reasons, re.DOTALL)
    if m2:
        fragment = m2.group(1).strip()
        # Try to recover by closing the list and re-parsing
        try:
            # Drop trailing partial token (might be cut mid-string) then close
            cleaned = re.sub(r",?\s*'[^']*$", "", fragment)
            return ast.literal_eval("[" + cleaned + "]")
        except Exception:
            pass
        # Last resort: extract all quoted strings from the fragment
        return re.findall(r"'([^']*)'", fragment)
    return []


def _semicolon_columns(cols: list[str]) -> list[str]:
    """Return columns that look like a semicolon-delimited header row."""
    return [c for c in cols if c.count(";") >= 3]


def _item_like_count(header: str) -> int:
    """Count item-like tokens in a semicolon-delimited header string."""
    tokens = [t.strip() for t in header.split(";")]
    return sum(1 for t in tokens if ITEM_LIKE.match(t))


def _raw_semicolon_header(reasons: str) -> str | None:
    """Extract a semicolon-delimited header fragment directly from reasons text.

    Handles both complete column lists and truncated ones where the closing ]
    was cut off by the 400-char batch limit.
    """
    m = re.search(r"Columns present:\s*\[[\s'\"]*([^\]'\"]{10,})", reasons)
    if not m:
        return None
    fragment = m.group(1).strip().strip("'\"")
    if fragment.count(";") >= 3:
        return fragment
    return None


# ---------------------------------------------------------------------------
# Classification rules (applied in priority order — first match wins)
# ---------------------------------------------------------------------------

def classify(row: pd.Series) -> tuple[str, str]:
    reasons = str(row.get("reasons") or "")
    title = str(row.get("title") or "")
    n_part = row.get("n_participants")
    n_items = row.get("n_items")
    n_resp = row.get("n_responses")

    cols = _cols_from_reasons(reasons)
    cols_lower = [c.lower() for c in cols]

    # ── RULE 1: HTML markup in column names ─────────────────────────────────
    # Scraped HTML tables from papers; cells have <b>, <i>, <p> etc.
    if any(_has_html(c) for c in cols):
        return ("not_item_response",
                "HTML markup in column names — file is a scraped paper table, not raw data")

    # ── RULE 2: HTML in title (paper prose, not a dataset title) ────────────
    if _has_html(title):
        return ("not_item_response",
                "Title is HTML-encoded paper prose — file is a scraped element, not a dataset")

    # ── RULE 3: Data-dictionary / codebook file ──────────────────────────────
    col_str = " ".join(cols)
    if DICT_COL_PATTERNS.search(col_str) or any(
        c in ("variable name", "variable label", "codebook") for c in cols_lower
    ):
        return ("not_item_response",
                "Column names match a data dictionary / codebook (Variable Name, Variable Label, etc.) — "
                "this file describes the dataset, it is not the data itself")

    # ── RULE 4: Literature-review / summary table ────────────────────────────
    if REVIEW_COL_PATTERNS.search(col_str):
        return ("not_item_response",
                "Column names match a literature-review or results table "
                "(Study Type, Key Findings, Theme, etc.) — not item-response data")

    # ── RULE 5: SAPA-style codebook (item_id + item, no resp) ────────────────
    if "item_id" in cols_lower and "item" in cols_lower:
        return ("wrong_file_selected",
                "File has codebook columns (item_id, item) but no response column — "
                "the batch script grabbed the item dictionary instead of the data matrix. "
                "Look for a wider file in the same dataset (e.g. SAPA response CSV).")

    # ── RULE 6: Wrong delimiter (semicolon-delimited read as CSV) ────────────
    # Check both parsed cols (complete list) and raw fragment (handles truncation)
    sc_cols = _semicolon_columns(cols)
    raw_header = _raw_semicolon_header(reasons) if not sc_cols else None
    candidate_header = sc_cols[0] if sc_cols else raw_header
    if candidate_header:
        header = candidate_header
        item_n = _item_like_count(header)
        tokens = [t.strip() for t in header.split(";") if t.strip()]
        if item_n >= 3:
            n_item_cols = sum(1 for t in tokens
                              if re.match(r"[A-Za-z]{1,4}\d{1,3}R?$", t.strip()))
            note = (f"File is semicolon-delimited but was read with comma delimiter. "
                    f"Header tokens include {tokens[:6]}... — re-read with sep=';' and "
                    f"re-run triage. Contains ~{n_item_cols} apparent item columns.")
            return ("recoverable_format", note)
        else:
            return ("not_item_response",
                    f"File is semicolon-delimited but read as CSV; columns appear to be "
                    f"non-item metadata ({tokens[:5]})")

    # ── RULE 6b: Text-coded Likert item columns detected ─────────────────────
    # coerce_to_irw() flags this explicitly when >=2 excluded columns look
    # like short, repeated text categories (e.g. "Strongly Agree") rather
    # than numeric codes -- a positive signal of a real instrument, not
    # noise. See README.md's Step 1b note (2026-07-30 "Human eye" audit).
    if "text-coded Likert items" in reasons:
        return ("worth_retrying",
                "Item columns appear to hold text-coded Likert responses "
                "('Strongly Agree', etc.) rather than numeric codes — "
                "confirm the category set/order against the source "
                "instrument and recode to numeric; not a content problem.")

    # ── RULE 7: Only 2 columns, both non-numeric labels ──────────────────────
    if len(cols) == 2 and not any(re.search(r"\d", c) for c in cols):
        return ("not_item_response",
                f"Only 2 label-style columns ({cols}) — likely a reference list or name table, "
                "not person×item data")

    # ── RULE 8: Implausible n_responses ratio (summary / aggregate table) ────
    if pd.notna(n_part) and pd.notna(n_items) and pd.notna(n_resp) and n_items > 0 and n_part > 0:
        ratio = n_resp / (n_part * n_items)
        if n_part <= 5 and n_resp > 10_000:
            return ("not_item_response",
                    f"n_participants={n_part:.0f} but n_responses={n_resp:.0f} — "
                    f"'participants' are almost certainly rows in a summary table, "
                    f"not real respondents (ratio={ratio:.0f}×)")
        if ratio > 200:
            return ("not_item_response",
                    f"n_responses/n_participants/n_items ratio={ratio:.0f}× — "
                    "strongly suggests a long aggregate table, not individual responses")

    # ── RULE 9: >50 unique resp values ──────────────────────────────────────
    if ">50 unique values" in reasons:
        if pd.notna(n_part) and n_part >= 50:
            return ("aggregate_continuous",
                    "Response has >50 unique values after wide-to-long melt — "
                    "likely continuous measurement (VAS, RT, scale scores), "
                    "not ordinal item responses. Confirm resp range before including.")
        else:
            return ("aggregate_continuous",
                    "Response has >50 unique values and very few apparent participants — "
                    "likely a summary / aggregate file with continuous measures")

    # ── RULE 10: dup_id_item with plausible longitudinal structure ───────────
    if "dup_id_item" in reasons and pd.notna(n_part) and pd.notna(n_items) and pd.notna(n_resp):
        ratio = n_resp / (n_part * n_items) if n_part * n_items > 0 else float("inf")
        if n_part >= 50 and 1 <= ratio <= 8:
            return ("worth_retrying",
                    f"dup_id_item fail but n_participants={n_part:.0f}, ratio={ratio:.1f}× — "
                    "consistent with a longitudinal/repeated-measures design. "
                    "Re-examine file for a wave/timepoint/date column to use as "
                    "third key; if present this is likely IRW-eligible.")
        if n_part >= 50 and ratio <= 20:
            return ("aggregate_continuous",
                    f"dup_id_item with ratio={ratio:.1f}× and n_participants={n_part:.0f} — "
                    "possible longitudinal data but the high repeat rate and resp_ordinal* "
                    "warning suggest responses may be continuous. Quick data check needed.")

    # ── RULE 10b: resp_scale_mixed on a multi-instrument questionnaire ──────
    # One questionnaire carrying several instruments -- an MBI on 0-6, a coping
    # scale on 1-5, a personality block on 0/1 -- fails `resp_scale_mixed` every
    # time, because the automatic single melt pools blocks that were never one
    # scale. That is not ambiguity: `datastandard.md` already answers it with
    # "one file per scale". Before this rule such rows fell through to the
    # human_review default; on the 2026-09-01 PLOS weekly batch that was 5 of
    # the 7 human_review rows, and all 5 became shipped tables on first
    # inspection (zhou_2016_*, teo_2021_*, shao_2025_*, smirnov_2025_*, plus one
    # genuine drop). Routed to recoverable_format -- the file is fine, the
    # *read* is what needs redoing -- so they stay in the machine-follow-up
    # pile rather than the eyes-needed one.
    if "resp_scale_mixed" in reasons and pd.notna(n_part) and n_part >= 100:
        multi = "multi_scale" in reasons
        return ("recoverable_format",
                f"QC failed on resp_scale_mixed with n_participants={n_part:.0f}"
                + (" plus a multi_scale warning" if multi else "") +
                " — consistent with one questionnaire carrying several "
                "instruments on different response scales, which calls for a "
                "per-scale split (one output file each), not a human decision. "
                "Re-read the item columns by block prefix, confirm each block's "
                "range against the paper's Methods rather than against the "
                "pooled min/max, and check any leftover out-of-range value for "
                "the single-item isolation that marks a keying slip.")

    # ── RULE 11: Low-confidence id mapping only (no hard errors) ────────────
    has_fail = "QC failed" in reasons
    has_big_resp = ">50 unique" in reasons
    has_dup = "dup_id_item" in reasons
    if ("low-confidence" in reasons or "Column mapping was a low-confidence guess" in reasons) \
            and not has_fail and not has_big_resp and not has_dup:
        return ("worth_retrying",
                "Only issue is a low-confidence id column mapping — "
                "re-examine the first column to confirm it is the person identifier; "
                "if so, this dataset may be usable")

    # ── DEFAULT ──────────────────────────────────────────────────────────────
    return ("human_review",
            "No clear automated classification — raw file needs human inspection "
            "to determine IRW eligibility")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

FLAG_ORDER = [
    "not_item_response",
    "wrong_file_selected",
    "recoverable_format",
    "aggregate_continuous",
    "worth_retrying",
    "human_review",
]


HUMAN_REVIEW_DIR = "human_review"

# Columns the existing human_review/*.csv archive uses, in order. A retriage
# output carries these plus whatever the connector added; extras are dropped so
# every file in the directory stays diffable against the others.
HUMAN_REVIEW_COLS = [
    "source", "title", "url", "doi", "license", "flag", "reasons",
    "n_responses", "n_participants", "n_items", "density", "data_file",
    "n_other_files", "refined_flag", "refined_reason",
]


def archive_human_review(retriage_csv, *, source=None, date=None, stream=None):
    """Copy the `human_review` rows of a retriage output into the permanent archive.

    Step 2b's own output is a per-run file under `runs/`, which is gitignored
    and disposable -- so before this existed, an unattended run's `human_review`
    rows died with the container. `human_review/*.csv` is the standing archive
    that replaced the retired "human eye" queue tab (deprecated 2026-08-12), and
    `_load_human_review_exclusions()` reads every file in it on every discovery
    run, so a row that never lands here is a row a future run will re-surface
    and re-triage from scratch. The 2026-09-09 PMC weekly run lost three that
    way (see the 2026-09-09b BATCH_LOG entry); this makes the archive a step
    the runner takes rather than one a caller has to remember.

    Writes `human_review/human_review_<source>_<date>.csv`. Re-running the same
    source on the same day merges into that file and de-duplicates on `doi`
    rather than clobbering it. Returns the path written, or None if the
    retriage held no `human_review` rows.
    """
    import os, sys
    from datetime import date as _date
    stream = stream or sys.stderr

    try:
        df = pd.read_csv(retriage_csv)
    except Exception as exc:
        print(f"!! human_review archive skipped: cannot read {retriage_csv} ({exc})",
              file=stream, flush=True)
        return None
    if "refined_flag" not in df.columns:
        return None
    hr = df[df["refined_flag"] == "human_review"].copy()
    if hr.empty:
        return None

    if source is None:                          # connectors stamp every row with
        col = hr["source"] if "source" in hr.columns else None   # their own name
        source = str(col.mode().iat[0]) if col is not None and not col.mode().empty             else "unknown"
    source = re.sub(r"[^a-z0-9]+", "_", str(source).lower()).strip("_") or "unknown"
    date = date or _date.today().isoformat()

    # Relative to this file, not cwd: a scheduled connector may be invoked from
    # anywhere, and an archive written outside automated_finding/ is one the
    # exclusion loader will never read.
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           HUMAN_REVIEW_DIR)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"human_review_{source}_{date}.csv")

    hr = hr.reindex(columns=HUMAN_REVIEW_COLS)
    n_new = len(hr)
    if os.path.exists(out):
        try:
            prev = pd.read_csv(out).reindex(columns=HUMAN_REVIEW_COLS)
            hr = pd.concat([prev, hr], ignore_index=True)
            if "doi" in hr.columns:
                hr = hr.drop_duplicates(subset="doi", keep="first")
            n_new = len(hr) - len(prev)
        except Exception as exc:                # never lose today's rows to a
            print(f"!! could not merge into {out} ({exc}); "                    # bad
                  f"writing this run's rows only", file=stream, flush=True)     # merge
    hr.to_csv(out, index=False)
    shown = os.path.relpath(out, os.getcwd())      # a connector run from outside
    if shown.startswith(os.pardir):                # the repo gets the plain path
        shown = out                                # rather than a ../../.. chain
    print(f"[human_review] archived {n_new} row(s) -> {shown}", flush=True)
    return out


def chain_step2b(triage_csv, *, run=True, stream=None):
    """Run Step 2b over `triage_csv`'s human_assistance rows, or say it wasn't.

    Step 2b was retitled REQUIRED on 2026-09-07 (#2076), which also gave
    irw_batch_updated.py a --retriage flag to chain it in-process. That fix
    reached exactly one of the four triage entry points: the three scheduled
    connectors (irw_discover_plos_monthly.py, irw_discover_pmc_monthly.py,
    irw_discover_monthly.py) import irw_triage_updated directly and never
    touch irw_batch_updated, so the step stayed unreachable for precisely the
    unattended runs it was written for -- the 2026-09-08 PLOS weekly run
    committed 13 unclassified human_assistance rows nineteen hours after
    #2076 merged. Sharing one implementation is what keeps the next entry
    point from missing it too.

    Returns the retriage output path, or None if there was nothing to do.
    """
    import os, subprocess, sys
    stream = stream or sys.stderr
    try:
        df = pd.read_csv(triage_csv)
    except Exception as exc:                    # a triage CSV we can't read is
        print(f"\n!! Step 2b skipped: cannot read {triage_csv} ({exc})",
              file=stream, flush=True)          # the caller's problem, not ours
        return None
    if "flag" not in df.columns:
        return None
    n_ha = int((df["flag"] == "human_assistance").sum())
    if not n_ha:
        return None

    out = os.path.splitext(str(triage_csv))[0] + ".retriage_ha.csv"
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "irw_retriage_ha.py")
    cmd = [sys.executable, script, "--input", str(triage_csv), "--output", out]
    if not run:
        print(f"\n!! {n_ha} human_assistance row(s) are NOT yet sub-classified.",
              file=stream)
        print("   Step 2b is required before anyone reads this triage: without "
              "it\n   there is no refined_flag column, so the not_item_response "
              "rows\n   can't be dropped and the human_review rows can't be "
              "archived.", file=stream)
        print(f"   Run:  {' '.join(cmd)}", file=stream, flush=True)
        return None

    print(f"\n[step 2b] retriaging {n_ha} human_assistance row(s) -> {out}",
          flush=True)
    rc = subprocess.call(cmd)
    if rc != 0:
        print(f"\n!! Step 2b FAILED (exit {rc}). The triage at {triage_csv} is "
              f"complete but its\n   human_assistance rows are still "
              f"unclassified -- rerun the command above\n   before treating "
              f"this run as done.", file=stream, flush=True)
        raise SystemExit(rc)
    return out


def main():
    import argparse, os, sys
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input",  default="irw_triage.csv",
                    help="triage CSV to read (default: irw_triage.csv)")
    ap.add_argument("--output", default="irw_retriage_ha.csv",
                    help="output CSV (default: irw_retriage_ha.csv)")
    ap.add_argument("--no-archive", action="store_true",
                    help="don't copy the human_review rows into human_review/ "
                         "(default: archive them, since runs/ is disposable)")
    args = ap.parse_args()

    args.input = resolve_in_path(args.input)
    df = pd.read_csv(args.input)
    ha = df[df["flag"] == "human_assistance"].copy()
    print(f"Loaded {len(ha)} human_assistance rows from {args.input}")

    results = [classify(row) for _, row in ha.iterrows()]
    ha["refined_flag"]   = [r[0] for r in results]
    ha["refined_reason"] = [r[1] for r in results]

    # Sort by flag priority
    ha["_order"] = ha["refined_flag"].apply(
        lambda f: FLAG_ORDER.index(f) if f in FLAG_ORDER else 99)
    ha = ha.sort_values("_order").drop(columns="_order").reset_index(drop=True)

    args.output = in_runs_dir(args.output)
    ha.to_csv(args.output, index=False)
    print(f"Wrote {len(ha)} rows to {args.output}\n")

    # runs/ is disposable; human_review/ is not. Archiving here rather than in
    # chain_step2b covers both entry points at once, since that helper reaches
    # this script through main().
    if not args.no_archive:
        archive_human_review(args.output)

    # ── Summary ──────────────────────────────────────────────────────────────
    counts = ha["refined_flag"].value_counts()
    total = len(ha)
    print("=" * 60)
    print("RETRIAGE SUMMARY")
    print("=" * 60)
    descriptions = {
        "not_item_response":   "Clearly not item-response data (drop)",
        "wrong_file_selected": "Right dataset, wrong file — check other files",
        "recoverable_format":  "Wrong delimiter or per-scale split — re-read and re-triage",
        "aggregate_continuous":"Likely continuous / aggregate measures",
        "worth_retrying":      "Plausible data — worth a second download",
        "human_review":        "Genuinely ambiguous — needs human inspection",
    }
    for flag in FLAG_ORDER:
        n = counts.get(flag, 0)
        pct = 100 * n / total if total else 0
        desc = descriptions.get(flag, "")
        print(f"  {flag:22}  {n:3d} ({pct:4.0f}%)  {desc}")
    print("=" * 60)

    # ── Highlight worth_retrying ─────────────────────────────────────────────
    retrying = ha[ha["refined_flag"] == "worth_retrying"]
    if not retrying.empty:
        print(f"\n--- {len(retrying)} worth_retrying cases ---")
        for _, row in retrying.iterrows():
            print(f"  [{row.get('n_participants', '?'):.0f}p / "
                  f"{row.get('n_items', '?'):.0f}i]  "
                  f"{str(row['title'])[:70]}")
            print(f"    {row['refined_reason'][:110]}")
            print(f"    URL: {row.get('url','')}")
            print()

    # ── Highlight recoverable_format ─────────────────────────────────────────
    recoverable = ha[ha["refined_flag"] == "recoverable_format"]
    if not recoverable.empty:
        print(f"\n--- {len(recoverable)} recoverable_format cases ---")
        for _, row in recoverable.iterrows():
            print(f"  {str(row['title'])[:70]}")
            print(f"    {row['refined_reason'][:110]}")
            print(f"    URL: {row.get('url','')}")
            print()

    # ── Highlight wrong_file_selected ────────────────────────────────────────
    wrong = ha[ha["refined_flag"] == "wrong_file_selected"]
    if not wrong.empty:
        print(f"\n--- {len(wrong)} wrong_file_selected cases ---")
        for _, row in wrong.iterrows():
            print(f"  {str(row['title'])[:70]}")
            print(f"    URL: {row.get('url','')}")
            print()


if __name__ == "__main__":
    main()
