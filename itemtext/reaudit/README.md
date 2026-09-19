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

## Pilot results (2026-09-19)

256 tables in 100 deposits, triaged by five agents. A hand spot-check of 10 verdicts against their
sources confirmed 9 and contradicted none; the tenth (a Mendeley deposit) could not be fetched.

| verdict | tables |
|---|---:|
| OBTAINABLE | 124 |
| RIGHTS_BLOCK | 44 |
| NOT_PUBLISHED | 37 |
| NEEDS_HUMAN | 25 |
| UNREACHABLE | 20 |
| NOT_ITEM_TEXT | 6 |

- **Yield.** Weighted back to the pool, about 1,360 of the 2,438 candidates are obtainable (90%
  bootstrap over deposits: 1,080-1,580). By stratum, the obtainable share is: never_assessed 0.67,
  old BLOCKED 0.53, old UNAVAILABLE 0.32, old UNAVAILABLE (copyrighted) 0.06. 104 of the 124
  obtainable tables are low effort.
- **The old audit was wrong on 64 of 130 tables it had judged, and 40 of those are OBTAINABLE.**
  Its dominant failure was stopping at the paper: it missed wording in data-file labels, column
  headers, codebooks and supplements, and it treated figshare/Dataverse web-page failures as dead
  ends when their APIs work. Its "copyrighted" calls mostly held on outcome, not on reasoning.
