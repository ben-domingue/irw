# Extraction log: gilbert_meta_59

## Source type used
Public-domain standard instrument (PSS-10, Cohen, Kamarck & Mermelstein 1983),
verbatim text read from a directly-fetched PDF reproduction of the instrument,
NOT the dictionary-cited Lancet Psychiatry paper itself (which does not mention
PSS-10 at all — see below) and NOT the Dataverse raw data file (WAF-blocked, as
already established for this dataset across the gilbert_meta series). A companion
paper from the same cohort confirms PSS-10 was administered in this study; the
literal item wording comes from the standard published instrument, not from
either paper's text (neither paper reproduces the full item list).

## Source used
1. **Dictionary-cited reference paper**: Maselko, J., Sikander, S., Turner, E. L.,
   et al. (2020). *The Lancet Psychiatry*, 7(9), 775-787. Open-access PMC copy
   PMC8015797 (https://pmc.ncbi.nlm.nih.gov/articles/PMC8015797/), fetched via
   WebFetch. **Checked for PSS/PSS-10 mention: absent.** This paper's stated
   outcome measures are PHQ-9, WHO-DAS, and SCID (consistent with gilbert_meta_58's
   log); it does not mention Perceived Stress Scale anywhere.
2. **Companion paper confirming PSS-10 use in this exact cohort**: Haight SC,
   Gallis JA, Chung EO, Baranov V, Bibi A, Frost A, et al. (2022). "Stressful life
   events, intimate partner violence, and perceived stress in the postpartum
   period: longitudinal findings in rural Pakistan." *Social Psychiatry and
   Psychiatric Epidemiology*, 57(11), 2193-2205. doi:10.1007/s00127-022-02354-3.
   Identified via the Bachpan Study's own publications page
   (https://www.bachpanstudy.com/publications) as using the PSS in the same
   rural-Pakistan/Bachpan cohort as the dictionary dataset (doi:10.7910/DVN/IJE2PC).
   Open-access copy located at PMC10084399
   (https://pmc.ncbi.nlm.nih.gov/articles/PMC10084399/), fetched via WebFetch.
   Measures-section quote: "the 10-item Cohen Perceived Stress Scale (PSS-10), a
   global measure of perceived stress"; "Participants were asked about the
   frequency (never, almost never, sometimes, fairly often, very often)"; "Total
   scores were obtained by reversing the scores on the four positive items and
   summing all ten items with scores ranging from 0 to 40." Confirms PSS-10 (not
   a modified/short form), 0-4 response scale with those five anchor labels, and
   reversal of the four positively-worded items — but this paper does not itself
   reproduce the full 10-item verbatim list.
3. **Item text source**: standard Cohen (1983) PSS-10 instrument, read verbatim
   from a cached PDF, `.cache/gilbert_meta_59/pss10_wovenwomenvets.pdf`
   (downloaded via curl, read with the Read tool's native PDF parsing — not an
   AI-summarized fetch). This one-page handout is a direct reproduction of the
   instrument citing "Cohen, S., Kamarck, T., & Mermelstein, R. (1983). A global
   measure of perceived stress. Journal of Health and Social Behavior, 24,
   385-396" and includes the full 10 items, the "In the last month, how often:"
   stem, the 0-4 Never..Very Often response scale, and explicit reverse-scoring
   instructions for items 4, 5, 7, 8. Full detail and cross-check sources logged
   in `.cache/gilbert_meta_59/sources.md`.

## Cross-check: reverse-scored item positions
Live ground truth item labels are `pss1, pss2, pss3, pss4rev, pss5rev, pss6,
pss7rev, pss8rev, pss9, pss10`. The cached PSS-10 source states: "Reverse your
scores for questions 4, 5, 7, and 8." The `rev`-suffixed positions in the live
data (4, 5, 7, 8) match the standard instrument's reverse-scored item positions
exactly, with all other positions unsuffixed. Combined with the companion paper's
explicit confirmation that this Bachpan/Pakistan cohort administered "the 10-item
Cohen Perceived Stress Scale (PSS-10)" with reversal of "the four positive
items," this is treated as strong corroboration (not proof by range-matching
alone, per the skill's bare-integer-item caution) that pss1..pss10 follow the
standard PSS-10 presentation order 1:1.

## has_bare_integer_items
FALSE, as stated in the dictionary row — item values are already semantic labels
(`pss1`..`pss10`, with `rev` suffixes on 4 of them), not bare integers requiring
positional reconstruction from scratch. The reverse-item-position cross-check
above was still performed as an extra confirmation step (per task instructions),
even though it wasn't strictly required to resolve item identity the way it would
be for bare-integer items.

## OCR / image-based extraction
Not applicable. All source material used (PMC8015797 HTML, PMC10084399 HTML, and
the cached PSS-10 PDF) was native selectable/parseable text; no scanned-image
content was involved.

## Derived vs. directly-read values
- `item` (pss1..pss10, incl. rev suffixes) and `resp` (0-4) are read directly
  from the cached ground truth (`irw::irw_fetch("gilbert_meta_59")`), not
  derived or reconstructed.
- `instrument` name is the standard full name for PSS-10 with its canonical
  citation, not paper-specific wording (since neither paper names the scale in
  a self-contained title/heading).
- `instructions` ("In the last month, how often:") is transcribed verbatim from
  the cached PDF's column-header stem, which functions as the shared framing
  for every item — not a paraphrase.
- `item_text` for all 10 items is transcribed verbatim from the cached PDF (see
  Source #3 above), not paraphrased, expanded, or inferred beyond confirming the
  presentation-order mapping via the reverse-item cross-check.
- `option_text` (Never/Almost never/Sometimes/Fairly often/Very often mapped to
  resp 0-4) is transcribed verbatim from the same PDF's response-scale header,
  applied identically to every item (the PDF prints the same five-column header
  for all 10 rows). Note: `resp` in the live data is the RAW 0-4 code as
  administered; the `rev` in item names signals that reversal is applied only at
  total-score computation time (per the source's own scoring instructions), not
  in the raw per-item resp value, so `option_text` labels (Never..Very Often) are
  not flipped for the `rev` items.
- `correct_response` and `section_prompt` left blank for all rows — PSS-10 is a
  self-report scale with no scoring key, and there is no testlet/shared-passage
  structure (a single trivial `section_id` = `gilbert_meta_59_1` is used per the
  skill's convention for instruments without real section grouping).

## Validation result
`item` and `resp` sets match ground truth **exactly**: 10 items
(pss1, pss2, pss3, pss4rev, pss5rev, pss6, pss7rev, pss8rev, pss9, pss10), 5 resp
values (0, 1, 2, 3, 4). `item_text`/`option_text` coverage: 10/10 items, all with
literal source text recovered from a directly-read public-domain instrument
source (not fabricated/inferred wording) — full match, not a partial extraction.
No entry added to `pending_index_notes.csv` for this table since there is no
discrepancy to log.
