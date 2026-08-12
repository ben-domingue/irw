# Extraction log: vcism_polish_trzcinska_2023

## has_bare_integer_items
Dictionary row marks this FALSE ("items already have semantic labels") — confirmed. Ground-truth
`item` values are `pspcsa_1`, `pspcsa_6`, `pspcsa_7`, `pspcsa_10`, `pspcsa_13`-`pspcsa_17`,
`pspcsa_20`, `pspcsa_22`, `pspcsa_23`: named codes referencing the source instrument's own item
numbers, not bare integers requiring positional reconstruction. Still had to map the codes to
literal item wording (see below), just not via the bare-integer disambiguation procedure.

## Source type used
Three sources, escalating from the OSF data record to a since-published companion paper:

1. **OSF project `k2qew`** (dictionary's URL for data) — only 2 files: `psiat_validation.sav`
   (raw data) and a metadata/README PDF (`metadane study 1.docx-2.pdf`, cached as `metadane.pdf`).
   The metadata PDF confirmed `PSPCSA` = **"The Pictorial Scale of Perceived Competence and Social
   Acceptance for Young Children"**, its Polish adaptation, with `pspcsa_1`-`pspcsa_23` as "answers
   ... enabling calculating the total score" and two subscales, `PSPCSA_competences` /
   `PSPCSA_acceptance` — but no literal item text, no questionnaire/materials file. The linked
   preregistration (`osf.io/ch574`) has `has_materials: false` — also no item text there.
2. **`data/PMT_Trzcińska_2023.R`** (this repo's own existing processing script for this table,
   found by grepping `data/` for `pspcsa`) — explains the wave 0/1 split and, critically, why only
   12 of the (apparently) 23 `pspcsa_*` columns in the .sav end up as ground-truth items: the raw
   `.sav` only actually contains columns for a 12-item subset (test_df = non-`r`-suffixed columns,
   retest_df = `r`-suffixed reverse-coded companions renamed by stripping `r`). This also explained
   the table-name origin: `VCISM_Polish_Trzcińska_2023.Rdata` — **VCISM = "Validation of Child's
   Implicit Self-esteem Measure"**, the OSF project's own working title/acronym for the psiat
   validation study, not a construct or instrument name in its own right.
3. **Trzcińska, A., Podsiadłowski, W., & Wieleszczyk, J. (2025). Development and psychometric
   properties of the short Polish version of the Pictorial Scale of Perceived Competence and Social
   Acceptance for Young Children (PSPCSA). *Current Issues in Personality Psychology, 13*(4),
   281-290. https://doi.org/10.5114/cipp/200664** — a companion paper (not the dictionary's cited
   reference, which is just the OSF DOI link; found via web search once "PSPCSA" was confirmed) by
   the same author group, describing exactly this 12-item short form. Fetched and cached as
   `.cache/vcism_polish_trzcinska_2023/cipp_paper.pdf`. Its Table 1 lists all 24 original items with
   English descriptors and **bolds the 12 retained in the short form** — these 12 item numbers
   (1, 6, 7, 10, 13, 14, 15, 16, 17, 20, 22, 23) match the ground-truth `pspcsa_N` suffixes exactly.
   Its **Supplementary materials PDF** (`.cache/vcism_polish_trzcinska_2023/supp.pdf`, linked from
   the journal page) contains the **literal Polish translation of all 24 PSPCSA items** (both
   forced-choice statements per item, with `(R)` marking the psychometric reverse-scored line) —
   this is where the `item_text` values in the candidate came from.

## What "PSPCSA" and "vcism" turned out to mean
- **PSPCSA** = Pictorial Scale of Perceived Competence and Social Acceptance for Young Children
  (Harter & Pike, 1984), a forced-choice pictorial self-report instrument for preschoolers. The
  Polish short form (Trzcińska et al., 2025) reduced the original 24-item, 4-subscale instrument to
  12 items across a 2-factor structure (**Competence** = cognitive+physical competence items;
  **Acceptance** = peer+maternal acceptance items), 6 items each — confirming the task prompt's
  hypothesis that this table is one (short-form) instrument, not literally "one subscale of a
  larger pool," though the 12 retained item numbers are indeed a non-contiguous subset of the
  original 24-item numbering.
