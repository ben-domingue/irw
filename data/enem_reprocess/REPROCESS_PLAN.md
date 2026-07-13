# ENEM Re-processing → Regular-Application-Only Tables (2013–2025)

## Context

While preparing to add item text to the ENEM tables in the IRW, we discovered that the pushed/live ENEM response tables **mix multiple exam rounds**: the regular (main) application plus *reaplicação* (PPL) and, in some years, ENEM Digital. Verified consequences:

- Each area's items split into **disjoint 45-item pools** (regular vs reapplication share **0 items and 0 students**). The wide matrix is **block-diagonal and unlinked** — not one instrument but several parallel forms concatenated.
- The reapplication block is tiny: e.g. 2023 CH = **998,173 regular vs 1,827 reapplication** students; reapplication contributes ~half the item *universe* for <0.2% of respondents.
- Density in `metadata.csv` = `45 / n_items`, so `≈1.0`=1 round, `≈0.5`=2, `≈0.33`=3 (2017, 2020).

**Ben approved re-processing to provision cleaner data.** Objective: restrict **every ENEM table (2013–2025) to the main/regular-application items only**, yielding clean, fully-dense (density = 1.0), single-instrument tables where every item is text-linkable with high confidence. **Push cleaned tables first; build item text later** — but verify now that text is obtainable for every retained item.

## Principled main-item identification (verified, not "more data")

The INEP microdata **dictionary** (`Dicionário_Microdados_Enem_YYYY.xlsx`) labels every `CO_PROVA` value with its booklet color, suffixing reapplication ones `(Reaplicação)` (and Digital where present). Rule:

