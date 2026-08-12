# Extraction log: mhscdc_fried_2020_dass

## Source used
Dictionary URL (https://osf.io/mvdpe/) points to the OSF project for Fried & Epskamp
(2022), "Mental Health and Social Contact During the COVID-19 Pandemic: An Ecological
Momentary Assessment Study." The OSF project's "6. Measures" component
(node id `5ea1b1ee9fd59800f956831b`) contains six files; downloaded and cached under
`.cache/mhscdc_fried_2020_dass/`:
- `Measures_Baseline.pdf` (participant-facing survey export, Baseline assessment)
- `Measures_Post.pdf` (participant-facing survey export, Post assessment)
- `Codebook_Baseline.xlsx`, `Codebook_Post.xlsx`, `Codebook_EMA.xlsx` (variable-level
  codebooks mapping raw/clean column names to item text and response labels)
- `Measures_EMA.pdf` (checked and ruled out — see "Ambiguities" below)

`item_text` and `option_text` were transcribed literally from `Measures_Baseline.pdf`
(items 17(Q#25) through 37(Q#45), the block headed by item 16(Q#23) "Questionnaire 1").
`Codebook_Baseline.xlsx` and `Codebook_Post.xlsx` were used to confirm column-name-to-item
mapping and cross-check wording, not as the primary transcription source (see "OCR /
image-based extraction" below for why the PDF was preferred).

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` — confirmed. Ground-truth `item`
values are `"item_1"`..`"item_21"` (a named "item_N" convention, not bare integers), but
this is still a **generic** convention that says nothing on its face about which specific
paper item each `item_N` refers to, since the same "item_N" pattern is reused across
sibling tables in this study for entirely different scales (anger, procrastination, ps,
tired, etc., each built from a different question range). The mapping was NOT inferred by
position/range-matching on `item_N`'s own numbering — it was confirmed directly from
`data/mhscdc_fried_2020.r` (this repo's own processing script for this dataset), which
shows:
```r
dass_pre  <- process_dass_data2(bt_df, "Pre",  1, 21, "pre",  0)
dass_post <- process_dass_data2(bt_df, "Post", 38, 58, "post", 37)
```
i.e. `item = paste0("item_", as.integer(str_extract(item_rawname, "\\d+")) - item_offset)`.
For `wave="pre"`: raw columns `Pre1`..`Pre21` map to `item_1`..`item_21` (offset 0). For
`wave="post"`: raw columns `Post38`..`Post58` map to `item_1`..`item_21` (offset 37, since
38-37=1, 58-37=21). This was then cross-checked against the codebooks' own `cleandata_pre`
/ `clean_post` column labels (`Q1`..`Q21` at Baseline codebook rows 22-42, `Q38`..`Q58` at
Post codebook rows 47-67), both of which are explicitly labeled `Label/Scale = "DASS"` (row
22 of Codebook_Baseline.xlsx) and both of which contain, in identical order, item text
matching the official published DASS-21 item sequence (verified against the well-known
public DASS-21 instrument: "hard to wind down" / "dryness of my mouth" / "couldn't
experience any positive feeling" / ... / "life was meaningless", items 1-21 in that exact
canonical order in both the Baseline and Post codebook blocks). So `item_1` = DASS-21
official item 1, ..., `item_21` = DASS-21 official item 21, for both waves.

## Derived vs. directly-read values
- `item_text`, `option_text`: directly read (transcribed verbatim) from
  `Measures_Baseline.pdf`, not derived or paraphrased.
- `item` values (`item_1`..`item_21`): directly matched against ground truth; the
  *mapping* from `item_N` to a specific DASS-21 item is a derived/reconstructed value
  (see above), based on the processing script's numeric offset logic plus corroborating
  codebook cross-check — not a literal field copied from one source.
- `instrument` name ("Depression Anxiety Stress Scales - 21 Item (DASS-21)"): derived —
  not stated verbatim as a title anywhere in the OSF measures documents (the survey
  export only labels it "Questionnaire 1"), but confirmed as the correct instrument
  identity by exact item-text match against the well-known published DASS-21.
- `resp`/`option_text` scale: directly read from the PDF's 4 response options
  (1-4), matching ground truth `resp` values 1-4 exactly.
- `correct_response`: left blank — DASS-21 is a self-report symptom-severity scale with
  no scoring key/correct answer; not derived from any source, this is a structural
  no-value field.
- `instructions`: left blank (see below) — not derived or fabricated.

## OCR / image-based extraction
Not applicable. `Measures_Baseline.pdf` is a text-based (not scanned/image) PDF; `pdftotext
-layout` extracted clean, directly copy-pasteable text with no OCR needed. All 21 item
stems and all 4 response-option strings were extracted this way, and spot-checked by eye
against the raw `pdftotext` output for line-wrap artifacts (a few items wrap across two
lines in the PDF layout, e.g. item 20/25/30/35, but the wrapped text was reassembled
without alteration).

## Source type used
Primary: OSF-hosted "Measures" PDF (`Measures_Baseline.pdf`), a text-native export of the
Ethica survey-app screens shown to participants — this is the actual participant-facing
instrument text, preferred over the codebook for `item_text`/`option_text` transcription.
Secondary/corroborating: `Codebook_Baseline.xlsx` / `Codebook_Post.xlsx` (variable
codebooks), used only to (a) confirm the `item_N` <-> Q# <-> raw-column mapping and (b)
cross-check the item-count/order (21 items, `Label/Scale = "DASS"`). Also checked and
ruled out: `Measures_EMA.pdf` / `Codebook_EMA.xlsx` — the EMA (momentary, repeated many
times/day) battery uses a *different*, 5-point ("Not at all".."Extremely") single-item
per construct (Stress/Anxiety/Depression/Fatigue/...) design with only 18 items total, not
a 21-item 4-point DASS-21, and is a separate IRW table in this study
(`mhscdc_fried_2020_ema`) — not the source for this `_dass` table. The `_dass` table's
4-point 1-4 scale and 21-item count on both `pre` and `post` waves match only the
Baseline/Post "Questionnaire 1" block.

## Discrepancy: no standalone `instructions` text found
No standalone whole-instrument instructions/framing text was found anywhere in
`Measures_Baseline.pdf` or `Measures_Post.pdf` before the first DASS item. Item 16(Q#23)
/ item 38(Q#38 equivalent) is only a bare section-divider label, "Questionnaire 1", with
no participant-facing framing sentence captured under it — each item stem instead repeats
its own time-frame reminder ("In the past week, I ..."). Per the "match the source's
terseness" rule and the "don't fabricate" instruction, `instructions` was left blank
(`""`) rather than reconstructed from the well-known published DASS-21 standard
instructions ("Please read each statement and select a number 0, 1, 2, or 3 which
indicates how much the statement applied to you over the past week...") — that text is
not present in the actual source materials for this dataset. Logged in
`pending_index_notes.csv`.

## Minor wording discrepancy noted (not treated as a mismatch)
`Codebook_Baseline.xlsx`'s row 22 gives response option 3 as "Applied to me to a
considerable degree, or a good part **of the time**", while the participant-facing
`Measures_Baseline.pdf` consistently (all 21 occurrences) reads "... a good part **of
time**" (no "the"). Used the PDF wording (what participants actually saw) as the literal
source of record for `option_text`; noting the codebook's minor variant here in case it
matters for downstream comparison to the canonical published DASS-21 wording (which uses
"of the time").

## Items not extracted
None — all 21 ground-truth items (`item_1`..`item_21`) were extracted with full
`item_text` and all 4 `option_text`/`resp` pairs. Validated: `unique(item)` and
`unique(resp)` of `candidate_mhscdc_fried_2020_dass.rds` match
`.gt_mhscdc_fried_2020_dass.rds` exactly (21 items, resp 1-4, 84 total item x resp rows).
