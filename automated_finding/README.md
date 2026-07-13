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
python irw_batch_updated.py candidates.csv --out irw_triage.csv
python irw_batch_updated.py candidates.csv --out irw_triage.csv --resume

# 4. Open irw_triage.csv, sort by flag ('good' first), review candidates.
#    For anything you want to process, add a row to the "to be processed" tab:
#    https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8
#    (columns: doi, title, source, url)
#    For human_review rows from irw_retriage_ha.py, add them to the "human eye" tab.

# 5. Once actionable rows are captured in the sheet, delete the local triage CSV.
#    It is a temporary working file — search_terms_log.csv is the permanent record.
```

The triage step downloads each candidate and runs automated checks — it does
**not** save any data files. Its only output is `irw_triage.csv` (a temporary
working file — delete it once good candidates are in the queue sheet and
human_review rows are in the "human eye" tab).

`search_terms_log.csv` is the permanent record of all queries that have been
run. Update it whenever you add new search terms.

### Step 1b — Retriage human_assistance rows (optional)

After a full triage run the `human_assistance` bucket is usually large (hundreds
of rows). Most of it is recoverable without re-downloading anything:

```bash
python irw_retriage_ha.py --input irw_triage.csv --out irw_retriage_ha.csv
```

This reads the 400-char `reasons` strings already in the triage CSV and
sub-classifies each `human_assistance` row into one of six buckets:

| refined_flag | Typical cause | Action |
|---|---|---|
| `not_item_response` | HTML-markup scraped tables, data dictionaries, implausible participant counts | Drop |
| `aggregate_continuous` | >50 unique resp values after melt; extreme dup_id_item ratio | Drop *if* it's a composite/subscale score smuggled in as an item — but a genuinely continuous per-item response (e.g. a 0–100 slider) is valid IRW data and should not be dropped just for tripping this heuristic; check which case it is before deciding |
| `wrong_file_selected` | Codebook file downloaded instead of data matrix (common with SAPA-Project) | Re-resolve landing page manually |
| `recoverable_format` | Semicolon-delimited file read with comma delimiter | Re-read with `sep=';'`, re-triage |
| `worth_retrying` | dup_id_item with plausible longitudinal structure (ratio 1–8×, n≥50) | Re-download; look for wave/timepoint column |
| `human_review` | Genuinely ambiguous | Needs a human to look at the raw file |

In practice ~60% of `human_assistance` rows are resolved automatically, leaving
a much smaller set for manual review.

---

## Step 2 — Write a processing script per dataset

**Who:** Someone doing the actual IRW data work.
**When:** After candidates have been added to the queue sheet.
**Output:** One bespoke script per dataset in `data/`, writing upload-ready
CSVs directly to `irw_output/`.

> **This section used to describe a different flow** — `irw_process_queue.py`
> → `irw_output/queue/` → human cleanup → `irw_output/cleaned/` +
> `cleaned_index.csv`. That intermediate stage was eliminated 2026-06-24 (see
> `TODO.md`'s "Workflow notes"). `irw_process_queue.py`, `irw_output/queue/`,
> and `cleaned_index.csv` no longer exist — do not run or look for them.
> Current practice is below.

For each `good` or `worth_retrying` row in the queue sheet, write one
standalone script directly in `data/`, named `authorname_year_construct.py`
(see e.g. `data/frikha_2023_motivation.py`, `data/germann_2026_terrorism.py`).
The script downloads the raw file from its source (Dataverse/Figshare/OSF/
Zenodo API), converts it to IRW format, and writes one CSV per measurement
scale straight to `automated_finding/irw_output/`, named
`authorname_year_construct.csv`. There is no separate "processing queue" run
or intermediate holding directory — the script *is* the queue-processing
step, and its output is upload-ready, not a rough draft.

For the exact schema, column order, file naming, and conversion logic,
follow **`datastandard.md`** at the repo root — it is the canonical
output-format spec and supersedes anything here that conflicts with it.

### QC before submitting

Before uploading a file from `irw_output/` to Redivis, run through
`datastandard.md`'s "What to verify before saving" checklist. The QC
warnings printed during triage (and recorded in the triage CSV, glossary
below) point at exactly what to check in each file.

There is no `cleaned_index.csv` to update — `TODO.md` is the record of
what's been processed, uploaded, and biblio-entered per batch.

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
| IRW dictionary / Redivis (`bdomingu/irw_meta`) | Step 2 (before writing a script) | DOIs already in the IRW |

No local metadata files needed, but this check is now manual per dataset —
there is no longer a pipeline step that runs it automatically. Before writing
a processing script, check the dataset's DOI against the
[dictionary](https://docs.google.com/spreadsheets/d/1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s)
(or `irw_metadata()` in R) to make sure it isn't already in the IRW.

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
| `resp_ordinal*` | >50 unique resp values after melt — likely aggregate/continuous data, not item responses. Verify which: a composite/subscale sum is not a response and must be dropped; a genuinely continuous per-item response (e.g. a 0–100 slider) is legitimate — keep `resp` as a float, don't coerce to integer |
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

An unresolved license doesn't have to be a dead end: if the dataset is otherwise
strong, emailing the author for permission (template in
`processing_notes/Licensing.txt`) is an option — just don't process the data
until permission or updated license terms come back confirmed.

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
--out <path>   output path (default: candidates.csv)
```

### `irw_batch_updated.py`
Resolves landing pages to data files, downloads, triages, and writes
`triage.csv`. No data files are saved — triage only.
```
--limit <n>    process only the first N rows
--resume       continue from checkpoint after interruption
--out <path>   output path (default: irw_triage.csv)
```

### `irw_process_queue.py` — retired, do not run
Used to bulk-download and heuristically standardize every queued dataset to
`irw_output/queue/`. Eliminated 2026-06-24 in favor of one bespoke script per
dataset in `data/` (see Step 2 above) — the file is kept in this directory
for reference but is stale and should not be executed.

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
--input <path>   triage CSV to read (default: irw_triage.csv)
--output <path>  refined CSV to write (default: irw_retriage_ha.csv)
```
Run this after any full batch triage to reduce the manual review burden before
deciding which `human_assistance` cases to escalate.
