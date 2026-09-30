# Item-text repairs, #2401 (RULES.md Decisions 7 and 8), 2026-09-29

Nothing was uploaded, committed or pushed. The staged files are in `/home/ben/irw-stage/2401-audit/itemtext/`. The live copies they were built from are in `live/` beside them.

## 1. bitew_2020: administered-language fallback (4 tables)

**Rights register check first.** PHQ-9 is `ship`, under the "PHQ and GAD screener family" row (an express grant). OSSS-3 and GSE have no row, so neither is blocked. All four tables went ahead.

**The layout follows the schema and precedent, not the brief's wording.** The brief said to put the English in the `_translated` columns. The 2026-09-01 schema (`itemtext_standard.md`, "The fallback") says otherwise, as do both precedents: round 2 (`language_backfill/round2/add_language.py`, 16 tables uploaded 2026-09-02) and `gizaw_2023_phq9` (Amharic, batch_040). When the administered wording is not published:
- the English **stays in the base fields**;
- `language=Amharic` (the schema names languages plainly; it uses no code);
- the four `_translated` columns are present and `NA`;
- `text_source=translated_substitute`.

No base text field changed (the build script asserts this).

**`translation_source` is set per table rather than `study_supplied` for all four**, because that value is only accurate for LTE:

| table | translation_source | why |
|---|---|---|
| `bitew_2020_lte` | `study_supplied` | the study's own `.sav` variable labels |
| `bitew_2020_osss3` | `third_party_english` | canonical OSSS-3 wording, taken from Kocalevent/Berg 2018 (paper ref 28), not from the originator or the study |
| `bitew_2020_phq9` | `official_instrument_english` | canonical PHQ-9; the same basis as `gizaw_2023_phq9` |
| `bitew_2020_self_efficacy` | `mixed` | the items are canonical GSE English; the anchors are the study's `.sav` value labels |

