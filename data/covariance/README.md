# Covariance matrices (`irw_cov`, `source = "cov"`)

Processing scripts and records for the **covariance** data family (`source = "cov"`): published correlation and covariance matrices with no raw data behind them in the IRW, held in one format so they can be found, cited and fitted the way response tables are. The users in view are people doing SEM and other limited-information analyses, who need a matrix and its N, not a person × item table.

Not to be confused with `cov_*` columns in other families, which are person-level covariates.

**Status (2026-11-17).** Draft standard. 97 tables (1374 matrices) are built locally and pass `irw_validate.cov`, and every one has been checked to equal its package original exactly. `matrices.csv` records each matrix; `held.csv` records every candidate not built. On Redivis, `irw_cov:4e2q` v2.1 holds all 87 (released by Ben on 2026-11-17).

**Second batch (2026-11-17, #3582).** `batch_rpackages2.R` adds 7 tables (11 matrices) from `fungible`, `ggm`, `EFAtools`, `GPArotation` and `psychTools`. `fungible`, `ggm` and `EFAtools` are read from pinned CRAN source tarballs instead of being installed (`fungible` pulls in OpenMx). `held.csv` lists every candidate considered and not built, and why: held for licence, values or N; pending an N from the original paper; or out of scope. Dictionary rows for all tables are in `automated_finding/dictionary_auto_cov.csv` (`stage_dict_row.py --source cov`). `02_biblio.R` does not read it yet. `holzinger_1939_grantwhite9` is released on Redivis as `irw_cov` v1.0 (Ben, 2026-11-17).

**metaSEM and test manuals (2026-11-17, #3582).** `batch_metasem.R` builds 17 tables (511 study matrices) from `metaSEM` 2.0, read from its pinned CRAN tarball. Rulings (Ben, 2026-11-17):
- A variable a study never measured (a blank diagonal) is dropped from that study's matrix, and `notes` names it.
- A study still holding a blank cell after that was not built: 30 studies in `boer_2016_lmx`, `cheung_2000_tpb` and `scalco_2017_tpborganic`, listed in `held.csv`. Since 2026-11-18 blank cells are allowed (V4 below), so these can be built.
- Matrices computed by a package author from survey microdata (ISSP, WVS) are in scope, with a note.
- A matrix in a GPL package is GPL even when it comes from a commercial test manual. `batch_rpackages3.R` builds the WJ IV norming matrices (six age groups) and the NEO PI-R facets on that basis.

Gnambs18 keeps only its 36 reported matrices: the other 77 were reproduced from factor loadings, which is model output. Values are written at full precision (the ISSP covariances are not short decimals). `batch_sem.R` adds five classic SEM teaching matrices shipped with `sem` (Duncan–Haller–Portes, Wheaton, Kerckhoff, Blau–Duncan, McDonald–Clelland union sentiment), and `batch_rpackages3.R` adds `psych::cattell`. `zenodo_brady2005.py` builds Brady et al. (2005) from an MIT-licensed Zenodo deposit.

**CC BY MASEM deposits (2026-11-17, #3582 source 4).** Three corpora are built from open OSF/Zenodo deposits, parsing the deposited files as text without executing them: `osf_li2019_class.py` (26 CLASS samples), `osf_innami2022_listening.py` (32 L2-listening samples) and `zenodo_or2024_tam.py` (43 TAM studies; one with blank cells is held). A survey of further deposits, with licence and contents, is summarised in the PR for #3582.

```
Rscript data/covariance/pilot_rpackages.R <out dir>
python3 -m irw_validate.cov <out dir>/*.csv        # skip matrices.csv
Rscript data/covariance/check_roundtrip.R <out dir>
```

## Scope

A table belongs here when the source publishes a **matrix of correlations or covariances among variables** and the IRW does not hold the responses it was computed from. Examples are a correlation table in a paper, a matrix in a textbook or a methods package, or a study matrix from a meta-analytic SEM corpus.

Not here:

- **Matrices computable from an IRW table.** Those are a derived quantity, not data. The package helper `irw_cor()` (planned) computes one from a fetched table, and the user chooses Pearson or polychoric (Ben, 2026-11-17, "for now").
- **Simulated or artificial matrices**, such as Schmid & Leiman's 12 × 12 or West. Those belong with simsyn if anywhere.
- **Factor loadings, path coefficients and other model output.** Only the input to a model is in scope.

## Layout

One table holds one source's matrix, or several matrices published together for different samples. There is one row per cell of the **lower triangle, diagonal included**, plus optional rows for per-variable moments. Row order carries no meaning: Redivis does not keep it (`burt_1915_emotions11` comes back alphabetical). The published variable order is kept as data, in the record's `variables` field (below).

| column | |
|---|---|
| `stat` | `cor` or `cov` for a matrix cell; `sd` or `mean` for a per-variable moment. One group's matrix is all `cor` or all `cov`. |
| `var1`, `var2` | variable names as the source gives them (shortened only when the source has none). `var2` is blank on `sd`/`mean` rows. |
| `value` | the number **as published**: never rounded, smoothed or corrected. A suspected typo stays and goes in the record's `notes`. |
| `n` | the sample size the cell rests on: the pairwise n when the source reports one, otherwise the matrix N on every row. Never blank, so a table is enough on its own for `sample.nobs`. |
| `group` | optional. Present only when one source publishes matrices for several samples, such as boys and girls or two random halves. Each group is checked as its own matrix. |

Rules (the validator's V1-V8):

- **V1:** `stat`, `var1`, `var2`, `value` and `n` are present; `stat`, `var1` and `n` are never blank, and `value` is blank only on an off-diagonal `cor`/`cov` row (V4).
- **V2:** `stat` is one of `cor`, `cov`, `sd`, `mean`, with one matrix kind per group.
- **V3:** cell rows name two variables; moment rows name one.
- **V4:** every cell of the lower triangle has a row, exactly once, and (a, b) and (b, a) count as the same cell. A cell the source did not report, between two variables it did measure, is a row with an **empty `value`**: reported (info), never an error, and counted in `cov_metadata`'s `n_missing_cells`. A variable the source never measured is left out of that sample's matrix instead, so a blank is always "not reported", never "not measured" and never a transcription gap. A diagonal, `sd` or `mean` value is never blank.
- **V5:** a `cor` diagonal is 1, and every correlation (or the correlation a covariance implies) is in [-1, 1], with a tolerance of 0.001 for published rounding.
- **V6:** `value` is numeric, and `n` is a positive integer.
- **V7:** no columns beyond those above. Moments are given at most once per variable, only for variables in the matrix, and SD > 0.
- **V8:** a matrix that is **not positive definite is a warning, never an error.** For a matrix with blank cells it is judged on the complete part: the matrix after dropping the fewest variables that leaves no blank (ties keep the variables listed first). `cov_metadata`'s `min_eigenvalue` and `is_pd`, `irw_validate.cov.complete_drop` and the packages' `complete = TRUE` all use this rule. Rounding, pairwise deletion and typos make many published matrices non-PD (`burt_1915_emotions11` is one), and the user is better served by the matrix as published plus a flag than by a silently repaired one.

## Records kept for every table

- **A script** with the usual IRW header: citation, where the matrix was taken from, its licence, and anything changed in shape (never in value).
- **A row per matrix in `matrices.csv`** (keyed by `table` + `group`):
  - `n_obs`;
  - `matrix_type` (`pearson`, `polychoric`, `tetrachoric`, `mixed`, `unknown`);
  - `missing` (`listwise`, `pairwise`, `unknown`);
  - `population`;
  - `source_citation` and `source_location` (table and page);
  - `via` (the package or archive it was taken from, if not the paper);
  - `capture` (`package transcription`, `digital deposit`, `hand-entered`, `extracted`);
  - `verified` (`no`, `double entry`, or `reproduces published fit`);
  - `licence` and `licence_source`;
  - `variables`: the matrix's variables **in the source's published order**, separated by ` | ` (space, pipe, space). Each entry is the exact `var1`/`var2` name, optionally followed by ` = ` and a description: `x1 = father's education | x2 = father's occupation | y3 = son's education`, or names alone. Every variable of that sample's matrix appears once; a description never contains `|`, and may say where the source describes the variable ("see Table 1"). Blank means the order is unknown. The packages re-sort a fetched table by it, so matrices come back in published order (Ben, 2026-11-18; #3594);
  - `notes`.

  Several pilot tables overlap: one sample's matrix is a subset of another's. The `notes` column says so instead of one being dropped, because each is a canonical matrix in its own right.
- **A dictionary row** in `automated_finding/dictionary_auto_cov.csv` (planned; no sheet, as for conjoint and rankings).

## Intake rules

- **Licence:** a matrix takes the licence of where it was taken from, under the IRW licensing summary table:
  - Matrices from a GPL package (the whole pilot) are reshared under the GPL, with a modification notice.
  - Matrices from an open-access article under CC BY are reshared with attribution, a licence link and a modification notice.
  - Paywalled or unlicensed articles, and archives with no stated terms (for example the WMF Human Cognitive Abilities archive of Carroll's matrices), need written permission. Until then, link to them and do not reshare.

  Whether a published correlation table is a non-copyrightable fact is a question for counsel. Do not assume it.
- **N is required.** A matrix whose source gives no sample size is not taken: an SEM fit needs it. This is why the pilot left out `Schutz` (and `Harman.political`, until its N of 147 areas was found in the psych help page).
- **Pairwise n not given.** A matrix computed with pairwise deletion whose source gives only the sample N is built with that N on every row and `missing = "pairwise"`; its notes say the n is an upper bound, since cells with missing data rest on fewer cases. When the source gives per-cell n, that is used.
- **Aggregate units.** A matrix computed over units other than persons (election areas, states) is in scope. `population` names the units and `n` is the number of units.
- **A package copy that differs from the original source** is built from the package as-is, with each differing cell named in the notes (for example the two swapped cells of `guthrie_1973_kipt8`).
- **Table names:** the usual `author_year_construct`, lowercase, at most 40 characters. The author is the first author of the study that collected the data, not of the book that reprinted the matrix (for example `mullen_1939_physical8`, reprinted in Harman 1976).

## To do (non-data)

Data acquisition is tracked in #3582. Everything else lives here until the family has its own tracker.

**Plumbing.** This can be built now, but it is not released until #3582 shows a few hundred matrices are reachable.

- [x] `red_up --dataset irw_cov` (code only; `irw_cov` is not yet in `redivis_config.R` because the dataset doesn't exist): route uploads to `irw_validate.cov` (the destination chooses the validator, as for rankings), with `matrices.csv` as the gate. A table with no record row is refused.
- [x] `metadata/22_cov.R` → `cov_metadata` (also `n_missing_cells`; `min_eigenvalue` and `is_pd` are NA for an incomplete matrix): one row per table × group, with n_vars, N, matrix_type, PD flag, minimum eigenvalue and has_sd. Register it in `red_up/cli.py` `META_TABLES` and `upload_meta.py` `FILE_TABLE_MAP`.
- [x] `automated_finding/dictionary_auto_cov.csv` (#3584) plus `metadata/02_biblio.R` → `cov_biblio` (first produced by the next pipeline run) (no sheet, as for conjoint and rankings).
- [ ] Packages (R and Python). R: compute on fetch, `irw_cov_compute()` and `irw_cov2matrix()` are in Rpkg#235, and `method` also takes a user-defined function (Ben, 2026-11-17). Python: the same in itemresponsewarehouse/Python-pkg#150, with polychoric and tetrachoric written in numpy because scipy is not a dependency. Not started in either client: `source = "cov"` for published matrices.
  - `source = "cov"`;
  - `irw_cov2matrix()` returning matrix, n, sd and mean, ready for `lavaan(sample.cov=, sample.nobs=)` (prototype in `check_roundtrip.R`);
  - **compute on fetch**: `irw_fetch(<core table>, source = "cov")` returns the table's item matrix in this layout. It takes a method argument (Pearson by default, polychoric on request) and is labelled as computed, with method and IRW version, so it is never mistaken for a published matrix. It refuses tables with too many items, repeated measures without a wave filter, and non-core families. Pairwise `n` is kept.
- [x] First release of `irw_cov` (v1.0, 2026-11-17, `irw_cov:4e2q`; Ben), **then** the client config (Rpkg#236, Python-pkg#151, and `redivis_config.R` here) (the six symbols, in the order in `Rpkg/inst/developer/warehouses.md`). Never name the dataset in config before its first release.

**Site and docs.**

- [ ] `irw_site/cov_standard.qmd`: the standard, a "what the family holds" block and a worked lavaan example (Holzinger–Swineford).
- [ ] A row in the families table on `overview.qmd`, and the `src/ARCHITECTURE.md` families row.
- [ ] **The home page.** Not needed straight away, but in the long run the family appears there alongside the others.

**Standard decisions still open.**

- [x] Matrices printed with blank cells: allowed as an empty `value` (V4), with `complete = TRUE` in the packages (Ben, 2026-11-18; #3594).
- [ ] Variable order and labels: the `variables` record field (Ben, 2026-11-18; #3594). Spec, checks and package support are in; backfill for the built tables is pending (irw-7b).
- [x] Overlapping matrices: a free-text note in the record naming the overlapping table, no `subset_of` column (Ben, 2026-11-17; #3594).

**Later.**

- [ ] Linked IRW tables (one study, shared respondents, joined by `irw_merge()`): revisit whether the cross-table matrix is computed on fetch or stored. The prerequisite is a linkage record (study, tables, whether ids link: yes, no or unknown) instead of `irw_merge()`'s warning, which would also serve `irw_merge()`. Item-level only until reverse-keying exists.
- [ ] A validation pass: compare published item-level matrices against what compute-on-fetch gives for the matching IRW table. A mismatch is likely to point to a conversion bug.

## Rulings

- 2026-11-17 (Ben): the family holds published matrices only, for now. IRW-derived matrices are computed client-side, not stored. Name `cov` / `irw_cov`. SEM users come first.
- 2026-11-17 (Ben): derived matrices for single IRW tables are never stored; `irw_fetch()` on a core table with `source = "cov"` computes one. Linked multi-table matrices may be revisited.
- 2026-11-17 (Ben): in the long run the family goes on the home page.
- 2026-11-18 (Ben, #3594): published variable order and variable labels live in one record field, `variables`, not in row order, which Redivis does not keep.
- 2026-11-18 (Ben, #3594): a cell the source did not report is held as a row with an empty `value` rather than leaving the study out ("this seems better than skipping and is objective/reversible"). `irw_cov2matrix()` returns NA there with a warning, and `complete = TRUE` returns the complete part; `irw_cov2list()` keeps NA for metaSEM. Positive definiteness is judged on the complete part.
- 2026-11-17 (Ben): pairwise-deletion matrices with only a sample N are built, the n noted as an upper bound (`feraco_2026_seb`). Correlations over aggregate units are in scope (`harman_1967_political8`, `wilkinson_1990_crimes7`). A package matrix that differs from its source is built as-is with the difference noted (`guthrie_1973_kipt8`). Licence requests to depositors wait until the family is more mature. Matrices from a CC BY supplement to a paywalled article are held pending a ruling (`paquin_2016_identity6`).
