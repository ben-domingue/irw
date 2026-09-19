# Item-text re-audit (Y3 item 7)

The extraction queue (`extraction_batches/queue_state.csv`) was seeded once, from the 2026-08-17
availability audit, and was exhausted on 2026-09-19. This directory works out what is left to get.

**Candidates are built from the live corpus, not from the old audit**, which is known to be
unreliable (it has named the wrong instrument and applied a retired rights test).

- `candidates.csv`: every table in `metadata/metadata.csv` that has no live item text
  (`live_tables.csv`, case-insensitive) and no row in the queue. 2,438 tables on 2026-09-19.
  - `stratum`: the old audit's verdict for the table, or `never_assessed` if it had none.
  - `deposit`: the unit of work. It is the normalised data DOI, else the paper DOI, else the data
    URL, from `metadata/biblio.csv`, which gives 827 deposits. Tables sharing a deposit share a
    source, and usually a verdict.
- `pilot_sample.csv`: 100 deposits for the triage pilot, stratified and seeded (20260919): 45
  never_assessed, 25 UNAVAILABLE, 15 UNAVAILABLE (copyrighted), 15 BLOCKED. The rejected strata
  are over-sampled on purpose, to measure the old audit's error rate; weight back to the
  population when reporting yield.
- `pilot_results.csv` (when written): one row per table, with a triage verdict (OBTAINABLE /
  NOT_PUBLISHED / RIGHTS_BLOCK / NOT_ITEM_TEXT / UNREACHABLE / NEEDS_HUMAN), the source, the
  rights basis, and whether the old audit agreed.

The candidate list is a snapshot: rebuild it before queuing anything, and check every table
against `live_tables.csv` first (see irw#2230 for what re-extracting a live table costs).
