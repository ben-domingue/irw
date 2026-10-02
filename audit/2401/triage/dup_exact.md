# `dup_exact` triage (#2401, Decisions item 4)

82 tables in 33 families, 3,364,675 exact-duplicate rows. One row per family is in `dup_exact.csv`. The evidence comes from aggregate queries against live Redivis, the `data/` scripts, and, for jiang, zhang, ptcichina and emobank, the public raw files. Nothing in the corpus or the repo was changed.

| verdict | families | tables | exact rows |
|---|---|---|---|
| `rebuild_prefix` | 14 | 24 | 2,963,483 |
| `known_issue` | 8 | 16 | 302,717 |
| `dedupe` | 5 | 25 | 67,247 |
| `already_handled` | 6 | 17 | 31,228 |
| `prefix` | 0 | 0 | 0 |

**No family is a plain `prefix`.** Wherever ids collide, the separator was dropped by the script, or the one kept in IRW is not enough on its own: `crspolish`'s `cov_country` leaves 9,870 excess rows.

**`rebuild_prefix` is used here for "rebuild, keeping a column the script dropped".** Only five of the 14 put that column into `id`:
- `pisa2000` and `pisa2006` (SCHOOLID);
- `crspolish` (country plus parent role);
- `ptcichina` (sample C2 plus a row index);
- `rating_speed` (the rater suffix; this one goes into `rater`, not `id`).

In the rest, the dropped column is an occasion or a stimulus: `geography`, `steinberg`, `zhang`, `schoen` and `kalimah` need a time or trial column; `musifeast`, `mentalrotation`, `cvencek` and `western_reserve` need it in `item`. For all nine, deduping would destroy real responses. Ben may want those relabelled `rebuild_occasion`.

## For a human to eyeball

1. **`jiang_2024_*` (20 tables, 58,695 rows).** The source S1 file has 1,792 rows, but they are only 707 distinct response vectors, stacked at row offsets of exactly 707. Within each copy the items and completion time are identical, while gender and age differ. A dedupe gives 707 people with conflicting demographics. The paper's N=1792 looks inflated, so the choice is between dedupe and withdraw.
2. **PISA 2000/2006 (6 tables, 2.64M rows).** This is the bulk of the class. The rebuild needs the raw OECD files, and `pisa2000.R`'s fixed-width import is flagged by its own author.
3. **`emobank_buechel_2017` (192,950 rows).** A dedupe here would delete real ratings. The source has no annotator id, so the duplicates are annotators who agreed. It stays a known issue unless IRW accepts an anonymous per-sentence rater index.
4. **`petley_2025_flanker_*` (5 tables, 109,586 rows).** These rows are synthetic Bernoulli trials expanded from correct/total counts. The question is whether the expansion belongs in IRW at all, not how to dedupe it.
5. **`crspolish_wiesyk_2024_*`.** Two collisions are stacked: ids restart per country, and an id is a coparenting dyad. In country 1 both parents' sex is NA, so the parent-role column has to come from the source.

## Notes
- `geography` also has an rt sentinel: the exact duplicates' median rt is 2,147,483.647 s, the INT32-max value in milliseconds. That belongs in the `rt`/`cov_sentinel` batches too.
- `robison_2026_retesting_{ifr,paper_folding}` are not held (they have no `table_changes` row), but their siblings' practice-trial fix (#2513) is in the draft. Check them for practice or restart rows before any dedupe.
- For `selm_2019` and `smoking_perseverance`, `dedupe` covers only the fully duplicated record. The remaining colliding ids are `dup_id_item` cases for #1856.
