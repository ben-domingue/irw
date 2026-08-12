# Extraction log: psychotools_conspiracist

## Source used
Two sources, cross-checked against each other:
1. R package documentation: `psychotools::ConspiracistBeliefs2016` help page (`?ConspiracistBeliefs2016`,
   installed from CRAN, read via `tools::Rd_db("psychotools")` / `Rd2txt`). The Details section
   reproduces the literal text of all 15 GCBS items (`Q1`-`Q15`), states the response format is
   "15 five-point likert-rated items (0 = disagree to 4 = agree)", and gives full provenance: this
   is the Open Source Psychometrics Project's 2016 online administration of the Generic
   Conspiracist Beliefs (GCB) Scale (Brotherton, French & Pickering, 2013), not a re-run of the
   original 2013 study samples.
2. The GCBS codebook distributed with the raw data, `https://openpsychometrics.org/_rawdata/GCBS.zip`
   -> `data/codebook.txt` (fetched and cached, see below). This confirms "Q1 - Q15" "question numbers
   match to items in TABLE A1 of Brotherton, et. al. 2013" but does **not** itself reproduce the
   response-scale anchor wording.
3. The open-access source paper: Brotherton R, French CC, Pickering AD (2013). Measuring Belief in
   Conspiracy Theories: The Generic Conspiracist Beliefs Scale. *Frontiers in Psychology*, 4, 279
   (fetched via `frontiersin.org`, full text). This supplied the literal 5-point response-scale
   anchor wording ("1: definitely not true; 2: probably not true; 3: not sure/cannot decide;
   4: probably true; 5: definitely true") and confirmation of the 5 named facets (Government
   Malfeasance/GM, Malevolent Global Conspiracies/MG, Extraterrestrial Cover-up/ET, Personal
   Wellbeing/PW, Control of Information/CI), each with 3 items, presented in the paper's own
   interleaved item order (GM, MG, ET, PW, CI repeated 3 times) which exactly matches the
   `Q1..Q15` order given in the psychotools help page.

