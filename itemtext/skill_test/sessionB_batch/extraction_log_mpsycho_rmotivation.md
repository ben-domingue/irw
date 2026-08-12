# Extraction log: mpsycho_rmotivation

## Source used
The dictionary URL (for data) is the CRAN landing page for the `MPsychoR` R package
(https://cran.r-project.org/web/packages/MPsychoR/index.html), which contains the
`Rmotivation` dataset used by the source paper (Mair, Hofmann, Gruber, Zeileis, & Hornik,
2015, PNAS). MPsychoR was already installed locally (`library(MPsychoR)` succeeds); the
`?Rmotivation` help page was already cached at
`.cache/mpsycho_rmotivation/Rmotivation_help.txt` from a prior (crashed) attempt and was
reused as-is rather than re-fetched.

That help page is the primary source for `item_text`: it documents the dataset as "A data
frame with 852 individuals, 36 motivation items, and 9 covariates" and gives the literal
completion text for each of the 36 items under headers `ext1`...`ext12`, `hyb1`...`hyb19`,
`int1`...`int5`, e.g. `ext1`: "I can publish the packages in scientific journals." The
help page itself states the items "were taken from Reinholt's motivation scale and adapted
to R package authors. Each item started with 'I develop R packages, because...'" — this
stem was used as the shared `instructions` prefix.

Two cached PNAS supplementary files (`sd02.txt`, `sd03.txt`, from PMC) were present from
the earlier crashed attempt but turned out to be stale/broken fetches (both contain an
NCBI "HTTP 404 [Not Found]" HTML error page, not the actual variable-description or R-code
files) — not usable, and not re-fetched again since the MPsychoR help page already fully
covers item wording. For the participant-facing response instructions (not given in the
MPsychoR help page), the PNAS main-text full text was fetched fresh via PMC
(https://pmc.ncbi.nlm.nih.gov/articles/PMC4672828/, PMCID for
doi:10.1073/pnas.1506047112), which quotes the exact instrument framing: "Please indicate
whether you agree or disagree with the following statements! Choose the option that
slightly better represents your position!" This, combined with `resp` being binary (0/1)
in the live IRW data and in `MPsychoR::Rmotivation` itself, confirms a forced binary
agree/disagree response format (no neutral option — consistent with "slightly better
represents").

## Source type used
- Item text: R package documentation (`?Rmotivation` help page, verbatim, packaged by the
  original paper's author P. Mair with MPsychoR).
- Response-format instructions: open-access journal main text (PNAS via PMC), not a PDF.
- No OCR was involved — both sources were machine-readable text (R help `.txt` and PMC
  HTML-derived text via WebFetch).

## OCR / image-based extraction
Not applicable. No scanned images, PDFs requiring OCR, or screenshots were used. The
`Rmotivation_help.txt` cache is a plain-text R help page (`Rd`-rendered), and the PNAS
instructions quote was retrieved as rendered text from PMC's HTML full text.

## Derived vs. directly-read values
- `item_text` for all 36 items: directly read, verbatim, from the MPsychoR help page (not
  derived/inferred).
- `instructions`: directly quoted stem ("I develop R packages, because...") from the help
  page's Description field, concatenated with the directly-quoted response instructions
  from the PNAS main text. Both spans are literal source text, just from two different
  documents; concatenated into one `instructions` field since both apply to the entire
  36-item instrument, not to any item subset.
- `section_id`: derived, not source text — grouped into `mpsycho_rmotivation_ext` /
  `_hyb` / `_int` following the item-name prefixes disclosed in the help page and dataset
  documentation (Extrinsic/Hybrid/Intrinsic motivation subscales are explicitly named in
  the help page's Description: "three subscales ... that measure extrinsic (12 items),
  hybrid (19 items), and intrinsic (5 items) aspects of motivation"). `section_prompt` was
  left blank for all rows — there is no literal shared passage/context text specific to
  each subscale (the ext/hyb/int grouping is a construct label used by the researchers,
  not participant-facing text), so recording anything there would not be a literal
  transcript per the skill's "don't invent section_prompt text" guidance.
- `option_text`: derived mapping, not literal source text quoting "Disagree"/"Agree" —
  the source instructions ask participants to "indicate whether you agree or disagree",
  and given a strictly binary 0/1 coding with no neutral in the live data (confirmed via
  both the ground-truth `resp` set and `table(Rmotivation$ext1)` showing only 0/1 values
  plus NA for missing), 0 was mapped to "Disagree" and 1 to "Agree" as the natural binary
  reading of that instruction. This is a reasonable, low-ambiguity derivation (a strictly
  binary agree/disagree item can only have two options), but is flagged here as derived
  rather than a source string that literally reads "0 = Disagree, 1 = Agree".
- `correct_response`: left blank for all items — this is a motivation/personality-style
  self-report inventory with no scoring key.

## has_bare_integer_items
FALSE, per the dictionary row, and confirmed: all 36 ground-truth `item` values are
semantic codes (`ext1`..`ext12`, `hyb1`..`hyb19`, `int1`..`int5`), not bare integers. No
reconstruction of item-to-position mapping was needed — the MPsychoR help page documents
`item_text` directly under a header matching each `item` code exactly (e.g. the help
page's `‘ext1’` entry maps 1:1 onto ground-truth `item == "ext1"`), so item labels were
matched to text by direct string equality, not by inferred ordering/position.

## Items not extracted
None — all 36 ground-truth items were extracted and validated.

## Validation result
Exact match: `unique(candidate$item)` == `unique(irw_fetch-equivalent ground truth$item)`
(36 items, `ext1..ext12`, `hyb1..hyb19`, `int1..int5`) and `unique(candidate$resp)` ==
`unique(ground truth$resp)` (`0`, `1`). Output written as
`candidate_mpsycho_rmotivation.rds`, one row per (item, resp) — 36 items x 2 resp values =
72 rows.
