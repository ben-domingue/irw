---
name: irw-automated-finding
description: This skill should be used when the user asks to "find new datasets for IRW", "run discovery", "search for item response datasets", "triage candidates", "retriage human_assistance rows", "process the queue", or otherwise references the automated_finding pipeline (irw_discover_updated.py, irw_batch_updated.py, irw_retriage_ha.py, irw_discover_plos.py, irw_discover_pmc.py, irw_process_queue.py) or its TODO.md/BATCH_LOG.md. Also applies to searching individual open-access journals (e.g. PLOS ONE, or any journal in irw_discover_pmc.py's JOURNALS list) directly, as opposed to data repositories, and to the journal_scout/ yield-measurement study used to decide which journals are worth adding to that list.
---

# IRW Automated Finding Pipeline

Orchestrates the multi-step pipeline in `automated_finding/` that finds,
triages, and standardizes candidate datasets for the Item Response Warehouse.
The scripts and full column/flag reference already live in
`automated_finding/README.md` — read it before running anything unfamiliar.
The output format itself — schema, naming, edge cases, and what counts as
a legitimate candidate in the first place (e.g. what `id` is allowed to
identify, what a "response" is) — is defined in `datastandard.md` at the
repo root; this file does not restate it. That makes `datastandard.md`
the authority not just when writing a script (Step 3), but for any
triage/review judgment call about whether a candidate fits — check it
before inventing a fit-or-skip rule that isn't written down anywhere.
This file is the orchestration layer: which step to run, in what order,
and the pipeline-specific hard rules that must not be skipped.

Work from inside `automated_finding/`.

## Prerequisites

`irw_batch_updated.py` and `irw_triage_updated.py` need `pandas`, `openpyxl`
(for `.xlsx` sources), `pyreadstat` (for `.sav`/`.sas7bdat` sources, via
`pd.read_spss`/`pd.read_sas`), and `pyreadr` (for `.RData`/`.rds` sources —
`.dta` needs neither extra package, `pd.read_stata` is pandas-native).
`irw_discover_updated.py` only needs `requests`, which is commonly already
present. A fresh machine may not have these installed — check with
`python3 -c "import pandas, openpyxl, pyreadstat, pyreadr"` before running
the triage steps. If missing and `pip install` refuses with
"externally-managed-environment",
`pip3 install --user --break-system-packages pandas openpyxl pyreadstat pyreadr`
is a reasonable, reversible fix (installs to the user's own site-packages,
no sudo, no system package changes) rather than fighting with a venv.
`irw_discover_plos.py` additionally needs `xlrd` (for old-style `.xls`
Supporting Information files — `openpyxl` only handles `.xlsx`); install the
same way if missing.

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
4. **The old queue Google Sheet (both its "human eye" and "to be processed"
   tabs) is deprecated as of 2026-08-12** — it grew to ~4,846 rows on the
   "human eye" tab alone and became unmanageable. Don't read from it, write
   to it, or tell the user to paste anything into it. Rows that flag
   `human_review` now go straight into a permanent CSV under
   `human_review/` in this repo — see Step 2/2b below for exactly which
   rows that means and the naming convention. `biblio_*.csv` rows (for
   Redivis/dictionary-sheet entries) still follow the older "prepare a CSV
   directly in `automated_finding/`, tell the user what to paste in" pattern
   — that part is unaffected by this change, only the human-review
   destination changed. Earlier batches used a scratchpad/`/tmp` path for
   staging CSVs (e.g. `/tmp/biblio_batchN.csv`) — don't repeat that: the
   scratchpad directory is tied to the session that created it, so the user
   can't reliably find it afterward (confirmed 2026-07-15 — biblio rows for
   a resolved batch had to be relocated into `automated_finding/` after the
   user couldn't locate them). `license_blocked_candidates.csv` and prior
   `biblio_*.csv` files already follow this repo-tracked pattern.
5. **Pick a discovery mode before running anything.** There are three
   independent, non-overlapping discovery sources, each with its own
   script, journal/repo scope, and term-recycling pool — check which one
   the user means (they may say "PLOS", name a specific journal from
   `irw_discover_pmc.py`'s `JOURNALS`, or just say "find candidates" /
   "run discovery", which defaults to the repo-based mode below). If it's
   genuinely ambiguous, ask rather than guessing:

   1. **PLOS journals** — `irw_discover_plos.py`. See "Alternate discovery
      source: single-journal search (PLOS ONE)" below.
   2. **The Europe-PMC-covered journals** — `irw_discover_pmc.py` (PeerJ,
      Scientific Reports, and the rest of `JOURNALS` — deliberately *not*
      PLOS, which stays on mode 1). See "Alternate discovery source:
      Europe-PMC-based multi-journal search" below.
   3. **Data repositories** (Dataverse/Zenodo/OSF/Dryad/Figshare/...) —
      `irw_discover_updated.py`, Steps 1-4 immediately below.

   These three pull from disjoint search surfaces, so a term already run
   against one is *not* a duplicate query against another — each has its
   own term-recycling rule (see the "Term selection" note in each mode's
   section) rather than one shared one.

## Step 1 — Discover (mode 3: data repositories)

```bash
python irw_discover_updated.py "search term 1" "search term 2" --out candidates.csv
```

- Exclusion (`_load_auto_exclusions()`) now checks two sources: DOIs already
  in the IRW dictionary, and DOIs already logged in any `human_review/*.csv`
  (added 2026-08-12, replacing the old "human eye" sheet dedup that never
  actually existed as an automated check). This means a candidate a person
  already reviewed and passed on in a past batch won't resurface in a new
  discovery run. `irw_discover_plos.py` and `irw_discover_pmc.py` share the
  same function, so this applies to all three discovery modes automatically.
- Pick terms not already in `search_terms_log.csv`. Good sources of new terms:
  named instruments not yet covered, constructs adjacent to recent batches,
  or a domain the user names explicitly.
- **Caveat on terms logged before 2026-07-14**: `irw_batch_updated.py`
  couldn't see `.sav`/`.dta`/`.sas7bdat`/`.RData` files at all before that
  date (fixed — see `BATCH_LOG.md`'s "Pipeline fix" note) — any landing page
  whose *only* file was one of those formats was silently triaged as
  `no_usable_file` without ever being opened. All 575 pre-fix **English**
  terms were re-run against this fix (2026-07-15): found 186 previously-
  invisible alt-format candidates out of 10198 (1.8%), yielding 21 new
  tables across 9 datasets — that's done, don't repeat it. The ~1500
  logged **non-English** terms have not been re-run this way; a per-language
  pilot to gauge whether it's worth doing at scale is queued in `TODO.md`
  (deliberately after other open items) rather than done yet — check there
  for the current state of that decision.
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
- For a **recurring, incremental** run of a fixed term list against OSF/
  Dataverse (e.g. a scheduled monthly check) rather than a one-off manual
  run, use `irw_discover_monthly.py` instead — it computes `--since` per
  term from its own prior runs so each pass only surfaces what's new. See
  `README.md`'s `irw_discover_monthly.py` entry for details; edit its
  `TERM_LIST` before relying on it, it's a starting draft.

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
- **On a large candidate pool (thousands of rows) where you only need a
  narrow yes/no signal** (e.g. "does this resolve to an alt-format file at
  all?"), a full triage is overkill and can take 1-2 days. Use
  `resolve_data_files()` from `irw_batch_updated.py` directly in a small
  throwaway script for a metadata-only pass (lists filenames via each repo's
  API, no download/parse) to narrow the pool first, then run full triage
  only on what's left. This cut a 10198-candidate pool to 186 in ~82 minutes
  during the 2026-07-15 re-discovery (see `BATCH_LOG.md`).
- **If one source (e.g. Dataverse) is rate-limiting or timing out mid-run**,
  don't stall on it or drop it outright — split into a fast-sources-first
  pass and a deferred pass for the degraded source once it recovers, then
  merge results. Used successfully 2026-07-15; see `BATCH_LOG.md`'s
  "English-terms re-discovery" entry for the concrete phase-1/phase-2
  pattern.
- Sort `irw_triage.csv` by `flag`, `good` first.
- `good` rows → go straight to Step 3 (write a processing script). There is
  no "stage it in the queue sheet first" step — that tab exists but this
  pipeline doesn't write to it (confirmed 2026-07-14: none of batches 14-16's
  processed DOIs were ever added to it). Don't add that step back in.
- `human_assistance` rows → run Step 2b before deciding what to do with them.
- Once every `good`/`worth_retrying` row has a processing script (or a
  documented skip reason) and every `human_review` row has been written to
  `human_review/` (see Step 2b), delete the local triage CSV — it's
  temporary; `search_terms_log.csv` is the permanent record.
- **Non-human/animal subjects are not, by themselves, a reason to skip.**
  `datastandard.md`'s `id`-column definition already establishes this —
  `id` is "the focal unit being measured — typically a person, but
  sometimes another entity" (its own example is a word in a lexical
  task). A repeated-measures item/trial battery on animals fits the
  standard id/item/resp long format exactly as well as a human Likert
  survey does. Skip a candidate for the same reasons you'd skip a human
  one (composite-only data, N too small, no real item structure, no
  per-subject repeats) — not simply because the subject isn't human.
  (2026-08-10: a cichlid mate-preference candidate was dropped pre-review
  on "non-human" grounds alone during PLOS batch 21's worth_retrying pass
  — that reasoning wasn't grounded in `datastandard.md` and was wrong;
  re-evaluate any future non-human candidate on content merits per the
  actual standard, not an invented species restriction.)

## Step 2b — Retriage `human_assistance` (recommended before reviewing by hand)

```bash
python irw_retriage_ha.py --input irw_triage.csv --out irw_retriage_ha.csv
```

Sub-classifies each `human_assistance` row into `not_item_response` /
`aggregate_continuous` / `wrong_file_selected` / `recoverable_format` /
`worth_retrying` / `human_review` (see README for what each means and the
typical action). Usually resolves ~60% of the bucket automatically.

**Only rows whose `refined_flag` is literally `human_review` go into
`human_review/`.** Write them to
`human_review/human_review_<mode>_batch<N>.csv` in this repo (e.g.
`human_review_pmc_batch1.csv`, `human_review_plos_batch27.csv`,
`human_review_batch14.csv` for the repository-discovery mode) — a
permanent, git-tracked archive, replacing the old "human eye" queue-sheet
tab (deprecated 2026-08-12). These files are never deleted and nothing
needs to be pasted anywhere; they double as the exclusion list new
discovery runs check (see Step 1). The other five buckets are **not**
human-review rows and must **not** go in `human_review/` — they still need
machine-side follow-up (a re-download, a re-read with a different
delimiter, a second look for a wave column, etc.) before anyone can decide
anything, so they stay exactly where they already lived: dropped
(`not_item_response`, and `aggregate_continuous` when it's a genuine
composite), or kept on disk as the batch's own retriage CSV with an open
`TODO.md` entry until acted on (`recoverable_format`, `wrong_file_selected`,
`worth_retrying`, and `aggregate_continuous` when it turns out to be a
legitimate continuous per-item response).

**When reviewing `human_review` rows by hand, check the reason string
first.** Rows whose only reason is "Could not confidently identify item
columns" are disproportionately real, recoverable datasets, not ambiguous
ones — see README's Step 1b for why and the two specific fixes to try
(header-row offset, text-Likert item columns) before spending real time on
one.

## Step 3 — Write the processing script and QC it

**Note:** the README still documents an older `irw_process_queue.py` →
`irw_output/queue/` → `cleaned_index.csv` flow. Per `BATCH_LOG.md`'s
"Workflow notes (2026-06-24)", that intermediate stage was eliminated —
`irw_process_queue.py` is stale and should not be run. `irw_output/queue/`
and `cleaned_index.csv` no longer exist. The README hasn't been updated to
match; treat `BATCH_LOG.md`'s latest workflow notes as authoritative over the
README when they conflict.

**Before writing a new script, check the DOI hasn't already been shipped
via a different pathway.** `pmc_seen_dois.csv`/the PLOS equivalent only
catch re-*discovery* within the same connector, and only once that file
exists and is up to date — they don't catch a DOI that was already turned
into a `data/*.py` script through a different route (e.g. a manual
worth_retrying/deferred-candidate pass) earlier the same day, before that
run's bookkeeping was committed. Run
`grep -rl "DOI: <the doi>" ../data/*.py` (scripts embed the source DOI in
their header comment, see e.g. `data/moon_2023_pregnancy_stress.py`) before
writing a new script for any candidate — if a script already exists for
that DOI, stop and reconcile with the existing one instead of writing a
second, independent script. (2026-08-12: this exact gap let
`10.7717/peerj.16295` get shipped twice — once via a deferred-candidate
resolution pass, again ~3.5 hours later via the next weekly discovery run,
because `pmc_seen_dois.csv` didn't exist yet when the second run's search
executed. Two conflicting `data/moon_2023_*.py` scripts and biblio rows
were both uploaded before the duplication was noticed.)

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

- **PII in the raw source file — skip the dataset entirely, don't
  scrub-and-ship.** `datastandard.md`'s "no PII" checklist item is phrased
  as "don't include it in the output," which reads as permission to drop
  the offending column(s) and process the rest. That's not the policy for
  this pipeline: if the raw supplementary file contains real names,
  emails, birthdates, IP/GPS, or national ID numbers *anywhere* — even in
  a column that would never be selected as an item or covariate — treat
  the whole candidate as skip, the same tier as an unresolvable license,
  not a fixable QC warning. Decided 2026-08-12 after two PMC-connector
  candidates surfaced real PII (a participant email column on a study of
  LGB medical students' mental health — skipped outright given the
  compounding sensitivity of email + stigmatized-identity data on a
  narrow population; a real `date of birth` column on an otherwise
  unremarkable nursing-profession opinion survey — also skipped, even
  though that case looked "lower severity" and the standard fix would
  have just been dropping one column). The point of a blanket rule is to
  not re-litigate severity per candidate — a source file containing PII at
  all is reason enough to skip, regardless of how contained the fix would
  otherwise look. Log the skip in `BATCH_LOG.md` with what the PII was and
  why, same as a license-blocked candidate, but there is no
  `pii_blocked_candidates.csv` standing file — unlike a license issue,
  there's no path to later un-blocking a PII-flagged candidate, so nothing
  needs to persist past the batch writeup.
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
- **Sample size floor is N(unique id)>=100, flat, no ask-first band.**
  Originally a hard floor of 50 with a 50-99 ask-first band (set
  2026-08-01), simplified 2026-08-12 (memory `feedback_min_sample_size`) —
  the middle band was adding a round trip per candidate for marginal
  value. Check unique `id` count before writing a script; N<100 → skip
  outright and log why, the same as any other skip, no need to surface it
  to ben-domingue first. Don't reintroduce a 50-99 holding pattern in
  `TODO.md` — a batch that logs candidates as "awaiting a ben-domingue
  go/no-go" between N=50 and 100 is re-litigating an already-decided
  question (happened once, 2026-08-12, PLOS batch 27/PMC batch 4 — fixed
  same day once caught).
- **Same instrument across multiple samples → one merged file, not
  split files.** When a paper gives the *same* instrument (same items,
  same response scale) to two or more independently-recruited samples,
  ship one file with a `cov_study` covariate distinguishing the samples,
  even if the paper's own Data Availability listing splits them into
  separate SI attachments (e.g. "S1 Data"/"S2 Data"). Only merge when the
  paper's Methods text or a clear structural match (identical item
  columns, identical response range) confirms identical administration —
  see `datastandard.md`'s "Confirmed identical administration" guidance —
  and offset the second sample's `id` past the first sample's actual
  observed max rather than assuming a round-number gap is enough (raw id
  columns can be household-style codes well into six digits, not small
  sequential integers). `powell_2018_empathy.py` did this correctly the
  first time; `wen_2022_pyd.py` split two same-instrument samples into
  separate files and was corrected after the fact (ben-domingue,
  2026-08-12) — see memory `feedback_collapse_same_instrument` for the
  full rationale.

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

