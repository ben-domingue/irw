# enem_2021_1mil_cn (slot 9, agent b)

**Current state.** Live in `item_response_warehouse` (v65_0). It has item text, which was skipped per the brief (enem, collaborator-owned). The legacy sweep entry is `size_skipped` (info only). It is not itself in table_changes: #1942 annulled-item removal covered 2021 `_mt`, and the #955 realignment covered `_lc`.

**Data (aggregate SQL only; 44,991,368 rows).** `live_dup`: 0 excess id+item. 999,846 ids, 45 items, resp {0,1} with no NULL, `resp_raw` ∈ {A-E, `.`, `*`}, and `.`/`*` are always scored 0. Six booklets: 909-912 (~250k ids each, 45 items), and the adapted booklets 916 (143 ids, 36 items) and 917 (415 ids, 44 items). Every booklet×position maps to one item. Item p ranges 0.11-0.68, so no all-zero (annulled) item survives. Per-person item counts are 36/44/45 and match the booklets. No `cov_*`.

**Bookkeeping, not a finding.** `metadata.csv` is stale: 45,000,000 rows, 1,000,000 ids and 99 items, against 44,991,368 / 999,846 / 45 live. That clears on the next pipeline run.

**Source caveat.** `data/enem_2021.R`: absentees are filtered on INEP's presence flag and annulled items are dropped. Nothing meets #2529 beyond what `table_changes` already carries.

**Outcome.** `no_action` (clean).
