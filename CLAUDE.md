# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Item Response Warehouse (IRW)** is a large-scale open-source repository that standardizes and aggregates item response datasets to facilitate psychometric research. Published in *Behavior Research Methods* (2025). Data lives on Redivis; this repo contains the processing pipeline.

## Running Things

**Streamlit dataset builder:**
```bash
streamlit run irw-dataset-builder/main.py
```

**Metadata pipeline** (run in order):
```bash
Rscript metadata/01_metadata.R
Rscript metadata/02_biblio.R
Rscript metadata/03_tags.R
Rscript metadata/04_tables.R
```

**Individual data processing scripts** are run standalone — there is no central build system. Scripts live in `data/` and are executed one at a time to convert raw datasets.

## Repository Structure

- **`data/`** — 500+ per-dataset processing scripts (R, Python, Stata). Each converts raw data into IRW format. Branch naming convention: `username/dataset_identifier`.
- **`metadata/`** — Numbered R scripts that maintain and upload dataset metadata to Redivis.
- **`irw-dataset-builder/`** — Streamlit web app for interactively building IRW-formatted datasets. Modular tabs in `tabs/`, shared components in `components/`, helpers in `utils/`.
- **`itemtext/`** — Scripts for extracting and uploading item text content.
- **`manuscript_src/`** — Reproducible analysis scripts for the IRW paper.
- **`misc/`** — Utility R functions (reliability, psychometric models).
- **`tags/`** — Tagging data with human annotators.
- **`training/`** — Workshop and training materials.
- **`processing_notes/`** — Data processing guidelines and licensing docs.
- **`automated_finding/`** — Automated pipeline that discovers, triages, and
  standardizes candidate datasets from public repositories (Dataverse,
  Figshare, OSF, Zenodo, Dryad). See its
  `.claude/skills/irw-automated-finding/SKILL.md` for orchestration and
  `README.md` for the script/column reference.

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
- Output saved as both `.csv` and `.RData`

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

Full guidance: `processing_notes/DataProcessingInstructions.md`. Summary:

- The goal is not to empty the queue — it's to maximize data in the IRW. There will always be more incoming, so use time on what grows the IRW most rather than rushing to clear the backlog.
- Before processing a dataset raised in a GitHub issue: check the [dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s) for an existing duplicate, and prioritize by format quality and data volume — a messy, small (e.g. ~150-respondent), unpublished dataset can wait.
- **License must be explicitly and verifiably open** (cc0, cc-by, cc-by-sa, or equivalent) confirmed on the source page. Unknown/missing license, or a platform UUID that doesn't resolve to a named open license → skip; don't write a processing script speculatively. If unsure, email the author for permission using the template in `processing_notes/Licensing.txt`, but don't process until permission or updated license terms are confirmed.
- Ask clarifying questions before processing rather than guessing on an ambiguous dataset; move on to the next one while waiting on an answer instead of blocking.

## Key Conventions

- **R** is the primary language; heavy use of `dplyr`/`tidyr` (tidyverse). Python is used for the Streamlit app and some newer scripts. Stata (`.do`) files handle some complex datasets.
- Data scripts in `data/` are self-contained — they read raw inputs and write IRW-formatted outputs. Do not introduce shared dependencies between scripts.
- The Redivis API is used to upload metadata tables. Credentials are managed externally (not in this repo).
- Branch PRs reference GitHub issue numbers (e.g., `#253` in commit messages).
