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

A row whose script cannot be found is NOT screened, so it is reported as
UNRESOLVED and fails the run. Silently passing a row nobody looked at is the
failure this script exists to stop.

Every other row is screened too (#2049). Assigning codes by position is a
property of the SCRIPT, not of the basis someone later claimed in the ledger:
on 2026-09-07, 24 rows had a positional script and not one of them was in the
NOT_NEEDED/data_labels population, so the screen above covered none of them.
For those rows a positional script is legitimate -- a numeric per-item route
can establish the order -- but only if the evidence says so. A row whose
evidence never speaks to the ordering is reported as a WARN, not a failure:
the keyword test is crude, and a miss means "read the evidence", not "wrong".

So the two outcomes stay separate:
  FLAG  positional script AND the data_labels exemption claimed   -> exit 1
  WARN  positional script, no exemption, evidence silent on order -> exit 0

Usage:  python3 itemtext/check_label_claims.py [mapping_verification.csv] [-v]
Exit 1 if any claim is flagged or unresolved. `-v` also lists the positional
rows whose evidence does address the ordering, and the unscreened ones.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# How many scripts a prefix may match before it stops being a resolution and
# starts being noise. Above this the row is reported UNRESOLVED with the count,
# which is more useful than screening a dozen unrelated siblings.
MAX_PREFIX_HITS = 4

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
    # The newer automated_finding Python scripts rename source columns to a
    # positional code with `enumerate` and an f-string, which none of the
    # R-shaped patterns above see. dong_2025_teacher_leadership, dou2025_area
    # and conspiracy_asd__* all slipped through on these (reported on PR #2041).
    #
    # These are deliberately narrow. The near-identical
    #     ITEM_COLS = [f"Q{i}" for i in range(1, 51)]
    # must NOT match: it GENERATES source column names in order to select them,
    # so the strings have to equal real headers or the selection would raise.
    # The tell is `enumerate` over the columns (position -> new name), or an
    # assignment into `item`, not an f-string with a counter in it.
    #
    # The dict-comprehension pattern binds the loop index with a backreference
    # so that the f-string is numbered by the same variable enumerate supplies.
    (re.compile(r"""\{\s*\w+\s*:\s*f["'][^"'\n]*\{\s*(\w+)\s*(?:[+-]\s*\d+\s*)?\}"""
                r"""[^"'\n]*["']\s+for\s+\1\s*,\s*\w+\s+in\s+enumerate\("""),
     'rename(columns={col: f"..._{i}"}) over enumerate'),
    (re.compile(r"""\[\s*["']item["']\s*\]\s*=\s*\[\s*f["']"""),
     'item = [f"..." for ...]'),
    (re.compile(r"""\w+\[\s*f["'][^"'\n]*\{\s*(?:rank|i|idx|pos|n)\s*\}[^"'\n]*["']\s*\]\s*="""),
     'new column named by a loop rank'),
]

# Tier 2: the code is DERIVED from the source column name rather than kept
# verbatim. Shift risk is nil (the derivation is reversible), but the
# `data_labels` exemption still may not hold: these sources are typically bare
# CSVs whose headers are codes, with the wording in a separate codebook. Worth
# a look, not an alarm.
DERIVED = [
    (re.compile(r"item\s*=\s*as\.numeric\(str_replace"), "numeric-stripped column name"),
    (re.compile(r"item\s*=\s*substr\(item"), "truncated column name"),
    # Choosing the item columns by position rather than by name. Not itself a
    # code assignment, but the column SET can shift under it if the source
    # sheet changes -- dou2025_area slices [27:39] across `Unnamed` gap columns.
    (re.compile(r"\.columns\[\s*\d+\s*:\s*\d+\s*\]"), "positional column slice"),
]


