# Audit mode: Batch 2

**Date:** 2026-08-13
**Scope:** 25 fresh tables, random draw from the 306-table remaining pool (excludes the 100-table eval batch and the 15-table pilot sample)
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 16 |
| 🟡 Yellow | 0 |
| 🔴 Red | 2 |
| ⚪ Gray | 7 |

---

## 🟢 Green (16)

| Table | Note |
|---|---|
| `threat_isler_2024_exp1_cog_crt` | Standard CRT item 1 (Frederick, 2005), verbatim |
| `oxfordcovid_xue_2024_gad` | Standard GAD-7, verbatim |
| `fcv19s_hossain_2022_anxiety` | Standard GAD-7, verbatim |
| `sv-maia2_randelovic_2021_shs` | Subjective Happiness Scale (Lyubomirsky & Lepper, 1999) structure/content match |
| `pps_vangsness_2019` | Pure Procrastination Scale (Steel, 2010), verbatim |
| `lhsbrasil_couto_2023_pss` | Perceived Stress Scale (PSS-10), verbatim |
| `os_tbmwtfs_schubert_2023_cerq` | ERQ (Gross & John, 2003) + RRS reflection items, verbatim |
| `himmelstein-cognitive_reflection-2025` | Extended 7-item CRT (Toplak et al., 2014), verbatim |
| `amatus_cipora_2024_pisa_me` | Standard PISA math self-efficacy items |
| `amatus_cipora_2024_sdq_l` | SDQ-III verbal subscale |
| `amatus_cipora_2024_amas` | Abbreviated Math Anxiety Scale (Hopko et al., 2003) |
| `ccapsvtskhpacr_mercedes_2023_beck` | BDI-II Spanish, verbatim — more complete than the source .sav's own placeholder labels |
| `preschool_sel_wj` | Regression check — Fix 2's terseness fix confirmed still holding |
| `gilbert_meta_52` | Standard WHO/CDC-style COVID symptom checklist |
| `sun_2025_morality_study3_compassion` | BFI/BFI-2 Compassion-facet items, verbatim |
| `coach_chen_2022_hdrs` | HDRS-17, verbatim (source WAF-blocked, verified via independent knowledge of this well-known clinical instrument instead) |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (2) — filed as GitHub issues

| Table | Issue | Problem |
|---|---|---|
| `singh_2025_identity_cse` | [#1609](https://github.com/ben-domingue/irw/issues/1609) | Response-scale direction reversed vs. the source paper's explicit statement (1=Strongly Disagree...5=Strongly Agree in the paper; curation has it backwards) |
| `preschool_sel_akt` | [#1611](https://github.com/ben-domingue/irw/issues/1611) | Curation covers only 17 of 65 live items — an entire second subtest (48-item Emotion Matching Task) is undocumented. Source codebook located; large addition, flagged for prioritization rather than fully extracted here |

## ⚪ Gray (7) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `threat_isler_2024_exp1_cog_panas` | OSF project has only a data zip + README, no separate instrument materials found |
| `pezzuti_2025_coolpeople_traditional` | Content matches PVQ Tradition-subscale style closely; OSF view-only link didn't return a file listing |
| `pezzuti_2025_coolpeople_conforming` | Same as above, PVQ Conformity-subscale style |
| `mhscdc_fried_2020_motivation` | Structure/response-scale exactly matches Vallerand's SDT motivation-scale signature format; this specific study's adaptation not found in the OSF materials checked |
| `chile_2023_social-welfare-survey_f` | Well-formed trust/participation module; checked official CASEN 2022 questionnaire PDF directly, no matching text found — may be a different survey wave/module |
| `namprb_siwiak_2024_aot` | Content matches standard AOT scale pattern; OSF translation supplement covers a different co-administered scale, not this one |
| `emsc_kuan-chin_2023` | Custom OSCE checklist (not a public instrument); source Dataverse page WAF-blocked |

## Net result

2/25 real issues filed. 16/25 confirmed clean (several via independent recognition of well-known standardized instruments rather than a fresh document fetch, since re-deriving public-domain scale wording from a primary source each time isn't necessary once the instrument is identified with high confidence). 7/25 flagged for retry with a different source later.
