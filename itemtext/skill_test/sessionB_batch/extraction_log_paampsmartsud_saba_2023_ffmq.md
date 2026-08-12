# Extraction log: paampsmartsud_saba_2023_ffmq

## has_bare_integer_items
FALSE, as given in the dictionary row. Ground-truth `item` values are named
codes (`FFMQ_1_POST`...`FFMQ_25_POST`, skipping `FFMQ_23_POST` -- 24 of a
25-numbered set), not bare integers, so this isn't the bare-integer case
described in the skill in the strict sense. In practice, though, the
per-item mapping problem is identical: the numeric suffix is a raw survey
question index with no disclosed correspondence to a specific FFMQ item's
wording, so item-level text still could not be safely assigned (see
"Ambiguities" below).

## Source used
- Target paper: Saba, S. K., & Black, D. S. (2023/2024). "Psychometric
  Assessment of the Applied Mindfulness Process Scale (AMPS) Among a Sample
  in Residential Treatment for Substance Use Disorder." *Mindfulness*. DOI
  10.1007/s12671-023-02144-1. Open-access full text at PMC12959836
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC12959836/), same paper already
  used for the sibling `paampsmartsud_saba_2023_amps` table (AMPS is the
  primary instrument in this paper; FFMQ-24 is used there only as a
  convergent-validity measure).
- The paper states (quoted): "A self-report measure to quantify an
  individual's tendency to be mindful in daily life over a 30-day period
  (Bohlmeijer et al., 2011). The 24-item measure asks participants to rate
  items on a 5-point Likert scale from 1 *never or very rarely true* to 5
  *very often or always true*." This confirms: (a) the instrument is the
  24-item FFMQ short form (FFMQ-24 / FFMQ-SF), (b) its source citation is
  Bohlmeijer, E., ten Klooster, P. M., Fledderus, M., Veehof, M., & Baer,
  R. A. (2011). "Psychometric Properties of the Five Facet Mindfulness
  Questionnaire in Depressed Adults and Development of a Short Form."
  *Assessment*, 18(3), 308-320, and (c) the two disclosed response-scale
  endpoint labels.
- OSF project (https://osf.io/9jgxs/) raw data, reused from the sibling
  AMPS table's cache (`.cache/paampsmartsud_saba_2023_amps/amps_data.csv`,
  the same file covers both instruments) contains `FFMQ_1_POST` through
  `FFMQ_25_POST` (skipping `FFMQ_23_POST`) and parallel `_BASELINE` columns,
  plus `FFMQ_SUM_POST`/`FFMQ_SUM_BASELINE` totals only -- no per-facet
  (Observing/Describing/Nonjudging/Nonreactivity/Acting-with-Awareness) sum
  columns, unlike the AMPS file's `_SUM` columns for its three subscales.
  This matters: it is what made the AMPS item-order mapping empirically
  verifiable (reconstructing subscale sums from named `AMPS_##` columns) but
  leaves the FFMQ item order **unverifiable** the same way -- see
  "Ambiguities" below.
- Full text of the Bohlmeijer et al. (2011) source paper (paywalled at
  SagePub, `10.1177/1073191111408231`) could not be retrieved -- SagePub,
  ResearchGate, and Academia.edu full-text pages all returned 403/paywall
  responses to WebFetch. Secondary sources were checked instead (see below).

## Source type used
Web-rendered full-text HTML (via WebFetch) of the applied paper (PMC12959836)
for the instrument description/response-scale text, plus a cached PDF
("In This Moment" FFMQ-SF/FFMQ handout, Strosahl & Robinson / New Harbinger,
reproducing both the Baer et al. 2006 39-item FFMQ and a renumbered-1-24
FFMQ-SF) and several web searches attempting to locate the Bohlmeijer et al.
(2011) original-item-number-to-FFMQ-24-item mapping. None of the secondary
sources checked gave a mapping that was both internally consistent (correct
facet item counts: Observing=4, Describing=5, Nonjudging=5,
Nonreactivity=5, Acting-with-Awareness=5, total=24) and directly
attributable to the primary Bohlmeijer et al. (2011) table -- one
AI-summarized web-search result explicitly contradicted a plausible-looking
hypothesis (that `FFMQ_1`..`FFMQ_25`\{-23\} follows the original Baer et al.
2006 1-39 item numbering), and another summarized source produced a
5-facet item count (6+6+6+5+6=29) that is internally inconsistent with the
known 24-item total, indicating a hallucinated/unreliable extraction from
that source's search snippet. No literal item wording could be assigned
to a specific `FFMQ_<n>_POST` code with any confidence as a result.

