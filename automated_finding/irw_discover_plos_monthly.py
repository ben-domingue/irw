"""
irw_discover_plos_monthly.py
==============================
Incremental scheduled discovery+triage for irw_discover_plos.py. Meant to be
invoked on a schedule (see the `schedule` skill), in two modes:

  --mode weekly  a small, proven-high-yield term subset (HIGH_YIELD_TERMS),
                 run every week -- kept small on purpose so a full
                 discover+triage pass (real downloads, not just search) stays
                 cheap and bounded.
  --mode full    the same broad ~100-term construct list irw_discover_monthly.py
                 uses for the repo connector (imported from there, not
                 duplicated here), run monthly.

Why incrementality here isn't a --since date filter (unlike
irw_discover_monthly.py's repo connector): the PLOS Solr search API this
script's discovery layer (irw_discover_plos.py's search_plos) uses has no
date-range parameter wired up. Instead, incrementality rides on
irw_discover_plos.py's own SEEN_DOIS_PATH (plos_seen_dois.csv) -- a
persistent, cross-run record of every DOI *either* a manual
(`python irw_discover_plos.py ...`) *or* this scheduled script has ever
attempted, regardless of what triage flag it got. That store is shared
deliberately: without it, a term you search by hand today and the same
term showing up in HIGH_YIELD_TERMS next week would re-download and
re-triage the same candidates, wasting PLOS API/CDN load and producing
duplicate rows across PRs. This script does not maintain its own separate
seen-DOI file -- it calls irw_discover_plos.py's load_seen_dois() /
append_seen_dois() directly.

--limit bounds each run's total triaged-candidate count (real downloads are
the expensive, rate-limit-relevant part -- see README.md's triage timing
note). If a run hits the cap, remaining terms for that mode are left
untried and picked up on the next scheduled run naturally (seen-DOI state
persists across runs) -- print a clear notice so a human doesn't assume the
term list was fully covered.

Run:
    python irw_discover_plos_monthly.py --mode weekly
    python irw_discover_plos_monthly.py --mode full --limit 150
    python irw_discover_plos_monthly.py --mode weekly --dry-run
"""

from __future__ import annotations

import csv
import os
import argparse
from datetime import datetime, timezone

from irw_discover_updated import _load_auto_exclusions
from irw_discover_plos import (
    from_plos, process_one_isolated, _new_pool, JOURNALS, DEFAULT_JOURNAL,
    FIELDNAMES, SEEN_DOIS_PATH, load_seen_dois, append_seen_dois,
)
from irw_discover_monthly import TERM_LIST as FULL_TERM_LIST

LOG_PATH = "search_terms_log.csv"
OUT_PREFIX = "plos_monthly_candidates_"

# Small, proven-yield subset for the weekly pass -- pulled from constructs
# BATCH_LOG.md calls out as having produced real, processed PLOS hits (not
# just present in the relevance vocabulary). Same shortlist logic as
# irw_discover_monthly.py's TERM_LIST comment: bare/root construct terms,
# not "X scale"/"X questionnaire" phrasing. Edit freely as yield data comes
# in -- this is a starting point, not a final answer.
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
    ap.add_argument("--journals", default=DEFAULT_JOURNAL,
                     help="comma-separated journal slugs to search, from: "
                          f"{', '.join(JOURNALS)} (default: {DEFAULT_JOURNAL})")
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
            any_hit = False
            for journal in journals:
                for hit in from_plos(term, journal):
                    any_hit = True
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
        "notes": f"plos monthly-script automated run; mode={args.mode}; "
                 f"{n_done} candidates triaged; {terms_fully_covered}/{len(terms)} terms covered",
    }])


if __name__ == "__main__":
    main()
