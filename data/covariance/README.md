# Covariance matrices (`irw_cov`, `source = "cov"`)

Processing scripts and records for the **covariance** data family (`source = "cov"`): published correlation and covariance matrices with no raw data behind them in the IRW, held in one format so they can be found, cited and fitted the way response tables are. The users in view are people doing SEM and other limited-information analyses, who need a matrix and its N, not a person × item table.

Not to be confused with `cov_*` columns in other families, which are person-level covariates.

**Status (2026-11-17).** Draft standard. 254 tables (1864 matrices) are built locally and pass `irw_validate.cov`, and every one has been checked to equal its package original exactly. `matrices.csv` records each matrix; `held.csv` records every candidate not built. On Redivis, `irw_cov:4e2q` v2.1 holds all 87 (released by Ben on 2026-11-17).

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
| `stat` | `cor` or `cov` for a matrix cell; `sd`, `mean` or `rel` (reliability) for a per-variable row. One group's matrix is all `cor` or all `cov`. |
| `var1`, `var2` | variable names as the source gives them (shortened only when the source has none). `var2` is blank on `sd`/`mean` rows. |
| `value` | the number **as published**: never rounded, smoothed or corrected. A suspected typo stays and goes in the record's `notes`. |
| `n` | the sample size the cell rests on: the pairwise n when the source reports one, otherwise the matrix N on every row. Never blank, so a table is enough on its own for `sample.nobs`. |
| `group` | optional. Present only when one source publishes matrices for several samples, such as boys and girls or two random halves. Each group is checked as its own matrix. |

