# Itemtext Audit — Omnibus Report (Batches 1–13)

**Status: complete.** Every table in the ~421-table IRW itemtext pool has
now been checked at least once — either in the original 100-table
blind-extraction eval (`itemtext/skill_test/sessionA/B/C_batch`), or in this
13-batch audit. This audit ran 330 individual table checks (the pilot's 9
known-drift regression checks + 15 fresh, plus 306 tables across batches
2–13); excluding the 9 regression repeats (already covered by the original
eval), it added 321 tables never checked before — bringing total pool
coverage to 100 (original eval) + 321 (this audit) = 421.

This document rolls up all 13 individual batch reports
(`batch01_pilot.md` – `batch13.md`, kept in place unmodified) into one
place. See the individual files for full per-table detail; this report
gives the totals, the full issue list, and the patterns that recurred
across batches.

## What this audit does

Audit mode (`irw-auto-itemtext` skill) reprocesses a table that already has
a Redivis-curated itemtext entry: extract item text blind from the primary
source (same Steps 2–4 as the normal skill), diff it against
`irw::irw_itemtext(table)`, and classify into one of four outcomes:

- 🟢 **Green** — curated version and fresh extraction are close enough. No action.
- 🟡 **Yellow** — curation stays, but there's a specific documentable issue worth a public callout on `itemtext_issues.qmd`. Draft text only, never applied directly.
- 🔴 **Red** — needs human review/replacement. Filed as a GitHub issue (`ben-domingue/irw`, labels `data fix`+`ITEMS`). Never auto-uploaded — `upload.py` replaces a table's entire content on conflict, so every replace candidate is Ben's call.
- ⚪ **Gray** — unverifiable (blocked/missing source), but no evidence of a problem. Logged as a retry candidate, not a resolved outcome.

## Overall totals

| | n |
|---|---|
| Individual table checks | 330 |
| 🟢 Green | 275 |
| 🟡 Yellow | 1 |
| 🔴 Red | 24 |
| ⚪ Gray | 30 |

