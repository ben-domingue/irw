# IRW table-name consistency audit -- 2026-10-05

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets plus automated_finding/dictionary_auto*.csv included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (177 rows). Nothing here is auto-fixed -- triage by hand.

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
| altahla_2024_whoqol_bref | core |  |  | 1 |  |  |
| dvivdtws_ppmial_marcatto_2023_cwb | core |  |  | 1 |  |  |
| hachenberger_2025_gonogo | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_bin | core |  |  | 1 |  |  |
| hachenberger_2025_webexec | core |  |  | 1 |  |  |
| kazarovytska_2026_ingroup_event_attribution | core |  |  | 1 |  |  |
| liang2026_extrinsic_motivation | core |  |  | 1 |  |  |
| liang2026_intrinsic_motivation | core |  |  | 1 |  |  |
| lindstrom2021_conscientiousness | core |  |  | 1 |  |  |
| moral_absolutism_goyal_2025_moral | core |  |  | 1 |  |  |
| moral_absolutism_goyal_2025_nfc | core |  |  | 1 |  |  |
| robison_2026_retesting_mmi | core |  |  | 1 |  |  |
| simsalrbim_human_largevalence_2017 | core |  |  | 1 |  |  |
| simsalrbim_human_largevalence_2018 | core |  |  | 1 |  |  |
| simsalrbim_human_lowvalence_2017 | core |  |  | 1 |  |  |
| simsalrbim_mice_largevalence | core |  |  | 1 |  |  |
| simsalrbim_mice_lowvalence | core |  |  | 1 |  |  |
| simsalrbim_monkey_largevalence | core |  |  | 1 |  |  |
| wvs_panasiuk_science | core |  |  | 1 |  |  |
_...and 147 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
