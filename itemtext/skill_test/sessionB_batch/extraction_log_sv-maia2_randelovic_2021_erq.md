# Extraction log: sv-maia2_randelovic_2021_erq

## Source used
Ground truth (`.gt_sv_maia2_randelovic_2021_erq.rds`) has `item` values `ERQ_1`..`ERQ_10`
(10 distinct, already semantically labeled — no bare-integer reconstruction needed) and
`resp` values `1,2,3,4,5` (5-point).

Following the same pattern used for the `sv-maia2_randelovic_2021_delta` sibling table in
this batch: the root OSF project `osf.io/em3wf` has no top-level files, but a "Method"
child component (`osf.io/vrhdu`) contains `Serbian validation of MAIA2 Materials.pdf`,
which lists every questionnaire used in the study with a direct link to its instrument
record. For "Emotion regulation," that materials PDF states:

> Emotion Regulation Questionnaire (ERQ, Gross & John, 2003) https://osf.io/fdpc2/

Queried `osf.io/fdpc2`'s files via the OSF v2 API and found `erq_eng_srp.odt` — a REPOPSI
(Repository of Psychological Instruments in Serbian) instrument record containing the full
English original and Serbian translation/adaptation (by Goran Knežević, 2021 — the same
year/translator context as this study), including instructions, the complete 10-item text,
and the reappraisal/suppression scoring key. Cached at
`itemtext/.cache/sv-maia2_randelovic_2021_erq/erq_eng_srp.odt` (and `erq.txt`, the
pandoc-converted plain text used for extraction).

This is a directly-linked record from the study's own OSF materials (not a generic
publisher-site fallback), so treated as strong, study-specific evidence for `instructions`
and Serbian `item_text`. Numeric mapping `ERQ_N` -> REPOPSI item `N` is a direct 1:1 read
(REPOPSI lists items 1-10 in the standard Gross & John published order — no positional
inference required, unlike a bare-integer case).

## Key discrepancy: response-scale point count (5 vs. 7)
The REPOPSI record's "Response scale" field for both the English and Serbian versions
states a **7-point** scale (`1 -- strongly disagree ... 4 -- neutral ... 7 -- strongly
agree` / `1 -- uopšte se ne slažem ... 4 -- neutralan/na sam ... 7 -- u potpunosti se
slažem`), matching the standard published Gross & John (2003) ERQ. But the live ground
truth for this table has only **5** distinct `resp` values (1-5), not 7. This means the
study as actually administered (or as coded into this IRW table) used a modified 5-point
response scale, which is not documented anywhere in the retrieved source material (paper,
OSF materials PDF, or the REPOPSI instrument record all describe the item stems only —
none of them documents a 5-point variant of the ERQ response scale for this study).

Per the "do not guess/fabricate" instruction, `option_text` is left blank (`NA`) for all
50 rows rather than inventing anchor wording for an unconfirmed 5-point scale (e.g.
guessing 1/3/5-anchor labels by analogy to the 7-point original) — the numeric `resp`
values (1-5) themselves are taken directly from ground truth per the skill's rule, but the
verbal option text tied to that numbering is not recoverable from any source found. This
row is appended to `pending_index_notes.csv`.

## Structure of output
Single flat section (`sv-maia2_randelovic_2021_erq_1`) for all 10 items, `section_prompt`
blank — same reasoning as the `hexaco60` sibling table: reappraisal/suppression is a
scoring-key/subscale grouping (items 1,3,5,7,8,10 = Reappraisal; 2,4,6,9 = Suppression, per
REPOPSI's own scoring-key field), not a testlet with shared framing/passage text presented
to respondents, so it does not qualify for `section_id`/`section_prompt` splitting per the
skill's rule.

## OCR / image-based extraction
None. `erq_eng_srp.odt` is a native OpenDocument Text file (structured table, not a scan);
extracted via `pandoc erq_eng_srp.odt -o erq.txt` (native XML/text extraction), not OCR.

## Derived vs. directly-read values
- **Directly read**: `instructions` (Serbian, verbatim from the REPOPSI record's
  "Instructions for participants" field, Translation/Adaptation block), `item_text`
  (Serbian, verbatim from the same record's numbered "Items" field, items 1-10).
- **Derived**: numeric `item` (`ERQ_N`) -> item-text mapping is a direct 1:1 read by
  number (REPOPSI lists items 1-10 in the standard published order), not an inference —
  no positional/order guessing was needed since the ground truth already uses
  semantically-numbered labels (`ERQ_N`) that align with the source document's own item
  numbering.
- `option_text` intentionally left blank/`NA` for every row — see discrepancy section
  above. This is a deliberate omission of unconfirmed text, not a missed extraction step.
- `correct_response` left blank throughout (personality/trait self-report questionnaire,
  no right-or-wrong scoring key).

## Source type used
Study-specific OSF materials record (REPOPSI instrument entry directly linked from this
study's own "Method" component materials PDF, `osf.io/fdpc2`), not a generic
publisher/copyright-holder fallback. This is the strongest tier of source used across this
batch's `sv-maia2_randelovic_2021_*` siblings (matches the pattern already established for
`_delta`, distinct from `_hexaco60`, which had to fall back to the instrument's own
publisher site because the OSF `_hexaco60` link had no retrievable content).

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` ("items already have semantic
labels"). Confirmed: ground truth `item` values are `ERQ_N` (semantic/named codes tied
directly to the instrument's own published item numbering, not bare integers), so Step 4's
bare-integer reconstruction procedure did not apply here — the `ERQ_N` -> item-N mapping
is a direct read, not a positional inference.

## Validation
`sort(unique(candidate$item))` == `sort(unique(gt$item))`: TRUE (exact, all 10 items,
`ERQ_1`..`ERQ_10`).
`sort(unique(candidate$resp))` == `sort(unique(gt$resp))`: TRUE (exact, 1-5, both
`numeric`).

## Items not extracted
None — `item_text` recovered for all 10 ground-truth items. The only incomplete field is
`option_text` (blank for all rows), which is a deliberate non-fabrication decision, not a
coverage gap in item identification.
