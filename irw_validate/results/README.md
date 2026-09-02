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

# `dup_id_item` triage, 2026-09-02

`dup_id_item_triage_2026-09-02.csv` follows up the 101 tables the sweep flagged.

Ben's method: **where the local `.Rdata` row count matches `metadata.csv`, trust the
local copy.** That covers 57 of the 101 — 39 differ from what is published and 5 are
not in `metadata.csv`, so those need live data before anything can be said.

Of the 57:

| | tables | what it means |
|---|---|---|
| **explained by a column the check ignores** | 14 | `rater` ×11, plus `trialnum`, `order`, `period` |
| **bare `id`/`item`/`resp`** | 15 | nothing can explain the repeat — real defects |
| **unexplained** | 28 | other columns present, none resolves it — needs a per-table look |

## The 14 were the check's fault, and it is fixed

`dup_id_item` asked whether `wave`/`timepoint`/`date` explained a repeated `id`+`item`.
That list came from `validate_irw.R` and is stale: it predates `rater` and never covered
trial-level designs. Two raters scoring the same person on the same item is **the design**,
and `datastandard.md` documents `rater` as a legitimate column — so the check was reporting
the standard's own schema as an error.

The gate profiles now consult `rater`, `trialnum`, `trial`, `order`, `session`, `occasion`,
`period`, `block` and `subtest` as well. `triage` is unchanged, because fifty scripts
depend on it.

Deliberately **not** included: `group`, `study`, `treatment`. Those describe the person or
the arm rather than the occasion, and a person appearing twice under them is a real
question, not an explanation. Eleven of the 28 unexplained have exactly such a column.

## What is left

- **15 bare tables** — the `florida_twins_behavior_*` family is six of them, each with
  100% of rows duplicated and no other column. Candidate for a straight dedupe, but the
  source should say whether the duplication is in the original.
- **28 unexplained** — per-table judgment.
- **44 not yet analysed** — 39 whose local copy disagrees with what is published, 5 absent
  from `metadata.csv`. These need live data; `data/pub` cannot answer for them.
