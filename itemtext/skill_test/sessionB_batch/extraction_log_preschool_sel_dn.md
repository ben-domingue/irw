# Extraction log: preschool_sel_dn

## Source used
Same LDbase dataset page as `preschool_sel_wj` and `preschool_sel_pl`:
`https://ldbase.org/datasets/38d4a723-c167-4908-a250-2cf29a4ff49b` ("Preschool Social
and Emotional Development Study—Connecticut Dataset," Bailey et al., LDbase, DOI
10.33009/ldbase.1680213217.8ed0). Reused the study's own public child-level codebook
already cached from the `preschool_sel_wj` extraction at
`itemtext/skill_test/sessionB/.cache/preschool_sel_wj/codebook.txt` (no re-fetch
needed) — the "Day & Night (DN) Stroop" section (codebook pp. 38-40, lines ~1689-1841
of the pdftotext output) covers every `dn_*_t1` variable in full: variable label
(literal item stem + which stimulus card) and value-label anchors for every trial.

## What "DN" stands for
Confirmed against the codebook's instrument-summary table (p. 7 of the PDF, line 212):
**"Day–Night Task (DN)"** — the classic day-night Stroop-like interference-control task
(Gerstadt, Hong, & Diamond, 1994, *Cognition*, 53(2), 129-153), NOT "Denver" — no Denver
II or other Denver-named instrument appears anywhere in the codebook under a `dn_`
prefix. The codebook's own description: "The Day–Night (DN) measures children's
interference control, which is their ability to ignore an internal or an external
prompt, and to perform an alternative action."

## Is item-level content publicly disclosable?
Yes, unlike `preschool_sel_wj` (WJ-IV, commercial/proprietary, withheld) and more like
`preschool_sel_pl` (PreLAS, commercial but codebook-disclosed). The Day-Night task is a
non-commercial, freely-described research paradigm from a 1994 journal article (not a
commercially published/copyrighted test kit like WJ-IV or PreLAS) — the literal item
prompt ("What do you say for this one?") plus the stimulus identity (sun card / moon
card) for each of the 14 trials is spelled out directly in the study's own codebook, so
there is no copyright-hygiene concern analogous to the WJ-IV/PreLAS cases. No leaked or
third-party administration manual was sought or needed.

## Source type used
Study's own public IES-funded codebook (same source type as `coach_chen_2022_phq9`,
`preschool_sel_wj`, `preschool_sel_pl`), not a separate task manual — none is needed
since the codebook itself fully documents the item-level content for this measure.

## OCR / image-based extraction
None. All text came from the pre-existing `pdftotext` output (`codebook.txt`, produced
during the `preschool_sel_wj` extraction), not from image/OCR extraction of the PDF.

## Derived vs. directly-read values
- `item_text` — directly read from the codebook's "Variable Label" column for each
  `dn_*_t1` variable, e.g. `dn_1_t1` = "What do you say for this one? (moon card)",
  `dn_2_t1` = "What do you say for this one? (sun card)". The moon/sun card identity per
  item was read directly (not inferred) from each variable's codebook row:
  dn_1=moon, dn_2=sun, dn_3=moon, dn_4=sun, dn_5=sun, dn_6=moon, dn_7=moon, dn_8=sun,
  dn_9=moon, dn_10=sun, dn_11=sun, dn_12=moon, dn_13=sun, dn_14=moon.
- `correct_response` — set to `"2"` uniformly for all 14 items, directly reflecting the
  codebook's stated anchor "2 = Correct" (the only anchor denoting a correct response).
- `option_text` — the codebook gives *four* raw anchor labels per item that collapse
  onto only *three* distinct `resp` values actually present in the live data (0, 1, 2):
  "0 = Incorrect response" and "0 = No response" both map to `resp=0`; "1 = Similar
  word" and "1 = Self-correct" both map to `resp=1`; "2 = Correct" maps to `resp=2`.
  This is a directly-read (not derived/invented) collapse — the codebook itself assigns
  both labels to the same numeric code within each item's anchor block. Combined the two
  literal labels per collapsed value with " / " rather than picking one arbitrarily or
  inventing new wording: `resp=0` -> "Incorrect response / No response", `resp=1` ->
  "Similar word / Self-correct", `resp=2` -> "Correct".
- `instructions` — the codebook's one-sentence instrument description (quoted above, p.
  7 of the codebook), used directly, citing Gerstadt, Hong, & Diamond (1994). This is a
  description of what the task measures, not a literal examiner administration script
  (the actual scripted framing given to the child, e.g. "For this game, when you see
  this card you say...", is not present in the codebook) — flagged as such rather than
  presented as a verbatim admin script, same handling as `preschool_sel_pl`.
- `section_id` — a single shared id (`preschool_sel_dn_1`) for all 14 items; there is no
  testlet/shared-passage structure (each trial is a self-contained card-naming prompt),
  so `section_prompt` is blank throughout, consistent with the skill's "no grouping ->
  blank section_prompt" guidance.

## has_bare_integer_items
FALSE, confirmed: all 14 ground-truth items are named codes (`dn_1_t1`...`dn_14_t1`),
not bare integers requiring positional reconstruction — the codebook's own variable
names line up directly with the IRW `item` values (only the practice-trial variables
`dn_p11_t1`, `dn_p12_t1`, `dn_p21_t1`, `dn_p22_t1`, `dn_p31_t1`, `dn_p32_t1` and the
assent/session/scoring variables were excluded, since they are not in the live `item`
set).

## Copyright note
The Day-Night task (Gerstadt, Hong, & Diamond, 1994) is a non-commercial, freely
published research paradigm described in a peer-reviewed journal article — not a
proprietary/copyrighted commercial test kit like WJ-IV or PreLAS 2000. No copyright
concern applies; all text used is the study's own public codebook documentation.

## Validation result
Exact match. `unique(item)` (14 values: `dn_1_t1`..`dn_14_t1`) and `unique(resp)`
(0, 1, 2) from `candidate_preschool_sel_dn.rds` match the cached ground truth
(`.gt_preschool_sel_dn.rds`) exactly.

## Items not extracted
None — all 14 ground-truth items x 3 resp values (42 rows) were populated with
item_text, option_text, correct_response, instructions, and section_id; full coverage,
no entries in `pending_index_notes.csv` needed for this table.
