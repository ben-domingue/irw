#!/usr/bin/env python3
"""
irw_claude_assist.py — Claude-in-the-loop column mapping for human_review rows.

Written by Stacy Cremer (June 2026); brought into the pipeline 2026-11-06.
This is Step 2c of the automated_finding workflow (SKILL.md): it runs on rows
that irw_retriage_ha.py could not classify and archived to human_review/.

For each row it:
  1. PROFILES the file in code (column names, dtypes, sample values, three
     rows — never the full dataset).
  2. Sends the profile, with datastandard.md as the system prompt, to Claude
     and asks for a strict-JSON verdict: a column mapping, or a flag saying
     why not (and which kind of flag).
  3. APPLIES a mapping deterministically with pandas — Claude never touches
     the data — and runs run_qc() plus a few checklist guards.
  4. RECORDS the outcome in leads/claude_assist_ledger.csv. It never writes
     IRW tables: a "lead" verdict is a proposal for a build session, which
     still writes data/<name>.py and checks it against the source.

Verdicts written to the ledger:
  not_item_response  Claude: high confidence the file is not person x item
                     data. Closes the row; nobody needs to open it.
  lead               mapped, QC clean. Build it (see the mapping_json).
  needs_human        mapped with QC failures, mapping rejected by the code,
                     wrong file/sheet read, below the 100-id floor, or any
                     flag short of high-confidence not_item_response.
  not_checked        never reached Claude: several data files, no tabular
                     file, blocked licence, download or API error.

Usage:
  # Step 2c: the next 25 unchecked rows of the human_review/ archive,
  # through the logged-in Claude Code CLI (no API key needed):
  python irw_claude_assist.py --archive --limit 25 --backend cli

  # Rows from any triage CSV:
  python irw_claude_assist.py --input runs/irw_triage.csv --limit 5

  # One local file:
  python irw_claude_assist.py --file raw/messy.xlsx --name smith_2024_anxiety
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
import time

import pandas as pd
import requests

from irw_triage_updated import load_table, run_qc

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-5-5"          # swap via --model if needed
BACKEND = "api"                              # or "cli" (claude -p)
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "leads", "claude_assist_ledger.csv")
HUMAN_REVIEW_DIR = os.path.join(HERE, "human_review")

# Where datastandard.md lives relative to this script (repo root).
DATASTANDARD_CANDIDATES = [
    os.path.join(HERE, "..", "datastandard.md"),
    os.path.join(HERE, "datastandard.md"),
]


# ---------------------------------------------------------------------------
# 1. PROFILE — compact, code-built summary of the raw file
# ---------------------------------------------------------------------------

def _sample_values(s: pd.Series, k: int = 8) -> list:
    vals = s.dropna().unique()[:k]
    out = []
    for v in vals:
        v = str(v)
        out.append(v[:40] + "…" if len(v) > 40 else v)
    return out


def profile_dataframe(df: pd.DataFrame, filename: str = "") -> dict:
    """Column-level profile sent to Claude. Never includes the full data."""
    cols = []
    for c in df.columns:
        s = df[c]
        info = {
            "name": str(c),
            "dtype": str(s.dtype),
            "n_unique": int(s.nunique(dropna=True)),
            "pct_missing": round(float(s.isna().mean()) * 100, 1),
            "sample_values": _sample_values(s),
        }
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            info["min"] = float(s.min())
            info["max"] = float(s.max())
        cols.append(info)
    return {
        "filename": filename,
        "n_rows": int(len(df)),
        "n_cols": int(df.shape[1]),
        "columns": cols,
        "first_rows": df.head(3).astype(str).to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# 2. ASK CLAUDE — datastandard.md is the system prompt; output is strict JSON
# ---------------------------------------------------------------------------

MAPPING_INSTRUCTIONS = """
You will receive a JSON profile of a raw dataset (column names, dtypes,
sample values — not the full data). Using the IRW data standard above,
decide how to map this file into IRW long format.

