"""
pmc_term_scout.py — cheap per-term yield measurement before a PMC sweep.

SKILL.md's rule for a new journal ("numFound-check the term yield first,
don't build speculatively") applies just as well to a new *term list*: a
150-term sweep across 11 journals is hours of per-candidate downloads, and
the terms that carry it are not knowable a priori.

This does one lite Europe PMC search per term against all target journals at
once (ISSN OR-group, so ~1 request per term rather than 1 per term-journal)
and reports what actually matters: how many relevant, supplementary-bearing,
open-access hits the term has that are NOT already in the IRW dictionary,
human_review/, or pmc_seen_dois.csv. That last count is the term's real
marginal yield.

Read-only: touches no ledger, writes one CSV to runs/.
"""
import argparse
import csv
import sys
import time

from irw_triage_updated import preflight_deps
from irw_discover_updated import _load_auto_exclusions, in_runs_dir, Hit, is_relevant, norm_doi
from irw_discover_pmc import JOURNALS, _europepmc_get, load_seen_dois

FIELDNAMES = ["term", "hits", "relevant", "with_suppl", "new", "journals"]


def scout(term: str, issns: list[str], exclude: set, seen: set,
          max_rows: int = 500, page_size: int = 100) -> dict:
    issn_clause = " OR ".join(f'ISSN:"{i}"' for i in issns)
    cursor, fetched = "*", 0
    hits = relevant = with_suppl = 0
    new_dois, journals = set(), set()
    while fetched < max_rows:
        data = _europepmc_get({
            "query": f'{term} AND ({issn_clause}) AND HAS_FT:y AND OPEN_ACCESS:y',
            "resultType": "lite", "pageSize": page_size,
            "cursorMark": cursor, "format": "json",
        })
        if not data:
            break
        results = data.get("resultList", {}).get("result", [])
        if not results:
            break
        for d in results:
            hits += 1
            title = d.get("title", "")
            if not is_relevant(Hit("pmc", title, "", d.get("doi", ""), ""),
                               enabled=True, query=term):
                continue
            relevant += 1
            if d.get("hasSuppl") != "Y" or not d.get("pmcid"):
                continue
            with_suppl += 1
            doi = norm_doi(d.get("doi", ""))
            if doi and doi not in exclude and doi not in seen:
                new_dois.add(doi)
                journals.add(d.get("journalTitle", "")[:40])
        fetched += len(results)
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
    return {"term": term, "hits": hits, "relevant": relevant,
            "with_suppl": with_suppl, "new": len(new_dois),
            "journals": "; ".join(sorted(journals)[:4])}


def main():
    preflight_deps()
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True, help="file of terms, one per line")
    ap.add_argument("--journals", default=",".join(JOURNALS))
    ap.add_argument("--out", default="pmc_term_scout_2026-09-19.csv")
    args = ap.parse_args()

    slugs = [j.strip() for j in args.journals.split(",") if j.strip()]
    bad = [j for j in slugs if j not in JOURNALS]
    if bad:
        raise SystemExit(f"Unknown journal slug(s): {bad}")
    issns = [JOURNALS[j][0] for j in slugs]

    terms = [t.strip() for t in open(args.terms, encoding="utf-8") if t.strip()]
    exclude, seen = _load_auto_exclusions(), load_seen_dois()
    print(f"{len(terms)} terms x {len(slugs)} journals; excluding "
          f"{len(exclude):,} dictionary/human_review DOIs and {len(seen):,} "
          f"already-triaged DOIs\n")

    out = in_runs_dir(args.out)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES, lineterminator="\n")
        w.writeheader()
        total_new = 0
        for i, t in enumerate(terms, 1):
            row = scout(t, issns, exclude, seen)
            total_new += row["new"]
            w.writerow(row)
            fh.flush()
            print(f"  {i:3}/{len(terms)}  new={row['new']:3}  "
                  f"suppl={row['with_suppl']:3}  hits={row['hits']:4}  {t}",
                  flush=True)
            time.sleep(0.2)
    print(f"\n{len(terms)} terms scouted, {total_new} new candidate DOIs -> {out}")


if __name__ == "__main__":
    sys.exit(main())
