# Extraction log: sv-maia2_randelovic_2021_maia

## Source used
Ground truth (`.gt_sv_maia2_randelovic_2021_maia.rds`) has `item` values `MAIA2_1`..
`MAIA2_37` (37 distinct, already semantically labeled — no bare-integer reconstruction
needed) and `resp` values `0,1,2,3,4,5` (6-point, 0-5).

Followed the same navigation pattern established for the `sv-maia2_randelovic_2021_erq`
and `_hexaco60` sibling tables in this batch: the root OSF project `osf.io/em3wf` has no
top-level files, but has four child components (`txn2y` Data and analytic scripts, `u2m7p`
Supplemental material, `vrhdu` Method, `brehn` Preregistration). The "Method" component
(`osf.io/vrhdu`) contains `Serbian validation of MAIA2 Materials.pdf`, which lists every
questionnaire used in the study with a direct link to its instrument record. For
"Interoceptive awareness" it states:

> Multidimensional Assessment of Interoceptive Awareness-2 (MAIA2, Mehling et al., 2018)
> https://osf.io/tpn6u/

Queried `osf.io/tpn6u`'s files via the OSF v2 API and found `maia2_sr_eng_srp.odt`/`.pdf`
— a REPOPSI (Repository of Psychological Instruments in Serbian) instrument record
containing the full English original and Serbian translation, including instructions,
the complete 37-item text, response-scale description, and the official 8-subscale
scoring key. Cached at
`itemtext/.cache/sv-maia2_randelovic_2021_maia/maia2_sr_eng_srp.pdf` (also `.odt`,
`Metadata_MAIA-2_self-report.xml`, and the "Method" materials list PDF
`maia2_materials.pdf`/`.txt`). Extracted via `pdftotext -layout`.

This is a directly-linked record from the study's own OSF Method-component materials
(not a generic publisher-site fallback), so treated as the strongest tier of source
evidence — same tier as the `_erq` sibling's REPOPSI record. Because MAIA-2 is this
paper's own focal/named instrument, the REPOPSI record's numeric item ordering (1-37)
was cross-checked against the standard published Mehling et al. (2018) MAIA-2 item order
and subscale grouping (also reproduced in the same record's "Instrument in full -
Original" English block) — they match exactly, so the `MAIA2_N` -> item-N mapping is a
direct 1:1 read, not a positional inference.

I did not need to fall back to the official osher.ucsf.edu/maia site — the REPOPSI record
already contains the verbatim Serbian translation used for this specific study (its own
"Source of the translation/adaptation" field even cites
`osher.ucsf.edu/.../maia2_serbian.pdf`, i.e. this Serbian translation is itself the
official UCSF-hosted one, just mirrored/catalogued via REPOPSI for this study's use).

## Structure of output
Eight sections, one per MAIA-2's official named subscale (per the REPOPSI record's
"Scoring keys" field, which matches the published Mehling et al. 2018 structure exactly):
`_Noticing` (items 1-4), `_NotDistracting` (5-10), `_NotWorrying` (11-15),
`_AttentionRegulation` (16-22), `_EmotionalAwareness` (23-27), `_SelfRegulation` (28-31),
`_BodyListening` (32-34), `_Trusting` (35-37). 4+6+5+7+5+4+3+3 = 37, matching the full
item count. `section_prompt` left blank for every section — the subscale grouping is a
scoring-key/factor-structure grouping, not a shared passage/testlet prompt presented to
respondents, so no distinct `section_prompt` text exists to record (consistent with the
skill's instructions/section_prompt boundary rule: this is not framing text at all, just
a structural grouping key).

`instructions` (whole-instrument framing, identical for all 37 items regardless of
subscale) is recorded once: "U nastavku je niz tvrdnji. Molimo Vas da označite koliko
često se svaka od njih uopšteno odnosi na Vas u svakodnevnom životu. Označite po jedan
broj u svakom redu." — verbatim from the record's "Instructions for participants" field,
Translation block.

## Response scale / option_text
The source states "6-stepena skala; 0 - nikad, 5 - uvek" ("6-point scale; 0 - never,
5 - always") — only the two endpoints are given verbal anchors; points 1-4 are
unlabeled numeric scale points in the source (standard for this instrument, consistent
with the published English MAIA-2 which also only labels 0 and 5). `option_text` is set
to "nikad" for resp=0 and "uvek" for resp=5, and left `NA` for resp 1-4 — did not invent
labels for the unlabeled midpoints.

## OCR / image-based extraction
None. `maia2_sr_eng_srp.pdf` is a native, text-layer PDF (not a scan) — extracted via
`pdftotext -layout` (native text-layer extraction), not OCR. Cross-checked line breaks
against the `-layout` output; no ambiguous character recognition issues (Serbian
diacritics č/ć/š/ž/đ rendered correctly).

## Derived vs. directly-read values
- **Directly read**: `instructions` (Serbian, verbatim from the REPOPSI record's
  "Instructions for participants" field, Translation block), `item_text` (Serbian,
  verbatim from the same record's numbered "Items" field, items 1-37), endpoint
  `option_text` labels ("nikad"/"uvek") from the record's "Response scale" field.
- **Derived**: `section_id` subscale assignment — derived from the record's own
  "Scoring keys" field (explicit Q-number groupings per subscale), not inferred or
  guessed; this is a direct read of an explicit key, not a positional inference.
  Numeric `item` (`MAIA2_N`) -> item-text mapping is likewise a direct 1:1 read (REPOPSI
  numbers items 1-37 in the standard published Mehling et al. 2018 order).
- `option_text` for resp 1-4 intentionally left `NA` (unlabeled scale points in the
  source) — a deliberate non-fabrication, not a missed extraction step.
- `correct_response` left blank throughout (self-report interoceptive-awareness
  questionnaire, no right-or-wrong scoring key).

## Source type used
Study-specific OSF materials record: REPOPSI instrument entry (`osf.io/tpn6u`) directly
linked from this study's own "Method" OSF component materials PDF (`osf.io/vrhdu`).
Same strongest tier as the `_erq` sibling's REPOPSI-record extraction (both reached via
the "Method" component's materials list, not a generic publisher fallback). No fallback
to the official osher.ucsf.edu MAIA-2 site was needed since the REPOPSI record already
contains — and cites as its own source — that same official Serbian translation.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` ("items already have semantic
labels"). Confirmed: ground truth `item` values are `MAIA2_N` (semantic/named codes tied
directly to the instrument's own published item numbering, not bare integers), so Step
4's bare-integer reconstruction procedure did not apply here — the `MAIA2_N` -> item-N
mapping is a direct read, not a positional inference.

## Validation
`sort(unique(candidate$item))` == `sort(unique(gt$item))`: TRUE (exact, all 37 items,
`MAIA2_1`..`MAIA2_37`).
`sort(unique(candidate$resp))` == `sort(unique(gt$resp))`: TRUE (exact, 0-5, both
`numeric`).

## Items not extracted
None — `item_text` recovered for all 37 ground-truth items, and `section_id` subscale
grouping recovered for all 37 as well, from an explicit scoring-key field (not inferred).
The only incomplete field is `option_text` for the four unlabeled midpoint scale values
(1-4), which is a deliberate non-fabrication decision matching the source material
exactly, not a coverage gap.
