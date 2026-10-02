# pauli_2021_ppos_d6 (slot 22, agent d)

**State.** Live in item_response_warehouse_4; no item text. Not in withdrawals / table_changes / data_notes / validator results.

**Data (full read, 1,973 rows).** Matches metadata.csv (1,973; 332 ids; 6 items). Upload profile: conforms, passes. Warnings: `resp_scale_nested_support` (ppos4 has no 5s; 0-5 agreement scale per the script header, so this is category non-use, below bar) and `rights_register` on the codes `ppos1-6` (PPOS row, verdict block). The codes are generic numbering, not wording, and the table ships no item text, so the rights check does not apply to this table. No dup id+item. The script drops the -99 sentinel from resp.

**Finding (covariate, fix, high).** `cov_birth_year` keeps the source's **-99 missing sentinel** (3 ids), plus two impossible values, **200** and **1756** (1 id each). `data/pauli_2021_ppos_d6.py` `build_long` passes `raw["v5"]` through unfiltered, even though the header itself documents -99 as the sentinel. The fix is to set -99 to NA, and 200/1756 too since they are impossible. The same code builds the sibling `pauli_2021_coercion_attitudes`, so it almost certainly has the same defect (not checked: outside my slots).

**Source caveat.** None beyond the sentinel.

**Outcome.** One `fix` (high); group `sentinel_in_cov`.
