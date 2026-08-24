# Notes for the next scheduled pipeline run

Cron: `0 6 * * 1 metadata/weekly_pipeline_cron.sh` -- **next run Monday
2026-08-31, 06:00**. Delete or trim entries here once they've been checked
off; this file is for the human reviewing the run, cron does not read it.

## What happened on 2026-08-24 (all resolved -- background only)

The run **failed at stage 02**, so 03/05/06/07/09 never executed and had to be
re-run by hand. Cause: column A of the core dictionary sheet had been renamed
from `table` to `x`, so `02_biblio.R:129` matched on a NULL column. Ben renamed
it back. `audit_tables.R` hit the same missing column but exited 0 and reported
"595 incomplete" -- with the sheet parsing again it was 179, and 66 after the
dictionary gaps were filled. **If the audit's incomplete count jumps by
hundreds, suspect the dictionary sheet before believing the number.**

Also fixed that day, no action needed now:

- 124 duplicate rows in the core dictionary sheet (removed via Sheets'
  "Remove duplicates"; 3,930 -> 3,807).
- 10 stale biblio-only rows dropped (`adhd_silk_2019_*`, `su_2024_*`,
  `alcoholhealthwarninglabel_brennan_2022_positive_arousal`,
  `racialsocialnormsbrazilianstudents_portella_2022`).
- `altahla_2024_swls` existed in two shards; deleted from shard 4.

## 1. NEW: 01_metadata.R now refreshes existing rows (`refresh.per.run`)

This is the fix for the "47 tables have a stale n_responses" item that used to
be in this file. Until now only *new* tables were ever fetched, so a re-uploaded
table kept its original row forever. Each run now also re-fetches
`refresh.per.run` (default **200**) tables that were already in metadata.csv,
oldest-refreshed first, tracked in `metadata_refresh_log.csv`.

What to check in the 2026-08-31 log:

- A `refresh pass: N of M existing table(s)` line, then ~200 `refresh k/200`
  lines. This adds roughly 45-60 min to stage 01. Set `refresh.per.run<-0` to
  disable if a run needs to be quick.
- `metadata_refresh_changes.csv` -- every stat that moved, with old and new
  values. On the smoke test the enem_2023/2024 shards were all wrong
  (`enem_2023_1mil_cn` n_items 93 -> 45, n_participants 1000000 -> 999722), so
  expect real changes for a while as the backlog gets swept.
- `refresh: N table(s) failed transiently and were left unchanged` -- fine,
  they retry next run (they are only logged as refreshed on success).

## 2. NEW: dead tables are detected and dropped

Some tables are returned by `list_tables()` but 404 on access, so the "remove
tables" step at the top of 01_metadata.R cannot see them -- that was the
`enem_2023_1mil_*` / `enem_2024_1mil_*` item in the old version of this file.
The refresh pass now classifies a fetch failure: a definite not-found drops the
row and records it in `metadata_dead_tables.csv`; anything else (timeout, 403,
transient) leaves the row alone.

**Note:** as of 2026-08-24 those 8 enem tables resolve again and are NOT dead --
they were merely stale, and the refresh pass corrected them. So this path is
unit-tested but has not yet fired on live data. If `metadata_dead_tables.csv`
appears, check the table on the Redivis site before trusting it.

## 3. NEW: upload_meta.py verifies row counts

`comps_metadata` had been silently **appending** on every weekly upload --
23 unique rows had become 90, and this run's upload took it to 180.
`replace_on_conflict` only replaces an upload whose *name* matches, and that
table carried rows inherited from the released version that `list_uploads()`
does not expose, so each upload landed beside the old data instead of over it.

`upload_meta.py` now compares each table's `numRows` to the local CSV after
uploading and **exits non-zero** on a mismatch. If it reports rows were
appended: delete that table's data (or the table) on the `next` draft in the
Redivis UI, then re-run the script for just that file. Do not publish a draft
with a failed verification.

The table was rebuilt clean on 2026-08-24 (23 rows), so a normal run should
now verify cleanly. If `comps_metadata` fails verification again, the
inherited-rows problem has come back and is worth a proper look.

## 4. NEW: metadata.csv no longer written in scientific notation

`options(scipen=999)` at the top of 01_metadata.R. With R's default, write.csv
emitted whichever form was shorter, so 98 cells across 43 tables (all the large
`enem_*` shards) were published as `4.5e+07` / `1e+06`. Values round-trip
exactly, so nothing was lost -- but they broke integer parsing and read as
wrong. Should be plain integers from now on; worth a glance at any enem row.

## Still open -- your call, nothing automated

**String-typed `resp` and the literal "NA" token.** 310 of ~3,024 core tables
have a string `resp`, and on those the four-character token "NA" is not null,
so it is counted as a response. `n_responses` therefore includes rows that
almost certainly are not responses (`dscore_denver_weber_2019`: 118,589 of
142,899). Changing this redefines `n_responses` corpus-wide, so it has not been
touched.

To get numbers for the decision:

    cd metadata
    Rscript hotfixes/report_string_resp_na.R            # full sweep, resumable
    Rscript hotfixes/report_string_resp_na.R --limit 25 # quick sample
    Rscript hotfixes/report_string_resp_na.R --summary  # re-print summary

Writes `hotfixes/string_resp_na_report.csv` (per table: rows, responses counted
now, "NA" count, blank count, what n_responses would become, and the percentage).
A 4-table sample on 2026-08-24 found all 4 affected, 3,360 of 45,144 responses
being the "NA" token. The full sweep takes roughly half an hour and is
resumable, so it can be interrupted freely.

**Four biblio rows have empty `author = {}` and `year = {}`**: `mpsycho_wilpat`,
`immer12_immer`, `ptam1_immer`, `immer10_immer`. All are CRAN package citations
(MPsychoR, immer) with `DOI = "NA"`. Fixing properly means supplying real
values (Mair for MPsychoR; Robitzsch & Grund for immer) rather than deleting
the empty fields, which would leave an authorless citation.

**BibTeX churn on rows with no DOI.** When a dictionary row has no DOI,
02_biblio.R generates the BibTeX via Claude, and it is not deterministic --
across two runs on 2026-08-24 the same paper produced `Raber, F. G.` vs
`Raber, G. F.` vs `Raber, F.`, and keys `CIS3406` / `cis3406` / `CIS_3406`.
This only happens while a row is not yet in the *published* biblio table, since
02 re-adds it as new each run. It settles once uploaded, but it does mean a
stage 02 diff showing "changed: N" on no-DOI rows is usually noise, not signal.

**7 `spain_2023_identity_*` tables still have no dictionary rows** --
`{authenticity, centralism, europe, patriotism, pride, state, territorial}`.
Ben has someone looking into it (2026-08-24); they will keep showing up in the
audit's incomplete list until then.

## Reminder: the site is a separate repo

Stage 09 writes `hero_stats.json` into the `irw_site` checkout, which is
`github.com/datapages/irw`. Rendering the site does nothing unless that file is
**committed and pushed to main** first -- on 2026-08-24 the workflow ran
successfully against a version of the file from 2026-08-10 and republished the
old numbers.
