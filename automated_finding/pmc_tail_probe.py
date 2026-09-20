"""
pmc_tail_probe.py — measure the Data-Availability yield of the unaudited
tail of `pmc_seen_dois.csv`.

The #2203 backlog re-mine covered 260 DOIs: the subset whose pre-fix triage
verdict survived in a committed CSV. The other ~2,900 DOIs in the ledger were
retired by runs whose per-run CSV lived in `runs/` and is gone, so nothing
records whether they were rejected on the supplementary-file path alone.

Rather than pay ~2,900 core lookups + full-text fetches to find out, this
samples the tail and reports the same numbers the #2203 write-up did
(statement found / names a repository / flag mix), so the full pass can be
sized against a measurement instead of a guess.

Read-only with respect to every standing ledger: it never appends to
pmc_seen_dois.csv and never writes outside runs/.
"""
import argparse
import csv
import random
import re
import sys

from irw_triage_updated import preflight_deps
from irw_discover_updated import _load_auto_exclusions, in_runs_dir
from irw_batch_updated import (check_license, extract_external_link,
                               triage_external_link)
from irw_discover_pmc import (fetch_core_license, fetch_fulltext_xml,
                              extract_data_availability, _europepmc_get)

FIELDNAMES = ["doi", "pmcid", "journal", "title", "license", "flag", "reasons",
              "data_availability", "external_link", "data_file", "n_responses",
              "n_participants", "n_items", "density"]

_RE_PMCID = re.compile(r"(PMC\d+)")


def resolve(doi: str) -> dict | None:
    """DOI -> PMCID + title + journal, via one lite Europe PMC lookup."""
    data = _europepmc_get({"query": f'DOI:"{doi}"', "resultType": "lite",
                           "pageSize": 1, "format": "json"})
    hits = (data or {}).get("resultList", {}).get("result", [])
    if not hits:
        return None
    h = hits[0]
    pmcid = h.get("pmcid") or ""
    if not pmcid:
        m = _RE_PMCID.search(h.get("fullTextIdList", {}).get("fullTextId", "") or "")
        pmcid = m.group(1) if m else ""
    if not pmcid:
        return None
    return {"pmcid": pmcid, "title": h.get("title", "")[:200],
            "journal": h.get("journalTitle", "")}


def probe_one(doi: str) -> dict:
    base = {"doi": doi, "pmcid": "", "journal": "", "title": "", "license": "",
            "flag": "", "reasons": "", "data_availability": "",
            "external_link": "", "data_file": "", "n_responses": "",
            "n_participants": "", "n_items": "", "density": ""}
    meta = resolve(doi)
    if not meta:
        return {**base, "flag": "no_pmcid",
                "reasons": "no PMCID for this DOI in Europe PMC"}
    base.update(meta)

    license_norm, blocked, _unknown = check_license(fetch_core_license(meta["pmcid"]))
    base["license"] = license_norm
    if blocked:
        return {**base, "flag": "license_restricted",
                "reasons": f"license '{license_norm}' does not permit redistribution"}

    try:
        xml = fetch_fulltext_xml(meta["pmcid"])
    except Exception as e:
        return {**base, "flag": "no_fulltext", "reasons": str(e)[:200]}

    avail = extract_data_availability(xml)
    base["data_availability"] = avail[:300]
    if not avail:
        return {**base, "flag": "no_statement",
                "reasons": "no Data Availability statement in the JATS full text"}

    link = extract_external_link(avail)
    base["external_link"] = link
    if not link:
        return {**base, "flag": "statement_no_link",
                "reasons": "statement present but names no resolvable repository"}

    return {**base, **triage_external_link(link, dict(base))}


def main():
    preflight_deps()
    ap = argparse.ArgumentParser()
    ap.add_argument("--seen", default="pmc_seen_dois.csv")
    ap.add_argument("--exclude-run",
                    default="runs/pmc_backlog_data_availability_2026-09-16.csv",
                    help="the #2203 re-mine output; its DOIs are already audited")
    ap.add_argument("--sample", type=int, default=100)
    ap.add_argument("--seed", type=int, default=20260919)
    ap.add_argument("--out", default="pmc_tail_probe_2026-09-19.csv")
    args = ap.parse_args()

    seen = [r["doi"].strip() for r in csv.DictReader(open(args.seen))
            if r.get("doi", "").strip()]
    audited = set()
    try:
        audited = {(r.get("doi") or "").strip().lower()
                   for r in csv.DictReader(open(args.exclude_run))}
    except FileNotFoundError:
        print(f"WARNING: {args.exclude_run} not found — the #2203 rows are "
              f"NOT excluded, so this sample is not the unaudited tail.")
    in_irw = _load_auto_exclusions()

    tail = [d for d in dict.fromkeys(seen)
            if d.lower() not in audited and d not in in_irw]
    print(f"{len(seen):,} ledger rows -> {len(tail):,} unaudited "
          f"({len(audited):,} re-mined in #2203, {len(in_irw):,} excluded as "
          f"already in IRW or human_review)")

    rng = random.Random(args.seed)
    sample = rng.sample(tail, min(args.sample, len(tail)))
    out = in_runs_dir(args.out)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES, extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for i, doi in enumerate(sample, 1):
            try:
                row = probe_one(doi)
            except Exception as e:
                row = {"doi": doi, "flag": "error", "reasons": str(e)[:200]}
            w.writerow(row)
            fh.flush()
            print(f"  {i:3}/{len(sample)} [{row.get('flag', ''):20}] {doi}",
                  flush=True)
    print(f"\n{len(sample)} probed -> {out}")


if __name__ == "__main__":
    sys.exit(main())
