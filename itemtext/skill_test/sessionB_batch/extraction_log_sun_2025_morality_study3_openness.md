# Extraction log: sun_2025_morality_study3_openness

## Source used
- Full-text open-access PDF of the published article: Sun, J., Wu, W., & Goodwin, G. P.
  (2025). Are moral people happier? Answers from reputation-based measures of moral
  character. *Journal of Personality and Social Psychology, 128*(5), 1160-1180.
  https://jessiesun.me/publication/sun-2025/sun-2025.pdf (author's own postprint copy).
  DOI 10.1037/pspp0000539 is paywalled at the APA site, so this author copy was reused
  (already cached from `sun_2025_morality_study1_dependability` at
  `.cache/sun_2025_morality_study1_dependability/sun_2025_paper.pdf` /
  `sun_2025_paper.txt`). No new fetch needed.
- OSF project https://osf.io/5e9y3/overview, file `data-clean/normdat-labels.csv`
  (reused from the same cache directory). This is the codebook for a separate MTurk
  moral-relevance norming study run on the same item pool, keyed to standard BFI-2 item
  numbers (`mv.BFI2.<n>`), and gives verbatim lowercase item text for all 60 BFI-2 items.

## has_bare_integer_items
FALSE, as stated in the dictionary row. `item` values are named codes (`itbfi220`,
`itbfi230`, `itbfi240`, `itbfi25`, `itbfi255`, `itbfi260`), not bare integers. As with
the sibling `study1_dependability` table, the codes still required decoding (they are
not self-evidently BFI-2 item text), so the same reconstruction rigor was applied.

## Structure discovered
Ground truth (read directly via `readRDS`, exact strings printed):
`item` = `"itbfi220" "itbfi230" "itbfi240" "itbfi25" "itbfi255" "itbfi260"` (6 items),
`resp` = `1 2 3 4 5`, N id = 437, N rows = 2622 (437 x 6 = 2622, confirming full
crossing with no missing-item dropout distorting the item set).

