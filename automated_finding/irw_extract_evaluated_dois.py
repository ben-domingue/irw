#!/usr/bin/env python3
"""
irw_extract_evaluated_dois.py
==============================
Extracts DOI-like identifiers for every dataset already evaluated (any
outcome — good, skip, human_review, worth_retrying, processed) in
BATCH_LOG.md, normalized to the same form irw_discover_updated.py uses.

Why this exists: irw_discover_updated.py's auto-exclusion only checks the
IRW dictionary sheet and the processing-queue "to be processed" sheet — a
dataset that was already looked at and explicitly *skipped* isn't recorded
in either, so it can resurface as a "new" candidate in a later batch and get
re-reviewed from scratch. DVN/5ZQHV6 did exactly this in both batch 14 and
batch 15 (matched on shape by the triage heuristic both times, despite
being explicitly documented as ineligible after batch 14). BATCH_LOG.md is
the only place "already evaluated, regardless of outcome" is recorded, so
this script mines it for a supplementary exclusion set.

This is a heuristic, not a guarantee: it only catches datasets that were
mentioned with a recognizable DOI/identifier in BATCH_LOG.md's prose. A
dataset discussed by title only, with no ID given, won't be caught. Because
a false *positive* here (wrongly excluding a genuinely new candidate) is
worse than a false negative (an occasional redundant re-review, the
pre-existing status quo), treat this as a secondary filter to review before
trusting blindly — spot-check what it excludes, especially early on.

Usage:
    python irw_extract_evaluated_dois.py                   # print count + list
    python irw_extract_evaluated_dois.py --out dois.txt     # write to file
    python irw_extract_evaluated_dois.py --check candidates_batch16.csv
        # report which candidate rows match an already-evaluated DOI

Import usage (e.g. from a merge/filter step in a batch):
    from irw_extract_evaluated_dois import extract_evaluated_dois
    already_seen = extract_evaluated_dois()
    df = df[~df["doi"].apply(norm_doi).isin(already_seen)]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from irw_discover_updated import norm_doi

DEFAULT_LOG = Path(__file__).resolve().parent / "BATCH_LOG.md"


def extract_evaluated_dois(path: str | Path = DEFAULT_LOG) -> set[str]:
    text = Path(path).read_text(encoding="utf-8")
    dois: set[str] = set()

    # Explicit DOIs anywhere in the text.
    for m in re.finditer(r'10\.\d{4,9}/[^\s,)\]"\'>]+', text):
        d = norm_doi(m.group(0).rstrip('.,;:)'))
        if d:
            dois.add(d)

    # Dataverse shorthand: DVN/XXXXXX
    for m in re.finditer(r'\bDVN/([A-Za-z0-9]+)\b', text):
        dois.add(norm_doi(f"10.7910/dvn/{m.group(1)}"))

    # figshare NNNNNNN (article id, with or without a literal "figshare" prefix)
    for m in re.finditer(r'figshare[/\s.]?(\d{6,9})', text, re.I):
        dois.add(norm_doi(f"10.6084/m9.figshare.{m.group(1)}"))

    # osf.io/xxxxx
    for m in re.finditer(r'osf\.io/([a-z0-9]+)', text, re.I):
        dois.add(norm_doi(f"10.17605/osf.io/{m.group(1)}"))

    # zenodo record NNNNN
    for m in re.finditer(r'zenodo[/\s.]?(\d{4,9})', text, re.I):
        dois.add(norm_doi(f"10.5281/zenodo.{m.group(1)}"))

    # Legacy sanitized-filename convention from early batches, e.g.
    # "10_7910_dvn_ireejj.csv" -> 10.7910/dvn.ireejj
    for m in re.finditer(r'\b10_(\d{4,9})_([a-z0-9_]+?)(?:\.csv|\.py)\b', text, re.I):
        prefix, rest = m.group(1), m.group(2)
        dois.add(norm_doi(f"10.{prefix}/{rest.replace('_', '.', 1)}"))

    return dois


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=str(DEFAULT_LOG))
    ap.add_argument("--out", default=None, help="write the DOI list to this path")
    ap.add_argument("--check", default=None,
                     help="candidates CSV to check against the exclusion set "
                          "(reports matches, does not modify the file)")
    args = ap.parse_args()

    dois = extract_evaluated_dois(args.log)
    print(f"Extracted {len(dois)} normalized DOI-like identifiers from {args.log}")

    if args.out:
        Path(args.out).write_text("\n".join(sorted(dois)) + "\n")
        print(f"Wrote to {args.out}")
    elif not args.check:
        for d in sorted(dois):
            print(d)

    if args.check:
        import csv
        with open(args.check, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        matches = [r for r in rows if norm_doi(r.get("doi", "")) in dois]
        print(f"\n{len(matches)} of {len(rows)} candidates in {args.check} "
              f"match a DOI already evaluated in {args.log}:")
        for r in matches:
            print(f"  {r.get('doi','')}  —  {r.get('title','')[:70]}")


if __name__ == "__main__":
    main()
