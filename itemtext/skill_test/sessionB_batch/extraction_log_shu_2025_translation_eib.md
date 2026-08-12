# Extraction log: shu_2025_translation_eib

## Source type used
PLOS ONE main article (fully open access, https://doi.org/10.1371/journal.pone.0318101,
also PMC11774393) plus its own **Supporting Information file S1 File ("Full version of
the questionnaire")**, downloaded directly from PLOS's supplementary-file endpoint
(`https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0318101.s002&type=supplementary`)
and cached as a native `.docx` at `.cache/shu_2025_translation_eib/s002.bin`. This is a
literal transcript source, not OCR — the docx's paragraph text was read directly with
Python's `python-docx`, no image/PDF-scan step involved. (Note: `.s001` at that same
endpoint is PLOS's boilerplate "Inclusivity in global research" checklist, not the
questionnaire — had to check `.s002` through `.s006` to find the right file; `.s003`-`.s006`
are supplementary figures/tables, not the questionnaire.)

The Figshare record at the URL in the dictionary row (28136309) is the raw response-level
dataset (same content as `irw::irw_fetch`, not additional item-text metadata) — checked
its listing but the questionnaire text itself came from the PLOS S1 File, not Figshare.

## OCR / image-based extraction
None used. The S1 File is a native Word document (not a scanned image/PDF), so all item
text below is a direct copy-paste from the docx's paragraph runs — no OCR, no
transcription-by-eye from a screenshot.

## What "eib"/"pishp" and the 172-232 numbering scheme mean
Confirmed (not merely the batch prompt's hypothesis) via the S1 File and cross-checked
against the original PISHSP validation paper (Cheng et al., PMC7712674):

- The paper's questionnaire has 4 parts: Part 1 Demographics, Part 2 the translated
  **MCPIS-9** (9 items, the paper's main scale-under-validation), Part 3 the
  **Professional Identity Scale for Healthcare Students and Professionals (PISHSP)**
  (used as a concurrent/convergent-validity criterion measure, per the main text: "the
  correlation between the total scores of the MCPIS-9 and the PISHSP was tested"), and
  Part 4 additional open-ended questions.
- PISHSP itself has 4 named subscales, listed in the S1 File in this order: "Professional
  Commitment & Devotion" (16 items), **"Emotional Identification & Belongingness" (7
  items)**, "Professional Goals & Values" (5 items), "Self-fulfilment & Retention
  Tendency" (5 items) — 33 items total, matching the original PISHSP development paper's
  factor structure.
- So `eib` = **E**motional **I**dentification & **B**elongingness (the PISHSP subscale
  name), and `pishp` = the PISHSP instrument code. This table is **not** the MCPIS-9 (the
  scale the paper is translating/validating) — it's the *criterion* instrument's EIB
  subscale, used alongside it in the same combined questionnaire. `has_bare_integer_items`
  is correctly marked FALSE: items already carry this semantic `eib_pishp###` code, not
  bare integers.
- The `172/182/192/202/212/222/232` numbers are spaced by exactly 10 with no gaps or
  branching in this particular block, consistent with an online-survey-platform (e.g.
  Chinese platforms like Wenjuanxing/问卷星, commonly used for this kind of survey)
  internal question/widget-ID export convention where each question reserves a block of
  IDs. **This mechanical explanation is inferred, not literally stated anywhere in the
  paper, S1 File, or Figshare record** — none of the sources checked explain the numeric
  scheme itself. What IS directly confirmed from the source is the substantive point that
  matters for extraction: these 7 codes are, in ascending numeric order, a 1:1, in-order
  match to the 7 EIB subscale items as literally listed in the S1 File (item count 7
  exactly matches `irw_fetch`'s 7 unique items; response range 1-9 exactly matches the
  PISHSP's stated 9-point scale). The item-to-code assignment below is therefore a
  positional inference (ascending code order == source presentation order), the same
  convention used elsewhere in this pipeline for ordered item codes, not a guess from
  response-range plausibility alone.

## Derived vs. directly-read values
- `item_text` — directly read, verbatim, from S1 File paragraphs 41-47 (the 7 lines
  following the "Emotional Identification & Belongingness" subscale header, before the
  next subscale header "Professional Goals & Values").
- `option_text` — directly read, verbatim anchor labels, from S1 File paragraph 22 (the
  Part 3 rating-scale line): "1- extremely disagree; 2-disagree very much; 3-moderately
  disagree; 4- slightly disagree; 5- neither agree nor disagree; 6- slightly agree;
  7- moderately agree; 8- agree very much; 9- extremely agree". All 9 points have explicit
  verbal anchors in the source (unlike some 5-point scales elsewhere in this repo where
  only 1/3/5 are labeled) — nothing was invented for unlabeled points.
- `instructions` — the same Part 3 rating-scale line above, since it applies uniformly to
  all PISHSP items in the questionnaire, including this subscale; no additional
  instrument-level framing text precedes it in Part 3 (the subscale name itself, "Emotional
  Identification & Belongingness", is used as `instrument` context, not `section_prompt`,
  since it names the sub-instrument rather than giving item-shared passage/context text).
- `section_prompt` — left blank; there's no shared passage/testlet context beyond the
  scale-level instructions already captured in `instructions`. A single trivial
  `section_id` (`shu_2025_translation_eib_1`) was used per the skill's convention for
  instruments without real testlet grouping.
- **item -> code mapping (derived, positional)**: ascending `eib_pishp###` code assigned
  in order to the 7 items exactly as listed in the S1 File (172="For me, healthcare is the
  best career that I can do" ... 232="I feel that I am a member of the healthcare
  profession"). This is the one non-literal inferential step in this extraction; flagged
  per Step 6b guidance even though validation passed exactly, since the code<->item pairing
  itself isn't literally printed in any source document.

## Validation result
Exact match: `unique(candidate$item)` == `unique(irw::irw_fetch("shu_2025_translation_eib")$item)`
(7 items) and `unique(candidate$resp)` == `unique(...)$resp` (1-9), both confirmed via
`readRDS(".gt_shu_2025_translation_eib.rds")` per this benchmark's cached ground truth.

## Items not extracted
None — all 7 ground-truth items extracted with full item text and all 9 response-option
labels.
