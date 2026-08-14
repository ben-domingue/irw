"""
irw_discover_monthly.py
========================
Incremental monthly discovery run for a fixed list of high-hit terms against
the most productive repositories (OSF, Dataverse by default). Meant to be
invoked on a schedule (see the `schedule` skill) so new candidates surface
without re-running the same terms against the same full history every time.

How incrementality works:
  - Each term's `--since` date is looked up from this script's own prior
    entries in search_terms_log.csv, not the whole log. The log is shared
    with other parts of the pipeline (e.g. PLOS batch term reuse) whose
    rows don't represent a repository-API run at all -- scoping the lookup
    to rows this script wrote (output_file starts with "monthly_candidates_")
    avoids picking up an unrelated date and silently under-searching.
  - The lookup is also scoped to the *source set* being queried this run,
    not just the term text: a prior row only counts as covering this run
    if its logged sources= set is a superset of --sources. A term's date
    from an osf+dataverse run does not establish coverage for a later
    zenodo-only run of the same term -- zenodo was never actually checked,
    so using that date would silently skip everything zenodo has ever
    published for the term. (Fixed 2026-08-14 after exactly this happened:
    an ad hoc run against zenodo/dryad/figshare/datacite/scholars_portal/
    surf inherited the same-day osf/dataverse sweep's "already run today"
    date and returned almost nothing until re-run with an explicit
    lookback. See automated_finding PR #1625 / TODO.md.)
  - A term run for the first time at a given source set has no prior row,
    so it falls back to --default-lookback-days (default 90) before today.
  - After a run, one row per term is appended to search_terms_log.csv with
    today's date, so next month's invocation advances automatically.

TERM_LIST below is a starting point, not a final answer -- edit it freely.
Pull candidates from search_terms_log.csv (which terms/notes mention high
hit counts) and BATCH_LOG.md (which batches such terms fed) before trusting
it as-is.

Run:
    python irw_discover_monthly.py                      # full run (~100 terms), osf+dataverse
    python irw_discover_monthly.py --mode weekly         # HIGH_YIELD_TERMS subset (~15 terms)
    python irw_discover_monthly.py --dry-run             # show since-dates only, no queries
    python irw_discover_monthly.py --sources osf dataverse surf aussda scholars_portal
"""

from __future__ import annotations

import csv
import sys
import argparse
from datetime import datetime, timedelta, timezone
from dataclasses import asdict

from irw_discover_updated import (
    discover, SOURCE_MAP, _load_auto_exclusions,
)

LOG_PATH = "search_terms_log.csv"
OUT_PREFIX = "monthly_candidates_"

