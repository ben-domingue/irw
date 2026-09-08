# IRW table-name consistency audit -- 2026-09-07

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (127 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| alomari_2025_student_questionnaire | core |  |  | 1 |  |  |
| altahla_2024_whoqol_bref | core |  |  | 1 |  |  |
| dvivdtws_ppmial_marcatto_2023_cwb | core |  |  | 1 |  |  |
| hachenberger_2025_gonogo_main | core |  |  | 1 |  |  |
| hachenberger_2025_gonogo_pilot | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_main_bin | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_pilot_bin | core |  |  | 1 |  |  |
| hachenberger_2025_webexec_main | core |  |  | 1 |  |  |
| hachenberger_2025_webexec_pilot | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_canada | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_india | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_peru | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_uganda | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_usa | core |  |  | 1 |  |  |
| thirdpartypunishmentunfairsharing_mcauliffe_2025_vanuatu | core |  |  | 1 |  |  |
| wvs_panasiuk_science | core |  |  | 1 |  |  |
| wvs_panasiuk_security | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_main_nominal | nom |  |  | 1 |  |  |
| hachenberger_2025_stroop_pilot_nominal | nom |  |  | 1 |  |  |
| cricket | comp |  | 1 | 1 |  |  |
| debate | comp |  | 1 | 1 |  |  |
| epl_matches_2021-2022 | comp |  | 1 | 1 |  |  |
| league_of_legends | comp |  | 1 | 1 |  |  |
| mlb_baseball | comp |  | 1 | 1 |  |  |
| nhl_hockey | comp |  | 1 | 1 |  |  |
| abdullah_2024_hbbloat_subjnorm | core |  | 1 | 1 |  |  |
| alexander_2017_ecr | core |  | 1 | 1 |  |  |
| anthropomorphism_health_voropaeva_2026 | core |  | 1 | 1 |  |  |
| apfcompact_ptacek_2024_dass-21 | core |  | 1 | 1 |  |  |
| autobiographicalinterview_lockrow_2023_detailcounts | core |  | 1 | 1 |  |  |
_...and 97 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
