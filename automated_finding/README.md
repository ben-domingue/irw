# IRW Automated Finding Pipeline

Automated tools for finding, screening, and standardizing datasets for the IRW.
The pipeline has **two distinct steps** with different people and cadences in mind.

This file is the **script and column/flag reference** — exact CLI flags, what
each triage column means, what each QC warning means. For orchestration —
what order to run things in, and the hard rules that must not be skipped
(the 9-language discovery requirement, the license-verification procedure,
what's current vs. retired) — see
`.claude/skills/irw-automated-finding/SKILL.md`, not this file. That skill
is what an agent actually follows step-by-step; this README is what it
consults for the details. Where the two disagree, the skill wins — it gets
updated whenever practice changes, and duplicated instructions here have
drifted stale before (e.g. the 9-language requirement below was silently
dropped for three batches until caught).

---

## Step 1 — Find and triage candidates

**Who:** Anyone with Python and internet access.
**When:** Periodically, or when targeting a new domain/instrument.
**Output:** A CSV ranking candidates by how cleanly they map to IRW format.

```bash
# 1. Search across repositories. Exclusion is automatic and live: the script
#    fetches DOIs already in the IRW dictionary directly from the Google
#    Sheet on every run (see _load_auto_exclusions() in
#    irw_discover_updated.py) — there is no local metadata file to
#    regenerate first.
python irw_discover_updated.py "PHQ-9" "reading assessment" --out candidates.csv

# 2. Test on 10 rows before running everything
python irw_batch_updated.py candidates.csv --limit 10 --out triage_test.csv

# 3. Full run — safe to interrupt and resume
python irw_batch_updated.py candidates.csv --out irw_triage.csv
python irw_batch_updated.py candidates.csv --out irw_triage.csv --resume

# 4. Open irw_triage.csv, sort by flag ('good' first), review candidates.
#    `good`/`worth_retrying` rows go straight to Step 2 (write a processing
#    script) -- there is no "add to a queue tab" staging step for these; see
#    the note below. For human_review rows from irw_retriage_ha.py, add them
#    to the "human eye" tab:
#    https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8

# 5. Once actionable rows are captured, delete the local triage CSV.
#    It is a temporary working file — search_terms_log.csv is the permanent record.
```

The triage step downloads each candidate and runs automated checks — it does
**not** save any data files. Its only output is `irw_triage.csv` (a temporary
working file — delete it once `good`/`worth_retrying` candidates have a
processing script and human_review rows are in the "human eye" tab).

**Note on the "to be processed" tab:** the queue sheet has a second tab by
this name, and older docs described writing `good` rows there as a staging
step before processing. That hasn't been the actual practice since batch 7
(confirmed 2026-07-14 by checking batches 14-16's processed DOIs against the
tab — none were ever added) — the automated pipeline goes straight from a
`good` triage flag to a processing script in `data/`, whose output lands
directly in the dictionary sheet. `irw_discover_updated.py` also dropped it
as a dedup-exclusion source the same day (2026-07-14) — it's a manually
maintained tab for other, non-pipeline contributors, not something this
pipeline's own candidates ever land in, so excluding on it no longer made
sense. Exclusion now runs off the IRW dictionary alone. The tab itself still
exists and still gets manual additions from others; this pipeline just
doesn't read or write it anymore. Don't resurrect either the "add to
to-be-processed" step or the exclusion check.

**Every new search term must also be run translated into several other
languages in the same discovery run** — non-English repositories surface real
candidates the English term alone misses. The current language set and the
exact rule are maintained in `SKILL.md` (Step 1), not here, since this list
has drifted out of sync with actual practice before.

`search_terms_log.csv` is the permanent record of all queries that have been
run. Update it whenever you add new search terms.

**A term logged before 2026-07-14 is not a complete "already covered" signal.**
`irw_batch_updated.py` couldn't see `.sav`/`.dta`/`.sas7bdat`/`.RData` files
before that date (fixed — see `SKILL.md` Step 1 and `BATCH_LOG.md`'s
"Pipeline fix" note), so a pre-fix run of that term only ruled out
`.csv`/`.xlsx`-visible candidates, not ones whose only file was one of those
formats. Don't assume this needs fixing by re-running every historical term
wholesale, though — check `TODO.md` for the current state of a small pilot
re-run that's assessing whether that's actually worth the cost first.

`license_blocked_candidates.csv` is a similar standing record, but for
datasets: whenever an otherwise-strong candidate gets skipped purely for a
missing/unresolvable license (not a content problem), it's logged there —
title, URL, size, contributors — before it's dropped, so it isn't lost the
moment the triage CSV that found it gets cleaned up. See `SKILL.md` Step 4
for what to capture.

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
**When:** Right after Step 1's triage flags a candidate `good` or
`worth_retrying` — there is no intermediate queueing step (see the "to be
processed" tab note above).
**Output:** One bespoke script per dataset in `data/`, writing upload-ready
CSVs directly to `irw_output/`.

> **This section used to describe a different flow** — `irw_process_queue.py`
> → `irw_output/queue/` → human cleanup → `irw_output/cleaned/` +
> `cleaned_index.csv`. That intermediate stage was eliminated 2026-06-24 (see
> `BATCH_LOG.md`'s "Workflow notes"). `irw_process_queue.py`, `irw_output/queue/`,
> and `cleaned_index.csv` no longer exist — do not run or look for them.
> Current practice is below.

For each `good` or `worth_retrying` row in the triage output, write one
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

One more hard rule applies at this stage that lives in `SKILL.md`, not
`datastandard.md`, because it's a pipeline/triage concern rather than an
output-format one: a triage `license` of `unknown` is not verified and means
skip, but a bare OSF-style UUID is *not* automatically unverified — resolve
it via `GET https://api.osf.io/v2/licenses/{id}/` before deciding. See
`SKILL.md` Step 4 for the full procedure.

There is no `cleaned_index.csv` to update — `BATCH_LOG.md` is the record of
what's been processed, uploaded, and biblio-entered per batch.

---

## Keeping the queue current

The [queue Google Sheet](https://docs.google.com/spreadsheets/d/1hiJb3-Cv7SpNwwtwAGmdqn-fZyJ4624P5HE6VZZTOw8/edit) has two tabs:

| Tab | Purpose |
|---|---|
| **to be processed** | A place other (manual, non-pipeline) contributors queue datasets. This automated pipeline neither writes to it nor reads it — `good`/`worth_retrying` candidates go straight to a processing script and from there into the dictionary sheet, and exclusion runs off the dictionary alone. Don't add a "stage it here first" step, and don't add it back as an exclusion source. |
| **human eye** | Datasets with `refined_flag = human_review` that need a person to open the raw file and decide if they're worth processing. Once a decision is made, either write a processing script (if eligible) or drop it — there's no intermediate tab to move it to. |

| Source | When it's checked | What it excludes |
|---|---|---|
| IRW dictionary / Redivis (`bdomingu/irw_meta`) | Step 1 (discovery), automatically; also worth a manual double check in Step 2 before writing a script | DOIs already in the IRW |

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
| `good` | Confident column mapping, no QC errors | Strong candidate — write a processing script (Step 2) |
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
Auto-excludes known DOIs by fetching the IRW dictionary sheet live on every
run (`_load_auto_exclusions()`) — no local file needed. (The "to be
processed" queue sheet was dropped as an exclusion source 2026-07-14 — see
the note in Step 1 above.)
```
--all          disable relevance filter
--out <path>   output path (default: candidates.csv)
```

### `irw_batch_updated.py`
Resolves landing pages to data files, downloads, triages, and writes
`triage.csv`. No data files are saved — triage only. Recognizes
`.csv`/`.tsv`/`.xlsx`/`.xls`/`.sav`/`.dta`/`.sas7bdat`/`.rdata`/`.rda`/`.rds`
on a landing page (`TABULAR_EXT`) — the SPSS/Stata/SAS/R formats were added
2026-07-14; see the "Pipeline fix" note in `BATCH_LOG.md` for why and what
it needed (`pyreadstat`/`pyreadr`, see Prerequisites in `SKILL.md`).
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
Evaluate a single file directly (useful for spot-checking). `load_table()`
here is what `irw_batch_updated.py` calls too, so its format support
(`.csv`/`.tsv`/`.xlsx`/`.xls`/`.sav`/`.dta`/`.sas7bdat`/`.rdata`/`.rda`/`.rds`)
is shared between both entry points:
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

### `irw_extract_evaluated_dois.py`
Mines `BATCH_LOG.md` for DOI-like identifiers of every dataset already
evaluated in any prior batch — any outcome (good, skip, human_review,
worth_retrying, processed), not just what's in the IRW dictionary or queue
sheet. Exists because the dictionary/queue exclusion in
`irw_discover_updated.py` can't catch a dataset that was looked at and
explicitly *skipped* — it never lands in either sheet, so it can resurface
as a "new" candidate in a later batch (this happened to DVN/5ZQHV6 twice,
in batches 14 and 15, before this tool existed).
```bash
python irw_extract_evaluated_dois.py                        # print count + list
python irw_extract_evaluated_dois.py --out dois.txt          # write to file
python irw_extract_evaluated_dois.py --check candidates.csv  # report matches in a candidate file
```
Run the `--check` form against a merged candidate file before triaging it,
same as the license/dictionary checks. It's a heuristic (only catches
datasets mentioned with a recognizable ID in `BATCH_LOG.md`'s prose) —
treat a 0-match result as "no repeats caught," not "no repeats exist."