- **vcism** = "Validation of Child's Implicit Self-esteem Measure," the OSF project's own working
  title for the parent PSIAT-validation study this PSPCSA administration was embedded in — not a
  construct/instrument acronym itself. The table's actual instrument is PSPCSA; "vcism" only
  identifies which parent study/dataset the PSPCSA administration came from.
- Item numbering non-contiguity (1, 6, 7, 10, 13-17, 20, 22, 23 out of 1-24) is exactly the
  16-item... no, 12-item selection documented in the companion paper's Table 1, not an artifact of
  a different subscale extraction.

## Structure of output
- `instrument`: full PSPCSA name + short-Polish-version citation, one value for all rows.
- `instructions`: table-wide, drawn closely from the companion paper's Study 1 "Measures"
  paragraph — describes the structured-alternative-format administration (two pictured "kinds of
  children," child picks the one more like them, then says "a lot" or "a little" like that child).
  This is the paper's own procedural description, not a verbatim interviewer script (see Ambiguity
  below) — kept close to source wording since the source itself is already fairly terse.
- `section_id`: `<table>_competence` / `<table>_acceptance`, one per subscale, matching the 6+6
  item split reported in the paper. `section_prompt` left blank for all — there is no shared
  passage/context text specific to a subscale beyond the whole-table instructions already recorded
  once in `instructions`, per the boundary rule (never duplicate the same span of text in both
  fields).
- `item_text`: literal Polish two-statement forced-choice pair, transcribed directly from the
  supplementary PDF, in the order printed there (`positive-statement / negative-statement`, though
  the printed order flips for a handful of items — preserved as printed, not normalized).
- `correct_response`: blank for all — self-perception measure, no scoring key.
- `option_text`: **left blank/NA for all rows** — see Ambiguity below, this is a deliberate
  non-fabrication, not an oversight.
- `resp`: 1-4 for every item, per the paper's explicit statement ("scored on a scale of one to
  four: 1 representing low perceived competence or acceptance and 4 representing high").

## OCR / image-based extraction
Not applicable — all source text (OSF metadata PDF, companion journal article PDF, supplementary
materials PDF) was text-layer PDF, read directly via the PDF reader tool; no OCR was needed or
performed.

## Derived vs. directly-read values
- **Directly read (literal)**: `item_text` (both Polish statement lines per item, verbatim from
  the supplementary PDF), the 12 `item` -> subscale assignments (from the paper's Table 1 bolding),
  the instrument name/citation, the 1-4 `resp` range (paper states this explicitly).
- **Derived/paraphrased (not verbatim)**: `instructions` is a close paraphrase of the paper's
  "Measures" paragraph describing the administration protocol, not a literal instructions script —
  no verbatim interviewer script was available (that lives in Harter & Pike's unpublished 1983
  "Procedural manual," which is not accessible from any source consulted here).
- **Intentionally left blank rather than derived**: `option_text`. The paper states the response
  scale runs 1 (low) to 4 (high) and describes the *procedure* ("a lot like that child" vs. "a
  little like that child") but never prints the literal verbal anchor labels a child would see or
  hear for each of the 4 scale points (no "bardzo prawda"/"trochę prawda"-type printed labels in
  either the main paper or the supplementary materials). Constructing per-item option text by
  combining the two Polish item statements with inferred "a lot/a little" qualifiers would be a
  plausible-sounding but fabricated anchor wording, which the task instructions explicitly rule
  out. Recording this as a real discrepancy below rather than guessing.

## Items not extracted
None — all 12 ground-truth items were matched to literal Polish item text and validated exactly
against `item` and `resp` in the cached ground truth (the 3 `NA` `resp` values in ground truth are
ordinary missing responses, not a distinct response category, and are not part of the `resp`
value set the schema requires matching).

## Discrepancy logged (see pending_index_notes.csv)
`option_text` is blank for all 48 rows: the source materials (OSF project, companion journal
article, and its supplementary PDF) disclose the 1-4 scoring direction and the forced-choice
administration procedure, but never print literal per-option anchor/label text for the 4 scale
points. Item-level `item_text` (both statements) and `resp` (1-4) are fully and literally sourced.
