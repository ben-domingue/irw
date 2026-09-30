# `_translated` rights flags, #2401, 2026-09-29

The 2026-09-29 sweep flagged 8 tables only through their `_translated` columns (`audit/2401/triage/rights_translated.csv`). Each was read item by item from the live item text (`irw::irw_itemtext()`, copies in `/home/ben/irw-stage/2401-audit/itemtext/live/`).

Two rulings apply, both Ben's and both from 2026-09-29, both in RULES.md:
- **Decision 7:** a `block` row covers `*_translated`.
- **"A block covers translations":** a `block` row covers the instrument in every language, in `item_text` as well as in `*_translated`. This superseded the first pass, which had blanked only `_translated`.

Nothing was uploaded, committed or pushed.

## Verdicts

| table | family | verdict | evidence | action |
|---|---|---|---|---|
| `sun_2025_morality_study2_meaning` | MLQ | CONFIRMED | MLQ-Presence, not PERMA: codes `tsmlq1`-`tsmlq5`, `_translated` 5/5 MLQ verbatim ("I understand my life's meaning."), and `item_text` is the Chinese MLQ | **whole withdrawal**, nothing staged |
| `jablonska_2020_swls` | SWLS | CONFIRMED | `_translated` is the canonical English SWLS 5/5 ("In most ways my life is close to my ideal."), and `item_text` is the Polish SWLS | **whole withdrawal**; the earlier `_translated`-only staged file was removed |
| `queiros_2018_qcae` | IRI | CONFIRMED (6 items, not 4) | QCAE items 1-6 are Davis's IRI (PT 1, 3, 4, 5, 6; FS 2), e.g. QCAE_5 "...'put myself in his shoes' for a while". The sweep missed QCAE_2 and QCAE_3, whose wording varies and uses a curly apostrophe | **partial:** QCAE_1-6 rows dropped, 124 -> 100 |
| `corti_2023_academic_adaptation` | SWLS | FALSE | P1_d "I'm satisfied with my life as a student" is an FTAQ item | none |
| `dasilva_2019_hexaco24` | SDT/CSDT | FALSE | HEXACO24_7 "I think science is boring" is a BHI item, not the IMI | none |
| `merlo2025_eng_emotional` | SDT/CSDT | FALSE | ENG_EMO_09 "I think studying is boring" is a Student Engagement Scale item | none |
| `sv-maia2_randelovic_2021_maia` | STAI | FALSE | MAIA2_1 "When I am tense, I notice where in my body..." is a MAIA-2 item | none |
| `rogowska_2023_maia2` | STAI | FALSE | MAIA2_01 is the same MAIA-2 item | none |

Two sibling tables were added under the second ruling:

| table | family | evidence | action |
|---|---|---|---|
| `gomez_2022_qcae` | IRI | QCAE1r, QCAE2r and QCAE3-QCAE6 carry the English IRI in `item_text` | **partial:** those rows dropped, 124 -> 100 |
| `powell_2018_qcae` | IRI | QCAE1-QCAE6 carry the English IRI in `item_text` | **partial:** those rows dropped, 124 -> 100 |

## Staged (`/home/ben/irw-stage/2401-audit/itemtext/`)

`queiros_2018_qcae__items.csv`, `gomez_2022_qcae__items.csv` and `powell_2018_qcae__items.csv`: 100 rows and 25 items each. The instructions and anchors are unchanged. Built by `audit/2401/repairs/build_rights_translated.py`, which asserts that the IRI stem is in the dropped set and not in what is kept.

**Gates:**
- `normalize_nulls.R` applied.
- `irw-validate --profile upload`: clean.
- `check_provenance.R`: clean.
- `validate_items.R --table-sets` and `audit_batch.R` fail or warn only on the six withdrawn items. They are still in the response data, which is expected for a partial withdrawal.

## Records

- **`itemtext/withdrawals.csv`:** 5 rows appended after the uruguay and DEMOS rows, all with `released` blank:
  - `sun_2025_morality_study2_meaning` and `jablonska_2020_swls` as whole withdrawals;
  - the three QCAE tables as partials.
  - The earlier jablonska and queiros `_translated`-only rows are left in place, because the ledger is append-only. The new rows say they supersede them.
  - `itemtext/tests/test_withdrawals.py` passes.
- **Provenance:** the rights note and `public_note` are updated in `batch_054` (jablonska), `batch_151` (queiros), `batch_041` (gomez) and `batch_142` (powell). CRLF line endings are kept. `check_provenance.R` is clean.
- **Register:** the SWLS, IRI and MLQ rows now say that translations are covered, and name the tables affected.

## NOT DONE: the withdrawal script

The auto-mode permission classifier refused the rewrite of `tools/withdrawals/withdraw_translated_rights.py`, flagging it as a cloud-storage mass delete. The rewrite would have added two whole-table deletes and three row-dropping replaces across `irw_text` and `irw_text_2`.

The committed script still implements only the first `_translated`-only pass. It is safe as it stands: it aborts because jablonska's staged file is gone and queiros' staged file no longer matches. It must not be run until it is extended.

The new ledger rows cite it and say so. The extension follows `withdraw_bfi2.py`:
- `WHOLE` = {`irw_text`: sun_2025_morality_study2_meaning__items; `irw_text_2`: jablonska_2020_swls__items};
- `PARTIAL` (`irw_text_2`) = the three QCAE tables with the drop sets above;
- keep-set: `jablonska_2020_rses__items` and `jablonska_2020_instagram_addiction__items`;
- the partials are re-derived from the published copy and compared with the staged files before anything is deleted.

That needs Ben, or a permission rule.

## Still open

- `sun_2025_morality_study1_meaning` was not re-read. The register's PERMA claim was wrong for study2.
- Any other QCAE table carries the same six IRI items.
- jablonska's response-table item codes are English renderings of the SWLS ("52. I am satisfied with my life."). No item-text withdrawal reaches them.
