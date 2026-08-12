# Extraction log: gilbert_meta_108

## has_bare_integer_items
FALSE. Ground-truth items are already semantically labeled (`l2a`...`l2h`, matching
survey codes rather than positional integers), so no item-to-position reconstruction was
needed -- only item-*text* recovery was attempted.

## Source type used
Working paper (grey literature / discussion paper), not the peer-reviewed journal
article or the raw questionnaire/codebook. Specifically:
- Dictionary URL (`dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OBZUCX`)
  and DOI (`10.1080/00220388.2024.2404573`, Timu, Shee, Ward & You 2025, *Journal of
  Development Studies* 61(3):336-356) as given.
- `dataverse.harvard.edu` was WAF-blocked on both attempts in this session: the dataset
  landing page returned an empty body via WebFetch, and a direct `curl` to the Dataverse
  API (`/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/OBZUCX`) returned
  `HTTP 202` with an empty body -- the same block pattern seen elsewhere in the
  `gilbert_meta_*` family, confirmed here even though this table's depositor (IFPRI) is
  different from the usual Kim/Gilbert group. So the WAF block is host-level, not
  depositor-specific.
- The DataCite metadata API (`api.datacite.org/dois/10.7910/dvn/obzucx`) *did* work and
  returned dataset-level metadata (study design, sample, file formats/sizes -- three
  files: 573KB/42KB/5KB, `.tsv` + Stata `.do`), but no variable-level codebook content
  (DataCite doesn't carry per-file variable labels).
- Found the actual underlying IFPRI working paper via CGSpace (open-access repository
  mirror, not paywalled): **"Rural Credit, Food Security, and Resilience: An Empirical
  Evaluation from Kenya," IFPRI Discussion Paper 02351 (August 2025)** --
  `cgspace.cgiar.org/items/5b283fa3-8aca-42d6-9a42-40b27b6422c5`, PDF bitstream cached at
  `itemtext/.cache/gilbert_meta_108/rural_credit_food_security_resilience.pdf`
  (`pdftotext` output: `rural_credit.txt`). This title matches the Dataverse dataset's
  own reference title exactly, so it is very likely the paper actually paired with this
  specific replication data (as opposed to the companion JDS gender-focused paper, which
  was also checked but doesn't appear to describe the CSI construction in as much
  detail). Also fetched a second, apparently distinct IFPRI Discussion Paper (2215, "A
  field study for assessing risk-contingent credit...") via a different CGSpace record --
  cached at `.cache/gilbert_meta_108/ifpri_discussion_paper_2215.pdf` -- but it does not
  discuss the CSI/L2 module at all and appears to be an earlier/different paper in the
  same project family; not used for extraction.
- The published JDS article itself (tandfonline.com) is paywalled and no open-access
  manuscript version was found beyond the CGSpace items above.

## OCR / image-based extraction
None used. Both cached PDFs are text-based (not scanned images); `pdftotext` extracted
clean, searchable text directly. No image transcription was needed or performed for this
table.

## What the 8 resp categories (0-7) turned out to represent
Confirmed (with high confidence, but see caveat below) via the discussion paper's own
methods section (`rural_credit.txt` lines 366-376):

> "To construct the CSI, households could select from among a pre-identified list of
> eight strategies that households could apply to cope with food insecurity. We then
> created a binary variable for each coping strategy that took a value of one if the
> strategy was applied at least once in the past seven days and zero otherwise. The CSI
> measure is then the sum of these eight binary indicators, and could take a value
> between 0 and 8."

This confirms: `l2a`-`l2h` are the 8 sub-items of a **Coping Strategy Index (CSI)**
checklist -- a standard household food-insecurity measurement instrument (Maxwell-style
CSI; the paper does not cite Maxwell & Caldwell by name or give the item wording). The
paper describes its own *derived analysis variable* as binary (used the strategy in the
past 7 days: yes/no), but the raw ground-truth `resp` values are integers 0-7 per item,
not 0/1 -- this is consistent with (and not contradicted by) the standard CSI/rCSI
survey design, where the raw question asked is **"In the past 7 days, how many days did
your household have to rely on [strategy]?"**, with a numeric response of 0-7 days, which
the paper's own analysis then collapses to a binary "used at least once" indicator for
constructing the summary CSI score (0-8). The 0-7 range matches this "days in the past 7
days" framing exactly (8 possible values, 0 through 7 inclusive).

**Caveat -- this is a derived inference, not a directly confirmed source statement.**
The paper never explicitly states the raw per-item response scale is "0-7 days" -- it
only describes the derived binary variable. I did not find the literal survey question
wording, the identity of the 8 specific coping strategies (e.g. which is "ate
less-preferred foods" vs. "reduced meal frequency" etc.), or which of `l2a`...`l2h`
corresponds to which specific strategy. No appendix, footnote, or citation (e.g. to
Maxwell & Caldwell 2008, the standard CSI methodology reference) listing the 8 items by
name was found in either cached PDF.

## Derived vs. directly-read values
- **Directly read from source**: "8 pre-identified coping strategies," "binary variable
  per strategy based on use in the past seven days," "CSI = sum of the 8 binary
  indicators, range 0-8" -- all direct quotes/paraphrases of the paper's stated methods.
- **Derived/inferred by this extraction**: that the raw `l2a`-`l2h` response scale
  (0-7, confirmed from ground truth) represents "number of days out of the past 7 the
  strategy was used" is my inference from (a) the paper's explicit statement that the
  *derived* binary variable is built from an underlying per-strategy measure, and (b) the
   exact numeric match between 0-7 and a 7-day recall window. This inference is strong
  but **not a literal transcription**, so per instructions I did not write it into
  `item_text` or `option_text` -- both are left `NA` for all 8 items/64 rows rather than
  fabricating option labels like "0 days"/"1 day"/etc. The `instrument` field records the
  identified construct name (CSI) and the survey module code ("L2"), which I judge safe
  to state since it's the paper's own terminology for its own instrument, not invented
  item wording.

## Structure of output
Single `section_id` (`gilbert_meta_108_1`) covering all 8 items, since they form one
CSI checklist administered together (a single shared 7-day recall context), even though
the literal shared framing text couldn't be recovered to populate `section_prompt`.
`instructions` and `section_prompt` are both `NA` (not recovered). `item_text` is `NA`
for all 8 items (exact strategy wording not recovered). `correct_response` is `""` (no
scoring key -- behavioral frequency measure, not a knowledge/ability item).
`option_text` is `NA` for all resp values (see caveat above -- the "days" interpretation
is inferred, not literally sourced, so left blank per instructions rather than guessed).
`resp` is populated 0-7 for every item, matching ground truth exactly.

## Items not extracted (text-wise)
All 8 items (`l2a`-`l2h`) are present with correct `item`/`resp` values (validated exact
match against ground truth), but **none have recovered `item_text`, `option_text`, or
`instructions`/`section_prompt` text** -- the specific strategy wording per item and the
literal survey question/response-scale text were not found in either accessible source
(discussion paper text, DataCite metadata) and Dataverse itself -- where a codebook or
`.do` file with variable labels for `l2a`-`l2h` most likely lives -- is WAF-blocked for
automated fetching. This is a partial/discrepant extraction (construct-level and
scale-range identification only; no item-level or option-level text), logged to
`pending_index_notes.csv`.

## Validation result
Exact match: `unique(candidate$item)` == `unique(irw::irw_fetch("gilbert_meta_108")$item)`
(8 items, `l2a`...`l2h`) and `unique(candidate$resp)` == `unique(irw::irw_fetch("gilbert_meta_108")$resp)`
(8 values, 0-7). No `raw_resp` needed since the numeric `resp` values themselves are
already correct and complete -- only the human-readable text mapped onto them is
missing.
