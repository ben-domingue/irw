# Audit mode: Batch 1 (pilot)

**Date:** 2026-08-12
**Scope:** 9 known-drift tables (regression set, re-diffed against live curation) + 15 fresh tables (never touched by the 100-table eval)
**Total:** 24 tables

## Legend

- 🟢 **Green** — curated version and fresh extraction are sufficiently close. No action.
- 🟡 **Yellow** — curated version stays as-is, but there's a specific, documentable issue worth noting on the public website. Ready-to-use text included below.
- 🔴 **Red** — requires human review and likely replacement. Filed as a GitHub issue.
- ⚪ **Gray** — could not be independently confirmed (unverifiable source, or source access blocked), but no evidence the curated version is wrong. Not a website caveat, not an issue — just not yet verified.

## Summary

| | n |
|---|---|
| 🟢 Green | 7 |
| 🟡 Yellow | 1 |
| 🔴 Red | 11 |
| ⚪ Gray | 5 |

---

## 🟢 Green (7)

| Table | Note |
|---|---|
| `suicide_reinbergs_2025_gad` | Standard GAD-2 wording, 0 mismatches |
| `mpsycho_learnemo` | MPsychoR package docs, 0 mismatches |
| `mhscdc_fried_2020_conscientiousness` | OSF source PDF, 0.99 item_text sim (punctuation only) |
| `mhscdc_fried_2020_loneliness` | OSF source PDF, 0.99 item_text sim |
| `alsecypiamh_wu_2022_pei` | Standard Gallup wording, 0 mismatches |
| `florida_twins_panas` | LDbase codebook, 0 mismatches |
| `gilbert_meta_87` | Trexler preprint appendix, 0 mismatches, 11/11 verbatim |

## 🟡 Yellow (1)

### `florida_twins_friends`

19/21 items (`friends1`-`friends19`) confirmed exactly against the Florida Twin Project's W1_Child codebook. `friends20`/`friends21` are in the live data and current curation but not documented in that codebook.

**Website text (for `itemtext_issues.qmd`):**
```
::: {.g-col-4 .dataset-item}
::: {.callout-warning collapse='true'}
## florida_twins_friends
Items friends20 and friends21 ("My friends attend the same school as me." /
"My friends are older than me.") are not documented in the Florida Twin
Project's Wave 1 Child Survey Measures codebook. Item text for these two
items could not be independently verified against a public source.
:::
:::
```

## 🔴 Red (11) — all filed as GitHub issues

| Table | Issue | Problem |
|---|---|---|
| `political_psychology` | [#1594](https://github.com/ben-domingue/irw/issues/1594) | 7/37 items have wrong resp-scale mappings |
| `dumas_organisciak_2022` | [#1598](https://github.com/ben-domingue/irw/issues/1598) | Missing `instructions` field entirely |
| `ccapsvtskhpacr_mercedes_2023_tsk` | [#1599](https://github.com/ben-domingue/irw/issues/1599) | 2 of 4 response-scale labels missing |
| `sv-maia2_randelovic_2021_erq` | [#1600](https://github.com/ben-domingue/irw/issues/1600) | Curated resp scale (1-7) stale vs. live (1-5) |
| `sv-maia2_randelovic_2021_hexaco60` | [#1601](https://github.com/ben-domingue/irw/issues/1601) | 24/60 items have NA resp despite live data existing |
| `chile_2023_social-welfare-survey_h` | [#1602](https://github.com/ben-domingue/irw/issues/1602) | `h3_e` missing resp category 3 |
| `shu_2025_translation_eib` | [#1603](https://github.com/ben-domingue/irw/issues/1603) | `eib_pishp232` missing resp category 1 |
| `eammi_grahe_2018_socmedia` | [#1604](https://github.com/ben-domingue/irw/issues/1604) | `SocMedia_bias_dummy` resp is NA despite live data existing |
| `threat_isler_2024_exp4_cog_crt` | [#1605](https://github.com/ben-domingue/irw/issues/1605) | Only 1 of 3 live items documented |
| `gilbert_meta_80` | [#1606](https://github.com/ben-domingue/irw/issues/1606) | 8 curated items don't exist in live data (orphaned, not a text-quality issue) |
| `gilbert_meta_78` | [#1607](https://github.com/ben-domingue/irw/issues/1607) | 3 curated items don't exist in live data (orphaned, not a text-quality issue) |

## ⚪ Gray (5) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `mpsycho_rogers_ocd` | Item identity confirmed via package docs; specific self-report wording variant unconfirmable from public sources |
| `lshs-e_quidaja_2022` | Structure/translation plausible; no primary source located for this paper's exact translation |
| `sun_2025_morality_study2_self-moral-character` | Translation spot-checked accurate; paper paywalled, no codebook on OSF |
| `himmelstein-number_series-2025` | Item identity/answers confirmed via GitHub repo; actual number-sequence stimuli not in any public file checked |
| `gilbert_meta_40` | Source (Harvard Dataverse) blocked by AWS WAF on both curl and WebFetch; also surfaced a pre-existing curator note questioning whether items belong in `gilbert_meta_39` instead |

## Net result

0/24 cases where the skill's extraction was wrong and curation was right. 11 real issues filed, 1 website caveat drafted, 5 flagged for retry/revisit later, 7 confirmed clean.
