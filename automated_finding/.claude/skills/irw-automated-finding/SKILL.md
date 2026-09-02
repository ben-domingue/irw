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

**This is enforced, not advisory.** Every entry point calls
`preflight_deps()` (in `irw_triage_updated.py`) as the first statement of
`main()`: it checks the optional readers, attempts a
`pip install --user --break-system-packages` for whatever is missing, and
aborts the run with `SystemExit` if any are still absent. Do not remove or
work around that call. The reason is concrete — a missing reader does not
fail loudly, it makes `load_table()` raise per-file, which the callers
record as a per-row `download_failed` that looks exactly like a dead URL,
and the DOI/key is then written to the seen ledger so the candidate is never
retried. The 2026-08-24 repos run and the 2026-08-25 PLOS run each lost
double-digit candidates this way (see `BATCH_LOG.md`).

**Cloud/CCR runs start from a bare sandbox.** `preflight_deps()`'s
auto-install handles this, but if the sandbox blocks outbound pip the run
will now abort rather than silently produce an all-`no_usable_file` result —
that abort is the correct outcome, and the fix is to install the packages in
the environment, not to skip the check.

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
5. **Know where files go: every per-run output belongs in `runs/`.**
   The candidate lists, triage outputs, retriage outputs, and sanity-check
   CSVs this pipeline generates all live in `automated_finding/runs/` —
   never at the top level of `automated_finding/`. Pass `--out
   runs/<name>.csv` explicitly; the scripts also route a bare `--out
   name.csv` into `runs/` themselves (`in_runs_dir()` in
   `irw_discover_updated.py`), and resolve a bare *input* filename to
   `runs/<name>.csv` if it isn't at cwd (`resolve_in_path()`), so an older
   command still works. `runs/` is gitignored in full — don't `git add -f`
   anything in it, and don't report a run as "committed" on the strength of
   a file being written there.

   What stays at the top level of `automated_finding/` is the standing,
   cumulative record — never write these into `runs/`:
   `search_terms_log.csv`, `plos_seen_dois.csv`, `pmc_seen_dois.csv`,
   `repo_triage_seen_keys.csv`, `license_blocked_candidates.csv`,
   `plos_deferred_candidates.csv`, any `pii_blocked_candidates.csv`, the
   `biblio_*.csv` handed to the user for the dictionary sheet, plus
   `BATCH_LOG.md`, `TODO.md`, and the `human_review/` directory. Rule of
   thumb: if deleting it after the batch write-up would lose information,
   it does not belong in `runs/`.
6. **Pick a discovery mode before running anything.** There are three
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
python irw_discover_updated.py "search term 1" "search term 2" --out runs/candidates.csv
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
python irw_batch_updated.py runs/candidates.csv --limit 10 --out runs/triage_test.csv   # sanity check first
python irw_batch_updated.py runs/candidates.csv --out runs/irw_triage.csv     # full run
python irw_batch_updated.py runs/candidates.csv --out runs/irw_triage.csv --resume   # if interrupted
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
- Sort `runs/irw_triage.csv` by `flag`, `good` first.
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
python irw_retriage_ha.py --input runs/irw_triage.csv --out runs/irw_retriage_ha.csv
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

**While you have the raw file open, note whether the item text is there** —
variable/value labels, stem-bearing column headers, a codebook in the deposit.
Step 3.5 turns that into a shipped item text table in the same batch, and it
is far cheaper to see now than to rediscover later. Record the verdict in the
script's header comment alongside the existing `Source:`/`DOI:`/`Data:`/
`License:` lines, whichever way it goes:

```
Item text: shipped (SPSS variable + value labels)
Item text: not shipped — labels are positional ("FTD-SS Item 1"); needs the published FTD-SS
```

That header is the only permanent per-candidate record of the source, so a
"not shipped" line is what stops the next pass re-deriving the same answer.

## Step 3.5 — Item text, when it's cheap

Item text ships **in the same batch as the response table**, not in a later
`irw-auto-itemtext` pass. Step 3 is the only moment when the raw deposit, the
source paper, and the item-code derivation are all in hand at once — a later
pass has to re-find the paper from the dictionary DOI and reverse-engineer
`data/<table>.py` to learn how the codes were assigned. It is also the safest
moment: of 50 tables audited by the itemtext pipeline, 10 had positional or
script-generated item codes and *every mapping defect found in review was one
of them*. Here you wrote that mapping, so it is known rather than
reconstructed.