24 red-classified tables break down as: 1 pre-existing issue corroborated
(#1594, filed before this audit began) + 22 new issues filed by this audit,
one of which (#1614) covers 2 tables — so 22 new issues cover 23 tables,
plus the 1 pre-existing = 24 total.

**Zero-issue batches:** 6 of 13 (05, 08, 09, 11, 12, 13).

**Core finding, held with zero exceptions across all 13 batches:** every
real disagreement between the skill's blind extraction and the existing
Redivis curation traced back to the curation being stale, incomplete,
mislabeled, or reflecting a live-data bug — never to the fresh extraction
being wrong. No case in the whole audit required overriding a *correct*
curated entry with a worse one.

## Per-batch summary

| Batch | Date | Tables | 🟢 | 🟡 | 🔴 | ⚪ | Notes |
|---|---|---|---|---|---|---|---|
| 01 (pilot) | 2026-08-12 | 24 (9 known-drift + 15 fresh) | 7 | 1 | 11 | 5 | Regression set + first fresh sample; established the 4-status framework |
| 02 | 2026-08-13 | 25 | 16 | 0 | 2 | 7 | #1609, #1611 |
| 03 | 2026-08-14 | 25 | 18 | 0 | 5 (4 issues) | 2 | #1613–#1616; first "item count vs. cited source" mismatch |
| 04 | 2026-08-15 | 25 | 18 | 0 | 2 | 5 | #1617, #1618; first mislabel-within-paper + item-code collision |
| 05 | 2026-08-16 | 25 | 20 | 0 | 0 | 5 | First zero-issue batch |
| 06 | 2026-08-17 | 25 | 21 | 0 | 2 | 2 | #1619, #1620; LibreOffice `.doc`→txt technique introduced |
| 07 | 2026-08-18 | 25 | 21 | 0 | 1 | 3 | #1621; dictionary-Description-only error |
| 08 | 2026-08-19 | 25 | 25 | 0 | 0 | 0 | All green |
| 09 | 2026-08-20 | 25 | 25 | 0 | 0 | 0 | All green |
| 10 | 2026-08-21 | 25 | 23 | 0 | 1 | 1 | #1622; item literally named `"NA"` |
| 11 | 2026-08-22 | 25 | 25 | 0 | 0 | 0 | All green; `narqing` false-alarm resolved |
| 12 | 2026-08-23 | 25 | 25 | 0 | 0 | 0 | All green |
| 13 | 2026-08-12 | 31 (final — pool exhausted) | 31 | 0 | 0 | 0 | All green; corroborated #1614 and #1617 |

## Full GitHub issue list (22 issues, 24 tables)

| Issue | Table(s) | Problem |
|---|---|---|
| [#1594](https://github.com/ben-domingue/irw/issues/1594) | `political_psychology` | 7/37 items have wrong resp-scale mappings (pre-existing, filed before this audit; audit corroborated it) |
| [#1598](https://github.com/ben-domingue/irw/issues/1598) | `dumas_organisciak_2022` | Missing `instructions` field entirely |
| [#1599](https://github.com/ben-domingue/irw/issues/1599) | `ccapsvtskhpacr_mercedes_2023_tsk` | 2 of 4 response-scale labels missing |
| [#1600](https://github.com/ben-domingue/irw/issues/1600) | `sv-maia2_randelovic_2021_erq` | Curated resp scale (1–7) stale vs. live (1–5) |
| [#1601](https://github.com/ben-domingue/irw/issues/1601) | `sv-maia2_randelovic_2021_hexaco60` | 24/60 items have NA resp despite live data existing |
| [#1602](https://github.com/ben-domingue/irw/issues/1602) | `chile_2023_social-welfare-survey_h` | `h3_e` missing resp category 3 |
| [#1603](https://github.com/ben-domingue/irw/issues/1603) | `shu_2025_translation_eib` | `eib_pishp232` missing resp category 1 |
| [#1604](https://github.com/ben-domingue/irw/issues/1604) | `eammi_grahe_2018_socmedia` | `SocMedia_bias_dummy` resp is NA despite live data existing |
| [#1605](https://github.com/ben-domingue/irw/issues/1605) | `threat_isler_2024_exp4_cog_crt` | Only 1 of 3 live items documented |
| [#1606](https://github.com/ben-domingue/irw/issues/1606) | `gilbert_meta_80` | 8 curated items don't exist in live data (orphaned) |
| [#1607](https://github.com/ben-domingue/irw/issues/1607) | `gilbert_meta_78` | 3 curated items don't exist in live data (orphaned) |
| [#1609](https://github.com/ben-domingue/irw/issues/1609) | `singh_2025_identity_cse` | Response-scale direction reversed vs. source paper |
| [#1611](https://github.com/ben-domingue/irw/issues/1611) | `preschool_sel_akt` | Curation covers 17/65 live items; whole 2nd subtest undocumented |
| [#1613](https://github.com/ben-domingue/irw/issues/1613) | `eammi_grahe_2018_npi` | `item_text` entirely blank for all 13 items |
| [#1614](https://github.com/ben-domingue/irw/issues/1614) | `shu_2025_translation_pcd`, `shu_2025_translation_srt` | 21 items combined, cited source paper explicitly a 9-item scale (MCPIS-9) — corroborated in batch11 (`_pgv`) and batch13 (`_mcpis`, the genuine 9-item table) |
| [#1615](https://github.com/ben-domingue/irw/issues/1615) | `gilbert_meta_35` | 4/12 items entirely blank `item_text` |
| [#1616](https://github.com/ben-domingue/irw/issues/1616) | `double_marking_steele_2022` | `item_text` is bare section name; real per-section rubric uncaptured |
| [#1617](https://github.com/ben-domingue/irw/issues/1617) | `rmet_higgins_2022_tom` | Table implies RMET; content is actually the Imposing Memory Task — corroborated isolated (not systemic) in batch10 (`_aq`, `_tas`) and batch13 (`_rmet`, the genuine table) |
| [#1618](https://github.com/ben-domingue/irw/issues/1618) | `pezzuti_2025_coolpeople_main_big5_southkorea` | Item `korean_big5_faults` conflates 2 BFI-10 questions under 1 item code (live-data collision) |
| [#1619](https://github.com/ben-domingue/irw/issues/1619) | `singh_2025_identity_pit` | Curated 5th item doesn't exist in live data |
| [#1620](https://github.com/ben-domingue/irw/issues/1620) | `gilbert_meta_42` | 8/20 items entirely blank `item_text` |
| [#1621](https://github.com/ben-domingue/irw/issues/1621) | `heekerens2025_bfi_neuroticism` | Dictionary Description says "Openness" — corroborated isolated in batch10 (`_openness` sibling correctly labeled) |
| [#1622](https://github.com/ben-domingue/irw/issues/1622) | `lys_2020_rape_1_rma` | Live 20th item literally named `"NA"`, 742 all-missing rows (live-data bug) |

## Recurring failure patterns

1. **Stale resp scale/category** — curated response options don't match what's actually live (#1594, #1600, #1602, #1603).
2. **Field exists but is entirely blank** — `item_text`/`instructions` present as a column but empty for some or all rows (#1598, #1601, #1604, #1613, #1615, #1616, #1620). The most common pattern by count.
3. **Orphaned curated items** — curation documents items that no longer exist in the live table (#1606, #1607, #1619).
4. **Source-attribution / instrument mislabeling** — table name, dictionary Description, or cited source doesn't match the actual content (#1605, #1614, #1617, #1621). Always checked (and in every case here, confirmed) to be isolated to one table rather than systemic across a paper's other tables.
5. **Live-data construction bugs** — item-ID collisions or garbage item rows in the underlying data itself, not a curation-text problem (#1618, #1622).
6. **Undocumented sub-instrument** — curation covers only part of a live multi-part measure (#1611).

## Techniques that proved reusable across batches

- **Recognize well-known standardized instruments directly** (PHQ-9, GAD-7, PSS-10, BFI/IPIP facets, RSES, DASS-21, HADS, CRT, etc.) rather than re-fetching a primary source every time — most green classifications in the back half of the audit came from this.
- **R package documentation as a primary source**: `library(tools); Rd_db("PackageName")` gives verbatim item wording fast for CRAN-hosted datasets (MPsychoR, psychTools, psychotools, PCMRS).
- **LibreOffice headless conversion** for old binary `.doc` codebooks that Python's `zipfile`-based `.docx` parser can't touch: `soffice --headless --convert-to txt file.doc`.
- **Check the full item list, not a truncated preview** — a `head()`/default-print truncation caused at least two false alarms (`narqing` in batch11, an overstated `dumas_organisciak_2022` finding in the pilot) before being caught.
- **Row-count-per-item as a cheap diagnostic** — catches item-ID collisions that content review alone would miss (`table(gt$item)`, used to find #1618).
- **Check the sibling tables from the same paper/project** before assuming a mislabeling is systemic — every mislabel found in this audit turned out to be isolated to one table (#1617, #1621), confirmed by checking siblings.
- **Literal string `"NA"` vs. true `NA`** — some curated data stores missing values as the string `"NA"`; base `is.na()` misses these, `diff_itemtext.R`'s `is_missing()` helper checks for both.

## Outstanding

- The single yellow-bucket item from the whole audit — `florida_twins_friends` (2 undocumented items, `friends20`/`friends21`) — has drafted website text (see `batch01_pilot.md`) but it was never pasted into the live `itemtext_issues.qmd` at `/home/ben/Dropbox/projects/irw/irw_site/itemtext_issues.qmd`.
- No further audit batches are scheduled; the pool is exhausted. A future re-run would only make sense after a substantial batch of new itemtext tables is added, or periodically as a spot-check.
