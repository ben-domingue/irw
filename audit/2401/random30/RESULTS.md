# Random-30 base rate, 2026-09-29

This is a random draw of 30 of the 4,596 live tables (seed 2401). The checks were current state, live data, rights, and the script header. The full results are in `worklist.csv` (41 finding rows) and `dossiers/`.

## Rate

| | tables | share | 95% CI (approx.) |
|---|---|---|---|
| Clean (no finding at all) | 16 | 53% | |
| **Wrong values in `resp` or item text** (changes an item-level analysis) | 5 | **17%** | 6–35% |
| Wrong covariate values only | 3 | 10% | |
| Only a data note or a ruling | 6 | 20% | |

The five with wrong `resp` or item text:
- `guatemala_2024_homes_energy`: "don't know" is shipped as resp=3.
- `mclaughlin_samuel_2025_auditory_session_2`: every trial is doubled as its complement, and ratings are mixed in with the items.
- `SV-MAIA2_Randelovic_2021_MAIA`: 5,846 rows with the literal string "NA".
- `lee_2020_empathy`: 10 negatively worded items are unreversed, and the script header says they were reversed.
- `amatus_cipora_2024_fsmas_se`: the option text is inverted on the 4 reverse-keyed items.

The three with wrong covariates only:
- `pauli_2021_ppos_d6`: birth year holds −99, 200 and 1756.
- `robison_2026_retesting_flanker`: age is 100 for undergraduates, and there are placeholder ids.
- `sned_bendall_2024`: whole-study completion time is shipped as `rt`.

Scaled up, that is roughly **17% × 4,596 ≈ 800 tables with resp-level errors**, and about 1,250 including covariates. The interval is wide at n = 30. Findings also cluster by source family: guatemala has 16 siblings, avci 27, robison and pauli several each. So the number of *distinct fixes* is well below the number of tables.

## Why the audit can't be handled table by table

At this rate, table-level handling is out of the question: Ben's concern holds. But nearly every finding falls into a **class a script can detect**, and most of those classes also have a mechanical fix:

| class | seen in | detector | fix |
|---|---|---|---|
| literal "NA" / string sentinel in `resp` | SV-MAIA2 | `resp` not numeric after cast. The 09-09 sweep filed this table as scattered missingness, so the detector needs tightening | mechanical |
| out-of-range code on a bounded item (e.g. 3 on a yes/no) | guatemala | item's distinct-value count exceeds its sibling items', or exceeds the item text's option count | mechanical, per family |
| sentinel or impossible covariate (−99, 999, age 100 in students, birth year 200) | pauli, robison, avilesgonzalez | extend `live_cov_range` to all `cov_*` | rule: undefined code → NA |
| `rt` constant within id | sned | a one-line aggregate | rename to `cov_completion_time_s` |
| duplicated trials | mclaughlin | `live_dup` (already exists) | rebuild |
| a block of items anti-correlated with the rest | lee | an item–rest correlation < 0 on a whole block | data note, or reverse after a ruling |
| option text reversed against the data | amatus | item–rest correlation sign vs the option order in item text | fix the item text |

## Recommendation

Turn the audit from "review tables" into **"run detectors, fix classes"**:

1. **Build the six detectors** above as aggregate queries in `irw_validate/live_*`, then run them over all 4,596 tables. Aggregate queries fall outside the export cap.
2. **The output is a count per class, not a list of tables.** Ben rules once per class: for example, "undefined covariate codes → NA, no review".
3. **Mechanical classes are fixed in family batches** and logged in `table_changes.csv`. Ben sees batch totals only.
4. **Non-mechanical findings get a `known_issues` flag** (banner plus noindex) instead of a fix, until someone chooses to work them. Nothing waits on Ben.
5. **Data notes are opportunistic:** write them when a table is touched anyway, and never go looking for them.
6. **Rights and the `_translated` columns stay a separate strand.** The random draw found no rights problems in 17 item-text tables. That is consistent with a low rate, but at n = 17 it can't rule out a few percent.

Cost of this pass: 30 tables in about 6 minutes of wall time with 5 agents, about 340 agent-minutes in all (about 11 minutes per table). The detector approach replaces nearly all of that per-table cost.