Rules (the validator's V1-V8):

- **V1:** `stat`, `var1`, `var2`, `value` and `n` are present; `stat`, `var1` and `n` are never blank, and `value` is blank only on an off-diagonal `cor`/`cov` row (V4).
- **V2:** `stat` is one of `cor`, `cov`, `sd`, `mean`, `rel`, with one matrix kind per group.
- **V3:** cell rows name two variables; moment rows name one.
- **V4:** every cell of the lower triangle has a row, exactly once, and (a, b) and (b, a) count as the same cell. A cell the source did not report, between two variables it did measure, is a row with an **empty `value`**: reported (info), never an error, and counted in `cov_metadata`'s `n_missing_cells`. A variable the source never measured is left out of that sample's matrix instead, so a blank is always "not reported", never "not measured" and never a transcription gap. A diagonal, `sd`, `mean` or `rel` value is never blank.
- **V5:** a `cor` diagonal is 1, and every correlation (or the correlation a covariance implies) is in [-1, 1], with a tolerance of 0.001 for published rounding.
- **V6:** `value` is numeric, and `n` is a positive integer.
- **V7:** no columns beyond those above. Per-variable rows are given at most once per variable, only for variables in the matrix; SD > 0, and a reliability is at most 1.
- **V8:** a matrix that is **not positive definite is a warning, never an error.** For a matrix with blank cells it is judged on the complete part: the matrix after dropping the fewest variables that leaves no blank (ties keep the variables listed first). `cov_metadata`'s `min_eigenvalue` and `is_pd`, `irw_validate.cov.complete_drop` and the packages' `complete = TRUE` all use this rule. Rounding, pairwise deletion and typos make many published matrices non-PD (`burt_1915_emotions11` is one), and the user is better served by the matrix as published plus a flag than by a silently repaired one.

## Records kept for every table

- **A script** with the usual IRW header: citation, where the matrix was taken from, its licence, and anything changed in shape (never in value).
- **A row per matrix in `matrices.csv`** (keyed by `table` + `group`):
  - `n_obs`;
  - `matrix_type` (`pearson`, `spearman`, `polychoric`, `tetrachoric`, `kendall`, `mixed`, `unknown`; most SEM software cannot fit a `kendall` matrix directly);
  - `missing` (`listwise`, `pairwise`, `unknown`);
  - `population`;
  - `source_citation` and `source_location` (table and page);
  - `via` (the package or archive it was taken from, if not the paper);
  - `capture` (`package transcription`, `digital deposit`, `hand-entered`, `extracted`);
  - `verified` (`no`, `double entry`, or `reproduces published fit`);
  - `licence` and `licence_source`;
  - `variables`: the matrix's variables **in the source's published order**, separated by ` | ` (space, pipe, space). Each entry is the exact `var1`/`var2` name, optionally followed by ` = ` and a description: `x1 = father's education | x2 = father's occupation | y3 = son's education`, or names alone. Every variable of that sample's matrix appears once; a description never contains `|`, and may say where the source describes the variable ("see Table 1"). Blank means the order is unknown. The packages re-sort a fetched table by it, so matrices come back in published order (Ben, 2026-11-18; #3594);
  - **study-level moderators**, as the source publishes them (Ben, 2026-11-18): `year` (of data collection, or of publication when that is all the source gives; the `notes` say which), `country` (ISO 3166 codes, `;`-separated for a multinational sample), and `moderators` for anything else the source reports per sample, as `name = value` entries separated by ` | ` (`design = longitudinal | mean_age = 34.2 | women = 0.61`). Only moderators the source publishes go here, never ones the IRW codes itself: like the matrix, they are kept as published. Blank when the source gives none. Formats (2026-11-18):
    - `year` is `YYYY` or a range as the source gives it, `YYYY-YYYY`; a range is never collapsed to one year.
    - `country` is ISO 3166-1 alpha-2 only. A place with no code of its own takes its state's code, and `notes` names it (Northern Cyprus: `CY`). Blank when the source does not state the sample's country; it is never inferred from author affiliations.
    - `moderators` names are snake_case. Use these names whenever they apply, so the fields are comparable across tables: `mean_age`, `sd_age`, `median_age` (years); `age_range` (`12-18`); `women` (a proportion from 0 to 1; a published percentage divided by 100 is the one conversion allowed); `design` (`cross-sectional`, `longitudinal`, `experimental` or `other`); `language` (ISO 639-1 codes, `;`-separated); `setting` (free text: school, clinical, online, ...); `unit` (what one observation was, when not a person: team, country, ...). Other names are free. A value never contains `|` or ` = `;
  - `overlaps`: the other IRW tables, of any family, whose data include this sample, `;`-separated (Ben, 2026-11-18). Examples: the `Opd2014` samples of `gnambs_2018_rses10` were computed from the same Open Psychometrics data as the core table `rosenberg_selfesteem`; the two `nohe_2015` tables share 19 studies; `becker_1992_ability3` and `becker_1994_ability3` share 4. Blank when no overlap is known. When a fetched table has any, the packages print a one-line note naming them, so a matrix is not pooled with its own data twice;
  - `notes`.

  Several pilot tables overlap: one sample's matrix is a subset of another's. Each is kept, because each is a canonical matrix in its own right, and `overlaps` names the other. A matrix computed from an IRW table is normally never stored (Rulings, 2026-11-17); one is kept only when it cannot be recomputed from the IRW copy, such as Gnambs's per-country Open Psychometrics samples (the IRW copy has no country column), and then `overlaps` always names the table it came from.
- **A dictionary row** in `automated_finding/dictionary_auto_cov.csv` (planned; no sheet, as for conjoint and rankings).

## Subject tags (#3645)

What a table is about, so it can be found by subject. Held in `tags.csv` here (`table`, `construct_type`, `sample`, `framework`, `notes`; one row per table), joined into `cov_metadata` by `metadata/22_cov.R`. Not in the core tags Sheet or `03_tags.R`, for the reasons conjoint gave (`tags/decisions/2919_conjoint_topic_tags.md`). Tags are living: corrections go by PR against `tags.csv`. An intake PR does not have to tag its tables: new tables are tagged in batches, under these rules. Until then they have NA tags in `cov_metadata`, and both `22_cov.R` and `metadata/tests/test_cov_tags.py` list them.

**`construct_type` and `sample` are core's columns**, with core's values and rules: `TAG_VOCAB` in `metadata/tag_normalize.R`, and the decision rules in `tags/.claude/skills/irw-auto-tag/references/vocab.md` (#1837 for `construct type`, #1760 and #1704 for `sample`). Multi-select, comma-joined, as in core, so one filter value finds core and cov tables alike. A cov table is tagged by what its matrix's variables measure, not by what the paper was about (core's rule 1). Demographic covariates in a matrix (age, sex, grade) do not add a value.

Codes are shared with core wherever they fit (Ben, 2026-11-18: "codes should intersect with core when possible"). Where none of core's values fits, cov may add one, recorded here. The cov additions so far:

- `construct_type` **`Socioeconomic/attainment`**: socioeconomic status and attainment measured as variables in their own right: education and occupation (one's own or a parent's), income, deprivation, and area indicators such as unemployment or homeownership rates. The classic status-attainment path models (`blau_1967_occupation5`, `duncan_1968_peer10`, `kerckhoff_1974_ambition7`) are the core case. Not for a parental-education covariate beside a psychological battery, by the demographic rule above. Votes cast and crime counts are `Behavioral` (what people did), which an aggregate table may carry alongside this value (`harman_1967_political8`).

**`sample` on a pooled table.** A table whose groups come from many separate studies (most MASEM tables) has no single recruitment, which core never needed to cover. Rule (Ben, 2026-11-18):

- **Setting** values (`Clinical`, `Educational`, `Workplace`, `Internet-based`, `Program-based`) are the union over the groups: a value is given when any group was reached that way, as in core's "a study that samples both takes both". `norton_2013_hads14` pools patients and community samples and is `Clinical`. A setting may be read from the design when every group shares it by construction (supervisor-subordinate leadership studies are `Workplace`), and `notes` says so.
- **Frame** values (`Representative`, `Targeted/specific`, `General/non-specific`) are left blank.
- When the groups record no population and the design implies none, `sample` is blank.

A **respondent-type** value applies as in core: a matrix over states or election areas is `Non-person unit`, alone.

On a single-sample table, the frame follows core's rules, read from the record (`population`, `notes`) or the source; when recruitment is not described, the frame is blank.

**`framework`** (cov only; single value; usually blank) names the theory a matrix was assembled to test, when its variables are that model's constructs: the paper fits the model, or the meta-analysis pooled studies of it. An extended model is still that model (TPB plus health consciousness is `TPB`). A matrix that borrows one construct from a theory gets no framework. Values:

| value | model |
|---|---|
| `TPB` | theory of planned behaviour (attitude, subjective norm, perceived behavioural control, intention, behaviour) |
| `RAA` | reasoned action approach (TPB with the attitude and norm components split) |
| `HAPA` | health action process approach |
| `TAM` | technology acceptance model |
| `UTAUT` | unified theory of acceptance and use of technology |
| `SCCT` | social cognitive career theory |
| `HBM` | health belief model |
| `status_attainment` | Blau-Duncan status attainment and its extensions (Wisconsin model) |

A new value is added here first, with the tables that need it.

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
- [x] Overlapping matrices: the `overlaps` record field, with a note on fetch (Ben, 2026-11-18; replaces the free-text note of 2026-11-17, #3594).

**Later.**

- [ ] Linked IRW tables (one study, shared respondents, joined by `irw_merge()`): revisit whether the cross-table matrix is computed on fetch or stored. The prerequisite is a linkage record (study, tables, whether ids link: yes, no or unknown) instead of `irw_merge()`'s warning, which would also serve `irw_merge()`. Item-level only until reverse-keying exists.
- [ ] A validation pass: compare published item-level matrices against what compute-on-fetch gives for the matching IRW table. A mismatch is likely to point to a conversion bug.

## Rulings

- 2026-11-17 (Ben): the family holds published matrices only, for now. IRW-derived matrices are computed client-side, not stored. Name `cov` / `irw_cov`. SEM users come first.
- 2026-11-17 (Ben): derived matrices for single IRW tables are never stored; `irw_fetch()` on a core table with `source = "cov"` computes one. Linked multi-table matrices may be revisited.
- 2026-11-17 (Ben): in the long run the family goes on the home page.
- 2026-11-18 (Ben): `gnambs_2018_rses10`'s Opd2014 samples stay, although computed from the same data as `rosenberg_selfesteem`: they cannot be recomputed from the IRW copy (no country column) and make a didactic example of a published matrix beside its raw data. Overlaps are recorded in `overlaps`, and the packages note them on fetch.
- 2026-11-18 (Ben): study-level moderators are in scope when the source publishes them (record fields `year`, `country`, `moderators`), and per-variable reliability is a `rel` row beside `sd` and `mean`. Prompted by a reviewer: MASEM routinely uses year, country and reliability.
- 2026-11-18 (Ben, #3594): published variable order and variable labels live in one record field, `variables`, not in row order, which Redivis does not keep.
- 2026-11-18 (Ben, #3594): a cell the source did not report is held as a row with an empty `value` rather than leaving the study out ("this seems better than skipping and is objective/reversible"). `irw_cov2matrix()` returns NA there with a warning, and `complete = TRUE` returns the complete part; `irw_cov2list()` keeps NA for metaSEM. Positive definiteness is judged on the complete part.
- 2026-11-17 (Ben): pairwise-deletion matrices with only a sample N are built, the n noted as an upper bound (`feraco_2026_seb`). Correlations over aggregate units are in scope (`harman_1967_political8`, `wilkinson_1990_crimes7`). A package matrix that differs from its source is built as-is with the difference noted (`guthrie_1973_kipt8`). Licence requests to depositors wait until the family is more mature. Matrices from a CC BY supplement to a paywalled article are held pending a ruling (`paquin_2016_identity6`).
- 2026-11-19 (Ben): meta-analysts' averaged cells are not as reported (yang_2022_phomath15 out). Latent-factor correlations stay out (Feraco 0087a). A repo matrix whose dummy variable is coded the other way from the paper is built as-is with the coding noted (Feraco 0128a). Kendall's tau is allowed as matrix_type `kendall`.
- 2026-11-18 (Ben, #3645): subject tags reuse core's `construct type` and `sample` (values and rules) plus a cov-only `framework`, rather than a cov vocabulary; new values are allowed where core has none that fits ("codes should intersect with core when possible"), the first being `Socioeconomic/attainment`. On a pooled table, `sample` is the union of the groups' settings with the frame blank.
- 2026-11-19 (Ben): a matrix copied from a commercial test manual into a CC BY deposit takes the deposit's licence (ruchensky_2018_ppir8), as for GPL packages. Kosovo samples get a blank country with a note (no official ISO 3166-1 code; XK is user-assigned).
