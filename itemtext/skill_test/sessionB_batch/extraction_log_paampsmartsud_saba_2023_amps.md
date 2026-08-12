# Extraction log: paampsmartsud_saba_2023_amps

## has_bare_integer_items
FALSE, as given in the dictionary row. Ground-truth `item` values are already
semantic codes (`AMPS_01`...`AMPS_15`), not bare integers, so no positional
reconstruction of which paper item maps to which `item` code was needed in the
usual sense — but see "Derived vs. directly-read values" below for how the
mapping was still empirically confirmed rather than assumed.

## Source used
- Target paper: Saba, S. K., & Black, D. S. (2023/2024). "Psychometric Assessment
  of the Applied Mindfulness Process Scale (AMPS) Among a Sample of Women in
  Treatment for Substance Use Disorder." *Mindfulness*. DOI
  10.1007/s12671-023-02144-1. Open-access full text at PMC12959836
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC12959836/). This paper states the AMPS
  is scored on "a 5-point Likert scale from 1 *never* to 5 *almost always*"
  (narrative paraphrase) but a companion measure-repository summary of the same
  scale states "0 to 4 with 0 for 'Never' to 4 for 'Almost always'" — the ground
  truth's actual 0-4 coding confirms the latter is correct and the paper's prose
  description of the endpoints ("1"/"5") is a non-literal paraphrase, not the
  scoring key.
- The Saba 2023 paper explicitly states "A list of all AMPS items is included in
  Supplemental Materials" rather than reprinting the 15 items in the body text.
  The supplemental file (`NIHMS2143772-supplement-Supplemental_Material.docx`,
  linked from the PMC page) could not be downloaded — the PMC binary-file host
  serves a JS/proof-of-work interstitial page instead of the file to non-browser
  clients (confirmed: fetched bytes were an HTML "Preparing to download..."
  challenge page, not a docx). Cached at
  `.cache/paampsmartsud_saba_2023_amps/supplement_FETCH_FAILED_challenge_page.html` (this is the HTML
  challenge page, not real content — kept only as a record of the failed
  fetch, not as a source).
- OSF project (https://osf.io/9jgxs/, DOI target from the dictionary row)
  contains only a `data/` folder with `amps psychometric eval.csv` — the raw
  wide-format response data, no instrument/questionnaire document. Cached at
  `.cache/paampsmartsud_saba_2023_amps/amps_data.csv`.
- Because the applied paper doesn't reprint the item text, item wording was
  taken from the AMPS's original validation paper, which the applied paper
  cites and reuses without modification: Li, M. J., Black, D. S., & Garland,
  E. L. (2016). "The Applied Mindfulness Process Scale (AMPS): A process
  measure for evaluating mindfulness-based interventions." *Personality and
  Individual Differences*, 93, 6-15. Open access at PMC4742344
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC4742344/), which reproduces the
  full 15-item scale, the shared item stem, the instructions paragraph, and the
  factor/subscale assignment in an appendix/table.

## Source type used
Web-rendered full-text HTML (via WebFetch) of two open-access PMC articles —
no PDF or scanned image was used for either the applied paper (PMC12959836) or
the original validation paper (PMC4742344). No OCR was involved anywhere in
this extraction (see next section).

## OCR / image-based extraction
None. All text (instructions paragraph, the 15-item stems, the shared
"I used mindfulness practice to..." prefix, and the 0=Never/4=Almost always
response anchors) was read directly from PMC's HTML article rendering, not
from a scanned image or PDF requiring OCR.

## Derived vs. directly-read values
- **Directly read, verbatim**: instructions paragraph, the shared item-stem
  prefix ("I used mindfulness practice to…"), all 15 item completions, and the
  0/Never and 4/Almost always response endpoint labels — all read directly
  from PMC4742344's appendix table.
- **Derived (verified empirically, not assumed)**: the mapping of `AMPS_01`..
  `AMPS_15` (the ground-truth `item` codes) onto the original scale's item
  numbers 1-15 (and hence onto the item text above) was checked directly
  against the actual raw data, not just assumed from naming convention. The
  OSF `amps_data.csv` file contains `AMPS_DECENT_SUM`, `AMPS_POSEMOREG_SUM`,
  and `AMPS_NEGEMOREG_SUM` subscale total columns alongside the 15
  `AMPS_01`..`AMPS_15` item columns. Summing `AMPS_01+03+12+13+15` (the
  published Decentering factor: items 1, 3, 12, 13, 15),
  `AMPS_04+07+09+11+14` (Positive Emotion Regulation: 4, 7, 9, 11, 14), and
  `AMPS_02+05+06+08+10` (Negative Emotion Regulation: 2, 5, 6, 8, 10)
  reproduced the corresponding `_SUM` columns exactly, row for row, for the
  S3 wave. This confirms `AMPS_01`..`AMPS_15` follow the original 1-15 item
  numbering from Li et al. (2016), not some other order — a much stronger
  check than range/plausibility matching.
- **Response-option labels for resp 1/2/3**: not derived — left blank
  (`option_text = ""`) because neither PMC4742344 nor the Saba 2023 paper
  discloses verbal anchors for the three interior scale points, only the two
  endpoints (0=Never, 4=Almost always). This mirrors the sessionB model
  example (`firstborn_personality`), which also leaves interior Likert points
  unlabeled when the source doesn't label them, rather than inventing labels.

## Structure of output
Single `section_id` (`paampsmartsud_saba_2023_amps_amps`) covering all 15
items — the AMPS has no testlet/passage structure, just one shared
instructions paragraph and one shared item stem, so `section_prompt` is blank
throughout and the whole-instrument framing goes in `instructions` per the
skill's instructions/section_prompt boundary rule.

## Items not extracted
None — all 15 ground-truth items (`AMPS_01`-`AMPS_15`) and all 5 ground-truth
resp values (0-4) were extracted and matched exactly against
`irw::irw_fetch("paampsmartsud_saba_2023_amps")` (cached ground truth
`.gt_paampsmartsud_saba_2023_amps.rds`):
- `unique(item)` match: TRUE (15/15)
- `unique(resp)` match: TRUE (0/1/2/3/4, integer-vs-numeric storage type only)

## Ambiguities / caveats for the human reviewer
- The literal instructions/stem text used is from the *original 2016 AMPS
  validation paper*, not reprinted verbatim in the 2023 SUD-sample paper
  (whose only disclosure was "past week" framing, consistent with but not
  identical in wording to "the last week (past 7 days)" from 2016). Since
  Saba 2023 explicitly cites AMPS as an unmodified, previously validated
  instrument and doesn't describe any wording changes, using the original
  item text is treated as correct, not as a discrepancy requiring a
  `pending_index_notes.csv` entry.