## Alternate discovery source: single-journal search (PLOS ONE) (mode 1)

`irw_discover_plos.py` is a different discovery mode from Steps 1-4 above,
not a variant of them — it searches a single open-access *journal* rather
than a data *repository*. Use it when the user asks to search a journal
directly, or references PLOS ONE / Supporting Information files.

**Why this exists**: `irw_discover_updated.py`'s connectors all query
repositories (Dataverse/Zenodo/OSF/Dryad/Figshare/DataCite/...) for
dataset-shaped records. PLOS ONE papers instead commonly attach their raw
data directly to the article as a "Supporting Information" file — that data
is structurally invisible to every repo-based connector, since it was never
deposited in any of those systems. Confirmed in the 2026-07-26 pilot (see
`BATCH_LOG.md`): 32 `good` + 107 `worth_retrying` candidates from 22 terms
against one journal, none overlapping the IRW dictionary.

```bash
python irw_discover_plos.py "PHQ-9" "self-esteem scale" --out plos_triage.csv
python irw_discover_plos.py "term" --limit 10 --out plos_test.csv   # sanity check first
python irw_discover_plos.py "term1" "term2" --out plos_triage.csv --resume   # after an interrupted run
```

- **Term selection: recycle non-PLOS terms from `search_terms_log.csv`
  before inventing new ones.** `search_terms_log.csv` is a shared record
  across *every* discovery mode — each row's `file` column ties it to the
  specific triage output it was run against (a repository-connector
  `candidates.csv`/batch file, or a `plos_batch*_triage.csv`). A term
  already used against Dataverse/Zenodo/OSF/etc. has never been run against
  PLOS ONE, since that's a completely separate search surface
  (`api.plos.org` full-text/Solr vs. repository connector APIs) — reusing
  it is not a duplicate query. Batches 1–11 picked fresh instrument names
  each time and never checked this, which means a large pool of
  already-validated real instrument/construct/task terms (searched
  successfully elsewhere, proven to surface genuine datasets) sat unused
  for PLOS while newly-brainstormed terms — no better a priori, and
  unvalidated — were used instead. Before a new batch: filter
  `search_terms_log.csv` to rows whose `file` does NOT contain "plos",
  exclude any that (case-insensitively) match a term already in a
  `plos_batch*` row, and prioritize picking from what's left (favor terms
  that read as clean instrument/construct/task names) over inventing new
  ones from scratch. Batch 12 (2026-07-30) did this for the first time —
  see `BATCH_LOG.md`'s batch 12 entry for the method and results. The
  candidate pool is large (~1,200 unused-for-PLOS English terms found in
  one pass) — expect several more batches' worth before this pool runs dry.
