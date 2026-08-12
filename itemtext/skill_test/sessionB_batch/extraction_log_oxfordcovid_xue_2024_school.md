# Extraction log: oxfordcovid_xue_2024_school

## has_bare_integer_items
FALSE, and confirmed correct: the ground-truth `item` values (`school_1`, `school_2`,
`school_pos_neg_1`..`school_pos_neg_11`, `school_stress`, `school_support_1`..`school_support_5`)
are already semantically-named REDCap field names, not bare integers, so no positional
reconstruction was needed to map `item` -> item text.

## Source type used
PDF (same REDCap "Data Dictionary Codebook" export reused from the already-completed
`oxfordcovid_xue_2024_mfq` extraction — `.cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.pdf`
/ `.txt`, 46 pages, "Wellbeing and Resilience during COVID-19" REDCap project). No new fetch
was needed. `grep -n -i school .cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.txt` located
all 19 target fields at lines 4071-4506 (PDF pages 27-29), inside REDCap's `Instrument: covid
(covid)` form — a general COVID-context form, not a form named after "school". Read the
surrounding block directly from the plain-text extraction (field boundaries, radio/dropdown
option lists, and "Section Header:" lines were unambiguous machine-generated text at this
location, so no `-layout` re-extraction was needed here, unlike the EDEQ block).

## What the 4 sub-blocks turned out to be
Investigated each block separately per the task instructions rather than assuming a single
uniform 0-7 scale. All four are drawn from the same REDCap "covid" instrument/form but are
visually and functionally distinct question groups, each with its own response scale:

1. **`school_1`, `school_2`** — two standalone school-status items, no shared "Section
   Header" text tying them together (each is its own free-standing radio/dropdown field).
   - `school_1` ("Is your school currently:"): `radio`, 3 options — 1=open, 2=closed,
     3=on a holiday break. Matches ground truth (`resp` in {1,2,3}).
   - `school_2` ("How many days a week are you in school?"): `dropdown`, options 0-7 (the
     option text is literally the numeral, i.e. number of days). Ground truth only exercises
     a subset of that range ({0,1,2,4,5,7} — no respondent reported 3 or 6 days), which is
     expected sampling variation, not a scale mismatch — the full 0-7 codebook range is
     still the correct `option_text`/`resp` mapping to emit.
   - Grouped under one placeholder `section_id`
     (`oxfordcovid_xue_2024_school_general`) with blank `section_prompt` since no shared
     header text exists to record, per the skill's "no real testlet grouping -> still emit a
     section_id, blank prompt" rule.

2. **`school_support_1`..`school_support_5`** — a 5-item `radio (Matrix)` block under
   **`Section Header: Do you think your school is taking enough measures to:`** (verbatim).
   Each item is a short measure-specific completion of that stem (e.g. "Support students'
   mental health?", "Wear masks?"). All 5 share the same 3-point scale: 1=no, 2=yes,
   3=not applicable. Matches ground truth (`resp` in {1,2,3} for all 5 items).
   `section_id = oxfordcovid_xue_2024_school_support`; the section header text was placed in
   `section_prompt` (scoped to just these 5 items), not `instructions`, since it is specific
   to this sub-block, not the whole table.

3. **`school_stress`** — a single standalone item, no section header:
   "How stressful are you finding school and/or home schooling compared to this time last
   year?" (`nding` -> `finding`, ligature-stripped by `pdftotext`; see OCR section below).
   5-point scale, its own distinct anchor set: 1=much more stressful, 2=somewhat more
   stressful, 3=equally stressful, 4=somewhat less stressful, 5=much less stressful. Matches
   ground truth (`resp` in {1,2,3,4,5}) — this is the one sub-block confirmed to NOT use the
   0-7 range at all. `section_id = oxfordcovid_xue_2024_school_stress`, blank `section_prompt`
   (single item, no header text to record).

4. **`school_pos_neg_1`..`school_pos_neg_11`** — an 11-item `radio (Matrix)` block under
   **`Section Header: Please rate how positive (helpful) or negative (harmful) you have found
   the following, relating to your school experience in the past week`** (verbatim). Each item
   is a short topic label (e.g. "School in general", "Getting grades", "Cases of COVID-19 at
   your school"). All 11 share the same 8-point 0-7 scale: 0=Not applicable, 1=Very negative,
   2=Quite negative, 3=A bit negative, 4=Neither negative nor positive, 5=A bit positive,
   6=Quite positive, 7=Very positive. This is the sub-block that supplies the full 0-7 range
   seen in the task's "N resp = 8" summary — it is NOT shared by the other three blocks.
   Matches ground truth (`resp` in {0..7} for all 11 items). `section_id =
   oxfordcovid_xue_2024_school_posneg`; section header placed in `section_prompt`.

No text was found anywhere in the "covid" instrument that reads as whole-table framing
covering all four of these sub-blocks together (they're clearly separate question groups
sharing only the same REDCap form), so the merged `instructions` column is blank for every
row rather than fabricated — consistent with the `oxfordcovid_xue_2024_edeq` precedent of
leaving `instructions` blank when only section-specific headers exist.

## OCR / image-based extraction
Same REDCap PDF-export artifact pattern as the MFQ/EDEQ extractions — `pdftotext` dropped
`fi`/`fl` ligatures and the literal word "field" throughout the surrounding REDCap boilerplate
("Show the [field] ONLY if..."). Within the actual item/section text used in this extraction,
only one ligature correction was needed:
- "you are nding school" -> "you are finding school" (`school_stress` item text).
No other OCR ambiguity was present in this block — item boundaries, the `school_*`/
`school_support_*`/`school_pos_neg_*` field-name labels, the "Section Header:" lines, and all
option-list text were unambiguous machine-generated text (not scanned raster), so no items
were left uncertain due to image quality. One cosmetic normalization (not a correction of
misread characters): `school_pos_neg_10`'s option label "Taking/ Retaking exams" had a stray
space after the slash in the raw extraction, normalized to "Taking/Retaking exams".

## Derived vs. directly-read values
- `item`, item wording, item order, the two section-header prompts (`school_support`,
  `school_pos_neg`), and all option-label sets (school_1's 3 options, school_2's 0-7 day
  count, school_support's 3-point no/yes/n-a, school_stress's 5-point scale, school_pos_neg's
  8-point scale) were all read directly and verbatim (modulo the one ligature fix above) from
  the codebook's per-item REDCap field blocks in the `Instrument: covid (covid)` section.
- `correct_response` was left blank for all 19 items — none of these are scored/keyed items
  (self-report status/experience/attitude items).
- `instrument` is original composition (not derived/interpolated): built from the codebook's
  literal `Instrument: covid (covid)` label plus the specific field names in scope, since
  there is no separately-named published "school" instrument here (unlike MFQ-26/EDEQ-12,
  this is simply a block of study-specific COVID/school-context items within the general
  "covid" REDCap form, not a validated scale with its own title).
- `section_id` values (`oxfordcovid_xue_2024_school_general`,
  `oxfordcovid_xue_2024_school_support`, `oxfordcovid_xue_2024_school_stress`,
  `oxfordcovid_xue_2024_school_posneg`) are constructed join keys reflecting the 4 sub-blocks
  identified above, not source text.

## Items not extracted
None. All 19 ground-truth items were extracted with full item text and full response-option
sets. Validated exact match: `unique(candidate$item) == unique(irw_fetch ground truth $item)`
TRUE, and `unique(candidate$resp) == unique(irw_fetch ground truth $resp)` TRUE (integer-typed
to match; both resolve to the same 8-element set {0..7} once type is aligned). Per-item
response-value coverage was also checked individually (not just the merged union): every
ground-truth `resp` value observed for each of the 19 items is present among that item's
candidate `option_text`/`resp` rows — no discrepancy to log in `pending_index_notes.csv`.
