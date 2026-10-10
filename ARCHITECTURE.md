# IRW: project map

The map of the Item Response Warehouse for someone who has read nothing else:
which repository owns what, where the data lives, and **which document to trust
when two disagree**.

This file is deliberately thin. It is not a code tour and it does not document
individual scripts. Where a fact is already recorded somewhere, this file links
to it rather than repeating it — see [Two rules](#two-rules) at the end.

---

## 1. Repositories

Four repositories across **three** GitHub accounts. That split is the single most
confusing thing about this project's layout, so it is stated first:

| Repository | GitHub | Owns |
|---|---|---|
| `src` | `ben-domingue/irw` | Per-dataset processing scripts, the metadata pipeline, automated dataset finding |
| `irw_site` | `datapages/irw` | The Quarto site published at [itemresponsewarehouse.org](https://itemresponsewarehouse.org) |
| `Rpkg` | `itemresponsewarehouse/Rpkg` | The `irw` **R** package |
| `Python-pkg` | `itemresponsewarehouse/Python-pkg` | The `irw` **Python** package |

`src` is on a personal account, the site on `datapages`, and the two client
packages on the `itemresponsewarehouse` org. There is no technical reason for
this; it is history. The Python package installs from PyPI (`pip install irw`);
the R package installs from GitHub until its CRAN submission (Rpkg#147) is
accepted. This repository publishes one package of its own, `irw-validate`, to
PyPI from a tag (section 6).

Package versions are deliberately not written here: they moved four times in a
week and both numbers in this table were wrong within days of being typed. Read
them from `Rpkg/DESCRIPTION` and `Python-pkg/pyproject.toml`, which cannot go
stale.

## 2. Redivis

All data lives on Redivis under the account **`datapages`**. Everything else in
this repository reads that from one place:

> `IRW_OWNER`, `IRW_CORE_DATASETS`, `IRW_TEXT_DATASETS`, `IRW_CONJ_DATASETS` and
> `IRW_AUX_DATASETS` in [`metadata/redivis_config.R`](metadata/redivis_config.R) are authoritative
> for the owner and the dataset names.

> **Redivis caps any single dataset at 1000 tables.** That cap is the reason
> sharding exists, and it applies to *every* dataset, not just the response data.

**Core shards** hold the response data. A *shard* here is simply one of several
Redivis datasets with identical structure, named `item_response_warehouse`,
`item_response_warehouse_2`, and so on — a new one is added when the last hits
the cap. Which shard a given table is in is not predictable
from its name, so the client packages search them **newest-first** and return the
first match — meaning a name present in more than one shard resolves to its most
recent copy.

**Item text shards the same way**, for the same reason: `irw_text`, `irw_text_2`,
`irw_text_3`, … in `IRW_TEXT_DATASETS`, searched newest-first, first match wins. A table stays
reachable from whichever shard already holds it, so tables are never moved
between shards — moving one *creates* the shadowing problem rather than solving
it. `Rpkg/inst/developer/warehouses.md` carries the checklist for adding a shard
of either kind.

**Conjoint shards the same way too**, since October 2026, when `irw_conjoint`
passed 800 tables: `irw_conjoint`, `irw_conjoint_2`, … in `IRW_CONJ_DATASETS`,
newest-first, first match wins. Unlike core, a name present in two conjoint
shards is *flagged*: `16_conjoint.R` reports it, and both client packages warn
from `list_tables(source = "conj")`, before the newest copy is kept. Where NEW
conjoint tables are uploaded is `CONJ_DEFAULT` in `red_up/targets.py` (None:
the newest shard, since 2026-10-09); an existing table is always updated in the
shard that holds it. `red_up` refuses any upload that would take a dataset past
the 1000-table cap, counting its open draft.

**Data families.** Every response table belongs to exactly one of five *data
families*, and each family lives in its own Redivis dataset or shard list. Core
and conjoint are shard lists; the other three are single datasets, only because
none is near the cap:

| Family | `source =` | Redivis dataset | What defines it | Standard |
|---|---|---|---|---|
| core | (default) | `item_response_warehouse`, `_2`, … | person × item → ordered or continuous response | `datastandard.md` |
| nominal | `nom` | `irw_nominal` | response categories with no order | site `nominal_standard.qmd` |
| competitions | `comp` | `irw_competitions` | two agents meet and an outcome is recorded; also pairwise comparisons of fixed things, such as texts judged against each other | site `comps_standard.qmd` |
| simsyn | `sim` | `irw_simsyn` | responses not produced by real people | site `simsyn.qmd` |
| conjoint | `conj` | `irw_conjoint`, `_2`, … | respondent × task × profile choices or ratings, profiles randomly assembled from attributes | `data/conjoint/README.md`, site `conjoint_standard.qmd` |

Four families are defined by the shape of the data; simsyn is defined by
provenance (a simulated table can be dichotomous, nominal, anything). The
families are still exclusive in practice, one table to one dataset. The line
between competitions and conjoint is what is compared: competitions compare the
same named agents again and again, conjoint compares bundles of attributes
assembled at random for each task. The packages' `source` argument selects the
family; it keeps that name, though "source" elsewhere in this repo means data
provenance.

Conjoint tables have their own layout (one row per respondent × task × profile,
no `item`/`resp`). `red_up` checks them with `irw_validate.conjoint` rather
than the core validator, `16_conjoint.R` writes `conj_metadata` and
`conj_outcomes`, and their biblio comes from the automated dictionary file
alone, with no sheet.

**Auxiliary datasets** hold no response data and describe the tables in the
families: `irw_meta` (all metadata, biblio, tags and collections tables) and
item text. "Auxiliary" means only these. Groups inside a family, such as the
trial-level sports tables, ESM, PISA or the `gilbert_meta_*` series, are
*groups* (or collections, when curated), not families.

How many of each exist today is *not* recorded here, deliberately — that number
grows, and a count written into prose is wrong the day it changes. `redivis_config.R`
is the answer:

```r
source("metadata/redivis_config.R")
IRW_CORE_DATASETS; IRW_TEXT_DATASETS; IRW_CONJ_DATASETS; IRW_AUX_DATASETS
```

Until August 2026 all of this lived under the personal Redivis account
`bdomingu`. Redivis resolves references to a previous owner automatically, so
older scripts still work.

> **Duplicated, and checked.** The dataset identifiers are declared in three
> files: `metadata/redivis_config.R` here, `R/redivis-config.R` in `Rpkg`, and
> `src/irw/config.py` in `Python-pkg`. All three describe themselves as a single
> source of truth. They are reconcilable — this repo carries plain dataset
> *names*, the two packages additionally carry version *hashes* — but a new shard
> must be added in all three, and each file carries *three* shard lists, core,
> item text and conjoint (`IRW_CORE_DATASETS`/`IRW_TEXT_DATASETS`/`IRW_CONJ_DATASETS`,
> `.irw_datasource_specs$core`/`.irw_itemtext_specs`/`.irw_datasource_specs$conj`,
> `MAIN_REFS`/`ITEMTEXT_REFS`/`CONJ_REFS`), so adding a shard means one edit per
> file, in all three files, and the parity check compares order for all three lists.
>
> They drifted once already, undetected for months: `Python-pkg` had no
> reference to `irw_nominal`, so that source was reachable from R and not from
> Python (#1733). The duplication is not going away — three languages, three
> runtimes, no shared build — so what changed is that
> [`metadata/check_config_parity.py`](metadata/check_config_parity.py) now
> compares the three on every pull request, and it, not this paragraph, is what
> tells you they disagree. Per rule 2 below: run it rather than trust this.

```bash
python metadata/check_config_parity.py   # with Rpkg and Python-pkg as siblings
```

## 3. Google Sheets

These Google Sheets are load-bearing. They are the human entry surface for
metadata that is not derivable from the data itself:

| Sheet | What it holds |
|---|---|
| Data Dictionary — core | Descriptions, origins, licenses, references. Read by `metadata/02_biblio.R` and many other call sites (`git grep` its sheet id) |
| Data Dictionary — competitions, nominal, simsyn | The same, one per family. Conjoint has no sheet (`automated_finding/dictionary_auto_conj.csv` only) |
| IRW Tags | The eight hand-annotated tag columns. Read by `metadata/03_tags.R` |
| Nominal tags | The same, for the `nominal` source |
| Item text index | Not data: a table of *links*. `itemtext/join.R` reads a URL from each of columns 3–6 and fetches four further per-table tabs (`instrument`, `sections`, `items`, `responses`), then merges them |

The sheet URLs live in the scripts that read them; this file does not repeat
them.

`competitions` and `simsyn` have **no** tags sheet. That is a decision, not a
gap — see `Rpkg/inst/developer/tags.md`.

An eighth sheet, the automated-finding processing queue, was **retired
2026-08-12**. Its URL survives in `automated_finding/irw_process_queue.py` only
so that module still imports; `main()` refuses to run.

### These sheets are read-only *from code*

These are ordinary spreadsheets that maintainers edit by hand every day. What is
constrained is *automation*: no code in any of the four repositories writes to a
Google Sheet. There is no service account, and no `googlesheets4` or `gspread`
dependency anywhere. Every automated pipeline that produces sheet-shaped rows
writes them to a local CSV for a human to paste. The decision record is
[ben-domingue/irw#1708](https://github.com/ben-domingue/irw/issues/1708), which
concluded that no service account should be provisioned: automated rows reach the
published tables by another route instead (below). All issue numbers in this file
refer to `ben-domingue/irw`.

So "read-only" never means the data is stuck. Repairing even thousands of rows is
a find-and-replace or a column paste, not a code change.

Both sheets now take automated rows the same way — a git-tracked CSV unioned at
export — but they differ in *granularity*, and that difference is deliberate:

- **Tags** — automated rows land in `tags/tags_auto.csv`. On export, `03_tags.R`
  concatenates it with the sheet's rows and drops any automated row for a table a
  human has already tagged, so a human entry always wins (#1723). This supersedes
  at **row** level, which strands 19–76 tables per column whose sheet row leaves
  that column blank (#1863, open).
- **Dictionary** — automated rows land in
  `automated_finding/dictionary_auto.csv`, written by `stage_dict_row.py`. On
  export, `metadata/dict_union.R` merges it into the sheet at **column** level: a
  human cell wins the cell it occupies, an automated cell fills a cell the human
  left blank (#1732). Column-wise from the start because a sparse-but-present
  dictionary row is the common case, where for tags it is the exception.
  `metadata/biblio_provenance.csv` records which cells came from the automated
  file, and unlike the tags sidecar it is committed. The comps, nominal and
  simsyn dictionaries work the same way, each with its own file
  (`dictionary_auto_comps.csv`, `_nom.csv`, `_sim.csv`; `stage_dict_row.py
  --source comps|nom|sim`), so no dictionary sheet needs rows pasted (#2628).
  Their sheets spell three columns differently from core; `normalize_dict_layout()`
  maps them onto core's names in the export only.

> **One column exists only in the automated file: `DOI (for data)`.** The sheet
> does not have it and is not going to. 979 rows put a *deposit* DOI (Dataverse,
> Mendeley, figshare, Zenodo, Dryad, OSF, ICPSR) in `DOI (for paper)`, which is a
> different object -- its year is a deposit year and it resolves to the
> depositor, not the authors. `DICT_AUTO_ONLY_COLS` in `metadata/dict_union.R`
> carries the split; `union_dict()` creates the column in the merged frame
> (#1690). This is also the **only** case where an automated cell beats a filled
> human one: where the automated `DOI (for data)` equals the sheet's
> `DOI (for paper)`, the paper cell is cleared *in the export*, never in the
> sheet, and every cleared cell is named in the provenance file.

> **`OSF_PERMISSION_PROJECTS` in `metadata/dict_union.R` asserts a fact about
> the outside world.** It stamps `Derived_License = "Permission via Email"` on
> the OSF deposits that state no licence, blank cells only. Its premise is that
> the deposit is *silent*, and when that is wrong the stopgap quietly publishes
> a weaker licence than the source grants -- 61 rows across eleven projects did,
> until #2302. Run
> [`metadata/check_osf_permission_projects.py`](metadata/check_osf_permission_projects.py)
> before adding an entry and whenever the list is touched; it asks the OSF API
> and exits non-zero on any project that publishes a licence. A project that
> does gets its value from `dictionary_auto.csv` and leaves the list (#2058).

> **Do not delete the rename in `metadata/tag_normalize.R`.** Its comment says to
> fix the sheet itself once the Sheets-write question is resolved, which reads as
> temporary. It is not. The rename is idempotent, and it also repairs rows entered
> without quoting that split on a value's internal comma. It stays even after
> someone cleans the sheet by hand.

## 4. How a dataset travels

```
paper / repository
      |
      v
data/<script>.R                      one script per dataset, self-contained
      |
      v
red_up  ------------------------->   a core Redivis shard
      |
      v
metadata/NN_*.R / NN_*.py            reads the shards + the Sheets + data/,
      |                              writes CSVs into metadata/
      v
red_up  ------------------------->   irw_meta, as a DRAFT version
      |
      v
   published by hand on Redivis
      |
      +--> irw_site      queries Redivis live at render time
      +--> Rpkg          irw_fetch() / irw_filter() / irw_metadata()
      +--> Python-pkg    irw.fetch() / irw.filter()
```

Two things about this are easy to get wrong:

**Everything scheduled is a GitHub Action.** There is no crontab anywhere, on
any machine. `.github/workflows/metadata-pipeline.yml` runs Mondays 13:00 UTC:
it regenerates the metadata CSVs, runs `audit_tables.R` (which cross-checks
table names across the metadata, tags and biblio outputs against the live
Redivis datasets), and opens a **pull request** with the diff. It does not open
an issue and does not auto-merge — there, the review is the product.

`metadata/weekly_pipeline_cron.sh`, the local entry point this replaced, was
deleted in #1940: nothing invoked it, its header described the run in the
present tense, and adding it to a crontab would produce a second, unreviewed
run against the same sheets. `git log -- metadata/weekly_pipeline_cron.sh` if
you need it.

See **section 6** for the full list of what runs on a schedule and where.

**Nothing uploads automatically.** No scheduled job ever uploads.
Every upload goes through one tool, [`red_up`](red_up/README.md), and it only
ever creates a *draft* Redivis version — Redivis keeps an unpublished working
copy that nobody outside the project can see until someone clicks publish. That
click is always a human action taken after reviewing a diff.

**Changes may sit in a draft for up to one week, and that is fine.** Releasing
after every upload is unmanageable, so batching is the norm and an unreleased
draft is a normal state rather than a loose end. **Live tables being somewhat
out of date is not a problem to panic about** — a corpus that is a few days
behind is a corpus working as intended.

Two things follow that are easy to get wrong:

- **Until the version is released, the upload has not happened** as far as
  anyone outside the project is concerned. `irw_fetch()`, `irw_itemtext()`,
  `irw_metadata()` and the site all read the *released* version. A script that
  reports a successful upload and a `count(*)` that matches has told you about
  the draft and nothing else.
- **The one thing that does not wait is a wrong answer.** The line is narrow,
  and it is not staleness: it is whether the released data would give someone a
  *wrong* result rather than an *incomplete* one. A table that is missing, or
  missing its newest rows, is incomplete — that waits happily. `irw#1816` is
  the other kind: three item text tables served every item twice with different
  text, so anything joining item text to responses fanned out 2x and returned
  answers that were not true of the data. Release that kind when it lands;
  batch everything else.

`python3 -m red_up.drafts` reports every dataset with unreleased changes and how
long the public corpus has been behind, exiting non-zero past the window. It
counts **time since the last released version**, because the two obvious clocks
both lie: a table's `updatedAt` resets for every table in the draft whenever the
draft is touched, and the draft version's own `createdAt` resets on each upload.

`red_up` replaced thirteen near-identical copies of one script, each hardcoding
a different dataset, so the destination used to be decided by which file you
happened to run. It reads the dataset list from `metadata/redivis_config.R`,
defaults by filename (`*__items.csv` → the newest item-text shard, otherwise the
newest core shard), checks every shard of both kinds for an existing table of the
same name before writing — because a copy in a newer shard *shadows* the older one
rather than replacing it — and verifies each table with a `count(*)` afterwards.
When a name is already in use somewhere that could not legally hold the file, it
stops rather than writing to a dataset of another kind.

`irw_site` builds its homepage hero numbers (`data/hero_stats.json`, untracked)
at render time from published irw_meta, in the pre-render step
`landing/hero_stats.R` (#1940; this used to be `metadata/09_hero_status.R`,
committed by hand).

**Some files in this repository's `main` are published the moment they merge.**
The site, both client packages and the MCP server read them over HTTPS from
`raw.githubusercontent.com/ben-domingue/irw/main/`, with no Redivis release in
between, so a merge to `main` is the release for these:

| File | Read by |
|---|---|
| `metadata/version_manifest.tsv` | site, Rpkg, Python-pkg |
| `metadata/aggregators.csv` | site, Rpkg |
| `metadata/table_changes.csv` | site (`corrections.qmd`) |
| `metadata/data_notes.csv` | site, MCP `get_processing_notes` |
| `metadata/column_docs.csv`, `metadata/covariate_labels.csv`, `metadata/codebook_links.csv` | site (table-page Codebook); the first and last also MCP `describe_columns`. The Python package and MCP read value labels from irw_meta's `covariate_labels`, so that one reaches them only after a release |
| `metadata/table_scripts.csv`, `data/` scripts, `processing_notes/` | MCP `get_processing_notes` |
| `itemtext/withdrawals.csv` | site (tombstone pages for withdrawn tables) |
| `datastandard.md` | site (the Codebook's column definitions, joined at render time) |

The list comes from grepping the three consumer repos for that URL; grep again
rather than trust it.

### The table-page Codebook

Each table page has a **Codebook** section saying what the table's columns
mean, and the MCP's `describe_columns` answers the same question (#2755,
#2763, #2766, #2770). Its three files are built separately and read from `main`
(table above). Each owner's header documents its columns; this only says which
file holds which fact.

| File | What it answers | Built by | When |
|---|---|---|---|
| `metadata/column_docs.csv` | Per (table, column): does `datastandard.md` define it, and which source column did the build script rename into it. The definition text is not copied: the page joins it from `datastandard.md` at render time | `metadata/14_column_docs.py` (stage 14) from `metadata.csv`'s `variables`, `table_scripts.csv` (stage 13) and the `data/` scripts. Core tables only: the other catalogues carry no column list | every pipeline run |
| `metadata/covariate_labels.csv` | What each code of a coded `cov_*` column means, using the source's own value labels verbatim (1 = hombre). Also an irw_meta table | `metadata/covariate_labels/harvest.py` re-runs `data/` scripts that read SPSS/Stata files, then `build.py` turns the logs into the CSV. Scripts the harvest cannot re-run are entered by hand in `manual.csv` (with `not_harvestable.tsv` recording them as checked); `institutions.csv` decides which code lists are withheld | **by hand** (section 6): it downloads sources, so it cannot run in CI |
| `metadata/codebook_links.csv` (+ `codebook_links_checked.csv`, what was swept) | A link to the source deposit's own codebook file, never a guess: `how_found` records the evidence | `metadata/find_codebook_links.py`. Stage 15 runs it `--new-only` on new tables; the wider crawls (#2787, #2792) are hand runs. `automated_finding/stage_dict_row.py --codebook-url` records a codebook a person found at ingest in `automated_finding/codebook_at_ingest.csv`, which it trusts first; `metadata/codebook_by_review.csv` does the same for statistics-office codebooks found by review (#2787 step 3) | weekly for new tables; by hand for crawls and reviews |

Two guards keep these honest. `metadata/check_label_harvest.py` runs in the
`contract` job and warns, without failing, when a PR's script reads a labelled
file and writes `cov_*` columns but has never been harvested. The page itself
says the Codebook is a best reconstruction, not the source's codebook. Which
link kinds the page shows, and in what order, is decided in `irw_site`'s
`landing/emit_landing_pages.R` (`source_codebook_html`). Kinds it does not
show, such as Dataverse DDI exports and READMEs that do not name the columns,
stay in the CSV for the MCP.

## 5. Which document wins

When two documents disagree, this is the order of precedence:

| Question | Authoritative source |
|---|---|
| Output schema, column names, file naming | [`datastandard.md`](datastandard.md) |
| Redivis owner and dataset names | `IRW_OWNER` / `IRW_CORE_DATASETS` in [`metadata/redivis_config.R`](metadata/redivis_config.R) — `red_up` parses this file rather than restating it |
| How anything gets uploaded to Redivis | [`red_up/README.md`](red_up/README.md) |
| Whether a table meets the standard | [`irw_validate`](irw_validate/README.md) — `datastandard.md` states the rules, `irw-validate` is the one thing that enforces them, and `red_up` will not upload a table it blocks |
| Redivis version hashes | Each client package's own config — this repo deliberately carries none |
| Which Redivis version of every dataset was live at a given time | [`metadata/version_manifest.tsv`](metadata/version_manifest.tsv) — written by `red_up.manifest` from Redivis' own version history, refreshed daily by the `version-manifest` GitHub Action (13:30 UTC), which opens and merges its own PR when the file changes and files an issue when it cannot. The R and Python packages read the committed copy over HTTPS, so the file in `main` *is* the published record. An IRW version number is a citation: rows are appended, never renumbered, and the writer refuses rather than change one |
| Which published tables were corrected, renamed or retired, and when | [`metadata/table_changes.csv`](metadata/table_changes.csv) — one row per table per released correction, appended by hand once the release is live (checklist in [`red_up/README.md`](red_up/README.md)); rendered by `irw_site`'s `corrections.qmd`, which also states the corrections policy (#2168). Response tables only: item-text caveats live on `itemtext_issues.qmd` and rights withdrawals stay internal |
| Caveats about a table's *source* that are not IRW defects (a doubtful source key, what a column means, pooled forms) | [`metadata/data_notes.csv`](metadata/data_notes.csv): hand-appended, rendered as a plain Notes section on landing pages (no banner, no `noindex`) and returned by the MCP's `get_processing_notes` (#2529). IRW defects awaiting a fix are `irw_site`'s `landing/known_issues.tsv`; released fixes are `table_changes.csv` |
| Tag vocabulary for `sample` and `construct type` | `TAG_VOCAB` in [`metadata/tag_normalize.R`](metadata/tag_normalize.R) — enforced; the pipeline halts on an unknown value |
| Which sources have tags | `.irw_tag_sources` in `Rpkg/R/redivis-config.R` |
| Metadata pipeline run order | `DEFAULT_ORDER` in `.claude/skills/irw-site-update/scripts/run_pipeline.sh` — the order actually executed |
| Automated-finding procedure | `automated_finding/.claude/skills/irw-automated-finding/SKILL.md` over `automated_finding/README.md`; `automated_finding/BATCH_LOG.md`'s latest notes override both on workflow specifics |
| Item text schema, and the administered-language rules | [`itemtext/.claude/skills/irw-auto-itemtext/references/itemtext_standard.md`](itemtext/.claude/skills/irw-auto-itemtext/references/itemtext_standard.md), which mirrors the public page at `itemresponsewarehouse.org/itemtext.html`. It beats the automated-finding SKILL.md, which runs item text extraction at its Step 3.5 but does not own the schema |
| Provenance vocabularies for item text (`translation_source`) | [`itemtext/provenance_vocab.csv`](itemtext/provenance_vocab.csv) — enforced by `itemtext/check_provenance.R`, the way `TAG_VOCAB` is enforced for tags. SKILL.md and `itemtext/language_backfill/README.md` say when to reach for each value, never what the values are |
| Item text *extraction judgment* (what goes in `instructions` vs `section_prompt`, when to leave a field blank) | Step 4 of `itemtext/.claude/skills/irw-auto-itemtext/SKILL.md` |
| Dataset descriptions and licenses | The per-source dictionary Sheet, by convention — no document claims this in writing |
| What kind of work to do next, and what not to | [`PRIORITIES.md`](PRIORITIES.md) — advisory, and ben-domingue overrules it. `CLAUDE.md`'s "Processing Priorities" answers the narrower question of which *dataset* to pick |

Two entries deserve their reasoning stated, because both are counter-intuitive:

**The run order points at a shell script, not at prose.** Four files used to
restate the pipeline order, and by 2026-10 every copy was wrong. They now point
at `DEFAULT_ORDER` instead. `run_pipeline.sh` is the one that runs, so it wins by
construction — which is the point of rule 2 below.

**The version manifest is a record, not a plan.** It says what *was* released,
never what is about to be. `red_up` only ever writes an unreleased draft and
publishing is a human action, so nothing an upload does appears in the manifest
until the version is actually released and the next daily run sees it.

## 6. What runs on a schedule

Inventoried and settled in #1940 (2026-09-08); workflow table re-read from `.github/workflows/` 2026-10-03. Everything on a clock runs on one
of two runners — **GitHub Actions** and **Claude cloud routines**. Nothing runs
from a crontab: `crontab -l` was empty and no systemd timer referenced the
project when this was written (checked on the maintainer's machine, which is the
only one that ever had an entry).

Work that is deliberately *hand-run* rather than scheduled is listed at the end
of this section — that is a third way things happen, but it is not a runner.

### GitHub Actions, `ben-domingue/irw`

| Workflow | When (UTC) | What it does | Merges? |
|---|---|---|---|
| `metadata-pipeline.yml` | Mon 13:00 | the metadata CSVs: every stage in `DEFAULT_ORDER` (section 5) | opens a PR, **never** auto-merges — the review is the product |
| `version-manifest.yml` | daily 13:30 | records newly *released* Redivis versions | opens a PR and **squash-merges it**, because it only records what already happened |
| `itemtext-issues.yml` | daily 13:45 | refreshes `itemtext/live_tables.csv`; fails when a live table's triage note never reached the public item-text issues page (#2236) | opens and **squash-merges** its own snapshot PR, like the manifest |
| `drift-report.yml` | daily 14:00 | reports what downstream is behind | writes no code; rewrites issue #2085 in place |
| `tests.yml` | every PR, and every push to `main` | the test suites, config parity, the R smoke tests, and the `contract` job (validator gate plus the advisory label-harvest check) | — |
| `release-irw-validate.yml` | on a pushed `irw-validate-v*` tag | publishes `irw_validate/` to PyPI as `irw-validate` (Trusted Publishing; procedure in the file's header) | — |
| `To Do.yml`, `In Progress.yml`, `Under Review.yml` | on issue and comment events | move issue cards on the `ben-domingue` user project board (`PROJECTS_TEST` secret) | — |

The daily times are staggered so that the drift report reads the manifest the
13:30 job refreshed.

### GitHub Actions, `datapages/irw` (the Quarto site)

| Workflow | When (UTC) | What it does |
|---|---|---|
| `quarto_publish.yaml` | `workflow_dispatch`, **and** every 3 h at :17 (datapages/irw#205) | renders and publishes to `gh-pages`; the scheduled run first checks whether `main` has moved since the last publish and skips if not; one publish at a time (`concurrency`) |

The scheduled run watches *that repository only*. Pages query Redivis live at
render time, so a new `irw_meta` release changes what the site would say without
changing anything in the repo — that direction is reported by `drift-report.yml`,
never rendered automatically, because a render that races a publish republishes
the old numbers into every page (2026-08-24).

### Claude cloud routines

Read from the routines API on 2026-09-08, when, of the 20 most recently created
routines, exactly two were enabled and the other 18 were fired one-shot PR
check-ins. The third row was added later. Whether each is enabled *today* is not
recorded here, because it is toggled from the routines page; read it there.

| Routine | id | When (UTC) |
|---|---|---|
| IRW morning status render | `trig_01JAY3UEYPP4EQLt93erbFE9` | `27 11 * * *` (04:27 PT) |
| IRW daily search nudge | `trig_014YcLgR2Sa2D8P2yAkvQFTx` | `0 15 * * *` (08:00 PT) |
| IRW Monthly Discovery — Repos (full sweep + triage) | `trig_01NT4fqYRrf7nRemLN3fAZm4` | `0 21 2 * *` (2nd of month, 21:00); prompt rewritten 2026-10-02 (runs/ never committed, --retriage, GitHub MCP not gh) |

> **This table is not the whole account, and cannot be made so from here.** The
> API's `list` returns the newest 20 with `has_more: true`, and passing its
> `next_cursor` back returns *the identical page* — verified 2026-09-08, so the
> cursor is accepted and ignored. The oldest routine visible was created
> 2026-08-25; the standing weekly/monthly discovery sweeps (repos / PLOS / PMC)
> were created ~2026-08-13/14 and therefore fall outside the window. **Their
> existence and schedule cannot be confirmed or denied from a session** — read
> them at https://claude.ai/code/routines. That is what still blocks "thin the
> standing weekly discovery routines" in `automated_finding/TODO.md`.

Two one-shot PR watchers (`trig_01UfLcQ11WAtgNEgyR6Yp5WF`,
`trig_0184pheJDQbsY8tBE1uPkY7S`) re-armed hourly from 2026-08-24 before anyone
noticed, and were disabled. That is the argument for recording an id here the
day a routine is created: a routine nobody can name is a routine nobody can
stop, and the API will stop showing it after twenty more exist. Routines cannot
be deleted from a session — https://claude.ai/code/routines.

### What is deliberately NOT scheduled

- **`upload_meta.py`, and the Publish click.** Section 4: that click is always a
  human action. `drift-report.yml` reports when the warehouse has fallen behind
  the repository; it never publishes.
- **Merging the weekly pipeline PR.** The diff is the thing to read on Monday.
- **Item-text extraction rounds**, and the discovery sweeps above.
- **`covariate_labels.csv`** (#1775), irw_meta's codebook for coded covariates.
  `metadata/covariate_labels/harvest.py` re-runs the `data/` scripts that read
  SPSS/Stata files, which download from OSF, Zenodo and the like, and a few
  read files that exist only on one machine; that does not belong in CI.
  Re-run it, then `build.py`, when a script shipping coded covariates changes.

## 7. Where things go inside a directory

Each working directory (`automated_finding/`, `itemtext/`, `metadata/`, `tags/`)
keeps live scripts and standing records at its top level, and anything that is
only kept for the record goes into a subfolder:

| Subfolder | Holds |
|---|---|
| `archive/` | Finished workstreams, one-time reports, spent one-off scripts. Nothing that runs reads them |
| `logs/`, `pipeline_logs/`, `runs/` | Output a run writes for review (`runs/` is gitignored and can be thrown away) |
| topic folders (`automated_finding/leads/`, `automated_finding/naming_audit/`, `automated_finding/itemtext_verification/`, `tags/age_range/`, `tools/withdrawals/`) | Everything for one job or one kind of record together, with a README naming whatever reads it by path |

The directory's own README has the full layout. Before moving a file, `git grep`
its path. Scripts, skills, workflows and provenance records cite files by
path, and some readers skip a missing file without saying so (`03_tags.R`'s
`file.derived`). History docs such as `automated_finding/BATCH_LOG.md` and
`itemtext/extraction_batches/round_log.md` keep the
path the file had when they were written.

## 8. The rest of the tree

Sections 2–7 cover the pipeline. The other top-level entries, briefly; each
directory's README (where there is one) goes further:

| Path | What it is |
|---|---|
| `data/` | One script per dataset (R, Python, Stata). Subfolders group scripts by data family or by group: `competitions/`, `nominal/`, `simsyn/`, `conjoint/` for the four families other than core; `trials/` for trial-level sports tables; `gilbert_hte/` for the IL-HTE `gilbert_meta_*` series; `pisa/` for PISA; `tests/` for the CI checks on the ENEM scoring helpers. Older top-level scripts predate the naming rule in `datastandard.md` and keep their names, because `metadata/table_scripts.csv` and the MCP find scripts by path |
| `audit/2401/` | The #2401 retroactive corpus audit: `RULES.md` (the audit's frozen rules), detectors, pilot and sample dossiers, triage and repair builders. A workstream folder, not a pipeline stage |
| `tools/withdrawals/`, `tools/repairs/` | One already-run script per withdrawal or one-off repair, kept because provenance records cite them by path. `tools/withdrawals/ledger.py` is the live part: withdrawal scripts call it to append to `itemtext/withdrawals.csv` |
| `collections/` | `registry.csv` and `curated/` are the data `10_collections.R` reads (#1633); `scout_instruments.py` and `presort_instruments.py` propose curated members for human review |
| `irw_validate/` | The validator (section 5). A separate PyPI distribution with its own `pyproject.toml`, released by tag (section 6). `misc/validate_irw.R` is its R twin for contributors without Python; a CI test keeps the two in step through `# @check` markers |
| `red_up/`, root `pyproject.toml` | The uploader (section 4). The root `pyproject.toml` packages only `red_up`, so `pip install -e .` gives the `red_up` command |
| `irw_secrets.py` | The one place a write-scoped Redivis token is resolved. Anything that writes to Redivis imports it rather than reading the environment itself |
| `redivis_shim.py` | A patch that makes whole-table reads work under redivis 0.20.11 with urllib3 2.x. Its docstring says when to remove it |
| `.claude/skills/` | `irw-site-update` (the metadata pipeline) and `irw-vignette` live here. `irw-auto-itemtext`, `irw-automated-finding` and `irw-auto-tag` are **symlinks** into `itemtext/`, `automated_finding/` and `tags/`, so edit them there |
| `processing_notes/` | Processing and licensing guidance, `validator_overrides.csv` (read by the MCP), outreach letters and per-table metadata-repair notes |
| `manuscript_src/`, `training/`, `misc/` | Frozen analysis code for the 2025 BRM paper, workshop materials, and small R utilities |

## Two rules

**1. A fact lives in exactly one place; everything else links to it.**
`tags/.claude/skills/irw-auto-tag/references/vocab.md` is the model: rather than listing the
tag vocabulary, it says `TAG_VOCAB` in `tag_normalize.R` is authoritative. The
two therefore cannot disagree.

**2. Prefer documentation that cannot go stale.** The tag vocabulary is enforced
by code that halts the pipeline on a bad value. That is worth more than any
number of paragraphs saying which values are allowed. Where a rule can be made
executable, make it executable instead of writing it down.

These are not aspirations. Writing this file in August 2026 turned up nine
defects, filed as ben-domingue/irw#1729–#1733, datapages/irw#104–#105 and
itemresponsewarehouse/Python-pkg#9–#10. Two were not documentation at all: the
Python client could not reach one of the sources, and nothing had noticed.

The pattern is old. The rule that dataset searches must run in nine languages
rather than English alone was silently dropped for three rounds of discovery
before anyone caught it — because the instruction lived in two places and the
copies drifted apart.

**Rule 1 needs a corollary: say which document owns a rule that spans two of
them.** On 2026-09-01 the item text schema gained the administered-language
columns, and the automated-finding SKILL.md went on telling its Step 3.5 to
*skip* any table whose wording existed only as "a translated substitute" — a
rule that had been correct a day earlier and now contradicted the schema. It
would have discarded seven correctly-extracted tables.

The near miss is instructive because rule 1 *was* being followed. That file has
a section headed "Schema and extraction rules — do not restate them here",
which explicitly delegates to `itemtext_standard.md` and says it "deliberately
does not fork a second copy". The stale bullet sat a few lines above it, in a
list about *triage* — whether extracting is cheap enough to do now. Nobody
classified "is a translation acceptable?" as a schema question, so it was never
covered by the delegation, and the commits that changed the schema
(`1331807`, `f43a1c4`) touched only `itemtext/` and never looked outside it.

So: a rule that reads as procedure in one file and as schema in another has two
plausible owners and will drift. Name the owner in the authority table above —
item text now has two rows there for exactly this reason — and when you change
a rule, grep the whole repo for it rather than the directory you are working
in.
