"""
irw_retriage_ha.py
==================
Post-hoc refinement of the human_assistance cases in irw_triage_new.csv.

Uses metadata and reason-text patterns (no re-download required) to sub-classify
the 376 human_assistance rows into actionable buckets, reducing the manual review
burden and surfacing datasets that are genuinely worth a second look.

Reason text alone cannot tell a parse failure from aggregate data -- a banner
row, a two-row survey header, a headerless .tsv or covariates melted in beside
the items all read as ">50 unique values" (#2221; 5 of 8 `aggregate_continuous`
rows on the 2026-09-16 PMC batch). So the connectors look again while the file
is in hand (`irw_triage_updated.reread_hint`) and leave a "Re-read with ..."
reason, which Rule 0 below routes to `recoverable_format`.

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
conj                 -- a conjoint experiment: belongs in the `conj` source
                       (Redivis irw_conjoint), not core. Logged as a `todo`
                       (or `held: ...`) row in data/conjoint/candidates.csv.

Output
------
irw_retriage_ha.csv  -- original columns + refined_flag + refined_reason
human_review/human_review_<source>_<date>.csv
                     -- the human_review rows, copied into the permanent
                        archive that discovery runs read for exclusions.
                        Suppress with --no-archive.
data/conjoint/candidates.csv
                     -- conjoint designs, from the human_assistance rows AND
                        from any other row of the triage (a conjoint often
                        triages `good` as a bare id/item/resp file). Appended,
                        never rewritten; a DOI already in the ledger is
                        skipped. Suppress with --no-archive.
"""

from __future__ import annotations

import os
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
# Conjoint designs (#2887)
# ---------------------------------------------------------------------------
# Conjoints used to be skipped as "out of scope" or squashed into a core
# id/item/resp file (the LGBTQ-judges deposit DVN/CDLVDH, batch 19; a PLOS
# tourism choice experiment). Neither is right now that the `conj` source
# exists (Redivis irw_conjoint, data/conjoint/README.md): randomized profile
# attributes are the point of the design, and the core standard cannot hold
# them (itemcov_* must be constant within an item). So a conjoint is routed,
# never built as core and never dropped.

CONJ_TITLE = re.compile(
    r"\bconjoint\b|\bdiscrete[- ]choice\s+experiment|\bchoice[- ]based\s+conjoint",
    re.IGNORECASE)
# Column signals: a task index and a profile index together, the conjoint
# long layout. Either alone is common (a "task" column in a cognitive battery).
_CONJ_TASK_COL = re.compile(r"^(task|task_?(num|no|number|id|index)|choice_?set|contest)$",
                            re.IGNORECASE)
_CONJ_PROFILE_COL = re.compile(r"^(profile|profile_?(num|no|number|id|index)|alternative|alt)$",
                               re.IGNORECASE)


def looks_like_conjoint(title: str, cols) -> str | None:
    """Return why a candidate looks like a conjoint experiment, or None."""
    m = CONJ_TITLE.search(str(title or ""))
    if m:
        return f"title says '{m.group(0)}'"
    names = [str(c).strip() for c in (cols or [])]
    task = [c for c in names if _CONJ_TASK_COL.match(c)]
    prof = [c for c in names if _CONJ_PROFILE_COL.match(c)]
    if task and prof:
        return f"columns {task[0]!r} and {prof[0]!r} (task x profile layout)"
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

    # ── RULE C: conjoint experiment -> the `conj` source, not core ──────────
    # First, ahead of the parse rules: whatever is wrong with the read, a
    # conjoint is built under data/conjoint/'s layout, not re-read for core.
    why = looks_like_conjoint(title, cols)
    if why:
        return ("conj",
                f"Conjoint experiment ({why}) — route to the `conj` source "
                "(data/conjoint/README.md): logged in data/conjoint/candidates.csv, "
                "not built as a core table.")

    # ── RULE 0: triage already re-read the file, and it parsed cleanly ───────
    # reread_hint() (irw_triage_updated, #2221) tries the obvious other reads
    # -- a sniffed delimiter, header=1, a two-row header, no header -- while
    # the file is still in hand, and says so here when one of them triages as
    # good. That is a parse failure, not aggregate data and not "no instrument":
    # on the 2026-09-16 PMC batch 5 of the 8 `aggregate_continuous` rows were
    # a banner row, a two-row SurveyMonkey header or a headerless .tsv.
    # recoverable_format rather than a pass: a clean small-integer block can
    # also be binary covariates, so someone still reads the column names.
    hint = next((p.strip() for p in reasons.split(" | ")
                 if p.strip().startswith("Re-read with")), None)
    if hint:
        return ("recoverable_format", hint)

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
    "conj",
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


