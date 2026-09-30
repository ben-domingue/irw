# spain_2026_love_association (slot 19, agent d)

**State.** Live in item_response_warehouse_4 (ref `...:v6_0.spain_2026_love_association`); item text live in `irw_text` (`__items`, 36 rows). Not in withdrawals.csv, table_changes.csv, data_notes.csv, or the dup_id_item / cov_age result files.

**Data (full read, 44,670 rows).** Row count equals metadata.csv (44,670; 5,006 ids; 9 items). Upload profile: conforms, gate passes; only an `imputed_values` concentration warning (below bar). No dup id+item, no NA resp. Every item uses resp {1,2,4,5}: the script (`data/spain_2026_love.do` l.96-123) sets CIS codes 8/9 (NS/NC) to NA and drops code 3 (the unread spontaneous middle category), which is the documented convention across the spain_* CIS family (e.g. spain_2024_values.do, spain_2026_prostitution.do). Item text maps 1=Mucho, 2=Bastante, 4=Poco, 5=Nada, so the gap is labelled and consistent. cov_age 18-98, cov_sex Hombre/Mujer: plausible.

**Rights.** Register CIS row (verdict `allow`, 2026-09-22) governs all spain_* item text. `check_item_text` run with the register passed explicitly against item_text, *_translated, instructions, section_prompt and option_text columns: no hit.

**Source caveat.** None stated in the script header.

**Outcome.** `no_action` (high).
