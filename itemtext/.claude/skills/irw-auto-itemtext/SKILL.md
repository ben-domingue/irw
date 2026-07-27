---
name: irw-auto-itemtext
description: This skill should be used when the user asks to "generate item text for X", "process the itemtext queue", "extract items for this table", or otherwise references transcribing/extracting instrument, section, item, or response-option text for an IRW table from its source paper. Also applies when the user references itemtext/join.R, itemtext/upload.py, the itemtext index workbook, or the itemtext.html public schema.
---

# IRW Item Text Extraction

Transcribes the literal instrument/section/item/response-option text for an IRW table
from its source paper and writes it as a validated `{table}__items.csv`, ready for
`itemtext/upload.py`. The output format is defined in `references/itemtext_standard.md`
(copied verbatim from itemresponsewarehouse.org/itemtext.html) — read it before
extracting anything, don't re-derive the schema from a merged example alone.

Work from inside `itemtext/`.

## Output path: CSV-direct, not Sheets-fill

**Confirmed with the user (2026-07-27): this skill writes `{table}__items.csv` directly
— it does not create or fill the 4-tab per-table Google Sheets that the human workflow
uses.** Two reasons this was chosen over Sheets-fill, in case the decision needs
revisiting later:

1. No tool available to this skill can edit individual tabs of an existing multi-tab
   Google Sheet — only whole-file create/copy/read. The `irw-automated-finding` skill
   hit the identical gap and settled on writing CSVs directly rather than claiming a
   sheet was updated it couldn't actually touch; this skill follows the same precedent.
2. It matches the direction already taken elsewhere in this repo's automation: auto-fill
   and write directly, human spot-checks the output rather than reviewing an
   intermediate editable surface.

This means: **do not** attempt to write into the Sheet1 `instrument`/`sections`/`items`/
`responses` link columns for tables this skill processes, and don't create new per-table
spreadsheets. `join.R` still exists and still works the old way for anyone using the
manual Sheets-fill workflow on a different table — don't modify it.

## Before doing anything

1. Read `references/itemtext_standard.md` for the schema and the per-tab column layout.
2. Check whether a `{table}__items.csv` already exists locally in `itemtext/` for the
   table in question — if so, don't reprocess without being told to redo it.
3. Note: there's no standing local cache directory yet. If you fetch a paywalled or
   rate-limited source PDF, save it under `itemtext/.cache/<table>/` (already gitignored)
   so a retry doesn't re-fetch it. Create the directory if it doesn't exist.

## Step 1 — Find a candidate table

If the user names a specific table, skip to Step 2.

For "process the queue", run:

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/list_candidates.R
```

This diffs `irw::irw_list_itemtext_tables()` (done) against `irw::irw_list_tables()`
(all), then removes anything already claimed or excluded via the index workbook's
`queue`, `tables_excluded`, `xz_todo`, `nj_todo` tabs, or already has populated links in
Sheet1 itself. On 2026-07-27 this returned 1233 open candidates out of 2233 total tables
(421 already done, 580 claimed/excluded) — expect similar order-of-magnitude numbers.
The four cross-check tabs have inconsistent internal schemas (some have headers, some
don't; column names differ) — the script does a raw substring match across each tab's
lines rather than assuming a shared structure, which is deliberate, not a shortcut to
fix later.

A "PRESENT -- inspect before proceeding" hit on any of those tabs doesn't necessarily
mean skip outright — e.g. `xz_todo`/`nj_todo` may just mean someone flagged it for
later, not that it's actively claimed. Use judgment; when genuinely unsure whether a
table is claimed, ask rather than duplicate someone's in-flight work.

## Step 2 — Get the ground truth and source-paper leads

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/table_context.R <table>
```

Prints, in one shot:
- The exact `item` and `resp` value sets from `irw::irw_fetch(table)` — this is the
  target the extraction must hit, not a nice-to-have. Every `item` and `resp` value you
  write must come from this set; never invent one.
- The dictionary row (Description, URL for data, Reference, DOI for paper) — same
  source used for dataset processing scripts.
- This table's current status in the index workbook (existing NOTES, whether Sheet1
  links are already populated, and presence on the four cross-check tabs). If links are
  already populated, the script prints a STOP — respect it.

## Step 3 — Get the source paper/instrument

