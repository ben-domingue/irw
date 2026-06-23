"""
irw_retry_dup.py
================
Retry rows flagged worth_retrying (dup_id_item failures with valid licenses).

The original triage only looked for columns named exactly 'wave', 'timepoint',
or 'date'. Many real datasets use other names for the time dimension. This
script downloads each file, tries a broader set of disambiguation strategies,
and writes cleaned IRW files where possible.

Output:
  irw_output/cleaned/<name>_<scale>.csv  — cleaned long-format files
  irw_retry_results.csv                  — one row per input row with outcome
"""

from __future__ import annotations

import io
import re
import sys
import time
import csv
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from irw_batch_updated import resolve_data_files, polite_get, TABULAR_EXT
from irw_triage_updated import coerce_to_irw, run_qc, load_table

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"
RETRY_QUEUE = Path(__file__).parent / "irw_retry_queue.csv"
RESULTS    = Path(__file__).parent / "irw_retry_results.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Patterns that suggest a time/wave/condition column
WAVE_PATTERNS = re.compile(
    r"^(wave|time|session|visit|round|period|phase|assessment|occasion|"
    r"measure|point|t\d+|pre|post|cond|condition|group|cohort|year|month|"
    r"week|day|arm|block|run|trial_block)$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_wave_col(df: pd.DataFrame, id_col: str) -> str | None:
    """Return the best candidate column for a wave/timepoint disambiguator."""
    candidates = []
    for col in df.columns:
        if col in (id_col, "id", "item", "resp"):
            continue
        name = col.strip().lower()
        # Name match
        name_match = bool(WAVE_PATTERNS.match(name))
        # Low cardinality (2–20 distinct values) and numeric or short string
        n_uniq = df[col].nunique(dropna=True)
        low_card = 2 <= n_uniq <= 20
        if (name_match or low_card) and not pd.api.types.is_float_dtype(df[col]):
            candidates.append((col, name_match, n_uniq))

    if not candidates:
        return None
    # Prefer name-matched, then lowest cardinality
    candidates.sort(key=lambda x: (not x[1], x[2]))
    return candidates[0][0]


def _try_fix(df_raw: pd.DataFrame, data_file: str) -> dict:
    """
    Attempt to produce a valid IRW long-format DataFrame.
    Returns a dict with keys: status, dfs (list of DataFrames), notes.
    """
    coercion = coerce_to_irw(df_raw)
    if coercion.df is None:
        return {"status": "coercion_failed", "dfs": [], "notes": coercion.notes}

    df = coercion.df.copy()
    notes = list(coercion.notes)

    # Check for dup_id_item
    dups = df.duplicated(subset=["id", "item"]).sum()
    if dups == 0:
        return {"status": "clean_no_dups", "dfs": [df], "notes": notes}

    # --- Strategy 1: find wave col in already-long data ---
    wave_col = _find_wave_col(df, "id")
    if wave_col is not None:
        df2 = df.copy()
        df2["id"] = df2["id"].astype(str) + "_" + df2[wave_col].astype(str)
        df2 = df2.drop(columns=[wave_col])
        remaining_dups = df2.duplicated(subset=["id", "item"]).sum()
        if remaining_dups == 0:
            notes.append(f"Fixed dup_id_item by compositing id with '{wave_col}' column.")
            return {"status": "fixed_wave_col", "dfs": [df2], "notes": notes}
        else:
            notes.append(
                f"Tried compositing id with '{wave_col}' but {remaining_dups} dups remain."
            )

    # --- Strategy 2: try each low-cardinality column as wave ---
    for col in df.columns:
        if col in ("id", "item", "resp"):
            continue
        n_uniq = df[col].nunique(dropna=True)
        if 2 <= n_uniq <= 20:
            df2 = df.copy()
            df2["id"] = df2["id"].astype(str) + "_" + df2[col].astype(str)
            df2 = df2.drop(columns=[col])
            if df2.duplicated(subset=["id", "item"]).sum() == 0:
                notes.append(
                    f"Fixed dup_id_item by compositing id with column '{col}' "
                    f"(cardinality={n_uniq})."
                )
                return {"status": "fixed_wave_col", "dfs": [df2], "notes": notes}

    # --- Strategy 3: check ratio for clue ---
    n_part = df["id"].nunique()
    n_item = df["item"].nunique()
    n_resp = len(df)
    ratio = n_resp / (n_part * n_item) if n_part and n_item else 0
    notes.append(
        f"Could not resolve dup_id_item automatically. "
        f"Ratio n_resp/(n_id×n_item)={ratio:.2f} — "
        f"suggests ~{round(ratio)} waves if longitudinal. "
        f"Columns in melted data: {list(df.columns)}"
    )
    return {"status": "unresolved", "dfs": [], "notes": notes}


def _save(df: pd.DataFrame, slug: str, scale: str, doi: str, title: str,
          license_: str, notes: list) -> dict:
    """Write cleaned file and return index row."""
    fname = f"{slug}_{scale}.csv"
    df.to_csv(OUT_DIR / fname, index=False)
    n_part = df["id"].nunique()
    n_item = df["item"].nunique()
    n_resp = len(df)
    resp_vals = sorted(df["resp"].dropna().unique())
    resp_range = f"{resp_vals[0]}-{resp_vals[-1]}" if resp_vals else "?"
    return {
        "file": fname, "doi": doi, "title": title,
        "scale": scale, "n_participants": n_part,
        "n_items": n_item, "n_responses": n_resp,
        "resp_range": resp_range, "license": license_,
        "notes": "; ".join(str(n) for n in notes),
        "status": "cleaned",
    }


def _slug(title: str, doi: str) -> str:
    t = re.sub(r"[^a-z0-9]+", "_", title.lower())[:40].strip("_")
    d = re.sub(r"[^a-z0-9]", "_", doi.lower())[-12:]
    return f"{t}_{d}" if t else d


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    with open(RETRY_QUEUE, newline="", encoding="utf-8") as f:
        worth = list(csv.DictReader(f))
    print(f"Processing {len(worth)} worth_retrying rows…\n")

    results = []
    index_rows = []

    for i, row in enumerate(worth, 1):
        title  = row.get("title", "")
        doi    = row.get("doi", "")
        url    = row.get("url", "")
        src    = row.get("source", "")
        lic    = row.get("license", "")
        dfile  = row.get("data_file", "")
        print(f"[{i}/{len(worth)}] {title[:60]}")

        result = {
            "doi": doi, "url": url, "title": title,
            "data_file": dfile, "license": lic,
            "outcome": "", "notes": "",
        }

        # Resolve file URL
        try:
            files, _ = resolve_data_files(row)
        except Exception as e:
            result["outcome"] = "resolve_failed"
            result["notes"] = str(e)
            results.append(result)
            print(f"  → resolve_failed: {e}")
            continue

        if not files:
            result["outcome"] = "no_files"
            results.append(result)
            print("  → no_files")
            continue

        # Prefer the file named in data_file if we have it
        target = next(
            ((fu, fn) for fu, fn in files
             if fn.lower() == dfile.lower()),
            files[0],
        )
        file_url, fname = target

        # Download
        try:
            content = polite_get(file_url).content
        except Exception as e:
            result["outcome"] = "download_failed"
            result["notes"] = str(e)
            results.append(result)
            print(f"  → download_failed: {e}")
            continue

        # Load
        try:
            df_raw = load_table(io.BytesIO(content), fname)
        except Exception as e:
            result["outcome"] = "load_failed"
            result["notes"] = str(e)
            results.append(result)
            print(f"  → load_failed: {e}")
            continue

        # Try to fix
        fix = _try_fix(df_raw, fname)
        notes_str = "; ".join(str(n) for n in fix["notes"])
        result["notes"] = notes_str
        result["outcome"] = fix["status"]

        if fix["dfs"]:
            slug = _slug(title, doi)
            scale = "scale"
            idx = _save(fix["dfs"][0], slug, scale, doi, title, lic, fix["notes"])
            index_rows.append(idx)
            print(f"  → {fix['status']} ✓  saved {slug}_{scale}.csv")
        else:
            print(f"  → {fix['status']}")

        results.append(result)

    # Write results CSV
    if results:
        fieldnames = ["doi", "url", "title", "data_file", "license", "outcome", "notes"]
        with open(RESULTS, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(results)
        print(f"\nResults → {RESULTS}")

    # Append to cleaned index
    if index_rows:
        idx_exists = INDEX_FILE.exists()
        with open(INDEX_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(index_rows[0].keys()))
            if not idx_exists:
                w.writeheader()
            w.writerows(index_rows)
        print(f"Index   → {INDEX_FILE} ({len(index_rows)} new rows)")

    # Summary
    from collections import Counter
    counts = Counter(r["outcome"] for r in results)
    print("\nOutcome summary:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
