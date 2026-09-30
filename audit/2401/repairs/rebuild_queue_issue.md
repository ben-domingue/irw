**Title:** Rebuild queue: 14 families whose scripts dropped a key column (identical rows, #2401)

---

The #2401 audit found 24 live tables in 14 families where rows are exactly identical because the `data/` script dropped a column that told them apart. Deduping them would delete real responses. Each one needs a rebuild from the raw files with that column kept. That is too much to do inside the audit, so this issue is the queue.

2,963,483 identical rows in all, 2,643,499 of them (89%) in PISA 2000/2006. Per-family evidence is in `audit/2401/triage/dup_exact.csv` and `dup_exact.md`.

## The queue

"Goes into" says where the restored column belongs: `id` (a person key), `rater`, `wave`/`date`/trial (an occasion) or `item` (a stimulus).

| family | tables | identical rows | dropped column | goes into | raw source | effort |
|---|---|---|---|---|---|---|
| **pisa2000** | `_math`, `_read`, `_science` | 1,438,492 | `SCHOOLID` (selected, then dropped) | id (`CNT`+`SCHOOLID`+`STIDSTD`) | OECD fixed-width `intcogn_v4.txt` + SAS control file | **high**: see below |
| **pisa2006** | `_math`, `_read`, `_science` | 1,205,007 | `SCHOOLID` (read, then dropped) | id (`CNT`+`SCHOOLID`+`STIDSTD`) | OECD `INT_Cogn06_S_Dec07.txt`, `INT_Stu06_Dec07.txt` | medium: large files, simple change |
| crspolish_wiesyk_2024 | 4 (`_crs`, `_enrich`, `_lie`, `_p_stress`) | 5,381 | country + parent role (dyad member) | id | PsychArchives `CRS_dec.csv` (review-only link) | medium: parent role must come from the source; `cov_sex` is NA in country 1 |
| ptcichina_zhan_2024 | 1 | 648 | sample `C2` + row index | id | OSF tj8rh, `PTCI_data.sav` | low |
| rating_speed_2025 | 1 | 26,285 | the `male`/`female` suffix on `Ppn`, stripped by `gsub` | rater | OSF 9htuv, `All_Arousal.csv` | low: drop the `gsub` |
| geography | 1 | 18,299 | `inserted` timestamp (commented out) | date | slepemapy `answer.csv` | medium: large log; also set the INT32-max rt sentinel (2,147,483.647 s) to NA |
| zhang_2020_trait_creativity_mood | 1 | 1,335 | beep time (`StartTime`) | date or wave | PLOS S1 (10.1371/journal.pone.0236987) | low |
| steinberg_2023_mentalizing | `_momentary` | 1,004 | `surveyid` (excluded explicitly) | wave/trial | OSF 9cm75, `Steinberg_DailyMz_Momentary_Data.csv` | low |
| schoen_2019_to_2022_mkt | 1 | 22 | `datacollectionwave` | wave | OSF twgcu, yearly CSVs | low: same fix as KTEEM (#1842 `restore_wave`) |
| kalimahnorms_alzahrani_2025 | 1 | 278 | Gorilla trial index / timestamp | trial | OSF zajk6 (view-only link), `raw_ratings.csv` | medium |
| musifeast17_vanderwalle_2025 | 1 | 266,431 | clip id | item | OSF 5ebz2, `M17_raw_data_cleaned.csv` | medium: 190,672 of the rows are person-level `genre_exposure` repeated 17×, which is a plain dedupe |
| mentalrotation_wolf_2024 | 1 | 13 | trial or same/mirror field | item | OSF rgvf7, `Combined_Subject_Data.csv` | medium: not yet checked against the raw file |
| childrensocialcognition_cvencek_2025 | 4 | 32 | Inquisit `trialnum` | item (or trial) | OSF w35zk, `Data.sav` (study 1–4 scripts) | medium: four scripts |
| western_reserve_project | 1 | 256 | two wave-7 columns that both become item `1760` (names lowercased) | item | LDbase, `cq_wave7.csv` / `cqb_wave7.csv` | low: its 2026-09-08 `table_changes` row is before the 09-22 hold cutoff |

## PISA 2000/2006: most of the class

- Students are numbered within school (`STIDSTD`), and both scripts build `id` from `CNT`+`STIDSTD` and then drop `SCHOOLID`. So in KGZ, THA and LTU (2006), and CAN, CHE and THA (2000), one `id` holds up to 77 students (2006) or 21 (2000). The fix is `id = CNT_SCHOOLID_STIDSTD`.
- **pisa2006** already reads `SCHOOLID`. It's a one-line change, but the files are large.
- **pisa2000 needs care first.** `data/pisa/pisa2000.R` reads the fixed-width file with `SAScii`, then shifts column names by hand (`names(student)[10:228] = names(student)[9:227]`). Its own comment says "caution is advised". Check the layout against the OECD SAS/SPSS control files before trusting any column, including `SCHOOLID`, or re-import from the official SPSS file.
- The licence is CC BY-NC-SA 3.0, so the rebuilt tables are published under the same terms.

## The 9 families that need an occasion or stimulus, not an id

In these the repeats are **different responses** (repeat occasions, or different stimuli) that look the same only because the key was dropped. A dedupe would destroy data. Maybe track them as `rebuild_occasion`:

- **occasion (wave/date/trial):** geography, zhang_2020_trait_creativity_mood, steinberg_2023_mentalizing, schoen_2019_to_2022_mkt, kalimahnorms_alzahrani_2025
- **stimulus (item):** musifeast17_vanderwalle_2025, mentalrotation_wolf_2024, childrensocialcognition_cvencek_2025, western_reserve_project

The other five restore a person key: pisa2000, pisa2006, crspolish_wiesyk_2024 and ptcichina_zhan_2024 (`id`), and rating_speed_2025 (`rater`).

## Done means

- The rebuilt table passes `irw-validate --profile upload` with no `dup_exact`.
- Every family has a `table_changes` row that gives the rows before and after.
- Any `dup_id_item` left over is either explained or handed to #1856.

Refs #2401, #1856.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
