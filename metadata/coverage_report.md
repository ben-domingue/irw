# Coverage audit -- 2026-11-11

Denominator: **10435 live tables** (10397 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 10397 | 10397 | 0 | 100 |
| biblio_row | 10397 | 10397 | 0 | 100 |
| citation | 10397 | 10397 | 0 | 100 |
| licence | 10397 | 10397 | 0 | 100 |
| page | 10397 | 10397 | 0 | 100 |
| tag_row | 8038 | 7926 | 112 | 98.6 |
| script | 10397 | 5944 | 4453 | 57.2 |
| codebook_link | 8159 | 3042 | 5117 | 37.3 |
| column_docs | 7898 | 4774 | 3124 | 60.4 |
| data_note | 10381 | 1888 | 8493 | 18.2 |
| has_construct_name | 8038 | 7926 | 112 | 98.6 |
| itemtext_shipped | 10397 | 2633 | 7764 | 25.3 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 6775 |
| shipped | 2633 |
| excluded | 402 |
| blocked | 307 |
| done_not_shipped | 267 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 69 |
| conj | 1204 | 0 | 0 | 0 | 0 | 228 |
| core | 7898 | 0 | 0 | 0 | 56 | 3069 |
| nom | 140 | 0 | 0 | 0 | 56 | 115 |
| rank | 1018 | 0 | 0 | 0 | 0 | 961 |
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
| item_response_warehouse_9 | 370 | 0 | 0 | 1 |

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

