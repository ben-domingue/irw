# openESM 0013_hoebeke: plan

Hoebeke (2022). community sample. 4x/day time-contingent equidistant intervals.
Data: 0013_hoebeke_ts.tsv, 2,102 rows, 40 people. Licence: CC BY 4.0 (original: CC BY 4.0).

## Proposed tables

**hoebeke_2022_rumination** (5 items, scale 0..100)
- `perseverance`: How much time did you spend thinking of one or more emotional experiences? (observed 0.0..100.0, n=2,062)
- `negativity`: To what extent were your thoughts negative? (observed 0.0..100.0, n=2,062)
- `self_criticism`: "To what extent were your thoughts self -critical?" (observed 0.0..100.0, n=2,062)
- `brooding`: How much did you think about the causes and consequences of emotional experiences? (observed 0.0..100.0, n=2,062)
- `replaying`: To what extent have you mentally replayed emotional experiences that you’ve had? (observed 0.0..100.0, n=2,062)

## Candidates (decide)

- `activity`: unclear
- `att_control`: unclear

## Not shipped

- `modified`: PosixCt: Time of modification
- `ended`: PosixCt: Time of ending
- `expired`: PosixCt: Time of expiring

## Flags (each needs a `resolution` in the spec)

1. `wave` = each person's prompts numbered in created order (openESM time columns, best first: ['created', 'ended', 'modified', 'expired']). `date` = created as Unix seconds. Data run 2021-02-26 09:01 .. 2021-06-08 21:23 as written. Set date.window from the paper's collection period.
2. Time zone of created. Written with a `Z`, but in 0072_neubauer and 0056/0057_ryvkina the `Z` stamps are local time. Hour-of-day counts as written: 9h:342, 10h:157, 11h:1, 13h:456, 14h:77, 15h:1, 17h:433, 18h:87, 19h:9, 21h:447, 22h:92. No Unix time column to check against: compare with the paper. Set date.tz to 'UTC' if the stamps are true UTC, or to the study's IANA zone (e.g. 'Europe/Berlin') if they are local time, and say how you know in date.tz_evidence.
3. Tables are a first guess from file order, response scale, source, prompts asked at, and column-name prefixes. Read the codebook and split or merge so each table is one instrument or subscale (datastandard.md, 'One file per scale'); rename each `<author>_<year>_<construct>`, and set `script` to the record's name.
4. `candidates` holds columns that may or may not be items (binary checkboxes, counts, rating scales whose coding gives no anchors -- activity, att_control). Move any that are responses into a table; the rest go to `not_shipped` with a reason. activity, att_control
5. openESM says cross-sectional (baseline) data exist. Covariates such as age and gender are not handled by this tool: add them by hand to the generated script if wanted (neubauer_2023_stecco does), or note why not.
6. Read openESM's additional_comments: 'some variable codings unclear'
7. Licence: openESM 'CC-BY 4.0'; original deposit 'CC BY 4.0' (OSF API, node dngyk). IRW carries openESM's label when it is stricter (ruled 2026-10-04); if the two differ, the difference goes in the notes and in the report to openESM.
8. `reference` is drafted from openESM's BibTeX. Check it against the paper's DOI: the year (online vs print), page range and author list are where it goes wrong.