The paper's Study 3 "Informant-Reported Nonmoral Personality Traits" subsection (p.
1171 of the printed pagination, `sun_2025_paper.txt` lines ~874-882) states: "we
obtained informant reports of three nonmoral personality traits: extraversion (e.g.,
'Is outgoing, sociable'), neuroticism (e.g., 'Worries a lot'), and openness (e.g., 'Has
little creativity' [r]). For each of these traits, informants rated six statements from
the BFI-2-S (Soto & John, 2017b) using a 5-point scale anchored by strongly disagree
and strongly agree." This independently confirms: (a) exactly 6 openness items, matching
the ground truth's 6-item set; (b) the response format (5-point, strongly
disagree/strongly agree anchors); (c) one specific item verbatim ("has little
creativity" — case-folded, see below), which must correspond to one of the 6 codes.

### Decoding itbfi2<NN> -> BFI-2 item <NN>
Applying the `itbfi2<NN>` = BFI-2 item `<NN>` convention established for
`study1_dependability` (there confirmed via `data/sun_2025_morality.do`'s
compassion/respectfulness item blocks and cross-checked against
`normdat-labels.csv`):
- `itbfi220` -> item 20 -> Aesthetic Sensitivity -> "is fascinated by art, music, or literature"
- `itbfi230` -> item 30 -> Creative Imagination -> "has little creativity"
- `itbfi240` -> item 40 -> Intellectual Curiosity -> "is complex, a deep thinker"
- `itbfi25`  -> item 5  -> Aesthetic Sensitivity -> "has few artistic interests"
- `itbfi255` -> item 55 -> Intellectual Curiosity -> "has little interest in abstract ideas"
- `itbfi260` -> item 60 -> Creative Imagination -> "is original, comes up with new ideas"

**On "itbfi25" specifically**: this is `itbfi2` + `5`, i.e. BFI-2 item 5, NOT a typo for
`itbfi205`/`itbfi250`/etc. Two independent lines of evidence converge on this:
1. **Direct textual match.** The paper's own example quote for the openness measure is
   "Has little creativity" [r], which case-insensitively matches `mv.BFI2.30` in
   `normdat-labels.csv` ("has little creativity") exactly. `itbfi230` therefore
   unambiguously decodes to item 30 — confirming the `itbfi2<NN>` convention holds for
   this table with no digit-count irregularity (item 30 -> two-digit suffix "30", exactly
   as expected). This validates the decoding rule generally for this item set.
2. **Domain/facet structure check.** The official 60-item BFI-2's Openness domain
   comprises exactly three facets: Aesthetic Sensitivity (items 5, 20, 35, 50), Creative
   Imagination (items 15, 30, 45, 60), and Intellectual Curiosity (items 10, 25, 40, 55).
   Decoding all 6 ground-truth codes (with `itbfi25` = item 5) yields items {5, 20, 30,
   40, 55, 60} — exactly two items per Openness facet (5+20 from Aesthetic Sensitivity,
   30+60 from Creative Imagination, 40+55 from Intellectual Curiosity). This is exactly
   the structure of the BFI-2-S (Soto & John, 2017b) short form, which samples 2 items
   per facet, and exactly matches the paper's own statement that informants "rated six
   statements from the BFI-2-S" for openness. Every one of the 6 decoded numbers falls in
   the official Openness item set (12 possible values: 5,10,15,20,25,30,35,40,45,50,55,60)
   with clean 2-per-facet coverage — a decoding under any other reading of "itbfi25"
   (e.g. as item 205 or 250, both nonexistent in a 60-item inventory) would be impossible,
   and a misread as item 25 (Intellectual Curiosity) would produce two items from
   Intellectual Curiosity (25, 40, 55 -- three) and only one from Aesthetic Sensitivity
   (20), breaking the clean 2-per-facet BFI-2-S pattern. Item 5 is the only reading that
   keeps the structure clean.

Conclusion: `itbfi25` = BFI-2 item 5 ("has few artistic interests"), not a typo or
alternate scheme. The apparent "irregular numbering" flagged in the task brief is fully
explained: `itbfi2` + `5` just prints as a 4-digit-total variable name because item 5 is
single-digit, unlike items 20/30/40/55/60 which are two-digit.

## Structure of output
One `section_id` (`sun_2025_morality_study3_openness_1`) for all 6 items, since they
share the same response instructions and instrument.

Per the instructions/section_prompt boundary rule: the whole-instrument response-format
framing ("Informants rated six statements from the BFI-2-S ... using a 5-point scale
anchored by strongly disagree and strongly agree") went in `instructions`, transcribed
close to verbatim from the paper.

`section_prompt` was left **blank**, not populated with the "[Target's name] is someone
who..." stem used for the moral-character composite in `study1_dependability`. That
stem sentence is explicitly stated in the paper only for the compassion/respectfulness/
dependability facets of the *moral character* measure (p. 1165-1166: "The compassion,
respectfulness, and dependability facets were preceded by the item stem, '[Target's
name] is someone who...' "). The paper's Nonmoral Personality Traits paragraph (the one
actually describing this openness measure) does not restate or reference that stem
sentence at all -- it only gives the 5-point response-scale framing. While it is
plausible informants saw the same or a similar stem for these BFI-2-S items (BFI-2 items
are conventionally third-person completions), the paper never says so for this specific
measure, so per the "do not guess/fabricate" instruction, no stem text was invented for
`section_prompt` here -- it is left blank rather than reusing the dependability-facet
stem by analogy. Logged below as a discrepancy/uncertainty.

`option_text` populated only for resp 1 ("strongly disagree") and resp 5 ("strongly
agree") -- the paper states the scale is "anchored by" these two endpoints only; no
verbal labels for intermediate points 2-4 are given anywhere in the paper or OSF
materials, so those were left blank (same convention as `study1_dependability` and the
`firstborn_personality` reference example).

`correct_response` left blank throughout -- personality-trait rating measure, no scoring
key.

Note (not encoded in any output column, informational only): the paper marks "has little
creativity" (item 30 / `itbfi230`) with "[r]", indicating it is reverse-scored in the
openness composite. This does not change `item_text` (still the literal statement as
administered) or the `resp`/`option_text` mapping (informants still respond on the same
raw 1-5 disagree-to-agree scale; reverse-keying is a scoring-time transformation, not an
administration-time difference), so no adjustment was made to the extracted item text or
response options.

## OCR / image-based extraction
None needed. The source PDF is text-based (not scanned/image); `pdftotext -layout` output
was reused directly from the `study1_dependability` cache. No OCR used anywhere in this
extraction.

## Derived vs. directly-read values
- `item_text` for all 6 items is directly read from `normdat-labels.csv` (verbatim
  lowercase BFI-2 item-bank text keyed by item number), independently cross-checked
  against the one item quoted verbatim in the paper's own prose ("Has little creativity"
  [r], case-folded match to item 30's codebook text). Not inferred from range-matching or
  facet-position guessing alone.
- The `itbfi2<NN>` -> BFI-2 item `<NN>` -> item-text chain is a decoding/inference, but
  one confirmed by two independent, mutually consistent lines of evidence (direct
  verbatim quote match for one item; full-set 2-per-facet Openness-domain structure
  matching the paper's explicit "six statements from the BFI-2-S" statement for all six),
  not assumed from the naming pattern alone.
- `instructions` is a close transcription of the paper's own sentence describing the
  rating task and response scale.
- `option_text` anchors ("strongly disagree"/"strongly agree") are a direct,
  paraphrase-free read of the paper's stated scale anchors.
- `section_prompt` is a directly-read absence, not a derived value: left blank because no
  literal stem text could be found in the paper specifically for this measure (see above).

## Source type used
Published journal article (author's open-access postprint PDF) as primary source for the
item count, response-scale anchors, and one verbatim example item text; cross-checked
against the dataset's own OSF repository (`data-clean/normdat-labels.csv`, a related
norming-study codebook using the same BFI-2 item numbering) for the literal text of all 6
items and their facet assignments.

## Ambiguities / items not extracted
- All 6 ground-truth items were extracted, mapped, and validated with exact `item`/`resp`
  set match against `.gt_sun_2025_morality_study3_openness.rds`.
- One discrepancy logged (see `pending_index_notes.csv`): `section_prompt` (item stem
  text, e.g. a possible "[Target's name] is someone who...") could not be confirmed for
  this specific measure and was left blank rather than assumed by analogy to the
  study1_dependability moral-character facets, which explicitly state that stem only for
  their own items.
