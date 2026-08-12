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

**If the dictionary URL points at a CRAN package** (MPsychoR, psychTools, psychotools,
PCMRS, etc.), check the package's own `Rd_db()` documentation before searching for a
paper — it's faster and more authoritative than reconstructing item wording from a paper
citation:
```r
library(tools)
db <- Rd_db("MPsychoR")
Rd2txt(db[["Dataset.Rd"]])
```
This has recovered full verbatim item wording directly for several tables across this
skill's use.

**If a source codebook is an old binary `.doc` file (not `.docx`)**, Python's
`zipfile`-based `.docx` parser can't read it — convert it first:
```bash
soffice --headless --convert-to txt file.doc
```
LibreOffice is available in this environment; this has recovered otherwise-inaccessible
codebook text (e.g. old Florida Twin Project codebooks) that would otherwise look like a
dead end.

### Step 3b — Verify the table name/description actually matches what you found

Before extracting, check that the instrument you're about to transcribe is the one the
table is actually built from — don't assume the table name or dictionary Description
names the right instrument just because it's the obvious reading of the source paper.
A paper commonly administers several instruments (a named scale plus demographic/
comorbidity checklists, or several scales in the same battery), and the table name can
end up describing the wrong one. Cross-check the live `item`/`resp` values from Step 2
against what you're about to transcribe: does the item count, response range, and item
content actually match the named instrument, or does it look like a different measure
from the same study? Real examples hit in testing: a table named for a kinesiophobia
scale (TSK-17) whose live items were actually a baseline comorbidity checklist from the
same paper's Table I; a table named for the Insomnia Severity Index whose live items
were actually that study's PHQ-9; a table named for the FAD-Plus whose live items were
actually the Rosenberg Self-Esteem Scale administered alongside it. In each case the
live data matched a *different* instrument in the same source than the one implied by
the table name. A subtler variant: a table named for the Reading the Mind in the Eyes
Test (RMET) whose live items were actually the Imposing Memory Task, a distinct
secondary Theory-of-Mind measure from the same paper — here both instruments were
independently plausible names for the paper's ToM battery, so the mismatch only showed
up by checking the live item content (story-vignette text, not eye-photo trials) against
what RMET items actually look like, not by the name alone looking obviously wrong.

If you find a mismatch: extract against what the live data actually is (not what the
name implies), set the `instrument` field to the correct instrument name, and log it via
Step 6b so the table name/dictionary Description can be corrected — don't force-fit the
extraction to match the table's name.

## Step 4 — Extract and structure

Build the 4-tab structure (see `references/itemtext_standard.md` for exact columns),
in memory or as a scratch CSV — you don't have to actually create Sheets tabs, just
produce data shaped like them before merging:

- **instrument/instructions** — full instrument name + literal instructions text that
  applies to the entire table regardless of `section_id`.
- **section_id/section_prompt** — only for testlets/shared-passage items, and scoped to
  just the items sharing that `section_id` (e.g. a passage or context given before a
  testlet). If the instrument has no such grouping, still emit one `section_id` per item
  (e.g. `<table>_1`) with a blank `section_prompt`, rather than omitting the column — the
  merge step needs a join key. Never record the same span of source text in both
  `instructions` and `section_prompt` — decide which one it belongs to (whole-table
  framing goes in `instructions`; testlet/passage-specific text goes in `section_prompt`
  only, even if it reads like instructional language) and record it once. See
  `references/itemtext_standard.md` for the full rule. **When a table has more than one
  `section_id`, check whether the framing text actually differs by section before
  defaulting to `instructions`** — e.g. a self-report and parent-report block of the same
  instrument often share near-identical wording that differs only in a few words ("how
  you feel" vs. "how your child feels"). If the wording varies at all across sections,
  that's decisive: it's section-specific and belongs in `section_prompt` for each section,
  never in `instructions`, even if it reads like generic whole-table framing at a glance.
  Only text that is truly identical across every section (or a genuinely single-section
  table with no other candidate text) should go in `instructions`.
- **item/item_text/correct_response** — `item` values must be exactly the ones from
  Step 2's ground truth, not invented. `correct_response` blank when there's no scoring
  key; semicolon-separated when multiple answers are correct (e.g. `A;C`). **When the
  ground-truth `item` values are bare integers** (e.g. `1`, `2`, `3` rather than named
  codes like `q1_anx`), you have to reconstruct which paper item each integer refers to
  — usually by position/order in the instrument. Confirming that `resp`'s type and range
  look plausible for that item (e.g. "a 1–5 Likert item exists") is not sufficient
  validation on its own, since many items in the same instrument share the same response
  range and would pass that check regardless of which one you picked. Before assigning
  `item_text` to a specific bare-integer `item`, cross-check the paper's stated item
  count and presentation order, and any distinguishing wording/position cues (item
  numbering in a table/appendix, subscale grouping, reverse-scored markers) — don't rely
  on range-matching alone. If the mapping is genuinely ambiguous, say so and log it per
  Step 6b rather than guessing.
- **resp/option_text** — `resp` values must be exactly the ones from Step 2's ground
  truth. Map extracted option text onto that existing numeric/ordinal coding — for a
  standard Likert-style instrument this is usually the ascending order the paper
  presents options in, but check against the instrument's known scoring convention
  rather than assuming. When the scoring key can't be recovered (the source only gives
  a categorical/lettered code with no way to tie it to the existing numeric `resp`), put
  the raw option in a `raw_resp` column instead of forcing it into `resp` — see
  `gilbert_meta_11` for a real example of this pattern.

