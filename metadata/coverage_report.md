# Coverage audit -- 2026-11-24

Denominator: **11138 live tables** (11100 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 11100 | 11100 | 0 | 100 |
| biblio_row | 11100 | 11100 | 0 | 100 |
| citation | 11100 | 11100 | 0 | 100 |
| licence | 11100 | 11100 | 0 | 100 |
| page | 11100 | 11100 | 0 | 100 |
| tag_row | 8558 | 8446 | 112 | 98.7 |
| script | 11100 | 10930 | 170 | 98.5 |
| codebook_link | 7279 | 5628 | 1651 | 77.3 |
| column_docs | 8397 | 6570 | 1827 | 78.2 |
| data_note (info) | 11084 | 2075 | 9009 | 18.7 |
| has_construct_name | 8558 | 8446 | 112 | 98.7 |
| itemtext_shipped | 11100 | 2631 | 8469 | 23.7 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

column_docs is all-or-nothing per table; the mean share of a table's columns documented is 91.2%.

| itemtext_status | n |
|---|---|
| unassessed | 7313 |
| shipped | 2631 |
| withdrawn | 420 |
| excluded | 402 |
| blocked | 313 |
| failed | 13 |
| done_not_shipped | 8 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 6 |
| conj | 1292 | 0 | 0 | 0 | 0 | 0 |
| core | 8397 | 0 | 0 | 0 | 56 | 164 |
| nom | 161 | 0 | 0 | 0 | 56 | 0 |
| rank | 1113 | 0 | 0 | 0 | 0 | 0 |
| sim | 16 | 0 | 0 | 0 | 0 | 0 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 0 | 494 |
| item_response_warehouse_2 | 864 | 0 | 0 | 321 |
| item_response_warehouse_3 | 955 | 0 | 0 | 465 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 0 | 275 |
| item_response_warehouse_6 | 926 | 0 | 56 | 276 |
| item_response_warehouse_7 | 961 | 0 | 0 | 155 |
| item_response_warehouse_8 | 916 | 0 | 0 | 183 |
| item_response_warehouse_9 | 869 | 0 | 0 | 6 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| encceja_2018_ef_ci | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_ef_hg | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_ef_lp | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_ef_ma | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_em_ch | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_em_cn | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_em_lc | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2018_em_mt | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_ef_ci | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_ef_hg | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_ef_lp | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_ef_ma | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_em_ch | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_em_cn | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_em_lc | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2019_em_mt | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2020_ef_ci | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2020_ef_hg | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2020_ef_lp | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |
| encceja_2020_ef_ma | core | 7 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language column_docs |

