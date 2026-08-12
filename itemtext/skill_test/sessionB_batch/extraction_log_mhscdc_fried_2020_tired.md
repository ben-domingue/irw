# Extraction log: mhscdc_fried_2020_tired

## Source used
Dictionary URL (https://osf.io/mvdpe/) points to the same OSF project used for the
sibling tables `mhscdc_fried_2020_dass`, `mhscdc_fried_2020_anger`,
`mhscdc_fried_2020_procrastination`, `mhscdc_fried_2020_ps`: Fried & Epskamp (2022),
"Mental Health and Social Contact During the COVID-19 Pandemic: An Ecological
Momentary Assessment Study." Reused the already-cached OSF "6. Measures" component
files under `.cache/mhscdc_fried_2020_dass/` (no new download needed):
- `Measures_Baseline.pdf` / `Measures_Baseline.txt` (participant-facing survey export,
  Baseline assessment) — primary transcription source for items 1-8 (the items that
  appear in the Baseline/"pre" wave).
- `Codebook_Baseline.xlsx`, `Codebook_Post.xlsx` — variable-level codebooks, used to
  confirm the raw-column-to-item mapping and, for items 9-10 (post-wave-only items,
  never asked at Baseline), as the primary source of `item_text` since no
  `Measures_Post.pdf` is cached locally.

`item_text` and `option_text` for items 1-8 were transcribed literally from
`Measures_Baseline.txt` (lines 592-638, "Questionnaire 8" block, items
101(Q#238)-108(Q#245)). Items 9-10 (post-only) were transcribed from
`Codebook_Post.xlsx`'s `Item` column (rows for `clean_post` = Q63 and Q68), since the
Baseline survey never asked them and no cached Post-wave survey-text PDF exists.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` — confirmed. Ground-truth `item`
values are `"item_1"`..`"item_10"` (a named "item_N" convention, not bare integers),
but as with the other sibling tables in this study this is a **generic** naming
convention reused across many sibling tables (dass, anger, ps, procrastination, tired,
etc.), each built from a different question range and, in this table's case, a
*different offset per wave-and-block* — so the mapping was NOT inferred by
position/range-matching on `item_N`'s own numbering, nor assumed to match any sibling
table's offset. It was confirmed directly from `data/mhscdc_fried_2020.r`
(this repo's own processing script), which shows the tiredness-specific calls:

```r
# ----- Tiredness Data -----  some items in post are not in pre.
dass_pre    <- process_dass_data2(bt_df, "Pre",  78, 85, "pre",  77)
dass_post_1 <- process_dass_data2(bt_df, "Post", 59, 62, "post", 58)
dass_post_2 <- process_dass_data2(bt_df, "Post", 64, 67, "post", 59)
dass_post_3 <- process_dass_data2(bt_df, "Post", 63, 63, "post", 54)
dass_post_4 <- process_dass_data2(bt_df, "Post", 68, 68, "post", 58)
```

i.e. `item = paste0("item_", as.integer(str_extract(item_rawname, "\\d+")) - item_offset)`.
This table is unusual among the siblings in that it stitches together **four separate
post-wave column blocks with three different offsets**, plus a fifth pre-wave block:
- Pre columns `Pre78`..`Pre85` (offset 77) -> `item_1`..`item_8`.
- Post columns `Post59`..`Post62` (offset 58) -> `item_1`..`item_4`.
- Post columns `Post64`..`Post67` (offset 59) -> `item_5`..`item_8`.
- Post column `Post63` alone (offset 54) -> `item_9` (63-54=9).
- Post column `Post68` alone (offset 58) -> `item_10` (68-58=10).

This produces the union `item_1`..`item_10`, matching ground truth's 10 items exactly
(items 9 and 10 only ever appear via the post-wave rows, since they were not asked at
Baseline — hence the script's own comment "some items in post are not in pre").

This was cross-checked against the codebooks' own `cleandata_pre` / `clean_post` column
labels: `Codebook_Baseline.xlsx` rows with `cleandata_pre` = `Q78`..`Q85` (spreadsheet
rows 99-106) are labeled `Label/Scale = "Tiredness"` (on the first row) and contain, in
order, 8 item texts; `Codebook_Post.xlsx` rows with `clean_post` = `Q59`..`Q68`
(spreadsheet rows 68-77) are labeled `Label/Scale = "Specifc questions 6"` (generic/
typo'd label on the first row, same pattern as seen for `_procrastination`) and contain
10 item texts in order, where positions 1-4 and 6-9 (Q59-Q62, Q64-Q67) word-for-word
match the 8 Baseline items in the same relative order, and positions 5 and 10 (Q63,
Q68) are the two extra post-only items. This word-for-word match across both codebooks
and the Baseline PDF, item-by-item and in the exact order dictated by the script's
offsets, is the confirmation — not a guess based on `item_N`'s own numbering or
range-matching against the 4-point response scale (which is shared by every item and
would not distinguish between them).

## Instrument identity
The 8-item Baseline block is labeled `"Tiredness"` in `Codebook_Baseline.xlsx`; the
Post block is labeled with the generic `"Specifc questions 6"`. No standalone
published-instrument citation was found in the OSF measures/codebook materials
themselves. However, the item wording — "Do you have problems with tiredness?", "Do
you need to rest more?", "Do you feel sleepy or drowsy?", "Do you have problems
starting things?", "Do you lack energy?", "Do you have less strength in your muscles?",
"Do you feel weak?", "Do you have difficulties concentrating?", plus "Do you start
things without difficulty but get weak as you go on?" — is a close, recognizable match
to the **Chalder Fatigue Scale** (Chalder et al., 1993, "Development of a fatigue
scale," Journal of Psychosomatic Research), which uses this exact "Less than
usual/No more than usual/More than usual/Much more than usual" 4-point response format
and near-identical item stems. `instrument` was recorded as `"Chalder Fatigue Scale"`
based on this wording/response-format match; no explicit citation to Chalder et al. was
found in the cached OSF materials, so this identification is inferential (same
confidence tier as calling the procrastination block "Procrastination Scale" from its
codebook label — here going one step further to name the recognized published
instrument since the wording is a strong match). Item 10 in this dataset ("Do you think
as clearly as usual?") differs somewhat from the standard published 11-item CFQ's
corresponding item ("Do you have problems thinking clearly?"), and the standard CFQ
item "Once you start doing things do you have problems finishing them?" is absent here
— so this is a modified/subset version of the Chalder scale, not necessarily the
canonical 11-item form.

## Derived vs. directly-read values
- `item_text` for items 1-8: directly read (transcribed verbatim) from
  `Measures_Baseline.txt`, not derived or paraphrased.
- `item_text` for items 9-10: directly read (transcribed verbatim) from
  `Codebook_Post.xlsx`'s `Item` column — not derived, but sourced from the codebook
  rather than a participant-facing survey-text PDF since no `Measures_Post.pdf` is
  cached locally (see "Items not extracted from the primary PDF source" below).
- `option_text` (all items): directly read from `Measures_Baseline.txt`'s response
  options shown under items 101-108 ("Less than usual" / "No more than usual" / "More
  than usual" / "Much more than usual"), applied uniformly to items 9-10 as well since
  the codebook confirms all ten items share the same `Measurement level = Ordinal` /
  4-point structure and ground truth's `resp` set (1-4) is identical for every item.
- `item` mapping (`item_N` -> specific paper item): derived/reconstructed from the
  processing script's per-block numeric offsets (see above), not copied literally from
  any single source field, but cross-checked word-for-word against both codebooks.
- `instrument` name (`"Chalder Fatigue Scale"`): inferred from wording/response-format
  match to the published Chalder et al. (1993) scale; not stated verbatim as a citation
  in the source materials (see "Instrument identity" above).
- `resp`/`option_text` scale: directly read from the PDF's 4 response options,
  matching ground truth `resp` values 1-4 exactly.
- `correct_response`: left blank — self-report symptom-frequency scale, no scoring key;
  not derived from any source, this is a structural no-value field.
- `instructions`: left blank (see below) — not derived or fabricated.

## OCR / image-based extraction
Not applicable. `Measures_Baseline.pdf` is a text-based (not scanned/image) PDF; the
already-cached `Measures_Baseline.txt` (`pdftotext -layout` output, produced for the
`_dass` table extraction and reused here) gave clean, directly copy-pasteable text with
no OCR needed for items 1-8. Items 9-10 were read from `Codebook_Post.xlsx`, a native
spreadsheet (`openpyxl`-readable cell text), also not an OCR/image extraction.

## Source type used
Primary (items 1-8): OSF-hosted "Measures" PDF (`Measures_Baseline.pdf` / cached `.txt`
export), a text-native export of the Ethica survey-app screens shown to participants —
the actual participant-facing instrument text (same precedent as `_dass` and
`_procrastination`).
Primary (items 9-10): `Codebook_Post.xlsx`'s `Item` column, used because no
`Measures_Post.pdf`/text export is cached and these two items were only ever asked in
the Post-wave survey, which is not represented in the cached Baseline PDF.
Secondary/corroborating (all items): `Codebook_Baseline.xlsx` / `Codebook_Post.xlsx`,
used to confirm the `item_N` <-> Q# <-> raw-column mapping for each of the five
script blocks (not assumed to reuse any sibling table's offsets) and to cross-check
item wording/order/count across both waves.

## Discrepancy: no standalone `instructions` text found
No standalone whole-instrument instructions/framing text was found anywhere in
`Measures_Baseline.pdf`/`.txt` before the first tiredness item. Item 100(Q#237) is only
a bare section-divider label, "Questionnaire 8", with no participant-facing framing
sentence captured under it. Per the "match the source's terseness" rule and the
"don't fabricate" instruction, `instructions` was left blank (`""`) rather than
reconstructed — same pattern as the sibling `_dass` and `_procrastination` tables.
Logged in `pending_index_notes.csv`.

## Discrepancy: items 9-10 text sourced from codebook, not survey-text PDF
Items 9 and 10 (post-wave-only) could not be transcribed from a participant-facing
survey-text export because no `Measures_Post.pdf`/`.txt` is cached locally (only
`Measures_Baseline.pdf` and `Measures_EMA.pdf` are present in
`.cache/mhscdc_fried_2020_dass/`). Their `item_text` was instead read from
`Codebook_Post.xlsx`'s `Item` column, which for the other eight items matches the
Baseline PDF's wording word-for-word — giving reasonable confidence the codebook's
`Item` text is the literal participant-facing wording rather than a paraphrase, but
this was not independently verified against a survey-text PDF for items 9-10
specifically. Logged in `pending_index_notes.csv`.

## Instrument-name inference note
`instrument` (`"Chalder Fatigue Scale"`) is an inferred identification based on strong
wording/format match, not a citation found verbatim in the cached OSF materials.
Logged in `pending_index_notes.csv` as a lower-confidence field, though it does not
affect the `item`/`resp` validation match.

## Items not extracted from the primary PDF source
Items 9-10 only (see discrepancy note above) — extracted from the codebook instead.
All 10 ground-truth items (`item_1`..`item_10`) have full `item_text` and all four
`option_text`/`resp` pairs populated; no item was left without text.

## Validation result
Manually compared `candidate_mhscdc_fried_2020_tired.rds` against the cached ground
truth `.gt_mhscdc_fried_2020_tired.rds` (per task instructions, did not call
`irw::irw_fetch` directly):
- `unique(item)`: exact match, `item_1`..`item_10` on both sides.
- `unique(resp)`: exact match, values `1,2,3,4` on both sides (`setequal()` initially
  reported FALSE only because ground truth's `resp` is stored as `numeric` and the
  candidate's as `integer`; `identical(sort(unique(gt$resp)), sort(as.numeric(unique(cand$resp))))`
  confirms the underlying values are identical — same benign type-only difference seen
  in the `_procrastination` table).
- Total rows: 40 (10 items x 4 resp), matching the 10x4 fully-crossed structure of the
  ground truth's item/resp sets.

**Result: EXACT match** on item/resp coverage. Two discrepancies logged (blank
`instructions`; items 9-10 sourced from codebook rather than a survey-text PDF) are
provenance/confidence notes, not item/resp mismatches.