CONJ_LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           os.pardir, "data", "conjoint", "candidates.csv")
CONJ_LEDGER_COLS = ["doi", "title", "licence", "lead", "status", "tables", "notes"]

# Intake rules, data/conjoint/README.md. The licence is screened here only so a
# clearly-ineligible deposit is logged as held rather than todo; whoever builds
# a todo row still confirms the licence (CC0, CC BY, CC BY-SA or CC BY-NC, no
# ND) from the Dataverse API.
_CONJ_OK_LICENCE = re.compile(r"cc0|cc[- ]?zero|public[- ]domain|cc[- ]?by\b|"
                              r"creative[- ]commons[- ]attribution", re.IGNORECASE)
# NC is admitted (Ben 2026-10-07, as elsewhere in IRW); ND still stops a deposit.
_CONJ_BAD_LICENCE = re.compile(r"(\bnd\b|no[- ]?deriv|-nd\b|-nd-)", re.IGNORECASE)
_CONJ_NO_LICENCE = re.compile(r"limited[- ]information|^none\b|no[- ]information",
                              re.IGNORECASE)
CONJ_MIN_RESPONDENTS = 100
CONJ_INTAKE_NOTE = ("intake (data/conjoint/README.md): licence CC0/CC BY/CC BY-SA/CC BY-NC "
                    "confirmed from the Dataverse API with no restricted files; "
                    ">=100 respondents; attribute levels as displayed text, "
                    "else hold")


def conj_ledger_row(row, *, lead: str, why: str = "") -> dict:
    """One candidates.csv row for a conjoint lead, screened against the intake rules.

    Status is `todo` unless the triage already shows a rule fails: a named
    licence outside CC0 / CC BY / CC BY-SA / CC BY-NC (any ND), Dataverse's "no information on use"
    text, or fewer than 100 respondents -> `held: <reason>`. A blank or
    `unknown` licence stays `todo`: the triage often misses a licence the
    deposit page states."""
    from irw_discover_updated import norm_doi
    doi = norm_doi(str(row.get("doi") or "")) if pd.notna(row.get("doi")) else ""
    if not doi:
        doi = str(row.get("url") or "").strip()
    lic = row.get("license")
    lic = "" if lic is None or (isinstance(lic, float) and pd.isna(lic)) else str(lic).strip()
    n = row.get("n_participants")
    n = None if n is None or pd.isna(n) else int(n)

    held = []
    if lic and lic.lower() != "unknown":
        if _CONJ_NO_LICENCE.search(lic):
            held.append("no licence")
        elif _CONJ_BAD_LICENCE.search(lic) or not _CONJ_OK_LICENCE.search(lic):
            held.append(f"licence {lic} is not CC0/CC BY/CC BY-SA/CC BY-NC")
    if n is not None and n < CONJ_MIN_RESPONDENTS:
        held.append(f"fewer than {CONJ_MIN_RESPONDENTS} respondents (triage count {n})")

    notes = []
    if n is not None:
        notes.append(f"est. respondents: {n} (triage)")
    if not lic or lic.lower() == "unknown":
        notes.append("licence not found by triage")
    if why:
        notes.append(f"detected: {why}")
    url = row.get("url")
    if url is not None and pd.notna(url) and str(url).strip():
        notes.append(f"url {str(url).strip()}")
    notes.append(CONJ_INTAKE_NOTE)
    return {
        "doi": doi,
        "title": str(row.get("title") or "").strip(),
        "licence": lic or "unknown",
        "lead": lead,
        "status": ("held: " + "; ".join(held)) if held else "todo",
        "tables": "",
        "notes": "; ".join(notes),
    }


