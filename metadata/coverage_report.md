# Coverage audit -- 2026-11-27

Denominator: **12485 live tables** (12447 after excluding 38 withdrawn). Definitions in the header of `metadata/17_coverage.R`; per-table rows in `coverage_matrix.csv`. Report-only: nothing here is fixed automatically.

## Per dimension (active tables)

| dimension | applicable | covered | missing | pct |
|---|---|---|---|---|
| metadata_row | 12447 | 12422 | 25 | 99.8 |
| biblio_row | 12447 | 12185 | 262 | 97.9 |
| citation | 12447 | 12185 | 262 | 97.9 |
| licence | 12447 | 12185 | 262 | 97.9 |
| page | 12447 | 12185 | 262 | 97.9 |
| tag_row | 9905 | 9516 | 389 | 96.1 |
| script | 12447 | 12033 | 414 | 96.7 |
| codebook_link | 8031 | 6118 | 1913 | 76.2 |
| column_docs | 9719 | 7589 | 2130 | 78.1 |
| data_note (info) | 12431 | 2079 | 10352 | 16.7 |
| has_construct_name | 9905 | 9516 | 389 | 96.1 |
| itemtext_shipped | 12447 | 2720 | 9727 | 21.9 |

## Item-text status

Issues against the public item-text page are the daily `itemtext-issues.yml` check, not this report.

column_docs is all-or-nothing per table; the mean share of a table's columns documented is 91.1%.

| itemtext_status | n |
|---|---|
| unassessed | 8570 |
| shipped | 2720 |
| withdrawn | 421 |
| excluded | 402 |
| blocked | 313 |
| failed | 13 |
| done_not_shipped | 8 |

## Per source

| source | live | no_metadata | no_licence | no_page | untagged | no_script |
|---|---|---|---|---|---|---|
| comp | 121 | 0 | 0 | 0 | 0 | 6 |
| conj | 1292 | 0 | 0 | 0 | 0 | 0 |
| core | 9744 | 25 | 262 | 262 | 333 | 408 |
| nom | 161 | 0 | 0 | 0 | 56 | 0 |
| rank | 1113 | 0 | 0 | 0 | 0 | 0 |
| sim | 16 | 0 | 0 | 0 | 0 | 0 |

## Core, per shard

| dataset | live | no_page | untagged | text_shipped |
|---|---|---|---|---|
| (no metadata row) | 25 | 25 | 25 | 0 |
| item_response_warehouse | 970 | 0 | 0 | 493 |
| item_response_warehouse_10 | 1000 | 78 | 93 | 66 |
| item_response_warehouse_11 | 1 | 1 | 1 | 0 |
| item_response_warehouse_2 | 899 | 0 | 0 | 321 |
| item_response_warehouse_3 | 955 | 0 | 0 | 465 |
| item_response_warehouse_4 | 976 | 0 | 0 | 456 |
| item_response_warehouse_5 | 962 | 0 | 0 | 275 |
| item_response_warehouse_6 | 981 | 55 | 111 | 285 |
| item_response_warehouse_7 | 990 | 29 | 29 | 155 |
| item_response_warehouse_8 | 990 | 74 | 74 | 183 |
| item_response_warehouse_9 | 995 | 0 | 0 | 21 |

## Worst 20 tables (by n_gaps)

Excludes the 25 live tables with no metadata row yet (stage 01's rolling throttle; stage 12 names any that persist). Listed in the matrix with `metadata_row = FALSE`.

| table | source | n_gaps | missing |
|---|---|---|---|
| astini_2026_brand_attitude | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| astini_2026_brand_image | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| astini_2026_perceived_greenwashing | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| batsukh_2024_brand_trust | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bramastya_2026_environmental_concern | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bramastya_2026_environmental_knowledge | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bramastya_2026_green_merchant_trust | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bramastya_2026_green_purchase_intention | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| bramastya_2026_green_purchase_value | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| cetinkaya_2025_italy_travel_motives | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| grant_2025_policy_support | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_antagonistic_climate | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_coercive_power | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_committed_cooperation | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_confidence_climate | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_enforced_compliance | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_implicit_trust | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_legitimate_power | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_reason_based_trust | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |
| hartl_2015_service_climate | core | 13 | biblio_row citation licence page tag_row tag_age_range tag_sample tag_measurement_tool tag_item_format tag_primary_language script codebook_link column_docs |

