# Extraction log: oxfordcovid_xue_2024_edeq

## has_bare_integer_items
FALSE, and confirmed correct: the ground-truth `item` values (`edeq_1` .. `edeq_12`) are
already semantically-named REDCap field names, not bare integers, so no positional
reconstruction was needed to map `item` -> item text.

## Source type used
PDF (same REDCap "Data Dictionary Codebook" export reused from the already-completed
`oxfordcovid_xue_2024_mfq` extraction — `.cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.pdf`,
46 pages). No new fetch was needed; this PDF documents the entire REDCap project ("Wellbeing
and Resilience during COVID-19"), which includes every instrument in the study including
EDEQ-12, not just the MFQ-26 form. Confirmed via
`grep -n -i "edeq" .cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.txt`, which located
`Instrument: EDEQ-12 (edeq12)` starting at line 5465 (PDF pages 37-39). Re-extracted pages
37-39 with `pdftotext -layout` (rather than relying on the plain-text `.txt` cache) to
confirm the section-header line, table layout, and column association weren't scrambled by
plain extraction.

## What EDE-Q variant this turned out to be
Investigated rather than assumed, per the caution carried over from the MFQ extraction (in
that case "MFQ-26" turned out not to be the standard Mood and Feelings Questionnaire at
all). Here:

- The codebook's REDCap section header reads verbatim **"Instrument: EDEQ-12 (edeq12)"**
  — an explicit **12-item short-form variant** of the Eating Disorder Examination
  Questionnaire, not the standard 28-item EDE-Q (which has 4 subscales scored 0-6 over the
  past 28 days). This is internally consistent with the ground truth: exactly 12 items
  (`edeq_1`..`edeq_12`), exactly 4 response levels (1-4), matching the codebook's own
  4-point per-item response scales — no mismatch between paper-disclosed and live-data
  item/response counts, unlike the `fivpei_perrig_2023_attdiff` precedent flagged in the
  skill docs.
- Structurally, EDEQ-12 splits into two REDCap "Section Header" blocks with genuinely
  different recall windows and response anchors, not a single uniform scale as initially
  guessed from "12 items, 1-4 scale" alone:
  - `edeq_1`-`edeq_10`: section header **"On how many of the past days..."** (verbatim,
    including the trailing ellipsis as displayed in the source — REDCap truncates this
    section-header label at that point across all 10 items in the block), each item asking
    about frequency of an eating/weight-control behavior, scored **1=0 days, 2=1-2 days,
    3=3-5 days, 4=6-7 days**.
  - `edeq_11`-`edeq_12`: section header **"Over the past 7 days..."**, asking about
    weight/shape-related self-judgment and dissatisfaction, scored on a different anchor
    set: **1=not at all, 2=slightly, 3=moderately, 4=markedly**.
  This two-scale structure (10 frequency items + 2 severity items) mirrors the "Restraint"/
  "behavioral" items vs. "Weight/Shape Concern" items split of the standard EDE-Q's item
  content, condensed into a 12-item screening form — consistent with EDEQ-12 being a
  purpose-built short form for this study (item content overlaps standard EDE-Q items
  1-16ish in spirit, e.g. dietary restraint, fear of weight gain, loss-of-control eating,
  compensatory exercise/purging, weight/shape-driven self-evaluation, weight/shape
  dissatisfaction) rather than a verbatim subset of the full 28-item instrument.
- No instrument-wide instructions text (e.g. a generic "answer honestly" preamble) was
  found in the codebook for this form — only the two section headers above, which are
  section-specific (recall-window) prompts, not overall instrument framing. `instructions`
  was therefore left blank rather than fabricated; the two section headers were placed in
  `section_prompt`, scoped to their respective `section_id` groups, per the
  instructions/section_prompt boundary rule (they are recall-window framing specific to a
  subset of items, not whole-table instructions, even though they read a little like
  instructional language).

## OCR / image-based extraction
Same REDCap PDF-export artifact pattern as the MFQ extraction — `pdftotext` (both plain and
`-layout` mode) dropped `fi`/`fl` ligatures. Corrected by hand against context, all within
the EDEQ-12 block (PDF pages 37-39):
- "in uence" -> "influence" (edeq_1, edeq_2)
- "di cult" -> "difficult" (edeq_3, edeq_4)
- "de nite" -> "definite" (edeq_5)
- "burn o " -> "burn off" (edeq_8)
- "dissatis ed" -> "dissatisfied" (edeq_12)
No other OCR ambiguity was present — item boundaries, the `edeq_N` field-name labels, the
section-header lines, and the 1-4 option labels were all unambiguous machine-generated
text (not scanned raster), so no items were left uncertain due to image quality.

## Derived vs. directly-read values
Nothing was derived/inferred beyond the ligature repair above. `item` values, item order,
item wording, the two section-header prompts, and both 1-4 response-option label sets were
all read directly and verbatim from the codebook's per-item REDCap field blocks
(`Instrument: EDEQ-12 (edeq12)` section, fields `edeq_1`..`edeq_12`). `correct_response`
was left blank for all items — this is a clinical symptom-frequency/severity self-report
measure with no scoring key beyond the raw response values. `instrument` is original
composition (not derived/interpolated), built directly from the codebook's literal
`Instrument: EDEQ-12 (edeq12)` label plus context (Oxford ARC COVID-19 study) to make it
human-readable; it does not claim a formal published EDEQ-12 citation, since none was
located — this is a REDCap-internal short-form label for the study, not a named published
instrument. `section_id` values (`oxfordcovid_xue_2024_edeq_days`,
`oxfordcovid_xue_2024_edeq_7days`) are constructed join keys, not source text, matching the
skill's convention of one `section_id` per grouping of items sharing a section prompt.

## Items not extracted
None. All 12 ground-truth items (`edeq_1`..`edeq_12`) were extracted with full item text
and all 4 response-option labels (1-4) each. Validated exact match:
`unique(candidate$item) == unique(irw_fetch ground truth $item)` and
`unique(candidate$resp) == unique(irw_fetch ground truth $resp)` — both TRUE, no
discrepancy to log in `pending_index_notes.csv`.
