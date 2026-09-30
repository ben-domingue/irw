# enem_2020_1mil_mt (slot 12, agent b)

**Current state.** Live in `item_response_warehouse` (v65_0). It has item text, which was skipped per the brief. `table_changes`: v367 (2026-09-10, #1942) removed items INEP annulled and added `resp_raw`, and the live table has both. The legacy sweep entry is `size_skipped` (info).

**Data (aggregate SQL only; 43,947,884 rows).** `live_dup`: 0 excess. 998,883 ids, 44 items (45 minus the annulled one), resp {0,1} with no NULL, `resp_raw` ∈ {A-E, `.`, `*`}, and `.`/`*` are scored 0. Booklets 587-590 (~250k each, 44 items), and adapted 594 (141 ids, 36 items) and 595 (460 ids, 40 items). One item per booklet×position. Item p ranges 0.14-0.65, with no all-zero item. No `cov_*`.

**Bookkeeping, not a finding.** `metadata.csv` still shows the pre-#1942 shape (45M rows, 1M ids, 144 items).

**Outcome.** `no_action` (clean; the #1942 fix is confirmed live).
