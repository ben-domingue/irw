# Coverage audit -- 2026-10-21

Denominator: **8061 live tables** (8023 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 8023 | 8023 | 0 | 100 |
| biblio_row | 8023 | 7955 | 68 | 99.2 |
| citation | 8023 | 7955 | 68 | 99.2 |
| licence | 8023 | 7955 | 68 | 99.2 |
| page | 8023 | 7955 | 68 | 99.2 |
| tag_row | 6753 | 6463 | 290 | 95.7 |
| script | 8023 | 5046 | 2977 | 62.9 |
| codebook_link | 6863 | 2757 | 4106 | 40.2 |
| column_docs | 6613 | 4303 | 2310 | 65.1 |
| data_note | 8006 | 1760 | 6246 | 22 |
| has_construct_name | 6753 | 6463 | 290 | 95.7 |
| itemtext_shipped | 8023 | 2855 | 5168 | 35.6 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 4425 |
| shipped | 2855 |
| excluded | 402 |
| blocked | 299 |
| done_not_shipped | 29 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 110 | 0 | 0 | 0 | 0 | 68 |
| conj | 1143 | 0 | 0 | 0 | 0 | 223 |
| core | 6613 | 0 | 68 | 68 | 223 | 2559 |
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
| item_response_warehouse_7 | 961 | 66 | 42 | 156 |
| item_response_warehouse_8 | 1 | 0 | 0 | 1 |

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

