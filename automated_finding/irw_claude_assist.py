#!/usr/bin/env python3
"""
irw_claude_assist.py — Claude-in-the-loop column mapping for the IRW pipeline.

Sits between triage and human review. For datasets the heuristics in
irw_triage_updated.py could not coerce (the human_assistance / human_review
buckets), this script:

  1. PROFILES the file in code (column names, dtypes, sample values — never
     the full dataset).
  2. Sends the profile + datastandard.md to the Claude API and asks for a
     strict-JSON column mapping (which column is id, which columns are items,
     which scales exist, sentinel codes, etc.).
  3. APPLIES the mapping deterministically with pandas — Claude never touches
     the data itself — and runs the existing run_qc() checks.
  4. Writes cleaned files ONLY if QC passes and --apply is set; otherwise
     records the suggestion, Claude's reasoning, and the QC outcome in a CSV
     for fast human review.

Division of labour: Claude does the judgment, code does the work, QC and a
human get the final say.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...

  # Single local file (good for testing / Colab):
  python irw_claude_assist.py --file raw/messy.xlsx --name smith_2024_anxiety

  # Rows from a triage run (re-downloads each file):
  python irw_claude_assist.py --input irw_triage.csv --flags human_assistance --limit 5

  # Actually write cleaned CSVs when QC passes:
  python irw_claude_assist.py --input irw_triage.csv --apply

Requires: pandas, requests, and irw_triage_updated.py on the path
(plus irw_batch_updated.py when using --input).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time

import pandas as pd
import requests

from irw_triage_updated import load_table, run_qc

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-6"          # swap via --model if needed
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "irw_output", "cleaned")

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
  "id_strategy": "column" | "row_index",
  "id_col": "",                       // source column name (if id_strategy=column)
  "scales": [                         // one entry per output file
    {"out_suffix": "anxiety",         // appended to dataset name
     "item_cols": ["A1","A2"],        // exact source column names to melt
     "valid_min": 1, "valid_max": 5}  // null if unknown
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


def ask_claude(profile: dict, standard: str, model: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Set ANTHROPIC_API_KEY in your environment.")
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
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


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
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        for s in (m.get("sentinel_values") or []):
            long = long[long["resp"] != s]
        vmin, vmax = sc.get("valid_min"), sc.get("valid_max")
        if vmin is not None and vmax is not None:
            long = long[(long["resp"] >= vmin) & (long["resp"] <= vmax)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        name = base_name + ("_" + sc["out_suffix"] if sc.get("out_suffix") else "")
        results.append(_finish(long, name, m, sc))
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

def process_dataframe(df, base_name, standard, model, apply_files, writer):
    profile = profile_dataframe(df, base_name)
    try:
        mapping = ask_claude(profile, standard, model)
    except Exception as e:
        writer({"dataset": base_name, "status": "api_error", "detail": str(e)[:200]})
        return
    if mapping.get("decision") == "flag":
        writer({"dataset": base_name, "status": "flagged_by_claude",
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
        saved = ""
        if apply_files and r["qc_errors"] == 0:
            os.makedirs(OUT_DIR, exist_ok=True)
            path = os.path.join(OUT_DIR, r["out_name"])
            r["df"].to_csv(path, index=False)
            saved = path
        writer({"dataset": base_name, "status": "mapped",
                "out_name": r["out_name"], "saved_to": saved,
                "rows": r["rows"], "ids": r["ids"], "items": r["items"],
                "resp_range": f"{r['resp_min']:.0f}-{r['resp_max']:.0f}",
                "qc_errors": r["qc_errors"], "qc_notes": r["qc_notes"],
                "qc_detail": r["qc_detail"],
                "confidence": mapping.get("confidence", ""),
                "reasoning": mapping.get("reasoning", ""),
                "mapping_json": json.dumps(mapping)})
        print(f"  {r['out_name']}: rows={r['rows']} ids={r['ids']} "
              f"items={r['items']} resp={r['resp_min']:.0f}-{r['resp_max']:.0f} "
              f"qc_errors={r['qc_errors']}"
              + (f"  -> {saved}" if saved else "  (dry run — use --apply to save)"))


FIELDNAMES = ["dataset", "status", "out_name", "saved_to", "rows", "ids",
              "items", "resp_range", "qc_errors", "qc_notes", "qc_detail",
              "confidence", "detail", "reasoning", "mapping_json"]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", help="single local data file (csv/tsv/xlsx)")
    src.add_argument("--input", help="triage CSV from irw_batch_updated.py")
    p.add_argument("--name", default="", help="output base name for --file "
                   "(authorname_year_construct)")
    p.add_argument("--flags", default="human_assistance,human_review",
                   help="triage flags to re-process (comma-separated)")
    p.add_argument("--limit", type=int, default=0, help="max datasets to process")
    p.add_argument("--out", default="irw_claude_suggestions.csv")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--standard", default=None, help="path to datastandard.md")
    p.add_argument("--apply", action="store_true",
                   help="write cleaned CSVs when QC passes (default: dry run)")
    a = p.parse_args()

    standard = load_datastandard(a.standard)

    rows_out = []
    writer = rows_out.append

    if a.file:
        base = a.name or re.sub(r"\.\w+$", "", os.path.basename(a.file)).lower()
        df = load_table(a.file)
        print(f"[1/1] {base}  ({df.shape[0]} rows x {df.shape[1]} cols)")
        process_dataframe(df, base, standard, a.model, a.apply, writer)
    else:
        from irw_batch_updated import resolve_data_files, polite_get, \
            check_license, TABULAR_EXT
        wanted = {f.strip() for f in a.flags.split(",")}
        with open(a.input, newline="", encoding="utf-8") as f:
            triage_rows = [r for r in csv.DictReader(f)
                           if r.get("flag") in wanted]
        if a.limit:
            triage_rows = triage_rows[:a.limit]
        print(f"{len(triage_rows)} triage rows with flag in {sorted(wanted)}")
        for i, row in enumerate(triage_rows, 1):
            base = re.sub(r"\W+", "_", (row.get("doi") or row.get("title") or
                                        f"dataset_{i}").lower()).strip("_")
            print(f"[{i}/{len(triage_rows)}] {base}")
            try:
                files, license_raw = resolve_data_files(row)
                # datastandard.md: license must be explicitly open -> else STOP.
                # check_license returns (normalized, is_blocked, is_unknown);
                # both blocked and unknown/missing mean stop.
                lic_name, lic_blocked, lic_unknown = check_license(license_raw)
                if lic_blocked or lic_unknown:
                    writer({"dataset": base, "status": "license_not_open",
                            "detail": f"license={lic_name or license_raw or 'missing'}"})
                    continue
                tabular = [(u, n) for u, n in files
                           if str(n).lower().endswith(TABULAR_EXT)]
                if not tabular:
                    writer({"dataset": base, "status": "no_tabular_file",
                            "detail": f"{len(files)} files, none tabular"})
                    continue
                # datastandard.md: multiple data files -> flag, don't guess.
                if len(tabular) > 1:
                    writer({"dataset": base, "status": "multiple_files",
                            "detail": "; ".join(n for _, n in tabular[:6])})
                    continue
                url, fname = tabular[0]
                df = load_table(polite_get(url).content, fname or url)
            except Exception as e:
                writer({"dataset": base, "status": "download_error",
                        "detail": str(e)[:200]})
                continue
            process_dataframe(df, base, standard, a.model, a.apply, writer)

    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows_out)
    print(f"\nWrote {len(rows_out)} result rows to {a.out}")
    n_ok = sum(1 for r in rows_out if r.get("status") == "mapped")
    n_fl = sum(1 for r in rows_out if r.get("status") == "flagged_by_claude")
    print(f"  mapped: {n_ok}   flagged for human: {n_fl}   "
          f"errors: {len(rows_out) - n_ok - n_fl}")


if __name__ == "__main__":
    main()
