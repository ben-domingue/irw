# Legacy sweep, 2026-09-02 — and why its findings are a candidate list

`legacy_sweep_2026-09-02.csv` is the first run of `irw-validate` over the 922
`.Rdata` tables in `../data/pub/` (#1703 sub-item 1.5). No checker had ever
touched them.

```
nice -n 19 python3 -m irw_validate.sweep_legacy ../data/pub \
    -o irw_validate/results/legacy_sweep_2026-09-02.csv --resume --max-mb 8
```

852 tables opened, 70 deferred by the 8 MB cap, 28 with nothing to report.

## Read this before acting on the findings

**`data/pub/` is not a faithful mirror of what is published.** Comparing each
archive file's row count against `metadata/metadata.csv`:

| | tables |
|---|---|
| archive matches published exactly | 603 |
| differs by under 1% | 125 |
| archive holds 50–99% of published | 65 |
| archive holds under 50% | 3 |
| **archive is empty, published is not** | **16** |
| archive holds *more* than published | 2 |

The under-1% group is most likely an artefact of the comparison rather than
drift — this sweep counts rows with a non-null `resp`, and `metadata.csv` may
not. The other 86 are real divergence.

**The 16 empty ones are every PISA cycle from 2000 to 2012** — `pisa2000_math`
through `pisa2012_science`. Each is a 4 KB file holding the right columns and
**zero rows**, while the published tables hold between 1.5M and 22.6M responses.
The newer cycles (2015, 2018, 2022) are the real 130–196 MB files. So the local
archive lost the older PISA data at some point, and nothing noticed because
nothing reads these files.

**56 of the 131 tables with an error have an archive copy that differs from what
is published.** So more than a third of the errors below may be defects in a
stale local file rather than in the corpus. Confirm against live data before
treating any single finding as a corpus defect.

## What it found, in the 852 opened

Errors:

| check | tables | |
|---|---|---|
| `dup_id_item` | 101 | the same person answering the same item twice, with no `wave`/`timepoint`/`date` to distinguish them |
| `name_length` | 19 | over the 40-character cap — `threatperceptions_isler_2024_*` accounts for 11 |
| `id_na` / `item_na` / `resp_na` | 16 | the empty PISA files above |
| `resp_variation*` | 16 | the same 16 |

Warnings worth a look: `imputed_values*` (557), `column_order` (444),
`name_charset` (254 — the known non-lowercase names), `cov_range` (24, the
#1779 class), `sample_floor` (52 under 100 respondents).

## One correction this sweep forced

`resp_numeric` as inherited from `run_qc` measures how many values parse as
numbers over **all** rows, so NaN counts as "does not parse". A float column
with missing values therefore failed it — and `resp_na` already reports
missingness. That produced 86 false errors here, including
`BAFACALO_Golino_2013_CIS`, whose `resp` is 39% null and **100% numeric over the
values that are present**.

The gate profiles (`upload`, `legacy`) now re-judge it over non-null values.
`triage` keeps the inherited behaviour, because fifty scripts in `data/` depend
on it.

## What should happen next

The useful version of 1.5 points at **live data**, not this directory. The
tooling is the same; only the loader changes. This run's value is the candidate
list and the fidelity measurement above — not a verdict on the corpus.

---

# `dup_id_item` verdicts, 2026-09-02

`dup_id_item_verdicts_2026-09-02.csv` carries a verdict for **all 101** tables the
sweep flagged, keyed by the name the sweep used, with `live_table` giving the name
the data lives under now.

## Method: live data, not `data/pub`

The triage above could only speak for the 57 tables whose archive copy matches
`metadata.csv`. `data/pub` is a stale archive (Ben, 2026-09-02), so this pass ignores
it and measures the **live corpus** instead — with **server-side queries, never
`irw_fetch`**. Exports are capped at 200GB/30 days against a 181.8GB corpus
(#1736, `itemtext/.../table_sets.R`); aggregate queries are not capped. One query per
table computes, in a single pass:

| measure | what it answers |
|---|---|
| `excess_pair` | rows beyond the first in each `id`+`item` group — the flag itself |
| `excess_exact` | of those, how many are byte-identical to a row already present |
| `excess_after_all_columns` | what survives grouping by **every** column but `resp` |
| `n_conflicting_pairs` | `id`+`item` groups holding more than one distinct `resp` |
| `excess_occ` | what survives once the occasion columns from #1835 are consulted |

96 of the 101 names resolved live. Of the 5 that did not, **4 are renames**, each
confirmed by an exact match on rows/ids/items against the archive copy:

| flagged as | lives as |
|---|---|
| `Veterans.Affairs.SSVF.Survey.2016-17` | `Veterans_Affairs_SSVF_Survey_2016-17` |
| `Aspirations_Sonmez_2023` | `Aspirations_Sonmez_2022` |
| `Mechanical_Turk_Lexical` | `mturkddm_lexical` |
| `Mechanical_Turk_Recognition` | `mturkddm_recognition` |

`AAQ-II` has no successor — nothing in the corpus matches its 10,521 rows / 1,497 ids
/ 7 items. It is retired, and the finding dies with it.

## The verdicts

| verdict | tables | what to do |
|---|---|---|
| `document_column` | 28 | nothing to the data — an occasion column already explains the repeat |
| `id_collision` | 27 | the same `id` means **different people**; namespace `id`, do not dedupe |
| `dedupe` | 18 | every excess row is byte-identical; drop duplicates |
| `mixed_dedupe_then_source` | 12 | part exact duplicates, part genuine conflicts |
| `restore_trial_index` | 10 | trial-level data whose trial index was never carried through |
| `restore_wave` | 4 | the source **has** an occasion column and the script dropped it |
| `retired` | 1 | `AAQ-II` |
| `conflicting_needs_source` | 1 | `realpic_souza2021` — 28 conflicts, nothing explains them |

### `id_collision` is the big finding, and it is not a repeated measure

27 tables — the largest single class — are not repeated measures at all. Independent
samples were numbered from 1 and then stacked, so **id 1 in one sample and id 1 in
another are different people**. The processing scripts say so outright:

- `PEMAIW_Qiu_2020.R` — `mutate(id = row_number())` on each of two recruitment files,
  then `rbind` with a `group` label. Seven tables.
- `EWAS_Sanford_2024.R` — `df$id <- seq(1, nrow(df))` on each of two studies.
  Study 1 numbers 236 people 1–236, study 2 numbers 482 people 1–482; all 236 collide.
- `AOMT_..._Geiger_2021` — Bulgaria (248 ids) and North America (259 ids) share a
  namespace: 286 distinct ids where 507 people were measured. Three tables.
- `OS_TBMWTFS_Schubert_2023_*` — English (215) and German (176), 176 colliding. Four tables.

Deduping any of these **destroys real responses**. The fix is to make `id` unique.

`pass20_klosowska_2025_*` proves the class from the data alone: three ids in each
table carry two different ages, two different sexes *and* two different incomes.

This vindicates #1835's refusal to let `group`/`study`/`treatment` count as resolving.
Had they been folded into "resolved", 27 tables of corrupted person identifiers would
have been marked clean.

### Four tables lost a column the source actually has

- **`pact_project`** — `data/pact_project.R:361` rbinds four cohort-year waves under
  the comment `# COMBINE WAVES` and never carries a wave identifier out. `treat` does
  not rescue it: 581,824 of 1,018,383 rows have `treat` NULL.
- **`ravens_deboeck2012`** — `data/IRTrees.R:17` does `fsdatT %>% select(-node, -sub)`.
  `fsdatT` is De Boeck & Partchev (2012) IRTrees data, where each response is
  decomposed into tree **nodes**, so one row per node is the design. The table is
  exactly 2× its pair count (11,622 = 2 × 5,811). `stress_deboeck2012` is the same script.
- **`KTEEM_Schoen_2019-2022`** — renames `DataCollectionWave` to `group`. It *is* a
  wave (Spring19–Spring22, `PublicID` persists, 832 of 1,130 ids recur). Rename it
  and mark the table longitudinal; no data change.

### `florida_twins_behavior_*` — dedupe, but regenerate

Six of the seven are the largest `dedupe` cases, and they are worse than duplicates.
`data/florida_twins_behavior.R` builds `df0` from `bg_id0`/`ends_with("0")` and `df1`
from `bg_id1`/`ends_with("1")`, `bind_rows` them, then strips the trailing twin suffix
from `item`. Every `id`+`item` pair then occurs exactly twice with an **identical**
`resp` and zero conflicts — density 1.99 in `metadata.csv`, against 1.24 for the
separately-processed `florida_twins_cads`. Twins cannot agree on 100% of items, so
this is one twin's data emitted twice and the other twin's data probably absent.
Dedupe restores the shape; only regenerating from source restores the sample.

### `rt` is not an identifier

The 10 `restore_trial_index` tables (`motion`, `rr98_accuracy`,
`non_parametric_mixture_modeling_exp1_Cleaned`, and seven `duolingo_*`) are trial-level
by design, but the only column separating their repeated rows is `rt`. A response time
is a measurement, not an occasion label, and must not be what makes rows unique. The
`duolingo_*` tables are the sharpest case: `session` leaves most of the excess
unseparated because a learner meets the same lexeme repeatedly *within* a session.

## Not done here

Nothing was re-uploaded — that is Ben's step. The verdicts name the fix per table;
they do not apply it.
