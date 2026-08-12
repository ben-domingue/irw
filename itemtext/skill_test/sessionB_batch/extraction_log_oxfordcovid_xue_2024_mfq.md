# Extraction log: oxfordcovid_xue_2024_mfq

## has_bare_integer_items
FALSE, and confirmed correct: the ground-truth `item` values (`mfq_26_1` ... `mfq_26_20`)
are already semantically-named REDCap field names, not bare integers, so no
positional reconstruction was needed to map `item` -> item text.

## Source type used
PDF (scanned/exported REDCap "Data Dictionary Codebook" — a machine-generated PDF
export of REDCap's online codebook viewer, not an OCR'd scan of a printed page, but
`pdftotext` extraction still produced the ligature-stripping artifacts described below,
which is why this is logged under "OCR / image-based extraction" too).

## What "mfq_26" turned out to mean
Investigated rather than assumed. The dictionary row's URL (https://osf.io/4b85w/,
Parsons et al. 2022 "Oxford ARC study" OSF project) hosts the companion data-paper
materials for the Oxford Achieving Resilience during COVID-19 (ARC) study. Confirmed
via the study's data-paper (Parsons et al., "Data and Protocol for the Oxford
Achieving Resilience During COVID-19 (ARC) Study," Journal of Open Psychology Data,
https://openpsychologydata.metajnl.com/articles/10.5334/jopd.56) and the OSF-hosted
`data paper/codebooks/raw_data_codebook.pdf` (cached at
`.cache/oxfordcovid_xue_2024_mfq/raw_data_codebook.pdf`, text-extracted to
`raw_data_codebook.txt`):

- "MFQ" = **Mental Flexibility Questionnaire**, a trait-level measure of psychological
  flexibility developed in-house by the Oxford ARC study team (Parsons et al.) — **not**
  the Mood and Feelings Questionnaire (the far more common "MFQ" in adolescent-mental-
  health research) and **not** the Cognitive Flexibility Inventory (Dennis & Vander Wal).
  The data-paper explicitly states "The Mental Flexibility Questionnaire (MFQ) was
  developed by our group to index psychological flexibility" and reports baseline
  reliability (Cronbach's alpha 0.88 young persons / 0.91 parents).
- The codebook's REDCap section header reads verbatim **"Instrument: MFQ-26 (mfq26)"**.
  "26" is REDCap's internal instrument/form label suffix, not an item count and not a
  26-item variant of the instrument — the form itself contains exactly 20 items
  (`mfq_26_1` .. `mfq_26_20`, field names inherited from the REDCap instrument label
  `mfq26`). This resolves the task's flagged ambiguity: "26" is a naming artifact of the
  REDCap form, unrelated to the 33-item/13-item standard-MFQ conventions that don't apply
  here since this isn't the Mood and Feelings Questionnaire at all.
- The unusual 6-point 1-6 "Strongly Disagree" ... "Strongly Agree" scale (rather than the
  0-2/1-3 scale typical of the Mood and Feelings Questionnaire) is consistent with this
  being a distinct, differently-constructed trait-agreement instrument, not a data-entry
  anomaly on a standard MFQ.

## Structure discovered
Single unified 20-item instrument, no testlets/shared passages, so one `section_id`
(`oxfordcovid_xue_2024_mfq_1`) covers all 20 items with a blank `section_prompt`, per the
skill's rule for instruments without sub-groupings. `instructions` (applies instrument-
wide) is the codebook's literal REDCap "Section Header" text: "Please rate the degree to
which you agree or disagree with each of the questions on the scale below. Think
carefully about each question and answer them honestly." All 20 items share the same
6-point response scale (1=Strongly Disagree ... 6=Strongly Agree), transcribed verbatim
from the codebook's per-item radio-matrix option list.

## OCR / image-based extraction
The codebook is a PDF (REDCap's codebook-viewer export), and `pdftotext` extraction
dropped several `fi`/`fl` ligatures, producing artifacts that were corrected by hand
against surrounding context before use:
- "di erent" -> "different" (items 3, 8, 12, 14)
- "con dent" -> "confident" (item 5)
- "nd" -> "find" (items 7, 8 "to nd a solution", 11 "I nd it exciting")
- "di culties" -> "difficulties" (item 8)
No other OCR ambiguity was present — item boundaries and the mfq_26_N field-name labels
were unambiguous machine-generated text (not scanned raster), so no items were left
uncertain due to image quality.

## Derived vs. directly-read values
Nothing was derived/inferred beyond the ligature repair above. `item` values, item order,
item wording, and the 1-6 response-option labels were all read directly and verbatim from
the codebook's per-item REDCap field blocks (`Instrument: MFQ-26 (mfq26)` section,
fields `mfq_26_1`..`mfq_26_20`). `correct_response` was left blank for all items — this is
a trait self-report personality/flexibility measure with no scoring key. `instrument` and
`instructions` fields are original composition/transcription (not derived/interpolated
values), built directly from the codebook's literal section header and the data-paper's
description of what the instrument is.

## Items not extracted
None. All 20 ground-truth items (`mfq_26_1`..`mfq_26_20`) were extracted with full
item text and all 6 response-option labels (1-6). Validated exact match:
`unique(candidate$item) == unique(irw_fetch ground truth $item)` and
`unique(candidate$resp) == unique(irw_fetch ground truth $resp)` — both TRUE, no
discrepancy to log in `pending_index_notes.csv`.
