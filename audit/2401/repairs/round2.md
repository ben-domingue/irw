# #2401 round 2: what changed (2026-09-29)

These carry out Ben's "Decisions, round 2" on the identical-rows class (RULES.md). Nothing was uploaded, committed or filed, and nothing touched Redivis. The only network reads were OSF (petley raw files) and PLOS (the jiang S1 .sav).

## 1. `jiang_2024_*`: withdrawn (21 tables, plus 6 item-text tables)

- **Re-checked independently** against a fresh download of the S1 `.sav`. It is 1,792 × 128. Setting `index`/Gender/Age aside, it holds 707 distinct response vectors, and the three row blocks are equal at offsets 0, 707 and 1414.
- `tools/withdrawals/retire_jiang_2024.py` (new) covers:
  - the 21 response tables in `item_response_warehouse_3`;
  - `jiang_2024_{ptsexp,ptsinv,ptspr}__items` in `irw_text`;
  - `jiang_2024_{growthm,instituinteg,ptsacc}__items` in `irw_text_2` (shards from `itemtext/live_tables.csv`).
- The script:
  - is a dry run by default (`APPLY=1` applies);
  - asserts that the `jiang_2024_` prefix in each shard is exactly its target set, and that no other shard holds one;
  - asserts that each draft lost exactly the targets.
- It has been compiled but **not run**.
- `itemtext/withdrawals.csv`: 27 rows appended by hand, `reason=wrong_data`, noted "staged, not yet applied". This follows `withdraw_iesr_translated.py`, so the script does **not** call `ledger.record()` on apply. `itemtext/tests/test_withdrawals.py` passes.
- `audit/2401/repairs/withdrawals_table_changes.csv` (new): 21 "Retired: ..." rows for #2401, with each table's row count.
- `data/jiang_2024_student_thriving.py`: a header line says the family is withdrawn, so it isn't re-ingested.

## 2. `petley_2025_flanker_*`: kept (5 tables)

- (a) `data/petley_2025_flanker.py`: `_expand()` no longer makes the `cumcount` index, and a docstring now explains the expansion.
  - **Nothing to stage.** Study 1 made the index and then dropped it before writing, so it never reached a table.
  - I rebuilt all 5 from OSF p9cbk before and after the edit. The outputs are **byte-identical**, and they match live row counts and columns (`metadata/metadata.csv`).
  - Re-uploading identical tables would gain nothing and risks the append-doubling seen before. So nothing is in `~/irw-stage/2401-audit/batch1/`, and `batch1_petley_table_changes.csv` was not created: no user-visible change.
  - `irw-validate --profile upload` blocks study 1 on `dup_id_item` only, and passes with the waiver. Study 2 passes (warnings only).
- (b) `metadata/data_notes.csv`: 5 rows. The study 2 wording says "person, condition and session (`wave`)", because `wave` there is the real test/retest session.
- (c) `processing_notes/validator_overrides.csv`: 5 `dup_id_item` waivers, `user=ben`.
  - Note: this file already had an uncommitted CRLF→LF rewrite of its first 4 rows, from an earlier session.

## 3. Known-issue flags: `audit/2401/repairs/known_issues_rows.tsv`

- 11 rows (8 families) in the live two-column format (`table<TAB>issue`), all under issue 2401. Source checkout: `~/Dropbox/projects/irw/irw_site/landing/known_issues.tsv`, not edited.
- The live format has **no text column**. The banner is generic and links to the issue. So the user-facing wording for each table is in a `#` comment above its row.
- **Worth a look before pasting:**
  - A flagged page is also removed from search (`noindex`, no JSON-LD or sitemap entry).
  - For `emobank_buechel_2017` the defect is permanent: the source has no annotator id. That reads more like a data note than "being fixed".
  - `megart_tonkovic_2021` is mostly a `dup_id_item`/#1856 matter.

## 4. Rebuild-queue issue draft: `audit/2401/repairs/rebuild_queue_issue.md`

- 14 families, 24 tables, 2,963,483 identical rows.
- PISA is called out, including `pisa2000.R`'s hand-shifted column names.
- It lists the 9 occasion/stimulus families. Not filed.

## Files

Changed:
- `data/petley_2025_flanker.py`
- `data/jiang_2024_student_thriving.py`
- `metadata/data_notes.csv`
- `processing_notes/validator_overrides.csv`
- `itemtext/withdrawals.csv`

New:
- `tools/withdrawals/retire_jiang_2024.py`
- `audit/2401/repairs/{withdrawals_table_changes.csv, known_issues_rows.tsv, rebuild_queue_issue.md, round2.md}`

Staged: none.
