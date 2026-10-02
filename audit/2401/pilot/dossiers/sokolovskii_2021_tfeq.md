# sokolovskii_2021_tfeq (strand: data, with a rights cross-check)

**Lead** (round_log.md L18285, 2026-09-11 banked leads; and the TFEQ register row's notes, from batch_175 around L17261): "response table, `i_n` codes outside the TFEQ pattern". The register row TFEQ (block) has `match_item_code` `^TFEQ[0-9]+$`, and this table's codes are `i_1..i_51`.

## Independent checks

**Live** (`datapages.item_response_warehouse_4:980f:v10_0.sokolovskii_2021_tfeq:6e2s`, aggregate SQL only):
- 10,863 rows = 213 ids x 51 items, resp 1-5.
- Distinct codes are exactly `i_1..i_51`: opaque positional labels, not wording.

**Register** (`itemtext/instrument_rights_register.csv`, TFEQ row, verdict block, Pearson terms):
- `match_item_code ^TFEQ[0-9]+$`.
- The match_item_text strings are English TFEQ-R18 wordings (PhenX).
- The notes already record this lead: "LEAD, unchecked: sokolovskii_2021_tfeq ... codes are i_1..i_51, which this code pattern does NOT reach."

**Code surface:** I ran `irw_validate.rights.check_item_codes` on the live code set. It returns 0 findings for i_1..i_51. As a control, TFEQ1..TFEQ5 fire the TFEQ row. The code check exists to ask whether the codes ARE the wording (per its docstring, #2123/#2101). `i_n` are not, so the miss is correct.

**Live item text:**
- `itemtext/live_tables.csv` (as of 2026-09-28) has no `sokolovskii_2021_tfeq__items`.
- `itemtext/reaudit/triage_results.csv` already classifies it `RIGHTS_BLOCK` by instrument identity (TFEQ-51 Russian).
- It is not in the item-text queue.

## Verdict
Nothing to act on.
- The response table is not a rights problem: the rulings are about wording, and the codes carry no wording.
- No item text is live.
- Future item-text work is already stopped by the reaudit triage.

Widening the register's code pattern to catch `i_n` would be wrong, because `^i_[0-9]+$` would sweep hundreds of unrelated tables. The real gap is structural. The register has no table-name scoping column, and its text strings are English-only, so a Russian extraction would pass both automated surfaces. That is a register-schema question for the rules (see fragments/data_notes.md), not a row change for this table.

## proposed_outcome: `no_action`
Optional follow-on: update the TFEQ row's notes from "LEAD, unchecked" to "checked 2026-09-29 (irw#2401 pilot): codes opaque, no live item text, reaudit RIGHTS_BLOCK". That would be a note edit, not a pattern change. If Ben wants that edit, the outcome becomes `register`.

**Confidence:** high. **Group:** `rights:register-code-pattern-gap` (with the PROMIS and DIENER-NC pattern-gap leads).
**Minutes:** ~10. **redivis_reads:** aggregate (2 queries).
