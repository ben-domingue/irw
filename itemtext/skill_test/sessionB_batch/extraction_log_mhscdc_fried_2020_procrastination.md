# Extraction log: mhscdc_fried_2020_procrastination

## Source used
Dictionary URL (https://osf.io/mvdpe/) points to the same OSF project used for the
sibling tables `mhscdc_fried_2020_dass` and `mhscdc_fried_2020_anger`: Fried & Epskamp
(2022), "Mental Health and Social Contact During the COVID-19 Pandemic: An Ecological
Momentary Assessment Study." Reused the already-cached OSF "6. Measures" component
files under `.cache/mhscdc_fried_2020_dass/` (no new download needed):
- `Measures_Baseline.pdf` / `Measures_Baseline.txt` (participant-facing survey export,
  Baseline assessment) — primary transcription source.
- `Codebook_Baseline.xlsx`, `Codebook_Post.xlsx` — variable-level codebooks, used to
  confirm the column-name-to-item mapping and cross-check wording/order across waves.

`item_text` and `option_text` were transcribed literally from `Measures_Baseline.txt`
(items 171(Q#223) through 175(Q#227), the block headed by item 170(Q#222) "Questionnaire
15"). Codebook_Baseline.xlsx and Codebook_Post.xlsx were used to confirm the mapping and
cross-check wording, not as the primary transcription source.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` — confirmed. Ground-truth `item`
values are `"item_1"`..`"item_5"` (a named "item_N" convention, not bare integers), but
as with the sibling `_dass` table this is still a **generic** convention reused across
many sibling tables in this study (dass, anger, ps, tired, procrastination, etc.), each
built from a different question range — so the mapping was NOT inferred by
position/range-matching on `item_N`'s own numbering, nor by assuming the same
start-offset as the `_dass` table. It was confirmed directly from
`data/mhscdc_fried_2020.r` (this repo's own processing script for this dataset), which
shows the procrastination-specific call:
```r
dass_pre  <- process_dass_data2(bt_df, "Pre",  141, 145, "pre",  140)
dass_post <- process_dass_data2(bt_df, "Post", 13, 17, "post", 12)
```
i.e. `item = paste0("item_", as.integer(str_extract(item_rawname, "\\d+")) - item_offset)`.
For `wave="pre"`: raw columns `Pre141`..`Pre145` map to `item_1`..`item_5` (offset 140,
since 141-140=1, ..., 145-140=5). For `wave="post"`: raw columns `Post13`..`Post17` map
to `item_1`..`item_5` (offset 12, since 13-12=1, ..., 17-12=5). This offset is different
from the `_dass` table's offsets (0 / 37) and from `_anger`'s raw-column convention —
confirmed by reading the script's procrastination-specific `process_dass_data2()` calls
directly rather than assuming the `_dass` table's pattern carried over unchanged.

This was then cross-checked against the codebooks' own `cleandata_pre` / `clean_post`
column labels: `Codebook_Baseline.xlsx` rows with `cleandata_pre` = `Q141`..`Q145`
(spreadsheet rows 162-166) are labeled `Label/Scale = "Procrastination"` (on the first of
the five rows) and contain, in order, the 5 item texts below; `Codebook_Post.xlsx` rows
with `clean_post` = `Q13`..`Q17` (spreadsheet rows 22-26) contain the identical 5 item
texts in the identical order (labeled `Label/Scale = "Specifc questions 1"` on the first
row — a generic/typo'd label, but the item text itself matches the Baseline block
word-for-word). Both codebook blocks and the `Measures_Baseline.txt` PDF export agree on
item order and wording, so `item_1` = the first item in that 5-item block ("I usually buy
even essential item at the last minute."), ..., `item_5` = the fifth ("I do not do
assignments until just before they are to be handed in."), for both waves.

## Instrument identity
The 5-item block is labeled `"Procrastination"` in `Codebook_Baseline.xlsx`. No
standalone published-instrument title (e.g. author/year citation) was found in the OSF
measures/codebook materials for this specific 5-item block — the survey export only shows
the bare section heading "Questionnaire 15". The item wording ("I usually buy even
essential item[s] at the last minute," "I generally delay before starting on work I have
to do," "I do not do assignments until just before they are to be handed in," etc.)
strongly resembles items from Lay's (1986) General Procrastination Scale, but since no
citation to that specific instrument was found in the source materials, `instrument` was
recorded as the codebook's own literal label, `"Procrastination Scale"`, rather than
asserting a specific published-instrument name/citation that isn't stated in the source.

## Derived vs. directly-read values
- `item_text`, `option_text`: directly read (transcribed verbatim) from
  `Measures_Baseline.txt` (pdftotext export of `Measures_Baseline.pdf`), not derived or
  paraphrased.
- `item` values (`item_1`..`item_5`): directly matched against ground truth; the
  *mapping* from `item_N` to a specific paper item is a derived/reconstructed value (see
  above), based on the processing script's numeric offset logic (specific to this
  measure, not copied from the `_dass` table) plus corroborating codebook cross-check —
  not a literal field copied from one source.
- `instrument` name (`"Procrastination Scale"`): directly read from the codebook's
  `Label/Scale` column value, not fabricated; not asserted to be a specific named
  published instrument beyond what the source states (see "Instrument identity" above).
- `resp`/`option_text` scale: directly read from the PDF's 5 response options
  (1-5), matching ground truth `resp` values 1-5 exactly.
- `correct_response`: left blank — this is a self-report characterological scale with no
  scoring key/correct answer; not derived from any source, this is a structural no-value
  field.
- `instructions`: left blank (see below) — not derived or fabricated.

## OCR / image-based extraction
Not applicable. `Measures_Baseline.pdf` is a text-based (not scanned/image) PDF; the
already-cached `Measures_Baseline.txt` (`pdftotext -layout` output, produced for the
`_dass` table extraction and reused here) gave clean, directly copy-pasteable text with
no OCR needed. All 5 item stems and all 5 response-option strings were extracted this
way and spot-checked by eye against the raw text (lines 1067-1102 of
`Measures_Baseline.txt`).

## Source type used
Primary: OSF-hosted "Measures" PDF (`Measures_Baseline.pdf` / cached `.txt` export), a
text-native export of the Ethica survey-app screens shown to participants — this is the
actual participant-facing instrument text, preferred over the codebook for
`item_text`/`option_text` transcription (same precedent as the `_dass` table).
Secondary/corroborating: `Codebook_Baseline.xlsx` / `Codebook_Post.xlsx`, used only to
(a) confirm the `item_N` <-> Q# <-> raw-column mapping for this specific measure (not
assumed to reuse the `_dass` table's offsets) and (b) cross-check the item-count/order (5
items, `Label/Scale = "Procrastination"`) across both waves.

## Discrepancy: no standalone `instructions` text found
No standalone whole-instrument instructions/framing text was found anywhere in
`Measures_Baseline.pdf`/`.txt` before the first procrastination item. Item 170(Q#222) is
only a bare section-divider label, "Questionnaire 15", with no participant-facing framing
sentence captured under it. Per the "match the source's terseness" rule and the "don't
fabricate" instruction, `instructions` was left blank (`""`) rather than reconstructed —
same pattern and same rationale as the sibling `_dass` table. Logged in
`pending_index_notes.csv`.

## Minor wording note (not treated as a mismatch)
`Codebook_Post.xlsx`'s row for the first item reads "I usually buy even **an** essential
item at the last minute" (with "an"), while both `Measures_Baseline.txt` and
`Codebook_Baseline.xlsx` consistently read "I usually buy even essential item at the last
minute" (no "an" — likely a source typo/omission, reproduced as-is rather than corrected).
Used the Baseline PDF wording (what participants actually saw at Baseline, and the
majority-consistent version across sources) as the literal source of record for
`item_text`.

## Items not extracted
None — all 5 ground-truth items (`item_1`..`item_5`) were extracted with full `item_text`
and all 5 `option_text`/`resp` pairs.

## Validation result
Manually compared `candidate_mhscdc_fried_2020_procrastination.rds` against the cached
ground truth `.gt_mhscdc_fried_2020_procrastination.rds` (per task instructions, did not
call `irw::irw_fetch` directly):
- `unique(item)`: exact match, `item_1`..`item_5` on both sides.
- `unique(resp)`: exact match, values `1,2,3,4,5` on both sides (a `setequal()` check
  initially reported FALSE only because ground truth's `resp` is stored as `numeric` and
  the candidate's as `integer`; `identical(sort(unique(gt$resp)), sort(as.numeric(unique(cand$resp))))`
  confirms the underlying values are identical).
- Total rows: 25 (5 items x 5 resp), matching the 5x5 fully-crossed structure of the
  ground truth's item/resp sets.

**Result: EXACT match**, no discrepancy to log for item/resp coverage. The only
discrepancy noted above (blank `instructions`) is the same structural non-fabrication
choice made for the sibling `_dass` table, not an item/resp mismatch.
