# IRW table-name consistency audit -- 2026-08-02

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (88 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| racialsocialnormsbrazilianstudents_portella_2022 | core |  |  | 1 |  |  |
| su_2024_isi | core |  |  | 1 |  |  |
| su_2024_phq9 | core |  |  | 1 |  |  |
| su_2024_pss14 | core |  |  | 1 |  |  |
| cricket | comp |  | 1 | 1 |  |  |
| debate | comp |  | 1 | 1 |  |  |
| epl_matches_2021-2022 | comp |  | 1 | 1 |  |  |
| league_of_legends | comp |  | 1 | 1 |  |  |
| mlb_baseball | comp |  | 1 | 1 |  |  |
| nhl_hockey | comp |  | 1 | 1 |  |  |
| anthropomorphism_health_voropaeva_2026 | core |  | 1 | 1 |  |  |
| condon_2024_sapa_personality | core |  | 1 | 1 |  |  |
| daiku_2021_dirty_dozen | core |  | 1 | 1 |  |  |
| daiku_2021_lie_scale | core |  | 1 | 1 |  |  |
| daiku_2021_lying_frequency | core |  | 1 | 1 |  |  |
| dolzdelcastellar_2021_faces | core | 1 |  |  | 1 |  |
| gumus_2025_dietarian_identity | core |  | 1 | 1 |  |  |
| horiuchi_2024_attachment | core |  | 1 | 1 |  |  |
| horiuchi_2024_dissociation | core |  | 1 | 1 |  |  |
| horiuchi_2024_rsmsm | core |  | 1 | 1 |  |  |
| jimenezherrera_2022_moral_sensitivity | core |  | 1 | 1 |  |  |
| machado_2020_cat_separation | core |  | 1 | 1 |  |  |
| pavic_2022_healthcare_trust | core |  | 1 | 1 |  |  |
| pavic_2022_natural_immunity | core |  | 1 | 1 |  |  |
| pavic_2022_science_literacy | core |  | 1 | 1 |  |  |
| pavic_2022_vaccine_conspiracy | core |  | 1 | 1 |  |  |
| su_2024_gad7 | core |  | 1 | 1 |  |  |
| tuason_2021_covid_coping_enjoy | core |  | 1 | 1 |  |  |
| tuason_2021_loneliness_emotional | core |  | 1 | 1 |  |  |
| tuason_2021_loneliness_social | core |  | 1 | 1 |  |  |
_...and 58 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
