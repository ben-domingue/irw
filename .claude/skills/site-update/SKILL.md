---
name: site-update
description: Use this skill when asked to regenerate or refresh the IRW dictionary, metadata, tags, or biblio CSVs that feed the Redivis "irw_meta:bdxt" dataset (metadata.csv, biblio.csv, tags.csv, comps_metadata.csv, nominal_metadata.csv, simsyn_metadata.csv, comps/nominal/simsyn biblio.csv, hero_stats.json), or to audit/reconcile table names across the metadata/tags/biblio tables and the live Redivis IRW datasets. Also applies to phrases like "run the metadata pipeline", "update Redivis metadata", "check for table name mismatches", "add item_response_warehouse_3 to metadata", or "which tables are missing from the dictionary/tags/biblio".
---

# IRW Site/Metadata Update

Two workflows over the `metadata/` pipeline (`ben-domingue/irw`, this repo). Both
**call the actual numbered R scripts in `metadata/`** — this skill never
reimplements their logic, only orchestrates them and reports what changed.
Everything here works from the repo root; the numbered scripts themselves
expect to run with `metadata/` as the working directory (matching their
existing convention, e.g. `09_hero_status.R`'s docstring).

Confirmed with Ben (2026-07-27) — see `references/pipeline.md` for the full
script-by-script writeup this was built from:

- Core pipeline order: `01_metadata.R` → `02_biblio.R` → `03_tags.R` →
  `05_comps.R` → `06_nominal.R` → `07_simsyn.R` → `09_hero_status.R` (must run
  **last**, it reads `metadata.csv` written by 01).
- **`05` and `06` are excluded from `run_pipeline.sh`'s default order as of
  2026-07-28 — read `TODO.md` before touching either.** `05_comps.R` has
  three confirmed bugs (wrong column list, an undefined `toadd` variable, and
  a final write that silently ignores the freshly-computed data) found during
  a live run; `06_nominal.R` looks structurally sound on inspection but was
  never actually verified standalone. Don't assume 06 is broken just because
  05 is, and don't attempt to fix either without first reading `TODO.md`'s
  full trace of what's actually wrong — a narrow patch to the reported crash
  alone would leave 05 "succeeding" while still silently doing nothing.
- `04_tables.R` (QC) is being superseded by this skill's audit workflow —
  details of exactly how are still being worked out with Ben; don't assume
  `04_tables.R` itself needs to keep running standalone.
- `08_itemtext.R` (itemtext readability stats) is out of scope here — it
  belongs to the separate `itemtext/` pipeline area.
- `metadata/hotfixes/` is out of scope for now (Ben, 2026-07-27) — don't run
  anything in there as part of this skill.

## Before doing anything

- **Prerequisites**: Redivis credentials configured externally (per root
  `CLAUDE.md` — not this repo's concern), `ANTHROPIC_API_KEY` set in the
  environment (used by `02_biblio.R`'s BibTeX-generation fallback — a plain
  single-turn `claude-haiku-4-5` call via `httr`, no SDK, swapped in from an
  earlier OpenAI/GPT-4o implementation on 2026-07-27; it will otherwise
  prompt interactively — fine in a foreground run, don't run that stage
  unattended without it set). R packages: `redivis`, `gsheet`, `dplyr`,
  `tidyr`, `tibble`, `httr`, `glue`, `progress`, `jsonlite`, `purrr`,
  `readr`, `irw`.
- **Nothing here uploads to Redivis.** Every numbered script just writes a
  local CSV/JSON. Getting that data into the actual `irw_meta:bdxt` Redivis
  tables is a separate, manual step outside this skill's scope — don't
  attempt it, and don't tell Ben something was "uploaded" when it was only
  regenerated locally.
- **Never silently overwrite.** Workflow 1 always snapshots before running
  and diffs after — if you're ever tempted to skip the diff step to save
  time, don't; that diff is the whole point (see "Safeguards" below for why
  this matters more than it looks).

## Workflow 1 — Generate metadata CSVs for Redivis upload

Regenerates the small local CSVs that get merged (by hand) into the
dictionary/tags/biblio/metadata Redivis tables, from whatever's new in the
source Google Sheets or newly live in Redivis (e.g. a new
`item_response_warehouse_3` table, or an edited dictionary-sheet row).

```bash
scripts/run_pipeline.sh                 # full default sequence: 01 02 03 07 09 (05/06 excluded, see TODO.md)
scripts/run_pipeline.sh 01 03           # only metadata.csv + tags.csv
scripts/run_pipeline.sh --no-09         # everything except the hero JSON
scripts/run_pipeline.sh 05              # try the known-broken comps stage explicitly
```

What it does, per stage:
1. Snapshots any existing output CSV(s) for that stage to a temp dir.
2. Runs the real `Rscript NN_*.R` from `metadata/` — unmodified, exactly as
   Ben runs it by hand.
3. Runs `scripts/diff_csv.py <snapshot> <new>` for each output CSV, keyed on
   `table` (case-insensitive). Prints rows added / removed / changed, and
   writes a `<name>.diff.csv` next to the real output — open that to review
   changed cells side-by-side before pasting anything into Redivis.

`09_hero_status.R` writes JSON, not a keyed CSV, so it's reported separately
(just read the file / the script's own stdout).

**Always summarize the diff output back to Ben** — counts of added/updated
rows per file, table names for anything added or removed, and every
long-text flag verbatim (see below). Don't just say "ran the pipeline."

### Long-text review flags — read this before dismissing one

`diff_csv.py` flags any added/changed cell over ~500 characters (warn) or
~2000 characters (FLAG) in any output CSV. **This is a deliberate stopgap,
not a false-positive nuisance** — treat every FLAG as something to actually
look at, not auto-dismiss. See "Safeguards" below for why it exists and what
it is *not* a substitute for.

## Workflow 2 — Cross-table consistency audit

**Prerequisite: run workflow 1 first, in the same working directory.** This
audit reads the local `metadata.csv`/`biblio.csv`/`tags.csv`/etc. as-is — it
does not fetch or regenerate them from Redivis itself (confirmed with Ben,
2026-07-27: "we don't want these CSVs from redivis. we need to generate new
ones."). Only `irw::irw_list_tables()` (ground truth for what's live) is
fetched remotely. Running the audit against stale or missing local CSVs will
misreport those tables as absent everywhere.

```bash
scripts/run_pipeline.sh                                              # generate fresh CSVs first
cd metadata
Rscript ../.claude/skills/site-update/scripts/audit_tables.R
Rscript ../.claude/skills/site-update/scripts/audit_tables.R --skip-dict   # faster, skips the 4 Google Sheet pulls
```

Ground truth is `irw::irw_list_tables(source = c("core","comp","nom","sim"))`
— the exported R-package accessor already used by the tags/itemtext skills,
not a raw re-query of Redivis. It wraps exactly the Redivis datasets the
numbered scripts use: `core` → `item_response_warehouse`/`_2`/`_3` (01),
`comp` → `irw_competitions` (05), `nom` → `irw_nominal` (06), `sim` →
`irw_simsyn` (07).

**Expect ~90 seconds minimum for the default run, most of it in the `core`
fetch alone** (measured 2026-07-27: `core` ≈ 59s for 2233 tables, `comp` ≈
10s; `--skip-dict` avoids 4 more Google Sheets round-trips on top of that).
This is normal — don't assume it's hung and kill it early.

**Bucket A reproduces `04_tables.R`'s `zz` object exactly** (confirmed with
Ben, 2026-07-28, after a naive generalization — flag anything missing even
1 source — proved far noisier than `zz` ever was: 805 rows, most
uninformative). `zz`'s actual rule: missing **at least 2** of the applicable
sources (not just 1), and rows where the *only* source present is
`tags_csv` are dropped entirely ("I definitely don't want tag only").
Output is the same **wide, one-column-per-source shape** `zz` had — no
`present_in`/`missing_from` strings, just a `1`/blank grid you scan across,
same as `04_tables.R` printing `zz` to the console used to give Ben.
Writes **a fresh report every run** — nothing is tracked or accumulated
across runs (confirmed with Ben: he triages the current list by hand each
time, no queue file needed here unlike `tags/tags_queue_staging.csv`).

Output, all written to `metadata/` (path configurable via `--out`):
- `table_audit_report_incomplete.txt` — **the one to open first.** Fixed-
  width plain text, one row per table, columns `table | category | redivis
  | dictionary_sheet | biblio_csv | metadata_csv | tags_csv`, `1` for
  present / blank for absent — reads as an aligned grid directly, no
  spreadsheet needed. This is bucket A, full list, sorted worst-first
  (fewest sources present).
- `table_audit_report_incomplete.csv` — same data, comma-separated, for
  spreadsheet use.
- `table_audit_report.md`:
  - **A. Incomplete coverage** — same grid, markdown-table preview
    (truncates at 30 rows — use the `.txt` for the full list). This is the
    main triage list, and the one to lead with when reporting results back
    to Ben.
  - **B. Urgent** — live in Redivis but in *no* local CSV at all yet
    (usually just means re-run workflow 1).
  - **C. Near-duplicate / inconsistent names — not implemented yet.** A
    first attempt (edit distance across the full ~2200-table universe) was
    almost entirely false positives — things like `algner2022_cse` vs
    `algner2022_oss`, which are different subscales of the same study, not
    naming inconsistencies. Ben (2026-07-27): hold off designing this
    properly until there are real bucket-A examples to look at together.
    Don't try to resurrect the edit-distance approach without discussing it
    first.

**This is an adjudication aid, not an auto-fixer.** Never merge, rename, or
delete rows based on this report — hand Ben the report and let him resolve
it.

`04_tables.R`'s exact QC role alongside this audit is still to be worked out
with Ben — don't assume this replaces it outright.

## Safeguards (read before generating anything that resembles a description)

**Confirmed gap (2026-07-27, verified by grepping `metadata/`, `tags/`,
`itemtext/`)**: the hash-cache / similarity-flagged / `construct_description
= NA` + `provenance = "pending review"` system Ben originally described does
**not exist anywhere in this codebase today**. The only reference to
`construct_description` in the whole repo is one aside in
`tags/.claude/skills/irw-auto-tag/SKILL.md` calling it a hypothetical field
from a `metadata/03b_describe.R` that doesn't exist.

What *does* exist today, and why it matters:
- `03_tags.R` selects columns `c(1,6:12,3)` from the "IRW Tags" sheet into
  `tags.csv` — this happens to exclude column 4, "Context Text" (the
  **verbatim excerpt** field, confirmed against the live sheet header), so
  raw paper text never reaches the public `tags.csv` today. This is
  incidental to a hardcoded column index, not an explicit check — if that
  sheet's columns are ever reordered, this protection silently breaks with
  no error. **If you ever touch `03_tags.R`'s column selection, flag this
  explicitly to Ben before changing it.**
- `diff_csv.py`'s long-text flag (above) is this skill's stopgap for the
  same underlying concern — a public metadata/biblio/tags CSV should never
  gain a full paragraph of raw source text — but it's a length heuristic,
  not hash-based or similarity-based, and has no `provenance`/pending-review
  concept at all.

**If a future task asks this skill to generate a new paraphrased
description-type field** (e.g. an eventual `03b_describe.R`), that's the
moment to actually build the hash-cache + similarity-flag +
`provenance = "pending review"` system Ben described, rather than assuming
it already exists or bolting it on as an afterthought — ask Ben for the
specifics (similarity against what corpus, what triggers a flag) before
writing it, per `references/pipeline.md`'s notes on this gap.
