# Extraction log: florida_twins_dbi

## Source used
Dictionary URL (`https://ldbase.org/datasets/3f7033dd-47a5-4ef8-aeab-08a559dce0d1`)
is the **Wave 1** Child Survey Measures dataset page on LDbase, not Wave 3. Ground
truth `item` values (`dbi1`-`dbi36`) and `wave == 3` in the data pointed to the Wave 3
Child Survey Measures dataset instead. Followed the "Related Datasets"/project
hierarchy links on the Wave 1 page to the correct sibling dataset:

- Wave 3 Child Survey Measures dataset: `https://ldbase.org/datasets/8f08a202-2515-4feb-92ff-d1bcf30bd410`
  (data file `w3multitwinq818 LDBase.csv`, matching the raw filename referenced in the
  prior crashed attempt)
- Its codebook document page: `https://ldbase.org/documents/9e28dca4-acb8-4ba4-aa26-c3d6f1d806ce`
  ("Codebook: Wave 3 Child Survey Measures Codebook")
- Actual downloadable file: `https://ldbase.org/system/files/documents/2021-07/W3_Child%20Codebook%20LDBase.docx`

Downloaded and cached as
`.cache/florida_twins_dbi/W3_Child_Codebook_LDBase.docx` (84,627 bytes, valid
Word 2007+ file), then extracted its `word/document.xml` to plain text
(`.cache/florida_twins_dbi/codebook_text.txt`) for transcription. Also cached
`.cache/florida_twins_dbi/dataset_page.html` (Wave 1 page, from the earlier
crashed attempt) — not the ultimate source, kept for reference.

## Source type used
Instrument codebook (.docx), scraped from the LDbase dataset repository page for the
Wave 3 Child Survey Measures dataset — not the published paper itself. No PDF/OCR
involved; the codebook is a native Word document, and its `document.xml` was parsed
directly as XML/text (no image-based extraction, no OCR).

## OCR / image-based extraction
None. The codebook is a native .docx (Word 2007+, valid zip/XML container). Item text
was extracted via a direct XML-to-text strip of `word/document.xml` — no scanned pages,
images, or OCR were involved anywhere in this extraction.

## Structure discovered
The codebook confirms "DBI" = **Disruptive Behaviors Inventory (DBI)**, described as a
"checklist/endorsement of behavioral problems related to reckless behavior, conduct
problems, or anti-social behaviors." Its dedicated "DBI" section (codebook pp. 18-19)
gives:

- Preamble/instructions text (transcribed verbatim into `instructions`): "The following
  statements pertain to your own experiences; below are listed minor behavioral problems
  that adolescents might become involved in. Please read each description and mark an X
  in the blank if you ever had this problem."
- A data-quality note about 4 TIDs (217400, 287700, 463200, 308700/01) whose
  questionnaires were recoded due to apparent reversed marking — not transcribed into
  any output field since it describes a data-cleaning decision, not instrument text.
- 36 numbered behavior statements. Items 1-22 are explicitly numbered in the source;
  items 23-36 continue as an unnumbered list immediately following item 22 in the same
  `dbi[#]` variable block, with no scale-break or renumbering — counted sequentially as
  23-36 to reach the full 36-item set matching `dbi1..dbi36` in the ground truth. The
  `dbi[#]` variable-naming convention stated directly beneath the item list ("dbi[#]
  Unchecked = 0; Checked = 1") is what justifies the direct positional mapping from
  codebook order to `dbi1`...`dbi36` — this is an explicit naming convention disclosed by
  the codebook, not a range-matching guess.
- Scoring key for the response scale, stated once for the whole block: "Unchecked = 0;
  Checked = 1" — matches `resp` values {0, 1} in the ground truth exactly. Mapped
  `option_text`: `resp=0` -> "Unchecked", `resp=1` -> "Checked".

## Derived vs. directly-read values
Everything in the output is a direct, literal transcription from the codebook text —
`instrument`, `instructions`, all 36 `item_text` strings, and the `option_text`/`resp`
scoring key. Nothing was derived, paraphrased, computed, or inferred beyond the
sequential item numbering described above (items 23-36 are unnumbered in the source
document but are positionally unambiguous — they immediately follow item 22 in the same
list with no intervening section break, and there are exactly 14 of them, completing
the 36 total the `dbi[#]` convention and the ground truth both require).

## has_bare_integer_items
FALSE, as given in the dictionary row — `item` values are semantic codes (`dbi1`..`dbi36`),
not bare integers, so no order-reconstruction-from-integer-codes step was needed; the
positional mapping used here is instead justified directly by the codebook's own
`dbi[#]` variable-naming convention (see above).

## Structure of output
Single section (`florida_twins_dbi_1`, blank `section_prompt` — no testlet/passage
grouping in this checklist instrument), one `instrument`/`instructions` pair applying to
all 36 items, `correct_response` blank throughout (behavior-checklist endorsement, no
scoring key/correct answer). 72 rows total (36 items x 2 resp levels each).

## Validation
`unique(item)` and `unique(resp)` in `candidate_florida_twins_dbi.rds` match
`unique(item)`/`unique(resp)` in `.gt_florida_twins_dbi.rds` exactly (36 items,
`dbi1`..`dbi36`; resp {0, 1}). No items skipped, no discrepancies to log in
`pending_index_notes.csv`.
