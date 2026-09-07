#!/usr/bin/env python3
"""Screen `NOT_NEEDED` mapping rows whose claimed basis is the source's own
variable labels (#1745).

A `mapping_basis=data_labels` row asserts that the source file ties item code
to item text, so no numeric verification is owed. That exemption is only
earned if the IRW item code really is the source column name. If the
processing script throws the source headers away and numbers the items by
position instead, the claim is false and nothing downstream will notice: both
gates (`audit_batch.R`, `diff_itemtext.R`) compare sets, and a shifted mapping
has an identical item set with plausible text on every row. `lint_verification.R`
cannot see it either -- it exempts NOT_NEEDED/data_labels by construction.

This is the cheap half of the check: read each row's processing script and
flag the ones that assign `item` positionally. A flag is not a defect, it is
a row whose basis has to be established by hand (as 16_personalityfactors was).

Matching is per FILE, not per block, so a script that builds several tables can
flag a table it does not actually mishandle (machivallianism_test_vcl is one).
That is the intended failure direction: a flag means "verify by hand", never
"defect".

Usage:  python3 itemtext/check_label_claims.py [mapping_verification.csv]
Exit 1 if any claim is flagged.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Tier 1: the script replaces the source column name with a POSITION. This is
# the defect class -- a one-position slip is undetectable downstream. These are
# the patterns that produced the abouhashish (#1737) and 16_personalityfactors
# defects; add to the list rather than loosening it.
POSITIONAL = [
    (re.compile(r"item[_ ]*(?:id)?\s*=\s*row_number\(\)"), "row_number()"),
    (re.compile(r"mutate\(\s*item_id\s*=\s*row_number\(\)"), "row_number() item_id"),
    (re.compile(r"rename\(\s*item\s*=\s*item_id\s*\)"), "rename(item = item_id)"),
    (re.compile(r"item\s*=\s*seq_along"), "seq_along"),
    (re.compile(r"item\s*=\s*paste0\(\s*['\"]item_?['\"]"), 'paste0("item_", i)'),
    (re.compile(r"\[\s*['\"]item['\"]\s*\]\s*=\s*(?:range|np\.arange|list\(range)"), "range()"),
    (re.compile(r"item\s*=\s*1\s*:\s*(?:n|len|ncol|nrow)"), "1:n"),
]

# Tier 2: the code is DERIVED from the source column name rather than kept
# verbatim. Shift risk is nil (the derivation is reversible), but the
# `data_labels` exemption still may not hold: these sources are typically bare
# CSVs whose headers are codes, with the wording in a separate codebook. Worth
# a look, not an alarm.
DERIVED = [
    (re.compile(r"item\s*=\s*as\.numeric\(str_replace"), "numeric-stripped column name"),
    (re.compile(r"item\s*=\s*substr\(item"), "truncated column name"),
]


def scripts_for(table: str) -> list[Path]:
    """Processing scripts that mention this table by name."""
    hits = []
    for p in sorted(DATA.rglob("*")):
        if p.suffix not in {".R", ".r", ".py"} or not p.is_file():
            continue
        try:
            if table in p.read_text(errors="replace"):
                hits.append(p)
        except OSError:
            pass
    return hits


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path(__file__).parent / "mapping_verification.csv"
    rows = list(csv.DictReader(path.open()))
    claims = [r for r in rows
              if r["status"].strip() == "NOT_NEEDED"
              and r["mapping_basis"].strip() == "data_labels"]

    flagged, derived, unmapped = [], [], []
    for r in claims:
        srcs = scripts_for(r["table"])
        if not srcs:
            unmapped.append(r["table"])
            continue
        for s in srcs:
            text = s.read_text(errors="replace")
            hit = next(((w, flagged) for p, w in POSITIONAL if p.search(text)), None)
            if hit is None:
                hit = next(((w, derived) for p, w in DERIVED if p.search(text)), None)
            if hit is not None:
                why, bucket = hit
                bucket.append((r["table"], s.relative_to(ROOT), why))
                break

    print(f"check_label_claims: {len(claims)} NOT_NEEDED/data_labels rows in {path.name}")
    for table, src, why in flagged:
        print(f"  [FLAG] {table}: {src} assigns `item` positionally ({why}) -- "
              f"the source's column names are discarded, so the data_labels "
              f"exemption is not earned. Verify by hand.")
    for table, src, why in derived:
        print(f"  [NOTE] {table}: {src} derives `item` from the column name "
              f"({why}) rather than keeping it verbatim. Reversible, so no shift "
              f"risk, but check the source really carries labels.")
    for table in unmapped:
        print(f"  [SKIP] {table}: no processing script found under data/; screen by hand")
    if not flagged and not derived:
        print("  no positional item assignment found among the claimed rows")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
