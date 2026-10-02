# robison_2026_retesting_flanker (slot 10, agent b)

**Current state.** Live in `item_response_warehouse_5` (v6_0). No item text. Not in withdrawals, table_changes, data_notes, or validate results. Script: `data/robison_2026_retesting.py`.

**Data (full read, 18,283 rows).** `metadata.csv` says 23,375. The difference is the practice/review-trial drop in 0a54f601 (#2525), which is live. metadata.csv is stale, and table_changes has no row for that rebuild. The row count is bookkeeping only; the missing table_changes row has not been investigated.
- 251 ids, 4 items (LLL/RRR congruent, LRL/RLR incongruent), resp 0/1, rt 0.07-22 s. Trial counts per id×wave vary from 7 to 165, which fits a time-limited ("Squared") task. `live_dup` excess is explained by `trial_number` (allbutresp = 0).
- **Placeholder ids.** `id` 0 (104 rows) and `id` 999 (60 rows) fall outside the 9001-9271 subject range, have no covariates, and restart `trial_number` inside one wave, so several runs are pooled under each. They look like test or unlinked accounts. Proposed: drop (164 rows). Medium confidence, so `needs_ruling`. The other robison_2026 cognitive tables probably have the same ids.
- **Repeated runs within a session.** 9062 (w2, 165 trials, trial_number to 95), 9092 (w1 and w2) and 9145 (w1) restart `trial_number` within one wave. No column separates the runs. Probably a source restart. Proposed `data_note`, medium.
- **`cov_age` = 100 for 6 respondents.** This is an undergraduate sample: the other ages run 17-34 with median 19. The value is inside [0,120], so `live_cov_range` would not catch it. It is almost certainly a sentinel or entry error. It comes from the shared demographics merge, so all robison_2026 tables carry it. Proposed `fix` (recode to NA), high. The precedent is the ieswriting mean-fill recode (4598a4f5).
- Other covariates: gpa 0.14-4.0, and the categoricals look sane.

**Rights.** No item text.

**Outcomes.** `needs_ruling` (ids 0/999); `data_note` (repeated runs); `fix` (cov_age 100, high).
