# #2401 batch 1: what is staged (2026-09-30)

These carry out BATCH_1.md B and C1 under Ben's "Decisions, round 2" (RULES.md). Nothing was uploaded, committed or filed. Nothing was written to Redivis; the only Redivis calls were reads.

- **Staged:** 29 tables in `~/irw-stage/2401-audit/batch1/`, plus one retirement (DEMOS) scripted but not run.
- **Change rows:** `audit/2401/repairs/batch1_table_changes.csv`, 30 rows, one per table, dated 2026-09-29 under #2401, with `irw_version` blank.
- **Gate:** `python3 -m irw_validate.cli --profile upload ~/irw-stage/2401-audit/batch1/` blocks on 3 files. All three are covered by waivers recorded in `processing_notes/validator_overrides.csv`, and each passes when re-run with its recorded waiver (`--override-check`). Details are under each family below.

Row counts are live table rows. `metadata.csv`'s `n_responses` counts non-missing `resp` only, so it is lower wherever the live table carried blank-`resp` rows (guatemala, chile). The per-table figures for those two families are in `batch1_table_changes.csv`.

## guatemala_2024_homes (17 tables)

- **Fix:**
  - code 3 ("NS") → dropped on the Sí/No/NS grids (15 tables);
  - blank-`resp` rows dropped (all 17);
  - `cov_lang` 98 → missing (the mechanical fix, folded in).
- **Rows:** 1,094,874 → 658,890 across the 17 tables. By table: water 41,316 → 32,118 and transport 68,860 → 4,322; the rest are in the change rows.
- **Validator:** all 17 pass. Warnings only.
- **Source of truth:** `data/guatemala_2024_homes.do`. The staged files were built by the untracked Python port `audit/2401/repairs/ports/guatemala_2024_homes.py`, because Stata isn't installed here. I checked that the edited .do carries the same logic as the port:
  - the `cov_lang` recode;
  - the same grid regex (`^[a-z]+_p0[45]a[0-9][0-9][ac][0-9]+$`), in the 15 grid blocks (water … transport) and not in country or transparency;
  - `drop if missing(resp)` in all 17 blocks.

  The port has been **deleted**. The .do has **not been executed**.
- **Superseded:** the 17 `mechanical/guatemala_2024_homes_*.csv` files, already in `mechanical/superseded_by_batch1/`. Their 17 rows were removed from `mechanical_table_changes.csv`, and their text is merged into the batch 1 rows.

## chile_2023 (3 tables)

| table | rows |
|---|---|
| `chile_2023_social-welfare-survey_h` | 146,042 → 135,907 |
| `chile_2023_social-welfare-survey_yy` | 67,404 → 49,343 |
| `chile_2023_children-adolescents-survey_cp_c` | 741,678 → 625,991 |

- **Validator:** `_h` and `_yy` pass. `_cp_c` blocks on `name_length` (43 characters, already published). It has a waiver (2026-09-30) and passes with it.
- **Superseded:** none.
- **Still open, not mine:** the chile ports (`audit/2401/repairs/ports/chile_*.py`) are tracked files, and the staged chile files came from them. The edited `.do` files were not executed. The earlier notes flag `cov_income_clp` as a misleading name for "income needed" (`cov_income_needed_clp`).

## EEN_Lacey_2024_Parent (1 table)

- **Fix:** `mh_treatable` recoded to No 0 / Maybe 1 / Yes 2, and `covid_jobloss` 2 → missing.
- **Rows:** 59,640 → 58,146.
- **Validator:** passes.
- **Superseded:** none.

## Dedupes (C1): 4 tables