- Two phases in one script: a cheap Solr search against `api.plos.org`
  (filtered to PLOS ONE's eissn `1932-6203`, not the journal name string —
  PLOS's own metadata inconsistently capitalizes "PLoS ONE" vs "PLOS ONE"),
  then per-candidate it fetches the article page, reads the Data
  Availability statement, and pulls any Supporting Information file with a
  tabular-looking declared format (CSV/XLSX/XLS/SAV/DTA). Same
  `triage_dataset()`/`load_table()` gate the regular pipeline uses.
- Also records any external-repo DOI mentioned in the Data Availability
  statement (`external_link` column), including bare unlinked DOIs like
  `doi: 10.5061/dryad.xxxx` — a lead worth chasing through the regular
  repo-based pipeline instead, not something this script re-downloads.
- **Expect roughly a 1% `good` rate and another ~2-4% recoverable via
  `irw_retriage_ha.py`** on the raw candidate pool (same retriage script,
  no changes needed — it works on this output unmodified). ~77% land in
  `no_usable_file` (data withheld, or the paper's data is only in an
  external repo already reachable via the regular pipeline).
- **Crash isolation is built in**: `pyreadstat`'s `.sav` parser can segfault
  outright on a corrupt file — a C-level crash that bypasses Python's
  try/except, which took down an entire unattended run before this was
  fixed (see `BATCH_LOG.md`). Each candidate now runs in its own worker
  process; a crash or >90s hang is recorded as a `crashed`/`timeout` row and
  the batch continues. Don't remove this to "simplify" the script.
- **Multi-term runs are slow** (single-domain rate limit against
  `journals.plos.org`, one article fetch each) — expect on the order of
  hours for a few thousand candidates. Launch in the background.
- **A `good` flag here needs a human glance more than usual.** The article
  often has multiple Supporting Information files, and the script only
  inspects the first tabular one per candidate — that can be a codebook or
  derived subscale-totals file rather than the raw item data (caught
  exactly this in the pilot: an MBI burnout study's first SI file held only
  aggregate subscale sums; the real 22-item data was in a different SI
  attachment). Before writing a processing script, fetch the article page
  and check `extract_si_files()`'s full list, not just the file the triage
  row used.
- **Generalizing to other journals**: PLOS's other journals (PLOS Medicine,
  PLOS Global Public Health, PLOS Mental Health, PLOS Digital Health) share
  the same `api.plos.org` index — swapping the eissn filter (or dropping it
  to search all PLOS journals at once) is close to zero new code. BMC
  journals (BMC Psychology, BMC Psychiatry, ...) were spot-checked and are
  also server-rendered with a scrapable "Data availability" +
  "Additional file N" structure, but need a new per-site parser. Frontiers
  was spot-checked and is a client-rendered JS SPA — not scrapable the same
  way; would need a headless browser or their internal API. Don't build a
  new-journal connector speculatively — numFound-check the term yield via
  `api.crossref.org` first (publisher-agnostic, works for any journal by
  `container-title` + bibliographic query), same as this pilot did before
  committing to a full run.

