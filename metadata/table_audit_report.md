# IRW table-name consistency audit -- 2026-08-10

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets skipped (--skip-dict).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (292 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| cricket | comp |  |  | 1 |  |  |
| debate | comp |  |  | 1 |  |  |
| epl_matches_2021-2022 | comp |  |  | 1 |  |  |
| league_of_legends | comp |  |  | 1 |  |  |
| mlb_baseball | comp |  |  | 1 |  |  |
| nhl_hockey | comp |  |  | 1 |  |  |
| anthropomorphism_health_voropaeva_2026 | core |  |  | 1 |  |  |
| racialsocialnormsbrazilianstudents_portella_2022 | core |  |  | 1 |  |  |
| su_2024_gad7 | core |  |  | 1 |  |  |
| su_2024_isi | core |  |  | 1 |  |  |
| su_2024_phq9 | core |  |  | 1 |  |  |
| su_2024_pss14 | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_main_nominal | nom |  |  | 1 |  |  |
| hachenberger_2025_stroop_pilot_nominal | nom |  |  | 1 |  |  |
| adhd_silk_2019_externalising_disorder | core |  |  | 1 |  | 1 |
| adhd_silk_2019_hyperactive_impulsive_criteria | core |  |  | 1 |  | 1 |
| adhd_silk_2019_inattentive_criteria | core |  |  | 1 |  | 1 |
| adhd_silk_2019_interalizing_disorder | core |  |  | 1 |  | 1 |
| ahmed_2019_food_consumption | core | 1 |  |  | 1 |  |
| ahmed_2019_wellbeing | core | 1 |  |  | 1 |  |
| alcoholhealthwarninglabel_brennan_2022_awareness_harms_followup | core | 1 |  |  | 1 |  |
| alcoholhealthwarninglabel_brennan_2022_emotional_arousal_followup | core | 1 |  |  | 1 |  |
| alcoholhealthwarninglabel_brennan_2022_positive_arousal | core |  |  | 1 |  | 1 |
| ali_2021_gad7 | core | 1 |  |  | 1 |  |
| ali_2021_iesr | core | 1 |  |  | 1 |  |
| ali_2021_isi | core | 1 |  |  | 1 |  |
| ali_2021_phq9 | core | 1 |  |  | 1 |  |
| ali_2021_spfi | core | 1 |  |  | 1 |  |
| autobiographicalinterview_lockrow_2023_detailcounts | core |  |  | 1 |  | 1 |
| autobiographicalinterview_lockrow_2023_scorerratings | core |  |  | 1 |  | 1 |
_...and 262 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
