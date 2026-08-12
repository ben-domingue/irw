# Extraction log: eammi_grahe_2018_socmedia

## Source used
Reused the cached EAMMi2 first-party materials from `.cache/eammi_grahe_2018_moa1/`
(same OSF project, https://osf.io/qtqpb/overview, no refetch needed):

- `EAMMi2-Data1.2-Codebook.xlsx` — project's own data dictionary (Variable Name /
  Question text / instructions / responses / Survey Question ID), read with `openpyxl`.
- `EAMMI2_Survey_withcodes.txt` (pdftotext -layout export of
  `EAMMI2_Survey_withcodes.pdf`) — the literal Qualtrics matrix-question layout as
  presented to respondents.

Both sources agree exactly on the 11 real `SocMedia_*` items and independently confirm
the response scale, so this is a high-confidence, literally-sourced extraction for those
items.

## Structure discovered
Ground truth items: `SocMedia_1`..`SocMedia_11` (11 real items) plus
`SocMedia_bias_dummy` (12th item), resp 1-5 overall.

The survey PDF (line ~660 of `EAMMI2_Survey_withcodes.txt`) shows a single Qualtrics
matrix question, stem: "Think of the social media platform (e.g., Facebook, Instagram,
Twitter, etc.) you use most often. How often do you use it for the following reasons?"
with 11 row items and one shared 5-point column scale: Never (1), Rarely (2), Sometimes
(3), Often (4), A lot (5). The codebook's `responses` column for each `SocMedia_1`..`_11`
row independently confirms "1-never, 5 a lot", and the 11 row labels match the PDF's row
items one-to-one and in the same order as the `SocMedia_1..11` numbering. `item` values
were already semantic/matching the codebook variable names directly (per
`has_bare_integer_items: FALSE`), so no positional-reconstruction judgment call was
needed for the 11 real items.

### SocMedia_bias_dummy — investigated per instructions
The codebook (`EAMMi2-Data1.2-Codebook.xlsx`) has an explicit row for this variable:

> `SocMedia_bias_dummy | response bias coded, 1 = all same answer | n/a | computed | ADDED`

This is one of a whole family of `*_bias_dummy` computed variables in the codebook (one
per scale block: `MOA_IMP_dummy`, `IDEA-bias-dummy`, `mindful_bias_dummy`,
`belong_bias_dummy`, `efficacy_bias_dummy`, `support_bias_dummy`, `NPI_bias_dummy`,
`phys_sym_bias_dummy`, `stress_bias_dummy`, plus a `SocMedia_biascheck` sum column) —
confirming this is the EAMMi2 team's standard straight-lining/careless-response QC flag,
computed after the fact from the 11 `SocMedia_*` items, **not an administered survey
question** with its own stem/response options. It has no row in the survey PDF because
participants were never shown it.

Cross-checked against this table's ground truth (`.gt_eammi_grahe_2018_socmedia.rds`):
`SocMedia_bias_dummy` appears for only 140 of ~3178 respondents, and **every one of those
140 rows has `resp == 1`** — consistent with the codebook's "1 = all same answer" coding
(only respondents who tripped the flag, or only the flag's "true" state, made it into the
long-format IRW extract; there is no `resp == 0` in this table for this item). This
confirms it is a derived QC indicator, not a Likert item, and its single `resp` value
(1) means "flagged as a straight-liner across the SocMedia block," not a normal Likert
scale point.

## Structure of output
`instrument` = "Social Media Use Motives (SocMedia)" — descriptive label built from the
codebook's own variable-block prefix (`SocMedia`); the EAMMi2 materials don't cite this
block as a separately-named published scale, so no formal citation name was invented.

`instructions` left blank for every row — nothing in the source applies unconditionally
to the whole table (the shared stem below applies only to the 11 real items, not to the
derived dummy), so nothing was force-fit into `instructions` just to have content there.

Two sections:
- `eammi_grahe_2018_socmedia_1` (the 11 real `SocMedia_1..11` items) — `section_prompt` =
  literal stem, "Think of the social media platform (e.g., Facebook, Instagram, Twitter,
  etc.) you use most often. How often do you use it for the following reasons?"
  `item_text` = literal row label for each item (e.g. "Avoid drifting apart from the
  people I know"). `option_text`/`resp`: Never=1, Rarely=2, Sometimes=3, Often=4, A lot=5
  (literal anchor labels from both the PDF and codebook, in the codebook's stated
  ascending order).
- `eammi_grahe_2018_socmedia_bias` (`SocMedia_bias_dummy`) — `section_prompt` blank (no
  participant-facing prompt exists). `item_text` honestly describes it as a derived,
  non-administered response-bias flag rather than treating it like a normal item. Single
  `option_text`/`resp` row: "Flagged as response bias (identical rating given to all
  SocMedia items)" / `resp = 1`, matching the only value present for this item in the
  live ground truth.

`correct_response` blank throughout — self-report frequency-of-use scale, no scoring key.

## OCR / image-based extraction
None. `EAMMI2_Survey_withcodes.pdf` is a native, text-layer Qualtrics print-export PDF,
extracted with `pdftotext -layout` (cached as `EAMMI2_Survey_withcodes.txt`) — not a
scan/image, no OCR used or needed. The codebook is a native `.xlsx` read directly.

## Derived vs. directly-read values
- The 11 real items' `item_text` and `option_text` are transcribed verbatim from the
  survey PDF's matrix layout and independently corroborated word-for-word by the
  codebook's `responses`/`Question text` columns.
- `SocMedia_bias_dummy`'s `item_text` is **not** a literal transcription of a
  participant-facing prompt (none exists) — it is a factual description of what the
  codebook says the computed variable represents ("response bias coded, 1 = all same
  answer"), written in explicit "derived indicator" language rather than presented as if
  it were an ordinary Likert item. Its single `resp = 1` value was confirmed against the
  live ground truth data (all 140 non-missing rows for this item are `resp == 1`), not
  guessed.
- `section_id` values are a light structural choice (splitting the 11 administered items
  from the 1 derived flag) but every text field within each section is either a literal
  quote or an explicit, labeled paraphrase of the codebook's own description — no
  fabricated content.

## Source type used
Primary: original data-collector's own OSF-hosted survey instrument PDF
(`EAMMI2_Survey_withcodes.pdf`) and data dictionary (`EAMMi2-Data1.2-Codebook.xlsx`),
both first-party materials from the dataset's own OSF repository — not the published
paper, not a secondary/paraphrased description. `has_bare_integer_items` is FALSE for
this table (items already have semantic labels, e.g. `SocMedia_1`), confirmed true
throughout — no bare-integer reconstruction/ordering judgment call was needed for the 11
real items. `SocMedia_bias_dummy` required an additional codebook cross-check (its
"computed" origin) rather than a survey-PDF lookup, since it isn't in the survey PDF at
all.

## Items not extracted
None — all 12 ground-truth items (`SocMedia_1`..`SocMedia_11`, `SocMedia_bias_dummy`)
were extracted, the 11 real items with full literal `item_text`/`option_text`, and the
derived `SocMedia_bias_dummy` with an honest derived-flag description instead of
fabricated Likert-item text.

## Validation
`unique(candidate$item)` and `unique(candidate$resp)` match
`readRDS(".gt_eammi_grahe_2018_socmedia.rds")` exactly (`setequal()` checks both TRUE in
`build_eammi_grahe_2018_socmedia.R`) — **exact match**, no discrepancy to log in
`pending_index_notes.csv`.
