#!/usr/bin/env python3
r"""Restore the double quotes that Figshare's `items.csv` exported as backslashes.

The source item bank (10.6084/m9.figshare.14073899, `items.csv`) wrote internal
double quotes as a literal `\` instead of `\"` or `""`, so the published text
reads

    ¿A qué deidad griega representa la estatua de \El Coloso de Rodas\?

where the question asked about "El Coloso de Rodas". This is the source's own
export defect, and the extraction that built the table FOUND it: see
itemtext/skill_test/sessionB_batch/extraction_log_spanishmegastudy.md, which
records the pattern, confirms the backslashes are always paired, and says it
normalised `\` to `"`. That normalisation never reached the published rows --
v38.0 and v39.0 both carry the backslashes -- so this script applies it.

The pairing is what makes the substitution a restoration rather than a guess:
every affected value holds an even number of backslashes, so each one is one
half of a quoted phrase, and no other reading of the character is available.
That invariant is asserted here rather than trusted, and the run refuses if any
value breaks it.

Nothing else about the table changes: same rows in the same order, same
`language` (Spanish, shipped in v39.0), same NA `_translated` columns.

    python3 fix_quoting.py          # published/ -> staging/, then upload with red_up
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = "spanishmegastudy"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

#: The only fields the source exported with the broken convention. The other
#: text fields are ours (`instrument`) or NA in this table, and are left alone
#: even if a backslash ever appears in them -- a backslash outside the quoted
#: item bank would mean something different and should be looked at, not swept.
FIX_COLS = ("item_text", "correct_response", "option_text")

#: A floor, not a target: the measurement on the published v39.0 rows was 667 /
#: 4 / 5 rows across the three columns. If a later release has fixed some of
#: them upstream the script should be deleted, not loosened, so a shortfall is
#: an error.
EXPECTED = {"item_text": 667, "correct_response": 4, "option_text": 5}


def main():
    src = os.path.join(HERE, "published", f"{TABLE}.csv")
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"{TABLE}: no published rows at {src}")

    counts = {c: 0 for c in FIX_COLS}
    out = []
    for r in rows:
        r = dict(r)
        for c in FIX_COLS:
            v = r.get(c) or ""
            n = v.count("\\")
            if not n:
                continue
            if n % 2:
                sys.exit(f"{TABLE}: unpaired backslash in {c}: {v!r}")
            r[c] = v.replace("\\", '"')
            counts[c] += 1
        out.append(r)

    for c, n in EXPECTED.items():
        if counts[c] != n:
            sys.exit(f"{TABLE}: {c} fixed {counts[c]} rows, expected {n} -- "
                     "re-measure against the published table before uploading")

    dst = os.path.join(HERE, "staging", f"{TABLE}__items.csv")
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in out:
            w.writerow({c: r.get(c, "NA") for c in COLS})

    # Read the file back: the assertions above only describe what was in memory.
    with open(dst, encoding="utf-8") as f:
        written = list(csv.DictReader(f))
    assert len(written) == len(rows), f"{len(written)} rows written, {len(rows)} read"
    for before, after in zip(rows, written):
        for c in COLS:
            b, a = before.get(c) or "", after.get(c) or ""
            if c in FIX_COLS:
                # The ONLY edit permitted is backslash -> double quote, so the
                # strings must agree once that substitution is undone.
                assert a.replace('"', "\\") == b.replace('"', "\\"), f"{c} changed: {b!r} -> {a!r}"
                assert "\\" not in a, f"{c} still holds a backslash: {a!r}"
            else:
                assert a == b, f"{c} changed: {b!r} -> {a!r}"

    total = sum(counts.values())
    print(f"  {TABLE:<20} {len(written):>5} rows, {total} field values requoted "
          f"({', '.join(f'{c}={counts[c]}' for c in FIX_COLS)})")
    print(f"\nwritten to {os.path.relpath(dst, HERE)} -- upload with red_up")


if __name__ == "__main__":
    main()
