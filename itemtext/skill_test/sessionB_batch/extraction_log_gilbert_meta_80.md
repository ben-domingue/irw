# Extraction log: gilbert_meta_80

## Source type used
- LDbase dataset page: `https://ldbase.org/datasets/de4bf144-39ed-430c-862d-201009d3d33e`
  (Cabell, Kim, White, Gale, Edwards, Hwang, et al., 2024, *Journal of Educational
  Psychology*, DOI 10.1037/edu0000916 — "Impact of a content-rich literacy curriculum on
  kindergarteners' vocabulary, listening comprehension, and content knowledge").
- The dataset's own codebook (`.docx`/converted `.txt`, cached from a prior session at
  `.cache/gilbert_meta_80/codebook.docx` / `codebook.txt`, both reused as-is — no
  re-fetch performed this session) documents every `wj_pv_NN_F`/`wj_pv_NN_S` variable
  (Fall/Spring administration) with: a variable label of the form `WJ PV: N. <word>`
  (the picture-naming target word for that item) and a value-label table giving the 0/1
  scoring: `0 = Incorrect/no response`, `1 = Correct`, uniformly across every `wj_pv_*`
  item.
- No open-access preprint search was performed beyond the LDbase page/codebook already
  in cache; the codebook alone was sufficient to identify the instrument and item
  numbering with high confidence.

## has_bare_integer_items
`FALSE`, confirmed. Ground-truth `item` values are already named codes (`wj_pv_01` …
`wj_pv_42`, with gaps), not bare integers, so no positional/order reconstruction was
needed — the codebook's `wj_pv_NN_F` variable names map 1:1 onto the ground truth's
`wj_pv_NN` (the `_F`/`_S` Fall/Spring suffix is dropped in the live table, consistent
with `wave` being carried as its own column rather than baked into `item`).

## OCR / image-based extraction
None. The codebook was already machine-readable text (`.docx` → `.txt`), no OCR was
required. No item images (picture stimuli) were extracted, viewed, or needed — see
copyright note below.

## Derived vs. directly-read values
- `item`, `resp`: read directly from ground truth (`.gt_gilbert_meta_80.rds`), not
  derived — confirms exactly against the codebook's `wj_pv_NN_F`/`_S` variable list
  (numbers 01–44 exist in the codebook; ground truth uses only 01–31, 33–36, 42 — the
  36-item subset actually retained in the live IRW table, likely fewer than the full WJ
  PV item bank due to basal/ceiling discontinue rules dropping some numbers, matching
  the pattern already seen in `preschool_sel_wj`).
- `correct_response`: directly read from the codebook's per-item variable label (the
  target picture-naming word, e.g. item `wj_pv_01` → "fork", `wj_pv_02` → "fish"). This
  is the codebook's own disclosed scoring anchor/target, not a derived/guessed value.
- `option_text`: directly read from the codebook's value-label table for each
  `wj_pv_NN_F` variable (`0 = Incorrect/no response`, `1 = Correct`), which is uniform
  across every item in the codebook — verified by spot-checking items 1, 2, 30–44.
- `item_text`, `instructions`, `section_prompt`: left `NA` — not derived, not guessed.
  See copyright note below for why.
- `instrument`: "Woodcock-Johnson IV (WJ-IV) Tests of Achievement: Picture Vocabulary
  subtest" — identified with high confidence from the codebook's variable labels
  ("WJ, Picture Vocabulary: ...") and is a standard, named, commercially published test;
  not itself sensitive to disclose (only its item content/stimuli are restricted).
- `section_id`: single value `gilbert_meta_80_1` for all rows (no testlet/passage
  grouping in this instrument — it's a flat picture-naming item set), per the skill's
  rule to still emit a join-key column rather than omit it.

## Copyright-hygiene note (WJ-IV Picture Vocabulary, commercial/copyrighted instrument)
The WJ-IV is a commercially published, actively-sold cognitive/achievement battery
(Riverside Insights); the actual test stimuli are picture cards/images bound in the
proprietary test book, and the standardized administration script lives in the
examiner's manual — neither was sought out, viewed, or used. Per the task instructions
and the `preschool_sel_wj` precedent (same WJ-IV family, see
`../sessionB/extraction_log_preschool_sel_wj.md`), no search for a leaked/pirated copy
of the WJ-IV manual or item images was performed.

What *was* used is the study's own already-public LDbase codebook — the standard source
type this pipeline transcribes from. That codebook discloses two things for each item:
(a) the target word the pictured object represents (used here as `correct_response`,
since it functions as the scoring key/target, not the visual stimulus itself), and
(b) the generic 0/1 "Incorrect/no response" / "Correct" scoring labels. Neither of these
reconstructs or reproduces the proprietary picture stimuli or the examiner's verbal
script. Because the actual item stimulus (the picture itself, and any standardized
prompt wording like "What is this?") is not disclosed anywhere in the public codebook or
the published paper, `item_text`, `instructions`, and `section_prompt` are left blank
(`NA`) rather than paraphrased or invented — this is a deliberate, disclosed gap, not an
oversight.

## Ambiguities / discrepancies
None on item/resp coverage — the codebook's item set is a strict superset of ground
truth's 36-item, 2-response-level structure, and the mapping between codebook variable
names and ground-truth `item` values is unambiguous (identical numbering, `_F`/`_S`
suffix dropped). The only limitation is the expected one: item-level stimulus text
(`item_text`) is not extractable from any public source due to test-security copyright
restrictions on the WJ-IV.

## Items not extracted (item_text)
All 36 items — `item_text`, `instructions`, and `section_prompt` are `NA` for every row.
`item`, `resp`, `correct_response`, and `option_text` are populated for all 36 items /
72 rows (36 items × 2 response levels).
