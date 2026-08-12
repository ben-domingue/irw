# Audit mode: Batch 11

**Date:** 2026-08-22
**Scope:** 25 fresh tables, random draw from the 81-table remaining pool
**Total:** 25 tables

## Summary

| | n |
|---|---|
| 🟢 Green | 25 |
| 🟡 Yellow | 0 |
| 🔴 Red | 0 |
| ⚪ Gray | 0 |

---

## 🟢 Green (25) — all tables

Fourth all-green batch (after batch05, batch08, batch09). Highlights:
- **`narqing` false-alarm resolved**: table name suggested NARQ content but an initial truncated item list only showed `meim_*` items (alphabetically first). Full fetch confirmed all 40 items across 3 combined instruments (NARQ, RSE, MEIM) exactly matching the dictionary description — a good reminder to check the full item list, not just a `head()` preview, before flagging a mismatch.
- `shu_2025_translation_pgv` adds corroborating evidence to the existing #1614 finding (same "pishp" item-pool family cited to the 9-item MCPIS-9 paper) — not a new issue, just more data for that one.
- `firstborn_personality` regression check (original pilot's Fix 1 example) still holds.
- Many more standardized-instrument matches: PSS-10, Berlin Numeracy Test (4/4 verbatim), DASS-21 Anxiety, BSI Anxiety, PSPCSA, ASLEC, Unintentional Procrastination Scale.
- `eammi_grahe_2018_marriage_attitudes` again showed curation more complete than the EAMMi2 codebook's own sparse labels (same pattern as `belong`/NPI items earlier).

## 🟡 Yellow (0) / 🔴 Red (0) / ⚪ Gray (0)

None this batch.

## Net result

Fourth zero-issue batch. Cumulative across all 11 batches: 22 GitHub issues filed (unchanged this batch). Remaining pool: ~56 tables (81 − 25).
