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

## 01_metadata.R re-pulls variable lists for every table, every run (found 2026-08-02)

Observed live: a plain `run_pipeline.sh` default run sat in `01_metadata.R`
for 45+ minutes with an active Redivis socket and low steady CPU -- not
hung, just slow. Traced to two separate loops in the file that behave very
differently:

- Lines 19-130 (`f()`, the per-table stats: `n_responses`, `n_categories`,
  `n_participants`, `n_items`, density, etc.) *does* reuse correctly -- it's
  only called for `new.tables[!toadd]`, i.e. tables not already present in
  the `metadata.csv` pulled from the live `irw_meta:metadata` Redivis table.
- Lines 142-157 (`table_vars_df`, the per-table variable-name listing used
  for the `longitudinal` flag) does **not** reuse anything -- it loops over
  every table in `unique(summaries$dataset)` (old + new alike, ~2000+ table
  and growing) and calls `table$list_variables()` on each one, every single
  run, regardless of whether that table's row already exists in `meta`. It
  also redundantly re-calls `ds$list_tables()` per dataset even though the
  identical result was already fetched into `tables` at line 22.

**Recommended fix:** thread the same `toadd`/`old.tables` reuse logic through
the variable-listing loop -- only fetch `list_variables()` for tables in
`new.tables[!toadd]`, and carry forward the previously-fetched `variables`
string for every other table (it doesn't change once a table is live, so
there's no correctness reason to redo it). Don't touch this without
confirming with Ben first, same as 05/06 below -- worth checking whether
`variables` is ever expected to change for an existing table (e.g. a
hotfix editing an already-shipped table) before assuming it's safe to
skip unconditionally.

## Discuss folding 08_itemtext.R into this skill (Ben, 2026-07-28)

Currently explicitly out of scope (see SKILL.md and `references/pipeline.md`)
-- it belongs to the separate `itemtext/` pipeline
(`itemtext/.claude/skills/irw-auto-itemtext/`), and `run_pipeline.sh` doesn't
have it wired up as a stage at all. Ben: in the long run he wants `08` (item-
text readability metadata -- word/char counts, Flesch-Kincaid, incremental
vs. the `hotfixes/08_itemtext_recompute.R` full-recompute variant) included
in *this* skill instead. Needs a real conversation before implementing --
at minimum: how it should relate to the separate `irw-auto-itemtext` skill
(which does the actual item-text *extraction* that `08` then summarizes --
folding `08` in here doesn't obviously mean moving that skill too), whether
it fits `run_pipeline.sh`'s snapshot/diff pattern the same way (it's
incremental-only by design, unlike 01/05/06/07/09), and where in the run
order it'd go. Don't just wire it into `DEFAULT_ORDER` without that
discussion.

## 05_comps.R is broken -- needs a real fix, not a patch (found 2026-07-28)

Confirmed three separate bugs while diagnosing a live-run crash. Fixing just
the reported crash would leave a script that "succeeds" but is still wrong
-- see #3.

1. **Line 10-12 crash (the one that actually surfaced):** `meta <- meta[,
   c("table","n_responses","n_categories","n_participants","n_items",
   "responses_per_participant","responses_per_item","density")]` -- these
   columns don't exist on the real `comps_metadata` Redivis table. Its
   actual schema is `table`/`n_responses`/`n_actors`, matching what this
   file's own `getvars()` computes (comps is pairwise-comparison data, not
   item-response data -- the 7-column list was copy-pasted from
   `01_metadata.R` and never adapted).
2. **`toadd` is referenced (line 61: `nms<-new.tables[!toadd]`) but never
   defined anywhere in the file.** `01_metadata.R` and `07_simsyn.R` both
   compute it (`toadd <- new.tables %in% old.tables`) before using it;
   `05_comps.R` doesn't. Even with #1 fixed, this crashes next. The
   script's own header comment ("this kinda works... a lot of the
   functionality outside of the f() function is not tested") suggests it
   was last run interactively, reusing a `toadd` left over in the console
   from having just run `01_metadata.R` in the same session -- it has
   likely never completed a standalone `Rscript 05_comps.R` run.
3. **Line 87 writes `meta`, not `summaries`.** `summaries` (old + newly
   computed rows for new `irw_competitions` tables) is built correctly a
   few lines above, then never used -- `write.csv(meta, 'comps_metadata.csv',
   ...)` writes only the old data back out unchanged. Fixing #1 and #2
   alone gives you a script that runs without error but silently never
   picks up new competition tables.

**Recommended fix:** don't patch these three spots independently -- rewrite
`05_comps.R`'s control flow to mirror `07_simsyn.R` (which has the correct
`toadd`/`torem`/`summaries` structure already) adapted for comps' 2-column
`n_responses`/`n_actors` schema, rather than reusing 01's 7-column shape.

## 06_nominal.R -- probably fine, just unverified (2026-07-28)

Traced the same way as 05 above and found no equivalent bugs: `toadd` is
defined correctly, the final `write.csv` uses `summaries` (not stale data),
and its column handling is actually *more* robust than 01/05/07 -- it reads
`names(meta)` from whatever the live Redivis table already has instead of
hardcoding a column list, so it isn't vulnerable to the same schema-mismatch
that broke 05. The only issue found in this file was the retry-loop success
check expecting `length(testvec)==7` when its own `getvars()` actually
returns 5 elements -- already fixed (2026-07-28, see `06_nominal.R`).

It was never actually run this session (the pipeline halted at 05 first).
**Don't assume it needs the same rewrite as 05** -- next time it's in
scope, just try running it standalone (`Rscript 06_nominal.R` from
`metadata/`) before touching anything.

## Until 05 is fixed

`scripts/run_pipeline.sh`'s default stage order excludes both 05 and 06 (see
that script's `DEFAULT_ORDER`) so a normal run doesn't keep dying on 05
before ever reaching 07/09. Both are still runnable explicitly:
`scripts/run_pipeline.sh 05` / `scripts/run_pipeline.sh 06`.
