# IRW Automated Finding Pipeline

## Quick start

```bash
# 0. One-time / periodic: refresh what's already in the IRW
#    (run in R whenever you want an up-to-date exclusion list)
Rscript -e "library(irw); write.csv(irw_metadata(), 'irw_metadata.csv')"

# 1. Find candidates — automatically excludes irw_metadata.csv and irw_queued.csv
python irw_discover_updated.py "PHQ-9 questionnaire" "reading assessment" --out candidates.csv

# 2. Test on 10 rows first
python irw_batch_updated.py candidates.csv --limit 10 --out triage_test.csv

# 3. Full run (resumable — safe to interrupt and continue)
python irw_batch_updated.py candidates.csv --out triage.csv
python irw_batch_updated.py candidates.csv --out triage.csv --resume

# 4. Open triage.csv; work 'good' rows first, then 'human_assistance'

# 5. For each dataset you decide to process, add a row to the queue sheet:
#    https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8
#    (columns: doi, title, source, url)
#    Future discovery runs will automatically exclude it.
```

### The two exclusion sources

| Source | What it contains | How to update |
|---|---|---|
| `irw_metadata.csv` (local file) | DOIs already in the IRW | `Rscript -e "library(irw); write.csv(irw_metadata(), 'irw_metadata.csv')"` — run periodically |
| [Processing queue Google Sheet](https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/edit) | DOIs decided for processing but not yet landed | Edit the sheet directly — must stay shared "anyone with link can view" |

Both are loaded automatically at startup — no flags needed. `irw_metadata.csv` is read from the working directory if present; the sheet is fetched over the network (a warning is printed if it can't be reached, and the run continues without it).

Once a dataset lands in the IRW, its DOI will appear in `irw_metadata.csv` on the next refresh and can be removed from the queue sheet.

---

## Output: triage summary CSV columns

| Column | What it means |
|---|---|
| `source` | Repository the candidate came from (`dataverse`, `figshare`, `zenodo`, `osf`, `dryad`) |
| `title` | Dataset title from the repository |
| `doi` | DOI if available; used for deduplication and linking |
| `url` | Landing-page URL |
| `flag` | Routing decision — see table below |
| `reasons` | Why the flag was assigned; pipe-separated list of QC findings |
| `n_participants` | Distinct `id` values in the coerced long table |
| `n_items` | Distinct `item` values |
| `n_responses` | Total non-NA rows |
| `density` | IRW density metric: `(√n_resp / n_part) × (√n_resp / n_item)` — 1.0 = complete matrix |
| `data_file` | Filename of the tabular file that was downloaded and triaged |
| `irw_file` | Path to the saved best-guess IRW-formatted CSV (empty if flag is `no_usable_file` etc.) |
| `n_other_files` | How many additional tabular files the landing page had (0 = only one; >0 = multi-file dataset, needs a human) |

### Flag values

| Flag | Meaning | Action |
|---|---|---|
| `good` | Confident column mapping, no QC errors | Review `irw_file`; check any listed warnings |
| `human_assistance` | Got data but mapping or QC needs a person | Read `reasons`; open `irw_file` if it exists |
| `not_item_response` | Data is shaped like IRW format but isn't response data (e.g. a stats table) | Skip |
| `no_usable_file` | Landing page had no resolvable `.csv`/`.tsv`/`.xlsx` | Skip |
| `download_failed` | Network or HTTP error | Retry manually if important |
| `error` | Unexpected pipeline error | Check `reasons` for the message |

---

## QC warning glossary

Warnings appear in the `reasons` column. Starred names (`*`) are heuristics added on top of the official IRW validator.

| Warning | Meaning |
|---|---|
| `resp_direction*` | After a wide-to-long melt, cannot auto-verify that higher resp = more of construct within each item — confirm no unreversed items |
| `resp_ordinal*` | >50 unique resp values — likely continuous or aggregate data rather than ordinal item responses; escalates to `human_assistance` after a melt |
| `multi_scale*` | Item names cluster into 2+ distinct prefixes — IRW requires separate files per scale |
| `imputed_values*` | Column names or value distributions suggest imputed data; IRW requires removal |
| `date_numeric*` / `date_range*` | `date` column is not numeric or looks too small for Unix seconds |
| `rt_units*` / `rt_negative*` | `rt` median suggests milliseconds instead of seconds, or negative values present |
| `item_level_cols*` | Columns like `itemcov_`, `rater`, `item_family` were excluded from the melt — verify alignment |
| `density*` | Matrix is very sparse; fine for adaptive/booklet designs, otherwise verify |
| `cov_prefix` | Unrecognized extra columns — prefix with `cov_` if they are person-level covariates |
| `treat_binary*` | `treat` column has values other than 0/1 |
| `dup_id_item` | Duplicate id+item rows (error if no longitudinal column; warning if `wave`/`date` present) |

---

## Scripts

### `irw_discover_updated.py` — find candidates

Searches Dataverse, Zenodo, OSF, Dryad, and Figshare. Applies a tiered relevance
filter: named instruments (PHQ-9, WAIS, BFI, …) always pass; strong psychometric
terms (Rasch, Likert, factor analysis, …) and construct terms (depression, ability,
personality, …) pass unless the title also contains epidemiological/clinical study
language. Supplementary file titles (`Table N_…`, `Data Sheet N_…`, `Supplementary
file N_…`) are blocked unconditionally — they are never standalone datasets.

```
--exclude <csv>   skip DOIs already in the IRW
--all             disable relevance filter entirely
--out <path>      output path (default: irw_discovered.csv)
```

### `irw_batch_updated.py` — triage at scale

Resolves each landing-page URL to actual data files (Zenodo, Figshare, Dryad,
Dataverse, OSF all supported), downloads the first tabular file, and runs
`irw_triage_updated.py` on it. Results are checkpointed after every row so the
run is safe to interrupt. Converted tables are saved under `irw_output/good/` and
`irw_output/human_assistance/`.

```
--limit <n>    process only the first N rows (use this to test)
--resume       continue from the checkpoint
--out <path>   output path (default: irw_triage_summary.csv)
```

### `irw_triage_updated.py` — evaluate one file

Runs a single file through download → coerce → QC → flag. Can be used standalone:

```bash
python irw_triage_updated.py path/to/data.csv
python irw_triage_updated.py https://example.com/data.csv
```

Prints a full report and writes a best-guess IRW-formatted CSV if a conversion
was possible. The coercion is a heuristic: `human_assistance` is the normal,
expected outcome for ambiguous datasets, not a failure.