Respond with ONLY a JSON object — no markdown fences, no prose — with
exactly these keys:

{
  "decision": "map" | "flag",
  "flag_reason": "",                  // why a human must look (if decision=flag)
  "flag_kind": "",                    // if decision=flag, exactly one of:
                                      // "not_item_response" (no person x item
                                      //   responses anywhere in this file),
                                      // "wrong_file" (codebook, README or
                                      //   summary sheet; the data is likely
                                      //   in another file or sheet),
                                      // "below_floor" (item responses, but
                                      //   under 100 unique ids),
                                      // "other"
  "id_strategy": "column" | "row_index",
  "id_col": "",                       // source column name (if id_strategy=column)
  "scales": [                         // one entry per output file
    {"out_suffix": "anxiety",         // appended to dataset name
     "item_cols": ["A1","A2"],        // exact source column names to melt
     "valid_min": 1, "valid_max": 5,  // null if unknown
     "value_labels": {}}              // text response -> number, e.g.
                                      // {"Strongly disagree": 1, ...};
                                      // keys are the response text as it
                                      // appears (case/whitespace ignored).
                                      // Use when responses are words.
  ],
  "cov_cols": {"Age": "cov_age"},     // source name -> cov_* rename
  "itemcov_cols": {},
  "exclude_cols": ["A_total"],        // aggregates, free text, metadata
  "wave_col": null, "treat_col": null, "rt_col": null,
  "rt_unit": null,                    // "s" or "ms" if rt_col set
  "sentinel_values": [99, 999],       // codes meaning missing
  "confidence": "high" | "medium" | "low",
  "reasoning": "2-4 sentences: why these choices."
}

Rules of engagement:
- Choose decision="flag" whenever the standard says to (trials/process data,
  multiple plausible data files, no identifiable response columns, license
  doubt) or when you are genuinely unsure. Flagging is success, not failure.
- item_cols must be exact column names from the profile. Never invent names.
- Do not recode reverse-scored items; do not impute.
- If the file appears to already be in long format (id/item/resp present),
  say so via reasoning and map those columns directly using a single scale
  whose item_cols is the existing item column: use {"long_format": true,
  "id_col": ..., "item_col": ..., "resp_col": ...} as an extra top-level key
  and leave scales empty.