Use the DOI/URL from Step 2 to find the paper. **Item-level text often lives in a
supplementary/appendix file rather than the main paper body** — check for supplementary
material links (journal site, OSF/Dryad/Figshare companion records, a "Supporting
Information" section) before concluding the text isn't available. If the paper is
paywalled, try an open-access route (PMC, author's institutional repository, the
dataset's own repository page) before giving up.

Cache anything fetched (PDF or scraped page text) under `itemtext/.cache/<table>/` so a
retry on a rate-limited or slow source doesn't refetch it.

## Step 4 — Extract and structure

Build the 4-tab structure (see `references/itemtext_standard.md` for exact columns),
in memory or as a scratch CSV — you don't have to actually create Sheets tabs, just
produce data shaped like them before merging:

- **instrument/instructions** — full instrument name + literal instructions text.
- **section_id/section_prompt** — only for testlets/shared-passage items. If the
  instrument has no such grouping, still emit one `section_id` per item (e.g.
  `<table>_1`) with a blank `section_prompt`, rather than omitting the column — the
  merge step needs a join key.
- **item/item_text/correct_response** — `item` values must be exactly the ones from
  Step 2's ground truth, not invented. `correct_response` blank when there's no scoring
  key; semicolon-separated when multiple answers are correct (e.g. `A;C`).
- **resp/option_text** — `resp` values must be exactly the ones from Step 2's ground
  truth. Map extracted option text onto that existing numeric/ordinal coding — for a
  standard Likert-style instrument this is usually the ascending order the paper
  presents options in, but check against the instrument's known scoring convention
  rather than assuming. When the scoring key can't be recovered (the source only gives
  a categorical/lettered code with no way to tie it to the existing numeric `resp`), put
  the raw option in a `raw_resp` column instead of forcing it into `resp` — see
  `gilbert_meta_11` for a real example of this pattern.

Merge the four pieces (`items` as the base, then `sections`, `instrument`, `responses`,
each via `merge(..., all.x=TRUE)` on shared key columns) into one data frame — this is
what becomes `{table}__items.csv`.

## Step 5 — Validate before writing anything final

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/validate_items.R <table> <candidate_items.csv>
```

This is the non-negotiable gate — same logic as `join.R`, but reports the actual
mismatched values instead of just TRUE/FALSE. It checks:
- Required columns present.
- `unique(item)` matches `irw::irw_fetch(table)$item` exactly.
- `unique(resp)` matches `irw::irw_fetch(table)$resp` exactly (skipped, by design, when
  the table uses `raw_resp` instead because no scoring key was recoverable).

**Do not force a match.** If the paper discloses a different item count than the live
data (e.g. `fivpei_perrig_2023_attdiff`: 28 items per the paper vs. 21 in the data, noted
in the index sheet), or text can't be fully recovered for every item, emit whatever
partial/defensible structure you have and record the discrepancy per Step 6b — don't
pad, guess, or drop items silently to make the counts line up.

Only once this passes (or the discrepancy is deliberately accepted and logged) does the
CSV get written as `itemtext/<table>__items.csv`.

## Step 6 — Write the output

```r
write.csv(items, file = "<table>__items.csv", row.names = FALSE)
```

Written directly into `itemtext/` (not a subdirectory) — this is where `upload.py`
expects to find files (`python3 upload.py .` uploads everything in the current
directory). Don't upload automatically; that's a separate, explicit step (see
"Uploading", below) since it pushes to the shared `bdomingu/IRW_text:next` Redivis
dataset.

### Step 6b — Logging discrepancies (no Sheets-write tool available)

There is no tool that can write into the index workbook's NOTES column directly — same
gap as Step 1's cross-check tabs, just on the write side. When validation surfaces a
real discrepancy (item-count mismatch, partial coverage, source inaccessible), append a
row to `itemtext/pending_index_notes.csv` (columns: `table,note`; create the file with a
header if it doesn't exist yet) and tell the user what to paste into Sheet1's NOTES
column — don't claim the index sheet was updated. This is a standing, cumulative file
like `automated_finding/license_blocked_candidates.csv` — append to it across batches,
don't delete it once a batch is written up; only remove a row once the user confirms
they've pasted it into the actual sheet.

## Idempotency & caching

- Never reprocess a table that already has a local `{table}__items.csv` or an already-
  populated Sheet1 row, unless told to redo it.
- Cache fetched PDFs/pages under `itemtext/.cache/<table>/` (gitignored) so retries on
  paywalled/rate-limited sources don't refetch.

## Batch behavior

- **"Generate item text for X"** — Steps 2–6 for that one table.
- **"Process the itemtext queue"** — Step 1 to get open candidates, then work through
  them one at a time (Steps 2–6 each). Given Step 3's paper/PDF lookup is the slow,
  judgment-heavy part, don't try to batch dozens unattended — process a handful, report
  what landed vs. what's in the "couldn't fully automate" bucket, and let the user
  redirect before continuing.

## Expect a real "couldn't fully automate this one" bucket

The validation gate in Step 5 exists precisely because full automation isn't feasible
for every table — some papers simply don't disclose full item text (see
`tables_excluded`'s existing `"couldn't find item text"` entries), some disclose a
different item count than what's in the live data, and some only give categorical
scoring with no recoverable numeric key. **Don't treat anything short of 100% coverage
as a failure of the skill** — a partial extraction with an honest discrepancy note in
`pending_index_notes.csv` is a correct outcome, not an incomplete one. Move on to the
next candidate rather than forcing a fabricated match.

## Uploading (separate, explicit step — don't do this automatically)

```bash
python3 upload.py .
```

Uploads every `*.csv` in the current directory to `bdomingu/IRW_text:next` on Redivis
(prompts before overwriting anything already there). Only run this when the user
explicitly asks to upload — it's a shared-system write, same caution as any other
Redivis upload in this repo.