**THE PRIME COMMANDMENT — `item` is the join key.** Every `item` value in the
item text table must appear in the response table, spelled exactly as the
response table spells it, and the two sets must match. Same for `resp`. Never
invent either one. A perfectly transcribed instrument whose `item` values
don't line up cannot be linked to a single response and is worthless.

### Do it only when the text is already in hand

Attempt extraction only from what Step 3 already gave you. Do **not** let item
text slow the batch down — the goal is still to maximize data in the IRW.

**Cheap — extract now:**

- SPSS/Stata variable labels *and* value labels (`pyreadstat` exposes both:
  `meta.column_names_to_labels`, `meta.variable_value_labels`). Check both
  levels — the stem is usually in the variable label, the response options in
  the value labels.
- Spreadsheet column headers that are full item stems.
- A codebook / questionnaire / data-dictionary file already in the same
  deposit.
- An appendix or supplementary file of the open-access paper already fetched.

**Not cheap — record and move on:**

- The paper is paywalled, or the instrument is a multi-hop citation away.
- The labels are positional ("FTD-SS Item 1", "Q1"), so the *published*
  instrument is needed to know what was asked.
- The wording exists only in a table *image* (OCR) or a third-party
  reproduction.

**A non-English administration is not a reason to skip.** This bullet used to
end "or a translated substitute". Since the administered-language columns
entered the schema on 2026-09-01 (#1774/#1777) that wording contradicts the
standard, and read literally it would have skipped seven correctly-extracted
tables in the PLOS weekly batch (#1783). Language handling is a *schema* rule,
not a triage rule, and it is owned by `itemtext_standard.md` -- see
"Administered language" there, and core model section 4 of
`irw-auto-itemtext`'s SKILL.md. Follow it there rather than re-deriving it
here.

When you skip, say **where the text actually is** in the `data/<table>.py`
header and in the `BATCH_LOG.md` entry, so a later pass starts from an answer
instead of re-deriving one. That is the whole cost of skipping — one sentence.

**Say which label levels you checked, not just what you concluded.** A skip
verdict is the one output here that nothing downstream re-tests: no gate runs
on a table that was never attempted, so the prose in the header is the whole
record. `estevez_2021_*` (#1770) was skipped on "no variable labels and no
value labels for any item"; the file carried value labels for all 82 shipped
items, and the verdict had been written from the variable-label level alone.
Name both levels — "no variable labels; value labels present but only on the
covariates", "both levels empty" — so the next reader can tell a checked
absence from an unchecked one.

Two carve-outs: **never extract item text for `enem*` tables** (Ben handles
those separately), and a table skipped for PII/license/N<100 has its item text
skipped with it.

### Schema and extraction rules — do not restate them here

The item text schema is defined in
`itemtext/.claude/skills/irw-auto-itemtext/references/itemtext_standard.md`
(paths in this section are from the repo root, `irw/src/`) — field
definitions, the `raw_resp` fallback, the merge logic. The extraction
judgment rules — `instructions` vs. `section_prompt`, when to leave
`item_text` blank rather than invent a stem, matching the source's terseness,
never padding an unlabeled scale point with its own number — are Step 4 of
`irw-auto-itemtext`'s SKILL.md. Read them there and follow them; this file
deliberately does not fork a second copy, for the same reason it defers the
response schema to `datastandard.md`.

The two rules worth repeating because they are what the gate actually
enforces: one row per item × response option, and `section_id` is never blank
(use `<table>_1` throughout when the instrument has no real testlet grouping —
the merge needs a join key).

### Output

Write to `automated_finding/itemtext_output/<table>__items.csv` — double
underscore, and the case of `<table>` exactly as the response table spells it.

Keep that directory to `*__items.csv` and the batch's own bookkeeping files.
An uploader walks a directory recursively, so a stray `provenance.csv` or
`notes.csv` used to be uploaded as if it were data -- this has happened, and it
is why `itemtext/itemtables/clean/` exists on the other side. `red_up` now
excludes anything that is not `*__items.csv` when the target is `irw_text`, and
names what it excluded, so a stray file is visible rather than uploaded. Do not
treat that as licence to leave junk there.

### Gate it against the staged response CSV

The response CSV must be **final** before item text is generated from it — the
item and resp sets are checked against the exact file that will ship. Run all
three, in order, from `itemtext/` (as the itemtext skill's own steps do):

```bash
cd itemtext
S=.claude/skills/irw-auto-itemtext/scripts

# 1. Canonical on-disk nulls. NOT optional: our processing scripts are Python,
#    and Python's csv writer emits "NA" where the corpus convention is a bare
#    NA token. Nothing downstream complains; the audit below will.
Rscript $S/normalize_nulls.R ../automated_finding/itemtext_output

# 2. Hard per-table gate — item set and resp set must match exactly.
Rscript $S/validate_items.R <table> \
    ../automated_finding/itemtext_output/<table>__items.csv \
    --resp-csv ../automated_finding/irw_output/<table>.csv

# 3. Batch-wide audit: per-item row-count anomalies, option coverage, blank
#    item_text, duplicate rows with conflicting text.
#    Give the report an explicit path OUTSIDE itemtext_output/ -- it defaults
#    to <dir>/audit_report.csv, which would leave a non-items CSV sitting in
#    the upload folder.
Rscript $S/audit_batch.R ../automated_finding/itemtext_output \
    ../automated_finding/runs/itemtext_audit_report.csv \
    --resp-dir ../automated_finding/irw_output
```

Before handing the batch over, confirm the folder is clean:

```bash
ls automated_finding/itemtext_output | grep -v '__items\.csv$'   # must print nothing
```

`--resp-csv` / `--resp-dir` are what make this work before upload: without
them both scripts read live Redivis data, which a table in this pipeline does
not have yet. A FAIL is disqualifying — fix it or ship the response table
alone. Explain every WARN rather than ignoring it.

### Decide whether the table needs an issues-page entry

The public issues page (`itemtext_issues.qmd` in the datapages/irw repo, checked
out at `irw/irw_site/itemtext_issues.qmd` -- a sibling of `src/`, not
`src/../irw_site/`) lists **concrete mismatches between the item text and the
IRW table**: the table has 6 items and the codebook 5, the paper describes a 1-7
scale and the table is on 1-5, the item codes don't identify what was asked.
That is the whole bar. It is not a place for gaps the source never published,
for ordinary missingness, or for a caveat about the study.

Two things make this a real step rather than a formality:

- **A non-empty `public_note` always forces a public callout**, even when the
  structured fields are clean (`draft_issues_qmd.R`, line ~100). So writing a
  chatty `public_note` publishes it. Put anything that is not a text-vs-table
  mismatch in `note`, which is internal.
- **A `data_labels` + `study_materials` table earns no callout by default** --
  the data file itself ties each code to its text, so there is nothing to
  caveat. If a cheap-gate table seems to need one, re-read the bar first.

`validate_items.R` and `audit_batch.R` will not find these for you: they check
item and resp sets at the **table** level, so a per-item defect can sit under a
PASS. Run this scan over the batch before deciding:

```python
# for each __items.csv with a staged response CSV
# 1. observed resp for an item with no option_text row  -> real mismatch
# 2. blank item_text                                    -> real gap
# 3. one item_text on two different items               -> conflation
# 4. option rows never endorsed for that item           -> NOT an issue
# 5. blank option_text at unlabeled midpoints           -> NOT an issue, required
```

Only 1-3 are issues-page material. 4 and 5 are normal and must not be published:
an unendorsed anchor is a fact about the responses, not a defect in the text, and
an unlabeled scale point is *required* to be blank rather than padded with its
own number (`audit_batch.R` warns when you pad it).

If a table does earn an entry, write the `public_note` as the one sentence that
would go in the callout, and say so in the batch's `TODO.md` handoff -- the page
lives in another repo and is edited there, not here.

### Record the provenance

Append one row per attempted table to `automated_finding/itemtext_provenance.csv`
(tracked, cumulative, never deleted at batch close — same class as
`license_blocked_candidates.csv`). Columns, matching the itemtext pipeline's own
record so the two stay diffable:

```
table,mapping_basis,text_source,source_ref,note,public_note,uploaded
```

- `mapping_basis` — how the item↔text tie was established: `data_labels` /
  `paper_explicit` / `paper_order` / `reconstructed` / `unknown`.
- `text_source` — where the wording came from: `study_materials` /
  `canonical_instrument` / `translated_substitute` / `unknown`.
- `public_note` — a one-sentence caveat for the public issues page, or blank.
- `uploaded` — a date, stamped **only** once Ben confirms. Never ahead of it.

Write it `QUOTE_ALL` with CRLF, matching the file's existing rows.

A cheap-gate table should almost always be `data_labels` + `study_materials`,
which is the one basis exempt from needing a `verify_<table>.R`. If you find
yourself writing anything else, that is a signal the table failed the
cheapness test — re-read the gate above before continuing.

Nothing needs mirroring into `itemtext/`. That pipeline derives its queue by
diffing live `irw_list_itemtext_tables()` against `irw_list_tables()`, so an
uploaded table drops out of it automatically, and a newly found table was
never in `queue_state.csv` to begin with.

## Step 4 — QC before submitting

Before uploading a file from `irw_output/` to Redivis, run through
`datastandard.md`'s "What to verify before saving" checklist — the QC
warnings recorded in the triage CSV point at exactly what to check.

If the batch also produced item text, its gate chain (Step 3.5:
`normalize_nulls.R` → `validate_items.R --resp-csv` → `audit_batch.R
--resp-dir`) is part of this checklist, and `itemtext_output/` must contain
nothing but `*__items.csv`. Item text is checked against the *final* response
CSV: if a table's response file changes after its item text was written — a
recoded `resp`, a dropped item, a renamed code — regenerate the item text and
re-run the gates. A stale item text table is worse than none, because it
still joins.

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
python irw_discover_plos.py "PHQ-9" "self-esteem scale" --out runs/plos_triage.csv
python irw_discover_plos.py "term" --limit 10 --out runs/plos_test.csv   # sanity check first
python irw_discover_plos.py "term1" "term2" --out runs/plos_triage.csv --resume   # after an interrupted run
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
python irw_discover_pmc.py "PHQ-9" "self-esteem scale" --out runs/pmc_triage.csv
python irw_discover_pmc.py "term" --limit 10 --out runs/pmc_test.csv   # sanity check first
python irw_discover_pmc.py "term" --journals peerj,heliyon --out runs/pmc_triage.csv   # subset of journals
python irw_discover_pmc.py "term1" "term2" --out runs/pmc_triage.csv --resume   # after an interrupted run
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

## Lessons that cost real work (added 2026-08-26)

Each of these came from a live failure in one session. They are cheap to
follow and expensive to rediscover.

**Run your own output through `run_qc()`.** A Step 3 script writes straight
to `irw_output/` and never touches triage, so *none* of the QC checks run on
it. The 2026-08-26 Eugene-Springfield build shipped 20 tables in which nine
mixed two or more response scales, plus two administrative columns
(`submiss`, `smiss` -- missing-response counts) carried as items, and nothing
objected. Two checks now exist for exactly this — `resp_scale_mixed` (fail)
and `item_scale_outlier` (warn) — but they only help if the script calls them.
Import `run_qc` and assert no `fail` before writing.

**A script that drops columns must balance its books.** After melting, assert
that every source column is either in the output or was skipped for a printed
reason. The same build silently lost ~1.0M responses -- two entire mailings of
person-descriptive adjectives -- because each adjective is its own column, so
under a group-by-prefix rule each became a one-item group and fell below the
minimum block size. 1,205 skip lines scrolled past unread. Worse, the loss was
invisible in the totals: it landed in the same change that correctly dropped
~1.1M possession counts, so the grand total barely moved.

**Assert output filenames are unique.** Two blocks that resolve to the same
table name overwrite each other with no error. Caught only because a table
appeared twice in a build log.

**Rank candidate pools by instrument shape, not response count.** Sorting
leads by `n_responses` puts census-scale replication files on top -- millions
of "participants" by a dozen "items" -- and none of it is item-response data.
This produced a "top eight leads, nothing shippable" result twice before the
pattern was recognised. Filter to roughly `100 <= N <= 50,000` and
`8 <= items <= 700`, or score by the presence of a coherent block of columns
sharing a prefix and a small ordinal range.

**Take landing URLs from the lead row; never reconstruct them.** A figshare
URL rebuilt from a Frontiers supplementary DOI fetched a completely unrelated
genomics table. Supplementary DOIs do not encode the figshare article id.

**Read author names off the deposit record.** A script was written as
`zhang_2024_*` on an assumption; the contributor was Jinchang Peng.

**Two response categories belong in core, not nominal.** With exactly two
options the ordered/unordered distinction is vacuous -- a dichotomy is
trivially ordinal and standard dichotomous IRT applies. An option-coded
column is a nominal-standard candidate only at **three or more** categories.

**Hand biblio rows over as a fully-quoted `.csv` for `File > Import`, NOT as a
`.tsv` for pasting.** (Superseded the previous advice on 2026-08-27 -- that
said the opposite; see below for why both halves were half-right.)

The old rule said `.tsv`, because Google Sheets' *paste* splits text on commas
without honouring CSV quoting, so every comma inside a `Description` or
`Reference` becomes a column break. That part is still true of the paste path.
But `.tsv` fails the paste path too, for a different reason: the dictionary
format mandates three always-blank columns -- H and K (`Custom License` x2) and
L (`Notes`) -- which in a TSV become consecutive tabs. Sheets' text-to-columns
collapses repeated delimiters into one; OpenOffice does not. So a TSV opens
correctly in OpenOffice and misaligns in Sheets, shifting `Contributor` and
`Date` three columns left. Re-copying the cells out of OpenOffice does not
help -- the clipboard still carries text that Sheets re-splits.

The fix is to change the *delivery path*, not the delimiter. Sheets' **import**
honours both RFC4180 quoting and empty fields, where its paste honours
neither. So:

- Write the file with `csv.QUOTE_ALL`, LF terminators, pure ASCII.
- Tell ben-domingue: **File > Import > Upload > Import location: "Append to
  current sheet" > Separator type: comma.**
- Confirmed working 2026-08-27 on a 121-row batch: all 121 rows landed
  contiguous at 14 columns with zero field mismatches across 1,694 cells.
  An `.xlsx` also works and avoids delimiters entirely, but the quoted CSV is
  what was actually verified end-to-end.

**Verify a paste/import by exporting the target tab, not by re-checking the
file.** The dictionary tab is gid `1337607315`
(`https://docs.google.com/spreadsheets/d/<id>/export?format=csv&gid=1337607315`
-- the default export returns a cover tab instead). Diff it field-by-field
against the source rows. On 2026-08-27 that localised a problem to one column
in 8 rows and simultaneously proved alignment, completeness and no-duplicates
for everything else; two rounds of re-checking the file itself had found
nothing, because the file was fine.

**Emit the `Date` column pre-formatted as `M/D/YYYY`, never ISO.** The sheet's
own convention is `M/D/YYYY` (3,474 rows vs 206 in ISO). Handing Sheets
`2026-08-27` and letting it auto-convert is unreliable -- on 2026-08-27 it
converted 113 of 121 rows and left 8 as literal left-aligned text.

**`csv.writer` defaults to CRLF.** Its `lineterminator` is `\r\n`, and opening
the handle with `newline=""` preserves it. Pass `lineterminator="\n"`
explicitly and verify with `file X.csv` (should not say "CRLF line
terminators").

**Keep fields boring anyway.** A 55-row biblio once failed to paste
repeatedly while being verifiably well-formed, and the cause was never found
(see `BATCH_LOG.md`, 2026-08-26). Since the failing component is the paste
path and it cannot be inspected, the cheap insurance is to keep every field
to plain prose: no tab, newline, carriage return or double quote, no leading
`=`, `+`, `-`, `@` or `'` (Sheets reads those as formula or literal-text
prefixes). Quotes in a `Reference` are decorative -- APA does not quote
article titles -- so strip them. **Do not claim to know what Sheets does to a
pasted quote**; that was asserted here once on a coincidence and did not hold
up when tested.

**Check that per field, never per line.** `'\t' in line` is vacuously true for
every line of a TSV, so a file-level substring test for the delimiter catches
nothing. Iterate fields:

    for r in rows:
        for v in r:
            assert not (set('"\t\r\n') & set(v))

**When a paste goes wrong, read the target sheet before theorising.** Fetch
its CSV export: it shows the real header (so a layout mismatch is ruled in or
out immediately) and exactly which rows landed and how they aligned. That one
step killed two plausible-looking theories at once and showed nothing had
half-landed. Verifying the *file* again is the wrong instinct once the file
has already been checked -- the fault is downstream of it.

**On Dataverse, download `format=original`, not the `.tab` conversion.** One
batch hit three distinct defects from the conversion alone: SPSS user-missing
cells arrive as `0` (a spurious sixth category on a 1-5 scale), a workbook's
trailing codebook-legend row is coerced to missing and silently dropped, and
`.sav` variable labels -- which is where a deposit admits to being
`SMEAN(...)`-imputed -- do not survive at all. The conversion is lossy in ways
that look like clean data.

**A fractional value in a Likert column is an imputation until proven
otherwise.** Chase it: if the non-integer cells each equal the column's mean
over the integer cells (or its reflection, when a reverse-code was applied
after imputation), the file is mean-imputed and those cells must be dropped,
not shipped.

**An item's observed maximum is not its scale.** `run_qc`'s
`resp_scale_mixed` reads it as one, so a rarely-endorsed top category on a few
items of a subscale trips it. Check the response distributions before
splitting: a handful of respondents reaching 7 on one item of four, with the
rest topping out at 6, is one left-skewed scale, not two. Waive the check
through a named, printed exemption rather than either splitting a real
subscale or silently dropping the assert.

**Demographics deposited as regression dummies are recoverable.** Take the
index of whichever indicator is 1, and the omitted index where none is -- the
omitted index *is* the reference category. That turns "skip, dummy expansion"
into eight real covariates.

**Get sheet column layouts from the live sheet, not from `metadata/`.**
`metadata/biblio.csv` and `metadata/nominal_biblio.csv` are Redivis snapshots
*regenerated from* the sheets; their headers are sanitised
(`DOI__for_paper_`) and identical to each other, so neither is a paste format.
Fetch the sheet's own CSV export and read row 1. The nominal sheet in
particular is close to the core dictionary but not the same: `table lower`
with a space, a single `Custom License` rather than two, and `Derived_License`
with an underscore.

## After finishing a batch

1. Append a dated entry to `BATCH_LOG.md` summarizing what ran and what was
   decided (new search terms used, candidate counts, good/skip decisions,
   batch/table names) — following the existing style already in the file.
   This is what lets the next run (by Claude or a human) avoid repeating
   work. Include one item text line per shipped table: shipped (and from
   what), or not shipped and where the text actually is.
2. Reconcile `TODO.md`: remove any item the batch resolved, add any new
   open item the batch surfaced (an on-hold dataset, an uninvestigated
   `worth_retrying` case, a pending upload). The pending-upload checkbox
   covers **both** folders in one confirmation, e.g.
   `- [ ] biblio_X.csv (N rows) + M item text tables need uploading/pasting`.
   `TODO.md` should always reflect
   only what's currently actionable — don't let resolved items linger there
   the way they used to linger unchecked in the old combined file.
3. Delete temp files once their content is captured elsewhere — this
   pipeline generates several per batch, all of them under `runs/`
   (`runs/candidates*.csv`, `runs/irw_triage*.csv`, `runs/irw_retriage*.csv`,
   any `runs/triage_test*.csv` sanity check, plus
   `irw_batch_checkpoint.jsonl` at top level) and they're disposable *once* every
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
   **Never delete `itemtext_provenance.csv`** either — it is a standing
   record, not a per-batch temp file.

### Uploading a batch that includes item text

The two folders go to two different Redivis datasets, in this order:

| Folder | Dataset | Upload with |
|---|---|---|
| `irw_output/` | the newest warehouse shard | `red_up irw_output` |
| `itemtext_output/` | `irw_text` | `red_up itemtext_output` |

`red_up` picks both defaults itself -- a directory of `*__items.csv` goes to
`irw_text`, anything else to the newest shard -- and shows the target for
confirmation before it writes. Do not hardcode a shard number here again: this
table used to name `item_response_warehouse_4` and went stale two shards ago.
`red_up` also checks every shard for a table of the same name first, because a
copy in a newer shard shadows the older one rather than replacing it. See
`src/red_up/README.md`.

**Response tables first.** Item text that references a table which isn't live
yet is a dangling reference.

**A held or rejected response table holds its item text with it.** If Ben
doesn't ship a table, don't ship its `__items.csv` — say so explicitly rather
than letting it ride along.

Stamp `uploaded=<date>` in `itemtext_provenance.csv` per table, only after
Ben confirms, never ahead of it. Uploading is always human-triggered; don't
run either upload script yourself.
