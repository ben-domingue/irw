# Extraction log: florida_twins_dweck

## Source used
Same underlying LDbase dataset (Florida Twin Project on Reading, Behavior, and
Environment) as sibling tables `florida_twins_dbi`, `_hwk`, `_class`, `_media` already
processed in this batch series. Reused the cached **Wave 3 Child Codebook**
(`W3_Child_Codebook_LDBase.docx`, plain-text extraction at
`.cache/florida_twins_dbi/codebook_text.txt`) — the `florida_twins_dbi` cache, not
`florida_twins_class`'s Wave 1 cache. The DWECK section (p. 17 per the codebook's own
table of contents) is present verbatim in that Wave 3 file; grepping the Wave 1 codebook
text (`.cache/florida_twins_class/codebook_text.txt`) for "dweck" returned no hits, so
Wave 1 does not contain this instrument.

## Source type used
Directly-transcribed text from the source codebook (a .docx converted to plain text and
cached locally), not an image/PDF. No OCR was involved — the .docx text layer was read
directly, so no OCR-related uncertainty applies here.

## OCR / image-based extraction
Not applicable. The codebook is a native Word document (`W3_Child_Codebook_LDBase.docx`);
its text was extracted programmatically (not via OCR of a scanned image), so there is no
OCR-error risk to flag for this table.

## Derived vs. directly-read values
- `item_text` for all 8 items: directly read from the codebook's "DWECK" section, in the
  literal presentation order given there. No paraphrasing.
- `item` codes (`qdweckt1`...`qdweckt8`): matched 1:1 by presentation order to the
  ground-truth item set. The codebook's own variable labels for items 3, 5, 7, and 8 are
  written with an `n` prefix (`nqdweckt3`, `nqdweckt5`, `nqdweckt7`, `nqdweckt8`),
  flagging them as the reverse-scored ("incremental"/growth-mindset) items used in the
  `DWECKincremental` derived-score formula documented later in the same codebook section.
  The ground-truth data uses `qdweckt3`, `qdweckt5`, `qdweckt7`, `qdweckt8` (no `n`
  prefix) — this is a naming-convention difference only (raw entry variable vs.
  distributed/IRW item code), not a different item; the item text and position are
  unambiguous, so this is a **directly-read** item-order mapping, not an inferred one.
- `resp`/`option_text` mapping (1=Strongly Agree ... 6=Strongly Disagree): directly read
  from the codebook's response-scale header row, which precedes all 8 items and is
  identical for each (`Strongly Agree / Agree / Mostly Agree / Mostly Disagree /
  Disagree / Strongly Disagree` against `1 2 3 4 5 6`). Confirmed the numeric direction
  is entry-order (1=Strongly Agree, not reverse) since the codebook lists the labels and
  digits in the same left-to-right order for every item. No re-derivation was needed;
  this is a directly-read scale, not something I reconstructed from range-matching.
- `correct_response`: left blank — the DWECK/Implicit Theories of Intelligence scale is
  an attitudinal/belief measure with no correct answer; the codebook only documents
  reverse-scoring for computing subscale sums (`DWECKtotal`, `DWECKentity`,
  `DWECKincremental`), which is a derived composite score, not an item-level scoring key,
  so it was not written into `correct_response`.

## has_bare_integer_items
FALSE, as given in the dictionary row — ground-truth `item` values are already
semantically named (`qdweckt1`...`qdweckt8`), so no position-based reconstruction of
which paper item an integer refers to was required; the item-order mapping used here was
still cross-checked against the codebook's stated presentation order (see above) purely
to get `item_text` right, not to resolve an item-code ambiguity.

## Wave discrepancy (flagged, not blocking)
Ground truth's own `wave` column contains only `2` and `3` (no wave-1 rows) for this
table. The extracted item text/instructions come from the **Wave 3** codebook only —
there is no cached Wave 2 child codebook in this batch's `.cache/` directories to confirm
Wave 2 used identical item wording. Circumstantial support that the wording is unchanged
across waves 2 and 3: the Wave 3 codebook's own "REFERENCES" section states "References
appear in same order as found in codebook/child booklet... Below are references for
scales used in Wave 2" directly above the DWECK citation — suggesting this codebook
section was carried over from a Wave 2 document without being rewritten, i.e. the DWECK
item wording is likely identical between waves 2 and 3. This is treated as sufficient to
extract with confidence but is logged since it wasn't independently verified against a
Wave 2 source document.

## Ambiguities
None affecting the validation gate. Item/resp sets matched `irw::irw_fetch` exactly (see
below).

## Items not extracted
None — all 8 ground-truth items (`qdweckt1`-`qdweckt8`) and all 6 ground-truth resp
values (1-6) were extracted with literal item text and response-option labels; validated
exact match against ground truth (`unique(item)` and `unique(resp)` identical, order
ignored).
