# 4thgrade_math_sirt (format strand)

**Lead.** Source `legacy_sweep` (`irw_validate/results/legacy_sweep_2026-09-02.csv`, line 3):
`imputed_values*` warn: "Item 'MA1' has one resp value accounting for 89% of responses — possible mean imputation." The same sweep also raised `multi_scale*` and `column_order` warnings on this table.

## Checks run

1. **Live table resolved.** It is `datapages.item_response_warehouse:as2e:v65_0.4thgrade_math_sirt:769d` (`version="current"`). Its columns are `item, id, resp, testlet, domain, subdomain`.
2. **Live aggregate.** `SELECT COUNT(*), COUNT(DISTINCT id), COUNT(DISTINCT item), COUNTIF(resp IS NULL)` returns 19,920 rows, 664 ids, 30 items and 0 nulls. This matches `metadata.csv` exactly (19,920 / 664 / 30, `n_categories` = 2).
3. **Live value counts per item.** `SELECT item, CAST(resp AS STRING), COUNT(*) ... GROUP BY 1,2`. Every item takes only the values {0, 1}.
   - MA1 has 588 ones and 76 zeros, a modal share of **88.6%**. That is the 89% in the lead.
   - Eight items exceed the 60% threshold: MA1 89%, MI3 80% (the modal value here is **0**, so a hard item), MC1 77%, MD2 75%, ME1 70%, MD1 68%, MI1 67% and MH4 67%.
   - The other 22 items sit between 50% and 66%.
4. **Script.** `data/sirt.R:21-32` reads `sirt::data.math`, drops its first two columns, melts the rest to long format and merges the item table (`x$item`). The script contains no imputation step. The source is the `sirt` package's scored 0/1 math test, so the data cannot contain a mean-imputed value: a mean of 0/1 data would not be an integer.

## Verdict

This is a **false alarm**. The flagged item is an easy dichotomous item (88.6% correct). The first item of a 4th-grade math test is plausibly the easiest. A concentrated value on a 0/1 item is simply the item's p-value. No response in the table is a non-integer.

The same sweep raised two other warnings. Neither changes an analysis:
- `multi_scale*` (item prefixes MA to MI) is also a false alarm. The table is one math test with testlet, domain and subdomain labels. Those labels are carried as columns, but without the `itemcov_` prefix. That is a naming deviation, not an analysis problem.
- `column_order` (`item, id, resp`) is cosmetic.

- **proposed_outcome:** `no_action`
- **confidence:** high
- **group:** `format:imputed_values_concentration`
- **minutes:** about 15 (this table). The 557-row estimate took about 15 more and is recorded in `fragments/format_notes.md`.
- **redivis_reads:** aggregate (3 queries, no rows read)

## Corpus estimate (from the legacy sweep CSV plus metadata.csv only)

- The 557 warnings fall on 557 distinct tables. That is 65% of the 852 tables the sweep opened.
- Every message uses the old wording. None of them names the dominant *value*, so the "dominant value is a scale endpoint" test cannot be run from the CSV.
- Joined to `n_categories`:

| n_categories | flagged tables | share of that band that got flagged |
|---|---:|---:|
| 2 or fewer (dichotomous) | 222 | 83% (222 of 269) |
| 3 to 4 | 86 | 60% |
| 5 to 7 | 158 | 42% |
| 8 to 11 | 50 | 72% |
| 12 or more (near-continuous) | 6 | 38% |
| no metadata match (renamed or retired) | 35 | |

**222 of the 557 (40%) are false alarms by construction.** On an integer scale, mean imputation yields a non-integer value, and a modal *integer* on a binary item cannot be one.

Most of the remaining 300 or so are almost certainly floor or ceiling items on short ordinal scales, but this CSV cannot show which value dominates. Only the 6 tables with 12 or more categories have a pattern that could plausibly be a fill value: `figure_skating`, `florida_twins_par`, `deception_professors`, `deception_game`, `tears` and `much_tte_2025_currentmotivation`.

See `fragments/format_notes.md` for why the check also *misses* real mean imputation (the control table, `movac_pakpour2022`).
