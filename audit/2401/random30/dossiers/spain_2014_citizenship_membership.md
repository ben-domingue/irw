# spain_2014_citizenship_membership (slot 16, agent c)

**Current state.** Live in `item_response_warehouse_6`; no item text. Not in withdrawals, table_changes, data_notes or validator results.

**Data (live, full read, 8,720 rows).** Rows = metadata.csv. 1,753 ids, consistent with every sibling spain_2014_citizenship_* table (1,687-1,755). 5 items (P801-P805), all 1-4; the script recodes 8/9 (NS/NC) to NA and drops them. No dup id+item. cov_age 18-96 (99 recoded to NA), cov_sex labelled. Upload profile: conforms, passes; imputed_values warns that p801 has 4 = "never belonged" at 89%. That is a genuine response concentration, a false alarm.

**Source caveat.** `data/spain_2014_citizenship.do` calls 1-4 an "ordered involvement scale" (belongs and participates / belongs without participating / used to belong / never). Whether this is ordinal is arguable, but it is the source's own coding. No stated defect.

**Rights.** No item text; skipped (CIS is an `allow` register row regardless).

**Outcome.** no_action (clean).
