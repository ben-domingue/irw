# spain_2026_international_influence (slot 29, agent e)

**State.** Live in `item_response_warehouse_3` (58,108 rows = metadata.csv). Item text live (`irw_text_3`, 100 rows, Spanish + `_translated`). Not in withdrawals, table_changes, data_notes or validator results.

**Data (full live read; upload profile: conforms, passes, nothing to report).** 5,989 ids x 10 items, resp 1-10 on every item (anchors 1 "Ninguna influencia" to 10 "Máxima influencia" in the option text); the CIS 98/99 sentinels are recoded to missing in `data/spain_2026_international.do` and none survive. No dups. `cov_age` 18-95 (>=99 set missing), `cov_sex` Hombre/Mujer.

**Rights.** Register on `item_text` and `item_text_translated`: no hits. Items are names of international institutions from CIS study 3564; nothing restricted.

**Source caveat.** Script: nothing stated.

**Outcome.** Clean: no_action (high).
