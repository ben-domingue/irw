"""Step 3: supplementary-file presence, on a sample.

For each journal, draw a reproducible random sample of SAMPLE_N open-access
full-text records from the most recent three years (per journals_resolved
+ step2 data), then call Europe PMC's supplementaryFiles endpoint for each
and record only: HTTP status, content-length, and the archive's file
manifest (names/extensions). Never reads file contents.

Writes journal_scout/step3_supp_manifest.csv (one row per sampled record).
Caches search results and manifests under journal_scout/cache/step3/.
"""
from __future__ import annotations

import csv
import json
import random
import sys
import time
import zipfile
import io
from pathlib import Path

import requests

HERE = Path(__file__).parent
CACHE = HERE / "cache" / "step3"
CACHE.mkdir(parents=True, exist_ok=True)
ERRLOG = HERE / "errors.log"

CONTACT_EMAIL = "ben.domingue@gmail.com"
UA = {"User-Agent": f"irw-journal-scout/0.1 (mailto:{CONTACT_EMAIL})"}

SAMPLE_N = 100
RECENT_YEARS = 3  # sample from the most recent 3 years with data
SEED = 20260811  # reproducible; recorded here and in the summary
REQUEST_DELAY = 0.25


def log_error(msg: str) -> None:
    with ERRLOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"  [error] {msg}", file=sys.stderr)


def cached_json_get(url: str, cache_key: str, params: dict | None = None) -> dict | None:
    path = CACHE / f"{cache_key}.json"
    if path.exists():
        return json.loads(path.read_text())
    try:
        resp = requests.get(url, params=params, headers=UA, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log_error(f"{cache_key}: {url} params={params} -> {e}")
        return None
    path.write_text(json.dumps(data, indent=1))
    time.sleep(REQUEST_DELAY)
    return data


def fetch_pmcids(issn: str, years: list[int]) -> list[str]:
    """Fetch PMCIDs for OA full-text records across the given years, paging
    through Europe PMC's cursor-based search."""
    all_ids = []
    year_lo, year_hi = min(years), max(years)
    query = (
        f'ISSN:"{issn}" AND (FIRST_PDATE:[{year_lo}-01-01 TO {year_hi}-12-31]) '
        f'AND HAS_FT:y AND OPEN_ACCESS:y'
    )
    cursor = "*"
    page = 0
    while True:
        cache_key = f"pmcids_{issn}_{year_lo}_{year_hi}_p{page}"
        data = cached_json_get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            cache_key,
            params={
                "query": query,
                "resultType": "idlist",
                "pageSize": 1000,
                "cursorMark": cursor,
                "format": "json",
            },
        )
        if not data:
            break
        results = data.get("resultList", {}).get("result", [])
        for r in results:
            pmcid = r.get("pmcid")
            if pmcid:
                all_ids.append(pmcid)
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor or not results:
            break
        cursor = next_cursor
        page += 1
        if page > 20:  # safety cap; 20k records is plenty to sample from
            break
    return all_ids


def fetch_manifest(pmcid: str) -> dict:
    """Fetch supplementary-files archive for a PMCID. Records status,
    content-length, and the file manifest (names/extensions) only --
    the zip's central directory is read to list names, never extracted."""
    cache_key = f"manifest_{pmcid}"
    path = CACHE / f"{cache_key}.json"
    if path.exists():
        return json.loads(path.read_text())

    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
    result = {"pmcid": pmcid, "http_status": None, "content_length": None, "manifest": [], "error": ""}
    try:
        resp = requests.get(url, headers=UA, timeout=60, stream=True)
        result["http_status"] = resp.status_code
        result["content_length"] = resp.headers.get("Content-Length")
        if resp.status_code == 200:
            body = resp.content  # supplementary archives are small enough to buffer
            try:
                zf = zipfile.ZipFile(io.BytesIO(body))
                result["manifest"] = zf.namelist()
            except zipfile.BadZipFile:
                result["error"] = "not_a_zip_or_corrupt"
        resp.close()
    except Exception as e:
        result["error"] = str(e)
        log_error(f"{cache_key}: {url} -> {e}")

    path.write_text(json.dumps(result, indent=1))
    time.sleep(REQUEST_DELAY)
    return result


def main():
    random.seed(SEED)

    with (HERE / "journals_resolved.csv").open() as f:
        journals = list(csv.DictReader(f))
    with (HERE / "step2_yearly_counts.csv").open() as f:
        yearly = list(csv.DictReader(f))

    max_year = max(int(r["year"]) for r in yearly)
    recent_years = list(range(max_year - RECENT_YEARS + 1, max_year + 1))

    rows = []
    for j in journals:
        issn = j["issn_l"]
        title = j["title_queried"]
        print(f"Step 3: {title} ({issn}) -- fetching PMCID pool for {recent_years}")
        pool = fetch_pmcids(issn, recent_years)
        pool = sorted(set(pool))  # dedupe, stable order before shuffling
        sample = pool[:]
        random.shuffle(sample)
        sample = sample[:SAMPLE_N]
        print(f"  pool={len(pool)} sample={len(sample)}")

        for pmcid in sample:
            m = fetch_manifest(pmcid)
            rows.append({
                "journal": title,
                "issn_l": issn,
                "pmcid": pmcid,
                "http_status": m["http_status"],
                "content_length": m["content_length"],
                "n_files": len(m["manifest"]),
                "manifest": ";".join(m["manifest"]),
                "error": m["error"],
            })

    out_path = HERE / "step3_supp_manifest.csv"
    with out_path.open("w", newline="") as f:
        fieldnames = list(rows[0].keys()) if rows else [
            "journal", "issn_l", "pmcid", "http_status", "content_length", "n_files", "manifest", "error"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out_path}")
    print(f"Seed used: {SEED}; recent years sampled: {recent_years}")


if __name__ == "__main__":
    main()
