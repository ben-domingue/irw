# Extraction log: kfcovid_pss_li2020

## Source used
- Paper: Li, D. C. Y., & Leung, L. (2020). Psychometric data on knowledge and fear of
  coronavirus disease 2019 and perceived stress among workers of filipino origin in Hong
  Kong. *Data in Brief*, 33, 106395. DOI 10.1016/j.dib.2020.106395. Open-access; fetched
  via PMC (https://pmc.ncbi.nlm.nih.gov/articles/PMC7546663/). The main text states the
  instrument is "the Short Form Perceived Stress Scale (PSS-4)" with "four items" and "a
  five-point Likert scale" (Cronbach's alpha 0.89), but does **not** reproduce the item
  wording or response-option labels in the article body or its tables.
- OSF project https://osf.io/m2v3h/ contains exactly one file:
  `Knowledge and Fear of COVID-19 and Perceived Stress.xlsb` (download link
  https://osf.io/download/g3ntr/), cached at
  `.cache/kfcovid_pss_li2020/kfcovid_data.xlsb`. This is the raw-data workbook, not a
  separate questionnaire PDF, but it contains a `Survey 3` sheet (literal PSS-4 item
  wording + response-option text in presentation order) and a `Codebook` sheet
  (per-column `Q1001`-`Q1004` documentation) that together fully disclose the item text,
  option text, and item→column mapping.

## OCR / image-based extraction
Not needed. The `.xlsb` file was read directly and losslessly with Python's `pyxlsb`
library (`open_workbook` / sheet `.rows()`); all text below was read as native cell
strings, not transcribed from an image or PDF scan.

## Derived vs. directly-read values
None of the extracted values were derived or computed. `item_text` and `option_text` are
copied verbatim from the `Survey 3` and `Codebook` sheets; `resp` values (0-4) and `item`
values (1001-1004) are copied verbatim from the `Codebook` sheet's `Code`
(`Q1001`...`Q1004`, stripped of the `Q` prefix per the ground-truth numbering) and
`Set of Possible Responses` columns, and cross-checked against the `DataSet` sheet's
column headers, which use the identical `Q1001`...`Q1004` names in the identical
left-to-right order as `Survey 3`'s row order.

## Source type used
Raw-data-file column headers/codebook (the OSF-hosted `.xlsb` workbook's `Codebook` and
`Survey 3` sheets), not the paper PDF/appendix — the paper itself discloses only the
instrument name and psychometric summary stats, not the item text.

## Bare-integer validation check
`has_bare_integer_items = TRUE` (ground-truth `item` values are `1001`-`1004`, not named
codes). Validation performed:
1. The `DataSet` sheet's column header row lists `Q1001, Q1002, Q1003, Q1004` immediately
   after the Fear-of-COVID-19 block (`Q101`-`Q107`) and the Knowledge block (`Q1`-`Q12`),
   confirming these are the "Survey 3" (Perceived Stress) block, consistent with the
   "kfcovid_pss" table name and the paper's stated three-survey structure
   (Knowledge / Fear / Perceived Stress).
2. The `Codebook` sheet gives, for each of `Q1001`-`Q1004`, an explicit "Survey" number
   (`3`), the literal question text, and the literal response-option coding
   (`0 - Never; 1 - Almost never; 2 - Sometimes; 3 - Fairly often; 4 - Very Often`).
3. The `Survey 3` sheet independently lists the same four questions in the same order
   (rows 1-4, "Questions" column), with matching `Choice of Options` text and a computed
   `Average Score` per item — a second, independent presentation-order source that agrees
   exactly with the `Codebook` ordering.
4. Because both the codebook *and* the raw-data column headers (not just item content/
   range plausibility) independently confirm the `Q1001`→row-1, `Q1002`→row-2, ...
   `Q1004`→row-4 mapping, this satisfies the skill's requirement to cross-check
   presentation order/position rather than relying on range-matching alone (all four PSS
   items share the same 0-4 range, which would not have discriminated between them).
   Result: mapping confirmed exactly, no ambiguity.
5. Final validation in R: `identical(sort(unique(candidate$item)), sort(unique(gt$item)))`
   → TRUE; `identical(sort(unique(candidate$resp)), sort(unique(gt$resp)))` → TRUE.

## Structure discovered
- Single instrument, single section (`kfcovid_pss_li2020_1`) — all 4 items share one
  short, ungrouped self-report scale; no testlet/passage structure, so `section_prompt`
  is blank per item.
- `instructions` left blank: neither the paper nor the raw-data workbook discloses a
  separate instrument-level preamble/instruction sentence distinct from each item's own
  "In the last month how often have you felt..." stem — that stem is already embedded in
  each `item_text`, matching the source's own terseness (no synthetic instruction text was
  added).
- `option_text` uses the workbook's own labels ("Never" / "Almost never" / "Sometimes" /
  "Fairly often" / "Very often"), title-cased as given in the `Codebook` sheet (the
  workbook itself is inconsistent — `Survey 3` sheet lowercases "almost never"/"sometimes"/
  etc. while `Codebook` capitalizes them; `Codebook`'s capitalization was used since it is
  the more formal/canonical of the two internally-consistent sources).
- `correct_response` blank throughout — perceived-stress items have no scoring key.

## Ambiguities
- The item wording as disclosed by this dataset is **not verbatim identical** to the
  commonly-cited PSS-4 (Warttig et al., 2013) item set. In particular, item `1002`
  ("...you lack confidence about your ability to handle your personal problems?") is
  phrased as a straight/forward-scored item here, whereas the standard published PSS-4
  phrases the analogous item as "felt confident about your ability to handle your
  personal problems" and reverse-scores it. This is the paper/dataset's own disclosed
  wording (used verbatim, per source-fidelity — not corrected to the "standard" wording),
  so it is flagged here rather than silently reconciled; it does not affect item/resp
  validation since text is taken from the primary raw-data source for this specific study,
  not assumed from the generic PSS-4 template.
- Trailing whitespace/tab characters present in the raw `Choice of Options` strings in the
  `Survey 3` sheet (e.g. `"3=fairly often\t"`) were treated as formatting noise and not
  reproduced in `option_text`.

## Items not extracted
None — all 4 ground-truth items (`1001`-`1004`) and all 5 ground-truth `resp` values
(`0`-`4`) were extracted and validated exactly against
`.gt_kfcovid_pss_li2020.rds`.
