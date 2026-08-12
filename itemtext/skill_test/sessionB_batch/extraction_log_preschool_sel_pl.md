# Extraction log: preschool_sel_pl

## Source used
Same LDbase dataset page as `preschool_sel_wj`:
`https://ldbase.org/datasets/38d4a723-c167-4908-a250-2cf29a4ff49b` ("Preschool Social
and Emotional Development Study—Connecticut Dataset," Bailey et al., LDbase, DOI
10.33009/ldbase.1680213217.8ed0). Reused the study's own child-level codebook already
cached from the `preschool_sel_wj` extraction at
`itemtext/skill_test/sessionB/.cache/preschool_sel_wj/codebook.pdf` /
`codebook.txt` (no re-fetch needed). Pages 20-24 of the codebook cover the "PreLas 2000"
section in full: Simon Says (English), Art Show (English), PreLAS Spanish gating item,
"A Simón Dice" (Simon Says, Spanish), and "Muestra de Arte" (Art Show, Spanish), each
giving the literal item-label text and the 1/0 scoring anchor for every `pl_*`/`plsp_*`
variable. The codebook's instrument-summary table (p.7 of the PDF) also gives one
sentence identifying and describing the instrument: "The preLAS tests receptive
language, listening comprehension, and expressive language. Two subtests were used:
Simon Says and Art Show," citing Duncan, S. E., & De Avila, E. A. (1998). PreLAS 2000.

## Source type used
Study's own public IES-funded codebook (same source type as `coach_chen_2022_phq9` and
`preschool_sel_wj`), not the PreLAS 2000 test manual/examiner kit itself. No PDF/image
OCR was needed — `codebook.txt` (already produced via `pdftotext` for the wj extraction)
had clean, directly-copyable text for this section.

## OCR / image-based extraction
None. All text came from the pre-existing `pdftotext` output (`codebook.txt`), not from
image/OCR extraction of the PDF.

## Derived vs. directly-read values
- `item_text` — directly read from the codebook's "Variable Label" column for each
  `pl_*`/`plsp_*` variable (e.g. `pl_as1_t1` = "What is this? (Apple)",
  `plsp_ss1_t1` = "Simón dice tócate la cara").
- `correct_response` — set to `"1"` uniformly (every item is coded 1 = correct
  response performed / correct word given, 0 = incorrect or other), directly reflecting
  the codebook's stated anchors.
- `option_text` — for Art Show items (`pl_as*`, `plsp_as*`), the resp=1 option text is
  the codebook's literal target-word anchor (e.g. "apple", "frog, toad", "mariposa");
  resp=0 is the codebook's literal "other"/"otro" anchor. For Simon Says items
  (`pl_ss*`), the codebook anchor is generic "1=correct / 0=incorrect" with no separate
  target-word text, so `option_text` is "correct"/"incorrect" verbatim. For Spanish
  Simon Says (`plsp_ss*`), the codebook restates the specific expected action for
  resp=1 (e.g. "toca la cara") and "otro" for resp=0 — both used directly.
- `instructions` — the codebook's one-sentence instrument description (quoted above),
  used directly. This is a description of the instrument, not a literal examiner
  administration script (see copyright note below) — flagged as such rather than
  presented as a verbatim admin script.
- `section_id` — a single shared id (`preschool_sel_pl_1`) for all 39 items; there is
  no testlet/shared-passage structure in this instrument (each Simon Says/Art Show item
  is a self-contained prompt), so `section_prompt` is blank throughout, consistent with
  the skill's "no grouping -> blank section_prompt" guidance.

## Copyright-hygiene note
PreLAS 2000 (Duncan & De Avila, 1998) is a commercially published, copyrighted
language-proficiency assessment (CTB/McGraw-Hill), the same category as the WJ-IV
subtest handled in `preschool_sel_wj`. As with that prior extraction, I used **only**
the study's own already-public codebook (which discloses the item prompts/labels and
scoring anchors as data documentation) and did **not** search for or use a leaked/
pirated copy of the PreLAS 2000 examiner's manual or test kit. The codebook does not
include the publisher's literal standardized administration script (e.g. any scripted
verbal framing beyond the prompt itself, or visual stimulus card descriptions beyond
what's implied by the item label), so `instructions` here is the codebook's own
descriptive sentence about the instrument, not a verbatim quote of a PreLAS
administration script.

## has_bare_integer_items
FALSE, confirmed: all 39 ground-truth items are named codes (`pl_as1_t1`, `pl_ss3_t1`,
`plsp_as7_t1`, etc.), not bare integers, so no item-to-content positional
reconstruction was needed — the codebook's variable names line up directly with the
IRW `item` values.

## Validation result
Exact match. `unique(item)` (39 values) and `unique(resp)` (0, 1) from
`candidate_preschool_sel_pl.rds` match the cached ground truth
(`.gt_preschool_sel_pl.rds`) exactly.

## Discrepancy noted (does not affect item/resp match)
The codebook also documents `plsp_ss10_t1` ("Simón dice siéntate" / "él/ella se
sienta"), continuing the Spanish Simon Says series to 10 items in parallel with the
English `pl_ss1_t1..pl_ss10_t1` series. Ground truth for this table has only
`plsp_ss1_t1..plsp_ss9_t1` (9 items) — `plsp_ss10_t1` is absent from the live IRW
response data. Per the skill's "don't force a match" rule, `plsp_ss10_t1` was **not**
included in the output (would have made 40 items, not 39). This mirrors the same kind
of codebook-vs-live-data item-count gap already documented for `preschool_sel_wj`
(missing LW ceiling items) — logged to `pending_index_notes.csv`.

## Items not extracted
None of the 39 ground-truth items were left without item_text/option_text/
correct_response — full coverage for all rows actually in the ground truth.
