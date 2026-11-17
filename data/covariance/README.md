# Covariance matrices (`irw_cov`, `source = "cov"`)

Processing scripts and records for the **covariance** data family (`source = "cov"`): published correlation and covariance matrices with no raw data behind them in the IRW, held in one format so they can be found, cited and fitted the way response tables are. The users in view are people doing SEM and other limited-information analyses, who need a matrix and its N, not a person × item table.

Not to be confused with `cov_*` columns in other families, which are person-level covariates.

**Status (2026-11-17).** Draft standard, pilot only. `pilot_rpackages.R` builds 12 tables (14 matrices) from matrices already transcribed into `psychTools`, `psych` and base R `datasets`. All pass `irw_validate.cov`, and `check_roundtrip.R` confirms that each rebuilt matrix equals its package original exactly and that lavaan fits on the IRW copy match fits on the original. Nothing is on Redivis. `irw_cov` does not exist yet and is named in no client config, per the rule that a dataset is configured only after its first release.

**Second batch (2026-11-17, #3582).** `batch_rpackages2.R` adds 7 tables (11 matrices) from `fungible`, `ggm`, `EFAtools`, `GPArotation` and `psychTools`. `fungible`, `ggm` and `EFAtools` are read from pinned CRAN source tarballs instead of being installed (`fungible` pulls in OpenMx). `held.csv` lists every candidate considered and not built, and why: held for licence, values or N; pending an N from the original paper; or out of scope. Dictionary rows for all tables are in `automated_finding/dictionary_auto_cov.csv` (`stage_dict_row.py --source cov`). `02_biblio.R` does not read it yet. `holzinger_1939_grantwhite9` is released on Redivis as `irw_cov` v1.0 (Ben, 2026-11-17).

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

One table holds one source's matrix, or several matrices published together for different samples. There is one row per cell of the **lower triangle, diagonal included**, written row by row in the published variable order, plus optional rows for per-variable moments.

| column | |
|---|---|
| `stat` | `cor` or `cov` for a matrix cell; `sd` or `mean` for a per-variable moment. One group's matrix is all `cor` or all `cov`. |
| `var1`, `var2` | variable names as the source gives them (shortened only when the source has none). `var2` is blank on `sd`/`mean` rows. |
| `value` | the number **as published**: never rounded, smoothed or corrected. A suspected typo stays and goes in the record's `notes`. |
| `n` | the sample size the cell rests on: the pairwise n when the source reports one, otherwise the matrix N on every row. Never blank, so a table is enough on its own for `sample.nobs`. |
| `group` | optional. Present only when one source publishes matrices for several samples, such as boys and girls or two random halves. Each group is checked as its own matrix. |

Rules (the validator's V1-V8):

- **V1:** `stat`, `var1`, `var2`, `value` and `n` are present; `stat`, `var1`, `value` and `n` are never blank.
- **V2:** `stat` is one of `cor`, `cov`, `sd`, `mean`, with one matrix kind per group.
- **V3:** cell rows name two variables; moment rows name one.
- **V4:** every cell of the lower triangle appears exactly once, and (a, b) and (b, a) count as the same cell. A matrix the source printed with blanks cannot be held.
- **V5:** a `cor` diagonal is 1, and every correlation (or the correlation a covariance implies) is in [-1, 1], with a tolerance of 0.001 for published rounding.
- **V6:** `value` is numeric, and `n` is a positive integer.
- **V7:** no columns beyond those above. Moments are given at most once per variable, only for variables in the matrix, and SD > 0.
- **V8:** a matrix that is **not positive definite is a warning, never an error.** Rounding, pairwise deletion and typos make many published matrices non-PD (`burt_1915_emotions11` is one), and the user is better served by the matrix as published plus a flag than by a silently repaired one.

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
  - `notes`.

  Several pilot tables overlap: one sample's matrix is a subset of another's. The `notes` column says so instead of one being dropped, because each is a canonical matrix in its own right.
- **A dictionary row** in `automated_finding/dictionary_auto_cov.csv` (planned; no sheet, as for conjoint and rankings).

## Intake rules

- **Licence:** a matrix takes the licence of where it was taken from, under the IRW licensing summary table:
  - Matrices from a GPL package (the whole pilot) are reshared under the GPL, with a modification notice.
  - Matrices from an open-access article under CC BY are reshared with attribution, a licence link and a modification notice.
  - Paywalled or unlicensed articles, and archives with no stated terms (for example the WMF Human Cognitive Abilities archive of Carroll's matrices), need written permission. Until then, link to them and do not reshare.

  Whether a published correlation table is a non-copyrightable fact is a question for counsel. Do not assume it.
- **N is required.** A matrix whose source gives no sample size is not taken: an SEM fit needs it. This is why the pilot leaves out `Schutz` and `Harman.political`.
- **Table names:** the usual `author_year_construct`, lowercase, at most 40 characters. The author is the first author of the study that collected the data, not of the book that reprinted the matrix (for example `mullen_1939_physical8`, reprinted in Harman 1976).

## To do (non-data)

Data acquisition is tracked in #3582. Everything else lives here until the family has its own tracker.

**Plumbing.** This can be built now, but it is not released until #3582 shows a few hundred matrices are reachable.

- [x] `red_up --dataset irw_cov` (code only; `irw_cov` is not yet in `redivis_config.R` because the dataset doesn't exist): route uploads to `irw_validate.cov` (the destination chooses the validator, as for rankings), with `matrices.csv` as the gate. A table with no record row is refused.
- [ ] `metadata/NN_cov.R` → `cov_metadata`: one row per table × group, with n_vars, N, matrix_type, PD flag, minimum eigenvalue and has_sd. Register it in `red_up/cli.py` `META_TABLES` and `upload_meta.py` `FILE_TABLE_MAP`.
- [ ] `automated_finding/dictionary_auto_cov.csv` plus `metadata/02_biblio.R` → `cov_biblio` (no sheet, as for conjoint and rankings).
- [ ] Packages (R and Python). R: compute on fetch, `irw_cov_compute()` and `irw_cov2matrix()` are in Rpkg#235, and `method` also takes a user-defined function (Ben, 2026-11-17). Python: the same in itemresponsewarehouse/Python-pkg#150, with polychoric and tetrachoric written in numpy because scipy is not a dependency. Not started in either client: `source = "cov"` for published matrices.
  - `source = "cov"`;
  - `irw_cov2matrix()` returning matrix, n, sd and mean, ready for `lavaan(sample.cov=, sample.nobs=)` (prototype in `check_roundtrip.R`);
  - **compute on fetch**: `irw_fetch(<core table>, source = "cov")` returns the table's item matrix in this layout. It takes a method argument (Pearson by default, polychoric on request) and is labelled as computed, with method and IRW version, so it is never mistaken for a published matrix. It refuses tables with too many items, repeated measures without a wave filter, and non-core families. Pairwise `n` is kept.
- [ ] First release of `irw_cov`, **then** the client config (the six symbols, in the order in `Rpkg/inst/developer/warehouses.md`). Never name the dataset in config before its first release.

**Site and docs.**

- [ ] `irw_site/cov_standard.qmd`: the standard, a "what the family holds" block and a worked lavaan example (Holzinger–Swineford).
- [ ] A row in the families table on `overview.qmd`, and the `src/ARCHITECTURE.md` families row.
- [ ] **The home page.** Not needed straight away, but in the long run the family appears there alongside the others.

**Standard decisions still open.**

- [ ] Matrices printed with blank cells: V4 refuses them today, but MASEM study matrices are incomplete by design. Allow `value` blank with a count in `cov_metadata`? #3582 reports how many there are.
- [ ] Variable labels (e.g. "Vocabulary, WAIS subtest"): a small labels table, the analogue of item text. Where does it live?
- [ ] Overlapping matrices: a free-text `notes` today. Is a `subset_of` column worth it?

**Later.**

- [ ] Linked IRW tables (one study, shared respondents, joined by `irw_merge()`): revisit whether the cross-table matrix is computed on fetch or stored. The prerequisite is a linkage record (study, tables, whether ids link: yes, no or unknown) instead of `irw_merge()`'s warning, which would also serve `irw_merge()`. Item-level only until reverse-keying exists.
- [ ] A validation pass: compare published item-level matrices against what compute-on-fetch gives for the matching IRW table. A mismatch is likely to point to a conversion bug.

## Rulings

- 2026-11-17 (Ben): the family holds published matrices only, for now. IRW-derived matrices are computed client-side, not stored. Name `cov` / `irw_cov`. SEM users come first.
- 2026-11-17 (Ben): derived matrices for single IRW tables are never stored; `irw_fetch()` on a core table with `source = "cov"` computes one. Linked multi-table matrices may be revisited.
- 2026-11-17 (Ben): in the long run the family goes on the home page.
