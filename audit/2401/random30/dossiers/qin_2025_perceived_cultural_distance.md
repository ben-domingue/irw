# qin_2025_perceived_cultural_distance (slot 27, agent e)

**State.** Live in `item_response_warehouse_2` (1,641 rows = metadata.csv). Item text live (`irw_text_2`, 18 rows). Not in withdrawals, table_changes, data_notes or validator results.

**Data (full live read; upload profile: conforms, passes, nothing to report).** 547 ids x 3 items (PCD1-3), all 1-6, 6 values used on each item, no dups, no covariates.

**Rights.** Register on item text: no hits; no `_translated` columns. Wording is from the CC BY 4.0 PLOS ONE paper (script header). `language=Chinese` with English base text and no `_translated` is the documented `translated_substitute` fallback when the administered Chinese wording isn't published, so not a claim problem.

**Source caveat.** `data/qin_2025_cultural_tourism.py`: CC BY 4.0 figshare deposit, filters to 1-6, nothing stated.

**Outcome.** Clean: no_action (high).
