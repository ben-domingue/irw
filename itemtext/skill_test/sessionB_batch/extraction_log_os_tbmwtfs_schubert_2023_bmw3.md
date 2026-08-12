# Extraction log: os_tbmwtfs_schubert_2023_bmw3

## Source used
This is the BMW-3 scale-development paper's own OSF "Online Supplement"
(https://osf.io/mxn3v/, DOI 10.3758/s13428-024-02500-6). The OSF project's
`osfstorage` root contains a file literally named `supplementary material.pdf`
(cached at `.cache/os_tbmwtfs_schubert_2023_bmw3/supplementary_material.pdf`,
fetched via the OSF v2 files API + direct download link, since the OSF project
page itself is JS-rendered and not scrapeable via a plain page fetch). That PDF
is Table S1, the **original German items** with their internal codes (UI-MW
1-4, I-MW 1-4, MA-MW 1-4), plus Figures S1/S2 confirming the same three-letter
prefixes map onto the live data's `BMW3_UN_`, `BMW3_IN_`, `BMW3_ME_` item
codes (Figure captions spell this out explicitly: "BMW3_UN: Unintentional Mind
Wandering scale... BMW3_IN: Intentional Mind Wandering scale... BMW_ME:
Meta-Awareness of Mind Wandering scale").

The **English item wording** was not in the OSF supplement (German-only)
but is disclosed in Table 2 of the main paper itself (open access via PMC,
PMC11525255, cached HTML at
`.cache/os_tbmwtfs_schubert_2023_bmw3/pmc_fulltext.html`), which gives
"English item translations" side-by-side with German means/loadings, in the
same UI-MW/I-MW/MA-MW 1-4 order as Table S1. Cross-checked the German Table S1
wording against the English Table 2 wording item-by-item (same order, same
content) to confirm the mapping — e.g. UI-MW 1 German "Während ich einen
Vortrag höre, wandern meine Gedanken ohne mein Zutun zu anderen Dingen." lines
up with English "While listening to a presentation, my thoughts start to
trail off unintentionally."

## Source type used
Primary source paper HTML full text (PMC open-access mirror) for the English
12-item wording, instructions text, and response-scale labels (Table 2 +
Methods/Material section). Primary source's own OSF-hosted supplementary PDF
for confirming the UN/IN/ME <-> UI-MW/I-MW/MA-MW code correspondence and item
order (Table S1, Figures S1-S2). No OCR was needed — both were machine-
readable text (PMC HTML markup stripped to plain text; the supplementary PDF
was read directly, also machine-readable text, not scanned images).

## OCR / image-based extraction
None. The OSF supplementary PDF is a text-layer PDF (tables/figure captions
extracted as text, not via image OCR) and the PMC article is HTML. Figure
S1/S2 (histograms) were used only for their text captions (item-code-to-
subscale-name mapping), not for any numeric/image-derived content.

## Derived vs. directly-read values
- `item`, `resp`: directly the ground-truth values from
  `.gt_os_tbmwtfs_schubert_2023_bmw3.rds` (12 items, resp 0-4) — not
  re-derived.
- `item_text`: directly transcribed, verbatim, from Table 2 of the paper
  (English column).
- `instructions`: directly transcribed, verbatim, from the paper's Material
  section ("Participants are instructed that they will see a couple of
  statements..."). Note this is the paper's own third-person description of
  the on-screen instructions, not a screenshot of participant-facing text —
  it's the most literal disclosure available and was not further paraphrased
  or expanded.
- `option_text`: directly transcribed, verbatim, from the paper's stated
  5-point scale ("0 = fully disagree, 1 = somewhat disagree, 2 = neutral,
  3 = somewhat agree, 4 = fully agree"), applied identically to `resp` values
  0-4 for every item (the paper states this same scale is used for all
  items, not one item-specific instance).
- `section_id`: derived, not directly disclosed as such — grouped by the
  paper's own three named subscales (UN/IN/ME), matching the item code
  prefixes already present in the ground-truth `item` values. This is a
  structural inference from the paper's explicit factor structure, not a
  guess: the paper presents the scale as three named 4-item subscales
  throughout (title, abstract, Table 2, all correlation tables S2-S8).
- `section_prompt`: left blank for all three sections. No passage/testlet-
  specific framing beyond the whole-instrument instructions was found;
  recording the same instructions text in both `instructions` and
  `section_prompt` was avoided per the boundary rule.
- `correct_response`: left blank throughout — BMW-3 is an individual-
  differences trait scale with no scoring key/correct answer.

## has_bare_integer_items
FALSE, and confirmed by inspection — ground-truth `item` values are already
named codes (`BMW3_UN_01` etc.), not bare integers, so no
position/order-based reconstruction was needed for item identity. Item order
within each 4-item subscale (01-04) was still cross-checked against the
paper's Table 2 / Table S1 presentation order (which is consistent across
both German and English tables) to confirm `_01`..`_04` map onto the papers'
first-through-fourth listed item per subscale, rather than assuming it.

## Ambiguities / notes not otherwise encoded
- Two items are noted in the paper's Table 2 footnote as reverse-scored:
  MA-MW 1 (`BMW3_ME_01`, "It takes a very long time for me to notice that my
  thoughts have wandered off.") and MA-MW 3 (`BMW3_ME_03`, "It takes me a
  while before I realize that I zoned out.") — footnote states "means and SDs
  were calculated after reverse scoring." This doesn't change `item_text` or
  `option_text` (participants still see the same literal statement and
  response scale), just flagging it since there's no dedicated column in this
  schema to encode reverse-keying, same situation as `firstborn_personality`'s
  IPIP-50 reverse-keyed items.
- IN/ME/UN confirmed to stand for Intentional (mind wandering), Meta-awareness
  (of mind wandering), and Unintentional (mind wandering) respectively —
  matches the pre-supplied hint exactly.

## Items not extracted
None — all 12 ground-truth items and all 5 resp levels were extracted and
validated as an exact match against
`.gt_os_tbmwtfs_schubert_2023_bmw3.rds` (`setequal()` on both `item` and
`resp` returned TRUE). No entry needed in `pending_index_notes.csv`.
