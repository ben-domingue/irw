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

## IRW Data Format (The "Commandments")

All processed datasets must conform to this schema:

| Column | Required | Description |
|--------|----------|-------------|
| `id` | yes | Person identifier |
| `item` | yes | Item identifier |
| `resp` | yes | Response value |
| `cov_*` | no | Covariates (demographic/background) — always prefixed `cov_` |

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

## Key Conventions

- **R** is the primary language; heavy use of `dplyr`/`tidyr` (tidyverse). Python is used for the Streamlit app and some newer scripts. Stata (`.do`) files handle some complex datasets.
- Data scripts in `data/` are self-contained — they read raw inputs and write IRW-formatted outputs. Do not introduce shared dependencies between scripts.
- The Redivis API is used to upload metadata tables. Credentials are managed externally (not in this repo).
- Branch PRs reference GitHub issue numbers (e.g., `#253` in commit messages).
