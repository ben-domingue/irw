# IRW table-name consistency audit -- 2026-07-28

Ground truth: `irw::irw_list_tables(source = c("core","comp","nom","sim"))`. 
Dictionary sheets skipped (--skip-dict).

## A. Incomplete coverage (missing >=2 sources, tag-only rows dropped -- matches metadata/04_tables.R's `zz`)

Full list, aligned columns: `table_audit_report_incomplete.txt`. Same data as CSV: `table_audit_report_incomplete.csv` (185 rows). Nothing here is auto-fixed -- triage by hand.

| table | category | redivis | dictionary_sheet | biblio_csv | metadata_csv | tags_csv |
|---|---|---|---|---|---|---|
| cricket | comp |  |  | 1 |  |  |
| debate | comp |  |  | 1 |  |  |
| epl_matches_2021-2022 | comp |  |  | 1 |  |  |
| league_of_legends | comp |  |  | 1 |  |  |
| mlb_baseball | comp |  |  | 1 |  |  |
| nhl_hockey | comp |  |  | 1 |  |  |
| anthropomorphism_health_voropaeva_2026 | core |  |  | 1 |  |  |
| chen_2019_cdrsc | core |  |  | 1 |  |  |
| chen_2019_csq | core |  |  | 1 |  |  |
| chinvararak_2021_bdi | core |  |  | 1 |  |  |
| chinvararak_2021_ecr | core |  |  | 1 |  |  |
| chinvararak_2021_phq15 | core |  |  | 1 |  |  |
| chinvararak_2021_ssq | core |  |  | 1 |  |  |
| chinvararak_2021_ylseq | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-1-4849 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-14548-19396 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-19397-24245 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-24246-29094 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-29095-33943 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-33944-38790 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-4850-9698 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100101-9699-14547 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100102-1-141 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100103-1-1479 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100104-1-254 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100104-1286-2448 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100104-255-1285 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100105-1-2450 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100105-2451-3888 | core |  |  | 1 |  |  |
| covid19risktool_peters_2025_100106-1-439 | core |  |  | 1 |  |  |
_...and 155 more, see the .txt or .csv._

## B. Urgent -- live in Redivis, not in any local CSV yet

_None._

## C. Near-duplicate / inconsistent names -- not implemented yet

_Deferred (Ben, 2026-07-27): hold off until bucket A has real examples to look at
together before designing this detector. See script header for what was tried
and discarded._
