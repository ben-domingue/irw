"""
irw_batch.py
============
Runs the triage pipeline over a whole discovery file (e.g. irw_discovered.csv),
turning ~hundreds of candidate landing pages into one ranked triage summary.

Pipeline per candidate:
    landing-page URL  ->  RESOLVE to a real data file  ->  download
                      ->  triage_dataset()  ->  record flag + metadata

Why this is more than "loop 500 times":
  * RESOLVE   : discovery stored landing pages, not direct file links. Each
                repository exposes its files through a different API, so we
                resolve them per-source. This is the brittle part.
  * POLITE    : per-domain delay so we don't hammer (and get blocked by) a repo.
  * RESUMABLE : every result is checkpointed to disk. Re-running skips finished
                rows, so a Colab disconnect at row 450 doesn't waste the first 449.
  * HONEST FLAGS: at scale the biggest bucket is usually "couldn't get a usable
                file" — that gets its own flag instead of masquerading as
                'human_assistance'.

Flags produced:
    good              confident mapping + clean QC (still needs a human glance)
    human_assistance  got data, but mapping/QC needs a person
    no_usable_file    landing page had no resolvable tabular file
    download_failed   network/HTTP error fetching the file
    error             unexpected problem (message recorded)

USAGE — always start small, then scale:
    python irw_batch.py irw_discovered.csv --limit 5      # test on 5 first!
    python irw_batch.py irw_discovered.csv                # full run, resumable
    python irw_batch.py irw_discovered.csv --resume       # continue after a stop
"""

from __future__ import annotations

import os
import re
import csv
import json
import time
import argparse
from collections import defaultdict
from urllib.parse import urlparse

import requests
import pandas as pd

from irw_triage_updated import load_table, triage_dataset, irw_metadata

UA = {"User-Agent": "irw-batch/1.0 (research; contact your-email)"}
TABULAR_EXT = (".csv", ".tsv", ".xlsx", ".xls")
PER_DOMAIN_DELAY = 1.5          # seconds between hits to the same domain
CHECKPOINT = "irw_batch_checkpoint.jsonl"


# ---------------------------------------------------------------------------
# License checking
# ---------------------------------------------------------------------------

_BLOCKED_LICENSES = {"cc-by-nc", "cc-by-nd", "cc-by-nc-nd", "cc-by-nc-sa",
                     "all-rights-reserved", "arr"}
_OPEN_LICENSES    = {"cc0", "cc-pddc", "cc-by", "cc-by-sa", "public-domain"}

def _norm_license(raw: str) -> str:
    s = raw.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[-_]?\d+\.\d+$", "", s)   # strip version (e.g. cc-by-4.0 -> cc-by)
    s = re.sub(r"https?://.*creativecommons\.org/licenses/([^/]+).*", r"cc-\1", s)
    s = re.sub(r"https?://.*creativecommons\.org/publicdomain/zero.*", "cc0", s)
    return s

def check_license(raw: str) -> tuple[str, bool, bool]:
    """Returns (normalized, is_blocked, is_unknown)."""
    if not raw:
        return ("unknown", False, True)
    n = _norm_license(raw)
    return (n, n in _BLOCKED_LICENSES, n not in _OPEN_LICENSES and n not in _BLOCKED_LICENSES)


# ---------------------------------------------------------------------------
# RESOLVE: landing page -> direct data-file URL(s) + license
#   Each helper returns ([(file_url, filename)], license_str).
# ---------------------------------------------------------------------------

