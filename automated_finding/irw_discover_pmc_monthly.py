"""
irw_discover_pmc_monthly.py
==============================
Incremental scheduled discovery+triage for irw_discover_pmc.py. Same shape
and rationale as irw_discover_plos_monthly.py -- see that file's module
docstring for the full explanation of why incrementality here is a
persistent seen-DOI store (pmc_seen_dois.csv, shared with manual
irw_discover_pmc.py runs) rather than a --since date filter: Europe PMC's
search endpoint has no date-range parameter wired up here either.

  --mode weekly  a small, proven-high-yield term subset (HIGH_YIELD_TERMS),
                 run every week across the JOURNALS list.
  --mode full    the same broad ~100-term construct list irw_discover_monthly.py
                 uses for the repo connector (imported from there, not
                 duplicated here), run monthly.

--limit bounds each run's total triaged-candidate count for the same
rate-limit/runtime reasons as the PLOS version.

Run:
    python irw_discover_pmc_monthly.py --mode weekly
    python irw_discover_pmc_monthly.py --mode full --limit 150
    python irw_discover_pmc_monthly.py --mode weekly --dry-run
"""

from __future__ import annotations

import csv
import os
import argparse
from datetime import datetime, timezone

from irw_discover_updated import _load_auto_exclusions
from irw_discover_pmc import (
    from_pmc, process_one_isolated, _new_pool, JOURNALS, DEFAULT_JOURNALS,
    FIELDNAMES, SEEN_DOIS_PATH, load_seen_dois, append_seen_dois,
)
from irw_discover_monthly import TERM_LIST as FULL_TERM_LIST

LOG_PATH = "search_terms_log.csv"
OUT_PREFIX = "pmc_monthly_candidates_"

# Same shortlist as irw_discover_plos_monthly.py's HIGH_YIELD_TERMS --
# proven-yield constructs, kept identical across connectors on purpose
# since the yield signal is about the construct, not the source. Edit
# freely as per-source yield data comes in; they don't need to stay in
# sync going forward.
HIGH_YIELD_TERMS = [
    "self-esteem",
    "grit",
    "self-efficacy",
    "depression",
    "anxiety",
    "burnout",
    "perceived stress",
    "well-being",
    "life satisfaction",
    "loneliness",
    "academic motivation",
    "work engagement",
    "resilience",
    "procrastination",
    "growth mindset",
]

DEFAULT_LIMIT_BY_MODE = {"weekly": 60, "full": 150}


def _append_log_rows(rows: list[dict], path: str = LOG_PATH) -> None:
    fieldnames = ["date", "query", "output_file", "notes"]
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["weekly", "full"], default="weekly")
    ap.add_argument("--journals", default=DEFAULT_JOURNALS,
                     help="comma-separated journal slugs to search, from: "
                          f"{', '.join(JOURNALS)} (default: all)")
    ap.add_argument("--limit", type=int, default=None,
                     help="cap total candidates triaged this run "
                          f"(default: weekly={DEFAULT_LIMIT_BY_MODE['weekly']}, "
                          f"full={DEFAULT_LIMIT_BY_MODE['full']})")
    ap.add_argument("--out", default=None,
                     help=f"output CSV (default: {OUT_PREFIX}<mode>_<today>.csv)")
    ap.add_argument("--dry-run", action="store_true",
                     help="print term/journal counts and seen-DOI store size, no queries run")
    args = ap.parse_args()

    journals = [j.strip() for j in args.journals.split(",") if j.strip()]
    bad = [j for j in journals if j not in JOURNALS]
    if bad:
        raise SystemExit(f"Unknown journal slug(s): {bad}. Choose from: {list(JOURNALS)}")

    terms = HIGH_YIELD_TERMS if args.mode == "weekly" else FULL_TERM_LIST
    limit = args.limit if args.limit is not None else DEFAULT_LIMIT_BY_MODE[args.mode]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seen = load_seen_dois()

    if args.dry_run:
        print(f"Mode: {args.mode} ({len(terms)} terms) x journals: {', '.join(journals)}")
        print(f"Seen-DOI store ({SEEN_DOIS_PATH}): {len(seen):,} DOIs already attempted "
              f"by any manual or scheduled run (never re-triaged)")
        print(f"Limit this run: {limit}")
        return

    exclude = _load_auto_exclusions()
    print(f"Excluding {len(exclude):,} DOIs already in the IRW dictionary")
    print(f"Excluding {len(seen):,} DOIs already triaged in a prior run "
          f"(manual or scheduled -- see {SEEN_DOIS_PATH})")

    out_path = args.out or f"{OUT_PREFIX}{args.mode}_{today}.csv"
    outf = open(out_path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()

    skip = seen | exclude
    newly_attempted = []
    n_done = 0
    terms_fully_covered = 0
    pool = _new_pool()
    capped = False
    try:
        for term in terms:
            print(f"\n[term] {term!r}", flush=True)
            for journal in journals:
                for hit in from_pmc(term, journal):
                    if hit.doi in skip:
                        continue
                    skip.add(hit.doi)
                    newly_attempted.append(hit.doi)
                    row, pool = process_one_isolated(hit, pool)
                    writer.writerow(row)
                    outf.flush()
                    n_done += 1
                    print(f"  [{row['flag']:18}] {hit.title[:70]}", flush=True)
                    if n_done >= limit:
                        capped = True
                        break
                if capped:
                    break
            if not capped:
                terms_fully_covered += 1
            if capped:
                print(f"\nHit --limit={limit}; stopping. Remaining terms picked up next run "
                      f"(seen-DOI state persists).", flush=True)
                break
    finally:
        pool.shutdown(wait=False)
        outf.close()
        append_seen_dois(newly_attempted)

    print(f"\n{n_done} candidates triaged -> {out_path}")
    print(f"{terms_fully_covered}/{len(terms)} terms fully covered this run")

    _append_log_rows([{
        "date": today,
        "query": f"[{args.mode}] {len(terms)} terms x journals={','.join(journals)}",
        "output_file": out_path,
        "notes": f"pmc monthly-script automated run; mode={args.mode}; "
                 f"{n_done} candidates triaged; {terms_fully_covered}/{len(terms)} terms covered",
    }])


if __name__ == "__main__":
    main()