**`bitew_2020_self_efficacy` also gains `SEFFICAY`** (GSE item 1: "I can always manage to solve difficult problems if I try hard enough"). The response table has carried this item since the 2026-08-31 restore (#1655), but the item text never had it, so the table failed the `item` join. It now has 40 rows and 10/10 items. Its `public_note` no longer says "9 of 10". The `pending_index_notes.csv` row saying the same is left for Ben to mark `resolved` after upload.

**Gates:** `validate_items.R --table-sets` PASS; `normalize_nulls.R` applied; `audit_batch.R` 5/5 PASS; `irw-validate` (upload profile) clean; `check_provenance.R` clean.

## 2. IES-R `_translated` removal

- **`beck_2021_iesr`: done (staged).** All four `_translated` columns are now `NA`. `item_text_translated` had been the Weiss & Marmar English. The instructions and anchors were English renderings of the German, which is itself a derivative of the blocked instrument. The German base text, `language=German` and the 88 rows are unchanged.
- **`ali_2021_iesr`: whole withdrawal, approved by Ben 2026-09-29.** It has no `_translated` columns. Its `item_text` *is* the English Weiss & Marmar IES-R (22/22 verbatim, e.g. "I felt watchful and on-guard.") and its `instructions` are the Weiss preamble, so no unblocked wording is left to keep. `ali_2021_iesr__items` (irw_text, 110 rows) is deleted whole by the same script. The response table `ali_2021_iesr` stays. A dry run passes; the script has not been applied.

  **table_changes-style note (item text):**

  | table | date | change | refs |
  |---|---|---|---|
  | `ali_2021_iesr__items` | 2026-09-29 | Item text withdrawn whole: the English IES-R wording (Weiss & Marmar 1997) is covered by the register's IES-R `block` row. The response data are unchanged. | #2401 |
  | `beck_2021_iesr__items` | 2026-09-29 | `*_translated` columns emptied: the English IES-R is covered by the IES-R `block` row. The German administered text is unchanged. | #2401 |

  The `ali_2021_iesr` row in `itemtext/itemtables/batch_003/provenance.csv` now follows the withdrawal convention: its `public_note` begins "IRW does not offer item text for", and its note records the withdrawal.

## 3. The rights sweep now reads `_translated`

- **`itemtext/sweep_instrument_rights.py`:**
  - It now also scans `item_text_translated`, `option_text_translated`, `instructions_translated` and `section_prompt_translated` in every table that carries them. The columns are found per table with `list_variables`.
  - Each hit is labelled by column. A hit is marked NEW when the same table's `item_text` did not match that instrument.
  - A new `--csv` option writes every hit to a file.
  - It also fixes a defect that was already there: the LIKE filter was repeated for every table in the UNION. With 83 blocking rows, that pushed every chunk past Redivis's 1,000,000-character query limit, and the sweep fell back to one query per table. The filter is now applied once, outside the union.
- **`irw_validate/rights.py`:** `check_item_text` now reads the same four `_translated` columns and names the column in each finding. There is a new test, `test_translated_column_hit_warns`, and `irw_validate/tests` all pass.

**Sweep run** (read-only, `--version current`, all three text shards; no table or column was skipped):
- 1,129 of 2,450 tables carry `_translated` columns.
- The sweep found 52 hits in all.
- **8 tables are newly flagged** because their `_translated` columns match an instrument their `item_text` does not. They are listed in `audit/2401/triage/rights_translated.csv`.

The 8 new flags split into two groups:
- **3 strong leads (3 or more items):**
  - `jablonska_2020_swls` (SWLS, 5 items);
  - `queiros_2018_qcae` (IRI, 4);
  - `sun_2025_morality_study2_meaning` (MLQ, 3). The skill records this table as a known false positive: it is PERMA-Profiler, not the MLQ.
- **5 weak leads (1 item each):** `corti_2023_academic_adaptation` (SWLS), `dasilva_2019_hexaco24` (SDT), `merlo2025_eng_emotional` (SDT), `sv-maia2_randelovic_2021_maia` (STAI) and `rogowska_2023_maia2` (STAI). These look incidental.

None of these were acted on.

`beck_2021_iesr` is **not** among the hits. The IES-R register row has no `match_item_text`; it matches only on `match_item_code`, and this sweep does not check item codes yet. Adding the Weiss stems to that row would let the sweep find other English IES-R copies.

## Files changed (worktree)

- `itemtext/itemtables/batch_008/provenance.csv`: rows for the 4 bitew tables (the fallback fields, the reasoning, the SEFFICAY addition, public notes) and a rights note on the beck row. The `uploaded` stamps are left as history.
- `itemtext/language_backfill/backfill_provenance.csv`: beck row changed to `translation_source=not_translated`, with the reason in the note.
- `itemtext/instrument_rights_register.csv`: the IES-R row's `notes` now record the 2026-09-29 ruling and the approved withdrawal of all of ali's item text.
- `itemtext/withdrawals.csv`: two rows added, both `rights`, `IES-R`, with `released` blank: `beck_2021_iesr__items` (`partial`) and `ali_2021_iesr__items` (`whole`).
  - `test_withdrawals.py` currently fails on `tools/withdrawals/retire_jiang_2024.py`, which a sibling agent in this audit is still writing along with its ledger row. It should pass once that agent finishes.
- `tools/withdrawals/withdraw_iesr_translated.py`: new script. It blanks beck's `_translated` columns (partial) and deletes `ali_2021_iesr__items` (whole). It does a dry run by default and has not been run. It rebuilds the table from the published copy and refuses to push unless the result equals the staged file.
- `itemtext/sweep_instrument_rights.py`, `irw_validate/rights.py`, `irw_validate/tests/test_rights.py`: the rights sweep changes described in section 3.
- `audit/2401/repairs/build_itemtext.py`: the build script for the staged files.
- `audit/2401/triage/rights_translated.csv`: the new flags.

## Staged (`/home/ben/irw-stage/2401-audit/itemtext/`)

`bitew_2020_lte__items.csv` (24 rows), `bitew_2020_osss3__items.csv` (14), `bitew_2020_phq9__items.csv` (36), `bitew_2020_self_efficacy__items.csv` (40), `beck_2021_iesr__items.csv` (88). Also there: `rights_sweep.log` and `rights_sweep_hits.csv`.

Upload the bitew tables with `red_up`'s delete-then-recreate. For beck and ali, run `withdraw_iesr_translated.py` (`APPLY=1`). Do not also push beck with `red_up`. Its ledger row already exists, so do not call `ledger.record()` again.
