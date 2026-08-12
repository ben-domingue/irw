# Extraction log: gilbert_meta_8

## Repo script check
`grep -rli "RKBVKY\|gilbert_meta_8\|Time to transfer\|spiraled content literacy" data/` returned
no matches for this specific table. Three loosely-named `gilbert_*` scripts exist
(`data/gilbert_86through87.R`, `data/gilbert_meta_83through85.R`, `data/gilbert_77through82.R`)
but none reference `RKBVKY`, `s_cc`, or this paper — no existing IRW processing script for
this table in this repo.

## Ground truth (verified directly, not assumed from the task prompt)
`readRDS(".gt_gilbert_meta_8.rds")`: 37,182 rows, columns
`id, cluster_id, block_id, item, resp, treat, tot, std_baseline, cov_black_num,
cov_hispanic_num, cov_other_num, cov_male_num, cov_lep_num, cov_iep_num, cov_ses_low,
cov_ses_med, cov_ses_high`. 1,335 unique `id`.

`sort(unique(item))` — confirmed exactly 29 items:
`s_cc_2_2021, s_cc_3_2021, s_cc_4_2021, s_cc_5_2021, s_cc_6_2021, s_cc_7_2021,
s_cc_8_2021, s_cc_9_2021, s_cc_10_2021, s_cc_11_2021, s_cc_14_2021, s_cc_15_2021,
s_cc_16_2021, s_cc_17_2021, s_cc_18_2021, s_cc_19_2021, s_cc_20_2021, s_cc_21_2021,
s_cc_22_2021, s_cc_23_2021, s_cc_26_2021, s_cc_27_2021, s_cc_28_2021, s_cc_29_2021,
s_cc_30_2021, s_cc_31_2021, s_cc_32_2021, s_cc_33_2021, s_cc_34_2021`
— i.e. raw item numbers 2-34 with 1, 12, 13, 24, 25 missing (five gaps). `resp` in `{0, 1}`.
`has_bare_integer_items = FALSE` (as given) — items already carry semantic labels
(`s_cc_<n>_2021`), so no position/order reconstruction of item *identity* was needed.

## Source located: EdWorkingPapers open-access preprint (paper itself confirmed, not guessed)
Dataverse (`dataverse.harvard.edu`, doi:10.7910/DVN/RKBVKY) was not attempted directly this
run — per the task brief, every `gilbert_meta_*` table tried so far in this batch series has
hit the same AWS WAF bot-challenge (HTTP 202, `x-amzn-waf-action: challenge`) on that host, so
time was spent on the DataCite/paper route instead.

1. **DataCite metadata API** (`api.datacite.org/dois/10.7910/DVN/RKBVKY`, not WAF-blocked) —
   returned HTTP 200. Title: "Replication Data for: Time to Transfer: Long-Term Effects of a
   Sustained and Spiraled Content Literacy Intervention in the Elementary Grades." Description
   confirms this Dataverse record backs the Developmental Psychology paper named in the
   dictionary row exactly. Cached at `.cache/gilbert_meta_8/datacite.json`. (No file-level
   listing available via this endpoint, same limitation noted in the `gilbert_meta_38` log.)
2. **EdWorkingPapers** (`edworkingpapers.com/ai23-769`) — open-access working-paper version of
   the exact same paper (Annenberg Institute, DOI 10.26300/t3c6-xh48). PDF fetched directly:
   `https://www.edworkingpapers.com/sites/default/files/ai23-769.pdf` (HTTP 200, 1.7 MB).
   Cached at `.cache/gilbert_meta_8/ai23-769.pdf` / `.txt` (via `pdftotext`, text layer native,
   no OCR needed).

## What the paper discloses (Methods + embedded Online Supplementary Materials)

- **"Domain-Specific (Science) Reading Comprehension"** (Methods, p.25): "We developed near-,
  mid-, and far-transfer domain-specific (science) reading comprehension passages and **29
  multiple-choice questions** to assess students' ability to read and understand main ideas
  and scientific concepts in those science passages." This is a direct, literal confirmation
  of the item count — **29**, matching the live ground-truth item count exactly.
- Cronbach's alpha: full assessment .86; near-transfer passage .72, mid-transfer .63,
  far-transfer .68.
- The three reading passages themselves are given verbatim in the embedded OSM appendix
  ("Domain-Specific (Science) Reading Comprehension Passages and Psychometric Properties"):
  (A) Near Transfer — macaque monkey heart-attack recovery/stem-cell study; (B) Mid Transfer —
  North American migratory birds' skeletal/muscular adaptation; (C) Far Transfer — anatomy of
  a skyscraper (no directly-taught vocabulary). All three ~299-300 words, Lexile 610L-800L.
  Full text cached in `.cache/gilbert_meta_8/ai23-769.txt` (lines ~2770-2860).
- A 2PL item-parameter table ("2PL Item Characteristic Curves", Content Comp.) lists
  discrimination/difficulty for items indexed **1 through 29 sequentially** — this is the
  paper's own internal re-numbering of the 29 retained items for the psychometric write-up,
  not the raw variable-name numbering. It is consistent with (but does not itself confirm)
  the raw-data pattern of items 1-34 minus 5 dropped items (1, 12, 13, 24, 25) = 29 retained,
  the same "drop low-functioning items from a larger numbered pool" pattern documented for
  the companion `gilbert_meta_2` study (Mosher et al. 2024 dropped 1 of 21 items citing Kim
  et al. 2022).

