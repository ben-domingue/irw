# `_translated` rights flags, #2401 (RULES.md Decision 7), 2026-09-29

The 2026-09-29 sweep flagged 8 tables only through their `_translated` columns (`audit/2401/triage/rights_translated.csv`). Each was read item by item from the live item text (`irw::irw_itemtext()`, copies in `/home/ben/irw-stage/2401-audit/itemtext/live/`). Nothing was uploaded, committed or pushed.

## Verdicts

| table | family | verdict | evidence |
|---|---|---|---|
| `jablonska_2020_swls` | SWLS | **CONFIRMED**, staged | `item_text_translated` is Diener's canonical English SWLS, 5/5 verbatim ("In most ways my life is close to my ideal." ... "If I could live my life over, I would change almost nothing."). |
| `queiros_2018_qcae` | IRI | **CONFIRMED** (6 items, not 4), staged | QCAE items 1-6 are Davis's IRI, near-verbatim, e.g. QCAE_5 "When I am upset at someone, I usually try to 'put myself in his shoes' for a while". The sweep missed QCAE_2 (FS: "usually objective when I watch a film or play") and QCAE_3 (PT: "look at everybody's side of a disagreement", which uses a curly apostrophe). |
| `sun_2025_morality_study2_meaning` | MLQ | **CONFIRMED, STOPPED** | This is the MLQ-Presence subscale, not PERMA: codes `tsmlq1`-`tsmlq5`, and `_translated` is 5/5 MLQ verbatim ("I understand my life's meaning."). `item_text` is the Chinese MLQ, and the MLQ row covers translations, so this would be a whole withdrawal. It is held for Ben. |
| `corti_2023_academic_adaptation` | SWLS | FALSE | P1_d "I'm satisfied with my life as a student" is an FTAQ item, not an SWLS one. |
| `dasilva_2019_hexaco24` | SDT/CSDT | FALSE | HEXACO24_7 "I think science is boring" is a Brief HEXACO Inventory item, not the IMI. |
| `merlo2025_eng_emotional` | SDT/CSDT | FALSE | ENG_EMO_09 "I think studying is boring" is a Student Engagement Scale item. |
| `sv-maia2_randelovic_2021_maia` | STAI | FALSE | MAIA2_1 "When I am tense, I notice where in my body the tension is located" is a MAIA-2 item. |
| `rogowska_2023_maia2` | STAI | FALSE | MAIA2_01 is the same MAIA-2 item, in its Polish-to-English rendering. |

## What was done for the two staged tables (the beck_2021_iesr pattern)

- **`jablonska_2020_swls`:** the whole table is the SWLS.
  - `item_text_translated` and `option_text_translated` are now `NA` on all 35 rows. The anchors are the appendix's English rendering of the Polish SWLS anchors; they were blanked as beck's were.
  - The Polish base fields are unchanged.
  - Provenance: `translation_source` is now `not_translated` (it was `study_supplied`), and the rights note and `public_note` are updated.
- **`queiros_2018_qcae`:**
  - `item_text_translated` is now `NA` for QCAE_1 to QCAE_6 only (24 rows).
  - The other 25 items, the instructions, the anchors and the Portuguese base fields are unchanged.
  - Provenance: `translation_source` stays `mixed`. A rights note is added and `public_note` item (3) is added.
- **Gates** (both tables):
  - `validate_items.R --table-sets` PASS;
  - `normalize_nulls.R` applied;
  - `audit_batch.R` 2/2 PASS (run on a scratch copy, so no committed report was overwritten);
  - `irw-validate --profile upload` clean;
  - `check_provenance.R` clean.

## Files

- **Staged** in `/home/ben/irw-stage/2401-audit/itemtext/`: `jablonska_2020_swls__items.csv` (35 rows) and `queiros_2018_qcae__items.csv` (124 rows).
- **Build script:** `audit/2401/repairs/build_rights_translated.py`.
- **Withdrawal script:** `tools/withdrawals/withdraw_translated_rights.py`, new, covering both tables (shard `irw_text_2`).
  - It does a dry run by default and has not been run.
  - It re-derives each table from the published copy and aborts unless the result equals the staged file. That filter was checked offline against the live copies and matches.
- **Ledger:** `itemtext/withdrawals.csv` has 2 new rows, both `partial` and `rights`, with `released` blank.
  - The rows were written by hand, so do not call `ledger.record()` again.
  - `itemtext/tests/test_withdrawals.py` passes.
- **Provenance:** `itemtext/itemtables/batch_054/provenance.csv` (jablonska) and `batch_151/provenance.csv` (queiros). CRLF line endings are preserved.
- **Register:** `itemtext/instrument_rights_register.csv`, with a 2026-09-29 note added to the SWLS, IRI and MLQ rows. The MLQ note corrects "sun_2025_morality_study{1,2}_meaning ... are PERMA-Profiler".

Upload: run `withdraw_translated_rights.py` with `APPLY=1`, or use `red_up` delete-then-recreate. Do one or the other, not both.

## For Ben

1. **`sun_2025_morality_study2_meaning`: whole withdrawal?** Its Chinese `item_text` is the MLQ-Presence subscale, and the MLQ row says translations are covered. Nothing is staged. `sun_2025_morality_study1_meaning` was not re-read. Since the register's PERMA claim was wrong for study2, study1 should be checked too.
2. **Translated base text:** is it also blocked? This is the same open question as beck's German IES-R.
   - jablonska: the Polish SWLS stays live in `item_text`.
   - queiros: the Portuguese renderings of the six IRI items stay live in `item_text`.
   - The SWLS and IRI rows, unlike the MLQ row, do not say whether they reach translations.
3. **A second surface on jablonska:** the response table's `item` codes are the deposit's English renderings of the SWLS ("52. I am satisfied with my life."). No item-text change reaches them.
4. **Not in this brief:** `gomez_2022_qcae` and `powell_2018_qcae` carry QCAE items 1-6, which are the IRI, in English in base `item_text`. The sweep lists them as ordinary `item_text` hits.
