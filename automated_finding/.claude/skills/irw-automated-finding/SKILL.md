---
name: irw-automated-finding
description: This skill should be used when the user asks to "find new datasets for IRW", "run discovery", "search for item response datasets", "triage candidates", "retriage human_assistance rows", "process the queue", or otherwise references the automated_finding pipeline (irw_discover_updated.py, irw_batch_updated.py, irw_retriage_ha.py, irw_process_queue.py) or its TODO.md/BATCH_LOG.md.
---

# IRW Automated Finding Pipeline

Orchestrates the multi-step pipeline in `automated_finding/` that finds,
triages, and standardizes candidate datasets for the Item Response Warehouse.
The scripts and full column/flag reference already live in
`automated_finding/README.md` — read it before running anything unfamiliar.
The output format itself — schema, naming, edge cases — is defined in
`datastandard.md` at the repo root; this file does not restate it. This file
is the orchestration layer: which step to run, in what order, and the
pipeline-specific hard rules that must not be skipped.

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

1. Read `TODO.md` — the short list of currently open action items (on-hold
   datasets, unresolved `worth_retrying` cases, pending uploads). Check
   whether anything you're about to do overlaps with it.
2. Read `BATCH_LOG.md` — the running, append-only log of every discovery
   run, batch, and decision made so far. Check it before starting new work
   so effort isn't duplicated (e.g. a search term or DOI already covered).
   `TODO.md` is for "what's still open"; `BATCH_LOG.md` is for "what's
   already been decided" — read both, but they answer different questions.
3. Read `search_terms_log.csv` — the permanent record of every query already
   run through `irw_discover_updated.py`. Only add genuinely new terms.
4. Note: this skill cannot write to the queue Google Sheet directly (no
   Sheets-editing tool is available, only Drive read/download). Prepare new
   rows as a CSV in the scratchpad or `/tmp` (matching the existing
   `/tmp/biblio_batchN.csv` convention visible in `BATCH_LOG.md`) and tell
   the user what to paste in, rather than claiming the sheet was updated.

## Step 1 — Discover

```bash
python irw_discover_updated.py "search term 1" "search term 2" --out candidates.csv
```

- Pick terms not already in `search_terms_log.csv`. Good sources of new terms:
  named instruments not yet covered, constructs adjacent to recent batches,
  or a domain the user names explicitly.
- **Translate every term into at least these 8 languages and include all
  variants in the same discovery run**: Spanish, German, French, Chinese
  (Simplified), Japanese, Arabic, Dutch, Korean (the set used in batch 9).
  Non-English repositories (especially Dataverse installations run by
  non-US institutions) surface real candidates that the English term alone
  misses. Batch 9 did this (9 languages × 30 topics); batches 10–13 regressed
  to English-only by omission, not by decision — don't repeat that. A batch
  of N English terms should become N × 9 discovery queries (English +
  8 translations), all logged and run together, not as a separate follow-up.
- After the run, append every term (English and each translation) to
  `search_terms_log.csv` as its own row.

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
- `good` rows → go straight to Step 3 (write a processing script). There is
  no "stage it in the queue sheet first" step — that tab exists but this
  pipeline doesn't write to it (confirmed 2026-07-14: none of batches 14-16's
  processed DOIs were ever added to it). Don't add that step back in.
- `human_assistance` rows → run Step 2b before deciding what to do with them.
- Once every `good`/`worth_retrying` row has a processing script (or a
  documented skip reason) and every `human_review` row is in the "human eye"
  tab, delete the local triage CSV — it's temporary; `search_terms_log.csv`
  is the permanent record.

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
`irw_output/queue/` → `cleaned_index.csv` flow. Per `BATCH_LOG.md`'s
"Workflow notes (2026-06-24)", that intermediate stage was eliminated —
`irw_process_queue.py` is stale and should not be run. `irw_output/queue/`
and `cleaned_index.csv` no longer exist. The README hasn't been updated to
match; treat `BATCH_LOG.md`'s latest workflow notes as authoritative over the
README when they conflict.

Current practice (see batches 7–9 in `BATCH_LOG.md` and e.g.
`data/frikha_2023_motivation.py`, `data/germann_2026_terrorism.py`): for each
`good` or `worth_retrying` candidate, write one bespoke script directly in
`data/`, named `authorname_year_construct.py`.

