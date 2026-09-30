# wang_2024_emotion3 (slot 24, agent d)

**State.** Live in item_response_warehouse_3; no item text. Not in withdrawals / table_changes / data_notes / validator results.

**Data (full read, 5,840 rows).** Matches metadata.csv (5,840; 1,460 ids; 4 items). Upload profile: conforms, passes, nothing to report. VAR31-34 each take resp 1-5 using all 5 values; complete (1,460 per item); no dup id+item. cov_gender and cov_grade are both coded 1/2 without labels (cosmetic).

**Source caveat.** The script header (`data/wang_2024_achievement_emotions.py`) says the construct names aren't in the source file, so the subscales ship as emotion1-5. The generic table name already carries this, and it doesn't change an analysis.

**Outcome.** `no_action` (high).
