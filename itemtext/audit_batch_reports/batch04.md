# Audit mode: Batch 4

**Date:** 2026-08-15
**Scope:** 25 fresh tables, random draw from the 256-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 18 |
| 🟡 Yellow | 0 |
| 🔴 Red | 2 |
| ⚪ Gray | 5 |

---

## 🟢 Green (18)

| Table | Note |
|---|---|
| `assessment_time_fournier_2025_phq` | PHQ-9, verbatim |
| `gilbert_meta_62` | PHQ-4, verbatim |
| `heekerens2025_sdq` | SDQ-20 (German), content pattern match |
| `mpsycho_wenchuan` | Standard PTSD symptom-checklist content |
| `aps_vangsness_2019` | Active Procrastination Scale (Choi & Moran, 2009), verbatim |
| `sun_2025_morality_study2_colleaguelike` | Single-item liking measure, structurally consistent |
| `sun_2025_morality_study1_morality` | Moral-character-rating item phrasing, consistent |
| `pezzuti_2025_coolpeople_powerful` | Plausible custom power-perception items |
| `gilbert_meta_34` | PHQ-9, verbatim |
| `sun_2025_morality_study1_respectfulness` | BFI-2 Respectfulness facet, verbatim |
| `fcv19s_hossain_2022__fear` | Fear of COVID-19 Scale (FCV-19S), verbatim |
| `heard_roch_2022_cope` | Brief COPE item themes, consistent |
| `estcrm_epia` | EPI Impulsiveness subscale + correctly-documented VAS scoring, verbatim |
| `360emergencymed_azami_2024` | Complete, professional 55-item clinical evaluation instrument |
| `gilbert_meta_11` | Matches the already-verified `gilbert_meta_12` item template |
| `eammi_grahe_2018_efficacy` | General Self-Efficacy Scale (Schwarzer & Jerusalem, 1995), verbatim |
| `gilbert_meta_82` | 18/18 items match live data exactly, no orphaned-item gap |
| `amatus_cipora_2024_bfi_n` | BFI-2 Neuroticism facet, verbatim |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (2) — filed as GitHub issues

| Table | Issue | Problem |
|---|---|---|
| `rmet_higgins_2022_tom` | [#1617](https://github.com/ben-domingue/irw/issues/1617) | Table name/description imply this is the RMET (eye-photo test), but content is actually the **Imposing Memory Task** (story-vignette ToM measure), a distinct instrument from the same paper — labeling/attribution issue, not necessarily wrong item text |
| `pezzuti_2025_coolpeople_main_big5_southkorea` | [#1618](https://github.com/ben-domingue/irw/issues/1618) | Item `korean_big5_faults` conflates 2 different BFI-10 questions under one item code — a live-data identifier collision, not just a curation display issue |

## ⚪ Gray (5) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `gilbert_meta_50` | Plausible, complete; source (Dataverse) WAF-blocked |
| `gilbert_meta_99` | Plausible, complete; source (Dataverse) WAF-blocked |
| `gilbert_meta_106` | Plausible, complete; source (Dataverse) WAF-blocked |
| `gilbert_meta_31` | ASER assessment-ladder items match the well-known public tool's level descriptions; this specific study's materials not accessed (Dataverse WAF-blocked) |
| `gilbert_meta_36` | Plausible, complete; source (Dataverse) WAF-blocked |

## Net result

2 real issues filed — both new failure patterns not seen in earlier batches: a table mislabeled with the wrong instrument name (like the pilot's Fix 4 cases, but for a within-paper secondary measure rather than a different paper entirely), and a live-data item-code collision (2 questions sharing 1 item ID) rather than a curation-only problem. Cumulative across all 4 batches: 17 GitHub issues filed.