## Source type used
Directly-read literal text: R package help documentation (`Rd2txt` output, distributed by the
package maintainers and sourced from the Open Source Psychometrics Project's own codebook) for
item wording and item order/facet assignment; the open-access Frontiers journal paper's own body
text for the literal 5-point response-scale anchor labels (the psychotools help page only gives a
paraphrased "0 = disagree to 4 = agree" gloss of the scale, not the actual anchor wording presented
to respondents — the paper's Table A1/Methods description was used instead since the GCBS.zip
codebook explicitly states its Q1-Q15 wording matches Table A1 of the 2013 paper). No OCR was
needed for either source.

## OCR / image-based extraction
None. The Rd help page is native package text; the Frontiers paper and the GCBS.zip codebook.txt
are both native-text web content, not scanned images. No image-based transcription was performed.

## Source type detail: fetched web/zip material
`https://openpsychometrics.org/_rawdata/GCBS.zip` was fetched, unzipped, and `data/codebook.txt`
read directly (plain text, not OCR) to confirm this dataset is the OSPP 2016 online GCBS
administration and that its `Q1-Q15` numbering matches Brotherton et al.'s (2013) Table A1 —
used only for provenance confirmation, not for the literal response-anchor text (the codebook
does not reproduce the anchor wording itself, only the item numbering correspondence).

## Structure discovered
Ground truth: 15 items (`q1`-`q15`), resp 0-4 (5-point). This matches `psychotools`'s
`ConspiracistBeliefs2016$resp` matrix exactly (columns `q1`...`q15`, values 0-4). Confirmed the
15 items decompose into 5 named facets of 3 items each, in the interleaved presentation order used
by both the psychotools help page and the paper: GM = {q1,q6,q11}, MG = {q2,q7,q12},
ET = {q3,q8,q13}, PW = {q4,q9,q14}, CI = {q5,q10,q15}.

## Structure of output
Five sections (`psychotools_conspiracist_gm`, `_mg`, `_et`, `_pw`, `_ci`), one per GCBS facet,
3 items each. `section_prompt` left blank for all — the facet grouping is a scoring/organizational
grouping, not a shared-passage/testlet structure with its own literal prompt text; `section_id` is
still populated per the skill's rule to always provide a join key. `instructions` is one sentence
describing the 5-point Likert response format with all 5 qualitative anchor labels, quoted/lightly
combined from the paper's own description of the scale ("a 5-point Likert-type scale, with a
qualitative label associated with each point") plus its literal stated anchors — this is
whole-table framing (applies regardless of facet), so it belongs in `instructions`, not
`section_prompt`. `option_text` is populated for all 5 resp values (0-4), unlike the two prior
psychotools tables in this batch (`gratitude_gart`/`gac`) which only had endpoint anchors disclosed
— here the source discloses a qualitative label for every point (not just the endpoints), so all
5 are transcribed to match the source's own completeness. `correct_response` left blank throughout
— this is a self-report belief-in-conspiracy-theories measure with no scoring key/correct answer.

## Derived vs. directly-read values
All 15 `item_text` values are directly-read literal transcriptions from the psychotools help page
(itself sourced from the OSPP codebook/original data). The facet assignment (`section_id`) is
directly read from the paper's own Table A1 facet structure combined with the item order/wording
match between the psychotools help page and the paper — not an independent inference, since the
interleaved order (GM,MG,ET,PW,CI x3) that produces `q1->GM, q2->MG, ...` was confirmed by matching
each `Qn` item's literal wording against the paper's facet-labeled item list, not just assumed from
position. `option_text` for all 5 resp values are direct quotes of the paper's stated Likert
anchors, mapped from the paper's 1-5 numbering down to the data's 0-4 numbering (1->0, 2->1, ...,
5->4), a straightforward index shift stated explicitly by both the psychotools help page ("0 =
disagree to 4 = agree", i.e. re-indexed) and consistent with the codebook.txt's confirmation that
Q1-Q15 correspond directly to Table A1. `instrument` name ("Generic Conspiracist Beliefs Scale
(GCBS; Brotherton, French & Pickering, 2013)") is directly read from the paper's own title/naming
of the instrument.

## has_bare_integer_items
FALSE, confirmed per the dictionary row. All 15 `item` values in the live data are named/labeled
codes (`q1`-`q15`, the "qN" convention), not bare integers — each mapped directly and unambiguously
to a psychotools help-page `Qn` item and its literal text and facet; no position-based
reconstruction of item identity from an ambiguous bare-integer coding was needed. (The `qN` labels
themselves are still ordinal/positional by construction, but that positional correspondence is
directly disclosed by the source, not inferred.)

## Ambiguities
One judgment call: the exact literal wording of the response-scale anchors is disclosed in the
2013 paper (1-5 numbering, "definitely not true"..."definitely true") rather than in the
psychotools help page describing this specific 2016-collected dataset (which only glosses the scale
as "0 = disagree to 4 = agree" without giving the actual anchor text). Since the GCBS.zip
codebook.txt explicitly confirms this dataset's `Q1-Q15` numbering "match[es] to items in TABLE A1
of Brotherton, et. al. 2013" (i.e. the same instrument, same anchor wording, just re-collected
online), the paper's literal anchor wording was used as directly-read source text for `option_text`
rather than treated as an assumption. This is a reasonable, sourced inference rather than a guess,
but is noted here in case Ben wants to confirm no wording drift occurred between the original 2013
in-person/lab administration and the OSPP's 2016 online version.

## Items not extracted
None — all 15 ground-truth items were extracted with literal item text, and the full resp 0-4
range was covered with a qualitative anchor label at every point (not just endpoints).

## Validation result
EXACT MATCH. `sort(unique(item))` == `c("q1","q10","q11","q12","q13","q14","q15","q2",...,"q9")`
for both candidate and ground truth; `sort(unique(resp))` == `0:4` for both, confirmed via
`Rscript` comparison against `.gt_psychotools_conspiracist.rds`. No discrepancy to log in
`pending_index_notes.csv`.
