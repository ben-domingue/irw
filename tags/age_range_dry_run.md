# Rule A dry run — 2026-09-01

Derived from each table's own `cov_age`, Redivis-side. Nothing has been published.

## What happens to the published column

| outcome | tables |
|---|---|
| confirmed | 1,790 |
| new row | 5 |
| Non-human preserved | 4 |
| **total derived** | **1,799** |

## Every change, by direction

| from | to | tables |
|---|---|---|

## Tables the rule declined to touch

| verdict | tables | why |
|---|---|---|
| unusable | 166 | only N respondents with an age |
| unusable | 98 | looks like banded codes: N distinct values, max N.N |
| unusable | 65 | ages outside [N, N]: N.N-N.N |
| unusable | 16 | ages outside [N, N]: -N.N-N.N |
| quarantine | 40 | ages equally consistent with months; held for a human |

## Where the 2% floor decided the tag

219 table(s) have respondents on both sides of 18 but too few on the smaller side to count as `Mixed`.

| table | ages | under 18 | of | share | tag |
|---|---|---|---|---|---|
| `kim_2023_gad7` | 13–64 | 4 | 202 | 1.98% | `Adult (18+)` |
| `kim_2023_phq9` | 13–64 | 4 | 202 | 1.98% | `Adult (18+)` |
| `kim_2023_pss10` | 13–64 | 4 | 202 | 1.98% | `Adult (18+)` |
| `lsbq_maleki_2025_non_persian_proficiency` | 15–59 | 6 | 307 | 1.95% | `Adult (18+)` |
| `lsbq_maleki_2025_persian_switching` | 15–59 | 6 | 314 | 1.91% | `Adult (18+)` |
| `lsbq_maleki_2025_persian_comprehension` | 15–59 | 6 | 315 | 1.90% | `Adult (18+)` |
| `ipip_openpsychometrics_ad` | 14–72 | 19 | 1000 | 1.90% | `Adult (18+)` |
| `ipip_openpsychometrics_do` | 14–72 | 19 | 1001 | 1.90% | `Adult (18+)` |
| `ipip_openpsychometrics_sc` | 14–72 | 19 | 1001 | 1.90% | `Adult (18+)` |
| `ipip_openpsychometrics_as` | 14–72 | 19 | 1004 | 1.89% | `Adult (18+)` |
| `teq_novak_2021_bfin` | 15–62 | 3 | 165 | 1.82% | `Adult (18+)` |
| `lsbq_maleki_2025_dominant_language_home_community` | 15–59 | 5 | 279 | 1.79% | `Adult (18+)` |
| `benitezsillero_2021_bullying` | 12–20 | 1417 | 1441 | 1.67% | `Child (<18y)` |
| `teq_novak_2021_selfesteem` | 15–85 | 3 | 195 | 1.54% | `Adult (18+)` |
| `teq_novak_2021_socdes` | 15–85 | 3 | 197 | 1.52% | `Adult (18+)` |

## The #1760 tables

The six named in the issue, plus the `sample` example.

| table | was | now |
|---|---|---|
| `colombia_2023_politics_voting` | `Adult (18+)` | `Adult (18+)` |
| `mexico_2023_quality_wellbeingservice` | `Adult (18+)` | `Adult (18+)` |
| `spain_2025_democracy_parties` | `Adult (18+)` | `Adult (18+)` |
| `spain_2024_politics_beliefs` | `Adult (18+)` | `Adult (18+)` |
| `margaretto_2025_translation_study_2_lextale` | `Adult (18+)` | `Adult (18+)` |
| `silvia_2024_funny` | `Adult (18+)` | `Adult (18+)` |
| `mexico_2023_quality_low` | `Adult (18+)` | `Adult (18+)` |

