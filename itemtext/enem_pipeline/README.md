# ENEM item-text pipeline

Everything that builds `itemtext/itemtables/batch_enem_<YYYY>/`, in one place.

It used to be copied into each of the eleven batch directories — 16 files per
year, 2.6 MB of duplicate, and a fix had to land eleven times. Each batch now
keeps only `scripts/README.md`: the record of which pinned versions built it,
with md5s that can be checked against `pins/`.

## Rebuilding a year

    python3 42_rebuild.py --year 2018      # source PDFs -> final tables
    python3 31_assemble_batch.py --year 2018
    Rscript ../.claude/skills/irw-auto-itemtext/scripts/normalize_nulls.R \
            ../itemtables/batch_enem_2018

`42_rebuild.py` is the whole pipeline for one year: font repair, parse, join,
gap fill, then every post-pass. Nine of the eleven years rebuild
**byte-identical** to what is committed, which is what makes a difference in
the tenth worth looking at. 2024 and 2025 come through the DOSVOX text path,
which the driver does not cover yet.

## Why the post-passes are inside the driver

Twice, a correction was applied to the batch directories and then silently
reverted by the next `31_assemble_batch.py`, which recopies the tables out of
`/scratch`. Once it was only null formatting; the second time it would have
un-fixed a minus sign that had shipped as a thorn, and 880 stripped option
letters.

So every post-pass runs inside `42_rebuild.py`, and `31_assemble_batch.py`
**refuses to copy** a table that still carries a post-pass's signature — a
self-prefixed option letter, a known-bad glyph, page furniture, two identical
options. It names the pass that is missing and stops. A README cannot prevent
that mistake; a refusal can.

## Checks that do not need the response data

    python3 41_staleness.py     # artifacts older than the tool that made them
    python3 40_charaudit.py     # every unusual character, by year, with context
    python3 37_anomalies.py     # 12 shape detectors over all items
    python3 50_model_check.py   # answer items from the extracted text alone

`41_staleness.py` exists because 2018 shipped a thorn for a minus while every
script was correct: the repaired PDFs predated the fix. No content gate can see
that — a wrong glyph leaves `item_set_match` TRUE.

## Documentation

- `EXTRACTION_RULES.md` — R0–R11, the contract every year must satisfy
- `STATUS.md` — per-year state and 48 numbered traps, each one a mistake that
  was actually made
- `HANDOFF.md` — entry point for picking the work up
