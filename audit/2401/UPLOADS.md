# #2401 uploads (Ben's confirmations)

A `table_changes` row is added only once a release is live (red_up/README.md). This file records what Ben has confirmed uploaded to a draft, so those rows can be written with the right version once the release is out.

| date | what | tables | draft/release |
|---|---|---|---|
| 2026-09-30 | `rights_recode/` | jablonska_2020_swls | item_response_warehouse_3 draft |
| 2026-09-30 | `rebuilds/` | tuason_2021_covid_coping_enjoy, mclaughlin_samuel_2025_auditory_session_2, amatus_cipora_2024_fsmas_se + 9 amatus_cipora_2024_* siblings | draft |
| 2026-09-30 | `batch1/` | 27 of 28: EEN_Lacey_2024_Parent; chile_2023 ×3; emoji_scheffler_2024; guatemala_2024_homes ×17; megart_tonkovic_2021; mhscdc_fried_2020_ema; smoking_perseverance_mcneish_2025; spalex_aguasvivas_2020; vollbracht_et_al_2026_ambulatory_assessment. Row counts verified by red_up. **selm_2019_climate_knowledge skipped**: red_up's gate blocked on dup_id_item (6 conflicting rows, #1856). validator_overrides.csv only records waivers; it doesn't grant them. | item_response_warehouse, _2 drafts |
| 2026-09-30 | `batch1/selm_2019_climate_knowledge.csv` | selm_2019_climate_knowledge, uploaded on its own with `--no-validate` (the only blocking finding was the 6 conflicting dup_id_item rows that stay with #1856) | item_response_warehouse_4 draft |
| 2026-09-30 | `itemtext_upload/` | bitew_2020_lte__items, bitew_2020_osss3__items, bitew_2020_phq9__items, bitew_2020_self_efficacy__items, amatus_cipora_2024_fsmas_se__items. 5/5 row-count verified. | item-text drafts |

## Withdrawal scripts run (Ben, 2026-09-30, APPLY=1)

| script | result |
|---|---|
| `withdraw_iesr_translated.py` | irw_text draft: beck_2021_iesr__items replaced (88 rows confirmed); ali_2021_iesr__items deleted |
| `withdraw_translated_rights.py` | irw_text draft: sun_2025_morality_study2_meaning__items deleted. irw_text_2 draft: jablonska_2020_swls__items deleted; gomez/powell/queiros QCAE replaced, 100 rows each confirmed |
| `retire_jiang_2024.py` | item_response_warehouse_3 draft: all 21 jiang_2024_* deleted. **Then ABORTED** before the item text: its "draft is missing published tables" check did not know about ali and sun, which were deleted earlier in the same draft. Fixed to accept pending ledger withdrawals and to skip targets already deleted. Re-run after the fix: 21 skipped as already removed; irw_text: jiang_2024_{ptsexp,ptsinv,ptspr}__items deleted; irw_text_2: jiang_2024_{growthm,instituinteg,ptsacc}__items deleted. All OK. |
| `retire_demos.py` | item_response_warehouse draft: DEMOS deleted |

| 2026-09-30 | `mechanical/` | 105/106 uploaded and row-count verified. **moral_absolutism_goyal_2025_nfc failed** (NotFound in the draft). Cause: a concurrent session withdrew all seven moral_absolutism_goyal_2025_* tables in the same item_response_warehouse_2 draft (#2563/#2564), so the audit's mechanical fixes for them are moot. Their staged files moved to `withdrawn_elsewhere/`, and their drafted table_changes rows removed. The goyal withdrawal's own re-run (`withdraw_goyal_2025`, resumable) must run AFTER all audit uploads to shard 2, in case `red_up` re-created any of them. | item_response_warehouse_2 draft |
| 2026-09-30 | goyal re-run (`withdraw_goyal_2025.py`, other session's script) | Deleted moral_absolutism_goyal_2025_pp and _stance from the item_response_warehouse_2 draft; the script confirmed all 7 removed. The audit has no more uploads for shard 2. | item_response_warehouse_2 draft |
| 2026-09-30 | `rights_recode/jablonska_2020_hads.csv` | jablonska_2020_hads (item codes recoded to hads_1..hads_14) | item_response_warehouse_3 draft |
| 2026-09-30 | `retire_foundationalassist.py` (APPLY=1) | foundationalassist_worden_2026 deleted; OK, 976 left | item_response_warehouse_4 draft |
| 2026-09-30 | `withdraw_iri_empathy.py` (APPLY=1) | alsecypiamh_wu_2022_empathy__items deleted; OK | irw_text draft |
