# Issue #1618 — `pezzuti_2025_coolpeople_main_big5_southkorea`

## Root cause

Not an item-code collision. The source SPSS file
(`Data_main experiment_13 countries_July 2 2024.sav`) contains **ten** Korean
BFI-10 columns, but one is misspelled: `koean_big5_art` (missing the `r`),
labelled "예술에 대한 관심이 별로 없다" — *has little interest in art*.

`data/pezzuti_2025_coolpeople.do:526` selected columns with
`keep id cov_* korean_big5_*`. That wildcard never matched the misspelled
column, so the Openness item was dropped before the hardcoded nine-name
`question_cols` list was reached. `korean_big5_faults` was always a single
question; the curated itemtext entry listed two texts under it because the
curator correctly found both BFI-10 texts in the source and had only nine
item codes to attach them to.

## Fix applied to the script

`data/pezzuti_2025_coolpeople.do` — added the misspelled column to the keep,
renamed it to `korean_big5_art` for consistency with its eight siblings, and
added it to the reshape and drop lists.

## Files here

- `pezzuti_2025_coolpeople_main_big5_SouthKorea.csv` — regenerated response
  table, **10 items / 2,940 rows / 294 ids** (was 9 / 2,646 / 294).
- `pezzuti_2025_coolpeople_main_big5_SouthKorea__items.csv` — corrected
  itemtext, 10 items x 7 resp levels = 70 rows. `korean_big5_faults` now
  carries only "Good at seeing other's faults."; "Has little interest in art."
  moves to `korean_big5_art`. All other texts are the previous curation
  verbatim.
- `build.py` / `itemtext.py` — how each was produced.

## Uploaded

Both are live in the **unreleased `next`** draft of their datasets, awaiting
your release:

| target | dataset | table | before | after |
|---|---|---|---|---|
| responses | `datapages.item_response_warehouse_2:epbx:next` | `pezzuti_2025_coolpeople_main_big5_SouthKorea` | 2,646 rows / 9 items | **2,940 / 10** |
| itemtext | `bdomingu.irw_text:07b6:next` | `pezzuti_2025_coolpeople_main_big5_southkorea__items` | 84 rows / 9 items | **70 / 10** |

Uploads append rather than replace once a version is released, so each draft
table was deleted and recreated. Neither had a description, so nothing was
lost. Verified with `COUNT(*)` queries, not `numRows`:

- responses: 2,940 rows / 294 ids / 10 items; every item 294 rows, 266
  answered, range 1-7.
- itemtext: 70 rows / 10 items, exactly 7 per item, one `item_text` each.
- join key: 10 items on both sides, 10 matched, 0 orphans either direction.

The itemtext dropped from 84 to 70 rows because the live version contained
**14 exactly-duplicated rows** (the whole `korean_big5_faults` block was
present twice, for both texts). The rebuild emits each item x resp level
once. All 63 distinct live rows that should survive are present unchanged.

## Why the CSV was built in Python

Stata is not installed on this machine, so the `.do` could not be re-run.
`build.py` reimplements the `.do`'s main-dataset preamble (lines 13-56) and
its Bookmark #10 block, including Stata's `export delimited` behaviour of
writing *value labels* (hence `cov_gender` is "Male"/"Female"), and the
`gen resp2 = resp` step that strips the label from `resp` so it exports
numeric.

**If Stata is available, prefer re-running the patched `.do`** and use this
CSV only as a cross-check.

## Validation of the Python reproduction

- 294 ids, 294 rows per item — matches the live table's counts.
- 266 complete-case respondents, `cov_gender` 175 Female / 91 Male — matches
  `irw_site/vignettes/gender_dif_data/pezzuti_2025_coolpeople_main_big5_SouthKorea.rds`
  (`n_persons = 266`, `group_ns = 175, 91`) exactly.
- `korean_big5_art` has the same 266 non-missing responses as its nine
  siblings, on the same 1-7 scale (mean 3.59, all levels used), and carries
  identical source value labels (1 = 전혀 동의 하지 않는다, 7 = 매우 동의한다),
  matching the curated `strongly disagree` / `strongly agree` anchors.
- Every `item` in the itemtext table is present in the response table and
  vice versa.

## Notes / not changed

- The 28 ids per item with empty `resp` (294 rows vs 266 answers) are Korean
  respondents who finished the survey but skipped the whole BFI block. They
  are present in the current live table too; reproduced as-is rather than
  silently dropped.
- The casing split is left as-is: the response table is named
  `..._SouthKorea`, the itemtext table `..._southkorea__items`, and the
  itemtext `table` column holds `..._SouthKorea`. This is what the live data
  already did and the join works across it; the mismatch is separately
  tracked in `fixes/itemtext_name_mismatches.csv`.
- The `.sav` supplies a verbatim Korean section stem
  ("당신이 떠올린 사람에 관련된 다양한 특성에 얼마나 동의 하시는지...") that
  could populate `section_prompt`, currently blank. Left blank to stay
  consistent with the existing English-translation curation.
