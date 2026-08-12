# ENEM IRW Project Log

**Contributor:** Mateus Mazzaferro  
**Started:** 2025-06-25  
**GitHub issues:** [#955](https://github.com/ben-domingue/irw/issues/955), [#723](https://github.com/ben-domingue/irw/issues/723), [#1403](https://github.com/ben-domingue/irw/issues/1403)

---

## Phase 0 � Environment (2025-06-25)

| Check | Status |
|-------|--------|
| R 4.5.1 | OK � `C:\Program Files\R\R-4.5.1\bin\Rscript.exe` |
| tidyverse | Installed |
| vroom | Installed |
| readr | Installed (via tidyverse) |
| Disk (C:) | Sufficient for processing (~710 MB + ~496 MB ZIPs downloaded) |

### Local data inventory

| File | Location | Notes |
|------|----------|-------|
| `microdados_enem_2023.zip` | `ENEM/downloads/` | Downloaded from INEP |
| `microdados_enem_2024.zip` | `ENEM/downloads/` | Downloaded from INEP |
| Extracted 2023 | `ENEM/extracted_2023/` | Contains `MICRODADOS_ENEM_2023.csv` (classic format) |
| Extracted 2024 | `ENEM/extracted_2024/` | Split format: `PARTICIPANTES`, `RESULTADOS`, `ITENS_PROVA` |
| Partial 2024 (pre-existing) | `ENEM/DADOS/` | Same split files + provas PDFs/DOSVOX |
| Provas 2024 | `ENEM/PROVAS E GABARITOS/` | PDFs + 2 DOSVOX `.txt` files |

### Format change (2024)

INEP 2024 microdata no longer ships a single `MICRODADOS_ENEM_2024.csv`. Response fields live in `RESULTADOS_2024.csv`; participant IDs (`NU_INSCRICAO`) are in `PARTICIPANTES_2024.csv`. Files are row-aligned (same row count); processing joins by row order after verifying alignment.

---

## Phase 1 � Response processing

*(Updated as runs complete)*

| Year | Area | Rows | IDs | Items | resp range | Status |
|------|------|------|-----|-------|------------|--------|
| 2023 | lc | 40,000,000 | 1,000,000 | 82 | 0-1 | done |
| 2023 | ch | 45,000,000 | 1,000,000 | 90 | 0-1 | done |
| 2023 | cn | 45,000,000 | 1,000,000 | 93 | 0-1 | done |
| 2023 | mt | 45,000,000 | 1,000,000 | 93 | 0-1 | done |
| 2024 | lc | 41,345,105 | 1,000,000 | 42 | 0-1 | done |
| 2024 | ch | 45,000,000 | 1,000,000 | 46 | 0-1 | done |
| 2024 | cn | 45,000,000 | 1,000,000 | 93 | 0-1 | done |
| 2024 | mt | 45,000,000 | 1,000,000 | 94 | 0-1 | done |

---

## Phase 2 � Item text

*(Updated as item text tables are built)*

---

## Decisions log

| Date | Decision |
|------|----------|
| 2025-06-25 | Priority: 2023�2024 responses first, then item text backfill |
| 2025-06-25 | Subsample: 1M IDs, `set.seed(5150)` (per Ben, issue #955) |
| 2025-06-25 | Processing on local machine; Stanford server if too slow |
