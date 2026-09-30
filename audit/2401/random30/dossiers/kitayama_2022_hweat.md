# kitayama_2022_hweat (slot 28, agent e)

**State.** Live in `item_response_warehouse_4` (3,636 rows = metadata.csv). Item text live (`irw_text_2`, 90 rows, Japanese + `_translated`). Not in withdrawals, table_changes, data_notes or validator results.

**Data (full live read; upload profile: conforms, passes).** 202 ids x 18 items, all 1-5; Q10 uses only 1-4 (`item_scale_outlier` warn): category non-use on a 202-person sample, not a different scale. No dups, no covariates. This is the S2 main validation sample (N=202); the S1 test-retest sample is handled separately per the script.

**Rights.** Register on `item_text` and `item_text_translated`: no hits. HWE-AT is AACN's; its tool page (https://www.aacn.org/nursing-excellence/healthy-work-environments/aacn-healthy-work-environment-assessment-tool, fetched 2026-09-29) carries only a generic "All rights reserved" footer and states no licence fee, NC or no-redistribution clause. Per RULES.md, that is no stated restriction. Japanese wording comes from the CC BY 4.0 PLOS ONE paper (Kitayama & Sakuramoto 2022).

**Source caveat.** `data/kitayama_2022_hweat.py` header: nothing stated.

**Outcome.** Clean: no_action (high on data, medium on rights, since AACN's generic copyright line could be read either way).
