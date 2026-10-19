# IRW table-name consistency audit -- 2026-10-19

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets plus automated_finding/dictionary_auto*.csv included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (305 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| cricket | comp |  | 1 |  |  |  |
| debate | comp |  | 1 |  |  |  |
| epl_matches_2021-2022 | comp |  | 1 |  |  |  |
| league_of_legends | comp |  | 1 |  |  |  |
| mlb_baseball | comp |  | 1 |  |  |  |
| nhl_hockey | comp |  | 1 |  |  |  |
| 2024_online_addiction_bsmas | core |  |  | 1 |  |  |
| 2024_online_addiction_igds | core |  |  | 1 |  |  |
| 2024_online_addiction_sabas | core |  |  | 1 |  |  |
| alomari_2025_student_questionnaire | core |  |  | 1 |  |  |
| altahla_2024_whoqol_bref | core |  |  | 1 |  |  |
| arvanitis_2023_compulsion | core |  | 1 |  |  |  |
| arvanitis_2023_mfq | core |  | 1 |  |  |  |
| arvanitis_2023_mfv | core |  | 1 |  |  |  |
| dai_2024_acculturation_index | core |  | 1 |  |  |  |
| dai_2024_cultural_difference | core |  | 1 |  |  |  |
| dai_2024_self_esteem | core |  | 1 |  |  |  |
| dai_2024_wellbeing | core |  | 1 |  |  |  |
| dufour_2024_biosecurity_frequency | core |  | 1 |  |  |  |
| dufour_2024_biosecurity_yesno | core |  | 1 |  |  |  |
| dvivdtws_ppmial_marcatto_2023_cwb | core |  |  | 1 |  |  |
| enke_2023_anchoring | core |  | 1 |  |  |  |
| enke_2023_brn | core |  | 1 |  |  |  |
| enke_2023_crt | core |  | 1 |  |  |  |
| enke_2023_wason | core |  | 1 |  |  |  |
| ghasemy_2025_ipanas_sf | core |  | 1 |  |  |  |
| glashouwer_2017_dpss_study1 | core |  | 1 |  |  |  |
| glashouwer_2017_dpss_study2 | core |  | 1 |  |  |  |
| glashouwer_2017_sdes_study2 | core |  | 1 |  |  |  |
| glashouwer_2017_sds_study1 | core |  | 1 |  |  |  |
_...and 275 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