"""


def load_datastandard(path: str | None = None) -> str:
    paths = [path] if path else DATASTANDARD_CANDIDATES
    for p in paths:
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return f.read()
    sys.exit("datastandard.md not found — pass --standard /path/to/datastandard.md")


def _ask_claude_cli(profile: dict, standard: str, model: str) -> str:
    """Same request through the Claude Code CLI (`claude -p`), using the
    logged-in session instead of an API key. No tools, no session saved."""
    import subprocess
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(standard + "\n\n---\n" + MAPPING_INSTRUCTIONS)
        sys_path = tf.name
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", model, "--tools", "",
             "--no-session-persistence", "--system-prompt-file", sys_path,
             "--output-format", "text"],
            input=json.dumps(profile, ensure_ascii=False),
            capture_output=True, text=True, timeout=600)
    finally:
        os.unlink(sys_path)
    if r.returncode != 0:
        raise RuntimeError(f"claude -p exited {r.returncode}: {r.stderr[:200]}")
    return r.stdout


def _parse_mapping(text: str) -> dict:
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    # tolerate prose around the object
    i, j = text.find("{"), text.rfind("}")
    return json.loads(text[i:j + 1] if i >= 0 and j > i else text)


def ask_claude(profile: dict, standard: str, model: str) -> dict:
    if BACKEND == "cli":
        return _parse_mapping(_ask_claude_cli(profile, standard, model))
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Set ANTHROPIC_API_KEY in your environment, or use --backend cli.")
    body = {
        "model": model,
        "max_tokens": 2000,
        "system": standard + "\n\n---\n" + MAPPING_INSTRUCTIONS,
        "messages": [{"role": "user",
                      "content": json.dumps(profile, ensure_ascii=False)}],
    }
    for attempt in range(3):
        r = requests.post(
            API_URL,
            headers={"x-api-key": api_key,
                     "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json=body, timeout=120)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(5 * (attempt + 1))
            continue
        r.raise_for_status()
        break
    else:
        raise RuntimeError("Claude API kept failing (rate limit / server error).")
    text = "".join(b.get("text", "") for b in r.json()["content"]
                   if b.get("type") == "text")
    return _parse_mapping(text)


# ---------------------------------------------------------------------------
# 3. APPLY — deterministic pandas execution of Claude's mapping + QC
# ---------------------------------------------------------------------------

def apply_mapping(df: pd.DataFrame, m: dict, base_name: str) -> list[dict]:
    """Execute the mapping. Returns one result dict per output scale.
    Raises ValueError on anything inconsistent — caller records the failure."""
    results = []
    src_cols = set(map(str, df.columns))
    df = df.copy()
    df.columns = [str(c) for c in df.columns]

    # --- id ---------------------------------------------------------------
    if m.get("long_format"):
        lf = m["long_format"] if isinstance(m["long_format"], dict) else m
        for k in ("id_col", "item_col", "resp_col"):
            if lf.get(k) not in src_cols:
                raise ValueError(f"long_format {k}={lf.get(k)!r} not in file")
        out = df.rename(columns={lf["id_col"]: "id", lf["item_col"]: "item",
                                 lf["resp_col"]: "resp"})
        out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
        out = out.dropna(subset=["resp"])
        out = out[["id", "item", "resp"]]
        return [_finish(out, base_name, m, None)]

    if m.get("id_strategy") == "column":
        id_col = m.get("id_col")
        if id_col not in src_cols:
            raise ValueError(f"id_col {id_col!r} not in file")
        df = df.rename(columns={id_col: "id"})
    else:
        df = df.reset_index(drop=True)
        if "id" in df.columns:          # an unusable source id: keep it out
            df = df.drop(columns=["id"])
        df.insert(0, "id", df.index + 1)

    # --- covariates ---------------------------------------------------------
    cov_map = {}
    for src, dst in (m.get("cov_cols") or {}).items():
        if src not in src_cols:
            raise ValueError(f"cov col {src!r} not in file")
        if not dst.startswith("cov_"):
            dst = "cov_" + re.sub(r"\W+", "_", dst.lower())
        cov_map[src] = dst
    df = df.rename(columns=cov_map)
    cov_cols = list(cov_map.values())

    # --- per-scale melt -----------------------------------------------------
    if not m.get("scales"):
        raise ValueError("mapping has no scales")
    for sc in m["scales"]:
        missing = [c for c in sc["item_cols"] if c not in df.columns]
        if missing:
            raise ValueError(f"item cols not in file: {missing[:5]}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=sc["item_cols"],
                       var_name="item", value_name="resp")
        labels = {str(k).strip().casefold(): v
                  for k, v in (sc.get("value_labels") or {}).items()}
        if labels:
            raw = long["resp"].astype("string").str.strip().str.casefold()
            unmapped = sorted(set(raw.dropna()) - set(labels))
            if unmapped:
                # Refuse rather than silently drop a response category.
                raise ValueError(f"value_labels miss {len(unmapped)} "
                                 f"response(s): {unmapped[:5]}")
            long["resp"] = raw.map(labels)
        nonblank = long["resp"].notna() & \
            (long["resp"].astype("string").str.strip() != "")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        # Text that is not a number is a finding, not a missing value (the
        # literal-"NA" lesson, #2029): count it so QC can fail on it.
        n_nonnumeric = int((nonblank & long["resp"].isna()).sum())
        long = long.dropna(subset=["resp"])
        for s in (m.get("sentinel_values") or []):
            long = long[long["resp"] != s]
        # valid_min/valid_max are NOT used to filter: dropping responses
        # outside a declared range alters the data. _extra_checks reports
        # them as resp_out_of_range, a QC failure (verdict needs_human).
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        name = base_name + ("_" + sc["out_suffix"] if sc.get("out_suffix") else "")
        results.append(_finish(long, name, m,
                               {**sc, "_n_nonnumeric": n_nonnumeric}))
    return results


SUSPECT_ITEM_NAMES = re.compile(
    r"^(age|gender|sex|education|edu|income|region|country|group|cond(ition)?"
    r"|date|time(stamp)?|year|id|subject|participant)s?$", re.I)


def _extra_checks(long: pd.DataFrame, sc: dict | None) -> list[tuple[str, str, str]]:
    """Code-side guards for datastandard.md's verification checklist items
    that run_qc does not cover. Returns (status, name, detail) tuples."""
    out = []
    # Checklist #2: covariate accidentally melted in as an item.
    bad_items = [i for i in long["item"].unique() if SUSPECT_ITEM_NAMES.match(str(i))]
    if bad_items:
        out.append(("fail", "covariate_as_item",
                    f"item names look like covariates: {bad_items[:5]}"))
    # Checklist #3: unexpected values when a scale range was declared.
    if sc and sc.get("valid_max") is not None:
        if long["resp"].max() > sc["valid_max"] or long["resp"].min() < (sc.get("valid_min") or 0):
            out.append(("fail", "resp_out_of_range",
                        f"resp {long['resp'].min()}-{long['resp'].max()} outside "
                        f"declared {sc.get('valid_min')}-{sc['valid_max']}"))
    if sc and sc.get("_n_nonnumeric"):
        out.append(("fail", "resp_nonnumeric",
                    f"{sc['_n_nonnumeric']} non-blank response(s) are not "
                    f"numbers and have no value_labels entry"))
    # Mirrors retriage heuristic: too many unique resp values -> maybe continuous/aggregate.
    if long["resp"].nunique() > 50:
        out.append(("warn", "many_unique_resp",
                    f"{long['resp'].nunique()} unique resp values — continuous measure?"))
    return out


def _finish(long: pd.DataFrame, name: str, m: dict, sc: dict | None) -> dict:
    if long.empty:
        raise ValueError(f"{name}: 0 rows after cleaning")
    checks = run_qc(long, coercion_method="claude_mapping")
    extra = _extra_checks(long, sc)
    n_err = sum(1 for c in checks if getattr(c, "status", "") == "fail") \
        + sum(1 for s, _, _ in extra if s == "fail")
    n_warn = sum(1 for c in checks if getattr(c, "status", "") == "warn") \
        + sum(1 for s, _, _ in extra if s == "warn")
    return {"out_name": name + ".csv", "df": long,
            "rows": len(long), "ids": long["id"].nunique(),
            "items": long["item"].nunique(),
            "resp_min": float(long["resp"].min()),
            "resp_max": float(long["resp"].max()),
            "qc_errors": n_err, "qc_notes": n_warn,
            "qc_detail": "; ".join(
                [f"{getattr(c,'status','?')}:{getattr(c,'name','')}:{getattr(c,'detail','')[:60]}"
                 for c in checks if getattr(c, "status", "") != "pass"]
                + [f"{s}:{n}:{d[:60]}" for s, n, d in extra])[:400]}


# ---------------------------------------------------------------------------
# 4. DRIVER
# ---------------------------------------------------------------------------

def process_dataframe(df, base_name, standard, model, writer):
    profile = profile_dataframe(df, base_name)
    try:
        mapping = ask_claude(profile, standard, model)
    except Exception as e:
        writer({"dataset": base_name, "status": "api_error", "detail": str(e)[:200]})
        return
    if mapping.get("decision") == "flag":
        writer({"dataset": base_name, "status": "flagged_by_claude",
                "flag_kind": mapping.get("flag_kind", ""),
                "confidence": mapping.get("confidence", ""),
                "detail": mapping.get("flag_reason", ""),
                "reasoning": mapping.get("reasoning", ""),
                "mapping_json": json.dumps(mapping)})
        return
    try:
        results = apply_mapping(df, mapping, base_name)
    except (ValueError, KeyError) as e:
        writer({"dataset": base_name, "status": "mapping_invalid",
                "confidence": mapping.get("confidence", ""),
                "detail": str(e)[:200],
                "reasoning": mapping.get("reasoning", ""),
                "mapping_json": json.dumps(mapping)})
        return
    for r in results:
        writer({"dataset": base_name, "status": "mapped",
                "out_name": r["out_name"],
                "rows": r["rows"], "ids": r["ids"], "items": r["items"],
                "resp_range": f"{r['resp_min']:.0f}-{r['resp_max']:.0f}",
                "qc_errors": r["qc_errors"], "qc_notes": r["qc_notes"],
                "qc_detail": r["qc_detail"],
                "confidence": mapping.get("confidence", ""),
                "reasoning": mapping.get("reasoning", ""),
                "mapping_json": json.dumps(mapping)})
        print(f"  {r['out_name']}: rows={r['rows']} ids={r['ids']} "
              f"items={r['items']} resp={r['resp_min']:.0f}-{r['resp_max']:.0f} "
              f"qc_errors={r['qc_errors']}")


FIELDNAMES = ["dataset", "status", "license", "out_name", "rows", "ids",
              "items", "resp_range", "qc_errors", "qc_notes", "qc_detail",
              "flag_kind", "confidence", "detail", "reasoning", "mapping_json"]

LEDGER_FIELDS = ["doi", "source", "url", "title", "verdict", "checked",
                 "model"] + FIELDNAMES


def verdict_for(r: dict) -> str:
    """The ledger verdict for one result row. Only a high-confidence
    not_item_response flag closes a row without a person looking."""
    st = r.get("status")
    if st == "flagged_by_claude":
        if (r.get("flag_kind") == "not_item_response"
                and r.get("confidence") == "high"):
            return "not_item_response"
        return "needs_human"
    if st == "mapped":
        return "lead" if str(r.get("qc_errors")) in ("0", "0.0") else "needs_human"
    if st == "mapping_invalid":
        return "needs_human"
    if st == "already_worked":
        return "already_worked"
    return "not_checked"


def load_ledger_dois(path: str = LEDGER) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {(r.get("doi") or "").strip().lower()
                for r in csv.DictReader(f) if r.get("doi")}


def append_ledger(rows: list[dict], path: str = LEDGER) -> None:
    """Append rows; a DOI checked again replaces its earlier rows."""
    if not rows:
        return
    new_dois = {r["doi"].strip().lower() for r in rows}
    old = []
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as f:
            old = [r for r in csv.DictReader(f)
                   if (r.get("doi") or "").strip().lower() not in new_dois]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(old + rows)


def archive_rows(directory: str = HUMAN_REVIEW_DIR) -> list[dict]:
    """Every row of the human_review/ archive, newest file first, one per
    DOI. googlesheet_humaneye.csv is the retired sheet export and is left
    out: its rows predate the archive and were worked by hand."""
    import glob
    out, seen = [], set()
    paths = sorted(glob.glob(os.path.join(directory, "human_review_*.csv")),
                   key=os.path.getmtime, reverse=True)
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                doi = (r.get("doi") or "").strip().lower()
                if doi and doi not in seen:
                    seen.add(doi)
                    out.append(r)
    return out


_WORKED_CORPUS: dict | None = None


def deposit_key(doi: str) -> str:
    """The distinctive part of a deposit DOI, as build scripts cite it:
    10.17632/nr9388gbzf.1 -> nr9388gbzf, 10.5281/zenodo.14870714 ->
    14870714, 10.6084/m9.figshare.30995812.v1 -> 30995812,
    10.7910/dvn/4y3y23 -> 4y3y23. "" when too short to search safely."""
    d = (doi or "").strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    tail = d.split("/", 1)[-1]
    tail = re.sub(r"\.v?\d{1,2}$", "", tail)             # version suffix
    tail = re.sub(r"^(zenodo|m9\.figshare|figshare|dvn/|journal\.)", "", tail)
    tail = tail.strip("./")
    tail = tail.rsplit("/", 1)[-1]
    return tail if len(tail) >= 6 else ""


def already_worked(doi: str, repo_root: str | None = None) -> str:
    """Where this deposit has already been dealt with, or "".

    Discovery's exclusion (_load_auto_exclusions) matches the IRW dictionary
    on DOIs, and the dictionary often holds the PAPER DOI, not the deposit's:
    zenodo.14870714 (sanchezgarcia_2025_*) and 10.17632/nr9388gbzf
    (mellat_2022_*) both sat in human_review/ after they shipped. So search
    for the deposit key in the build scripts, biblio.csv and the hand-recheck
    ledgers instead."""
    global _WORKED_CORPUS
    key = deposit_key(doi)
    if not key:
        return ""
    if _WORKED_CORPUS is None:
        import glob
        root = repo_root or os.path.join(HERE, "..")
        paths = (glob.glob(os.path.join(root, "data", "**", "*.py"), recursive=True)
                 + glob.glob(os.path.join(root, "metadata", "biblio.csv"))
                 + glob.glob(os.path.join(HERE, "leads", "human_review_recheck_*.csv")))
        _WORKED_CORPUS = {}                    # token -> first file citing it
        tok = re.compile(r"[0-9a-z]+(?:\.[0-9a-z]+)*")
        for p in paths:
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    text = f.read().lower()
            except OSError:
                continue
            rel = os.path.relpath(p, root)
            for t in set(tok.findall(text)):
                # whole dotted run and each dotted part: "zenodo.14870714"
                # also indexes "14870714", "pone.0273971" stays whole
                for part in {t, *t.split(".")}:
                    _WORKED_CORPUS.setdefault(part, rel)
    return _WORKED_CORPUS.get(key, "")


def check_row(row: dict, i: int, standard: str, model: str) -> list[dict]:
    """Resolve, download and map one triage/archive row. Returns its
    result rows (one per output scale, or one status row)."""
    from irw_batch_updated import resolve_data_files, polite_get, \
        check_license, TABULAR_EXT
    results = []
    writer = results.append
    base = re.sub(r"\W+", "_", (row.get("doi") or row.get("title") or
                                f"dataset_{i}").lower()).strip("_")
    lic_name = ""
    hit = already_worked(row.get("doi") or "")
    if hit:
        return [{"dataset": base, "status": "already_worked",
                 "detail": f"deposit cited in {hit}"}]
    try:
        if (row.get("source") or "").lower() == "plos":
            # resolve_data_files has no PLOS branch: the connector reads SI
            # files off the article page in-process.
            from irw_discover_plos import (fetch_plos_article,
                                           extract_si_files, extract_license)
            jm = re.search(r"journals\.plos\.org/([a-z]+)/", row.get("url") or "")
            html = fetch_plos_article(row["url"])
            files = extract_si_files(html, row.get("doi") or "",
                                     jm.group(1) if jm else "plosone")
            license_raw = extract_license(html)
            # the triage row already names the file it read
            want = (row.get("data_file") or "").strip()
            if want and any(n == want for _, n, *_ in files):
                files = [f for f in files if f[1] == want]
        else:
            files, license_raw, _oversized = resolve_data_files(row)
        # Same rule as irw_batch_updated: only a blocked licence stops here;
        # an unknown one is recorded for the reviewer.
        license_raw = license_raw or row.get("license") or ""
        lic_name, lic_blocked, _ = check_license(license_raw)
        if lic_blocked:
            return [{"dataset": base, "status": "license_not_open",
                     "license": lic_name, "detail": f"license={lic_name}"}]
        tabular = [(u, n) for u, n, *_ in files
                   if str(n).lower().endswith(TABULAR_EXT)]
        if not tabular:
            return [{"dataset": base, "status": "no_tabular_file",
                     "license": lic_name,
                     "detail": f"{len(files)} files, none tabular"}]
        # datastandard.md: multiple data files -> flag, don't guess.
        if len(tabular) > 1:
            return [{"dataset": base, "status": "multiple_files",
                     "license": lic_name,
                     "detail": "; ".join(n for _, n in tabular[:6])}]
        url, fname = tabular[0]
        df = load_table(polite_get(url).content, fname or url)
    except Exception as e:
        return [{"dataset": base, "status": "download_error",
                 "license": lic_name, "detail": str(e)[:200]}]
    process_dataframe(df, base, standard, model, writer)
    return [{**r, "license": lic_name} for r in results]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--archive", action="store_true",
                     help="unchecked rows of human_review/ (Step 2c); "
                          "results go to leads/claude_assist_ledger.csv")
    src.add_argument("--input", help="a triage CSV (irw_batch_updated.py)")
    src.add_argument("--file", help="single local data file (csv/tsv/xlsx)")
    p.add_argument("--name", default="", help="output base name for --file "
                   "(authorname_year_construct)")
    p.add_argument("--flags", default="human_assistance,human_review",
                   help="--input only: triage flags to check (comma-separated)")
    p.add_argument("--limit", type=int, default=0, help="max datasets to check")
    p.add_argument("--recheck", action="store_true",
                   help="--archive: include DOIs already in the ledger")
    p.add_argument("--out", default="",
                   help="results CSV (default for --input/--file: "
                        "irw_claude_suggestions.csv; --archive writes the ledger)")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--backend", choices=["api", "cli"], default="api",
                   help="api: ANTHROPIC_API_KEY; cli: the logged-in `claude -p`")
    p.add_argument("--standard", default=None, help="path to datastandard.md")
    a = p.parse_args()
    global BACKEND
    BACKEND = a.backend

    standard = load_datastandard(a.standard)
    rows_out = []

    if a.file:
        base = a.name or re.sub(r"\.\w+$", "", os.path.basename(a.file)).lower()
        df = load_table(a.file)
        print(f"[1/1] {base}  ({df.shape[0]} rows x {df.shape[1]} cols)")
        process_dataframe(df, base, standard, a.model, rows_out.append)
    else:
        if a.archive:
            todo = archive_rows()
            if not a.recheck:
                done = load_ledger_dois()
                todo = [r for r in todo
                        if (r.get("doi") or "").strip().lower() not in done]
            print(f"{len(todo)} unchecked human_review row(s)")
        else:
            wanted = {f.strip() for f in a.flags.split(",")}
            with open(a.input, newline="", encoding="utf-8") as f:
                todo = [r for r in csv.DictReader(f) if r.get("flag") in wanted]
            print(f"{len(todo)} triage rows with flag in {sorted(wanted)}")
        if a.limit:
            todo = todo[:a.limit]
        today = time.strftime("%Y-%m-%d")
        for i, row in enumerate(todo, 1):
            print(f"[{i}/{len(todo)}] {row.get('doi') or row.get('title')}")
            for r in check_row(row, i, standard, a.model):
                r.update({"doi": row.get("doi", ""), "source": row.get("source", ""),
                          "url": row.get("url", ""),
                          "title": (row.get("title") or "")[:200],
                          "checked": today, "model": a.model})
                r["verdict"] = verdict_for(r)
                rows_out.append(r)
            if a.archive:
                # write as we go: a long run that dies keeps what it did
                append_ledger([r for r in rows_out
                               if r["doi"] == row.get("doi", "")])

    if not a.archive:
        out = a.out or "irw_claude_suggestions.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows_out)
        print(f"\nWrote {len(rows_out)} result rows to {out}")
    else:
        print(f"\nLedger: {LEDGER}")
    from collections import Counter
    v = Counter(r.get("verdict") or r.get("status") for r in rows_out)
    print("  " + "   ".join(f"{k}: {n}" for k, n in sorted(v.items())))


if __name__ == "__main__":
    main()
