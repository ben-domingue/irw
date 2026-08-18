# Notes for the next scheduled pipeline run

Cron: `0 6 * * 1 metadata/weekly_pipeline_cron.sh` -- **next run Monday
2026-08-24, 06:00**. Delete or trim entries here once they've been checked
off; this file is for the human reviewing the run, cron does not read it.

## 2026-08-24: 01_metadata.R no longer exports tables to count rows

`getvars()` used to fall back to `tab$to_tibble()` -- a full table export --
whenever a variable's server-side `count` statistic came back NULL, just to
count non-missing `resp` rows. Redivis caps *data export* at 200 GB per
rolling 30 days per user and the core warehouse is 181.8 GB across its four
shards, so a few large tables hitting that fallback is enough to spend the
month's allowance. On 2026-08-18 the quota was exhausted account-wide (204 GB
used), which blocks `irw_fetch()` for every user and every table until the
window rolls over.

That fallback is now `count_resp_via_query()`, a single-row `SELECT COUNT(*)`
against the table's `qualified_reference`. Queries are not subject to the
export cap. Nothing else changed -- `metadata.csv` keeps the same columns.

What to check in the 2026-08-24 log:

- Grep for `counting via query`. Each line is a table that took the fallback;
  under the old code each one would have been a full export.
- No line should mention `to_tibble` for a warehouse table. The one remaining
  `to_tibble()` in the script (line 10) reads the small `irw_meta:metadata`
  table and is fine.
- If a count query fails, the table is retried 4x and otherwise left out of
  `metadata.csv` entirely (existing behaviour) -- it never falls back to an
  export. So watch for `giving up on <table>` lines as well.

## Two things the corpus scan turned up (NOT fixed -- your call)

I scanned the `resp` statistics for all 3,032 tables in `metadata.csv`.

**1. 47 tables have a stale `n_responses`.** The server-side `count` no longer
matches what `metadata.csv` says -- e.g. `western_reserve_project` is 1,445,422
on Redivis vs 1,066,535 published, `mhscdc_fried_2020_dass` is exactly double.
The script only fetches stats for *newly added* tables, so a table that gets
re-uploaded keeps its original row forever. 37 of the 47 are integer `resp`,
8 string, 2 float, so this is re-uploads, not a type issue. Fixing it means
periodically refetching existing rows -- cheap now that counting is a query.

**2. 8 tables in `metadata.csv` no longer resolve at all:**
`enem_2023_1mil_{ch,cn,lc,mt}` and `enem_2024_1mil_{ch,cn,lc,mt}`, all listed
under `item_response_warehouse_2`. They 404. Either they moved shard or were
removed; either way those rows are dead.

**3. 310 of 3,024 tables have a string-typed `resp`,** and on those the
literal `"NA"` token is common -- `dscore_denver_weber_2019` is 118,589 `"NA"`
out of 142,899 rows, `FACIT_YOUNT_2021_limitations` 10,276 of 42,200. The
published `n_responses` counts those rows as responses. Whether it should is
a real question, but changing it is a change to what `n_responses` *means*
across the whole corpus, so I left it alone -- see the comment above
`count_resp_via_query()` in 01_metadata.R.

## 05_comps.R and 07_simsyn.R got the same treatment

- `07_simsyn.R` had the identical NULL-count -> `to_tibble()` fallback; it now
  uses the same `count_resp_via_query()`.
- `05_comps.R` was worse: it called `tab$to_tibble()` *unconditionally*, on
  every table every run, purely to compute `n_actors` from
  `unique(c(df$agent_a, df$agent_b))`. That is now a server-side
  `COUNT(DISTINCT agent)` over a `UNION ALL` of the two columns.

Both sources are small next to the core warehouse, but they draw on the same
200 GB export pool, and 05 was spending it every single week.

After Monday's run, no script under `metadata/` should export a warehouse
table. The surviving `to_tibble()` calls are: reading the small
`irw_meta` metadata tables (01 line 10, 05 line 9, 06 line 9, 07 line 10),
`02_biblio.R:124` reading `biblio`, and the one-row query results.
