---
name: irw-site-update
description: Use this skill when asked to regenerate or refresh the IRW dictionary, metadata, tags, or biblio CSVs that feed the Redivis "irw_meta:bdxt" dataset (metadata.csv, biblio.csv, tags.csv, comps_metadata.csv, nominal_metadata.csv, simsyn_metadata.csv, comps/nominal/simsyn biblio.csv, itemtext_metadata.csv, collections.csv, collection_members.csv, hero_stats.json), to audit/reconcile table names across the metadata/tags/biblio tables and the live Redivis IRW datasets, or to actually upload those regenerated CSVs into the Redivis irw_meta tables. Also applies to phrases like "run the metadata pipeline", "update Redivis metadata", "check for table name mismatches", "add item_response_warehouse_5 to metadata", "which tables are missing from the dictionary/tags/biblio", or "upload biblio/tags/metadata to Redivis".
---

# IRW Site/Metadata Update

Three workflows over the `metadata/` pipeline (`ben-domingue/irw`, this repo).
Workflows 1 and 2 **call the actual numbered R scripts in `metadata/`** — this
skill never reimplements their logic, only orchestrates them and reports what
changed. Workflow 3 is this skill's own script (`upload_meta.py`) — there's no
existing numbered script to call, since uploading was previously a manual,
out-of-scope step (see `data/add2redivis/upload.py` for the sibling script
this was modeled on, which does the equivalent for the actual IRW data tables
rather than the metadata tables).
Everything here works from the repo root; the numbered scripts themselves
expect to run with `metadata/` as the working directory (matching their
existing convention, e.g. `09_hero_status.R`'s docstring).

Confirmed with Ben (2026-07-27) — see `references/pipeline.md` for the full
script-by-script writeup this was built from:

- Core pipeline order: `01_metadata.R` → `02_biblio.R` → `03_tags.R` →
  `05_comps.R` → `06_nominal.R` → `07_simsyn.R` → `08_itemtext.R` →
  `10_collections.R` → `09_hero_status.R` (must run **last**, it reads
  `metadata.csv` written by 01). `05`/`06` were fixed and `08` was added to the
  default order 2026-08-02 — see `TODO.md` for history if any of the three
  regress. **Numeric order is not run order**: `10` runs before `09`, and `04`
  is excluded entirely.
- **Collections (issue #1633, added 2026-08-29):** `10_collections.R` builds
  `collections.csv` + `collection_members.csv` from the version-controlled
  registry at `src/collections/registry.csv`. Alone among the stages it needs
  **no credentials and no Redivis access**, so it is fully reviewable offline.
  Adding a collection is a *data* change — one line in `registry.csv`,
  optionally one file in `src/collections/curated/` — and requires no edit to
  this skill, the R/Python packages, or the site. See
  `src/collections/README` for the rule grammar. Do not add per-collection
  branches anywhere.
- **Item text split of responsibility (confirmed with Ben, 2026-08-02): this
  skill produces metadata FOR item text that's already been procured; the
  separate `irw-auto-itemtext` skill (`itemtext/.claude/skills/irw-auto-itemtext/`)
  is what procures/extracts the item text itself** (writes
  `{table}__items.csv` from source papers — never touches
  `itemtext_metadata`). `08_itemtext.R` reads `irw::irw_list_itemtext_tables()`
  (tables whose item text is already available) and writes readability stats
  (Flesch-Kincaid etc.) to `itemtext_metadata.csv` — squarely "produce
  metadata for already-procured item text," so it lives in this skill's
  pipeline, not the extraction skill's. No code overlap between the two;
  only the incremental `08_itemtext.R` is wired into `run_pipeline.sh` — the
  full-recompute variant (`hotfixes/08_itemtext_recompute.R`) stays a
  deliberate, rare, manual operation outside the default pipeline.
- `04_tables.R` (QC) is being superseded by this skill's audit workflow —
  details of exactly how are still being worked out with Ben; don't assume
  `04_tables.R` itself needs to keep running standalone.
- `metadata/hotfixes/` (other than `08_itemtext_recompute.R`, see above) is
  out of scope for now (Ben, 2026-07-27) — don't run anything else in there
  as part of this skill.

## Before doing anything

- **Prerequisites**: a Redivis API token at `~/.redivis_api_token` (bare
  token value, no `REDIVIS_API_TOKEN=` prefix, `chmod 600` recommended —
  deliberately *not* `~/.Renviron`, since that also leaks into interactive
  `R` sessions and trips the redivis package's "deprecated and highly
  discouraged" interactive-token warning; see `run_pipeline.sh` and
  `audit_tables.R`, both of which load it from that file into their own
  process env only, 2026-07-28), `ANTHROPIC_API_KEY` set in the environment
  (used by `02_biblio.R`'s BibTeX-generation fallback — a plain single-turn
  `claude-haiku-4-5` call via `httr`, no SDK, swapped in from an earlier
  OpenAI/GPT-4o implementation on 2026-07-27; it will otherwise prompt
  interactively — fine in a foreground run, don't run that stage unattended
  without it set). R packages: `redivis`, `gsheet`, `dplyr`, `tidyr`,
  `tibble`, `httr`, `glue`, `progress`, `jsonlite`, `purrr`, `readr`, `irw`,
  plus `quanteda`/`quanteda.textstats` for stage 08's readability stats.
- **Workflows 1 and 2 never upload to Redivis.** Every numbered script just
  writes a local CSV/JSON, and the audit only reads. Don't tell Ben something
  was "uploaded" when it was only regenerated or read locally — that's what
  Workflow 3 is for, and it's a distinct, explicit action (see below), never
  an automatic side effect of running 1 or 2.
- **Never silently overwrite.** Workflow 1 always snapshots before running
  and diffs after — if you're ever tempted to skip the diff step to save
  time, don't; that diff is the whole point (see "Safeguards" below for why
  this matters more than it looks).

## Workflow 1 — Generate metadata CSVs for Redivis upload

Regenerates the small local CSVs that get merged (by hand) into the
dictionary/tags/biblio/metadata Redivis tables, from whatever's new in the
source Google Sheets or newly live in Redivis (e.g. a new
`item_response_warehouse_6` table, or an edited dictionary-sheet row).

```bash
scripts/run_pipeline.sh                 # full default sequence: 01 02 03 05 06 07 08 09
scripts/run_pipeline.sh 01 03           # only metadata.csv + tags.csv
scripts/run_pipeline.sh --no-09         # everything except the hero JSON
scripts/run_pipeline.sh 08              # just the itemtext metadata stage
scripts/run_pipeline.sh 10              # just the collections tables (no credentials needed)
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
Rscript ../.claude/skills/irw-site-update/scripts/audit_tables.R
Rscript ../.claude/skills/irw-site-update/scripts/audit_tables.R --skip-dict   # faster, skips the 4 Google Sheet pulls
```

Ground truth is `irw::irw_list_tables(source = c("core","comp","nom","sim"))`
— the exported R-package accessor already used by the tags/itemtext skills,
not a raw re-query of Redivis. It wraps exactly the Redivis datasets the
numbered scripts use: `core` → `item_response_warehouse`/`_2`/`_3`/`_4`/`_5`/`_6` (01),
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

## Workflow 3 — Upload the regenerated CSVs to Redivis

**Prerequisite: run workflow 1 first, in the same directory, and review its
diff output.** This is the manual-merge step workflows 1/2's docs used to
describe as entirely out of scope — it's now in scope, as its own explicit,
confirmed action, added 2026-08-02.

```bash
cd metadata
python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py            # all known files present in cwd
python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py biblio tags # only these
python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --dry-run  # show the plan, upload nothing
python3 ../.claude/skills/irw-site-update/scripts/upload_meta.py --yes      # skip the confirmation prompt
```

What it does: for each known local CSV present (`metadata.csv` → table
`metadata`, `biblio.csv` → `biblio`, `tags.csv` → `tags`,
`comps_biblio.csv`/`nominal_biblio.csv`/`simsyn_biblio.csv` →
`comps_biblio`/`nominal_biblio`/`simsyn_biblio`,
`comps_metadata.csv`/`nominal_metadata.csv`/`simsyn_metadata.csv` →
`comps_metadata`/`nominal_metadata`/`simsyn_metadata`, `nominal_tags.csv` →
`nominal_tags`, `itemtext_metadata.csv`
→ `itemtext_metadata`, `collections.csv` → `collections`,
`collection_members.csv` → `collection_members`), it fully replaces that
table's data on
`redivis.user("datapages").dataset("irw_meta", version="next")` — a **draft**
version. `hero_stats.json` is deliberately not in this list; it isn't a
Redivis table, it goes to the separate `irw_site` repo.

**Nothing is live after this runs.** `version="next"` writes to a draft —
review and publish it by hand on the Redivis site afterward. This mirrors
`data/add2redivis/upload.py`'s existing pattern for the IRW data tables
themselves.

**Credentials are deliberately separate from workflow 1/2's token.**
`~/.redivis_api_token` (used by `run_pipeline.sh`/`audit_tables.R`) is
read-only — confirmed 2026-08-02, every table in `irw_meta` returned `403
insufficient_scope: data.edit` when tested. `upload_meta.py` instead uses the
write-scoped token, resolved — like every other IRW uploader — by the shared
helper `src/irw_secrets.py` (`load_write_token()`), which reads, in order: an
already-exported `REDIVIS_API_TOKEN`, then `~/.config/irw/redivis-write.env`.
Never read or echo the value directly. Rotate in that one file and every
uploader picks it up; don't invent a second write-scoped token file for this
script alone. Note `~/.config/` is outside Dropbox and does not sync, so each
machine needs its own copy of it.

Before replacing a table, it lists that table's existing uploads and warns if
there's more than one upload name present — `replace_on_conflict` only
replaces the upload named after the table itself, so a stray differently-named
upload left over from manual work would silently survive a "replace" and
could leave stale rows. This is a warning, not an auto-fix — investigate on
the Redivis site rather than assuming the warning is spurious.

**Run for real end-to-end for the first time on 2026-08-02** — all 7 present
files (`metadata`, `biblio`, `tags`, `comps_biblio`, `nominal_biblio`,
`simsyn_biblio`, `simsyn_metadata`) uploaded cleanly to the `next` draft with
no stray-upload warnings on any table. Ben still needs to review and publish
that draft version on the Redivis site by hand — this script never does that
part.

## Safeguards (read before generating anything that resembles a description)

**Confirmed gap (2026-07-27, verified by grepping `metadata/`, `tags/`,
`itemtext/`)**: the hash-cache / similarity-flagged / `construct_description
= NA` + `provenance = "pending review"` system Ben originally described does
**not exist anywhere in this codebase today**. The only reference to
`construct_description` in the whole repo is one aside in
`tags/.claude/skills/irw-auto-tag/SKILL.md` calling it a hypothetical field
from a `metadata/03b_describe.R` that doesn't exist.

What *does* exist today, and why it matters:
- `03_tags.R` selects columns `c(1,6:12,3)` from each tags sheet into
  `tags.csv` / `nominal_tags.csv` — this excludes column 4, "Context Text"
  (the **verbatim excerpt** field, confirmed against the live sheet header),
  so raw paper text never reaches the public CSVs today. This rests on a
  hardcoded column index, not a by-name check — if a sheet's columns are ever
  reordered, the protection silently breaks with no error. The script now at
  least asserts column *count* and that row 1 is the instruction row, but
  neither catches a reorder. **If you ever touch `03_tags.R`'s column
  selection, flag this explicitly to Ben before changing it**, and confirm the
  output has no `context text` column.
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
