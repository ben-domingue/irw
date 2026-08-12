# Audit mode: Batch 5

**Date:** 2026-08-16
**Scope:** 25 fresh tables, random draw from the 231-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 20 |
| 🟡 Yellow | 0 |
| 🔴 Red | 0 |
| ⚪ Gray | 5 |

---

## 🟢 Green (20)

| Table | Note |
|---|---|
| `cbi_rodriguez_2021` | Creative Behavior Inventory (Brief form), content/format match |
| `sv-maia2_randelovic_2021_maas` | MAAS (Serbian), content pattern match |
| `lys_2020_rape_3_asi` | Ambivalent Sexism Inventory (Glick & Fiske, 1996), content match |
| `os_tbmwtfs_schubert_2023_acs` | Attentional Control Scale (Derryberry & Reed, 2002), verbatim |
| `lys_2020_rape_3_rma` | Illinois Rape Myth Acceptance scale, content match |
| `gilbert_meta_92` | GAD-7, verbatim |
| `sun_2025_morality_study1_meaning` | Meaning-in-life item themes, consistent |
| `gilbert_meta_84` | Plausible, locale-specific conspiracy-belief items (Smoleńsk reference) |
| `mpsycho_asti` | ASTI (Levenson et al., 2005), verbatim across all 25 items via package docs |
| `sun_2025_morality_study3_dependability` | BFI-2 Dependability facet + IPIP trust items, verbatim |
| `florida_twins_grit` | 12-item Grit Scale (Duckworth et al., 2007), verbatim |
| `fedsp_trzcinska_2023_prd` | Personal Relative Deprivation Scale (Callan et al., 2011), content match |
| `mpsycho_wilpat` | Wilson-Patterson Conservatism Scale, matches package docs exactly |
| `fcv19s_hossain_2022_depression` | WHO-5 Well-Being Index, verbatim |
| `idcr_martinez_2023_story_recall_3` | Same verified pattern as this table family's pilot example |
| `sun_2025_morality_study2_colleagueknow` | Single-item-per-target structure, consistent |
| `isi_insomnia_wang2025` | Insomnia Severity Index (Chinese), content pattern match |
| `gilbert_meta_75` | Complete, self-explanatory political-engagement checklist |
| `sun_2025_morality_study1_compassion` | BFI-2 Compassion facet, verbatim |
| `facit_yount_2021_hadsx` | Hospital Anxiety and Depression Scale (HADS), verbatim |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (0)

None this batch — first batch with zero real issues found.

## ⚪ Gray (5) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `florida_twins_tech` | Complete, plausible tech/media-use checklist; not in the cached W1_Child codebook, different source section not checked |
| `facit_yount_2021_crqsasx` | Abbreviated SPSS-style labels rather than literal question text; may be a legitimate source-level style, Dataverse WAF-blocked |
| `threat_isler_2024_exp2_cog_panas` | Same gray classification as `exp1_cog_panas` from batch02 — OSF project has no separate instrument materials |
| `namprb_siwiak_2024_kon2066` | Specialized Polish clinical instrument (KON-2006), no accessible verification source found |
| `swmd_mokken` | Plausible Dutch student-wellbeing scale, no primary source checked |

## Net result

First batch with no red findings — all real content checked out clean or plausible. Cumulative across all 5 batches: 17 GitHub issues filed (unchanged this batch).