## OCR / image-based extraction
None. All text used (the applied paper's instrument description and
response-scale endpoint labels) was read directly from PMC's HTML article
rendering. The "In This Moment" FFMQ-SF/FFMQ handout was read as a
digitally-generated (non-scanned) PDF, not OCR'd, but ultimately was **not**
used as a source for any field in the final output (see Ambiguities) because
its FFMQ-SF item numbering (1-24, its own presentation order) and its
full-length FFMQ item numbering (1-39, Baer et al. 2006 original) are two
different, non-interchangeable schemes, and neither could be confirmed to
match this dataset's `FFMQ_<n>_POST` numbering.

## Derived vs. directly-read values
- **Directly read, verbatim, from the applied paper (Saba & Black)**:
  instrument identity ("24-item measure," citing Bohlmeijer et al. 2011),
  and the two response-scale endpoint labels ("never or very rarely true"
  for the low end, "very often or always true" for the high end).
- **Not attempted / explicitly left blank**: `item_text` for all 24 items,
  and `option_text` for the three interior scale points (resp 2/3/4). See
  Ambiguities below for why.
- **Nothing was derived by inference/reconstruction** for this table (unlike
  the sibling AMPS table, where subscale-sum arithmetic empirically
  confirmed an item-number mapping) -- the FFMQ raw data has no per-facet
  sum columns to check a hypothesized mapping against, so no such check was
  possible here.

## Structure of output
Single `section_id` (`paampsmartsud_saba_2023_ffmq_ffmq`) covering all 24
items -- no testlet/passage structure, `section_prompt` blank throughout,
whole-instrument framing in `instructions` per the skill's
instructions/section_prompt boundary rule.

## Items not extracted
`item_text` is blank (`NA`) for all 24 ground-truth items
(`FFMQ_1_POST`-`FFMQ_22_POST`, `FFMQ_24_POST`, `FFMQ_25_POST`). `item` and
`resp` value sets match ground truth exactly:
- `unique(item)` match: TRUE (24/24, including exact `_POST` suffix)
- `unique(resp)` match: TRUE (1/2/3/4/5)
`option_text` is populated only for the two disclosed endpoints (resp 1 and
resp 5); resp 2/3/4 are blank.

## Ambiguities / caveats for the human reviewer
- **Core issue**: the ground-truth `item` codes are `FFMQ_1_POST` through
  `FFMQ_25_POST`, skipping `FFMQ_23_POST` (24 of a 25-numbered set). This
  numbering does **not** obviously correspond to the original 39-item FFMQ
  (Baer et al., 2006) item numbering that secondary sources use to describe
  which items Bohlmeijer et al. (2011) retained for the FFMQ-24/FFMQ-SF --
  the true FFMQ-24 selection draws items spread across the full 1-39 range
  (e.g., published facet-membership lists cited in IRT-analysis papers on
  the FFMQ short forms place several retained items above item 25), so a
  numbering confined to 1-25 cannot be that original numbering. It is more
  likely the *study's own* internal/Qualtrics-style sequential numbering of
  the 24-25 questions as administered in this particular survey, with
  `FFMQ_23_POST` apparently dropped from the exported data (reason
  unknown -- possibly a duplicate/attention-check question, a data-quality
  exclusion, or an artifact of how the platform assigned question numbers).
  No supplement, codebook, or appendix disclosing this study's actual
  on-screen item order was found (same access problem as the sibling AMPS
  table -- OSF hosts only the raw CSV, no instrument document; the paper's
  supplemental material link was previously confirmed inaccessible for
  AMPS, and no separate FFMQ-specific supplement was found either).
- Per the skill's explicit guidance ("If the mapping is genuinely ambiguous,
  say so and log it... rather than guessing"), `item_text` was left blank
  for all 24 items rather than assigning specific Bohlmeijer/Baer item
  wording to specific `FFMQ_<n>_POST` codes on an unverified guess.
- `instructions` is populated from the applied (Saba 2023) paper's own
  narrative description of the measure, which reads as a paraphrase/summary
  sentence describing the instrument rather than necessarily the literal
  on-screen instructions text shown to participants -- flagged here as a
  paraphrase-vs-literal uncertainty, though it is the only instructions-like
  text available from any source checked.
- Interior response-scale labels (resp 2, 3, 4) are left blank because the
  applied paper discloses only the two endpoints; standard FFMQ
  interior-point wording ("not often true" / "sometimes true, sometimes not
  true" / "often true") appears in secondary handout sources but was not
  confirmed against the primary Bohlmeijer et al. (2011) or Saba et al.
  paper text, so it was not used, consistent with the AMPS table's
  no-labels-when-not-disclosed precedent for interior Likert points.

This is logged in `pending_index_notes.csv` for the human reviewer to paste
into Sheet1's NOTES column.