## What the paper does NOT disclose
- **No literal multiple-choice question stems or answer options** for any of the 29 items.
  Searched for "multiple choice", "correct answer", "choose the", "which of the following",
  and inspected the full OSM/psychometrics appendix text — only passage text and aggregate
  item-parameter statistics (discrimination, difficulty) are given, never the question
  wording itself. This matches the established pattern for this research group's secure,
  researcher-designed assessments already documented in this batch's `gilbert_meta_2`,
  `gilbert_meta_12`, and `gilbert_meta_104` logs.
- **No stated item-to-passage mapping.** Unlike the companion `gilbert_meta_2` study (whose
  Mosher et al. 2024 paper states an explicit 7/7/6 near/mid/far item split), this paper gives
  no per-passage item count or any stated correspondence between the raw `s_cc_<n>_2021`
  item numbers (or the paper's internal 1-29 psychometric index) and which of the three
  passages a given item belongs to. Per SKILL.md's guidance (range/count plausibility alone
  is not sufficient validation for reconstructing structure), this mapping was **not**
  guessed and the three passages are therefore **not** encoded as `section_prompt` for any
  item — doing so would require asserting an item-section link that isn't supported by any
  located source.

## Structure of output
Same 10-column shape as `candidate_firstborn_personality.rds` (`table, section_id, item,
instrument, instructions, section_prompt, item_text, correct_response, option_text, resp`),
one row per (item, resp) — 29 items x 2 resp values = 58 rows.

- `table` = `"gilbert_meta_8"` throughout.
- `section_id` = `"gilbert_meta_8_<item>"` — one trivial section per item (SKILL.md's fallback
  for "no confirmable testlet/passage grouping"), the same choice made for `gilbert_meta_2`
  and for the identical reason: a 3-passage grouping exists conceptually but the item-passage
  assignment could not be confirmed.
- `instrument` = one descriptive string (with paper citation) repeated on every row.
- `instructions`, `section_prompt`, `item_text`, `correct_response`, `option_text` = `""`
  (empty string) on every row — none of these literal-text fields could be recovered for any
  individual item, despite the passages themselves being available (see rationale above for
  why they're withheld rather than attached to items without a confirmed mapping).
- `item` = exact ground-truth strings (`s_cc_2_2021` ... `s_cc_34_2021`, 29 values).
- `resp` = `0` / `1` (matching `irw_fetch`/ground-truth type and values exactly).

## has_bare_integer_items = FALSE
Confirmed: ground-truth `item` values are semantic labels (`s_cc_<n>_2021`), not bare
integers, so SKILL.md's bare-integer reconstruction procedure (position/order inference) does
not apply here. The item *identity* is already unambiguous; the open question was purely
whether the *literal question wording* behind each label could be recovered, and it could not.

## OCR / image-based extraction
Not needed. The EdWorkingPapers PDF has a native, machine-readable text layer — extracted
cleanly with `pdftotext`, no scanned/image-only pages encountered, no OCR step required.

## Derived vs. directly-read values
- `item` (29 values) and `resp` (0/1) were **directly read** — copied verbatim from the
  ground-truth object (`.gt_gilbert_meta_8.rds`), not transformed or recoded in any way.
- `instrument` is a **derived/composed** descriptive string (paper title + item count +
  citation) built from directly-read facts in the paper (29-item count, passage names,
  citation), not itself a literal quotation from the source.
- No `item_text`, `option_text`, `correct_response`, `instructions`, or `section_prompt`
  value was derived, estimated, or reconstructed and then included in the output — all are
  left blank because the literal source text could not be recovered, following the
  post-hoc correction precedent set in `gilbert_meta_38` (leave blank rather than infer).

## Source type used
- **DataCite metadata API** (`api.datacite.org`) — confirmed the Dataverse record's identity
  and that it backs the correct Developmental Psychology paper.
- **Open-access working-paper PDF** (EdWorkingPapers `ai23-769.pdf`, native text layer via
  `pdftotext`) — used for the Methods section (29-item count, Cronbach's alphas) and the
  embedded Online Supplementary Materials (verbatim passage text for all three transfer
  passages, 2PL item-parameter table).
- **Harvard Dataverse dataset page**: not attempted directly this run (known WAF block per
  task brief, consistent with every other `gilbert_meta_*` table logged in this batch).

## Validation
`unique(item)` in `candidate_gilbert_meta_8.rds` matches `readRDS(".gt_gilbert_meta_8.rds")`
exactly (29 items, `setequal` and sorted-`identical` both TRUE — checked in
`build_gilbert_meta_8.R`). `unique(resp)` matches exactly (`{0, 1}`). This is an **exact**
match on the structural (item/resp) validation gate. Item-level text content (`item_text`,
`option_text`, `correct_response`) is a logged, flagged gap — genuinely not disclosed in any
located public source — not a structural discrepancy.

**Overall: exact structural match; item/response-option wording not recoverable and left
blank, consistent with `gilbert_meta_2`/`_12`/`_104` in this same batch.**
