# Extraction log: sun_2025_morality_study3_extraversion

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
  (reused from the same cache directory). This is the codebook for a related MTurk
  moral-relevance norming study run on the same item pool, keyed to standard BFI-2 item
  numbers (`mv.BFI2.<n>`), and gives verbatim lowercase item text plus facet labels for
  all 60 BFI-2 items -- including a `Trait` column with the official facet name
  (Sociability, Assertiveness, Energy Level, etc.), which directly confirmed the
  Extraversion facet structure for this table with no need to consult an outside BFI-2
  source.

## has_bare_integer_items
FALSE, as stated in the dictionary row. `item` values are named codes (`itbfi21`,
`itbfi216`, `itbfi221`, `itbfi226`, `itbfi241`, `itbfi251`), not bare integers. As with
the sibling `study1_dependability` and `study3_openness` tables, the codes still required
decoding (they are not self-evidently BFI-2 item text), so the same reconstruction rigor
was applied.

## Structure discovered
Ground truth (read directly via `readRDS`, exact strings printed):
`item` = `"itbfi21" "itbfi216" "itbfi221" "itbfi226" "itbfi241" "itbfi251"` (6 items),
`resp` = `1 2 3 4 5`, N rows = 2622 (matching the sibling openness/dependability tables'
row count, consistent with the same set of targets/informants).

The paper's Study 3 "Informant-Reported Nonmoral Personality Traits" subsection (p.
1172-1173 of the printed pagination, `sun_2025_paper.txt` lines ~874-880) states: "we
obtained informant reports of three nonmoral personality traits: extraversion (e.g.,
'Is outgoing, sociable'), neuroticism (e.g., 'Worries a lot'), and openness (e.g., 'Has
little creativity' [r]). For each of these traits, informants rated six statements from
the BFI-2-S (Soto & John, 2017b) using a 5-point scale anchored by strongly disagree
and strongly agree." This independently confirms: (a) exactly 6 extraversion items,
matching the ground truth's 6-item set; (b) the response format (5-point, strongly
disagree/strongly agree anchors) -- identical instructions text to the sibling
`study3_openness` table, since all three "nonmoral personality trait" measures share one
administration paragraph; (c) one specific item verbatim ("Is outgoing, sociable"),
which must correspond to one of the 6 codes.

### Decoding itbfi2<NN> -> BFI-2 item <NN>
Applying the `itbfi2<NN>` = BFI-2 item `<NN>` convention established for
`study1_dependability` and confirmed again for `study3_openness`:
- `itbfi21`  -> item 1  -> Sociability   -> "is outgoing, sociable"
- `itbfi216` -> item 16 -> Sociability   -> "tends to be quiet"
- `itbfi221` -> item 21 -> Assertiveness -> "is dominant, acts as a leader"
- `itbfi226` -> item 26 -> Energy Level  -> "is less active than other people"
- `itbfi241` -> item 41 -> Energy Level  -> "is full of energy"
- `itbfi251` -> item 51 -> Assertiveness -> "prefers to have others take charge"

