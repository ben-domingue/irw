# Extraction log: sun_2025_morality_study1_dependability

## Source used
- Full-text open-access PDF of the published article: Sun, J., Wu, W., & Goodwin, G. P.
  (2025). Are moral people happier? Answers from reputation-based measures of moral
  character. *Journal of Personality and Social Psychology, 128*(5), 1160-1180.
  https://jessiesun.me/publication/sun-2025/sun-2025.pdf (author's own postprint copy,
  21 pages; cached at `.cache/sun_2025_morality_study1_dependability/sun_2025_paper.pdf`
  and `sun_2025_paper.txt` after `pdftotext -layout`). The DOI (10.1037/pspp0000539) is
  paywalled at the APA site, so this author copy was used instead.
- OSF project https://osf.io/5e9y3/overview (`data-clean/normdat-labels.csv`, cached at
  `.cache/sun_2025_morality_study1_dependability/normdat-labels.csv`, fetched via the OSF
  v2 files API since the raw project page render didn't expose file contents to WebFetch).
  This file is the codebook for a separate MTurk moral-relevance norming study the authors
  ran on the same item pool, not a Study-1-specific codebook, but it gives verbatim item
  text keyed to standard BFI-2 item numbers (`mv.BFI2.<n>`).
- `data/sun_2025_morality.do` in this repo (the existing IRW processing script for this
  dataset family) was also inspected to confirm the `itbfi2NN` variable-naming convention
  is the literal column name in the raw OSF `study1-maindat.csv`, not something the .do
  file invents — no per-item text or labels live in the .do file itself, so it didn't add
  new text but confirmed the naming pattern (`itbfi2` + BFI-2 item number: e.g. compassion
  facet block is `itbfi22 itbfi217 itbfi232 itbfi247` = BFI-2 items 2, 17, 32, 47, exactly
  the compassion facet's standard item numbers; respectfulness block is `itbfi27 itbfi222
  itbfi237 itbfi252` = items 7, 22, 37, 52, the standard respectfulness facet numbers).
  This cross-check was the basis for decoding `itbfi213`/`itbfi243` below.

## Structure discovered
Ground truth: only 2 items, `itbfi213` and `itbfi243`, resp 1-5 (plus NA for missing
responses, which is not a response-option value so isn't represented as its own row,
consistent with the `firstborn_personality` reference example and how
`validate_items.R`'s `sort(unique(...))` drops NA).

The paper (p. 1165-1166, "Measures" section) states the 32-item informant-reported moral
character measure includes "dependability (two items; e.g., 'Is reliable, can always be
counted on')" and explains: "The two most morally relevant items from the responsibility
facet [of BFI-2 conscientiousness] ('Is reliable, can always be counted on'; 'Is
dependable, steady') appear to capture the construct of dependability; thus, we formed a
dependability composite based on these two items." Items were selected from the Big Five
Inventory-2 (BFI-2; Soto & John, 2017).

Applying the `itbfi2<NN>` = BFI-2 item `<NN>` decoding rule (confirmed above via the
compassion/respectfulness blocks in `sun_2025_morality.do`, and independently confirmed by
`normdat-labels.csv` which has `mv.BFI2.13,Responsibility,"is dependable, steady"` and
`mv.BFI2.43,Responsibility,"is reliable, can always be counted on"`):
- `itbfi213` -> BFI-2 item 13 -> "is dependable, steady"
- `itbfi243` -> BFI-2 item 43 -> "is reliable, can always be counted on"

This is a two-independent-source confirmation (the paper's own prose gives both item
texts verbatim; the OSF norming-study codebook gives the same two texts keyed to the exact
BFI-2 item numbers embedded in the variable names), so treated as a solid mapping, not a
guess -- despite `item` not being a bare integer, this is functionally the same
"reconstruct which paper item a numeric code refers to" problem the skill flags for bare
integers, and it was resolved with two independent, mutually consistent sources rather
than range-matching.

## Structure of output
One `section_id` (`sun_2025_morality_study1_dependability_1`) for both items, since both
share the same instrument-wide response instructions and the same item stem. Per the
instructions/section_prompt boundary rule: whole-instrument response-format framing
("Informants rated the extent to which each of these statements described their target
using a 5-point scale anchored by strongly disagree and strongly agree") went in
`instructions`; the item stem specific to the compassion/respectfulness/dependability
facets ("[Target's name] is someone who...") went in `section_prompt` since it is not
universal to every item in the full 32-item measure (the paper explicitly says "All other
items were simply preceded by the target's name" -- i.e. other facets use a different,
shorter stem), so it doesn't belong in `instructions`.

`option_text` populated only for resp 1 ("strongly disagree") and resp 5 ("strongly
agree") -- the paper states the scale is "anchored by" these two endpoints only; no verbal
labels for the intermediate points 2-4 are given anywhere in the paper or OSF materials,
so those were left blank rather than invented (same convention as the
`firstborn_personality` reference example).

`correct_response` left blank throughout -- this is a personality/character rating
measure, no scoring key.

## has_bare_integer_items
FALSE, as stated in the dictionary row -- `item` values are the named codes `itbfi213`/
`itbfi243`, not bare integers, so Step 4's bare-integer reconstruction procedure did not
formally apply. In practice the same category of judgment call was still required (see
"Structure discovered" above), because the codes' meaning wasn't self-evident from the
ground truth alone and had to be decoded via the BFI-2 numbering convention.

## OCR / image-based extraction
None needed. The source PDF was text-based (not scanned/image), extracted cleanly with
`pdftotext -layout`; no OCR was used anywhere in this extraction.

## Derived vs. directly-read values
All values are directly read/transcribed, not derived or computed:
- `item_text` for both items is a verbatim quote from the published paper's own prose
  (both item texts appear in-line in quotation marks in the Measures section), independently
  cross-checked against the verbatim OSF `normdat-labels.csv` codebook entries for the same
  BFI-2 item numbers -- not inferred from item-bank conventions alone.
- `option_text` anchors ("strongly disagree"/"strongly agree") are a direct paraphrase-free
  read of the paper's stated scale anchors.
- `instructions` and `section_prompt` are close transcriptions of the paper's own
  description of the rating task and item stem (the paper does not print the instrument in
  a literal instructions-paragraph form the way a participant would see it, so this is the
  closest available literal text, not an invented summary).
- The `itbfi2<NN>` -> BFI-2 item `<NN>` decoding itself is an inference, but one confirmed
  by two independent sources (paper prose + OSF codebook) rather than assumed from the
  naming pattern alone.

## Source type used
Published journal article (author's open-access postprint PDF) as primary source for item
text and response-scale anchors, cross-checked against the dataset's own OSF repository
(`data-clean/normdat-labels.csv`, a related norming-study codebook using the same BFI-2
item numbering) and this repo's existing `data/sun_2025_morality.do` processing script
(for the `itbfi2<NN>` variable-naming convention only, not for item text itself, since the
.do file contains no item text or labels).

## Ambiguities / items not extracted
None -- both ground-truth items were extracted and mapped with two-source confirmation;
validated exact item/resp set match against the cached ground truth
(`.gt_sun_2025_morality_study1_dependability.rds`). No entry needed in
`pending_index_notes.csv` for this table.
