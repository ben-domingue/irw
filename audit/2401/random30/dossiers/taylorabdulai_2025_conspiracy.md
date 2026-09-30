# taylorabdulai_2025_conspiracy (slot 18, agent c)

**Current state.** Live in `item_response_warehouse_4`; no item text. Not in withdrawals, table_changes, data_notes or validator results.

**Data (live, full read, 666 rows).** Rows = metadata.csv. 253 ids of the source's 377 (the sibling tables have 377). 4 binary items, 0/1. No dup id+item. cov_age 17-69, categoricals labelled. Upload profile: conforms, passes. The script uses the row index as id, which is expected: the source has no id column.

**Reproduces.** Re-read the PLOS S1 File (377 x 58). The Yes+No counts per item (150/190/163/163) equal the live per-item counts exactly.

**Possible note (borderline).** The script drops "Not sure" as non-response, which datastandard.md requires. But "Not sure" is the *modal* answer on every item: 187-227 of 377, or 50-60%. It removes 124 people completely, and the table keeps 44% of possible responses. Anyone reading prevalence or item difficulty off this table is reading it among the decided only, and the table cannot show that. This is an IRW processing choice made under the standard, not a source defect, so it is at the edge of #2529's test. Proposed as a data_note, low confidence.

**Rights.** No item text; skipped.

**Outcome.** data_note (low confidence; borderline on #2529's scope).
