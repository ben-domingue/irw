# Coverage audit -- 2026-11-09

Denominator: **9970 live tables** (9932 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 9932 | 9932 | 0 | 100 |
| biblio_row | 9932 | 9932 | 0 | 100 |
| citation | 9932 | 9932 | 0 | 100 |
| licence | 9932 | 9932 | 0 | 100 |
| page | 9932 | 9932 | 0 | 100 |
| tag_row | 7616 | 7472 | 144 | 98.1 |
| script | 9932 | 5661 | 4271 | 57 |
| codebook_link | 7737 | 2992 | 4745 | 38.7 |
| column_docs | 7476 | 4651 | 2825 | 62.2 |
| data_note | 9916 | 1845 | 8071 | 18.6 |
| has_construct_name | 7616 | 7472 | 144 | 98.1 |
| itemtext_shipped | 9932 | 2630 | 7302 | 26.5 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 6313 |
| shipped | 2630 |
| excluded | 402 |
| blocked | 307 |
| done_not_shipped | 267 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 69 |
| conj | 1161 | 0 | 0 | 0 | 0 | 224 |
| core | 7476 | 0 | 0 | 0 | 77 | 2891 |
| nom | 140 | 0 | 0 | 0 | 67 | 115 |
| rank | 1018 | 0 | 0 | 0 | 0 | 961 |
| sim | 16 | 0 | 0 | 0 | 0 | 11 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 6 | 497 |
| item_response_warehouse_2 | 864 | 0 | 7 | 322 |
| item_response_warehouse_3 | 955 | 0 | 2 | 467 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 0 | 275 |
| item_response_warehouse_6 | 926 | 0 | 59 | 277 |
| item_response_warehouse_7 | 961 | 0 | 1 | 155 |
| item_response_warehouse_8 | 864 | 0 | 2 | 181 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| moral_absolutism_goyal_2025_immorality | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_mr_agree | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc15 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc41 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_kicks | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_passes | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nicoletti_correct_irw | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nicoletti_omni_irw | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| emidy2024_fevs | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link |
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

