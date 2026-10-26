# Coverage audit -- 2026-10-26

Denominator: **8601 live tables** (8563 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 8563 | 8563 | 0 | 100 |
| biblio_row | 8563 | 8495 | 68 | 99.2 |
| citation | 8563 | 8495 | 68 | 99.2 |
| licence | 8563 | 8495 | 68 | 99.2 |
| page | 8563 | 8495 | 68 | 99.2 |
| tag_row | 6822 | 6532 | 290 | 95.7 |
| script | 8563 | 5166 | 3397 | 60.3 |
| codebook_link | 6933 | 2770 | 4163 | 40 |
| column_docs | 6682 | 4337 | 2345 | 64.9 |
| data_note | 8546 | 1818 | 6728 | 21.3 |
| has_construct_name | 6822 | 6532 | 290 | 95.7 |
| itemtext_shipped | 8563 | 2713 | 5850 | 31.7 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 5009 |
| shipped | 2713 |
| excluded | 402 |
| blocked | 307 |
| done_not_shipped | 119 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 111 | 0 | 0 | 0 | 0 | 68 |
| conj | 1161 | 0 | 0 | 0 | 0 | 224 |
| core | 6682 | 0 | 68 | 68 | 223 | 2583 |
| nom | 140 | 0 | 0 | 0 | 67 | 115 |
| rank | 452 | 0 | 0 | 0 | 0 | 395 |
| sim | 17 | 0 | 0 | 0 | 0 | 12 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| item_response_warehouse | 968 | 0 | 6 | 568 |
| item_response_warehouse_2 | 864 | 2 | 12 | 365 |
| item_response_warehouse_3 | 955 | 0 | 3 | 547 |
| item_response_warehouse_4 | 976 | 0 | 0 | 497 |
| item_response_warehouse_5 | 962 | 0 | 83 | 275 |
| item_response_warehouse_6 | 926 | 0 | 77 | 281 |
| item_response_warehouse_7 | 961 | 66 | 42 | 154 |
| item_response_warehouse_8 | 70 | 0 | 0 | 26 |

## Worst 20 tables (by n_gaps)

Excludes the 0 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| amornsriwatanakul_2025_family_support | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| amornsriwatanakul_2025_friend_support | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| austin_2021_media_literacy | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| chen_2026_genai_learning | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| delapena_2026_fscale | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_aot | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_epistemic_beliefs | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_moralized_rationality | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_need_for_affect | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_need_for_closure | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| eichmeier_2019_nfc | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| espinoza_2024_dass21 | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hollibaugh_2024_ambition_reasons | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| kar_2022_ghq12 | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| khongsirisombat_2025_aaq_sf | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| ksiazkiewicz_2025_gspq | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| maruyama_2023_madagascar_math | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| munoztroncoso_2024_vi_gec | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| stiglic_2019_wemwbs | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| wicki_2021_av_concern | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |

