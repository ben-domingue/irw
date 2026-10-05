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
| 2026-10-05 | #2563 rebuild (`data/moral_absolutism_goyal_2025.py`, staged in `~/irw-stage/2563-goyal/out/`) | moral_absolutism_goyal_2025_{dt,mfq,pp,mr,stance} rebuilt plus new _nfc15, _nfc41, _mr_agree, _immorality (_nfc and _moral retired). Carries the audit's `rt` -> `cov_completion_time_s` rename. 9/9 row-count verified. | item_response_warehouse_2 draft |
| 2026-10-05 | #2506 wrong-now rebuilds, batch A (staged in `~/irw-stage/2506-rebuild-a/out/<dataset>/`) | PeSCBCSCe_Novak_2020_SPIRIT (#2836) -> item_response_warehouse draft; xue_2024_study3_cfa (#2837), lsbq_maleki_2025_dominant_language_home_community + lsbq_maleki_2025_non_persian_use (#2839), chen2022_sasc (#2841) -> item_response_warehouse_2 draft; yu_2015_bdi (#2840, new name for yu_2015_family_environment, which stays withdrawn) -> item_response_warehouse_3 draft. 6/6 row-count verified. | item_response_warehouse, _2, _3 drafts |
| 2026-10-05 | #2834 rebuild (`data/developmental_delay_anunciacao_2026.py`, staged in `~/irw-stage/2834-asqse/out/`) | development_delay_anunciacao_asqse and _concerns rebuilt after their withdrawal in the same draft: interval-specific item codes, padding dropped, personal data and free text removed. 2/2 row-count verified. | item_response_warehouse_2 draft |
| 2026-09-30 | `rights_recode/jablonska_2020_hads.csv` | jablonska_2020_hads (item codes recoded to hads_1..hads_14) | item_response_warehouse_3 draft |
| 2026-09-30 | `retire_foundationalassist.py` (APPLY=1) | foundationalassist_worden_2026 deleted; OK, 976 left | item_response_warehouse_4 draft |
| 2026-09-30 | `withdraw_iri_empathy.py` (APPLY=1) | alsecypiamh_wu_2022_empathy__items deleted; OK | irw_text draft |

## Released (Ben, 2026-09-30)

All drafts were published. The version manifest was refreshed by hand-triggering its workflow (#2575), and the audit's rows were recorded against these releases:

| shard | tag | first IRW version |
|---|---|---|
| irw_text | v29.0 | 475 |
| item_response_warehouse_4 | v11.0 | 476 |
| item_response_warehouse_3 | v11.0 | 477 |
| item_response_warehouse_6 | v5.0 | 478 |
| item_response_warehouse_2 | v29.0 | 479 |
| item_response_warehouse | v66.0 | 480 |
| irw_text_2 | v11.0 | 481 |

- `metadata/table_changes.csv`: 164 rows added, one per changed or retired response table, all dated 2026-09-30.
- `itemtext/withdrawals.csv`: `released` stamped on 37 #2401 rows. The two superseded first-pass rows (the `_translated`-only versions for jablonska_2020_swls__items and queiros_2018_qcae__items) are left blank, because they never ran as written.

**Staged after the release, not yet uploaded:** `~/irw-stage/2401-audit/held_released/`, 6 tables. They are the ones held for a pending draft:
- five narcissism_schneider_2025_study1_jauk_* tables (item_response_warehouse_2): `cov_alter` -99 set to NA;
- gcbs_brotherton_2013 (item_response_warehouse): `cov_familysize` 98 set to NA.

They were re-measured and repaired against the new release, and are verified. Their table_changes rows follow their own release.