## Alternate discovery source: Europe-PMC-based multi-journal search (mode 2)

`irw_discover_pmc.py` generalizes the single-journal-search idea above to
any journal that's well-indexed in Europe PMC, without writing a new
publisher-specific scraper for each one. Use it when the user asks to
search a non-PLOS open-access journal directly, or references the
`journal_scout/` yield study.

**Why this generalizes where `irw_discover_plos.py` couldn't**: that
script works by scraping `journals.plos.org`'s article HTML, which is
PLOS-specific plumbing — the earlier note about BMC needing a new parser
and Frontiers being an unscrapable JS SPA was written against that
approach. `irw_discover_pmc.py` never touches a publisher's own website:
it calls Europe PMC's `{PMCID}/supplementaryFiles` endpoint, which returns
an article's Supporting Information archive the same way regardless of
publisher, as long as the article is deposited in PMC. One connector, many
journals — the engineering cost of adding a journal is close to zero
*if* it's well-indexed in Europe PMC (see the caveat below; several are not).

```bash
python irw_discover_pmc.py "PHQ-9" "self-esteem scale" --out pmc_triage.csv
python irw_discover_pmc.py "term" --limit 10 --out pmc_test.csv   # sanity check first
python irw_discover_pmc.py "term" --journals peerj,heliyon --out pmc_triage.csv   # subset of journals
python irw_discover_pmc.py "term1" "term2" --out pmc_triage.csv --resume   # after an interrupted run
```

