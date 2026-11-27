# IRW table-name consistency audit -- 2026-11-27

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets plus automated_finding/dictionary_auto*.csv included (Public rows only).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (462 rows). Nothing here is auto-fixed -- triage by hand.

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
| agusta_2023_intrinsic_motivation | core |  | 1 |  |  |  |
| alomari_2025_student_questionnaire | core |  |  | 1 |  |  |
| altahla_2024_whoqol_bref | core |  |  | 1 |  |  |
| alzahrani_2026_arabic_ld | core | 1 |  |  |  |  |
| brysbaert_2016_dlp2 | core | 1 |  |  |  |  |
| brysbaert_2019_dcp | core | 1 |  |  |  |  |
| cao_2026_digital_health_literacy | core |  | 1 |  |  |  |
| chromy_2026_czeled | core | 1 |  |  |  |  |
| diazguerra_2024_uef1 | core |  | 1 |  |  |  |
| dvivdtws_ppmial_marcatto_2023_cwb | core |  |  | 1 |  |  |
| hachenberger_2025_gonogo | core |  |  | 1 |  |  |
| hachenberger_2025_stroop_bin | core |  |  | 1 |  |  |
| hachenberger_2025_webexec | core |  |  | 1 |  |  |
| haro_2024_emotional_ld | core | 1 |  |  |  |  |
| kazarovytska_2026_ingroup_event_attribution | core |  |  | 1 |  |  |
| keuleers_2012_blp | core | 1 |  |  |  |  |
| kwiatkowska_2022_bemas | core |  |  | 1 |  |  |
| liang2026_extrinsic_motivation | core |  |  | 1 |  |  |
| liang2026_intrinsic_motivation | core |  |  | 1 |  |  |
| lindstrom2021_conscientiousness | core |  |  | 1 |  |  |
| liu_2024_igd27 | core |  | 1 |  |  |  |
_...and 432 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

| table | category |
|---|---|
| alzahrani_2026_arabic_ld | core |
| brysbaert_2016_dlp2 | core |
| brysbaert_2019_dcp | core |
| chromy_2026_czeled | core |
| haro_2024_emotional_ld | core |
| keuleers_2012_blp | core |
| mandera_2020_ecp | core |
| martineztomas_2026_pseudoword_ld | core |
| nemati_2022_persian_ld | core |
| ota_2025_jalex | core |
| perezsanchez_2025_spaverb_ld | core |
| tsukahara_2020_discrimination | core |
| tsukahara_2020_lettersets | core |
| tsukahara_2020_numberseries | core |
| tsukahara_2020_rapm | core |
| tucker_2019_mald | core |

_These probably just need the generate-CSVs workflow re-run (01/05/06/07 pick up new Redivis tables automatically)._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
