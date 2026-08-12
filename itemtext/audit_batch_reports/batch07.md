# Audit mode: Batch 7

**Date:** 2026-08-18
**Scope:** 25 fresh tables, random draw from the 181-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 21 |
| 🟡 Yellow | 0 |
| 🔴 Red | 1 |
| ⚪ Gray | 3 |

---

## 🟢 Green (21)

Many standardized-instrument verbatim matches this batch: UPPS-P-20-R, SWEMWBS, Boredom Proneness Scale, IDEA, Brief Resilience Scale, IPIP-50 Openness, Intolerance of Uncertainty Scale, FFMQ, Short Grit Scale (8-item), plus 2 more `florida_twins_*` LDbase codebook confirmations (`florida_twins_nes`, 10/10 items verbatim) and 2 more Yoo/Donthu/Lenartowicz CVSCALE dimensions for the `pezzuti_2025_coolpeople` project (collectivism, uncertainty avoidance).

| Table | Note |
|---|---|
| `singh_2025_identity_pia` | Matches paper's own quoted sample item; resp direction correct |
| `oxfordcovid_xue_2024_ua` | Complete, plausible custom COVID-university-admission measure |
| `eammi_grahe_2018_idea` | IDEA, verbatim |
| `assessment_time_fournier_2025_upps` | UPPS-P-20-R, verbatim |
| `idcr_martinez_2023_story_recall_1` | Same verified pattern as this table family |
| `gilbert_meta_102` | Same vocabulary-task family as gilbert_meta_11/12 |
| `gilbert_meta_60` | Complete, plausible political-attitude items |
| `oxfordcovid_xue_2024_swemws` | SWEMWBS, verbatim |
| `singh_2025_identity_grit` | Short Grit Scale (8-item), verbatim |
| `bps_boredom_bieleke2022` | Boredom Proneness Scale, verbatim |
| `prcpsffmq_lecuona_2017` | FFMQ, verbatim |
| `vermeiren_2022_art` | Internally consistent Author Recognition Test |
| `threat_isler_2024_exp1_incentive_crt` | Same verified CRT item |
| `gilbert_meta_4` | Complete, plausible mood-screening items |
| `florida_twins_nes` | 10/10 items confirmed verbatim against LDbase codebook |
| `ffm_opn` | IPIP-50 Openness facet, verbatim |
| `pezzuti_2025_coolpeople_main_uncertaintyavoidance_usa_chile` | CVSCALE Uncertainty Avoidance, verbatim |
| `preschool_sel_htks` | Plausible repeated-instruction design for HTKS task |
| `oxfordcovid_xue_2024_iusc` | Intolerance of Uncertainty Scale, verbatim |
| `namprb_siwiak_2024_bsr10` | Matches Bullshit Receptivity Scale genre/style |
| `oxfordcovid_xue_2024_brs` | Brief Resilience Scale, verbatim |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (1) — filed as GitHub issue

| Table | Issue | Problem |
|---|---|---|
| `heekerens2025_bfi_neuroticism` | [#1621](https://github.com/ben-domingue/irw/issues/1621) | Table name and item content correctly say Neuroticism; dictionary Description field incorrectly says "Openness" |

## ⚪ Gray (3) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `threat_isler_2024_exp3_cog_panas` | Same gray classification as other `threat_isler_2024` PANAS tables |
| `threat_isler_2024_exp4_cog_panas` | Same as above |
| `rd_eppscqrk_kipkemoi_2024_scq` | Abbreviated domain labels rather than literal SCQ question text; labels do match genuine SCQ item domains |

## Net result

1 real issue filed — a dictionary Description error (wrong subscale name), a new sub-pattern of the table-labeling family of issues. Cumulative across all 7 batches: 20 GitHub issues filed.