**Read `datastandard.md` at the repo root before writing the script** — it is
the single source of truth for the required schema, column order, file
naming, output location, and the step-by-step conversion logic (load raw
data → identify id/covariates/items → melt to long → clean `resp` → enforce
column order → save). Follow it rather than improvising; this SKILL.md only
covers pipeline orchestration, not the data standard itself.

There is no separate "processing queue" run or intermediate holding
directory — the script IS the queue-processing step, and its output in
`irw_output/` is upload-ready (not a rough draft), so get the QC checks in
Step 4 right the first time.

## Step 4 — QC before submitting

Before uploading a file from `irw_output/` to Redivis, run through
`datastandard.md`'s "What to verify before saving" checklist — the QC
warnings recorded in the triage CSV point at exactly what to check.

One additional hard rule applies at this stage that isn't in
`datastandard.md`, because it's a pipeline/triage concern rather than an
output-format one:

- **License.** Only proceed if the license is explicitly verified as open
  (`cc0`, `cc-by`, `cc-by-sa`, or equivalent) on the source page itself. A
  triage `license` of `unknown` does not count as verified — skip. A bare
  OSF-style UUID is *not* automatically unverified, though: OSF nodes report
  their license as a raw license-object id (e.g.
  `563c1cf88c5e4a3877f9e96a`), not a name. Resolve it first —
  `GET https://api.osf.io/v2/licenses/{id}/` returns the actual license name
  — before deciding it's unverified. Only skip once that lookup fails to
  produce an explicit open license. If the dataset is otherwise strong,
  skipping isn't the only option — emailing the author for permission
  (template in `processing_notes/Licensing.txt`) is fine, but don't process
  the data until permission or updated license terms come back confirmed.
- **Log it before dropping it.** When a `good` (or otherwise structurally
  strong) candidate is skipped purely because of a missing/unresolvable
  license — not a content problem — append a row to
  `license_blocked_candidates.csv` (title, URL, paper DOI if any, n/items/
  density, contributors + OSF profile links, email if a linked *published*
  paper's Crossref/PMC metadata has one — OSF's API never exposes email
  directly, don't guess one) before moving on. This is a standing list, not
  a per-batch temp file — don't delete it. It exists so a strong,
  ready-to-process candidate isn't lost the moment its triage CSV gets
  cleaned up.

When adding a biblio/dictionary entry for a cleaned dataset, columns are, in
order: `table, table.lower, Description, URL (for data), Reference,
DOI (for paper), Original License, Custom License, Public Reshare?,
Derived License, Custom License, Notes, Contributor, Date`. Note `Custom
License` appears twice (both blank), `Derived License` mirrors `Original
License`, license values are full display names (`"CC0 1.0"`, not `"cc0"`),
`Contributor` is `"automated"`, and `Public Reshare?` is `"Public"` (not
`"Yes"`).

There is no `cleaned_index.csv` to update (eliminated 2026-06-24) —
`BATCH_LOG.md` is the record of what's been cleaned, uploaded, and
biblio-entered per batch.

## After finishing a batch

1. Append a dated entry to `BATCH_LOG.md` summarizing what ran and what was
   decided (new search terms used, candidate counts, good/skip decisions,
   batch/table names) — following the existing style already in the file.
   This is what lets the next run (by Claude or a human) avoid repeating
   work.
2. Reconcile `TODO.md`: remove any item the batch resolved, add any new
   open item the batch surfaced (an on-hold dataset, an uninvestigated
   `worth_retrying` case, a pending upload). `TODO.md` should always reflect
   only what's currently actionable — don't let resolved items linger there
   the way they used to linger unchecked in the old combined file.
3. Delete temp files once their content is captured elsewhere — this
   pipeline generates several per batch (`candidates*.csv`,
   `irw_triage*.csv`, `irw_retriage*.csv`, any `triage_test*.csv` sanity
   check, `irw_batch_checkpoint.jsonl`) and they're disposable *once* every
   actionable row has landed in `BATCH_LOG.md`, a `data/*.py` script, or a
   CSV handed to the user for the queue/dictionary sheet. Don't delete a
   `human_review_*.csv` or biblio CSV until the user has confirmed the rows
   were actually pasted into the sheet — check whether that item is still
   open in `TODO.md`, don't assume from an earlier "yes." **Never delete
   `license_blocked_candidates.csv`** — unlike the per-batch temp files, it's
   a standing, cumulative list (like `search_terms_log.csv`), not disposable
   once a batch is written up.
