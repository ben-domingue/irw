# IRW Automated Finding Pipeline

Automated tools for finding, screening, and standardizing datasets for the IRW.
The pipeline has **two distinct steps** with different people and cadences in mind.

---

## Step 1 — Find and triage candidates

**Who:** Anyone with Python and internet access.
**When:** Periodically, or when targeting a new domain/instrument.
**Output:** A CSV ranking candidates by how cleanly they map to IRW format.

```bash
# 0. Refresh what's already in the IRW (do this periodically)
Rscript -e "library(irw); write.csv(irw_metadata(), 'irw_metadata.csv')"

# 1. Search across repositories (auto-excludes known IRW datasets + queue)
python irw_discover_updated.py "PHQ-9" "reading assessment" --out candidates.csv

# 2. Test on 10 rows before running everything
python irw_batch_updated.py candidates.csv --limit 10 --out triage_test.csv

# 3. Full run — safe to interrupt and resume
python irw_batch_updated.py candidates.csv --out triage.csv
python irw_batch_updated.py candidates.csv --out triage.csv --resume

# 4. Open triage.csv, sort by flag ('good' first), review candidates.
#    For anything you want to process, add a row to the "to be processed" tab:
#    https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8
#    (columns: doi, title, source, url)
#    For human_review rows from irw_retriage_ha.py, add them to the "human eye" tab.
```

The triage step downloads each candidate and runs automated checks — it does
**not** save any data files. Its only output is `triage.csv`.

### Step 1b — Retriage human_assistance rows (optional)

After a full triage run the `human_assistance` bucket is usually large (hundreds
of rows). Most of it is recoverable without re-downloading anything:

```bash
python irw_retriage_ha.py --input triage.csv --out triage_ha_refined.csv
```

This reads the 400-char `reasons` strings already in the triage CSV and
sub-classifies each `human_assistance` row into one of six buckets:

| refined_flag | Typical cause | Action |
|---|---|---|
| `not_item_response` | HTML-markup scraped tables, data dictionaries, implausible participant counts | Drop |
| `aggregate_continuous` | >50 unique resp values after melt; extreme dup_id_item ratio | Drop — likely continuous measures |
| `wrong_file_selected` | Codebook file downloaded instead of data matrix (common with SAPA-Project) | Re-resolve landing page manually |
| `recoverable_format` | Semicolon-delimited file read with comma delimiter | Re-read with `sep=';'`, re-triage |
| `worth_retrying` | dup_id_item with plausible longitudinal structure (ratio 1–8×, n≥50) | Re-download; look for wave/timepoint column |
| `human_review` | Genuinely ambiguous | Needs a human to look at the raw file |

In practice ~60% of `human_assistance` rows are resolved automatically, leaving
a much smaller set for manual review.

---

## Step 2 — Process the queue

**Who:** Someone doing the actual IRW data work.
**When:** After candidates have been added to the queue sheet.
**Output:** Best-guess IRW-formatted CSV files, one per dataset, ready to review.

```bash
python irw_process_queue.py
```

This reads the **"to be processed"** tab of the [queue Google Sheet](https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/edit),
downloads each dataset, and saves a standardized file to `irw_output/queue/`.
Re-running is safe — datasets already in `irw_output/queue/` are skipped.

### What the queue files look like

Each file in `irw_output/queue/` is in IRW long format with (at minimum) three
columns:

| Column | Contents |
|---|---|
| `id` | Person identifier — best guess from the source data |
| `item` | Item identifier — column names from the wide source, or existing item labels |
| `resp` | Numeric response value |

Additional columns (`wave`, `treat`, `cov_*`) are carried through when the
pipeline can identify them. The conversion is a **heuristic best-guess**, not a
verified mapping.

### Cleaned files and the index

After human review and cleanup, finalized files go to `irw_output/cleaned/`.
That folder contains **only** the CSVs destined for Redivis upload — nothing else.
Each cleaning script in `data/` writes a row to `irw_output/cleaned_index.csv`
(one level up) recording key metadata and any outstanding issues. Update the
`status` column from `cleaned` to `submitted` once a dataset has been uploaded
to Redivis.

`cleaned_index.csv` columns:

| Column | Contents |
|---|---|
| `file` | Filename in `irw_output/cleaned/` |
| `doi` | Source DOI |
| `title` | Dataset title |
| `scale` | Instrument name |
| `n_participants` / `n_items` / `n_responses` | Dataset dimensions |
| `resp_range` | Response scale (e.g. `0-3`) |
| `notes` | Outstanding issues to resolve before submission |
| `status` | `cleaned` → `submitted` |

### What still needs a human before submission

These files are **ready to review, not ready to submit**. Before a file goes
into the IRW processing pipeline, check:

1. **Covariates in the item column.** Demographic columns (`Age`, `Sex`,
   `Education`, etc.) often get melted in as items. They need to be moved out
   and renamed with a `cov_` prefix or dropped.

2. **Multiple scales.** If the `multi_scale*` warning fired, the file likely
   contains two instruments that must be split into separate files.

3. **Response direction.** The `resp_direction*` warning fires on every
   wide-to-long conversion — it's a standing reminder to verify that higher
   values indicate more of the construct within each item (i.e., no unreversed
   items).

4. **Item labels.** Wide-format source data uses column names as item
   identifiers. These may be meaningful (`I found it hard to wind down`) or
   opaque (`V1`, `Q3`). Opaque labels should be replaced with proper item text
   where possible.

5. **Scale and range.** Glance at the unique `resp` values to confirm they
   match the expected response scale for the instrument.

