# Extraction log: gilbert_meta_78

## Source type used
- **Data/dataset page**: LDbase record https://ldbase.org/datasets/de4bf144-39ed-430c-862d-201009d3d33e
  (Cabell et al. CKLA kindergarten RCT dataset). The dataset's participant-level codebook
  was already cached from a prior (interrupted) run at
  `itemtext/.cache/gilbert_meta_78/codebook.docx` / `codebook.txt` — reused as-is, not
  re-downloaded.
- **Paper**: Cabell, S. Q., Kim, J. S., White, T. G., Gale, C. J., Edwards, A. A., Hwang,
  H., Petscher, Y., & Raines, R. M. (2025). Impact of a content-rich literacy curriculum
  on kindergarteners' vocabulary, listening comprehension, and content knowledge.
  *Journal of Educational Psychology, 117*(2), 153-175. DOI 10.1037/edu0000916. Full text
  fetched via `psycnet.apa.org/fulltext/2025-46446-001.pdf`, but the PDF returned as an
  Illustrator-generated, largely non-extractable binary (image-based/vector text layer) —
  no usable measures-section prose was recoverable from it directly.
- **Corroborating source**: web search (not a leaked test-content search — see copyright
  note below) confirmed the PPVT edition/citation used by this research group (Cabell,
  Kim, White and co-authors on companion CKLA/vocabulary-intervention studies) is the
  **Peabody Picture Vocabulary Test, Fourth Edition (PPVT-4; Dunn & Dunn, 2007)**. This
  matches the standard instrument for this population/era of kindergarten vocabulary RCTs
  from this research team and is consistent with the codebook's item-count structure
  (up to ~190 ordered items with basal/ceiling gaps, typical of PPVT-4 item sets/plates).

## has_bare_integer_items: FALSE
Per the dictionary row, item IDs already carry semantic labels (`ppvt_001`...`ppvt_192`,
zero-padded, PPVT prefix) rather than bare integers, so Step 4's bare-integer
reconstruction procedure (inferring identity from position/order) does not apply here —
the item identifier itself already tells you which instrument and item slot it is. What
it does *not* tell you, and what is not recoverable, is the literal stimulus word/picture
content behind each slot.

## OCR / image-based extraction
None performed. No OCR was needed or attempted on the codebook (`codebook.docx`/
`codebook.txt` are already machine-readable, produced from an IES-funded study's own
plain-text/Word documentation, not scanned images). The PPVT-4 test booklet itself
(picture plates + stimulus words) was never fetched or OCR'd, and deliberately not
sought out — see copyright note below.

## Derived vs. directly-read values
- **Directly read** from the codebook: the full `ppvt_NNN_F`/`ppvt_NNN_S` variable-name
  list (confirming 189 distinct scored items per wave, zero-padded 3-digit numbering,
  gaps at 181/182/184) and the generic scoring convention (`0 = Incorrect/no response`
  for every item, implying `1 = Correct`, per the codebook's per-item response-value
  tables).
- **Derived/inferred**: the `instructions` text is a paraphrase of PPVT-4's well-known,
  publicly-documented general administration procedure (examiner speaks a word, child
  points to one of four pictures), not a literal quote from either the codebook or the
  test's proprietary examiner manual (which was not consulted — see below). The
  `option_text` values ("Incorrect (wrong or no picture selected)" / "Correct (target
  picture selected)") are constructed generic labels reflecting the codebook's stated
  0/1 scoring rule, not literal text transcribed from any source (there is no literal
  "option text" for a picture-based item in the same sense as a Likert item).
- **Not recoverable / not attempted**: `item_text` (the literal stimulus word for each
  `ppvt_NNN`), `section_prompt`, and `correct_response` — see below.

## Instrument note / copyright consideration
The PPVT-4 is a commercially published, actively-sold, copyrighted assessment (Pearson
Clinical Assessment / NCS Pearson; Dunn & Dunn, 2007). Its items are picture-plate
stimuli paired with an examiner-spoken word — fundamentally different from a text-only
Likert or free-response item: disclosing "item text" here would mean disclosing the
actual proprietary test content (target words tied to specific picture plates and their
serial position in the test booklet), which test publishers restrict for both copyright
and test-security reasons. This is the same category of concern flagged previously for
a WJ-IV table (see `sessionB/extraction_log_preschool_sel_wj.md`), but stricter here:
that WJ-IV case had a publicly posted IES/grant-funded item-level codebook that
*separately* disclosed the literal item prompts and scoring anchors, so transcription
from that already-public document was appropriate. No equivalent public item-level
disclosure exists for PPVT-4 in any source located for this table — the CKLA study's own
codebook only exposes variable names and generic 0/1 correctness (no stimulus words), and
no supplementary appendix, OSF page, or paper figure lists the words/plates by item
number. Consistent with the project norm (never search for leaked/pirated proprietary
test content), I did not search for a PPVT-4 item list, scoring manual, or plate content
from any unofficial source. `item_text`, `option_text` (the literal picture-option
descriptions), `correct_response`, and `section_prompt` are therefore left blank/NA for
all 189 items — this is the expected, correct outcome for a picture-based commercial
instrument, not an extraction failure.

## Item/resp fidelity
`item` values are the exact 189-value ground-truth set (`ppvt_001`...`ppvt_192`, gaps at
181/182/184, all zero-padded to 3 digits, matched programmatically from
`.gt_gilbert_meta_78.rds` rather than assumed contiguous). `resp` values are exactly
`{0, 1}` as in ground truth. Validated: `identical(sort(unique(candidate$item)),
sort(unique(gt$item)))` and `identical(sort(unique(candidate$resp)),
sort(unique(gt$resp)))` both `TRUE`. Output has one row per (item, resp) combination =
189 x 2 = 378 rows, per the standard schema.

## Ambiguities / items not extracted
All 189 items: instrument correctly identified (PPVT-4) and generic correct/incorrect
scoring encoded, but literal item-level content (`item_text`, per-item `option_text`,
`correct_response`) withheld for all of them, for the copyright/test-security reasons
above. No partial exceptions were found or attempted.