# What evidence that addresses a positional script's ordering tends to say.
# Deliberately broad: a WARN that fires on evidence which does explain the
# order costs a reader a minute, a keyword list tight enough to miss real
# explanations would train people to ignore it. Written against the 24 rows
# measured on #2049 -- `short_dark_triad` ("item k must be the k-th column"),
# `riasec` ("columns in file order"), `depression_anxiety_stress` and
# `face_memory_test` (re-deriving the code), and the route-9 cell-count
# matches, which distinguish items on their own. Matched against `route` and
# `evidence` together.
ORDER_EVIDENCE = re.compile(
    # Not bare "order": "in order to" is in half the evidence column.
    r"\bordered\b|\bordering\b|\b(?:column|file|item|header|source|same|wave) order\b"
    r"|\bposition(?:al|ally)?\b|\bk-?th\b|\bsequen"
    r"|\brow_number\b|\benumerate\b|\bcolumn[- ]order|\bfile order"
    r"|\bre-?deriv|\bre-?ran\b|\bre-?run\b|\bcell[- ]count|\broute[- _]?9\b"
    r"|\bitem \d+\s*(?:\.\.|-|to)\s*\d+|\bi\.e\. irw item"
    # A per-item statistic that separates every item from every other item
    # establishes the order by itself, whatever the script did.
    r"|\bdistinguish|\bcell for cell\b|\bmutually distinct|\ball \d+ [^.;]{0,40}distinct",
    re.I)


def _positional(text: str) -> str | None:
    """The first Tier-1 pattern the script trips, or None."""
    return next((w for p, w in POSITIONAL if p.search(text)), None)


def _sources() -> list[tuple[Path, str]]:
    """Every processing script under data/, with its text, read once."""
    out = []
    for p in sorted(DATA.rglob("*")):
        if p.suffix not in {".R", ".r", ".py"} or not p.is_file():
            continue
        try:
            out.append((p, p.read_text(errors="replace")))
        except OSError:
            pass
    return out


def _prefixes(table: str) -> list[str]:
    """`table` itself, then progressively shorter prefixes on `__` then `_`.

    A multi-table script never contains the literal table name -- it builds it
    from a loop variable (`f"dpt_noncog__{scale_name}.csv"`,
    `wide[f"{prefix}_{rank}"]`). The stable part is the prefix, so fall back to
    that rather than giving up.
    """
    out = [table]
    if "__" in table:
        out.append(table.split("__")[0])
    stem = out[-1]
    while "_" in stem:
        stem = stem.rsplit("_", 1)[0]
        if len(stem) >= 6:
            out.append(stem)
    return out


def scripts_for(table: str, sources: list[tuple[Path, str]]) -> tuple[list[Path], str]:
    """Scripts for this table, and how they were matched.

    Returns ([], "") when nothing resolves. A prefix match is reported
    separately from a literal one because it is a weaker claim: it can pull in
    a sibling script, which is the safe direction (it can only add a flag).
    """
    # A script named for the table is authoritative: sibling scripts routinely
    # mention a table in a comment ("companion to ...") without building it,
    # which otherwise produces a cross-file flag on the wrong script.
    exact = [p for p, _ in sources if p.stem == table]
    if exact:
        return exact, "literal"

    # A script whose underscore-stripped stem is a prefix of the table's own
    # stripped name: `gilbertmeta.R` builds `gilbert_meta_16`. Checked before
    # the prefix chain because `gilbert_meta` alone matches 14 sibling scripts.
    flat = table.replace("_", "").lower()
    stem_hits = [p for p, _ in sources
                 if len(p.stem) >= 6 and flat.startswith(p.stem.replace("_", "").lower())]
    if stem_hits and len(stem_hits) <= MAX_PREFIX_HITS:
        return stem_hits, "script name"

    widest = ""
    for i, token in enumerate(_prefixes(table)):
        hits = [p for p, text in sources if token in text]
        # A short prefix can match half the directory; that is not a
        # resolution, it is noise. Keep shortening, but remember the best
        # near-miss so an unresolved row still points somewhere.
        if hits and len(hits) <= MAX_PREFIX_HITS:
            return hits, ("literal" if i == 0 else f"prefix '{token}'")
        if hits and not widest:
            widest = f"'{token}' matches {len(hits)} scripts, too broad to screen"

    # Last resort: the table's most distinctive token. A study name survives
    # even when the prefix does not -- `gad_BrummerHoffman_2021` is built by
    # `BF_BrummerHoffman_2021.R`, which shares no prefix with it at all.
    for token in sorted((t for t in table.split("_") if len(t) >= 8), key=len, reverse=True):
        hits = [p for p, text in sources if token in text or token in p.stem]
        if hits and len(hits) <= MAX_PREFIX_HITS:
            return hits, f"token '{token}'"
    return [], widest


