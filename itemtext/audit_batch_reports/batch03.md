# Audit mode: Batch 3

**Date:** 2026-08-14
**Scope:** 25 fresh tables, random draw from the 281-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 18 |
| 🟡 Yellow | 0 |
| 🔴 Red | 5 (4 unique issues — `shu_2025_translation_pcd`/`srt` share #1614) |
| ⚪ Gray | 2 |

---

## 🟢 Green (18)

| Table | Note |
|---|---|
| `gilbert_meta_98` | GQ-6 (McCullough et al., 2002), verbatim |
| `rd_ppcvdos_padconacns_jinbo_2019_dos` | Duesseldorf Orthorexia Scale, Chinese, content pattern match |
| `qaslu_lopez_2024` | Confirmed as the legitimate 45-item QaSLu-45 pre-reduction pool, not a mismatch with the QaSLu-27 name |
| `sv-maia2_randelovic_2021_hexaco100` | HEXACO-100, Serbian, content pattern match |
| `pezzuti_2025_coolpeople_hedonistic` | PVQ Hedonism facet, verbatim — also corroborates batch02's PVQ identification for `traditional`/`conforming` |
| `mpsycho_bsss` | Brief Sensation Seeking Scale (BSSS-8), verbatim |
| `gilbert_meta_89` | CREDI child-development items, content/format match |
| `singh_2025_identity_irs` | Matches paper's own quoted sample items; resp direction correct (unlike the companion CSE table, #1609) |
| `os_tbmwtfs_schubert_2023_maas` | Mindful Attention Awareness Scale, verbatim |
| `pezzuti_2025_coolpeople_main_powerdistance_usa_chile` | Standard individual-level Power Distance Belief scale, verbatim |
| `mexico_2023_quality_drainage` | Well-structured, correct stem/item split (contrast with earlier mexico_2023_quality_problems/administration gaps) |
| `singh_2025_identity_gi` | Plausible ethnic-identity content; resp direction correct |
| `pezzuti_2025_coolpeople_main_tight_usa_chile` | Gelfand's Tightness-Looseness Scale, verbatim |
| `gps_vangsness_2019` | Lay's General Procrastination Scale, verbatim |
| `oxfordcovid_xue_2024_pswq_c` | PSWQ-C (child), verbatim |
| `oxfordcovid_xue_2024_pswq_a` | PSWQ (adult), verbatim |
| `gilbert_meta_57` | PHQ-9, verbatim |
| `sun_2025_morality_study2_informant-moral-character` | Same 10-trait Chinese set already confirmed in the pilot, informant-rating structure consistent |

## 🟡 Yellow (0)

None this batch.

## 🔴 Red (4 issues, 5 tables) — filed as GitHub issues

| Table | Issue | Problem |
|---|---|---|
| `eammi_grahe_2018_npi` | [#1613](https://github.com/ben-domingue/irw/issues/1613) | `item_text` entirely blank for all 13 items; partial content recovered from the study's own codebook |
| `shu_2025_translation_pcd` + `shu_2025_translation_srt` | [#1614](https://github.com/ben-domingue/irw/issues/1614) | 21 items combined, but their cited source paper is explicitly about a **9-item** scale (MCPIS-9) — likely a source-attribution mismatch, not necessarily wrong item text |
| `gilbert_meta_35` | [#1615](https://github.com/ben-domingue/irw/issues/1615) | 4 of 12 items have entirely blank `item_text` |
| `double_marking_steele_2022` | [#1616](https://github.com/ben-domingue/irw/issues/1616) | `item_text` is just the bare section name; the source has a detailed grading rubric per section, entirely uncaptured |

## ⚪ Gray (2) — unverifiable, not evidence of a problem

| Table | Why unverified |
|---|---|
| `gilbert_meta_83` | Content matches Need for Closure Scale pattern; source (Dataverse) WAF-blocked |
| `gilbert_meta_61` | 3/6 items read as grammatically incomplete short labels rather than full question text; may be an intentional abbreviated style, source WAF-blocked |

## Net result

4 real issues filed (covering 5 tables). Two of them (#1613, #1616) are the same "field exists but is empty" pattern as `dumas_organisciak_2022` from the pilot. One (#1614) is a new pattern — item count mismatched against the cited source's own stated scale size, worth checking for elsewhere. Cumulative running total across all 3 batches: 15 GitHub issues filed (#1594, #1598–#1607, #1609, #1611, #1613–#1616).