# Candidate terms for the monthly run -- work this out with Ben before
# scheduling for real. search_terms_log.csv's `notes` field doesn't record
# per-term hit counts consistently enough to rank terms by historical yield,
# so this draft leans on two things BATCH_LOG.md does say explicitly:
#   - bare/root terms outperform qualified ones ("grit" surfaced hits
#     "grit scale" missed on page 1 -- see the 2026-07-xx entry on relevance
#     ranking vs phrase matching), so terms below are unqualified constructs,
#     not "X scale"/"X questionnaire" forms.
#   - these specific constructs are called out as having produced real,
#     processed hits in past batches (not just present in the relevance
#     filter's CONSTRUCT_TERMS vocabulary, which is necessary but not
#     sufficient evidence of yield).
# Unvetted beyond that -- edit freely.
TERM_LIST = [
    # Personality / individual differences
    "personality",
    "self-esteem",
    "grit",
    "self-efficacy",
    "emotion regulation",
    "resilience",
    "procrastination",
    "perfectionism",
    "narcissism",
    "dark triad",
    "locus of control",
    "self-control",
    "optimism",
    "attachment",
    "social desirability",
    "alexithymia",
    "shyness",
    "authenticity",
    "creativity",
    "curiosity",
    "rumination",
    # Clinical / psychopathology
    "depression",
    "anxiety",
    "burnout",
    "perceived stress",
    "loneliness",
    "post-traumatic stress",
    "childhood trauma",
    "insomnia",
    "eating disorder",
    "substance use",
    "internet addiction",
    "gaming disorder",
    "phobia",
    "obsessive-compulsive",
    "suicide risk",
    "dissociation",
    "health anxiety",
    "math anxiety",
    "impostor syndrome",
    # Health / well-being
    "well-being",
    "life satisfaction",
    "quality of life",
    "health literacy",
    "illness perception",
    "fatigue",
    "sleep quality",
    "medication adherence",
    "body image",
    "eating behavior",
    "flourishing",
    "happiness",
    "hope",
    "vitality",
    "positive affect",
    "gratitude",
    # Social / relationships
    "social support",
    "relationship satisfaction",
    "empathy",
    "trust",
    "conspiracy beliefs",
    "vaccine trust",
    # Academic / cognitive
    "academic motivation",
    "working memory",
    "executive function",
    "test anxiety",
    "self-regulated learning",
    "growth mindset",
    "academic buoyancy",
    "learning motivation",
    "meaning in life",
    "stroop",
    "flanker",
    "simon task",
    "go/no-go",
    "stop signal",
    "task switching",
    "prospective memory",
    # Work / organizational
    "job crafting",
    "work engagement",
    "psychological capital",
    "organizational justice",
    "psychological safety",
    "job satisfaction",
    "workplace incivility",
    "microaggressions",
    "turnover intention",
    "abusive supervision",
    "surface acting",
    "coping",
    # Consumer / economic / decision
    "financial literacy",
    "risk perception",
    "science literacy",
    "purchase intention",
    "technology acceptance",
    "delay discounting",
    # Sport / physical
    "sport motivation",
    "physical activity enjoyment",
    # Misc
    "youth development",
    "employability skills",
]

# Small, proven-yield subset for a weekly pass -- same shortlist used by
# irw_discover_plos_monthly.py / irw_discover_pmc_monthly.py's
# HIGH_YIELD_TERMS (kept identical across connectors on purpose, since the
# yield signal is about the construct, not the source). Edit freely as
# per-source yield data comes in; they don't need to stay in sync going
# forward.
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

DEFAULT_SOURCES = ["osf", "dataverse"]


def _parse_logged_sources(notes: str) -> set[str] | None:
    """Extract the {'sources=a,b,c'} set this script wrote into a log row's
    notes field, or None if the note has no parseable sources= segment
    (e.g. a legacy row from before this field existed)."""
    for part in notes.split(";"):
        part = part.strip()
        if part.startswith("sources="):
            return set(s.strip() for s in part[len("sources="):].split(",") if s.strip())
    return None


