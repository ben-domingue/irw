# dpt_noncog__psychological_flexibility (slot 11, agent b)

**Current state.** Live in `item_response_warehouse_2` (v26_0). Redivis normalises the name to `dpt_noncog_psychological_flexibility`. No item text. Not in withdrawals, table_changes, data_notes, or validate results. Script: `data/dpt_noncognitive_traits.py` (CC0, Harvard Dataverse 10.7910/DVN/Y75CP2).

**Data (full read, 2,682 rows = 298 × 9; matches metadata.csv).** `live_dup`: 0 excess. resp is 1-6 on every item (the PFQ is 1-6 per the header). Four items never use 1, which is ordinary floor sparsity, not a different scale. No sentinels, no NULLs. All 36 inter-item correlations are positive (.12-.51), so no reverse-keying surprises. No `cov_*`. N = 298.

**Source caveat.** The header states nothing.

**Outcome.** `no_action` (clean).
