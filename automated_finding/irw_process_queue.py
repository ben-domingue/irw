"""
irw_process_queue.py
====================
Processes datasets that have been manually added to the IRW processing queue
Google Sheet. For each queued dataset that has not already been processed:

  1. RESOLVE  — find the actual data file URL via the repository API
  2. DOWNLOAD — fetch the file
  3. COERCE   — convert to IRW long format (id / item / resp)
  4. QC       — run the standard IRW checks
  5. SAVE     — write the IRW-formatted CSV to irw_output/queue/<doi>.csv

Re-running is safe: any DOI whose output file already exists in irw_output/queue/
is skipped. Add new rows to the sheet and re-run to process just the additions.

Queue sheet (edit here to add candidates):
  https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/edit

Usage:
    python irw_process_queue.py
    python irw_process_queue.py --out-dir path/to/output   # default: irw_output/queue
"""

from __future__ import annotations

import csv
import io
import os
import re
import sys

import requests
import pandas as pd

from irw_triage_updated  import load_table, coerce_to_irw, run_qc, irw_metadata, print_report, triage_dataset, Triage
from irw_batch_updated   import resolve_data_files, polite_get, TABULAR_EXT
from irw_discover_updated import QUEUE_SHEET_URL, norm_doi

# Redivis tables that contain DOIs of datasets already in the IRW.
# Both biblio and metadata tables are scanned; DOI-like tokens are extracted
# from every cell so the column name doesn't need to be hardcoded.
_REDIVIS_IRW_TABLES = [
    "https://redivis.com/workspace/datasets/bdxt-4fqe5tyf4/tables/h5gs-a45yyran0",
    "https://redivis.com/workspace/datasets/bdxt-4fqe5tyf4/tables/qahg-c3vy0avfz",
]


def _load_redivis_dois() -> set:
    """Fetch DOIs already in the IRW from Redivis. Returns empty set on failure."""
    try:
        import redivis
        ds = redivis.user("bdomingu").dataset("irw_meta:bdxt")
        dois = set()
        for table in ds.list_tables():
            df = table.to_pandas_dataframe(dtype_backend="numpy")
            for col in df.columns:
                for val in df[col].dropna().astype(str):
                    d = norm_doi(val)
                    if "/" in d and " " not in d:
                        dois.add(d)
        print(f"Redivis: {len(dois):,} DOIs already in the IRW.")
        return dois
    except Exception as e:
        print(f"[warn] Could not load Redivis IRW metadata: {e}", file=sys.stderr)
        print(f"       Proceeding without Redivis deduplication.", file=sys.stderr)
        return set()

UA = {"User-Agent": "irw-process-queue/1.0 (research)"}


# ---------------------------------------------------------------------------
# Fetch the queue
# ---------------------------------------------------------------------------

def fetch_queue() -> list[dict]:
    """Download the processing queue from Google Sheets. Returns list of rows."""
    try:
        r = requests.get(QUEUE_SHEET_URL, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"ERROR: could not fetch queue sheet: {e}", file=sys.stderr)
        sys.exit(1)

    rows = list(csv.DictReader(io.StringIO(r.text)))
    if not rows:
        print("Queue sheet is empty.")
        sys.exit(0)
    return rows


# ---------------------------------------------------------------------------
# Output path helpers
# ---------------------------------------------------------------------------

def _doi_to_filename(doi: str) -> str:
    """Turn a DOI into a safe filename stem."""
    return re.sub(r"[^\w]", "_", doi).strip("_") + ".csv"


def output_path(doi: str, out_dir: str) -> str:
    return os.path.join(out_dir, _doi_to_filename(doi))


# ---------------------------------------------------------------------------
# Process one queued dataset
# ---------------------------------------------------------------------------

def process_one(row: dict, out_dir: str) -> dict:
    doi   = norm_doi(row.get("doi", ""))
    title = row.get("title", "")
    url   = row.get("url", "")
    src   = row.get("source", "").lower()

    result = {"doi": doi, "title": title, "source": src}

    # Build a minimal batch-style row so we can reuse resolve_data_files.
    batch_row = {"source": src, "url": url, "doi": doi}

    files, license_raw = resolve_data_files(batch_row)
    from irw_batch_updated import check_license
    license_norm, blocked, _ = check_license(license_raw)
    result["license"] = license_norm

    if blocked:
        result["status"] = "license_restricted"
        result["note"]   = f"license '{license_norm}' does not permit redistribution"
        return result

    if not files:
        result["status"] = "no_usable_file"
        result["note"]   = "resolver found no tabular files on the landing page"
        return result

    file_url, fname = files[0]
    result["data_file"] = fname
    if len(files) > 1:
        result["note"] = f"{len(files)-1} additional file(s) on landing page — only first processed"

    try:
        content = polite_get(file_url).content
        df_raw  = load_table(content, filename=fname)
    except Exception as e:
        result["status"] = "download_failed"
        result["note"]   = str(e)[:200]
        return result

    try:
        triage = triage_dataset(df_raw)
    except Exception as e:
        result["status"] = "error"
        result["note"]   = str(e)[:200]
        return result

    result["flag"] = triage.flag

    if triage.coercion.df is not None:
        path = output_path(doi, out_dir)
        triage.coercion.df.to_csv(path, index=False)
        result["status"]   = "saved"
        result["irw_file"] = path
        if triage.metadata:
            result.update({k: triage.metadata[k]
                           for k in ("n_participants", "n_items", "n_responses", "density")})
    else:
        result["status"] = "coercion_failed"

    result["reasons"] = " | ".join(triage.reasons)[:300]
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.join("irw_output", "queue"))
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    irw_dois = _load_redivis_dois()
    print()

    rows = fetch_queue()
    print(f"Queue has {len(rows)} dataset(s).\n")

    skipped, processed, failed = 0, 0, 0

    for row in rows:
        doi   = norm_doi(row.get("doi", ""))
        title = (row.get("title") or doi)[:65]

        if not doi:
            print(f"  [skip] row has no DOI: {row}")

        if doi and doi in irw_dois:
            print(f"  [skip] {title}")
            print(f"         already in IRW (Redivis)")
            skipped += 1
            continue
            skipped += 1
            continue

        path = output_path(doi, args.out_dir)
        if os.path.exists(path):
            print(f"  [skip] {title}")
            print(f"         already processed -> {path}")
            skipped += 1
            continue

        print(f"  [proc] {title}")
        result = process_one(row, args.out_dir)
        status = result.get("status", "?")
        flag   = result.get("flag", "")

        if status == "saved":
            processed += 1
            print(f"         -> {flag}  saved: {result.get('irw_file','')}")
            print(f"            N={result.get('n_participants','')}  "
                  f"items={result.get('n_items','')}  "
                  f"density={result.get('density','')}")
        else:
            failed += 1
            print(f"         -> {status}: {result.get('note', result.get('reasons',''))[:120]}")

        if result.get("reasons"):
            for line in result["reasons"].split(" | "):
                print(f"            • {line}")
        print()

    print("=" * 55)
    print(f"Done.  skipped={skipped}  processed={processed}  failed={failed}")
    if processed:
        print(f"IRW-formatted files -> {args.out_dir}/")


if __name__ == "__main__":
    main()
