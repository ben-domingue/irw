# martinez_2024_gonogo (slot 8, agent b)

**Current state.** Live in `item_response_warehouse_6` (v4_0). No item text. Not in withdrawals, table_changes, data_notes, or validate results. Script: `data/martinez_2024_capuchin.py`.

**Data (full read, 712 rows; matches metadata.csv).** 10 ids (capuchin monkeys), 8 items (`reward|noreward` x `t1-t4`), resp 0/1 only, rt 0.47-6.4 s, `date` is Unix seconds. `live_dup`: 633 excess id+item rows, all explained by `trial|date` (excess_occ = 0). This is a trial design, so that is fine.

**Sample under 100.** 10 ids. This was waived by Ben's ruling of 2026-09-16 (irw#2220), which the script header cites. Recorded, but no action.

**Source caveat.** The script drops the source's "2" code (no response) instead of scoring it 0, which the header documents: 88 trials in exp2. On the live table all four `reward_*` items have exactly 100 trials and the four `noreward_*` items have 68/78/72/94 = 312. So all 88 dropped non-responses are in the no-reward condition (inferred from the balanced 100-per-cell design). Omission is therefore informative: it makes accuracy in the no-reward condition look higher, and a reward vs no-reward comparison on `resp` is affected. The table can't express this, and the choice is documented only in a script comment. That fits #2529's bar ("something a user should know that the table can't express"), although the drop is an IRW processing choice and not a property of the source. Proposed `data_note`, medium.

**Rights.** No item text.

**Outcomes.** `no_action` (n = 10, already ruled in #2220); `data_note` (dropped non-responses concentrated in no-reward, medium).
