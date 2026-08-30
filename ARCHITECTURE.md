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
| `Rpkg` | `itemresponsewarehouse/Rpkg` | The `irw` **R** package (v1.0.1) |
| `Python-pkg` | `itemresponsewarehouse/Python-pkg` | The `irw` **Python** package (v0.0.2) |

`src` is on a personal account, the site on `datapages`, and the two client
packages on the `itemresponsewarehouse` org. There is no technical reason for
this; it is history. Neither package is on CRAN or PyPI — both install from
GitHub.

## 2. Redivis

All data lives on Redivis under the account **`datapages`**. Everything else in
this repository reads that from one place:

> `IRW_OWNER`, `IRW_CORE_DATASETS` and `IRW_AUX_DATASETS` in
> [`metadata/redivis_config.R`](metadata/redivis_config.R) are authoritative for
> the owner and the dataset names.

**Core shards** hold the response data. A *shard* here is simply one of several
Redivis datasets with identical structure, named `item_response_warehouse`,
`item_response_warehouse_2`, and so on — a new one is added whenever the warehouse
outgrows the last. Which shard a given table is in is not predictable
from its name, so the client packages search them **newest-first** and return the
first match — meaning a name present in more than one shard resolves to its most
recent copy.

**Auxiliary datasets** hold everything that is not response data: `irw_meta` (all
metadata, biblio, tags and collections tables), `irw_text` (item text), plus one
each for the `simsyn`, `competitions` and `nominal` sources.

How many of each exist today is *not* recorded here, deliberately — that number
grows, and a count written into prose is wrong the day it changes. `redivis_config.R`
is the answer:

```r
source("metadata/redivis_config.R"); IRW_CORE_DATASETS; IRW_AUX_DATASETS
```

Until August 2026 all of this lived under the personal Redivis account
`bdomingu`. Redivis resolves references to a previous owner automatically, so
older scripts still work.

> **Known hazard.** The dataset identifiers are duplicated in three files:
> `metadata/redivis_config.R` here, `R/redivis-config.R` in `Rpkg`, and
> `src/irw/config.py` in `Python-pkg`. All three describe themselves as a single
> source of truth. They are reconcilable — this repo carries plain dataset
> *names*, the two packages additionally carry version *hashes* — but a new shard
> must be added in all three, and nothing currently checks that they agree. They
> have already drifted once (#1733).

## 3. Google Sheets

These Google Sheets are load-bearing. They are the human entry surface for
metadata that is not derivable from the data itself:

| Sheet | What it holds |
|---|---|
| Data Dictionary — core | Descriptions, origins, licenses, references. Read by `metadata/02_biblio.R` and eight other call sites |
| Data Dictionary — competitions, nominal, simsyn | The same, one per non-core source |
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

The two sheets differ in how automated rows reach them, and this asymmetry is
historical rather than designed:

- **Tags** — automated rows land in a git-tracked CSV. On export, `03_tags.R`
  concatenates it with the sheet's rows and drops any automated row for a table a
  human has already tagged, so a human entry always wins (#1723).
- **Dictionary** — automated rows are produced by a per-batch script in
  `automated_finding/` and pasted in by hand. Proposed for the same treatment in
  #1732, queued behind the tags work.

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
upload.py  ---------------------->   a core Redivis shard
      |
      v
metadata/01..10_*.R                  reads the shards + the Sheets,
      |                              writes CSVs into metadata/
      v
upload_meta.py  ------------------>  irw_meta, as a DRAFT version
      |
      v
   published by hand on Redivis
      |
      +--> irw_site      queries Redivis live at render time
      +--> Rpkg          irw_fetch() / irw_filter() / irw_metadata()
      +--> Python-pkg    irw.fetch() / irw.filter()
```

Two things about this are easy to get wrong:

**The weekly run is a system crontab entry, not a GitHub Action.**
`metadata/weekly_pipeline_cron.sh` runs Mondays at 06:00 on a maintainer's
machine, regenerates the metadata CSVs, runs `audit_tables.R` (which cross-checks table
names across the metadata, tags and biblio outputs against the live Redivis
datasets), and opens a GitHub issue with the log.

**Nothing uploads automatically.** The cron job deliberately never runs
`upload_meta.py`. When `upload_meta.py` is run, it only ever creates a *draft*
Redivis version — Redivis keeps an unpublished working copy that nobody outside
the project can see until someone clicks publish. That click is always a human
action taken after reviewing a diff.

`irw_site` also reads one file directly off disk rather than from Redivis:
`data/hero_stats.json`, written into that repository by `metadata/09_hero_status.R`.

## 5. Which document wins

When two documents disagree, this is the order of precedence:

| Question | Authoritative source |
|---|---|
| Output schema, column names, file naming | [`datastandard.md`](datastandard.md) |
| Redivis owner and dataset names | `IRW_OWNER` / `IRW_CORE_DATASETS` in [`metadata/redivis_config.R`](metadata/redivis_config.R) |
| Redivis version hashes | Each client package's own config — this repo deliberately carries none |
| Tag vocabulary for `sample` and `construct type` | `TAG_VOCAB` in [`metadata/tag_normalize.R`](metadata/tag_normalize.R) — enforced; the pipeline halts on an unknown value |
| Which sources have tags | `.irw_tag_sources` in `Rpkg/R/redivis-config.R` |
| Metadata pipeline run order | `DEFAULT_ORDER` in `.claude/skills/irw-site-update/scripts/run_pipeline.sh` — the order actually executed |
| Automated-finding procedure | `automated_finding/.claude/skills/irw-automated-finding/SKILL.md` over `automated_finding/README.md`; `automated_finding/BATCH_LOG.md`'s latest notes override both on workflow specifics |
| Dataset descriptions and licenses | The per-source dictionary Sheet, by convention — no document claims this in writing |

Two entries deserve their reasoning stated, because both are counter-intuitive:

**The run order points at a shell script, not at prose.** Three files describe
the pipeline order and they do not agree. `run_pipeline.sh` is the one that runs,
so it wins by construction — which is the point of rule 2 below.

**`datastandard.md` beats `CLAUDE.md` on output format.** `CLAUDE.md` says
scripts write both `.csv` and `.RData`; `datastandard.md` overrides this to
CSV-only for the `automated_finding` pipeline, and says so explicitly.

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