**Match the source's terseness.** Transcribe `instructions`, `section_prompt`,
`item_text`, and `option_text` at the same level of brevity as the source material. If
the paper's instructions are one short sentence, keep it one short sentence — don't
expand it into an explanatory paraphrase. If item stems are terse phrases (e.g. "Felt
nervous"), keep them terse; don't pad them into full explanatory sentences or add
clarifying boilerplate that isn't in the original text. The goal is a literal transcript,
not a rewrite for clarity.

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

**Also check row count per item** (`table(gt$item)` on the live data) even when the item
*set* matches exactly — a matching set doesn't rule out one item code silently standing
in for two different questions. This caught a real case where one item had 4x the row
count of every other item because it was quietly conflating two distinct questions under
one code; content review alone didn't surface it, the row-count anomaly did.

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
  populated Sheet1 row, unless told to redo it. **Exception: Audit mode (below)
  deliberately targets already-done tables — that guard protects the queue workflow from
  duplicating in-flight human work and doesn't apply there.**
- Cache fetched PDFs/pages under `itemtext/.cache/<table>/` (gitignored) so retries on
  paywalled/rate-limited sources don't refetch.

## Audit mode — reprocessing tables that already have itemtext

Triggered by **"audit itemtext for X"** / **"audit the itemtext batch"**. Unlike the
queue workflow, this deliberately reprocesses tables that already have a curated Redivis
itemtext entry, to check whether that curation has drifted from the live
`irw::irw_fetch(table)` data. Motivated by
[ben-domingue/irw#1594](https://github.com/ben-domingue/irw/issues/1594) and a follow-up
audit that both found: every time a from-scratch extraction disagreed with existing
curation, the curation was the stale one, not the extraction.

1. **Candidate list** = `irw::irw_list_itemtext_tables()` directly — the ~421 tables that
   already have an itemtext entry. Don't run `list_candidates.R`'s queue diff or check
   Sheet1/index-workbook status for these; that machinery exists to avoid duplicating
   unclaimed human work on new tables and isn't relevant here.
2. **Extract** — same as Steps 2–4 above (fetch the live `item`/`resp` target via
   `table_context.R`, find the source paper, extract and structure). Write the result to
   a staging path, not `itemtext/<table>__items.csv` — e.g.
   `itemtext/audit_staging/<table>__items.csv` — so it can never be picked up by a stray
   `python3 upload.py .` before review.
3. **Diff** — run:
   ```bash
   Rscript .claude/skills/irw-auto-itemtext/scripts/diff_itemtext.R <table> itemtext/audit_staging/<table>__items.csv itemtext/audit_pending_review/<table>_diff.md
   ```
   This compares the staged extraction against `irw::irw_itemtext(table)` (current
   curation) using the same edit-ratio/Jaccard/resp-set-alignment/swap-tolerant
   instructions-section_prompt logic validated across the 100-table eval, and prints a
   suggested classification (`confirm` or `review`) plus an itemized mismatch list. This
   split is mechanical (similarity thresholds) — treat it as a starting triage, not a
   final answer; every `review` result needs the human judgment call in step 4 below,
   reading the actual mismatches rather than trusting the label. **When eyeballing
   `irw::irw_itemtext()` or `irw::irw_fetch()` output manually (outside the scripts
   above)**, always use `nrow()`/explicit `unique()` on the exact columns needed rather
   than scanning a bare `print()` or `head()` — a tibble's default print truncates to 10
   rows, and a truncated view has caused both a false "mismatch" alarm (an alphabetically-
   first subset of items looked like the wrong instrument until the full set was pulled)
   and an overstated real finding (claiming a field was "entirely missing" when a
   truncated print just hadn't shown the populated rows).
4. **Route the result into one of four statuses** (not just confirm/review — a `review`
   result always resolves into exactly one of green/yellow/red/gray):
   - 🟢 **Green** — `confirm`, or a `review` where the mismatches turn out to be noise
     (e.g. cosmetic wording, not substance). Append one row to
     `itemtext/audit_confirmed.csv` (columns `table,date,note`; create with a header if it
     doesn't exist) and stop — no Redivis write, no further action unless re-audited later.
   - 🔴 **Red** — the diff shows a genuine, evidence-backed problem with the *curated*
     version (fresh extraction matches a live `irw::irw_fetch(table)` check where curation
     has a gap — missing items, missing `resp` categories, a stale resp range, items that
     don't exist in live data, etc.) that needs human review and likely replacement. File
     a GitHub issue (`gh issue create --repo ben-domingue/irw --label "data fix" --label
     "ITEMS"`, title `` `table_name` <short description> ``, body with Summary/Evidence/
     Recommended fix sections — see #1594/#1600-1607 for the template) **and** list it in
     the batch report. **If the problem looks like it could be systemic** (a mislabeled
     instrument, a swapped dictionary field) rather than a one-off, check sibling tables
     from the same paper/project before writing the issue — every apparent mislabel found
     across this skill's use turned out to be isolated to the one table once siblings were
     checked, so note in the issue whether you verified that (and how), rather than
     leaving it open-ended. **Never run `upload.py` on an audit-mode table without the user's
     explicit per-table or per-batch approval first** — filing the issue is not the same
     as approval to replace; `upload.py` replaces a table's entire content on conflict (no
     row-level merge), so nothing gets auto-uploaded. Only after explicit approval, copy
     the approved tables' CSVs from `audit_staging/` into a clean temp directory and run
     `python3 upload.py <tempdir>`.
   - 🟡 **Yellow** — the curated version is fine to keep as-is, but there's a specific,
     articulable limitation worth telling website users about (e.g. some items aren't
     documented in the one source checked, a translation is independently-derived rather
     than verbatim-sourced) — distinct from red because there's no evidence the curated
     content is *wrong*, just an honest caveat about what was and wasn't confirmed. Draft
     the exact `.qmd` `.callout-warning` block for `itemtext_issues.qmd` (match the
     existing page's format — see batch01_pilot.md for a worked example) and include it in
     the batch report for later extraction to the website; don't edit
     `itemtext_issues.qmd` directly as part of this routine.
   - ⚪ **Gray** — could not be independently confirmed at all (source blocked, no primary
     material found, or a same-instrument-different-source-language ambiguity like
     `mpsycho_rogers_ocd`'s wording variant) and there's *no evidence either way* — not
     confirmed clean (so not green) and no specific issue to document (so not yellow).
     Log via Step 6b (`itemtext/pending_index_notes.csv`) as a candidate for retry later
     with a different source, not as a resolved outcome.
5. **Batch report**: write one `itemtext/audit_batch_reports/batchNN_<label>.md` per
   audit-mode run, using `batch01_pilot.md` as the template — a summary count table, then
   one section per status with the per-table detail (including yellow's ready-to-paste
   website text and red's issue links).

## Batch behavior

- **"Generate item text for X"** — Steps 2–6 for that one table.
- **"Process the itemtext queue"** — Step 1 to get open candidates, then work through
  them one at a time (Steps 2–6 each). Given Step 3's paper/PDF lookup is the slow,
  judgment-heavy part, don't try to batch dozens unattended — process a handful, report
  what landed vs. what's in the "couldn't fully automate" bucket, and let the user
  redirect before continuing.
- **"Audit itemtext"** — same pacing caveat as the queue: Step 3's lookup is still the
  slow part, so process a handful of already-done tables per session (start with a small
  pilot batch before committing to all ~421), write the batch report (green/yellow/red/gray
  breakdown per the Audit mode section above), and let the user redirect rather than
  trying to reprocess everything unattended.

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
