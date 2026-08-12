# Extraction log: paampsmartsud_saba_2023_pacs

## has_bare_integer_items
FALSE, as given in the dictionary row. Ground-truth `item` values are already
semantic codes (`PACS_1_POST`...`PACS_5_POST`), not bare integers. However,
the mapping of which specific PACS_# code corresponds to which of the
instrument's 5 standard questions (frequency/intensity/duration/resistance/
overall) still had to be inferred from the fixed, always-administered PACS
item order — see "Derived vs. directly-read values" below, since (unlike the
sibling `paampsmartsud_saba_2023_amps` table) no subscale-sum cross-check was
possible here to empirically confirm it.

## What "PACS" turned out to mean
**Penn Alcohol Craving Scale** (Flannery, Volpicelli, & Pettinati, 1999) —
*not* "Perceived Ability to Cope with Stress" as speculatively floated in the
task prompt, and not strictly alcohol-only in this application. The applied
paper (Saba & Black, 2024, *Mindfulness*, DOI 10.1007/s12671-023-02144-1)
states explicitly: "While the original PACS targets alcohol use cravings, we
revise the wording to also capture cravings for other drugs" — consistent
with the population (residential SUD treatment, not alcohol-specific) and
with the `cov_AUD_SUD_DIAGNOSES` covariate in the raw data showing e.g. "drug
use disorder" alongside alcohol-related codes.

## Source used
- Target paper: Saba, S. K., & Black, D. S. (2024). Same paper as the sibling
  `paampsmartsud_saba_2023_amps` table (open-access full text at PMC12959836,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC12959836/). The PACS is described
  in the paper's own Measures section (a different subsection than the AMPS
  description used for the sibling table).
