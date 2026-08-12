# Extraction log: mpsycho_ceaq

## Source used
The dictionary URL (for data) is the CRAN landing page for the `MPsychoR` R package
(https://cran.r-project.org/web/packages/MPsychoR/index.html), which contains the `CEAQ`
dataset used by the source paper (Funk, Fox, Chang, & Curtiss, 2008, Journal of Applied
Developmental Psychology). MPsychoR was already installed locally (`library(MPsychoR)`
succeeds). Following the same successful pattern as `mpsycho_rmotivation`, the `?CEAQ`
help page was fetched via `tools::Rd_db("MPsychoR")` / `Rd2txt()` and cached at
`.cache/mpsycho_ceaq/CEAQ_help.txt`.

That help page's `Format` section gives literal item wording for all 16 items under
headers `ceaq1`...`ceaq16` (e.g. `ceaq1`: "When I'm mean to someone, I usually feel bad
about it later."), plus the instrument description ("The CEAQ (Funk et al., 2008) is a
scale to measure empathy of late elementary and middle-school aged children.") and the
Source citation matching the dictionary's Reference/DOI exactly.

The published paper itself (ScienceDirect, doi:10.1016/j.appdev.2008.02.005) is
paywalled -- only the abstract/landing page was reachable (WebFetch returned 403 on the
ResearchGate mirror; no open-access PMC/preprint copy was found). No literal
participant-facing instructions text was recovered from any reachable source, so
`instructions` was left blank (`NA`) rather than invented.

For the response-scale wording, the MPsychoR help page and the paywalled original paper
do not give literal option labels. Two independent secondary sources -- a Spanish CEAQ
validation study (Vilte et al., via TPM journal abstract and ResearchGate listing) and
general web summaries of the instrument -- consistently describe the CEAQ's response
format as three categories: "No" / "Maybe" / "Yes". This is corroborated structurally by
the live data (`MPsychoR::CEAQ` raw item columns and the ground-truth `resp` set both
take exactly the values 1/2/3, consistent with a 3-point ordinal scale), but the
"No"/"Maybe"/"Yes" wording itself is a **derived/secondary-source value, not verified
against the original 2008 paper's own text** (which was not accessible). Mapped ascending
1=No, 2=Maybe, 3=Yes, the natural ordinal reading for an empathy-endorsement item.

## Source type used
- Item text (`item_text`, all 16 items): R package documentation (`?CEAQ` help page,
  verbatim, packaged by MPsychoR's author P. Mair, citing the same Funk et al. 2008
  paper as the dictionary Reference).
- Response-option wording (`option_text`, "No"/"Maybe"/"Yes"): secondary sources
  (independent validation-study abstracts/summaries), not the primary paper -- primary
  paper was paywalled and no open-access copy was found. Flagged as derived, not directly
  read, per Step 4's terseness/literalness standard.
- `instructions`: not recoverable from any reachable source; left `NA`.
- No OCR was involved -- both the R help page and the secondary web sources were
  machine-readable text.

## OCR / image-based extraction
Not applicable. No scanned images, PDFs requiring OCR, or screenshots were used. The
`CEAQ_help.txt` cache is a plain-text R help page (`Rd`-rendered via `Rd2txt()`), and all
web sources consulted were rendered HTML/text, not scanned documents.

## Derived vs. directly-read values
- `item_text` for all 16 items: directly read, verbatim, from the MPsychoR help page's
  `Format` section (not derived/inferred). Item labels (`ceaq1`..`ceaq16`) matched
  ground-truth `item` values by direct string equality -- `has_bare_integer_items` is
  FALSE per the dictionary row, confirmed (all 16 ground-truth items are the semantic
  codes `ceaq1`..`ceaq16`, not bare integers), so no position/order reconstruction was
  needed.
- `instrument`: directly read from the help page's title/Description ("Children's
  Empathic Attitudes Questionnaire (CEAQ)").
- `instructions`: left `NA` -- no literal instructions text was found in any reachable
  source (package doc or paper abstract).
- `section_id`: derived, not source text -- a single trivial `mpsycho_ceaq_1` grouping
  for all 16 items (no testlet/passage structure disclosed; CEAQ is a single unidimensional
  scale per the help page and paper title). `section_prompt` left blank for all rows.
- `option_text` ("No"/"Maybe"/"Yes"): **derived from secondary sources**, not directly
  read from the primary 2008 paper (paywalled, not accessible). Corroborated by two
  independent secondary descriptions of the instrument and consistent with the live
  data's 1/2/3 resp range, but should be treated as lower-confidence than the item_text.
- `correct_response`: left blank for all items -- this is an attitude/empathy self-report
  scale with no scoring key.

## has_bare_integer_items
FALSE, per the dictionary row, and confirmed: all 16 ground-truth `item` values are
semantic codes (`ceaq1`..`ceaq16`), not bare integers. No reconstruction of item-to-
position mapping was needed -- the MPsychoR help page documents `item_text` directly
under a header matching each `item` code exactly, so item labels were matched to text by
direct string equality, not by inferred ordering/position.

## Items not extracted
None -- all 16 ground-truth items were extracted (item_text) and validated.

## Discrepancy / lower-confidence flag (logged per Step 6b)
`option_text` ("No"/"Maybe"/"Yes") is sourced from secondary/corroborating references,
not the primary Funk et al. (2008) paper itself, which was paywalled with no accessible
open-access copy found. `item_text` and `item`/`resp` are fully confirmed from the
primary source (MPsychoR package, packaged by the CEAQ data's own maintainer). Logged in
`pending_index_notes.csv`.

## Validation result
Exact match: `unique(candidate$item)` == `unique(ground truth$item)` (16 items,
`ceaq1`..`ceaq16`) and `unique(candidate$resp)` == `unique(ground truth$resp)` (`1`, `2`,
`3`). Output written as `candidate_mpsycho_ceaq.rds`, one row per (item, resp) -- 16
items x 3 resp values = 48 rows.