def _zenodo_files(url: str) -> tuple:
    m = re.search(r"(?:record|records)/(\d+)", url)
    if not m:
        return [], ""
    r = requests.get(f"https://zenodo.org/api/records/{m.group(1)}",
                     headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    license_raw = (data.get("metadata", {}).get("license", {}) or {}).get("id", "")
    out = []
    for f in data.get("files", []):
        key = f.get("key", "")
        link = f.get("links", {}).get("self", "")
        if key.lower().endswith(TABULAR_EXT) and link:
            out.append((link, key))
    return out, license_raw


def _figshare_files(url: str) -> tuple:
    m = re.search(r"articles/(?:[^/]+/)?(?:[^/]+/)?(\d+)", url)
    if not m:
        return [], ""
    r = requests.get(f"https://api.figshare.com/v2/articles/{m.group(1)}",
                     headers=UA, timeout=30)
    r.raise_for_status()
    data = r.json()
    license_raw = (data.get("license") or {}).get("name", "")
    out = []
    for f in data.get("files", []):
        name = f.get("name", "")
        dl = f.get("download_url", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            out.append((dl, name))
    return out, license_raw


def _dryad_files(doi: str) -> tuple:
    if not doi:
        return [], ""
    enc = requests.utils.quote(f"doi:{doi}", safe="")
    base = "https://datadryad.org/api/v2"
    r = requests.get(f"{base}/datasets/{enc}/versions", headers=UA, timeout=30)
    r.raise_for_status()
    versions = r.json().get("_embedded", {}).get("stash:versions", [])
    if not versions:
        return [], ""
    latest_ver = versions[-1]
    license_raw = latest_ver.get("license", "")
    files_link = latest_ver.get("_links", {}).get("stash:files", {}).get("href", "")
    if not files_link:
        return [], license_raw
    r2 = requests.get(f"https://datadryad.org{files_link}", headers=UA, timeout=30)
    r2.raise_for_status()
    out = []
    for f in r2.json().get("_embedded", {}).get("stash:files", []):
        name = f.get("path", "")
        dl = f.get("_links", {}).get("stash:download", {}).get("href", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            out.append((f"https://datadryad.org{dl}", name))
    return out, license_raw


def _dataverse_files(url: str, doi: str) -> tuple:
    pid = f"doi:{doi}" if doi else None
    if not pid:
        return [], ""
    r = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/",
                     params={"persistentId": pid}, headers=UA, timeout=30)
    r.raise_for_status()
    latest = r.json().get("data", {}).get("latestVersion", {})
    license_raw = (latest.get("license") or {}).get("name", "") or latest.get("termsOfUse", "")
    out = []
    for f in latest.get("files", []):
        df = f.get("dataFile", {})
        name = df.get("filename", "")
        fid = df.get("id")
        if name.lower().endswith(TABULAR_EXT) and fid:
            out.append((f"https://dataverse.harvard.edu/api/access/datafile/{fid}",
                        name))
    return out, license_raw


def _osf_files(url: str) -> tuple:
    node_id = [s for s in url.rstrip("/").split("/") if s][-1]
    r = requests.get(
        f"https://api.osf.io/v2/nodes/{node_id}/",
        headers=UA, timeout=30)
    r.raise_for_status()
    license_raw = (r.json().get("data", {}).get("relationships", {})
                   .get("license", {}).get("data", {}) or {}).get("id", "")
    r2 = requests.get(
        f"https://api.osf.io/v2/nodes/{node_id}/files/osfstorage/",
        headers=UA, timeout=30)
    r2.raise_for_status()
    out = []
    for f in r2.json().get("data", []):
        name = f.get("attributes", {}).get("name", "")
        dl = f.get("links", {}).get("download", "")
        if name.lower().endswith(TABULAR_EXT) and dl:
            out.append((dl, name))
    return out, license_raw


def resolve_data_files(row: dict) -> tuple:
    """Dispatch to the right repository resolver. Returns ([(file_url, name)], license_str)."""
    src = (row.get("source") or "").lower()
    url = row.get("url") or ""
    doi = row.get("doi") or ""
    try:
        if src == "zenodo":
            return _zenodo_files(url)
        if src == "figshare":
            return _figshare_files(url)
        if src == "dryad":
            return _dryad_files(doi)
        if src == "dataverse":
            return _dataverse_files(url, doi)
        if src == "osf":
            return _osf_files(url)
    except Exception:
        return [], ""
    return [], ""


# ---------------------------------------------------------------------------
# Politeness: per-domain rate limiting
# ---------------------------------------------------------------------------

_last_hit = defaultdict(float)

def polite_get(url: str) -> requests.Response:
    dom = urlparse(url).netloc
    wait = PER_DOMAIN_DELAY - (time.time() - _last_hit[dom])
    if wait > 0:
        time.sleep(wait)
    resp = requests.get(url, headers=UA, timeout=120)
    _last_hit[dom] = time.time()
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Process one candidate
# ---------------------------------------------------------------------------

def process_one(row: dict) -> dict:
    base = {"source": row.get("source", ""), "title": row.get("title", ""),
            "url": row.get("url", ""), "doi": row.get("doi", "")}

    files, license_raw = resolve_data_files(row)
    license_norm, blocked, unknown = check_license(license_raw)
    base["license"] = license_norm

    if blocked:
        return {**base, "flag": "license_restricted",
                "reasons": f"license '{license_norm}' does not permit redistribution",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    if not files:
        return {**base, "flag": "no_usable_file",
                "reasons": "no resolvable .csv/.tsv/.xlsx on landing page",
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": ""}

    # Use the first tabular file. (Multi-file datasets -> human territory.)
    file_url, fname = files[0]
    try:
        content = polite_get(file_url).content
        df = load_table(content, filename=fname)
    except Exception as e:
        return {**base, "flag": "download_failed", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}

    try:
        t = triage_dataset(df)
        meta = t.metadata or {}
        reasons = list(t.reasons)
        if unknown:
            reasons.append(f"license_unknown* — license '{license_norm}' not recognised as open; verify before submission")
        return {**base, "flag": t.flag,
                "reasons": " | ".join(reasons)[:400],
                "n_responses": meta.get("n_responses", ""),
                "n_participants": meta.get("n_participants", ""),
                "n_items": meta.get("n_items", ""),
                "density": meta.get("density", ""),
                "data_file": fname,
                "n_other_files": len(files) - 1}
    except Exception as e:
        return {**base, "flag": "error", "reasons": str(e)[:200],
                "n_responses": "", "n_participants": "", "n_items": "",
                "density": "", "data_file": fname}


# ---------------------------------------------------------------------------
# Checkpointing for resumability
# ---------------------------------------------------------------------------

def _key(row: dict) -> str:
    return row.get("doi") or row.get("url") or row.get("title", "")

def load_done(path: str) -> dict:
    done = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done[rec["_key"]] = rec
                except Exception:
                    pass
    return done

def append_checkpoint(path: str, key: str, result: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"_key": key, **result}) + "\n")


# ---------------------------------------------------------------------------
# Batch driver
# ---------------------------------------------------------------------------

FLAG_ORDER = ["good", "human_assistance", "not_item_response",
              "no_usable_file", "license_restricted", "download_failed", "error"]

def run_batch(candidates_csv: str, out_csv: str, limit: int | None,
              resume: bool, checkpoint: str = CHECKPOINT) -> pd.DataFrame:
    rows = list(csv.DictReader(open(candidates_csv, encoding="utf-8")))
    if limit:
        rows = rows[:limit]

    done = load_done(checkpoint) if resume else {}
    if resume and done:
        print(f"Resuming — {len(done)} already done, will be skipped.")
    elif not resume and os.path.exists(checkpoint):
        os.remove(checkpoint)   # fresh run

    results = list(done.values())
    for i, row in enumerate(rows, 1):
        k = _key(row)
        if k in done:
            continue
        print(f"[{i}/{len(rows)}] {row.get('source',''):9} "
              f"{(row.get('title','') or '')[:55]}", flush=True)
        res = process_one(row)
        append_checkpoint(checkpoint, k, res)
        results.append(res)
        print(f"        -> {res['flag']}", flush=True)

    df = pd.DataFrame(results)
    if not df.empty:
        df["_o"] = df["flag"].apply(lambda f: FLAG_ORDER.index(f)
                                    if f in FLAG_ORDER else 99)
        df = df.sort_values(["_o", "density"], ascending=[True, False]).drop(columns="_o")
        df.to_csv(out_csv, index=False)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates_csv")
    ap.add_argument("--out", default="irw_triage_summary.csv")
    ap.add_argument("--limit", type=int, default=None,
                    help="process only the first N (use this to test first!)")
    ap.add_argument("--resume", action="store_true",
                    help="skip rows already in the checkpoint")
    args = ap.parse_args()

    df = run_batch(args.candidates_csv, args.out, args.limit, args.resume)
    print("\n" + "=" * 50)
    if df.empty:
        print("No results.")
        return
    counts = df["flag"].value_counts()
    print("TRIAGE SUMMARY")
    for flag in FLAG_ORDER:
        if flag in counts:
            print(f"  {flag:18} {counts[flag]}")
    print(f"\nFull summary -> {args.out}")
    print("Work the 'good' rows first; they're sorted to the top.")
    print("Add candidates you want to process to the queue sheet,")
    print("then run irw_process_queue.py.")


if __name__ == "__main__":
    main()
