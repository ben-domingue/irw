# Extraction log: phq_insomnia_wang2025

## Naming-mismatch investigation (primary finding)

The table name `phq_insomnia_wang2025` and the dictionary Reference both point to a paper
titled "Psychometric evaluation of the insomnia severity index in 570,295 Chinese
adolescents" — i.e. about the **Insomnia Severity Index (ISI)**, a 7-item scale scored
0-4 (5-point Likert, total 0-28). But the live ground-truth data for this table has:
- 9 items, literally named `PHQ_1`..`PHQ_9`
- `resp` values 0-3 (4-point scale)

Neither the item count nor the response range matches the ISI. Fetched the paper's full
text (SAGE, open access, https://journals.sagepub.com/doi/full/10.1177/18344909241310783)
directly and confirmed: the study administered a battery that included **both** the ISI
*and* a separate PHQ-9: "The present study utilized a comprehensive questionnaire that
included the Basic Information Questionnaire, the Insomnia Severity Index (ISI), the
Patient Health Questionnaire-9 (PHQ-9), and the Adolescent Self-rating Life Events
Checklist (ASLEC)." The paper describes the PHQ-9 as "a nine-item instrument designed to
evaluate an individual's level of depression... a four-point Likert scale ranging from 0
(not at all) to 3 (nearly every day), with the PHQ-9 total score varying from 0 to 27" —
this matches the live data's 9 items / 0-3 resp range exactly, while the ISI does not.

**Conclusion: this IRW table is actually the PHQ-9 (depression), administered as a
secondary/comorbid measure alongside the ISI in the same adolescent survey — not the ISI
that the paper's title and dictionary Reference are about.** Same mismatch pattern as
`ccapsvtskhpacr_mercedes_2023_physical` earlier in this batch (table name pointed to one
instrument, live items were something else). Set `instrument` = "Patient Health
Questionnaire-9 (PHQ-9)" accordingly, not ISI.

This should be flagged in the dictionary/index — the table name and Reference describe
the ISI, but the actual response data is PHQ-9.

## Source type used

- Primary source: SAGE full-text HTML of the paper (open access), fetched via WebFetch.
  Confirmed the ISI-vs-PHQ-9 structure, PHQ-9 response scale (0-3, "not at all" to
  "nearly every day"), and the paper's own citation of the PHQ-9 to Kroenke, Spitzer, &
  Williams (2001), "The PHQ-9: Validity of a brief depression severity measure."
- The paper does **not** reproduce literal PHQ-9 item text or instructions anywhere in
  its own body (checked explicitly — no table or appendix with item wording).
- Figshare supplementary data (https://figshare.com/s/59a2c9e849bc019da6e4, and the
  specific file URL `?file=48176917` from the dictionary row) was **not accessible**:
  repeated attempts via WebFetch and via `curl` (with a browser user-agent) returned
  either HTTP 403 or an HTTP 202 with an empty body carrying an
  `x-amzn-waf-action: challenge` header — i.e. blocked by an AWS WAF bot challenge that
  neither tool can solve. A ResearchGate mirror of the paper also returned 403.
- Because the paper doesn't reproduce PHQ-9 item text and the Figshare supplement was
  unreachable, `item_text`/`option_text` were populated using the **canonical published
  PHQ-9** (Kroenke, Spitzer, & Williams, 2001, *Journal of General Internal Medicine*) —
  the exact source the paper itself cites as the instrument's origin. This is the
  standard, fixed, public-domain English-language PHQ-9 wording (9 items, "Over the last
  2 weeks, how often have you been bothered by any of the following problems?", 0=Not at
  all .. 3=Nearly every day).
- Cache: `.cache/phq_insomnia_wang2025/paper_notes.txt` (paper fetch notes),
  `.cache/phq_insomnia_wang2025/figshare_file48176917.html` (empty — WAF-blocked fetch
  attempt, kept as evidence of the block).

## OCR / image-based extraction

Not applicable — all source text was fetched as machine-readable HTML (SAGE journal full
text), not scanned/image PDF. No OCR was performed.

## Derived vs. directly-read values

- `item` and `resp` values (`PHQ_1`..`PHQ_9`, 0-3): directly read from the ground-truth
  `irw_fetch`-equivalent cached data — not derived/guessed.
- PHQ-9 response-scale labels (0=Not at all, 1=Several days, 2=More than half the days,
  3=Nearly every day) and the instructions stem ("Over the last 2 weeks, how often have
  you been bothered by any of the following problems?"): directly read from the standard
  published PHQ-9 (Kroenke et al., 2001), corroborated by the paper's own paraphrase of
  the 0-3 anchor endpoints ("0 (not at all) to 3 (nearly every day)").
- Individual `item_text` wording for PHQ_1..PHQ_9: **derived by ordinal position**, not
  directly read from this paper (the paper gives no item-by-item text). Standard PHQ-9
  item order (Kroenke et al. 2001) was used to map `PHQ_1`..`PHQ_9` onto the 9 canonical
  DSM-IV-based depression items in their conventional presentation order. This ordering
  is fixed and universal for the PHQ-9 (it is not an instrument with variable item order
  across studies), so the position-based mapping is low-risk, but it was not confirmed
  against this specific paper's own item ordering (which isn't published) or against the
  Chinese-language version actually administered to respondents (translation not
  verified — the survey was conducted in Chinese; item text here is the standard English
  original).
- `instrument` field: derived from the naming-mismatch investigation above (set to
  "Patient Health Questionnaire-9 (PHQ-9)"), overriding what the table name and
  dictionary Reference would naively suggest (ISI).

## has_bare_integer_items

FALSE, as stated in the dictionary row — ground-truth items are already the named codes
`PHQ_1`..`PHQ_9`, not bare integers, so no position-based bare-integer reconstruction was
needed for the `item` values themselves (only the item *text* mapping, per above, relied
on positional/canonical PHQ-9 order since the paper doesn't spell out item-by-item
wording).

## Ambiguities / discrepancies

1. **Naming mismatch** (see above, main finding): table name/Reference describe the ISI;
   live data and correct `instrument` are PHQ-9.
2. **Item text not verbatim from this paper**: used the canonical Kroenke et al. (2001)
   PHQ-9 wording (cited by the paper) rather than this paper's own text, because the
   paper doesn't reproduce it and the Figshare supplement was WAF-blocked. Chinese
   translation used in the actual survey not verified.
3. Figshare supplementary file (dictionary URL) inaccessible due to bot-protection
   (AWS WAF challenge) — could not check whether it contains a codebook with literal
   (Chinese) item text that would supersede the canonical English text used here.

## Items not extracted

None — all 9 ground-truth items (`PHQ_1`..`PHQ_9`) and all 4 resp values (0-3) were
extracted and matched exactly against ground truth. Coverage is complete at the
item/resp-value level; the discrepancy is about *provenance* of the item text (canonical
instrument text vs. this specific paper's/dataset's own reproduction), not about missing
items.
