# `alsuhibani_2022_ecrs_s3` — replace, do not append

Rebuilt 2026-09-04 to add `wording_rights=NC` after the ECR-R ruling. This file is
**deliberately not staged into `itemtables/clean/`**, because everything in `clean/` is
uploaded by walking the directory, and that would *append* 84 duplicate rows to a table
that already has them.

## What changed

Nothing about the item text. The file was fetched from the live `irw_text` draft and one
column added; `table`, `section_id`, `item`, `instrument`, `instructions`,
`section_prompt`, `item_text`, `correct_response`, `option_text` and `resp` are
byte-identical to what is published. Checked, not assumed.

## Why the column is there

The ECR-R's author states the scales are in the public domain and free for
non-commercial research, but "may not be used for commercial purposes without
permission". IRW's copy of this wording came from the study's own deposited SPSS file
under the article's CC BY licence, so the source governs and the wording ships — but the
instrument-level restriction is recorded so a commercial reuser can find and exclude it
with a query. See `references/itemtext_standard.md` § Rights.

## The procedure

1. **Delete `alsuhibani_2022_ecrs_s3__items` from the `irw_text` draft first.**
   `replace_on_conflict` replaces an upload of the same name; rows inherited from the
   prior version survive alongside it. Deleting the table and re-creating it is the only
   thing that actually replaces the contents.
2. Upload this file.
3. Verify with `SELECT COUNT(*), COUNT(DISTINCT item)` — **84 and 12**. Never `numRows`,
   which reported stale values throughout the doubling incident.
4. Confirm `wording_rights` came through as a real column with `NC` on all 84 rows. This
   is the first table to carry it, so this upload is what widens `irw_text` to hold it —
   the same path the `_translated` columns took.

Only when all four are done should this file be deleted and the batch_004 provenance
note updated.
