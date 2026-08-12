# Extraction log: sv-maia2_randelovic_2021_hexaco60

## Source used
`irw::irw_fetch()` ground truth (cached, `.gt_sv_maia2_randelovic_2021_hexaco60.rds`) has
`item` values `HEXACO_60_1` ... up to `HEXACO_60_96` (60 distinct numbers, non-contiguous,
max 96 — NOT a clean 1-60 sequence). The Step-2 dictionary/OSF URL
(https://osf.io/em3wf/) has no accessible files via the OSF v2 files API
(`osfstorage` file list returns empty for node `em3wf`), so the actual survey instrument
as administered in this study could not be retrieved from the study's own OSF record.

Text was instead sourced from the HEXACO instrument's own publisher/copyright-holder site,
**hexaco.org** (official, freely downloadable for non-profit academic research use per the
site's own terms), specifically:
- `https://hexaco.org/downloads/ScoringKeys_100.pdf` and `ScoringKeys_60.pdf` — facet/item
  numbering keys for the 100-item and (separately renumbered) 60-item official forms.
- `https://hexaco.org/downloads/Serbian_self100.doc` — full Serbian 100-item self-report
  form, items numbered 1-100 in a table (cached at
  `itemtext/.cache/sv-maia2_randelovic_2021_hexaco60/Serbian_self100.doc`, extracted to
  `serbian_100_items.json` in the same cache dir).
- `https://hexaco.org/downloads/Serbian_self60.doc` — official Serbian 60-item form (own
  1-60 numbering), used only for cross-validation and for the instructions boilerplate
  (cached alongside the above).

## Why the 100-item numbering was used (key derivation step)
hexaco.org's own scoring-key notes state explicitly: "the items of the 60-item version
are not simply the first 60 items of the 100-item version. The item numbers are not the
same across the two versions." Since the ground truth's `HEXACO_60_N` labels go up to 96
(impossible under the official 60-item form's own 1-60 numbering, and consistent with the
100-item form's numbering, which also has an interstitial Altruism facet at 97-100 that is
absent from the ground truth's set), I tested whether the ground truth's 60 item numbers
are literally the underlying **100-item-form** item numbers.

Cross-checked by mapping each of the ground truth's 60 numbers onto the 100-item
scoring key's facet lists (4 items/facet, 24 facets + Altruism). Result: **every one of
the 6 domains x 4 facets contained either 2 or 3 of the ground truth's numbers**, summing
to exactly 10 items per domain / 60 total — the same 2-3 split (never 0,1,4) that the
*official* 60-item form's own scoring key shows per facet. This is strong evidence the
ground truth's 60 items are precisely the official HEXACO-60 item selection, but with the
researcher(s) having kept the original 100-item-pool item numbers as variable names
instead of the official form's renumbered 1-60 labels. This derivation is why
`serbian_100_items.json` (indexed 1-100) could be used directly: I pulled Serbian text for
exactly the 60 numbers appearing in the ground truth's `item` values, by number, no
positional/order guessing involved.

**Cross-validation:** compared the Serbian 100-item form's 100 item strings against the
Serbian *official* 60-item form's 60 item strings (independently downloaded/extracted).
56 of 60 matched byte-for-byte; the other 4 differed by minor rewording (e.g. slightly
different phrasing of the same trait content) — consistent with the two official forms
being separate translation passes of the same underlying item bank rather than the numbers
being coincidentally wrong. No manual reconciliation of those 4 was needed since the
ground truth's numbering matches the 100-item form, not the 60-item form's wording.

## OCR / image-based extraction
None. Both `Serbian_self100.doc` and `Serbian_self60.doc` are native `.docx` (Word 2007+)
files with a structured table (one row per item); text was extracted programmatically via
`python-docx`, not via OCR or manual transcription from an image/scan. The
`ScoringKeys_100.pdf` / `ScoringKeys_60.pdf` facet tables were extracted via `pdftotext`
(native PDF text layer, not scanned/OCR'd).

## Derived vs. directly-read values
- **Directly read**: `item_text` (Serbian, verbatim from the `Serbian_self100.doc` table
  cell for the matching item number), `option_text` (verbatim from that same doc's header
  row: `potpuno netačno` / `uglavnom netačno` / `nisam siguran` / `uglavnom tačno` /
  `potpuno tačno` for resp 1-5), `instructions` (verbatim, concatenated sentences from the
  form's instruction paragraphs).
- **Derived**: the *assignment* of item number -> item text (see facet-matching
  derivation above) — this is an inference, not a literal read, because the ground
  truth's own numbering scheme isn't disclosed anywhere in the source materials; it had to
  be reverse-engineered from the official scoring keys. Flagging this as the one
  non-trivial judgment call in this extraction, though it is well-supported (60/60 facet
  slot counts matched exactly, plus 56/60 independent text cross-validation).
- `instructions` uses the **60-item form's** phrasing ("Ovaj upitnik sadrži 60 tvrdnji" —
  "this questionnaire contains 60 statements") rather than the 100-item form's phrasing,
  since 60 items were in fact administered in this study (even though the item *numbering*
  internally follows the 100-item pool) — this one clause was picked from the 60-item
  form's instructions block for factual accuracy about the item count actually seen by
  respondents; the rest of the instructions text is identical between the two official
  forms.
- `correct_response` left blank throughout (personality trait inventory, no scoring key /
  right-or-wrong answer).
- `section_id`: single trivial section (`sv-maia2_randelovic_2021_hexaco60_1`,
  `section_prompt` blank) for all 60 items. HEXACO-60 items are presented as one
  continuous list rather than in blocks introduced by shared framing text per H/E/X/A/C/O
  factor (the factor structure is a scoring-key construct, not something presented to
  respondents with distinguishing intro text) — so per the skill's section-grouping rule
  this does not qualify as a testlet/shared-passage grouping, and per-factor sectioning
  was deliberately not used.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` ("items already have semantic
labels"). Confirmed: ground truth `item` values are `HEXACO_60_N` (semantic/named codes,
not bare integers), so Step 4's bare-integer reconstruction procedure did not apply here.
The numeric derivation problem in this table was different — not "which paper item does
integer N refer to," but "which of two possible numbering schemes (own 60-item vs.
underlying 100-item pool) does this table's `HEXACO_60_N` label use" — addressed above.

## Source type used
Publisher/copyright-holder official instrument site (hexaco.org), not the study's own
paper or OSF repository — the OSF project page for this specific study (osf.io/em3wf) had
no retrievable files, and the psyarxiv preprint page did not surface HEXACO-specific
material via fetch. HEXACO-PI-R/HEXACO-60 is explicitly released by its authors
(Ashton & Lee) for free non-profit academic use, including numerous language translations
hosted directly on hexaco.org, so this is treated as the authoritative source for item
text rather than a secondary/unofficial one.

## Validation
`sort(unique(candidate$item))` == `sort(unique(gt$item))`: TRUE (exact, all 60 items).
`sort(unique(candidate$resp))` == `sort(unique(gt$resp))`: TRUE (exact, 1-5, both coerced
to `numeric` to match the ground truth's column type).

## Items not extracted
None. All 60 ground-truth items received item text; no partial coverage.
