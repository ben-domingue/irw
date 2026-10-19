# Coverage audit -- 2026-10-19

Denominator: **7859 live tables** (7821 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 7821 | 7821 | 0 | 100 |
| biblio_row | 7821 | 7776 | 45 | 99.4 |
| citation | 7821 | 7776 | 45 | 99.4 |
| licence | 7821 | 7776 | 45 | 99.4 |
| page | 7821 | 7776 | 45 | 99.4 |
| tag_row | 6552 | 5920 | 632 | 90.4 |
| script | 7821 | 4909 | 2912 | 62.8 |
| codebook_link | 6661 | 2676 | 3985 | 40.2 |
| column_docs | 6412 | 4190 | 2222 | 65.3 |
| data_note | 7804 | 1734 | 6070 | 22.2 |
| has_construct_name | 6552 | 5920 | 632 | 90.4 |
| itemtext_shipped | 7821 | 2839 | 4982 | 36.3 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

| itemtext_status | n |
|---|---|
| unassessed | 4239 |
| shipped | 2839 |
| excluded | 402 |
| blocked | 299 |
| done_not_shipped | 29 |
| failed | 13 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 109 | 0 | 0 | 0 | 0 | 68 |
| conj | 1143 | 0 | 0 | 0 | 0 | 223 |
| core | 6412 | 0 | 45 | 45 | 565 | 2494 |
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
| item_response_warehouse_7 | 761 | 43 | 384 | 141 |

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