**On "itbfi21" specifically**: this is `itbfi2` + `1`, i.e. BFI-2 item 1, NOT item 21 and
NOT a typo. This is the same digit-count ambiguity flagged for `study3_openness`'s
"itbfi25" (`itbfi2` + single-digit item number prints as a short string, easily
misread as a two-digit item number). Two independent lines of evidence resolve it here,
mirroring the openness table's method:
1. **Direct textual match.** The paper's own example quote for the extraversion measure
   is "Is outgoing, sociable," which case-insensitively matches `mv.BFI2.1` in
   `normdat-labels.csv` exactly ("is outgoing, sociable"). This confirms `itbfi21` decodes
   to item 1 (not item 21 -- see facet check below for why item 21 is independently
   ruled out as `itbfi21`'s referent), and validates the `itbfi2<NN>` convention holds
   generally for this table.
2. **Domain/facet structure check.** The official 60-item BFI-2's Extraversion domain
   comprises exactly three facets: Sociability (items 1, 16, 31, 46), Assertiveness
   (items 6, 21, 36, 51), and Energy Level (items 11, 26, 41, 56) -- as given directly in
   `normdat-labels.csv`'s `Trait` column and independently matching the standard BFI-2
   facet structure (Soto & John, 2017). Decoding all 6 ground-truth codes as `itbfi2<NN>`
   -> item `<NN>` yields items {1, 16, 21, 26, 41, 51} -- exactly two items per
   Extraversion facet (1+16 from Sociability, 21+51 from Assertiveness, 26+41 from Energy
   Level). This is exactly the BFI-2-S (Soto & John, 2017b) short-form pattern (2 items
   per facet) and matches the paper's own statement that informants "rated six statements
   from the BFI-2-S" for extraversion. Reading `itbfi21` as item 21 instead of item 1
   would double-count Assertiveness (21, 21, 51 -- impossible/degenerate) and leave
   Sociability with zero items, breaking the clean 2-per-facet pattern and producing a
   contradiction (item 21 is already separately coded as `itbfi221`). Item 1 is the only
   reading consistent with `itbfi221` also being present as a distinct code and with the
   clean facet coverage.

Conclusion: `itbfi21` = BFI-2 item 1 ("is outgoing, sociable"), confirmed both by the
verbatim paper quote and by facet-structure necessity (item 21 is already claimed by the
`itbfi221` code, so `itbfi21` cannot also mean item 21). All 6 codes decode to items
{1, 16, 21, 26, 41, 51}, matching the facet hint given in the task brief exactly.

## Structure of output
One `section_id` (`sun_2025_morality_study3_extraversion_1`) for all 6 items, since they
share the same response instructions and instrument.

Per the instructions/section_prompt boundary rule: the whole-instrument response-format
framing ("Informants rated six statements from the BFI-2-S ... using a 5-point scale
anchored by strongly disagree and strongly agree") went in `instructions`, transcribed
close to verbatim from the paper -- identical text to `study3_openness`'s `instructions`
field, since both measures are described by the same sentence in the paper.

`section_prompt` was left **blank**, for the same reason documented in
`study3_openness`'s log: the paper's Nonmoral Personality Traits paragraph does not
restate the "[Target's name] is someone who..." stem that is explicitly stated only for
the moral-character (compassion/respectfulness/dependability) facets elsewhere in the
paper. No stem text was invented for this measure.

`option_text` populated only for resp 1 ("strongly disagree") and resp 5 ("strongly
agree") -- the paper states the scale is "anchored by" these two endpoints only; no
verbal labels for intermediate points 2-4 are given anywhere in the paper or OSF
materials, so those were left blank (same convention as `study1_dependability` and
`study3_openness`).

`correct_response` left blank throughout -- personality-trait rating measure, no scoring
key.

## OCR / image-based extraction
None needed. The source PDF is text-based (not scanned/image); `pdftotext -layout` output
was reused directly from the `study1_dependability` cache. No OCR used anywhere in this
extraction.

## Derived vs. directly-read values
- `item_text` for all 6 items is directly read from `normdat-labels.csv` (verbatim
  lowercase BFI-2 item-bank text keyed by item number and cross-tabbed with the official
  facet name), independently cross-checked against the one item quoted verbatim in the
  paper's own prose ("Is outgoing, sociable" -- case-folded match to item 1's codebook
  text). Not inferred from range-matching or facet-position guessing alone.
- The `itbfi2<NN>` -> BFI-2 item `<NN>` -> item-text chain is a decoding/inference, but
  one confirmed by two independent, mutually consistent lines of evidence (direct
  verbatim quote match for one item; full-set 2-per-facet Extraversion-domain structure
  matching the paper's explicit "six statements from the BFI-2-S" statement, plus the
  logical necessity that `itbfi21` != item 21 since `itbfi221` already occupies that
  slot), not assumed from the naming pattern alone.
- `instructions` is a close transcription of the paper's own sentence describing the
  rating task and response scale (identical source sentence to `study3_openness`).
- `option_text` anchors ("strongly disagree"/"strongly agree") are a direct,
  paraphrase-free read of the paper's stated scale anchors.
- `section_prompt` is a directly-read absence, not a derived value: left blank because no
  literal stem text could be found in the paper specifically for this measure (same
  reasoning as `study3_openness`).

## Source type used
Published journal article (author's open-access postprint PDF) as primary source for the
item count, response-scale anchors, and one verbatim example item text; cross-checked
against the dataset's own OSF repository (`data-clean/normdat-labels.csv`, a related
norming-study codebook using the same BFI-2 item numbering and facet labels) for the
literal text of all 6 items and their facet assignments.

## Ambiguities / items not extracted
- All 6 ground-truth items were extracted, mapped, and validated with exact `item`/`resp`
  set match against `.gt_sun_2025_morality_study3_extraversion.rds` (confirmed via
  `identical()` on the sorted unique sets).
- One discrepancy logged (see `pending_index_notes.csv`), same as `study3_openness`:
  `section_prompt` (item stem text, e.g. a possible "[Target's name] is someone who...")
  could not be confirmed for this specific measure and was left blank rather than assumed
  by analogy to the study1_dependability moral-character facets, which explicitly state
  that stem only for their own items.