| table | rows | validator |
|---|---|---|
| `mhscdc_fried_2020_ema` | 78,696 → 70,958 | pass |
| `smoking_perseverance_mcneish_2025` | 10,572 → 10,569 | pass |
| `selm_2019_climate_knowledge` | 606 → 603 | blocks on `dup_id_item` (the 6 conflicting rows left for #1856); passes with its recorded waiver |
| `foundationalassist_worden_2026` | 1,712,991 → 1,712,973 | pass |

- **Superseded:** `mechanical/selm_2019_climate_knowledge.csv`, already in `superseded_by_batch1/`. Its `cov_gender` drop is merged into the batch 1 row, and its mechanical row is removed.

### foundationalassist_worden_2026 (new today)

- **How it was built:** from the live table, not the raw data. The raw file (HF `ASSISTments/FoundationalASSIST`) is gated.
- **What was removed:** the 18 rows that `duplicated()` marks in the fetched live table (14 ids).
- **Script:** `data/foundationalassist_worden_2026.R` now runs `distinct()` after mapping.
- **Two things to look at before uploading:**
  1. **The dup_exact evidence is wrong.** It said "identical down to the timestamp". In fact all 18 have `date` = NA. The script already runs `distinct()` on the raw rows, so these rows *differed* in the raw file and became identical only when an unparseable `end_time` became NA. They may be separate, undated attempts at the same problem: 49,746 id+item repeats are normal in this table. Removing them follows the ruling, but its premise is weaker than stated.
  2. **The licence.** The earlier notes found that the HF card now declares `cc-by-nc-4.0`. `biblio.csv` records Custom / CC BY 4.0.
- **Also noted, not changed:**
  - `date` holds the literal string `NA` on 3,390 live rows (`write_csv`'s default).

## rt in milliseconds → seconds (4 tables)

All four were built in the `repair_classes.py` style: the fix is the SELECT on the live table (`CAST(rt AS FLOAT64)/1000 AS rt`, with every other column passed through in live order), after `redivis_shim.install()`. Each export was fetched with the live `rt` alongside. The checks were:

- row count equal to live `COUNT(*)`;
- the same NULLs;
- every value exactly live/1000, with a maximum absolute difference of 0;
- a median exactly 1000× smaller.

| table | rows (before = after) | median rt | ms confirmed by | validator |
|---|---|---|---|---|
| emoji_scheffler_2024 | 16,370 | 2,669 → 2.669 | magpie timer; summed RTs sit within each submission's ms span | pass |
| megart_tonkovic_2021 | 176,964 | 611 → 0.611 | deposit metadata: "expressed in milliseconds" | pass |
| spalex_aguasvivas_2020 | 16,962,757 | 1,189 → 1.189 | figshare 5924647: "reaction time in milliseconds" | pass, but see below |
| vollbracht_et_al_2026_ambulatory_assessment | 224,028 | 2,162 → 2.162 | inferred: the 15 per-beep RTs sum to a median of 24,342, impossible as seconds between beeps 1.5 to 3.5 h apart (no unit in the codebook) | blocks on `name_length` (43 characters, published); **waiver recorded today**; passes |

- **Scripts:** the edits in the four `data/` scripts are correct. For emoji, megart and vollbracht, the earlier agent's raw rebuilds reproduce live exactly before the edit, and after it only `rt` changes, by exactly ÷1000. megart's `resp = as.integer(stimulus_acc)` matches the 1/0 already live.
- **spalex was not rebuilt.** The earlier agent's 2.4 GB raw rebuild in `batch1_tools/rt/spalex/` was not used.
- **spalex validation:** the file is 2.6 GB, over the validator's 512 MB cap, so the full-directory run did only the name checks (`size_downgrade`). A 2M-row head sample conforms and passes.
- **Pre-existing, not changed:**
  - spalex has negative `rt` (minimum −3,599 s after the fix) and a non-Unix `date` (`2014-05-28 22:52:45`);
  - megart's `date` is also not numeric.
- **Mechanical fixes for spalex and megart: there are none.** Neither table is in `mechanical_spec.json`, in `mechanical_table_changes.csv`, in `mechanical/` or in its `repair_log.jsonl`. The detector flags on them are only `rt_units`, `dup_id_item` and `dup_exact` (megart). So nothing was merged, and nothing moved to `superseded_by_batch1/`, which still holds exactly the 18 files above.

## DEMOS: retirement scripted, not run

- **Script:** `tools/withdrawals/retire_demos.py` follows the README and `retire_marcatto_ocs.py`:
  - it is a dry run by default (`APPLY=1` applies);
  - it takes a write token via `irw_secrets.load_write_token()`;
  - it names an explicit `TARGET` and asserts it is in `current` and in no other shard;
  - it asserts the draft lost exactly DEMOS.
- **Ledger:** as with `retire_jiang_2024.py`, the ledger row was written by hand, so the script does not call `ledger.record()`. That row is already in `itemtext/withdrawals.csv`: `DEMOS,item_response_warehouse,whole,…,wrong_data,…,10656`.
- **Item text: none.** Checked live 2026-09-30: no `DEMOS*` table in `irw_text`, `irw_text_2` or `irw_text_3`, and none in `itemtext/live_tables.csv`.
- **Checks:** the script compiles, and `python3 -m pytest itemtext/tests/test_withdrawals.py` passes (7 tests, 322 subtests).
- **Change row:** "Retired: …", 10,656 rows withdrawn.

## Files changed in this pass

- `data/foundationalassist_worden_2026.R` (post-mapping `distinct()`)
- `processing_notes/validator_overrides.csv` (+1 row, the vollbracht `name_length` waiver)
- `audit/2401/repairs/mechanical_table_changes.csv` (18 superseded rows removed, 124 → 106, matching the 106 files left in `mechanical/`)
- `audit/2401/repairs/batch1_table_changes.csv` (new)
- `audit/2401/repairs/batch1.md` (new)
- `audit/2401/repairs/ports/guatemala_2024_homes.py` (deleted)

**Not touched:** spain_2013_services (another session).

## Held (2026-09-30): foundationalassist_worden_2026

Taken out of the upload set, and its script edit reverted. Two reasons:
- The 18 removed rows differed in the raw file, so they may be real attempts that the script collapsed. That would make this a rebuild, not a dedupe.
- The source's dataset card now says **CC BY-NC 4.0**, which is not an open license under IRW's rules.

The license question comes first. The staged file is at `~/irw-stage/2401-audit/held/`.