def last_run_date(term: str, active_sources: set[str], log_path: str = LOG_PATH) -> str | None:
    """Most recent date this monthly script itself ran `term` against a
    source set that fully covers `active_sources`, or None if it never has.

    Only considers rows whose output_file this script wrote (see
    OUT_PREFIX) -- ignores rows logged by other parts of the pipeline that
    happen to reuse the same term text (e.g. PLOS batches). Critically,
    also only considers rows whose logged sources= set is a superset of
    active_sources: a prior run of "self-esteem" against osf+dataverse
    does NOT establish a --since date for a later run of "self-esteem"
    against zenodo -- that source was never actually checked, and using
    the osf/dataverse row's date would silently skip everything zenodo
    has ever published for the term. A row with no parseable sources=
    (legacy) is treated as not covering anything, so it can't wrongly
    narrow the window either -- it just falls through to the fallback
    lookback, which is always safe (only ever searches more, not less)."""
    best = None
    try:
        with open(log_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("query", "").strip().lower() != term.strip().lower():
                    continue
                if not row.get("output_file", "").startswith(OUT_PREFIX):
                    continue
                logged_sources = _parse_logged_sources(row.get("notes", ""))
                if logged_sources is None or not active_sources.issubset(logged_sources):
                    continue
                d = row.get("date", "").strip()
                if d and (best is None or d > best):
                    best = d
    except FileNotFoundError:
        return None
    return best


def append_log_rows(rows: list[dict], log_path: str = LOG_PATH) -> None:
    fieldnames = ["date", "query", "output_file", "notes"]
    file_exists = True
    try:
        open(log_path, "r").close()
    except FileNotFoundError:
        file_exists = False
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["weekly", "full"], default="full",
                     help="weekly: HIGH_YIELD_TERMS subset (~15 terms), for a frequent "
                          "small-scope pass. full: TERM_LIST (~100 terms), the original "
                          "monthly sweep. Default 'full' preserves this script's original "
                          "behavior for the existing scheduled routine.")
    ap.add_argument("--sources", metavar="NAME", nargs="+", default=DEFAULT_SOURCES,
                     help=f"sources to query (choices: {', '.join(SOURCE_MAP)})")
    ap.add_argument("--default-lookback-days", type=int, default=90,
                     help="--since to use for a term with no prior monthly run")
    ap.add_argument("--dry-run", action="store_true",
                     help="print each term's computed --since date and exit, no queries run")
    ap.add_argument("--out", default=None,
                     help=f"output CSV (default: {OUT_PREFIX}<mode>_<today>.csv)")
    args = ap.parse_args()

    unknown = set(args.sources) - set(SOURCE_MAP)
    if unknown:
        ap.error(f"Unknown sources: {', '.join(unknown)}. Choices: {', '.join(SOURCE_MAP)}")
    active_sources = [SOURCE_MAP[s] for s in args.sources]

    terms = HIGH_YIELD_TERMS if args.mode == "weekly" else TERM_LIST

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fallback_since = (datetime.now(timezone.utc) - timedelta(days=args.default_lookback_days)).strftime("%Y-%m-%d")

    active_sources_set = set(args.sources)
    since_by_term = {}
    for term in terms:
        prior = last_run_date(term, active_sources_set)
        since_by_term[term] = prior if prior else fallback_since

    if args.dry_run:
        print(f"Mode: {args.mode} ({len(terms)} terms). Sources: {', '.join(args.sources)}")
        for term, since in since_by_term.items():
            origin = "prior monthly run (same source set)" if last_run_date(term, active_sources_set) else f"first run at this source set, {args.default_lookback_days}d lookback"
            print(f"  {term!r}: since={since} ({origin})")
        return

    out_path = args.out or f"{OUT_PREFIX}{args.mode}_{today}.csv"
    exclude = _load_auto_exclusions()
    if exclude:
        print(f"Excluding {len(exclude):,} DOIs already in the IRW dictionary")

    fieldnames = ["source", "title", "doi", "published", "url"]
    outf = open(out_path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()

    hits_by_term = {term: 0 for term in terms}

    def on_hit(h, term):
        hits_by_term[term] += 1
        writer.writerow(asdict(h))
        outf.flush()

    for term, since in since_by_term.items():
        print(f"\n[term] {term!r} (since {since})", flush=True)
        discover([term], exclude, relevance_on=True, sources=active_sources,
                  on_hit=lambda h, term=term: on_hit(h, term), since=since)

    outf.close()

    total = sum(hits_by_term.values())
    print(f"\n{total} candidates found -> {out_path}")

    log_rows = [
        {
            "date": today,
            "query": term,
            "output_file": out_path,
            "notes": f"monthly automated run; {n} candidates; sources={','.join(args.sources)}; since={since_by_term[term]}",
        }
        for term, n in hits_by_term.items()
    ]
    append_log_rows(log_rows)
    print(f"Logged {len(log_rows)} term rows to {LOG_PATH}")


if __name__ == "__main__":
    main()
