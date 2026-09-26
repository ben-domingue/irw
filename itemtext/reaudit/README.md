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

## Full triage (2026-09-19 on, irw#2255)

- `TRIAGE_BRIEF.md`: the brief every triage agent follows. It is the pilot brief plus a required
  upstream-originator rights check, a generic User-Agent rule, the WPAI naming ruling, and fetch
  workarounds learned in wave 1.
- `triage_scope.csv`: the 678 deposits (2,056 tables; `zhou_2025_peer_relationship` appears twice because `candidates.csv` lists it twice) in scope. These are the candidates whose own
  stratum is never_assessed, BLOCKED, UNAVAILABLE or AVAILABLE, outside the 100 pilot deposits,
  minus anything live or queued at build time. (#2255's "649" subtracted the 15 pilot copyright
  deposits twice.) Deposits are shuffled (seed 20260920) into waves of 100 and slices of 20.
- `triage_results.csv`: one row per table, appended wave by wave, in the pilot's columns plus
  `rights_sha256`, `wave` and `slice`. About 10 verdicts per wave are hand-checked against sources.
  Wave 1 checked 10: 9 were confirmed directly, 1 by its register row only, and none were
  contradicted.
- `register_rows_draft.csv`: draft rows for `instrument_rights_register.csv`, for a human to add.
  Rounds and triage never write `ship`.
- `triage_results.csv` column `retry`: rows to redo before anything is queued. `quota` means a Zenodo rate
  limit or an exhausted search budget blocked the check. `skipped_check` is a NOT_PUBLISHED whose evidence
  admits a check was not run. `spotcheck_wrong` means the hand check contradicted the verdict. Wave 4 ran
  into this machine's search and OpenAlex quotas partway through: 12 of its NOT_PUBLISHED rows skipped a
  check, against 1-3 in each earlier wave. Its spot-check found 2 false negatives, which trips the stop
  rule, so the brief was tightened before wave 5.
- **Redo pass (2026-09-25, irw#2382 step 1).** All 37 `retry` rows were re-triaged with the same brief and replaced in place;
  `retry` is now empty and `redo_note` records the old verdict, the retry reason and whether the skipped check could run.
  Outcome: 7 OBTAINABLE, 19 NEEDS_HUMAN (12 of them PsycTESTS holds), 3 RIGHTS_BLOCK, 4 NOT_PUBLISHED, 4 UNREACHABLE.
  Zenodo still 403s this machine, but WebFetch on `https://zenodo.org/api/records/<id>/files/<key>/content` saves the
  binary, so `ZENODO_RATELIMIT` rows are recoverable that way.
- **Rebuild (2026-09-25, irw#2382 step 3).** `candidates.csv` is rebuilt from the live corpus. The table list is read
  from the six core shards on Redivis via `red_up` (4,515 tables; `list_tables()` matched each shard's `tableCount`).
  Live item text comes from a fresh `live_tables.csv` (1,954 across `irw_text`, `_2`, `_3`), and queue rows from
  `queue_state.csv`. That leaves 2,192 candidates in 727 deposits:
  - 1,916 kept from the 09-19 list;
  - 276 new, with stratum `new_since_0919`;
  - 522 old rows dropped: 442 are now live, 490 are queued, 48 are gone from the core shards (the groups overlap).

  Deposit keys use the 09-19 rule. Ten new families added after the 2026-09-21 metadata run had no biblio row yet;
  their refs come from their processing script's header (`Reference_x` says so). 41 old `table:` fallback keys were
  re-keyed from the current biblio. For example, the robison_2026_retesting family was 25 one-table "deposits" and is
  now one.
  `triage_scope.csv`: 7 wave 5-7 tables that are no longer candidates were dropped. The new tables are wave 8. A deposit
  that spans waves sits in its earliest unclassified wave. **Unclassified now: 1,117 tables in 321 deposits** (waves 5-8).
- **Classification (2026-09-25, irw#2382 step 4).** Waves 5-8 cover 1,110 tables in 319 deposits; PISA and NEEDS_HUMAN
  re-runs were held back. Each wave used the brief plus its 09-25 addendum, and about 11 verdicts per wave were
  spot-checked: 11/11, 11/12, 10/11 and 11/12. Each miss was corrected in place, and none tripped the stop rule.
  Leads (table defects, personal data, questions) are in `leads_step4.md`. Seven tables found serving wrong data were
  withdrawn under Ben's standing rule (#2432-#2436).
- **Routing (2026-09-25, step 5).**
  - OBTAINABLE: 498 tables become queue slices 08-18 in `oneoff/itemtext-rights-bank/` (`slices_2382.csv`; 16 CC BY-SA
    rows need licence notices after upload). They are not yet queued.
  - 4 INFERRED tables are held for verification (`inferred_hold_2382.csv`).
  - NOT_PUBLISHED and NOT_ITEM_TEXT: 410 `excluded` rows in `queue_state.csv`.
  - RIGHTS_BLOCK with a quoted clause: `register_rows_draft_2382.csv`, 130 instrument rows covering 213 tables, for Ben
    to ratify.
