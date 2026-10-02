# sned_bendall_2024 (slot 25, agent e)

**State.** Live in `item_response_warehouse` (4,806 rows = metadata.csv). Item text live (`irw_text_2`, 60 rows). Not in withdrawals, table_changes, data_notes; only a `column_order` warn in the 2026-09-02 legacy sweep.

**Data (full live read, 4,806 rows; upload profile: conforms, passes).** 801 ids x 6 items, no dup id+item. RU* items 1-10, MacArthur 1-9 observed (ladder, 10-point). cov_age 18-79. `cov_ethnicity` has one person as `DATA_EXPIRED` and `cov_gender` one as `__other` (Prolific export tokens; below the bar).

**Finding 1 - `rt` is whole-study completion time (fix, high).** `data/sned_bendall_2024.R` renames Prolific's `Time.taken` to `rt`. Live: `rt` is constant within every one of the 801 ids (1 distinct value per id), median 3,789 s (63 min), max 177,642 s. The validator's `rt_units*` warns. IRW's `rt` is per-item response time; whole-survey time belongs in a covariate such as `cov_completion_time_s`. Anyone fitting an RT-aware model reads 63 minutes per item. Fix: rename the column.

**Finding 2 - the table bundles three different constructs (data_note, medium).** Item text shows RULiving/RULocation/RUMostTime are rural-urban placement (1=isolated countryside, 10=city centre), RULeisureRural and RULeisureUrban are liking ratings for leisure in each environment (opposite directions), and MacArthur is the subjective-SES ladder (Adler 2000). Not one scale. Splitting would leave single-item tables, so a note (like `depression_anxiety_stress`) fits #2529 better than a split.

**Rights.** Register run on item text: no hits. MacArthur ladder and Cox et al. rurality items: no register row, no stated restriction found. No `_translated` columns (English study).

**Source caveat.** Script header has no stated defect beyond the above.
