"""Step 4: license distribution for the Step 3 sample.

For every PMCID sampled in Step 3, pulls the `license` field from Europe
PMC's resultType=core (batched, ~25 PMCIDs/request via an OR query, to
avoid one request per record). Reported column only -- not a filter; IRW
derives license per table downstream and a human makes that call.

Writes journal_scout/step4_license.csv (one row per PMCID with its raw
license string). journal_yield.csv (Step 6) rolls this up per journal.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
CACHE = HERE / "cache" / "step4"
CACHE.mkdir(parents=True, exist_ok=True)
ERRLOG = HERE / "errors.log"

CONTACT_EMAIL = "ben.domingue@gmail.com"
UA = {"User-Agent": f"irw-journal-scout/0.1 (mailto:{CONTACT_EMAIL})"}
BATCH_SIZE = 25
REQUEST_DELAY = 0.25


def log_error(msg: str) -> None:
    with ERRLOG.open("a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(f"  [error] {msg}", file=sys.stderr)


def fetch_batch(pmcids: list[str]) -> dict[str, str]:
    key = hashlib.sha1(",".join(sorted(pmcids)).encode()).hexdigest()[:16]
    path = CACHE / f"batch_{key}.json"
    if path.exists():
        return json.loads(path.read_text())

    query = " OR ".join(f"PMCID:{p}" for p in pmcids)
    out: dict[str, str] = {}
    try:
        resp = requests.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": query, "resultType": "core", "pageSize": len(pmcids), "format": "json"},
            headers=UA,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        for r in data.get("resultList", {}).get("result", []):
            pmcid = r.get("pmcid")
            if pmcid:
                out[pmcid] = r.get("license", "")
    except Exception as e:
        log_error(f"batch_{key}: {len(pmcids)} pmcids -> {e}")
        return {}

    path.write_text(json.dumps(out, indent=1))
    time.sleep(REQUEST_DELAY)
    return out


def main():
    with (HERE / "step3_supp_manifest.csv").open() as f:
        sample_rows = list(csv.DictReader(f))

    pmcids_by_journal = {}
    for r in sample_rows:
        pmcids_by_journal.setdefault(r["journal"], []).append(r["pmcid"])

    out_rows = []
    for journal, pmcids in pmcids_by_journal.items():
        print(f"Step 4: {journal} ({len(pmcids)} records)")
        licenses: dict[str, str] = {}
        for i in range(0, len(pmcids), BATCH_SIZE):
            batch = pmcids[i:i + BATCH_SIZE]
            licenses.update(fetch_batch(batch))
        for pmcid in pmcids:
            out_rows.append({
                "journal": journal,
                "pmcid": pmcid,
                "license_raw": licenses.get(pmcid, ""),
            })

    out_path = HERE / "step4_license.csv"
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["journal", "pmcid", "license_raw"])
        w.writeheader()
        w.writerows(out_rows)
    print(f"\nWrote {len(out_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
