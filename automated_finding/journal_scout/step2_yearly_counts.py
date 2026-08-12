"""Step 2: per-journal, per-year Europe PMC hitCounts (2015-2025).

Reads journal_scout/journals_resolved.csv (Step 1 output), and for each
journal's issn_l, queries Europe PMC for three counts per year: total
records, full-text records, and open-access records. Only hitCount is
read -- no article-level data.

Writes journal_scout/step2_yearly_counts.csv (one row per journal-year).
Caches every raw JSON response under journal_scout/cache/step2/
(skip-if-exists, restartable). Rate limit: <=5 req/s to Europe PMC via a
fixed per-request sleep, run sequentially (not worth parallelizing here).
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
CACHE = HERE / "cache" / "step2"
CACHE.mkdir(parents=True, exist_ok=True)
ERRLOG = HERE / "errors.log"

CONTACT_EMAIL = "ben.domingue@gmail.com"
UA = {"User-Agent": f"irw-journal-scout/0.1 (mailto:{CONTACT_EMAIL})"}

YEAR_START = 2015
YEAR_END = 2025
REQUEST_DELAY = 0.25  # 4 req/s, under the 5 req/s guidance


def log_error(msg: str) -> None:
    with ERRLOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"  [error] {msg}", file=sys.stderr)


def cached_search(cache_key: str, query: str) -> int | None:
    path = CACHE / f"{cache_key}.json"
    if path.exists():
        data = json.loads(path.read_text())
        return data.get("hitCount")
    try:
        resp = requests.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": query, "resultType": "idlist", "pageSize": 1, "format": "json"},
            headers=UA,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log_error(f"{cache_key}: query={query!r} -> {e}")
        return None
    path.write_text(json.dumps(data, indent=1))
    time.sleep(REQUEST_DELAY)
    return data.get("hitCount")


def counts_for_journal_year(issn: str, year: int) -> dict:
    date_range = f"[{year}-01-01 TO {year}-12-31]"
    base = f'ISSN:"{issn}" AND (FIRST_PDATE:{date_range})'
    n_records = cached_search(f"{issn}_{year}_total", base)
    n_fulltext = cached_search(f"{issn}_{year}_ft", base + " AND HAS_FT:y")
    n_oa = cached_search(f"{issn}_{year}_oa", base + " AND OPEN_ACCESS:y")
    return {"n_records": n_records, "n_fulltext": n_fulltext, "n_oa": n_oa}


def main():
    with (HERE / "journals_resolved.csv").open() as f:
        journals = list(csv.DictReader(f))

    rows = []
    for j in journals:
        issn = j["issn_l"]
        title = j["title_queried"]
        print(f"Step 2: {title} ({issn})")
        for year in range(YEAR_START, YEAR_END + 1):
            c = counts_for_journal_year(issn, year)
            n_records = c["n_records"]
            n_fulltext = c["n_fulltext"]
            n_oa = c["n_oa"]
            pct_fulltext = round(n_fulltext / n_records, 3) if n_records else None
            pct_oa = round(n_oa / n_records, 3) if n_records else None
            rows.append({
                "journal": title,
                "issn_l": issn,
                "publisher": j["publisher_crossref"] or j["publisher_openalex"],
                "tier": j["tier"],
                "year": year,
                "n_records": n_records,
                "n_fulltext": n_fulltext,
                "n_oa": n_oa,
                "pct_fulltext": pct_fulltext,
                "pct_oa": pct_oa,
            })

    out_path = HERE / "step2_yearly_counts.csv"
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
