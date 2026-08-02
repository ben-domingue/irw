# site-update TODO

## biblio.csv: 182 rows still have Derived_License=NA (bug fixed + backfilled 2026-08-02, 2 remaining sub-issues)

`02_biblio.R`'s `getrows()` built new biblio rows via a `select()` that never
included the dictionary's `Derived License` column at all (line ~132-134) --
every row it ever added got `Derived_License` filled with `NA` by
`bind_rows()`, regardless of whether the dictionary had a real license value.
Confirmed 2026-08-02: 1,878 of 2,833 rows (66%) in `biblio.csv` had `NA`
there. Not a licensing-verification gap (per `feedback_license_verification`
-- the license IS checked upstream before a dataset is processed) -- purely
a reporting gap in this one column. **Fixed going forward**: `select()` now
includes `` `Derived License` ``, renamed to `Derived_License`.

**Backfilled 2026-08-02** via a one-off join of `biblio.csv`'s `table`
against the dictionary sheet's `table`/`Derived License` columns (a plain
re-run of `02_biblio.R` would NOT have fixed these -- its match logic only
reprocesses rows that are new-to-biblio or missing `BibTex`, so an
already-populated `Derived_License=NA` row never qualifies). 1,690 of 1,872
NA rows filled. 182 remain, in two different buckets:

1. **6 rows with no dictionary entry at all**: `su_2024_isi`, `su_2024_phq9`,
   `su_2024_pss14`, `racialsocialnormsbrazilianstudents_portella_2022`,
   `wvs_panasiuk_security`, `wvs_panasiuk_science`. Same orphan-biblio shape
   as the `liang_2026`/`ren2019` case resolved earlier this session (biblio
   row exists with no backing dictionary row) -- not yet investigated for
   these 6 specifically.
2. **176 rows where the dictionary row exists but its own `Derived License`
   cell is blank too** (e.g. the `heekerens2025_*`, `parenting_anunciacao_2025_*`
   families) -- a gap in the dictionary sheet itself, not fixable from
   `biblio.csv`'s side. List not yet compiled/handed to Ben.

## Resolved 2026-08-02 (kept here for history -- see git log for the actual diffs)

- **`02_biblio.R`'s `getrows()`: `Derived License` column name differs
  across the 4 dictionary sheets.** The earlier same-day fix for
  `Derived_License` always being `NA` (see the `biblio.csv` item above)
  hardcoded `` `Derived License` `` (with a space), matching only the core
  dictionary sheet. Surfaced as a hard crash (`Column 'Derived License'
  doesn't exist`) partway through a full `run_pipeline.sh` run, on the
  `comps` dictionary specifically. Checked all 4 sheets directly (two
  consecutive fetches each, to rule out the day's recurring flakiness) --
  confirmed real and consistent: `comps`/`nominal`/`simsyn` all use
  `Derived_License` (underscore), only `core` uses `Derived License`
  (space). Fixed with a normalize-before-select step in `getrows()` so it
  works regardless of which spelling a given sheet uses. Verified: a full
  `run_pipeline.sh` run completes end-to-end across all 4 dbs with 0
  changes.
- **`01_metadata.R`'s unconditional per-table variable-listing loop**
  (previously made a plain `run_pipeline.sh` run take 2+ hours) -- fixed to
  reuse `variables` for tables already known, matching the `toadd`-based
  reuse the stats loop already had. Verified: a full re-run with no new
  tables dropped from 45+ min to 19s, with `metadata.csv` diffing as 0
  added/removed/changed (proves the reuse is correct, not just faster).
- **`05_comps.R`'s three bugs** (wrong 7-column schema copy-pasted from
  `01_metadata.R`, undefined `toadd`, final write using stale `meta` instead
  of computed `summaries`) -- rewritten to mirror `07_simsyn.R`'s structure,
  adapted for comps' real `table`/`n_responses`/`n_actors` schema. Verified
  standalone: picked up `costa_gine_2023_wpt_matches` cleanly, 23 rows, no
  errors.
- **`06_nominal.R`** -- verified standalone, no bugs found (matches the
  earlier "probably fine" assessment). Picked up `cos101_2026_openended`
  cleanly, 12 rows, no errors. No code changes.
- **`08_itemtext.R` folded into `run_pipeline.sh`** as a real stage,
  positioned right before `09`. Confirmed architecture split with Ben: this
  skill produces metadata FOR item text that's already been procured; the
  separate `irw-auto-itemtext` skill procures/extracts the item text itself
  (`{table}__items.csv` from source papers) -- no code overlap. Only the
  incremental script is wired in; `hotfixes/08_itemtext_recompute.R` stays a
  manual, out-of-pipeline operation. `upload_meta.py`'s file->table map
  updated to include `itemtext_metadata`. Verified standalone (9s, "No new
  tables to process" -- handled gracefully by the diff step).
- `run_pipeline.sh`'s `DEFAULT_ORDER` is now `(01 02 03 05 06 07 08 09)` --
  full default order restored/extended, nothing excluded anymore.
