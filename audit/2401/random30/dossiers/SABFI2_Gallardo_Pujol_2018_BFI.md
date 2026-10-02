# SABFI2_Gallardo_Pujol_2018_BFI (slot 4, agent a)

**Current state.** Live in `item_response_warehouse` (v65_0), 85,140 rows = 1,419 x 60, matching metadata. No item text. Not in any ledger. The 09-02 legacy sweep gave only warnings (`imputed_values*` on BFI19, name_charset).

**Data (full read).** All 60 BFI-2 items are 1-5, with no NA and no dup id+item. BFI43 and BFI52 never use 1 (non-use). `group` (1 = Study 1, 1,000 ids; 3 = Study 3, 419 ids) matches the id prefixes `study1_`/`study3_`, so there are no id collisions. BFI19's 61% at resp 4 is an ordinary modal agree and appears in both studies, so the `imputed_values` warning is a false alarm. The upload profile warns only on the `group` prefix, name case, and a rights code match.

**Rights.** The item codes `BFI1..BFI60` match the BFI-2 and BFI-44 block rows *as codes*, but they're opaque numbers and not wording, and no item text is live. Nothing is shipped that the rulings cover.

**Source caveat.** `data/SABFI2_Gallardo_Pujol_2018.R` pools Studies 1 and 3 of the same Spanish BFI-2 under `group`, which is the right thing under "collapse same-instrument samples". Study 1 is truncated to its first 1,000 rows following the paper's own exclusion, and the script comment says so. Nothing meets #2529's test.

**Outcome.** Clean, `no_action` (high).