def route_conjoints(rows, *, source=None, date=None, ledger=None, stream=None):
    """Append conjoint leads to data/conjoint/candidates.csv, the conj ledger.

    `rows` is a DataFrame of triage rows already judged conjoint; an optional
    `conj_why` column carries the detector's reason. A DOI already in the
    ledger (any status) is skipped, so re-running a batch adds nothing twice
    and a human's later edit to a row is never overwritten. Returns the
    number of rows added."""
    import csv, sys
    from datetime import date as _date
    from irw_discover_updated import norm_doi
    stream = stream or sys.stderr
    ledger = ledger or CONJ_LEDGER
    if rows is None or len(rows) == 0:
        return 0
    if source is None:
        col = rows["source"] if "source" in rows.columns else None
        source = str(col.mode().iat[0]) if col is not None and not col.mode().empty else "unknown"
    lead = f"automated_finding {source} {date or _date.today().isoformat()}"

    have = set()
    if os.path.exists(ledger):
        with open(ledger, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            if list(r.fieldnames or []) != CONJ_LEDGER_COLS:
                print(f"!! conj routing skipped: {ledger} header is "
                      f"{r.fieldnames}, expected {CONJ_LEDGER_COLS}",
                      file=stream, flush=True)
                return 0
            have = {norm_doi(x.get("doi") or "") for x in r}

    new = []
    for _, row in rows.iterrows():
        rec = conj_ledger_row(row, lead=lead, why=str(row.get("conj_why") or ""))
        key = norm_doi(rec["doi"])
        if not key or key in have:
            continue
        have.add(key)
        new.append(rec)
    if not new:
        return 0

    exists = os.path.exists(ledger)
    if exists:                                  # never glue a row onto a last
        with open(ledger, "rb") as f:           # line that lacks its newline
            f.seek(0, os.SEEK_END)
            if f.tell():
                f.seek(-1, os.SEEK_END)
                if f.read(1) != b"\n":
                    with open(ledger, "a", encoding="utf-8") as g:
                        g.write("\n")
    else:
        os.makedirs(os.path.dirname(ledger), exist_ok=True)
    with open(ledger, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CONJ_LEDGER_COLS, lineterminator="\n")
        if not exists:
            w.writeheader()
        w.writerows(new)
    print(f"[conj] routed {len(new)} conjoint lead(s) -> {ledger} "
          f"({sum(r['status'] == 'todo' for r in new)} todo)", flush=True)
    return len(new)


def find_conjoints(df) -> "pd.DataFrame":
    """Rows of a whole triage CSV that look like conjoints, with a `conj_why`
    column. Covers every flag, not just human_assistance: a conjoint's
    profile rows parse as a clean id/item/resp file often enough (DVN/CDLVDH
    triaged `good`)."""
    whys = [looks_like_conjoint(r.get("title"), _cols_from_reasons(str(r.get("reasons") or "")))
            for _, r in df.iterrows()]
    out = df.assign(conj_why=whys)
    return out[out["conj_why"].notna()].drop_duplicates()


def chain_step2b(triage_csv, *, run=True, stream=None):
    """Run Step 2b over `triage_csv`'s human_assistance rows, or say it wasn't.

    Step 2b was retitled REQUIRED on 2026-09-07 (#2076), which also gave
    irw_batch_updated.py a --retriage flag to chain it in-process. That fix
    reached exactly one entry point: the scheduled article connectors
    (irw_discover_plos_monthly.py, irw_discover_pmc_monthly.py) import
    irw_triage_updated directly and never touch irw_batch_updated, so the
    step stayed unreachable for precisely the unattended runs it was written
    for -- the 2026-09-08 PLOS weekly run committed 13 unclassified
    human_assistance rows nineteen hours after #2076 merged.

    The MANUAL connectors (irw_discover_pmc.py, irw_discover_plos.py) were
    then missed in turn, for a year's worth of the same reason: they are the
    same code path as their _monthly wrappers but a different main(). The
    2026-09-22 PMC batch-2 sweep is what caught it -- a hand-fired run whose
    16 human_assistance rows had no refined_flag and whose 3 human_review
    rows were never archived until the step was run by hand. Both call this
    now. irw_discover_monthly.py deliberately does NOT: it is discovery-only
    and emits no flag column, so its candidates reach Step 2b through
    irw_batch_updated --retriage instead.

    Sharing one implementation is what keeps the next entry point from
    missing it too.

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
        # main() routes conjoints, but it never runs on a batch with no
        # human_assistance rows -- and a conjoint can triage `good` (#2887).
        if run:
            conj = find_conjoints(df)
            if not conj.empty:
                route_conjoints(conj)
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
        # Conjoints go to the conj ledger whatever their triage flag (#2887).
        conj = find_conjoints(df)
        if not conj.empty:
            route_conjoints(conj)

    # ── Summary ──────────────────────────────────────────────────────────────
    counts = ha["refined_flag"].value_counts()
    total = len(ha)
    print("=" * 60)
    print("RETRIAGE SUMMARY")
    print("=" * 60)
    descriptions = {
        "conj":                "Conjoint experiment — routed to data/conjoint/candidates.csv",
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
