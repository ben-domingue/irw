# Coverage audit -- 2026-10-15

Denominator: **7105 live tables** (7067 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 7067 | 6805 | 262 | 96.3 |
| biblio_row | 7067 | 6803 | 264 | 96.3 |
| citation | 7067 | 6803 | 264 | 96.3 |
| licence | 7067 | 6803 | 264 | 96.3 |
| page | 7067 | 6803 | 264 | 96.3 |
| tag_row | 5798 | 5541 | 257 | 95.6 |
| script | 7067 | 4209 | 2858 | 59.6 |
| codebook_link | 5907 | 2487 | 3420 | 42.1 |
| column_docs | 5566 | 3731 | 1835 | 67 |
| data_note | 7050 | 1584 | 5466 | 22.5 |
| has_construct_name | 5798 | 5541 | 257 | 95.6 |
| itemtext_shipped | 7067 | 2662 | 4405 | 37.7 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 3659 |
| shipped | 2662 |
| excluded | 405 |
| blocked | 299 |
| done_not_shipped | 29 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 109 | 0 | 0 | 0 | 0 | 68 |
| conj | 1143 | 170 | 170 | 170 | 0 | 372 |
| core | 5658 | 92 | 94 | 94 | 190 | 2291 |
| nom | 140 | 0 | 0 | 0 | 67 | 115 |
| sim | 17 | 0 | 0 | 0 | 0 | 12 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| (no metadata row) | 92 | 92 | 92 | 0 |
| item_response_warehouse | 974 | 0 | 6 | 616 |
| item_response_warehouse_2 | 865 | 2 | 12 | 399 |
| item_response_warehouse_3 | 955 | 0 | 3 | 584 |
| item_response_warehouse_4 | 976 | 0 | 0 | 530 |
| item_response_warehouse_5 | 870 | 0 | 0 | 246 |
| item_response_warehouse_6 | 926 | 0 | 77 | 287 |

## Worst 20 tables (by n_gaps)

Excludes the 262 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| wu2021_affect | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| wu2021_basic_empathy | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_gonogo_main | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_gonogo_pilot | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_stroop_main_bin | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_stroop_pilot_bin | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_immorality | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_mr_agree | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc15 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc41 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_kicks | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_passes | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nicoletti_correct_irw | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nicoletti_omni_irw | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| suarez_2026_statistics | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| wyscout_shots | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bringmann_2013_esm_mood | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link |
| dejonckheere_2018_esm_affect | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link |
| emidy2024_fevs | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link |
| encceja_2018_ef_ci | core | 8 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script column_docs |

