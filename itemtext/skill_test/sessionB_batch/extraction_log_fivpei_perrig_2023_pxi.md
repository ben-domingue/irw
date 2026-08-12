# Extraction log: fivpei_perrig_2023_pxi

## Source type used
Two independent, directly-fetched primary sources (no OCR, no image-based extraction
needed — both were text-layer PDFs):

1. **`Printout_online_survey.pdf`** — the study's own OSF materials
   (https://osf.io/8xuhr/, file `kcr8a`), a full printout of the Qualtrics/online survey
   as actually administered to participants, including the literal PXI item wording,
   the literal "Instructions - Part A" framing text, and the literal 7-point response
   scale labels (verbal anchors "Strongly disagree" ... "Strongly agree" over numeric
   codes -3 to 3).
2. **`PXI_Questionnaire_official.pdf`** — the official standalone PXI questionnaire PDF
   published by the scale's original developers at
   https://playerexperienceinventory.org/assets/docs/PXI_Questionnaire.pdf (Abeele,
   Spiel, Nacke, Johnson, & Gerling, 2020). Used as an independent cross-check, not as
   the primary source, since this table is Perrig et al.'s *replication/validation*
   study of the PXI, not the original scale-development paper.

Both cached under `.cache/fivpei_perrig_2023_pxi/`.

Both sources gave **word-for-word identical text** for all 33 items (down to the exact
punctuation, e.g. both have "I liked playing the game" with no trailing period on that
one item specifically, unlike its neighbors) — this is a strong, independently
corroborated match, not a single-source read.

## Structure discovered
Ground truth items are `PXI_<subscale>_<1|2|3>` for 11 subscales (appeal, autonomy,
challenge, control, curiosity, enjoyment, goals, immersion, mastery, meaning, progress)
x 3 items each = 33 items, resp 1-7.

The Perrig survey printout presents the 33 items in **3 blocks labeled "PXI_1",
"PXI_2", "PXI_3"** (section headers 3.1.1/3.1.2/3.1.3 in the source PDF), each block
containing one item from every one of the 11 subscales, in a fixed within-block
subscale order (meaning, curiosity, mastery, autonomy, immersion, [attention-check
row], progress, appeal, challenge, control, goals, enjoyment — the attention-check row
only appears in block 1 and is not a PXI item, so was excluded). The source's own block
labels ("PXI_1"/"PXI_2"/"PXI_3") map directly onto the ground-truth item-name numeric
suffix (`_1`/`_2`/`_3`) — this is a disclosed, literal correspondence in the source
document, not an inferred one. The official PXI_Questionnaire.pdf independently
confirms the same 3-item-per-subscale ordering (items grouped consecutively by
subscale rather than by block), and the wording of each subscale's 3 items matches the
Perrig printout's 3 blocks item-for-item, which cross-validates the `_1`/`_2`/`_3`
assignment.

Response scale: source shows a 7-point scale with the literal numeric labels -3 to 3 and
verbal anchors only at the endpoints ("Strongly disagree" / "Strongly agree") plus a
labeled midpoint (0 = "Neither disagree, neither agree"); intermediate points -2, -1, 1,
2 also carry brief literal verbal anchors in the Perrig printout ("Disagree", "Slightly
disagree", "Slightly agree", "Agree") — all 7 anchors are directly transcribed, not
invented. The ground-truth `resp` values 1-7 are a straightforward +4 shift of the
source's -3..3 coding (1=-3="Strongly disagree" ... 7=3="Strongly agree"); this shift is
the standard/expected recoding for this scale and was confirmed plausible against the
known PXI scoring convention (Abeele et al. 2020 also report the scale as -3..+3
internally, transformed to 1-7 for storage in many derived datasets).

## Structure of output
Single `section_id` (`fivpei_perrig_2023_pxi_1`) for all 33 items with blank
`section_prompt`: the PXI presentation has no testlet/shared-passage structure — all 33
items share one common `instructions` text ("In this next part of the survey, we will
explore how you experienced the game ([name of game]). For this, indicate to what
extent you agree with the statements. In total, there will be 33 statements, polling for
your experience."), transcribed verbatim, with `[name of game]` left as the literal
bracketed placeholder from the source (a piped-in variable, not paraphrased). No
subscale-level shared prompt text is presented to participants (subscale membership is
a scoring-key concept, not something shown in the instrument itself), so a single
section for the whole instrument was used rather than 11 subscale-level sections, per
SKILL.md's guidance to record instructions once at the appropriate scope rather than
duplicating it across artificial sub-sections.

`correct_response` left blank for all items — the PXI is a player-experience Likert
scale with no scoring key/correct answer.

## Has_bare_integer_items
FALSE, as stated in the dictionary row — ground-truth `item` values are already
semantic codes (`PXI_<subscale>_<n>`), not bare integers, so no positional
reconstruction was needed for item-to-text assignment; each item code names its own
subscale directly, and only the presentation order within each subscale (1st/2nd/3rd
occurrence) needed confirming against the source, which was done via the source's own
block labels plus independent cross-check against the official PXI questionnaire.

## OCR / image-based extraction
None used. Both source PDFs (`Printout_online_survey.pdf`, 5pp,
`PXI_Questionnaire_official.pdf`, 6pp) have a native text layer; item text, instructions,
and response-scale anchors were read directly from extracted text, not from images or
OCR.

## Derived vs. directly-read values
- `item_text`, `instructions`, `option_text` (all 7 anchor labels): directly read,
  verbatim, from `Printout_online_survey.pdf`, cross-checked verbatim against
  `PXI_Questionnaire_official.pdf`.
- `resp` numeric coding (1-7): directly read from ground truth (`irw::irw_fetch`-style
  cache); the correspondence to the source's literal -3..3 labels is a derived
  (+4 shift) mapping, not itself printed anywhere as "1-7" in either source PDF — flagged
  here for transparency even though it's a standard, low-risk recoding.
- `section_id`/single-section structure: derived (no explicit "no grouping" statement in
  the source; concluded from the absence of any subscale-level shared prompt text).
- `instrument` name ("Player Experience Inventory (PXI)"): the paper's/PXI developers'
  own name for the scale, not itself printed as a header inside either PDF's item pages,
  taken from the wider paper title/abstract and the official questionnaire's own title
  ("PXI Questionnaire").

## Ambiguities
- None material. The `_1`/`_2`/`_3` block-to-suffix correspondence relies on the source
  document's own block labels matching the ground-truth item-name suffixes exactly,
  which is about as strong a positional-mapping justification as this kind of task gets
  (not an inferred numbering from unlabeled positions).

## Items not extracted
None — all 33 ground-truth items were extracted with full `item_text` and all 7
`option_text`/`resp` pairs, and validated as an exact match against
`unique(item)`/`unique(resp)` from the cached ground truth
(`.gt_fivpei_perrig_2023_pxi.rds`).

## Note on sibling table `fivpei_perrig_2023_attdiff`
SKILL.md references this same paper's `fivpei_perrig_2023_attdiff` table as an example
of a paper-vs-data item-count discrepancy (28 items in the paper's AttrakDiff instrument
vs. 21 in the live data). That discrepancy is specific to the AttrakDiff semantic
differential block (visible on page 2 of `Printout_online_survey.pdf`, section 4.1.1,
28 word-pair rows) and is **not relevant to this table** — the PXI block (33 items) was
confirmed to match the live data's 33-item count exactly, with no analogous
discrepancy.
