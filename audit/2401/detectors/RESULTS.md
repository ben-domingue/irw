# Class detectors over the live corpus, 2026-09-29

- **Script:** `irw_validate/live_detectors.py`.
- **Raw measurements:** `~/irw-stage/2401-audit/corpus.jsonl.gz` (not in git, 9.6 MB), 4,605 tables, all measured, aggregate queries only.
- **Flags:** `corpus_flags.csv`. To re-flag after a threshold change, run `python3 -m irw_validate.live_detectors --flag corpus.jsonl -o corpus_flags.csv` (seconds, no network).

**Calibration on the random-30 draw:**
- caught 7 of the 8 tables with real value errors;
- the eighth, SV-MAIA2, is the literal-"NA" class, already swept on 09-07;
- 0 false alarms on the 16 clean tables.

The two agent findings it can't see: inverted option text (amatus), and one undefined categorical code (avilesgonzalez).

## Per class

The "families" column is a crude grouping by the table-name stem before the year. Precision is judged from about 8 random flags per class.

| class | tables | families | precision (eyeballed) | proposed ruling | mechanical? |
|---|---|---|---|---|---|
| `cov_all_null`: a `cov_*` column NULL on every row | 63 | 15 | ~100% | drop the column | yes |
| `cov_sentinel`: 98/99/−99 etc. set apart from a covariate's range | 56 | 12 | high | set to NA | yes |
| `cov_range`: age outside 0–120 (#1779 bound), birth year outside 1900–2026 | 50 | 9 | high; mostly one Colombia family (age 114) plus #1779 leftovers | set to NA | yes |
| `rt_constant`: `rt` identical across a person's rows | 20 | 5 | ~100% (9 of the 20 already have some `table_changes` row; check whether that fixed it) | rename to `cov_completion_time_s` | yes |
| `rt_units`: median rt > 300 | 4 | 4 | likely ms | divide by 1000 after a look | nearly |
| `resp_sentinel`: a missing code in `resp` | 1 | 1 | real (`piterova`, 98 on ScLit1–5) | set to NA | yes |
| `dup_exact`: rows identical in every column | 82 | 40 | real, but **two causes**: true duplication, or an **id collision** across countries or samples (e.g. `pisa2006_science`, 856k rows) | per family: dedupe, or prefix the id | no; the cause decides |
| `dup_id_item`: repeats that no occasion column explains, with differing resp | 142 | 62 | mixed: many are repeated-stimulus task designs (Duolingo, enkavi) | already the #1856 question; don't reopen here | no |
| `resp_binary_plus`: a rare extra code on yes/no items | 55 | 34 | ~40%: real for guatemala/chile "don't know"; false for PISA partial credit, BDI, RPQ | a human looks at each family | no |
| `resp_mixed_scale`: a few items on a far wider scale | 16 | 11 | ~50% | a human looks | no |
| `id_placeholder`: an id like 0/99/999 holding extra rows | 36 | 26 | **low**: mostly just person #99 | drop the class, keep `ml_harper_2015` only | — |

**369 tables in 156 families carry any flag, about 8% of the corpus.** That is far fewer than the random draw's 17% implied, for two reasons. The random draw's worst errors included classes these checks don't look for. And the detectors are tuned for precision, not recall.

## What Ben would rule on

1. **Mechanical classes, one yes each** (about 190 tables, about 45 families): `cov_all_null` → drop, `cov_sentinel` and `cov_range` → NA, `rt_constant` → rename, `resp_sentinel` → NA, `rt_units` → ÷1000. These are fixed family by family and logged in `table_changes.csv`.
2. **`dup_exact`** (40 families): one rule. For example: "if the same id appears in more than one country or sample column, prefix the id; otherwise dedupe". Families that fit neither case get a known-issue flag.
3. **The judgement classes** (`resp_binary_plus`, `resp_mixed_scale`; about 45 families): do they go to agents for triage, with only confirmed ones coming back as a batch? Or do they get a known-issue flag and wait?
4. **`dup_id_item`:** leave it with #1856.

## v2 tuning (2026-09-29, after the triage in `../triage/judgement.md`)

`corpus_flags.csv` stays as the v1 record that the decisions were made on. `corpus_flags_v2.csv` is the re-flag, done with no new queries.

- **`resp_binary_plus`:** now fires only on a `{1,2}` pair plus a rare 3, and only in tables with a pure `{1,2}` sibling and no short-Likert items. It goes from 55 tables to 11. Precision is about 73%.
- **`resp_mixed_scale`:** 0–100 sliders and items `resp_sentinel` already caught are skipped. It goes from 16 tables to 8.
- **`id_placeholder`:** downgraded to `info`.
- **Follow-up, not built:** an **option-text rule** over item text. It would flag a numeric `resp` whose `option_text` reads "no sabe / no aplica / no procede / don't know / not applicable / prefer not…". Triage showed it finds every real case, including the ones these thresholds can't see (chile h3_d/e, EEN covid_jobloss, spain 0="No procede"). The other higher-yield practice: once one table is confirmed, sweep every table its script writes.
