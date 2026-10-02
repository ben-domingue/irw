# #2401 small rebuild batch (RULES.md Decisions, item 8)

2026-09-29. Scripts edited in the worktree `/home/ben/irw-wt/2401-audit` (not committed).
Nothing uploaded. Draft `table_changes` rows: `rebuilds_table_changes.csv`. Item-text drafts:
`itemtext_followups.md`. Raw sources and before/after builds: `/home/ben/irw-stage/2401-audit/raw/`.
Validator: `python3 -m irw_validate.cli --profile upload`. None of these tables has a
`table_changes` row dated 2026-09-22 or later, so none is held.

`bitew_2020_*` (item 8) was not part of this batch.

## tuason_2021_covid_coping_enjoy

- **File changed:** `data/tuason_2021_thriving_covid.py`. `Enjoy_NN` = 1 if NN is among the
  comma-separated picks in `Emjoy`, else 0. Item codes and ids (row index) are unchanged.
- **Source:** PLOS S2 File (`.s002`), downloaded fresh. Its sha256 (c6d0daf7...3230) equals the
  cached copy the dossier used.
- **Rows:** 21,574 before and after (938 ids x 23 items). Per-id sums before: 0 for 322 ids, 2
  for 1, 4 for 2, 5 for 612, 8 for 1. After: 5 for all 938.
- **Check against the dossier:** of the 616 ids that were not all-zero, 610 match on all 23 cells
  (99.9% cell agreement). The 6 that differ had sums of 2, 4, 5, 5, 8 and 4. This is the dossier's
  610/616. 1,622 cells changed (1,617 from 0 to 1, 5 from 1 to 0) across 328 ids (322 + 6).
- **Siblings:** the script also writes the four other tuason tables. Rebuilt before and after the
  edit, they are byte-identical, so they need no re-upload.
- **resp format:** now written as `0`/`1` (it was `0.0`/`1.0`).
- **Validator (upload):** conforms, passes. One warning, `imputed_values` (binary concentration).
- **Staged:** `/home/ben/irw-stage/2401-audit/rebuilds/tuason_2021_covid_coping_enjoy.csv`
- **Item text:** the live `public_note` describes this defect. A replacement is drafted in
  `itemtext_followups.md`. It should go up only after the rebuilt table does.

## mclaughlin_samuel_2025_auditory_session_2

- **File changed:** `data/mclaughlin_samuel_2025_auditory_study.py`.
  - `_convert_transcription_long` keeps only `Correct` as `resp` and no longer writes the
    `Incorrect` complement rows or `itemcov_response_type`.
  - The Mandarin familiarity ratings and the session-2 SB total are no longer appended as items.
    The two helper functions stay but are no longer called.
- **Source:** OSF snmqt, `Analysis/Pre-processed_data/*.csv`, downloaded fresh. The unedited
  script reproduces the live table exactly (17,347 rows, 209 ids, 43 items).
- **Rows:** 17,347 to 8,360.
  - 8,360 complement rows removed.
  - 627 non-trial rows removed (209 each of `familiarity_mc_language`, `familiarity_mc_accent`
    and `sb`).
  - 209 ids, 40 items (24 accent, 16 noise). Columns: `id, item, resp, trial_index,
    itemcov_talker`. resp 0-4, no duplicate id+item.
  - The 8,360 rows kept match the old `correct` rows on id, item, trial_index and resp, with
    0 differences.
- **Sibling:** `mclaughlin_samuel_2025_auditory_session_1` is byte-identical before and after, so
  it is unaffected. Note, not fixed here: it is a one-item table (`sb`, 251 rows), which the
  current no-single-item-scales rule would not accept at intake.
- **cov_hhie_score: it should not be present as built.** `HHIE.csv` is keyed on *session-1*
  Gorilla ids: all 251 of its subjects are session-1 ids, and 0 of them are among the 209
  session-2 ids. So the script's merge never matches, and the column is dropped as all-empty.
  Its absence from the live table is not `script_drift`. HHIE could be attached through the
  source's crosswalk (`SB1_SB2_outliers_removed.csv`, `Session1_ID` to `Session2_ID`, which covers
  207 of the 209). That would add a new covariate, so it needs a ruling and was not done.
- **Validator (upload):** conforms. It is blocked only by `name_length`: the live name has 41
  characters and the cap is 40. This is a pre-existing published name. With
  `--override-check name_length`, it passes, with warnings `imputed_values`, `multi_scale`
  (accent/noise design blocks, one task) and `resp_scale_mixed` (0-3, 0-4 and 1-4 observed).
  **The override appended a line to `processing_notes/validator_overrides.csv` in the worktree.
  I gave the waiver myself, following the 2026-09-25 live-name precedent; Ben should confirm it
  or revert it.**
- **Staged:** `/home/ben/irw-stage/2401-audit/rebuilds/mclaughlin_samuel_2025_auditory_session_2.csv`

## amatus_cipora_2024_fsmas_se

- **File changed:** `data/amatus_cipora_2024.py`.
  - `age_range` is no longer dropped. It is kept as `cov_age_range`, because it is a band
    ("< 20 years", "20-29 years", ..., "over 50 years").
  - Every output table drops any `cov_*` column that is empty for all its rows. In fsmas_se
    that removes `cov_math_load` (as ruled) and also `cov_age`, which is empty for all 258
    teachers. This follows the `cov_all_null` class rule. No other table loses a column.
- **Source:** OSF gszpb `AMATUS_dataset.csv`. Its sha256 (d4f8a6b5...) matches the dossier.
- **Rows:** 2,322 before and after (258 ids, 9 items). Apart from the column changes, the file is
  identical, so no response changed. The -1 "not yet taught" codes in `cov_ease_teaching_*` and
  `cov_preference_teaching_*` are left as they are.
- **Teacher age bands:** 20-29: 201; 30-39: 24; < 20: 12; 40-49: 12; over 50: 9. The 12 teachers
  under 20 are as the source gives them.
- **Validator (upload):** conforms, passes. One warning, `imputed_values`.
- **Staged:** `/home/ben/irw-stage/2401-audit/rebuilds/amatus_cipora_2024_fsmas_se.csv`
- **Siblings: affected, not staged for upload.** All nine other `amatus_cipora_2024_*` tables
  (amas, arithmetic, bfi_n, gad, pisa_me, sdq_l, sdq_m, stai, tai) include the 258 teachers (256
  in arithmetic), who have `cov_age` NA and no other age. Rebuilt with the edited script, each
  gains only `cov_age_range`, with the same rows and every other column identical. The
  rebuilds are in `/home/ben/irw-stage/2401-audit/rebuilds/amatus_siblings_pending_ruling/`.
  There are no `table_changes` rows for them. Whether to upload them is Ben's call. If they are
  not uploaded, the edited script no longer reproduces the live siblings.
- **Item text:** the corrected SE1-SE4 option mapping is in `itemtext_followups.md`.

## lee_2020_empathy

- **File changed:** `data/lee_2020_medical_students.py`, docstring only. It now says items 11-20
  are *not* reverse-scored: they are the negatively worded JSPE stems, and resp is raw agreement
  on every item. I re-checked this on the fresh PLOS S1 `.sav`: block means are 5.58 and 2.80,
  and the JPSE_12 label is as quoted. I also checked the script's other claim, and it holds:
  `JPSE_sum_total` equals the plain sum of the stored items in 663 of 664 complete rows. So the
  source's own total is computed without reversal, and the header now says so.
- No rebuild, no `table_changes` row. Data unchanged.
