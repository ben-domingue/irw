# Coverage audit -- 2026-10-15

Denominator: **7289 live tables** (7251 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 7251 | 7251 | 0 | 100 |
| biblio_row | 7251 | 7249 | 2 | 100 |
| citation | 7251 | 7249 | 2 | 100 |
| licence | 7251 | 7249 | 2 | 100 |
| page | 7251 | 7249 | 2 | 100 |
| tag_row | 5982 | 5734 | 248 | 95.9 |
| script | 7251 | 4540 | 2711 | 62.6 |
| codebook_link | 6091 | 2486 | 3605 | 40.8 |
| column_docs | 5842 | 3860 | 1982 | 66.1 |
| data_note | 7234 | 1646 | 5588 | 22.8 |
| has_construct_name | 5982 | 5734 | 248 | 95.9 |
| itemtext_shipped | 7251 | 2698 | 4553 | 37.2 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 3810 |
| shipped | 2698 |
| excluded | 402 |
| blocked | 299 |
| done_not_shipped | 29 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 109 | 0 | 0 | 0 | 0 | 68 |
| conj | 1143 | 0 | 0 | 0 | 0 | 223 |
| core | 5842 | 0 | 2 | 2 | 181 | 2293 |
| nom | 140 | 0 | 0 | 0 | 67 | 115 |
| sim | 17 | 0 | 0 | 0 | 0 | 12 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 6 | 616 |
| item_response_warehouse_2 | 864 | 2 | 12 | 399 |
| item_response_warehouse_3 | 955 | 0 | 3 | 584 |
| item_response_warehouse_4 | 976 | 0 | 0 | 530 |
| item_response_warehouse_5 | 962 | 0 | 83 | 282 |
| item_response_warehouse_6 | 926 | 0 | 77 | 287 |
| item_response_warehouse_7 | 191 | 0 | 0 | 0 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| wu2021_affect | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| wu2021_basic_empathy | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_civic | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_djg | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_education | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_feelings | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_social_support | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_ucla | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| euls_2022_work | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_gonogo_main | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_gonogo_pilot | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_stroop_main_bin | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hachenberger_2025_stroop_pilot_bin | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| iclr_2024_peer_review | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_immorality | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_mr_agree | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc15 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc41 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_kicks | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| nflverse_passes | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |

