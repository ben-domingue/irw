# Audit mode: Batch 10

**Date:** 2026-08-21
**Scope:** 25 fresh tables, random draw from the 106-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 23 |
| 🟡 Yellow | 0 |
| 🔴 Red | 1 |
| ⚪ Gray | 1 |

---

## 🟢 Green (23)

| Table | Note |
|---|---|
| `assessment_time_fournier_2025_gad` | GAD-7, verbatim |
| `pezzuti_2025_coolpeople_secure` | PVQ Security facet, verbatim |
| `sun_2025_morality_study2_colleagueclose` | Established single-item-per-target structure |
| `sun_2025_morality_study3_honesty` | Matches established moral-character template |
| `idas_machado2024` | Regression check — original pilot table, still plausible |
| `psychtools_geras` | Gruber et al. (2020) GERAS, verbatim via package docs |
| `gilbert_meta_53` | Specific, plausible gender-attitude items |
| `florida_twins_sch` | 19/19 items confirmed verbatim against LDbase codebook |
| `florida_twins_behavior_tas` | Confirmed verbatim against FTP-BE 2010 .doc codebook |
| `paampsmartsud_saba_2023_attendance` | Simple, plausible attendance-tracking items |
| `mpsycho_condom` | MPsychoR::condom, verbatim (curation corrects a typo in the package doc) |
| `rmet_higgins_2022_aq` | AQ-28, verbatim — confirms #1617's mislabeling was isolated |
| `gilbert_meta_76` | Detailed TEMA-3 administration scripts, plausible |
| `sun_2025_morality_study1_nemotion` | Established negative-emotion-frequency structure |
| `fivpei_perrig_2023_imi` | Intrinsic Motivation Inventory, verbatim |
| `rmet_higgins_2022_tas` | TAS-20, verbatim — same conclusion as AQ |
| `sun_2025_morality_study1_prelationships` | Plausible positive-relationships items |
| `cdm_mentalhealth_tan_2023_rapi` | Rutgers Alcohol Problem Index, content match |
| `suicide_reinbergs_2025_stosa` | STOSA, verbatim — matches dictionary's own quoted sample item |
| `chile_2023_social-welfare-survey_oo` | Complete, consistent with other chile_2023_* tables |
| `amatus_cipora_2024_tai` | Test Anxiety Inventory, content match |
| `eurpar2_mudfold` | Complete, well-formed political-party unfolding items |
| `heekerens2025_bfi_openness` | Confirmed correct — sibling table to #1621's mislabeled Description |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (1) — filed as GitHub issue

| Table | Issue | Problem |
|---|---|---|
| `lys_2020_rape_1_rma` | [#1622](https://github.com/ben-domingue/irw/issues/1622) | Live data has a 20th item literally named `"NA"` with 742 rows, all resp missing — a data-construction bug, not a curation gap |

## ⚪ Gray (1) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `spelling2pronounce_edwards2023` | Single item ("difficulty") with blank item_text; may be structurally expected for this word-bank-style table rather than a genuine gap |

## Net result

1 real issue filed — a live-data naming bug (item literally named `"NA"`), a new pattern distinct from prior batches' curation-content issues. Two useful negative-result checks this batch: `heekerens2025_bfi_openness` confirmed the sibling neuroticism table's dictionary error (#1621) was isolated, and `rmet_higgins_2022_aq`/`tas` confirmed the RMET/IMT mislabeling (#1617) was also isolated to that one table.

**End of run**: batches 6-10 complete (125 tables total). Cumulative across all 10 batches: 22 GitHub issues filed. Remaining pool: ~81 tables (106 − 25).
