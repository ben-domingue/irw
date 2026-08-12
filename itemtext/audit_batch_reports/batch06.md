# Audit mode: Batch 6

**Date:** 2026-08-17
**Scope:** 25 fresh tables, random draw from the 206-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 21 |
| 🟡 Yellow | 0 |
| 🔴 Red | 2 |
| ⚪ Gray | 2 |

---

## 🟢 Green (21)

| Table | Note |
|---|---|
| `sun_2025_morality_study3_benevolence` | BFAS/BFI-2 Agreeableness-benevolence items, verbatim |
| `gilbert_meta_44` | SWEMWBS, verbatim |
| `florida_twins_behavior_ecs` | Confirmed verbatim against FTP-BE 2010 codebook (.doc, converted via LibreOffice) — parent-report ECS |
| `pezzuti_2025_coolpeople_main_trendy_usa` | Plausible custom fashion-perception items |
| `veterans_affairs_ssvf_survey_2018-20` | Regression check — original pilot's Fix 1 example, still complete |
| `movac_pakpour2022` | MoVac-COVID19S, content match to the validated instrument's 5C model |
| `pezzuti_2025_coolpeople_main_masculinity_chile` | Standard cross-cultural masculinity/gender-role content |
| `sun_2025_morality_study2_pemotion` | Structurally consistent positive-emotion frequency items |
| `gilbert_meta_64` | Specific, detailed Arabic content consistent with the cited RCT |
| `sun_2025_morality_study1_loyalty` | Matches established moral-character-rating template |
| `namprb_siwiak_2024_kop20` | Coherent superstition-belief content matching the paper's stated focus |
| `ffm_ext` | IPIP-50 Extraversion facet, verbatim |
| `sun_2025_morality_study1_honesty` | Matches established moral-character-rating template |
| `alsecypiamh_wu_2022_empathy` | IRI Empathic Concern subscale, verbatim |
| `florida_twins_cads` | 57/57 items confirmed verbatim against W1_Child codebook |
| `pezzuti_2025_coolpeople_main_collectivism_mexico_chile` | Yoo, Donthu & Lenartowicz (2011) CVSCALE Collectivism, verbatim — corroborates the power-distance scale identification from batch03 |
| `suicide_reinbergs_2025_ghsq` | General Help-Seeking Questionnaire, verbatim |
| `gilbert_meta_105` | Complete, standard social-support item themes |
| `gilbert_meta_49` | WHO SRQ-20, verbatim |
| `florida_twins_auth` | 100/100 items confirmed verbatim against the codebook's Author Recognition Test list |
| `sun_2025_morality_study3_neuroticism` | BFI-2 Neuroticism facet, verbatim |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (2) — filed as GitHub issues

| Table | Issue | Problem |
|---|---|---|
| `singh_2025_identity_pit` | [#1619](https://github.com/ben-domingue/irw/issues/1619) | Curated 5th item (`pit5`) doesn't exist in live data (4 items); resp direction is correct, verified against the paper's stated scale |
| `gilbert_meta_42` | [#1620](https://github.com/ben-domingue/irw/issues/1620) | 8 of 20 items (`life_satisfaction_*`, `locus_of_control_*`) have entirely blank `item_text` |

## ⚪ Gray (2) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `threat_isler_2024_exp2_picture_panas` | Same gray classification as other `threat_isler_2024` PANAS tables — no separate instrument materials found |
| `threat_isler_2024_exp1_incentive_panas` | Same as above |

## Net result

2 real issues filed. Notably productive batch for source-document recovery: converted an old binary `.doc` codebook via LibreOffice (`soffice --headless --convert-to txt`) to confirm `florida_twins_behavior_ecs` verbatim — worth remembering as a technique for `.doc` (not `.docx`) sources going forward. Cumulative across all 6 batches: 19 GitHub issues filed.
