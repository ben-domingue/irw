# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Item Response Warehouse (IRW)** is a large-scale open-source repository that standardizes and aggregates item response datasets to facilitate psychometric research. Published in *Behavior Research Methods* (2025). Data lives on Redivis; this repo contains the processing pipeline.

**Start with [`ARCHITECTURE.md`](ARCHITECTURE.md)** — which repo owns what, where
the data lives, and which document is authoritative when two disagree.

## Running Things

**Metadata pipeline.** `metadata/` holds numbered R and Python stages, and
numeric order is *not* run order. Do not invent a sequence — run the wrapper, which is
authoritative because it is the thing that actually executes:

```bash
.claude/skills/irw-site-update/scripts/run_pipeline.sh        # every stage in DEFAULT_ORDER
.claude/skills/irw-site-update/scripts/run_pipeline.sh 01 03  # just metadata.csv + tags.csv
```

It snapshots each stage's CSVs before and after so `diff_csv.py` can report what
changed. `04_tables.R` (QC) is deliberately excluded — superseded by
`audit_tables.R`; the old `09_hero_status.R` is retired (the site builds the hero
from published irw_meta, #1940), so there is no stage 09. Nothing here uploads to Redivis: uploading is a separate,
manual step, and it only ever writes a draft version for a human to publish.
One tool does every upload — `red_up` (see `red_up/README.md`); the metadata
CSVs go up with `upload_meta.py`, which is a thin wrapper around it.

**Individual data processing scripts** are run standalone — there is no central build system. Scripts live in `data/` and are executed one at a time to convert raw datasets.

## Repository Structure

- **`data/`** — Per-dataset processing scripts (R, Python, Stata), one per dataset. Each converts raw data into IRW format and is self-contained. Branch naming convention: `username/dataset_identifier`.
- **`metadata/`** — Numbered R and Python stages that regenerate the metadata, biblio, tags, item text, collections and Codebook CSVs (ARCHITECTURE.md §4). Uploading them is a separate manual step (see above).
- **`irw-dataset-builder/`** — Streamlit app for building IRW-formatted datasets interactively (`streamlit run irw-dataset-builder/main.py`). Dormant since 2025-02; it predates `irw_validate`.
- **`itemtext/`** — Scripts for extracting and uploading item text content.
- **`manuscript_src/`** — Reproducible analysis scripts for the IRW paper.
- **`misc/`** — Small R utilities, and `validate_irw.R`, the R twin of `irw_validate`.
- **`tags/`** — Tagging data with human annotators.
- **`collections/`** — Curated groupings of tables (`registry.csv` + `curated/`), read by `metadata/10_collections.R`.
- **`training/`** — Workshop and training materials.
- **`processing_notes/`** — Data processing guidelines and licensing docs.
- **`red_up/`** — The single Redivis uploader. **`irw_validate/`** — The format validator used to gate a table before upload.
- **`tools/withdrawals/`**, **`tools/repairs/`** — One already-run script per table withdrawal or one-off repair, cited by path in provenance records.
- **`audit/2401/`** — The #2401 retroactive corpus audit (rules, detectors, dossiers).
- **`automated_finding/`** — Automated pipeline that discovers, triages, and
  standardizes candidate datasets from public repositories (Dataverse,
  Figshare, OSF, Zenodo, Dryad). See its
  `.claude/skills/irw-automated-finding/SKILL.md` for orchestration and
  `README.md` for the script/column reference.

Inside `automated_finding/`, `itemtext/`, `metadata/` and `tags/`, the top level holds
live scripts and standing records. Finished work goes into `archive/`, `logs/` or a
topic folder: see ARCHITECTURE.md §7 and each directory's README. `git grep` a
file's path before moving it.

## IRW Data Format (The "Commandments")

The full schema, column order, file naming, and step-by-step conversion
guidance live in **`datastandard.md`** at the repo root — that file is the
single source of truth for output format across every script in `data/` and
the `automated_finding/` pipeline. Read it before writing a processing
script. Quick reference for the required columns:

| Column | Required | Description |
|--------|----------|-------------|
| `id` | yes | Person identifier |
| `item` | yes | Item identifier |
| `resp` | yes | Response value — numeric, at least ordinal (continuous/slider responses are also acceptable — see `datastandard.md`) |
| `wave` | no | Longitudinal timepoint (pre/during/post, or numeric order) — its own column, never `cov_wave` |
| `cov_*` | no | Covariates (demographic/background) — always prefixed `cov_` |

`datastandard.md` also covers less-common columns (`itemcov_*`, `treat`,
`rt`, `date`, `qmatrix*`, `rater`, `item_family`) and edge cases
(multi-scale files, sentinel/missing codes, opaque item labels, etc.) not
repeated here.

Additional rules:
- **Long format only** — one row per person-item observation
- Each measurement scale is saved as a **separate file**
- Response times in **seconds**
- Longitudinal timestamps in **Unix time**
- Output saved as both `.csv` and `.RData` — except the `automated_finding`
  pipeline, where `datastandard.md` overrides this (CSV only)

## Typical Processing Script Pattern

```r
# 1. Load raw data
d <- read.csv("raw/dataset.csv")

# 2. Rename/clean columns to IRW schema
d <- d %>% rename(id = SubjectID, resp = Score)

# 3. Rename covariates with cov_ prefix
d <- d %>% rename(cov_age = Age, cov_gender = Gender)

# 4. Pivot to long format
d <- d %>% pivot_longer(cols = starts_with("item"), names_to = "item", values_to = "resp")

# 5. Save
write.csv(d, "output/dataset.csv", row.names = FALSE)
save(d, file = "output/dataset.RData")
```

Python scripts follow the same logic using `pandas.melt()` instead of `pivot_longer()`.

## Processing Priorities

**This section is about which *dataset* to process next. For which *kind of work*
to do at all — corpus trust before gates before reach before volume — see
[`PRIORITIES.md`](PRIORITIES.md).**

Full guidance: `processing_notes/DataProcessingInstructions.md`. Summary:

- The goal is not to empty the queue — it's to maximize data in the IRW. There will always be more incoming, so use time on what grows the IRW most rather than rushing to clear the backlog.
- Before processing a dataset raised in a GitHub issue: check the [dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s) for an existing duplicate, and prioritize by format quality and data volume — a messy, small (e.g. ~150-respondent), unpublished dataset can wait.
- **License must be explicitly and verifiably open**, confirmed on the source page. The exact rule, including its narrow non-commercial exception, is in `datastandard.md`'s "Before you start". Unknown/missing license, or a platform UUID that doesn't resolve to a named open license → skip; don't write a processing script speculatively. If unsure, email the author for permission using the template in `processing_notes/Licensing.txt`, but don't process until permission or updated license terms are confirmed.
- Ask clarifying questions before processing rather than guessing on an ambiguous dataset; move on to the next one while waiting on an answer instead of blocking.

## Key Conventions

- `data/` scripts are R (tidyverse) or Python (pandas); most new scripts, including everything `automated_finding` writes, are Python. Stata (`.do`) files handle some complex datasets. The metadata pipeline is mostly R, with Python stages.
- Data scripts in `data/` are self-contained — they read raw inputs and write IRW-formatted outputs. Do not introduce shared dependencies between scripts.
- Every Redivis upload goes through `red_up`. The write-scoped token is resolved in one place, `irw_secrets.py`; the token itself is never in this repo.
- Branch PRs reference GitHub issue numbers (e.g., `#253` in commit messages).