- OSF project (https://osf.io/9jgxs/) raw data, reused from the sibling
  table's cache: `.cache/paampsmartsud_saba_2023_amps/amps_data.csv`. This
  file's header confirms `PACS_1_POST`..`PACS_5_POST` (and `PACS_1_BASELINE`..
  `PACS_5_BASELINE`, `PACS_MEAN_POST`, `PACS_MEAN_BASELINE`, not part of this
  table's ground truth) alongside the AMPS/FFMQ/PSS columns. No PACS-specific
  codebook, variable-label file, or supplementary questionnaire document was
  found on the OSF page — only the raw wide CSV.
- No table/appendix in PMC12959836 lists all 5 PACS items; the paper gives
  only 2 items as inline examples (quoted below) plus the response-scale
  description.
- Standard (published, unmodified/alcohol-only) PACS item wording and item
  order were checked against secondary sources (ARC-Wisconsin self-report
  measure page, NovoPsych PACS summary) to confirm the instrument's fixed
  5-item sequence (1=frequency, 2=intensity, 3=duration, 4=resistance,
  5=overall rating) — these sources describe the item content/order
  qualitatively but neither reproduces full verbatim item text with response
  anchors for all 5 items, so they were used only to confirm ordering, not as
  a source of quoted item_text.

## Source type used
Web-rendered full-text HTML (via WebFetch) of the open-access PMC article
(PMC12959836), plus two secondary web pages (ARC-Wisconsin, NovoPsych) used
only to confirm the instrument's standard item ordering, not for quoted text.
No PDF or scanned image was used. No OCR was involved (see next section).

## OCR / image-based extraction
None. All text used (response-scale description, the two example items) was
read directly from PMC's HTML article rendering.

## Derived vs. directly-read values
- **Directly read, verbatim, from the applied paper (Saba & Black, 2024)**:
  - Response-scale framing: "rate each item on a 7-point Likert scale from 0
    *none/never* to 6 *unable to resist/all the time*" — recorded in
    `instructions` (paraphrased down to a terse instruction sentence,
    following the sessionB model's own paraphrase-level terseness) and the
    endpoint anchors recorded as `option_text` for resp 0 and resp 6 only.
  - Two example items, quoted directly: "At its most severe point how strong
    was your craving?" and "How much time have you spent thinking about doing
    drugs or drinking?" — the paper does not attribute these to specific item
    numbers, it presents them only as "example items."
- **Derived (item-number assignment, NOT empirically confirmed)**: the two
  quoted example items were assigned to `PACS_2_POST` (intensity — "how strong
  was your craving") and `PACS_3_POST` (duration — "how much time...
  thinking") based on the PACS's standard, always-fixed published item order
  (1=frequency, 2=intensity, 3=duration, 4=resistance-to-drink, 5=overall
  rating), which is a fixed part of the instrument's administration (not
  something researchers reorder), and on the two quoted items' content
  matching the standard intensity and duration items respectively. Unlike the
  sibling AMPS table, there was no independent numeric cross-check available
  (e.g. no `PACS_MEAN_POST` decomposition that could confirm which raw items
  feed which subscale) — `PACS_MEAN_POST` is a simple mean across all 5 items
  regardless of order, so it cannot disambiguate item order. This assignment
  is treated as high-confidence but NOT independently verified, and is flagged
  below.
- **Left blank, not fabricated**: `item_text` for `PACS_1_POST`, `PACS_4_POST`,
  `PACS_5_POST` (frequency, resistance, overall-rating items) — the applied
  paper never quotes these, and the *original* (alcohol-only, pre-revision)
  published PACS wording found in secondary sources is explicitly NOT what
  was administered here, since the paper states wording was revised to
  include drugs. Using the original alcohol-only wording would misrepresent
  the actual administered item text, so these were left blank/NA rather than
  substituting the unrevised original wording. `option_text` for resp values
  1-5 (only the two endpoints, 0 and 6, are labeled anywhere in the source).
  `correct_response` left blank throughout — PACS is a self-report craving
  measure with no scoring key.

## Structure of output
Single `section_id` (`paampsmartsud_saba_2023_pacs_pacs`) covering all 5
items — PACS has no testlet/passage structure in this administration, just
one shared response-scale framing, so `section_prompt` is blank throughout
and the scale-level framing goes in `instructions` per the skill's
instructions/section_prompt boundary rule.

## Items not extracted
`item` and `resp` value sets match ground truth exactly (validated against
cached ground truth `.gt_paampsmartsud_saba_2023_pacs.rds`):
- `unique(item)` match: TRUE (5/5 — `PACS_1_POST`..`PACS_5_POST`)
- `unique(resp)` match: TRUE (0-6, integer-vs-numeric storage type only, same
  as the AMPS sibling table)

`item_text` is populated for only 2 of 5 items (`PACS_2_POST`, `PACS_3_POST`)
because the applied paper only quotes 2 example items verbatim and explicitly
revised the wording from the original published PACS, making the original
instrument's full wording an unsafe substitute. `item_text` for
`PACS_1_POST`/`PACS_4_POST`/`PACS_5_POST` is `NA`. `option_text` is populated
only for the two labeled endpoints (resp 0 and 6) of each item; resp 1-5 are
unlabeled in the source and left blank.

## Ambiguities / caveats for the human reviewer
- The `PACS_2_POST` -> intensity-item and `PACS_3_POST` -> duration-item
  assignment is inferred from the instrument's standard fixed item order, not
  independently confirmed the way the sibling AMPS table's item order was
  (via subscale-sum reconstruction). If this is wrong, `item_text` would be
  attached to the wrong `item` code. Flagged in `pending_index_notes.csv`.
- `item_text` for `PACS_1_POST`, `PACS_4_POST`, `PACS_5_POST` is blank — not
  disclosed anywhere accessible in revised (drug-inclusive) wording.
- Response-scale framing paraphrased down from the paper's descriptive Methods
  prose ("the five-item scale asks participants to rate each item on a
  7-point Likert scale...") to a terse instruction sentence, since the source
  text is written as third-person scale description for readers rather than
  a verbatim first/second-person participant instruction — matches the
  approach used for `firstborn_personality`'s instructions field.
