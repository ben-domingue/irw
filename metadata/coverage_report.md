# Coverage audit -- 2026-11-25

Denominator: **11696 live tables** (11658 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 11658 | 11658 | 0 | 100 |
| biblio_row | 11658 | 11658 | 0 | 100 |
| citation | 11658 | 11658 | 0 | 100 |
| licence | 11658 | 11658 | 0 | 100 |
| page | 11658 | 11658 | 0 | 100 |
| tag_row | 9116 | 9004 | 112 | 98.8 |
| script | 11658 | 11488 | 170 | 98.5 |
| codebook_link | 7487 | 5836 | 1651 | 77.9 |
| column_docs | 8955 | 7072 | 1883 | 79 |
| data_note (info) | 11642 | 2075 | 9567 | 17.8 |
| has_construct_name | 9116 | 9004 | 112 | 98.8 |
| itemtext_shipped | 11658 | 2631 | 9027 | 22.6 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

column_docs is all-or-nothing per table; the mean share of a table's columns documented is 91.5%.

| itemtext_status | n |
|---|---|
| unassessed | 7871 |
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
| core | 8955 | 0 | 0 | 0 | 56 | 164 |
| nom | 161 | 0 | 0 | 0 | 56 | 0 |
| rank | 1113 | 0 | 0 | 0 | 0 | 0 |
| sim | 16 | 0 | 0 | 0 | 0 | 0 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 0 | 494 |
| item_response_warehouse_10 | 402 | 0 | 0 | 0 |
| item_response_warehouse_2 | 899 | 0 | 0 | 321 |
| item_response_warehouse_3 | 955 | 0 | 0 | 465 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 0 | 275 |
| item_response_warehouse_6 | 926 | 0 | 56 | 276 |
| item_response_warehouse_7 | 961 | 0 | 0 | 155 |
| item_response_warehouse_8 | 916 | 0 | 0 | 183 |
| item_response_warehouse_9 | 990 | 0 | 0 | 6 |

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

