# Extraction log: florida_twins_class

## Source used
Dictionary URL (`https://ldbase.org/datasets/3f7033dd-47a5-4ef8-aeab-08a559dce0d1`) is the
**Wave 1** Child Survey Measures dataset page on LDbase. Unlike `florida_twins_dbi` (a sibling
table from the same LDbase project, whose ground-truth `wave` value pointed to Wave 3 and thus
required the Wave 3 codebook), `florida_twins_class`'s ground truth (`.gt_florida_twins_class.rds`)
has `wave == 1` for every row, so the Wave 1 dataset page is in fact the correct source here — no
redirect to a sibling dataset was needed.

Checked the already-cached `florida_twins_dbi` material first per instructions
(`.cache/florida_twins_dbi/codebook_text.txt`, the Wave 3 codebook): it does **not** contain a
`class[#]` item block (Wave 3 covers Homework/Free Time, Grades, Neighborhood Environment,
Information Sharing, Book Authors, PANAS, Friends, Substance Use, DWECK, DBI, LEQ only — no
"Class Time" section). So the cached Wave 3 codebook does not cover `class1`..`class10`; fetched
the Wave 1 codebook instead.

- Wave 1 dataset page: `https://ldbase.org/datasets/3f7033dd-47a5-4ef8-aeab-08a559dce0d1`
  (already cached from the `florida_twins_dbi` run as `.cache/florida_twins_dbi/dataset_page.html`,
  reused here rather than refetched)
- Its Wave 1 Child Codebook document page: `https://ldbase.org/documents/4d4acbc5-f07b-4282-9da3-5692ffacc8b0`
  ("Codebook: Wave 1")
- Actual downloadable file: `https://ldbase.org/system/files/documents/2021-07/W1_Child%20codebook%20LDBase.docx`

Downloaded and cached as `.cache/florida_twins_class/W1_Child_Codebook_LDBase.docx` (119,430
bytes, valid Word 2007+ file), then extracted its `word/document.xml` to plain text
(`.cache/florida_twins_class/codebook_text.txt`) for transcription.

## Source type used
Instrument codebook (.docx), scraped from the LDbase dataset repository page for the Wave 1
Child Survey Measures dataset — not the published paper itself. No PDF/OCR involved.

## OCR / image-based extraction
None. The codebook is a native .docx (Word 2007+, valid zip/XML container). Item text was
extracted via a direct XML-to-text strip of `word/document.xml` — no scanned pages, images, or
OCR were involved anywhere in this extraction.

## Structure discovered
The codebook's "Class Time" section (immediately following the Author Recognition Test / ART
section) gives:

- Preamble/instructions text (transcribed verbatim into `instructions`): "This set of questions
  is about how things work at your school.  How true is it that your teacher does the following:"
- 10 numbered items under the `class[#]` variable-naming convention, explicitly numbered 1-10 in
  the source, giving a direct, unambiguous positional mapping to `class1`..`class10`:
  1. Have students talk about their class work
  2. Let students decide where to sit at the beginning of the school year
  3. Allow students to choose their partners for group work
  4. Ask for students' ideas
  5. Let students help make school rules
  6. Pay too much attention to grades and not enough attention to helping students learn
  7. Only care about the smart kids in the class
  8. Have given up on some of their students
  9. Encourage students to compete against each other for grades
  10. Give students credit for trying hard
- Response scale header lists five categories (extraction artifact split "Somewhat True" across
  two lines as "Somewhat" / "True" — reassembled here): "Not at All" / "A little True" /
  "Somewhat True" / "Quite True" / "Very True", scored 1-5 in that ascending order for items
  1-5 and 10 (each followed directly by "1 2 3 4 5" in source order).
- Items 6-9 additionally show a jumbled reverse-coding table (`nclass6`..`nclass9`, values
  "1 5 2 4 3 3 4 2 5 1" etc.) documenting how the derived reverse-scored `nclassX` variables
  used in the `ClassSP` composite are computed from the raw `classX` items (1<->5, 2<->4, 3<->3).
  This is a scoring-derivation note for a *different* variable (`nclassX`), not additional
  response options for `classX` itself — the ground-truth `item` values are `class1`..`class10`
  (not `nclass6`..`nclass9`), so the plain 1-5 "Not at All"..."Very True" scale applies uniformly
  to all 10 items as transcribed above; the reverse-coding table was not used to alter
  `option_text`/`resp` mapping.
- Scale name/scoring note (not transcribed into item fields, background only): "Based on
  Perception of Teaching Style scale" (Eccles, Wigfield, Midgley, Reuman, Maciver, & Feldlaufer,
  1993). Three composites are defined (`ClassCA`, `ClassCM`, `ClassSP`) but these are
  derived/scored variables, not part of the item-level instrument text.

## Derived vs. directly-read values
Everything in the output is a direct, literal transcription from the codebook text —
`instrument` (constructed as "Class Time (Perception of Teaching Style scale)", combining the
codebook's section heading and its cited scale name — not itself a literal quoted phrase, but
built entirely from codebook-stated names, no invented content), `instructions`, all 10
`item_text` strings, and the `option_text`/`resp` scale. Nothing was derived, paraphrased,
computed, or inferred beyond reading straightforward sequential item numbering (items are
explicitly numbered 1-10 in the source, no gaps or renumbering, unlike the DBI table's
unnumbered tail).

## Source type used
(see above — .docx codebook, no OCR)

## has_bare_integer_items
FALSE, as given in the dictionary row — `item` values are semantic codes (`class1`..`class10`),
not bare integers, so no order-reconstruction-from-integer-codes step was needed; the codebook's
own explicit 1-10 item numbering directly justifies the positional mapping.

## Structure of output
Single section (`florida_twins_class_1`, blank `section_prompt` — no testlet/passage grouping in
this teacher-perception scale), one `instrument`/`instructions` pair applying to all 10 items,
`correct_response` blank throughout (attitude/perception scale, no scoring key/correct answer).
50 rows total (10 items x 5 resp levels each).

## Validation
`unique(item)` and `unique(resp)` in `candidate_florida_twins_class.rds` match
`unique(item)`/`unique(resp)` in `.gt_florida_twins_class.rds` exactly (10 items,
`class1`..`class10`; resp {1,2,3,4,5}). No items skipped, no discrepancies to log in
`pending_index_notes.csv`.