> **Main items = `CO_ITEM`s whose `CO_PROVA` is a POSITIVELY-labeled regular color** (Azul/Amarela/Branca/Rosa/Verde + their Ampliada/Superampliada/Braille/Libras/**Ledor** accessibility variants), excluding any label containing "Reaplicação"/"Digital".

Identify regular **positively** — absence of a label ≠ regular, because dictionaries don't enumerate every printed variant (2023 dict labeled only 52 of 120 codes; the 68 unlabeled add **no new items**). **Validated on 2023 CH:** dict-regular = exactly 45 items, each with 998,173 respondents; the 45 reapplication items each 1,827; the two methods agree perfectly (bimodal, no gray zone). **Fallback** if a year's dictionary lacks usable labels: the "majority respondent count" split (clean bimodal). Expected main-item counts ≈45/area, but **LC ≈ 50–52** (English+Spanish bilingual items) and **CN/MT sometimes 48** (accessibility-adapted item substitutions — still regular).

## Scope — 13 years × 4 areas (`enem_YYYY_1mil_{lc,ch,cn,mt}`)

| Group | Years | State | Action |
|-------|-------|-------|--------|
| Live, multi-pool | 2014–2018, 2020, 2021, 2022 | on Redivis | clean to regular-only |
| Live, already ~1 pool | 2013, 2019 | on Redivis, density≈1.0 | filter is a **no-op**; confirm & keep |
| Local, not uploaded | 2023, 2024 | raw on disk in `ENEM/` | reprocess regular-only, then upload |
| New | 2025 | on portal, **not downloaded** | download + process fresh |
| Missing script | 2021 | live table, **no `enem_2021.R`** | write new script |

## Decisions locked
- **Redivis:** Mateus has no token → I produce all artifacts locally (scripts, cleaned `.Rdata`/`.csv`, regular-item lists, QC logs) + open a PR; **Ben uploads / versions** the tables.
- **Sampling (recommended):** **full reprocess from raw**, drawing a fresh **1M sample from regular-application examinees only** (`set.seed(5150)`), giving exactly-1M, uniform, authoritative tables. See tradeoff below.
- **Item text:** verify availability now; the full 4-sheet PT+EN build (prior plan) is a later phase.

### Finalized definitions (locked with Mateus 2026-07-13)
- **Main items = STANDARD regular-booklet items** (plain colors Azul/Amarela/Branca/Rosa/Cinza; exclude Ampliada/Superampliada/Braille/Ledor/Libras/Videoprova/Adaptada, Reaplicação, Digital). Gives a clean 45 for CH/CN/MT at density ≈ 1.0. Accessibility students are kept but their non-standard substitute items are dropped (negligible residual sparsity).
- **LC keeps BOTH languages** (English + Spanish), documented as sparse (#723): universe ≈ 50 items, each student answers 45 (40 common + 5 in their `TP_LINGUA`), density ≈ 0.9. Map Q1–5 via the student's `TP_LINGUA` (0=Eng,1=Esp) — do NOT drop the ambiguous positions as the old pipeline did.
- **Method = B, full reprocess from raw** (necessary, not just preferred): filtering existing tables cannot implement LC-keep-both (old tables already dropped those items) nor hit exactly 1M. Sample **1M from regular-application examinees** (`set.seed(5150)`), then keep standard items per area. Heavy years → **Stanford cluster**; 2023/2024 run locally (raw on disk).

### Implementation detail — self-contained per-year scripts
Each `enem_YYYY.R` hardcodes two small vectors derived from that year's dictionary: `standard_prova_codes` (defines the main item set via `ITENS_PROVA$CO_ITEM[CO_PROVA %in% standard_prova_codes]`) and `regular_prova_codes` (defines regular examinees for the 1M sample). No xlsx dependency at runtime (readxl not installed); the code vectors are generated offline by `ENEM/scripts/identify_regular_items.py`. Validate at runtime that the standard item set == the majority-respondent set (fallback if a year's dict lacks labels).

## Approach / phases

**Phase 0 — Regular-item identifier (shared, already prototyped).** A self-contained block (inlined per script, per IRW's "no shared deps in `data/`" convention) that: parses the year's dictionary → regular `CO_PROVA` set → main `CO_ITEM` set per area; asserts against the majority-count fallback. Reference prototype logic already validated this session.

**Phase 1 — Acquisition (human, Mateus).** Download INEP microdata ZIPs for the backfill years (2013–2022) + 2025; 2023/2024 already on disk. Each ZIP contains `DADOS/` (microdata + `ITENS_PROVA`) and `DICIONÁRIO/`. I provide the exact file checklist.

**Phase 2 — Reprocess scripts (`irw/data/`).**
- Extend the existing `enem_YYYY.R` (2013–2020, 2022) and `enem_2023.R`/`enem_2024.R` with: (i) regular-only filter via Phase 0, (ii) 1M sample drawn from regular examinees. Reuse `enem_2022.R` (single-file microdata) and `enem_2024.R` (split `PARTICIPANTES`+`RESULTADOS`) as templates.
- Write **new `enem_2021.R`** and **`enem_2025.R`** from those templates (confirm each year's raw file layout first — INEP has changed formats over time).
- Output unchanged schema `id | item | resp | position | booklet`, now density = 1.0.

**Phase 3 — Validation (per table).** Assert: density = 1.0; `n_items` = regular count (≈45; LC 50–52; adapted 48); a single item-pool; `resp ∈ {0,1}`; ~1M ids; retained item set == dict-regular set (and == majority-count set). Emit a QC log mirroring the handoff's QC table. Diff against old live `n_items` to show exactly which items were dropped.

**Phase 4 — Item-text availability audit (no build yet).** Per year, confirm the regular accessible caderno (**Ledor / Leitor de Tela**) exists and covers all main items (2023 already on disk & verified). Produce `text_availability.csv` flagging any main item lacking a text source — so the later text phase is turn-key.

**Phase 5 — PR, docs, upload.** PR the scripts to `ben-domingue/irw` referencing #955/#1403. Prepare paste-ready data-dictionary + tags updates (note the round-cleaning; `item_text_provided` stays **No** until the text phase). Ben re-uploads/versions the 40 live tables and adds 2023/2024/2025. Draft the #723 note update (sparsity now resolved for the main tables).

**Phase 6 — Item text (later).** Full 4-sheet PT+EN build on the clean main items, official image descriptions (`[pic: ...]`) with AI fallback — per the earlier item-text design.

## Critical files
- Templates: [`irw/data/enem_2022.R`](irw/data/enem_2022.R), [`irw/data/enem_2024.R`](irw/data/enem_2024.R), [`irw/data/enem_2013.R`](irw/data/enem_2013.R).
- Per-year inputs: `ENEM/extracted_YYYY/DADOS/ITENS_PROVA_YYYY.csv`, `.../DICIONÁRIO/Dicionário_Microdados_Enem_YYYY.xlsx`.
- Metadata reference: [`irw/metadata/metadata.csv`](irw/metadata/metadata.csv) (density/n_items to diff against).
- Validation outputs → `ENEM/output/` + `irw-work-docs/`.

## Verification (prove on 2023 first — raw already on disk)
1. Run reprocessed `enem_2023.R` → 4 tables; QC log shows density = 1.0, CH n_items = 45 (LC 50–52), single pool, resp ∈ {0,1}, ~1M ids.
2. Confirm retained CH item set == the 45 dict-regular items == the 45 majority-count items (all three agree).
3. Repeat on 2024 (on disk). Only then scale to downloaded years (2013–2022, 2025), likely on the Stanford cluster.
4. Text-availability audit on 2023 passes (all 45×4 main items covered by the on-disk Ledor caderno).

## Human-intervention points
- **Downloads:** all backfill years (2013–2022) + 2025 microdata ZIPs (Mateus).
- **Compute:** Stanford cluster for the full-reprocess runs (Option B).
- **Redivis:** Ben uploads/versions every table (Mateus has no token).
- **Format confirmation:** 2021 & 2025 raw layouts before finalizing their scripts.
