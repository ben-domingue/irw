# IRW table-name consistency audit -- 2026-08-24

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (66 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| cricket | comp |  | 1 | 1 |  |  |
| debate | comp |  | 1 | 1 |  |  |
| epl_matches_2021-2022 | comp |  | 1 | 1 |  |  |
| league_of_legends | comp |  | 1 | 1 |  |  |
| mlb_baseball | comp |  | 1 | 1 |  |  |
| nhl_hockey | comp |  | 1 | 1 |  |  |
| alexander_2017_ecr | core |  | 1 | 1 |  |  |
| anthropomorphism_health_voropaeva_2026 | core |  | 1 | 1 |  |  |
| kemp_2019_mss_disorganized | core | 1 |  |  | 1 |  |
| kemp_2019_mss_negative | core | 1 |  |  | 1 |  |
| kemp_2019_mss_positive | core | 1 |  |  | 1 |  |
| hachenberger_2025_stroop_main_nominal | nom |  | 1 | 1 |  |  |
| hachenberger_2025_stroop_pilot_nominal | nom |  | 1 | 1 |  |  |
| abdullah_2024_hbbloat_subjnorm | core |  | 1 | 1 |  | 1 |
| autobiographicalinterview_lockrow_2023_detailcounts | core |  | 1 | 1 |  | 1 |
| autobiographicalinterview_lockrow_2023_scorerratings | core |  | 1 | 1 |  | 1 |
| autobiographicalinterview_lockrow_2023_selfreport | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_callousness | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_civic_behavior | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_crime_analog | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_d70 | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_dictator_game | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_exploitative | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_interp_dysfx | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_normlessness | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_sdo7s | core |  | 1 | 1 |  | 1 |
| darkfactorfrench_pischel_2026_worldview_cj | core |  | 1 | 1 |  | 1 |
| hachenberger_2025_gonogo_main | core |  | 1 | 1 |  | 1 |
| hachenberger_2025_gonogo_pilot | core |  | 1 | 1 |  | 1 |
| hachenberger_2025_stroop_main_bin | core |  | 1 | 1 |  | 1 |
_...and 36 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
