# Extraction log: suicide_reinbergs_2025_phq

## has_bare_integer_items
FALSE, confirmed. Ground-truth `item` values are already semantic codes (`phq01`..`phq09`),
not bare integers, so no positional reconstruction from item numbering was needed — the
mapping from `item` code to instrument position is unambiguous from the code itself
(`phqNN` = PHQ-9 item NN).

## Source used
The dictionary row's "URL (for data)" (`https://osf.io/f5qgm/files/4dwr5`) turned out to
resolve, via the OSF API, to `mdss-data-public.Rds` — a raw analysis data file for a
companion project ("Modified Depression Stigma Scale", same OSF node `f5qgm`), not an
instrument/appendix document. Its `haven_labelled` variable/value-label metadata was
checked (see below) but does not contain literal item-stem text.

The primary source actually used for `item_text`/`instructions`/`option_text` content is
the **preprint PDF itself**, fetched via the DOI (`10.31219/osf.io/3vd9f_v1` → OSF
preprint node `3vd9f` → primary file → `https://osf.io/download/3vd9f_v1/`), cached at
`.cache/suicide_reinbergs_2025_phq/preprint.pdf` (text-extracted to `preprint.txt` via
`pdftotext -layout`, a real text-layer PDF — no OCR needed, see below).

## Source type used
- Preprint PDF (text layer, machine-readable) — primary source for the "Mental Health
  Measures / PHQ-9" paragraph confirming instrument identity, item count, and response
  scale.
- OSF companion data file (`mdss-data-public.Rds`, `haven_labelled` metadata) — secondary
  source, used only to cross-check the response-scale wording and value coding, not for
  item-stem text (it doesn't have any).
- Canonical published PHQ-9 item text (Kroenke, Spitzer, & Williams, 2001) — used for the
  9 individual `item_text` stems themselves, since neither the preprint nor its OSF data
  companion reprints the literal item wording (see "Derived vs. directly-read" below).

## OCR / image-based extraction
None needed. `preprint.pdf` is a normal text-layer PDF (`pdftotext -layout` extracted
clean text directly, confirmed by grepping "PHQ" and getting readable prose, not garbage
characters).

## What the preprint itself confirms (verbatim, p.8, "Mental Health Measures" section)
> "Patient Health Questionnaire–9 (PHQ-9). The PHQ-9 (Kroenke et al., 2001) assesses
> participants' depression symptoms (e.g., fatigue, appetite, feeling like a failure,
> feeling hopeless, and other symptoms of depression) in the past two weeks. The PHQ-9
> consists of nine items rated on a 4-point Likert scale ranging from 0 (Not at all) to 3
> (Nearly every day)."

This confirms: (a) instrument is the standard, unmodified PHQ-9 — cited to its original
publication with no language suggesting altered/adapted wording; (b) 9 items; (c) 4-point
scale, response values **0=Not at all, 1=Several days(implied), ..., 3=Nearly every day**
— matching the ground-truth `resp` set `{0,1,2,3}` exactly (as opposed to the OSF data
file's `haven_labelled` value-label metadata, which lists labels against values 1-4 —
almost certainly a leftover Stata-export label-position artifact, since the actual stored
values in `mdss-data-public.Rds$phq01..09` are 0-3, matching both the paper's stated
scoring and the ground truth).

## Derived vs. directly-read values
- `instructions` ("Over the last 2 weeks, how often have you been bothered by any of the
  following problems?") and the 4 `option_text` values (Not at all / Several days / More
  than half the days / Nearly every day) are the **standard published PHQ-9 stem and
  response-scale wording** (Kroenke et al., 2001) — directly corroborated by (a) the
  paper's own paraphrase/citation (0="Not at all" ... 3="Nearly every day", verbatim
  quoted above) and (b) the OSF companion data file's variable label, which reads
  (truncated at 40 chars by Stata's export format) "Over the last 2 weeks, how often have
  you been bothered by any of the following" — an exact prefix match. Not directly quoted
  from a reprinted instrument block in either source (neither reprints a full item block),
  so treated as **derived-but-verified** rather than directly transcribed.
- The 9 `item_text` stems (little interest/pleasure, feeling down, sleep, energy,
  appetite, feeling bad about self, concentration, psychomotor, thoughts of
  death/self-harm) are the **canonical published PHQ-9 item text** — neither the preprint
  nor the OSF data file reprints the individual item stems (the paper only lists example
  symptom categories in prose: "fatigue, appetite, feeling like a failure, feeling
  hopeless"). These stems were not found verbatim in either source document for this
  table and are reconstructed from the well-documented, publicly available PHQ-9
  instrument (freely usable, no license fee, developed by Spitzer/Kroenke/Williams for
  Pfizer, in wide public/clinical use) rather than directly read from this study's own
  materials. This is flagged here per the task's "do not guess/fabricate item text
  without noting it" instruction — order/count/response-scale identity with the standard
  PHQ-9 was verified directly against this study's own sources (paper + OSF data), but the
  literal item-stem wording itself is carried over from the canonical instrument rather
  than confirmed word-for-word against this specific paper's own reprint (it doesn't
  provide one).
- `correct_response` left blank throughout — PHQ-9 is a symptom-severity screener with no
  scored "correct" answer per item.
- `section_id` — no testlet/passage grouping in this instrument; used a single trivial
  `suicide_reinbergs_2025_phq_1` for all 9 items with blank `section_prompt`, per
  `itemtext_standard.md`.

## Validation
`unique(item)`: exact match (`phq01`..`phq09`, both ground truth and candidate, N=9).
`unique(resp)`: exact match (`{0,1,2,3}`, both ground truth and candidate, N=4) — resp
type differs (ground truth `numeric`/double vs. candidate `integer`) but values are
identical; not a real discrepancy.

## Items not extracted
None — all 9 ground-truth items and all 4 resp values covered. No partial coverage.
