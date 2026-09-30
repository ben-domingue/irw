# spain_2015_immigration_assistance (slot 17, agent c)

**Current state.** Live in `item_response_warehouse_6`; item text live as `irw_text_3/spain_2015_immigration_assistance__items` (16 rows). Not in withdrawals, table_changes, data_notes or validator results.

**Data (live, full read, 9,036 rows).** Rows = metadata.csv. 2,424 ids, in line with siblings. 4 items (P101-P104), all 1-4 (1 Mucha ... 4 Ninguna); 8/9 recoded to NA and dropped per `data/spain_2015_immigration.do`. No dup id+item. cov_age 18-96, cov_sex labelled. Upload profile: conforms, passes (imputed_values warns on p101 "Poca" at 71%, a false alarm).

**Rights.** Register run on item_text, instructions and the `_translated` columns: no hits. CIS register row verdict `allow` (2026-09-22). The item text's resp-to-option mapping matches the .do file's coding. Aside, below the bar: `option_text_translated` is blank for "Ninguna" on all four items.

**Source caveat.** None stated.

**Outcome.** no_action (clean).