The QC warnings printed during processing (and recorded in the triage CSV)
tell you exactly what to look for in each file.

---

## Keeping the queue current

The [queue Google Sheet](https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/edit) has two tabs:

| Tab | Purpose |
|---|---|
| **to be processed** | Datasets queued for or already processed. Add rows here for anything you intend to process (`doi`, `title`, `source`, `url`). Rows are never removed — they serve as a permanent exclusion list. |
| **human eye** | Datasets with `refined_flag = human_review` that need a person to open the raw file and decide if they're worth processing. Move actionable rows to "to be processed" once a decision is made. |

| Source | When it's checked | What it excludes |
|---|---|---|
| Queue sheet — "to be processed" tab | Step 1 (discovery) | DOIs already queued for processing |
| Redivis (`bdomingu/irw_meta`) | Step 2 (process queue) | DOIs already in the IRW |

No local metadata files needed. The Redivis check runs once at the start of
`irw_process_queue.py` and skips any queued dataset whose DOI already appears
in the IRW.

---

## Triage CSV column reference

| Column | What it means |
|---|---|
| `source` | Repository (`dataverse`, `figshare`, `zenodo`, `osf`, `dryad`) |
| `title` | Dataset title from the repository |
| `doi` | DOI; used for deduplication and exclusion |
| `url` | Landing-page URL |
| `flag` | Routing decision — see below |
| `reasons` | Why the flag was assigned; pipe-separated QC findings |
| `n_participants` | Distinct `id` values |
| `n_items` | Distinct `item` values |
| `n_responses` | Total non-NA rows |
| `density` | IRW density: `(√n_resp / n_part) × (√n_resp / n_item)` — 1.0 = complete matrix |
| `license` | Normalized license string (e.g. `cc-by`, `cc0`, `unknown`) |
| `data_file` | Filename that was downloaded and triaged |
| `n_other_files` | Additional tabular files on the landing page (>0 = multi-file, needs a human) |

### Flag values

| Flag | Meaning | Action |
|---|---|---|
| `good` | Confident column mapping, no QC errors | Strong candidate — add to queue sheet |
| `human_assistance` | Got data, but mapping or QC needs a person | Read `reasons`; may still be worth adding |
| `not_item_response` | Data shaped like IRW format but isn't response data | Skip |
| `no_usable_file` | No resolvable tabular file on the landing page | Skip |
| `license_restricted` | License (NC, ND, All Rights Reserved) blocks redistribution | Skip |
| `download_failed` | Network or HTTP error | Retry manually if important |
| `error` | Unexpected pipeline error | Check `reasons` |

### QC warning glossary

Starred names (`*`) are heuristics beyond the official IRW validator.

| Warning | Meaning |
|---|---|
| `resp_direction*` | Cannot auto-verify coding direction within items — confirm no unreversed items |
| `resp_ordinal*` | >50 unique resp values after melt — likely aggregate/continuous data, not item responses |
| `multi_scale*` | Item names suggest 2+ subscales — IRW requires separate files per scale |
| `imputed_values*` | Column names or value distributions suggest imputed data — IRW requires removal |
| `date_numeric*` / `date_range*` | `date` column not numeric or too small for Unix seconds |
| `rt_units*` / `rt_negative*` | `rt` looks like milliseconds, or has negative values |
| `item_level_cols*` | Item-level columns (`itemcov_`, `rater`, `item_family`) excluded from melt — verify alignment |
| `cov_prefix` | Unrecognized columns — prefix with `cov_` if person-level covariates |
| `treat_binary*` | `treat` has values other than 0/1 |
| `dup_id_item` | Duplicate id+item rows (error without a longitudinal column) |
| `license_unknown*` | License not recognised as a known open license — verify before submission |
| `density*` | Very sparse matrix — fine for adaptive designs, otherwise verify |

---

## Scripts

### `irw_discover_updated.py`
Searches Dataverse, Zenodo, OSF, Dryad, and Figshare. Tiered relevance filter:
named instruments always pass; psychometric and construct terms pass unless
blocked by epi/clinical study language; supplementary file titles
(`Table N_…`, `Data Sheet N_…`) are always blocked.
Auto-loads `irw_metadata.csv` and the queue sheet to exclude known DOIs.
```
--all          disable relevance filter
--out <path>   output path (default: irw_discovered.csv)
```

### `irw_batch_updated.py`
Resolves landing pages to data files, downloads, triages, and writes
`triage.csv`. No data files are saved — triage only.
```
--limit <n>    process only the first N rows
--resume       continue from checkpoint after interruption
--out <path>   output path (default: irw_triage_summary.csv)
```

### `irw_process_queue.py`
Reads the queue sheet, downloads and standardizes each dataset to IRW format,
saves to `irw_output/queue/`. Skips DOIs already present in that folder.
```
--out-dir <path>   output directory (default: irw_output/queue)
```

### `irw_triage_updated.py`
Evaluate a single file directly (useful for spot-checking):
```bash
python irw_triage_updated.py path/to/data.csv
python irw_triage_updated.py https://example.com/data.csv
```

### `irw_retriage_ha.py`
Post-hoc refinement of `human_assistance` rows using metadata already in the
triage CSV — no re-download required. Adds `refined_flag` and `refined_reason`
columns and prints a summary with actionable follow-up lists.
```
--input <path>   triage CSV to read (default: irw_triage_new.csv)
--output <path>  refined CSV to write (default: irw_retriage_ha.csv)
```
Run this after any full batch triage to reduce the manual review burden before
deciding which `human_assistance` cases to escalate.