- **Term selection**: same rule as the PLOS section above — recycle terms
  from `search_terms_log.csv` that haven't been run against this source
  yet (`file` column won't mention "pmc"), rather than inventing new ones.
  This is a distinct search surface from both the repo connectors and
  `irw_discover_plos.py`, so a term already used against either is not a
  duplicate query here.
- **Which journals are in `JOURNALS`, and why not more**: the list is the
  "harvest now" / "sample manually first" tiers from a dedicated yield
  study — `journal_scout/journal_yield_summary.md` (2026-08-11/12), which
  measured `pct_with_data_like_supp` on a reproducible 100-article sample
  per candidate journal against a PLOS ONE positive control, plus license
  mix and Europe-PMC-index reliability. **Don't add a journal to
  `JOURNALS` without a yield measurement backing it up** — the same
  "don't build a new-journal connector speculatively" rule from the PLOS
  section applies here, just at the level of adding an ISSN to a list
  instead of writing a scraper. The PLOS family (PLOS ONE and siblings)
  scored well in that study too but was deliberately kept on
  `irw_discover_plos.py` rather than migrated, to avoid running two
  discovery paths over the same journals.
- **Not every OA journal is reachable this way, even if it's fully open
  and CC-BY.** The yield study found several journals (Frontiers in
  Education, Journal of Statistical Software, Large-scale Assessments in
  Education, Collabra: Psychology, Education Sciences/MDPI) whose true
  publication volume — cross-checked against Crossref — is 6x-600x what
  Europe PMC's own ISSN search reports. Those journals are essentially
  invisible to Europe PMC's index regardless of their real yield, so this
  connector cannot reach them; check `journal_scout/journal_yield_summary.md`
  before assuming a plausible-looking journal is a `JOURNALS` candidate.
- **License is fetched per-candidate, not scraped from an HTML page**:
  `fetch_core_license()` reads the `license` field off Europe PMC's
  `resultType=core` record — same source `journal_scout`'s Step 4 used.
  Unlike PLOS's `extract_license()` (regex over the article page), this
  doesn't need the article's HTML at all.
- **No Data Availability / external-repo-link tracking** (PLOS's
  `external_link` column has no equivalent here) — this connector's whole
  point is the attached-SI-file path; chasing a DAS-mentioned external repo
  is the regular repo-based pipeline's job, and would need a full-text XML
  fetch per candidate this script doesn't do today. If that turns out to
  matter, it's a known gap, not an oversight — see the script's docstring.
- **Same crash isolation as `irw_discover_plos.py`**: `load_table()` can
  still hit a native segfault on a corrupt `.sav`/`.xlsx`, so each
  candidate runs in its own worker process, same as the PLOS script. The
  isolation harness is duplicated in `irw_discover_pmc.py` rather than
  imported from `irw_discover_plos.py` — each discovery script stays
  self-contained, matching the "no shared dependencies between scripts"
  norm the rest of the pipeline follows.
- **Re-running `journal_scout/`**: the study itself (resolve → yearly
  counts → sample → license → assemble) is five scripts in
  `journal_scout/`, each caching its raw API responses under
  `journal_scout/cache/` (gitignored, regenerable) with skip-if-exists —
  rerunning after editing `journal_scout/journals_candidates.py` only
  re-fetches what changed. See the scripts' own docstrings for the
  per-step detail; `journal_yield_summary.md` documents what couldn't be
  measured and why (the PMC Journal List's deposit-scope field has no
  scrapable/API path, so a same-source IN_PMC-ratio proxy is used instead;
  `SPRINGER_API_KEY`-gated Springer OA counts were skipped since no key is
  set in this environment).

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
   CSV handed to the user for the dictionary sheet. Don't delete a biblio
   CSV until the user has confirmed the rows were actually pasted into the
   dictionary sheet — check whether that item is still open in `TODO.md`,
   don't assume from an earlier "yes." **Never delete a
   `human_review/human_review_*.csv` or `license_blocked_candidates.csv`** —
   unlike the per-batch temp files, these are standing, cumulative records
   (like `search_terms_log.csv`), not disposable once a batch is written up.
   `human_review/` files in particular need no confirmation step at all —
   there's no sheet to paste them into anymore (deprecated 2026-08-12), the
   file written during the batch *is* the permanent record.
