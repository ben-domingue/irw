# Unexplained repeated id-item rows (#3222, review R-21)

A published `density` above 1 is **proof** that an id-item pair repeats, by
pigeonhole: `density = n_responses / (n_participants * n_items)`, so above 1
there are more responses than person-item cells. That is ordinary for repeated
measures and the published row usually says so, with an occasion column. This
directory is the 2026-10-25 pass over the ones that do not.

## What was measured

`live_counts.py` asks each table for its live `COUNT(*)`, `COUNT(DISTINCT id)`,
`COUNT(DISTINCT item)` and duplicate id-item pair count, one query per table,
batched with `UNION ALL`, nothing exported:

    python3 audit/3222/live_counts.py --unexplained --out /tmp/out.csv

`audit_2026-10-25.csv` is that result joined to the published row, with the live
column list from `list_variables()`.

## What it found, out of 6,720 core tables

768 above 1, of which 700 named an occasion column and 122 a `date`. **68 said
nothing**, and they split cleanly:

| | tables | |
|---|---|---|
| stale `n_participants` | 27 | the row was right about `n_responses` and wrong about who answered |
| stale `n_items` | 2 | `vermeiren_2022_nd` 81→80, `west_2021_..._bpaq` 10→9 |
| stale `variables` | 20 | including 5 tables that **do** have an occasion column live |
| genuine duplicates | 38 | nothing in the live table explains the repeat |

`n_responses` was wrong for **none** of the 68. That is why the `counts` check
missed every one: it bounds each count above by `numRows`, and a stale
participant count is too *small*. Tables gain respondents, so this staleness
only ever points one way.

The 32 stale rows were refreshed in the same commit with `refresh_rows.R`. The
worst was `sris_silvia2022`: 221 participants published against 1,192 live, a
factor of 5.4. `KTEEM_Schoen_2019-2022` turned out to be two-wave —
`longitudinal` went `False` → `True`, so `irw_filter(longitudinal = TRUE)` had
been missing it. Five tables' column lists gained the occasion column they
always had (`rr98_accuracy` → `block`, `trialnum`; `motion` → `trialnum`;
`concretewords` → `rater`; `emobank_buechel_2017` → `trial_annotation`), and
nine more had a `group`/`study` column that was renamed to `cov_group` /
`cov_study` in the data without the catalog noticing.

## What is left, and is a data defect rather than a metadata one

40 tables, held as the `unexplained-repeats` baseline. Two families:

- **One id covering two respondents** (20 tables): the duplicate rows are
  exactly *k* whole extra response sets, and `k` is small — one for every
  `liu_2017_*`, `shan_2020_*` and `PROMISPME_Forrest_2021_*_Proxy` table, two
  for `gumus_2025_dietarian_identity` and `selm_2019_climate_knowledge`, eight
  for `johnhenderson_2020_health_mindset`. `liu_2017_*` and `shan_2020_*` prove
  the reading from their own covariates: the shared id carries two different
  ages and two different genders, so it is two people.
  `darkfactorfrench_pischel_2026_d70` is the outlier at 9,447 extra sets over
  163,114 ids (5.5% of its rows), which at that scale may be retests rather than
  collisions — it has `cov_version` and `cov_study` and wants its own look.
- **A repeat the design keys on something the table does not carry** (18
  tables): `matzke-*` (stop-signal, 99% of rows duplicated, up to 268 responses
  per person-item), `petley_2025_flanker_*` (99%), `crspolish_wiesyk_2024_*`
  (46%, and the same 665 extra sets in all four scales, so it is one roster
  problem not four), `ptcichina_zhan_2024` (49%),
  `selfcompassionscale_shortform_fuochi_2025` (12%),
  `face_memory_amado_2024` (15%), `opentsstvr_linnig_2025_*` (33%),
  `johnhenderson_2020_disinfection_behavior` (a non-integer 7.75 extra sets, so
  not a clean collision).
- Plus `hrm_rater_sim` and `nbashots_sim`, where the repeats are by
  construction; a simulated rater table should still name `rater`.

Both families mislead the same way: `irw_long2resp()` has nothing to key on, so
it aggregates, and the default for a numeric response is the mean. Two
respondents under one id are averaged into a person who does not exist.
