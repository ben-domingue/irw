# IRW

The **Item Response Warehouse (IRW)** is an open-source repository that
standardizes and aggregates item response datasets to advance psychometric
research. This repository (`ben-domingue/irw`, referred to internally as `src`)
holds the processing pipeline: the per-dataset conversion scripts, the metadata
pipeline, item text extraction, tagging, and automated dataset discovery. The
data itself lives on Redivis.

**New here? Read [`ARCHITECTURE.md`](ARCHITECTURE.md)** — which repository owns
what, where the data lives, and which document is authoritative when two
disagree.

## IRW menu

| | |
|---|---|
| [IRW website](https://itemresponsewarehouse.org) | Overview, browsable dataset list, standards, vignettes |
| [IRW paper](https://doi.org/10.3758/s13428-025-02796-y) | *Behavior Research Methods* (2025) — data format, inclusion criteria, and where we're going ([preprint](https://osf.io/preprints/psyarxiv/7bd54)) |
| [IRW data on Redivis](https://redivis.com/datapages) | Every dataset, under the `datapages` account |
| [IRW data dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit?gid=0#gid=0) | Descriptions, origins, and licenses of the processed datasets |
| [Processing code](data/) | One self-contained script per dataset |
| [Project map](ARCHITECTURE.md) | Repositories, Redivis layout, Google Sheets, document precedence |
| **Contact** | itemresponsewarehouse@stanford.edu |

## Getting the data

The easiest access is through the client packages. Both authenticate against
Redivis in the browser on first use.

**R:**
```r
remotes::install_github("itemresponsewarehouse/Rpkg")
library(irw)
irw_fetch("agn_kay_2025")
```

**Python:**
```bash
python -m pip install "git+https://github.com/itemresponsewarehouse/Python-pkg.git"
```
```python
import irw
irw.fetch("agn_kay_2025")
```

Worked examples for both live on the site's
[Getting Started](https://itemresponsewarehouse.org/getstarted.html) page.

## What's in this repository

| Directory | Contents |
|---|---|
| `data/` | Per-dataset processing scripts (R, Python, Stata) — one per dataset, self-contained, no shared dependencies |
| `metadata/` | Numbered R scripts that regenerate the metadata, biblio, tags, item text and collections CSVs uploaded to Redivis |
| `automated_finding/` | Pipeline that discovers, triages, and standardizes candidate datasets from public repositories |
| `itemtext/` | Extraction and upload of instrument, section, item, and response-option text |
| `tags/` | Human and automated tagging of tables |
| `collections/` | Curated groupings of tables |
| `irw-dataset-builder/` | Streamlit app for interactively building an IRW-formatted dataset (`streamlit run irw-dataset-builder/main.py`) |
| `manuscript_src/` | Reproducible analysis code for the IRW paper |
| `misc/`, `training/`, `processing_notes/` | Utility functions, workshop materials, and processing guidance |

Run order for the metadata pipeline is defined by
`.claude/skills/irw-site-update/scripts/run_pipeline.sh`, which is authoritative
because it is the thing that actually runs. Nothing in this repository uploads to
Redivis automatically; every publish is a human action.

## The data standard

[`datastandard.md`](datastandard.md) is the single source of truth for the output
schema, column order, and file naming — read it before writing a processing
script. The published version is at
[itemresponsewarehouse.org/standard.html](https://itemresponsewarehouse.org/standard.html).
The essentials:

- **Long format only**: one row per person-item observation, saved as CSV.
- **Required columns**: `id` (focal unit), `item` (item identifier), `resp`
  (numeric, at least ordinal). Continuous responses are fine; composites and
  imputed values are not.
- **Optional columns** carry fixed names: `wave`, `treat` (1/0), `rt` (seconds),
  `date` (seconds), `rater`, `item_family`, `qmatrix*`, plus `cov_*` for
  person-level and `itemcov_*` for item-level covariates. Never invent a variant
  such as `cov_wave` or `treatment`.
- **One file per scale.** A raw file holding a depression scale and an anxiety
  scale becomes two output files.
- **Naming**: `authorname_year_construct.csv`, lowercase, 40 characters or fewer.

`datastandard.md` also covers the cases this list skips — multi-scale files,
sentinel and missing codes, merged samples, opaque item labels — and it overrides
`CLAUDE.md` wherever the two disagree on output format.

## Adding to the IRW

Before writing any code, check the dataset against the inclusion criteria in
[`datastandard.md`](datastandard.md#before-you-start): an explicitly open license
(CC0, CC BY, or CC BY-SA, confirmed on the source page — a missing license or an
unresolvable UUID means stop), no existing copy in the dictionary, and at least
100 unique respondents. `processing_notes/DataProcessingInstructions.md` explains
how to prioritize among the datasets that pass.

Then:

1. **Open a GitHub issue** describing the decisions you had to make, and attach
   the data in IRW format. If the data cannot be shared publicly, email us
   instead.
2. **Submit a pull request** with the script that produced it, into
   [`data/`](data/) — against the main branch of this repository, not your fork.
3. **Update the [data dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s/edit#gid=0)**
   with the description, origin, and license.

Our queue of datasets awaiting processing is in
[the issue tracker](https://github.com/ben-domingue/irw/issues). Each has had some
initial vetting, but further investigation frequently turns up a problem — so ask
questions before processing rather than guessing, and move on to the next dataset
while you wait for an answer.

For contributing data you collected yourself, see
[itemresponsewarehouse.org/contribute.html](https://itemresponsewarehouse.org/contribute.html)
or just get in touch at itemresponsewarehouse@stanford.edu.
