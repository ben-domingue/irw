# guatemala_2024_homes_energy (slot 2, agent a)

**Current state.** Live in `item_response_warehouse_2` (v26_0). It has 41,316 rows (6,886 ids x 6 items), and 38,474 of them have non-NA resp, which is the `metadata.csv` figure (metadata counts non-missing), so the counts agree. Item text live in `irw_text_3` (24 rows, Spanish with English `_translated`). Not in withdrawals, table_changes, data_notes, validator_overrides or the irw_validate results.

**Data (full read).** No dup id+item. The skip pattern is coherent: the 525 households not connected to the grid (`e_p04a08`=2) are NA on every follow-up. `cov_age` 16-97, `cov_hhsize` 1-22. `cov_lang` carries a 98 code for 14 households, probably "other"/NS and not checked (below the bar). Upload profile: conforms, passes, with only warnings.

**Finding: "Don't know" is coded as the top category.** The live item text maps options for `e_p04a08a1..a4` as `SÍ`=1, `NO`=2, `NS` (No sabe / Don't know)=3. Live counts of resp=3: a1 28, a2 93, a3 61, a4 69, so 251 responses. So a non-response is shipped as a scale step above "No". `datastandard.md` (Step 6, "A sentinel can hide inside the valid range") requires these to be removed. Script `data/guatemala_2024_homes.do` only sets 98 to missing, and for `e_p04a08b` (the 1-10 satisfaction item) that turned 217 values into NA. So the missing-code handling is inconsistent between items in the same file. Fix: set resp=3 to NA on the `a*` items. Confidence is high on the meaning (the option text is live). The same `.do` pattern (98 only) builds all 17 `guatemala_2024_homes_*` tables, so the siblings probably carry NS=3 too. **That is unverified**, and the group key covers them.

Side note, not investigated: the `.do` does `gen resp2 = resp; drop resp; replace resp = ...`, which only runs through Stata's abbreviation of `resp2`, and would export a `resp2` column. Live has `resp`, so the script as committed may not reproduce the live file (possible `script_drift`).

**Rights.** INE Guatemala government survey (ENCASBA 2024). No register hits on `item_text` or `item_text_translated`.

**Outcomes.** `fix` (high). `script_drift` (low, recorded without investigating).