def main(argv: list[str]) -> int:
    verbose = "-v" in argv or "--verbose" in argv
    args = [a for a in argv[1:] if a not in ("-v", "--verbose")]
    path = Path(args[0]) if args else Path(__file__).parent / "mapping_verification.csv"
    rows = list(csv.DictReader(path.open()))

    def exempt(r):
        return (r["status"].strip() == "NOT_NEEDED"
                and r["mapping_basis"].strip() == "data_labels")
    claims = [r for r in rows if exempt(r)]
    others = [r for r in rows if not exempt(r)]

    sources = _sources()
    texts = dict(sources)
    flagged, derived, unresolved = [], [], []
    for r in claims:
        srcs, how = scripts_for(r["table"], sources)
        if not srcs:
            unresolved.append((r["table"], how))
            continue
        for s in srcs:
            text = texts[s]
            hit = next(((w, flagged) for p, w in POSITIONAL if p.search(text)), None)
            if hit is None:
                hit = next(((w, derived) for p, w in DERIVED if p.search(text)), None)
            if hit is not None:
                why, bucket = hit
                bucket.append((r["table"], s.relative_to(ROOT), why, how))
                break

    # The wider screen (#2049): same script test, every other row.
    silent, spoken, unscreened = [], [], []
    for r in others:
        srcs, how = scripts_for(r["table"], sources)
        if not srcs:
            unscreened.append(r["table"])
            continue
        hit = next(((s, w) for s in srcs if (w := _positional(texts[s]))), None)
        if hit is None:
            continue
        s, why = hit
        entry = (r["table"], r["status"].strip(), s.relative_to(ROOT), why, how)
        said = f"{r.get('route') or ''} {r.get('evidence') or ''}"
        (spoken if ORDER_EVIDENCE.search(said) else silent).append(entry)

    print(f"check_label_claims: {len(claims)} NOT_NEEDED/data_labels rows in {path.name}")
    for table, src, why, how in flagged:
        via = "" if how == "literal" else f", matched by {how}"
        print(f"  [FLAG] {table}: {src}{via} assigns `item` positionally ({why}) -- "
              f"the source's column names are discarded, so the data_labels "
              f"exemption is not earned. Verify by hand.")
    for table, src, why, how in derived:
        via = "" if how == "literal" else f", matched by {how}"
        print(f"  [NOTE] {table}: {src}{via} derives `item` from the column name "
              f"({why}) rather than keeping it verbatim. Reversible, so no shift "
              f"risk, but check the source really carries labels.")
    for table, why in unresolved:
        detail = why or "no processing script found under data/"
        print(f"  [UNRESOLVED] {table}: {detail}, so this row was NOT screened. "
              f"Name the script or screen by hand.")
    if not flagged and not derived:
        print("  no positional item assignment found among the claimed rows")
    if unresolved:
        print(f"  {len(unresolved)} row(s) unresolved -- an unscreened row is not a pass")

    print(f"\ncheck_label_claims: {len(others)} other rows screened for a "
          f"positional script (#2049)")
    for table, status, src, why, how in silent:
        via = "" if how == "literal" else f", matched by {how}"
        print(f"  [WARN] {table} ({status}): {src}{via} assigns `item` "
              f"positionally ({why}), and the evidence never mentions the "
              f"ordering. Make it say how item k was tied to the k-th source "
              f"column, or name the per-item route that establishes it.")
    print(f"  {len(silent) + len(spoken)} row(s) with a positional script: "
          f"{len(spoken)} evidence addresses the ordering, {len(silent)} WARN")
    if verbose:
        for table, status, src, why, _ in spoken:
            print(f"  [ok] {table} ({status}): {src} ({why}); evidence addresses order")
        for table in unscreened:
            print(f"  [unscreened] {table}: no processing script resolved")
    print(f"  {len(unscreened)} row(s) had no resolvable script and were not "
          f"screened (not a failure here; -v lists them)")
    return 1 if flagged or unresolved else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
