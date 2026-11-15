# Coverage audit -- 2026-11-15

Denominator: **10782 live tables** (10744 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 10744 | 10744 | 0 | 100 |
| biblio_row | 10744 | 10744 | 0 | 100 |
| citation | 10744 | 10744 | 0 | 100 |
| licence | 10744 | 10744 | 0 | 100 |
| page | 10744 | 10744 | 0 | 100 |
| tag_row | 8383 | 8271 | 112 | 98.7 |
| script | 10744 | 6219 | 4525 | 57.9 |
| codebook_link | 8504 | 3115 | 5389 | 36.6 |
| column_docs | 8222 | 4918 | 3304 | 59.8 |
| data_note | 10728 | 1891 | 8837 | 17.6 |
| has_construct_name | 8383 | 8271 | 112 | 98.7 |
| itemtext_shipped | 10744 | 2638 | 8106 | 24.6 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 7117 |
| shipped | 2638 |
| excluded | 402 |
| blocked | 307 |
| done_not_shipped | 267 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 69 |
| conj | 1205 | 0 | 0 | 0 | 0 | 229 |
| core | 8222 | 0 | 0 | 0 | 56 | 3139 |
| nom | 161 | 0 | 0 | 0 | 56 | 115 |
| rank | 1019 | 0 | 0 | 0 | 0 | 962 |
| sim | 16 | 0 | 0 | 0 | 0 | 11 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 0 | 497 |
| item_response_warehouse_2 | 864 | 0 | 0 | 322 |
| item_response_warehouse_3 | 955 | 0 | 0 | 467 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 0 | 275 |
| item_response_warehouse_6 | 926 | 0 | 56 | 277 |
| item_response_warehouse_7 | 961 | 0 | 0 | 155 |
| item_response_warehouse_8 | 916 | 0 | 0 | 183 |
| item_response_warehouse_9 | 694 | 0 | 0 | 6 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| encceja_2018_ef_ci | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_ef_hg | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_ef_lp | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_ef_ma | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_em_ch | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_em_cn | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2018_em_lc | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_ef_ci | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_ef_hg | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_ef_lp | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_ef_ma | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_em_ch | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_em_cn | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2019_em_lc | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_ef_ci | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_ef_hg | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_ef_lp | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_ef_ma | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_em_ch | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |
| encceja_2020_em_cn | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |

