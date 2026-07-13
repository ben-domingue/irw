---
name: irw-automated-finding
description: This skill should be used when the user asks to "find new datasets for IRW", "run discovery", "search for item response datasets", "triage candidates", "retriage human_assistance rows", "process the queue", or otherwise references the automated_finding pipeline (irw_discover_updated.py, irw_batch_updated.py, irw_retriage_ha.py, irw_process_queue.py) or its TODO.md.
---

# IRW Automated Finding Pipeline

Orchestrates the multi-step pipeline in `automated_finding/` that finds,
triages, and standardizes candidate datasets for the Item Response Warehouse.
The scripts and full column/flag reference already live in
`automated_finding/README.md` — read it before running anything unfamiliar.
This file is the orchestration layer: which step to run, in what order, and
the hard rules that must not be skipped.

Work from inside `automated_finding/`.

## Prerequisites

`irw_batch_updated.py` and `irw_triage_updated.py` need `pandas` and
`openpyxl` (for `.xlsx` sources); `irw_discover_updated.py` only needs
`requests`, which is commonly already present. A fresh machine may not have
`pandas`/`openpyxl` installed — check with
`python3 -c "import pandas, openpyxl"` before running the triage steps. If
missing and `pip install` refuses with "externally-managed-environment",
`pip3 install --user --break-system-packages pandas openpyxl` is a
reasonable, reversible fix (installs to the user's own site-packages, no
sudo, no system package changes) rather than fighting with a venv.

## Before doing anything

1. Read `TODO.md` — it is the running log of every discovery run, batch, and
   decision made so far. Check it before starting new work so effort isn't
   duplicated (e.g. a search term or DOI already covered).
2. Read `search_terms_log.csv` — the permanent record of every query already
   run through `irw_discover_updated.py`. Only add genuinely new terms.
3. Note: this skill cannot write to the queue Google Sheet directly (no
   Sheets-editing tool is available, only Drive read/download). Prepare new
   rows as a CSV in the scratchpad or `/tmp` (matching the existing
   `/tmp/biblio_batchN.csv` convention visible in `TODO.md`) and tell the user
   what to paste in, rather than claiming the sheet was updated.

## Step 1 — Discover

```bash
python irw_discover_updated.py "search term 1" "search term 2" --out candidates.csv
```

- Pick terms not already in `search_terms_log.csv`. Good sources of new terms:
  named instruments not yet covered, constructs adjacent to recent batches,
  or a domain the user names explicitly.
- After the run, append the new terms to `search_terms_log.csv`.

## Step 2 — Triage

```bash
python irw_batch_updated.py candidates.csv --limit 10 --out triage_test.csv   # sanity check first
python irw_batch_updated.py candidates.csv --out irw_triage.csv               # full run
python irw_batch_updated.py candidates.csv --out irw_triage.csv --resume      # if interrupted
```

- **Expect this to be slow.** Each candidate is a real network download plus
  a parse; a ~500-row candidate file has taken on the order of 2 hours
  wall-clock, dominated by per-domain rate limiting and the occasional large
  `.xlsx` (slow via `openpyxl`, can spike memory into the GBs transiently —
  not a hang, just let it run). Launch the full run in the background and
  check `wc -l irw_batch_checkpoint.jsonl` for progress rather than waiting
  on it synchronously.
- Sort `irw_triage.csv` by `flag`, `good` first.
- `good` rows → add to the "to be processed" tab of the queue sheet
  (doi, title, source, url).
- `human_assistance` rows → run Step 2b before deciding what to do with them.
- Once actionable rows are captured in the sheet, delete the local triage CSV
  — it's temporary; `search_terms_log.csv` is the permanent record.

## Step 2b — Retriage `human_assistance` (recommended before reviewing by hand)

```bash
python irw_retriage_ha.py --input irw_triage.csv --out irw_retriage_ha.csv
```

Sub-classifies each `human_assistance` row into `not_item_response` /
`aggregate_continuous` / `wrong_file_selected` / `recoverable_format` /
`worth_retrying` / `human_review` (see README for what each means and the
typical action). Usually resolves ~60% of the bucket automatically. Only
`human_review` rows need a person — add those to the "human eye" tab of the
queue sheet; everything else is either dropped or handled per its bucket.

## Step 3 — Write the processing script and QC it

**Note:** the README still documents an older `irw_process_queue.py` →
`irw_output/queue/` → `cleaned_index.csv` flow. Per `TODO.md`'s "Workflow
notes (2026-06-24)", that intermediate stage was eliminated —
`irw_process_queue.py` is stale and should not be run. `irw_output/queue/`
and `cleaned_index.csv` no longer exist. The README hasn't been updated to
match; treat `TODO.md`'s latest workflow notes as authoritative over the
README when they conflict.

Current practice (see batches 7–9 in `TODO.md` and e.g.
`data/frikha_2023_motivation.py`, `data/germann_2026_terrorism.py`): for each
`good` or `worth_retrying` candidate, write one bespoke script directly in
`data/`, named `authorname_year_construct.py`, that:

1. Downloads the raw file from its source (Dataverse/Figshare/OSF/Zenodo API).
2. Converts to IRW long format (`id`, `item`, `resp`, `cov_*`).
3. Writes one CSV per measurement scale straight to
   `automated_finding/irw_output/` (`REPO_ROOT / "automated_finding" /
   "irw_output"`), named `authorname_year_construct.csv`.

There is no separate "processing queue" run or intermediate holding
directory — the script IS the queue-processing step, and its output in
`irw_output/` is upload-ready (not a rough draft), so get the QC checks in
Step 4 right the first time.

## Step 4 — QC before submitting

Before uploading a file from `irw_output/` to Redivis, check the five items
under "What still needs a human before submission" in the README (covariates
melted in as items, multiple scales needing a split, response direction,
opaque item labels, response scale/range) — the QC warnings recorded in the
triage CSV point at exactly what to check.

Two hard rules apply at this stage, non-negotiable regardless of how good the
dataset otherwise looks:

- **License.** Only proceed if the license is explicitly verified as open
  (`cc0`, `cc-by`, `cc-by-sa`, or equivalent) on the source page itself. A
  triage `license` of `unknown` does not count as verified — skip. A bare
  OSF-style UUID is *not* automatically unverified, though: OSF nodes report
  their license as a raw license-object id (e.g.
  `563c1cf88c5e4a3877f9e96a`), not a name. Resolve it first —
  `GET https://api.osf.io/v2/licenses/{id}/` returns the actual license name
  — before deciding it's unverified. Only skip once that lookup fails to
  produce an explicit open license.
- **Naming.** Output files use `authorname_year_construct` (e.g.
  `smith2021_anxiety.csv`), never a content description. One file per
  measurement scale.
- **resp must be genuinely ordinal, not just numeric.** Check the codebook
  (variable-description file, OSF wiki, or paper) for every response scale
  before treating its raw codes as `resp`. A source column can be pure
  `int64` with zero `NaN`s and still be wrong: a sentinel category like
  "don't know" / "not applicable" / "refused" is a non-response, not a step
  on the ordinal scale, even though it's stored as an in-range integer (e.g.
  a 3-item financial-literacy quiz coded `0=incorrect, 1=correct, 2=don't
  know` — 2 is not "more correct" than 1). `dropna()` will **not** catch
  this, because the sentinel is a real number, not `NaN`. Identify these
  values from the codebook and exclude those specific item-responses (filter
  them out, don't recode them to 0 or drop the person entirely) before the
  file is considered ordinal and upload-ready.

When adding a biblio/dictionary entry for a cleaned dataset, columns are, in
order: `table, table.lower, Description, URL (for data), Reference,
DOI (for paper), Original License, Custom License, Public Reshare?,
Derived License, Custom License, Notes, Contributor, Date`. Note `Custom
License` appears twice (both blank), `Derived License` mirrors `Original
License`, license values are full display names (`"CC0 1.0"`, not `"cc0"`),
`Contributor` is `"automated"`, and `Public Reshare?` is `"Public"` (not
`"Yes"`).

There is no `cleaned_index.csv` to update (eliminated 2026-06-24) — `TODO.md`
is the record of what's been cleaned, uploaded, and biblio-entered per batch.

## After finishing a batch

1. Append a dated entry to `TODO.md` summarizing what ran and what was
   decided (new search terms used, candidate counts, good/skip decisions,
   batch/table names) — following the existing style already in the file.
   This is what lets the next run (by Claude or a human) avoid repeating
   work.
2. Delete temp files once their content is captured elsewhere — this
   pipeline generates several per batch (`candidates*.csv`,
   `irw_triage*.csv`, `irw_retriage*.csv`, any `triage_test*.csv` sanity
   check, `irw_batch_checkpoint.jsonl`) and they're disposable *once* every
   actionable row has landed in `TODO.md`, a `data/*.py` script, or a CSV
   handed to the user for the queue/dictionary sheet. Don't delete a
   `human_review_*.csv` or biblio CSV until the user has confirmed the rows
   were actually pasted into the sheet — check TODO.md's checkbox for that
   item, don't assume from an earlier "yes."
