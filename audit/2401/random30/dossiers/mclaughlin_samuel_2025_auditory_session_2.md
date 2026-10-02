# mclaughlin_samuel_2025_auditory_session_2 (slot 7, agent b)

**Current state.** Live in `item_response_warehouse_2` (v26_0). No item text. Not in withdrawals, table_changes, data_notes, or the dup_id_item/cov_age results. Script: `data/mclaughlin_samuel_2025_auditory_study.py`.

**Data (full read, 17,347 rows; matches metadata.csv).** 209 ids, 43 items, columns `id|item|resp|trial_index|itemcov_response_type|itemcov_talker`. `live_dup`: 8,360 excess id+item pairs, resolved only by `itemcov_response_type`.
- **Every transcription trial is in the table twice.** The script writes one row with `resp = correct` (keywords right) and one with `resp = incorrect` (keywords wrong) for each accent_/noise_ trial. In all 8,360 trials `correct + incorrect = 4`, so the second row is the exact complement of the first, with the scale reversed in the same `resp` column. Any analysis of `resp` that does not filter on `itemcov_response_type` doubles N and cancels the signal (means 2.07/1.93 and 2.42/1.58). Fix: keep the `correct` rows only.
- **Three non-trial items are mixed in:** `familiarity_mc_language` and `familiarity_mc_accent` (self-rated familiarity, 0-100) and `sb` (the Sandwich Builder total score, 0-10, a different task). Different constructs and scales from the 0-4 keyword counts. Fix: drop them, or move them to a separate table / `cov_`.
- No sentinels; no `cov_*` columns.

**Rights.** No item text; skipped.

**Source caveat.** No header; nothing stated.

**Also recorded.** The script merges `cov_hhie_score` into the session-2 frames when `HHIE.csv` is present, but the live table has no `cov_` column. That may be `script_drift` or just a missing file. Not investigated.

**Outcomes.** `fix` (complement rows, high); `fix` (mixed-in familiarity/sb items, high); `script_drift` (HHIE covariate, low).
