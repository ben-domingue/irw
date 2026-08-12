# Session C_batch grading report (corrected)

This supersedes the first pass of this report. Two bugs in `grade_batch.R`
itself were found and fixed before re-scoring — see (a) below — and the two
`fad_dataset*` "failures" flagged in the first pass turned out to be a third
grading bug, not extraction bugs (see (b)). (c) covers the two lighter-touch
tables. **No changes were made to the skill in this pass** — diagnosis only.

## (a) Corrected abstained-table classification + re-scored numbers

**The bug**: the first pass classified `pending_index_notes.csv`'s 51
free-text notes into an exclusion category via blunt keyword matching
(`"recover"`, `"disclos"`, `"withheld"`, etc.), which over-matched on
negated clauses like *"was **NOT** recovered"* and *"could **not** be
disclosed"*. That put 27 tables into a coarse "abstained" bucket and then
skipped **all** of their item/option/instructions comparisons outright —
including sub-fields that were actually fully populated and gradable (e.g.
`gilbert_meta_80` had `item_text` genuinely blank for copyright reasons but
`option_text`/`resp` fully correct; the old logic discarded all three).

**The fix**: read all 51 notes by hand and assigned each to one of twelve
categories (written to `pending_index_notes_categorized.csv`, alongside the
original file, so this doesn't need to be re-derived by keyword-matching in
future runs). Counts:

| category | n |
|---|---|
| Item text unrecoverable | 12 |
| Full-recovery documentation-only | 9 |
| Numbering ambiguous | 5 |
| Standard-scale wording | 4 |
| Response-scale incomplete | 4 |
| Commercial-copyright withheld | 3 |
| Table-name mismatch | 3 |
| Undocumented quirk | 3 |
| Other | 4 |
| Partial language gap | 2 |
| Author-revised wording | 1 |
| Disclosed-but-wrong-variable-set | 1 |

Only **Item text unrecoverable** and **Commercial-copyright withheld** (12 +
3 = **15 tables**) mean item_text is genuinely blank table-wide for a
source-availability reason — matching the manual pass's expected count
exactly. A byproduct of the hand-read: found and fixed a real casing bug
in the source file itself (`FEDSP_Trzcinska_2023_SMSD` vs. the manifest's
lowercase `fedsp_trzcinska_2023_smsd`), which silently dropped that table's
category in the first join attempt.

`grade_batch.R` no longer uses the exclusion category to bypass grading at
all — it now relies on the existing `is_missing()` per-field check (blank
vs. blank isn't scored; blank vs. populated is a genuine miss, scored 0;
populated vs. populated is graded normally) for every table. The category
only controls which section of the report a table's blanks land in.

**Corrected overall numbers** (85 tables in the main aggregate — 100 minus
the 15 genuinely-abstained minus 0 OCR-sourced — vs. the original pass's
73-table aggregate):

| field | original (73 tables, buggy exclusion) | corrected (85 tables) |
|---|---|---|
| item_text mean / median | 0.80 / 0.99 | 0.82 / 0.99 |
| option_text mean / median | 0.78 / 1.00 | 0.84 / 1.00 |
| context (instructions/section_prompt) mean / median | 0.68 / 0.90 | 0.73 / 0.96 |

The headline numbers moved only modestly despite fixing a real
over-exclusion bug — most of the 12 tables added back in still have partial
gaps (that's why they were flagged in the notes at all), so their gradable
sub-content roughly tracks the existing distribution rather than pulling it
sharply in either direction. Tripwire counts are unaffected by this fix:
still 3/100 tables fail item coverage, 6/96 fail resp-alignment, 79 swap
detections concentrated in the same 5 tables as before.

## (b) fad_dataset1 / fad_dataset2: diagnosis — grading bug, not extraction bug

Both scored **exactly 0.00** item_text similarity in the first pass. Root
cause, confirmed directly by reading both tables' `item_text` values
side-by-side (short fragments only):

- Ground truth stores item text in the **original administered language**
  (Chinese, e.g. `我相信未来是命运已经安排好了的`) in the `item_text` column,
  plus a separate `item_text_translated` column with the English
  translation.
- The candidate's `item_text` field (there is only one text field on the
  candidate side, no language split) is the **English translation** —
  and it matches `item_text_translated` **verbatim, item-for-item**
  (27/27 items on `fad_dataset1`, mean/median edit-ratio 1.00 once
  compared against the correct column).
- `fad_dataset2` has the identical situation, but its `item_text_translated`
  column's header was itself corrupted to `___5` at some point in the
  Session A_batch ground-truth caching step (a duplicate/blank-header
  collision on CSV read) — so it wasn't even recognizable as a translated
  field without opening the file. Once matched against `___5`, `fad_dataset2`
  also scores a perfect 1.00 (59/59 items).

**Both extractions are fully correct.** The 0.00 score was entirely an
artifact of my grading script comparing the candidate's English text
against the ground truth's Chinese column instead of its English one.

