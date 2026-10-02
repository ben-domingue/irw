# IRW table-name consistency audit -- 2026-10-02

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets plus automated_finding/dictionary_auto*.csv included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (204 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| cricket | comp |  | 1 |  |  |  |
| debate | comp |  | 1 |  |  |  |
| epl_matches_2021-2022 | comp |  | 1 |  |  |  |
| league_of_legends | comp |  | 1 |  |  |  |
| mlb_baseball | comp |  | 1 |  |  |  |
| nhl_hockey | comp |  | 1 |  |  |  |
| 17 health-literate communication techniques rated for effectiveness, yes=1/no=2 (don't-know dropped); maryland family physicians. the 1-5 scale belongs to the _freqsibling. 25 responses carry out-of-range 3-5 from 3 respondents, see irw#2196 | core |  | 1 |  |  |  |
| 2024_online_addiction_bsmas | core |  |  | 1 |  |  |
| 2024_online_addiction_igds | core |  |  | 1 |  |  |
| 2024_online_addiction_sabas | core |  |  | 1 |  |  |
| alomari_2025_student_questionnaire | core |  |  | 1 |  |  |
| alqerem_2024_mhls | core |  | 1 |  |  |  |
| altahla_2024_whoqol_bref | core |  |  | 1 |  |  |
| bateman_2026_depression | core |  | 1 |  |  |  |
| bateman_2026_prse | core |  | 1 |  |  |  |
| donnan_2024_chlq | core |  | 1 |  |  |  |
| dvivdtws_ppmial_marcatto_2023_cwb | core |  |  | 1 |  |  |
| fazekas_2019_psci | core |  | 1 |  |  |  |
| figueroaquinones_2026_jss4 | core |  | 1 |  |  |  |
| figueroaquinones_2026_nmq | core |  | 1 |  |  |  |
| figueroaquinones_2026_phq4 | core |  | 1 |  |  |  |
| gokalp_2026_bscs | core |  | 1 |  |  |  |
| gokalp_2026_patience | core |  | 1 |  |  |  |
| gokalp_2026_responsibility | core |  | 1 |  |  |  |
| guzmanmuzante_2025_gse | core |  | 1 |  |  |  |
| guzmanmuzante_2025_mts | core |  | 1 |  |  |  |
| hachenberger_2025_gonogo | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_bin | core |  |  | 1 |  |  |
| hachenberger_2025_webexec | core |  |  | 1 |  |  |
| kayir_2026_ai_use | core |  | 1 |  |  |  |
_...and 174 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
