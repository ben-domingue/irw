# Extraction log: gilbert_meta_100

## Source used
Dictionary row points to the Harvard Dataverse dataset doi:10.7910/DVN/CVO9EZ and the
reference Gilbert, J. B., Domingue, B. W., & Kim, J. S. (2025). *Estimating causal effects
on psychological networks using item response theory.* Psychological Methods
(doi:10.1037/met0000764). The published journal version is paywalled (APA PsycNet), so I
used the open PsyArXiv preprint instead: doi:10.31234/osf.io/7k6xz, resolved via the OSF
preprint API (`api.osf.io/v2/preprints/7k6xz/`) to its underlying file object and
downloaded directly (`files.osf.io/.../67351034423996340eb2f3ad` = v1,
`.../6750ff294b68617b5b925b9b` = v2/final; both checked, same relevant content). Cached at
`.cache/gilbert_meta_100/preprint.pdf` and `preprint_v2.pdf` (+ extracted text).

This repo's `data/` directory has no dedicated processing script for `gilbert_meta_100`
specifically — only `data/gilbert_meta_100.txt` ("data already in irw-compliant format").
`data/gilbertmeta.R` shows this table is one of many auto-exported from a large aggregate
`datasets_list.Rdata` object built for a companion paper (arXiv:2405.00161, IL-HTE); no
per-dataset script exists because none was needed for this one. I also checked
`data/content_literacy_intervention.R` (a script whose trailing comment says "this was
updated to gilbert_meta_2") — that script's own header comment and the existing
`pending_index_notes.csv` entry for `gilbert_meta_2` confirm it processes a *different*,
20-item MORE reading-comprehension assessment (Dataverse doi:10.7910/DVN/LAWFFU), not this
12-item vocabulary table, so it was not used as a source here (checked and ruled out, not
overlooked).

## Structure discovered
The preprint's own case-study section (pp. 19-22 of the PDF) explicitly describes its
worked example dataset: "the outcome measure was a 12-item researcher-developed vocabulary
assessment administered to a sample of 2,118 students at the end of grade 2" from an RCT of
the MORE (Model of Reading Engagement) content-literacy intervention (Kim et al., 2023).
Ground truth for `gilbert_meta_100` has exactly 12 items and 2,118 unique `id` values — an
exact match, not just plausible-range matching. The preprint also states explicitly (Section
5, data-availability paragraph): "The datasets are also available in the Item Response
Warehouse (IRW ...) under the prefix `gilbert_meta`" and that supplemental materials are
hosted at doi:10.7910/DVN/CVO9EZ — the same Dataverse DOI as this table's dictionary row.
This is strong, paper-stated confirmation (not inference) that `gilbert_meta_100` is this
case-study dataset.

Task format, quoted from the paper: "students saw a target word and were prompted to select
the two words from a list of four that 'best go with' the target word... Responses were
scored 1 when the two correct choices were selected and 0 for any other response pattern."
One fully worked example is given: target word *carnivore*, four options *fruit, care,
meat, prey*, correct = *meat* + *prey*.

A footnote (footnote 5, p. 22 of the PDF) discloses the complete 12-word target list by
listing them in three groups: "The ELA lessons contain the following eight assessed
vocabulary words: paleontologist, fossil, hunter, extinct, reptile, theory, evidence, and
carnivore. Trait, hypothesis, and organism were included in treatment lessons but not
explicitly taught. Brutal was explicitly taught in treatment lessons." That is 8 + 3 + 1 =
12 words total, matching the ground-truth item count exactly:
paleontologist, fossil, hunter, extinct, reptile, theory, evidence, carnivore, trait,
hypothesis, organism, brutal.

The paper states "We include the complete assessment in our supplement" — i.e. the literal
item wording/options for all 12 items (not just the one carnivore example) lives in a
supplement, not the paper body. That supplement is hosted on the Dataverse record
doi:10.7910/DVN/CVO9EZ. I was unable to retrieve it: every request to
`dataverse.harvard.edu` (both `curl` and the WebFetch tool) returned an empty
`HTTP 202` with header `x-amzn-waf-action: challenge` — an AWS WAF bot-challenge page that
requires a JS-capable browser, which isn't available in this environment. I also tried the
Dataverse native API endpoints (`/api/datasets/:persistentId/...`, `/api/search`) directly;
same WAF block. I did not find a mirrored copy of the CVO9EZ file listing elsewhere (web
search for the DOI/filenames returned nothing beyond generic Harvard Dataverse pages).

I also checked whether the original Kim et al. (2023) source paper(s) might separately
disclose the grade-2 item wording. I found and fully read two candidate papers:
- `files.eric.ed.gov/fulltext/ED662409.pdf` — a **grade-1** MORE evaluation with its own,
  *different* 12-item semantic-association vocabulary task (words: potential, unique,
  survive, species, behavior, resource, advantage, diversity, adaptation, habitat,
  physical feature, complex; scored 0-4, not 0/1). Confirmed via full-text read
  (`.cache/gilbert_meta_100/kim2023_eric.txt`) that this is a sibling instrument for a
  different grade/cohort — different words, different scoring — not our table. Ruled out
  explicitly, not assumed.
- The actual grade-1-to-grade-2 transfer trial paper (Kim et al., "A Longitudinal
  Randomized Trial of a Sustained Content Literacy Intervention From First to Second
  Grade..."), which is the correct source paper per the network-methods preprint's own
  citation, is hosted at `cepr.harvard.edu` — also behind the same Akamai/WAF-style block
  (`curl` returned an HTML "Access Denied" page) and ResearchGate returned HTTP 403 to
  WebFetch. Could not retrieve its appendix.

## Structure of output
Single trivial section (`gilbert_meta_100_1`, blank `section_prompt`) since there is no
testlet/passage grouping — each item is an independent semantic-association probe.
`instrument` and `instructions` are populated at the table level (quoting the task format
and scoring rule as stated in the paper). `item_text`, `option_text`, and
`correct_response` are left blank/NA for all 12 items — see "Items not extracted" below.
`item` (`"1"`-`"12"`) and `resp` (`0`/`1`) exactly match
`readRDS(".gt_gilbert_meta_100.rds")`'s `unique(item)`/`unique(resp)`.

## OCR / image-based extraction
Not needed. All source material (the PsyArXiv preprint PDF) was machine-readable text,
extracted with `pdftotext -layout`; no scanned images or OCR were involved anywhere in this
extraction.

## Derived vs. directly-read values
None of the values written were derived or computed — `item` and `resp` are copied
directly from the ground-truth RDS (as required), and every piece of instrument-level text
(`instrument`, `instructions`) is a direct paraphrase/quote of sentences read verbatim from
the source PDF, not inferred or calculated. No `item_text`/`option_text`/`correct_response`
values were written at all (left blank rather than derived/guessed) — see below.

## Source type used
Preprint (PsyArXiv PDF, open-access mirror of the paywalled Psychological Methods article)
for the instrument-level description, task format, worked example, and word list. This
repo's own processing scripts/text file (`data/gilbert_meta_100.txt`,
`data/gilbertmeta.R`) were checked for context but contained no item-level content for this
table. The Dataverse replication package (doi:10.7910/DVN/CVO9EZ), which the paper says
holds the "complete assessment," could not be accessed (WAF-blocked); an alternate original
source paper (the Kim et al. grade-1-to-grade-2 transfer RCT) that might have an item
appendix was also blocked (Akamai/ResearchGate 403). No PDF manual, no raw-data column
headers, and no OCR were used.

## Bare-integer validation check (has_bare_integer_items = TRUE)
Per SKILL.md Step 4's bare-integer rule, range/type plausibility alone ("resp is 0/1, could
be any of the 12 items") is explicitly not sufficient evidence. I instead verified:
- The paper's own stated dataset dimensions (12 items, N = 2,118) against the ground
  truth's exact `unique(item)` count (12) and unique `id` count (2,118) — an exact match on
  both counts, not merely a plausible range.
- The paper's explicit self-citation that its case-study data is deposited "in the Item
  Response Warehouse... under the prefix `gilbert_meta`" and hosted at the same Dataverse
  DOI (CVO9EZ) as this table's dictionary row — a direct textual link, not inference from
  content alone.
- I looked for (but could not access) a positional/order key — i.e., which of the 12 target
  words is `item` "1" vs. "2", etc. — which is exactly the kind of confirmation SKILL.md
  requires before assigning `item_text` to a specific bare integer. Since that key was not
  recoverable in this environment (Dataverse supplement WAF-blocked), I did **not** guess an
  order and left `item_text` blank for all 12 items, per the "genuinely not recoverable —
  don't fabricate" branch of the task instructions.

**Result: instrument identity confirmed with high confidence (exact N and item-count match
plus the paper's explicit self-citation); item-to-word ordering not confirmed — logged as a
discrepancy in `pending_index_notes.csv` rather than guessed.**

## Ambiguities
- Which specific one of the 12 recovered target words (paleontologist, fossil, hunter,
  extinct, reptile, theory, evidence, carnivore, trait, hypothesis, organism, brutal)
  corresponds to `item` "1" through "12" in the live IRW data is unresolved — the paper
  doesn't give a numbered list, and the file that would (the Dataverse "complete assessment"
  supplement) could not be fetched from this environment.
- The 4-option list is only known for one of the 12 items (carnivore: fruit, care, meat,
  prey); the other 11 items' option sets are likewise only in the unreachable supplement.

## Items not extracted
All 12 items' `item_text`/`option_text`/`correct_response` — instrument-level context
(instrument name, instructions/scoring rule, and the recovered 12-word target list) is
written and logged, but no per-item text was assigned to avoid guessing an unconfirmed
order. `item`/`resp` values themselves are complete and validated exactly against ground
truth (12/12 items, both resp values present).
