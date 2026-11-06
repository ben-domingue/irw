# Coverage audit -- 2026-11-06

Denominator: **9827 live tables** (9789 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 9789 | 9789 | 0 | 100 |
| biblio_row | 9789 | 9789 | 0 | 100 |
| citation | 9789 | 9789 | 0 | 100 |
| licence | 9789 | 9789 | 0 | 100 |
| page | 9789 | 9789 | 0 | 100 |
| tag_row | 7473 | 7165 | 308 | 95.9 |
| script | 9789 | 5631 | 4158 | 57.5 |
| codebook_link | 7594 | 2962 | 4632 | 39 |
| column_docs | 7333 | 4628 | 2705 | 63.1 |
| data_note | 9773 | 1845 | 7928 | 18.9 |
| has_construct_name | 7473 | 7165 | 308 | 95.9 |
| itemtext_shipped | 9789 | 2606 | 7183 | 26.6 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 6194 |
| shipped | 2606 |
| excluded | 402 |
| blocked | 307 |
| done_not_shipped | 267 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 69 |
| conj | 1161 | 0 | 0 | 0 | 0 | 224 |
| core | 7333 | 0 | 0 | 0 | 241 | 2778 |
| nom | 140 | 0 | 0 | 0 | 67 | 115 |
| rank | 1018 | 0 | 0 | 0 | 0 | 961 |
| sim | 16 | 0 | 0 | 0 | 0 | 11 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 6 | 497 |
| item_response_warehouse_2 | 864 | 0 | 12 | 322 |
| item_response_warehouse_3 | 955 | 0 | 3 | 467 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 83 | 275 |
| item_response_warehouse_6 | 926 | 0 | 77 | 277 |
| item_response_warehouse_7 | 961 | 0 | 42 | 155 |
| item_response_warehouse_8 | 721 | 0 | 18 | 157 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| amornsriwatanakul_2025_family_support | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| amornsriwatanakul_2025_friend_support | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| espinoza_2024_dass21 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
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
| kar_2022_ghq12 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| ksiazkiewicz_2025_gspq | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_immorality | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_mr_agree | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| moral_absolutism_goyal_2025_nfc15 | core | 9 | tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |

