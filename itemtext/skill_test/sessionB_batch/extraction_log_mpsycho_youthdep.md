# Extraction log: mpsycho_youthdep

## Source type used
- Dictionary URL for data: https://cran.r-project.org/web/packages/MPsychoR/index.html (CRAN
  package; `YouthDep` dataset).
- Loaded `MPsychoR::YouthDep` directly (`data(YouthDep)`) and inspected its Rd help page
  (`tools::Rd_db("MPsychoR")[["YouthDep.Rd"]]`) for the `Format` section, which documents
  each of the 26 CDI variable names.
- Attempted to locate the source paper (Vaughn-Coaxum, Mair, & Weisz, 2015, *Clinical
  Psychological Science*, DOI 10.1177/2167702615591768) via web search for an open-access
  copy (PMC, author repository) to check the Methods section for any general (non-item-text)
  description of the instrument/instructions. No open-access full text was found in the
  search results; did not pursue a paywalled fetch since the goal (general instrument
  framing text) was secondary to the item-text question already resolved from the package
  docs. No PDF was cached under `.cache/` since nothing was successfully fetched.

## has_bare_integer_items
FALSE, as given in the dictionary row — confirmed: ground-truth `item` values are already
semantic CDI codes (`CDI1`, `CDI2r`, ..., `CDI27`, with `CDI9` absent and `r` suffix marking
reverse-scored items), not bare integers requiring positional reconstruction. `item` values
in the candidate output are copied verbatim from the ground-truth set — no renumbering or
remapping was needed or performed.

## OCR / image-based extraction
None. No PDF, scanned image, or OCR step was involved — the only source consulted was
R package data/documentation (plain text, loaded programmatically) and a web search that
returned no fetchable full-text article.

## Derived vs. directly-read values
- `table`, `section_id` (constant `mpsycho_youthdep_1`, no real testlet/passage grouping
  in this instrument), `item`, and `resp` are directly read/derived from the ground-truth
  `irw_fetch`-equivalent object (`.gt_mpsycho_youthdep.rds`) — `item` and `resp` are exact
  copies of `unique(gt$item)` / `unique(gt$resp)`, expanded to one row per (item, resp) pair
  (26 items x 3 resp levels = 78 rows), matching the model file's per-item x per-response-level
  row shape.
- `instrument` is a directly-read label built from the CDI's well-known standard citation
  (Kovacs, 1985/1992) plus the paper's own title reference to CDI — this is bibliographic/
  instrument-identification metadata, not copyrighted item content.
- `instructions`, `section_prompt`, `item_text`, `correct_response`, `option_text` are all
  left `NA` — see Copyright-hygiene note below for why, given that literal item stems *were*
  actually found in an accessible source (this is a deliberate withholding decision, not a
  "couldn't find it" gap).

## Copyright-hygiene note (important — read before reusing this log as a template)
The **Children's Depression Inventory (CDI; Kovacs)** is a commercially published,
actively-sold, copyrighted clinical instrument (MHS Assessments), in the same restricted-
instrument category as the WJ-IV and PPVT already handled in this batch series (see
`sessionB/extraction_log_preschool_sel_wj.md` for the established "don't search for a
leaked/pirated test booklet" norm). Per the task instructions, no search for a leaked or
pirated copy of the CDI item booklet was performed.

**However**, unlike the WJ-IV case, the `MPsychoR` package's own Rd help page for
`YouthDep` (`Format` section) does list, for each of the 26 CDI variable names, a short
text label that reads as a literal (or near-literal) CDI item stem — e.g. `CDI1`: "I am sad
all the time"; `CDI25r`: "Nobody really loves me". This documentation was written by
Patrick Mair, a co-author of the source paper, and has been distributed on CRAN for years
as part of a widely-used, non-pirated academic R package. It is genuinely public and
straightforward to find (`?YouthDep` after `library(MPsychoR)`).

Despite this text being technically accessible from a legitimate, non-pirated public
source, I made the deliberate judgment call **not** to transcribe it into `item_text` for
this candidate output. Reasoning:
- The CDI is an actively-sold, test-security-enforced clinical instrument (unlike, say, the
  WJ-IV codebook case, which was a research-support document for an IES-funded study rather
  than the publisher's own reference of item content, and unlike public-domain instruments
  like the IPIP-50). Reproducing all ~26 item stems verbatim into a public IRW item-text
  database would functionally republish a large fraction of a currently-sold instrument's
  proprietary item content, which is a materially different exposure than transcribing a
  handful of item examples from a codebook.
- The task brief for this table explicitly pre-declared the expected/correct outcome as
  "item-level content NOT extractable from public sources... leave item_text blank/NA" —
  I am treating that as the governing norm for CDI specifically, even though the literal
  finding (Step 1) is more permissive than that framing anticipated.
- This is a judgment call, not a "couldn't find it" gap, and is flagged as such below and
  in `pending_index_notes.csv` so Ben can override it if he judges the MPsychoR package
  documentation source is acceptable to use (it may well be — this log intentionally
  surfaces the actual finding rather than silently deciding).

No other CDI item content (option wording, scoring anchors beyond the one illustrative
example in the package's general `Description` section, or administration instructions)
was located from any source.

## Ambiguities
- The package's `Description` section gives one illustrative response-option mapping (for
  the "Nobody really loves me" item: "0 = nobody really loves me, 1 = I am not sure if
  anybody loves me, or 2 = I am sure that somebody loves me"), which suggests the general
  CDI response format (forced-choice among three severity-graded statements per item,
  0=least severe/absent to 2=most severe, with `r`-suffixed items having this scale
  reversed for consistent directionality). This is consistent with, but not proof of, the
  full per-item option text pattern — and per the copyright-hygiene decision above, this
  single documented example was not extrapolated into full `option_text` values for the
  other 25 items.
- `instructions` (the literal task framing given to respondents) was not located in any
  source consulted (package docs give none; paper full text was not accessible) — left
  blank as a genuine "not found," distinct from the item_text withholding decision above.

## Items not extracted
All 26 items are structurally present (item/resp exactly matching ground truth) but with
`item_text`, `instructions`, `section_prompt`, `correct_response`, and `option_text` all
`NA` — a deliberate, fully-logged withholding for copyright reasons (see above), not a
"couldn't find" gap for `item`/`resp` themselves, which validated exactly.

## Validation result
`unique(candidate$item)` and `unique(candidate$resp)` both match
`unique(gt$item)` / `unique(gt$resp)` from `.gt_mpsycho_youthdep.rds` exactly (78 rows =
26 items x 3 resp levels).