**Is this shared with other tables, or a one-off?** Shared, and wider than
just these two: 14 tables in the batch have a real (non-blank)
`<field>_translated` companion column in ground truth —
`fad_dataset1`, `fad_dataset2`, `lys_2020_rape_2_rma`,
`lys_2020_rape_2_rma_pre`, `mexico_2023_quality_problems`,
`mexico_2023_quality_administration`, `mexico_2023_quality_corruptionperception`,
`preschool_sel_pl`, `chile_2023_social-welfare-survey_h`,
`sv-maia2_randelovic_2021_erq`, `sv-maia2_randelovic_2021_maia`,
`heekerens2025_bfi_extraversion`, `sun_2025_morality_study2_meaning`,
`rosenberg_fadplus_goto2021`. `grade_batch.R` now compares each candidate
field against **both** the primary and translated ground-truth text and
keeps whichever scores higher, for `item_text`, `option_text`,
`instructions`, and `section_prompt` alike (including the `___5` alias).
This is folded into the corrected numbers in (a) above, not a separate
adjustment.

**Bare-integer-item finding, corrected**: this changes last report's
headline conclusion substantially. With the bilingual-grading bug fixed,
the bare-integer vs. named-item gap essentially closes:

| has_bare_integer_items | mean item_text sim | mean option_text sim | mean context sim |
|---|---|---|---|
| FALSE (n=74) | 0.87 | 0.93 | 0.75 |
| TRUE (n=11) | 0.80 | 0.90 | 0.66 |

(Previously reported as 0.85 vs. 0.40 — driven almost entirely by
`fad_dataset1`/`fad_dataset2` scoring 0.00 for a grading reason, not an
extraction reason.) Two bare-integer tables now genuinely score 0.00:
`gilbert_meta_100` and `gilbert_meta_74` (both tagged "Numbering ambiguous"
in the corrected category column) — but this is the skill making a
deliberate, documented choice to leave `item_text` blank rather than guess
an item order it couldn't confirm, which ground truth does populate, so a
real 0 is the correct score here (not a bug to chase). Net: **Fix 1 looks
considerably more solid than the first pass suggested** — the remaining
bare-integer gap is small and concentrated in "declined to guess" cases,
not silent wrong-content failures.

## (c) political_psychology and aestheticfluency_cotter2023

**`political_psychology` (0.39 item_text similarity, also fails the
resp-alignment tripwire at 0.81) — a different failure mode from
fad_dataset, not the same root cause.** Direct comparison shows the two
tables' item numbering disagrees, but **not by a constant offset** — e.g.
the candidate's "Trump approval" content lands at item 14 while ground
truth has it at item 12 (+2 shift); the candidate's "feel tense" content
lands at item 21 vs. ground truth's item 14 (+7 shift); "2016 vote choice"
lands at candidate item 28 vs. ground truth item 30 (−2 shift). The
extraction log claims the item order was mechanically re-derived from
`data/political_psychology.R` and cross-validated item-by-item against
ground truth's own resp ranges ("item 7 → abort 1-4 ✓," etc.) — but
checking those specific claims against the actual cached ground truth
directly contradicts them (ground truth item 7 has resp range 1-6, not the
claimed 1-4; item 27 has range 1-7, not 1-3). This suggests either the
ground truth pulled for this batch reflects a different data snapshot than
what the candidate's re-derivation validated against, or a real indexing
bug in how the candidate assigned `item_id`s — worth a manual look at
whether Session A_batch's cached pull and the live column order the
candidate's script produced are from the same underlying data version,
rather than assuming the skill's item-ordering logic itself is wrong.

**`aestheticfluency_cotter2023` (0.63 item_text similarity) — a
terseness/verbosity gap, not a positional or content error.** Every
mismatched item is semantically identical, just longer on the candidate
side: ground truth stores bare surnames (`"dali"`, `"renoir"`, `"sargent"`,
`"klimt"`) matching this artist-recognition instrument's terse checklist
format, while the candidate wrote full names (`"Salvador Dalí"`,
`"Pierre-Auguste Renoir"`, `"John Singer Sargent"`, `"Gustav Klimt"`) for
roughly the first 25 of 36 items before switching to exact matches for the
rest. Content and item order are both correct; this is a Fix 2 (terseness
matching) gap specific to this table's unusually minimal ground-truth
format, not a new failure class.

## Bottom line

- The corrected exclusion logic and the bilingual-grading fix both push the
  overall numbers up modestly and make them more trustworthy; neither
  changes the general shape of the results.
- **Fix 1 (bare-integer reconstruction) is in much better shape than the
  first pass indicated** — the dramatic gap reported earlier was mostly a
  grading artifact. The residual gap is small and traceable to
  well-documented "declined to guess" cases, not silent errors.
- Two distinct, real issues surfaced by this batch that are worth follow-up
  outside this grading pass: (1) `political_psychology`'s non-constant item
  numbering mismatch, which may be a ground-truth/candidate data-version
  mismatch rather than an extraction defect — needs a human check before
  concluding either way; (2) a handful of tables (like
  `aestheticfluency_cotter2023`) where the skill's terseness-matching
  (Fix 2) doesn't fully adapt to an unusually minimal ground-truth format.
