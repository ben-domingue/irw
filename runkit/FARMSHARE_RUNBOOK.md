# ENEM Re-processing — FarmShare Runbook & Context

**Purpose:** run the full ENEM 2013–2025 re-processing (main/regular items only) on Stanford
FarmShare, where downloads and compute are cheap. This doc is self-contained so a fresh Claude
Code instance on FarmShare (or Mateus alone) can execute it. Written 2026-07-13.

---

## 1. Context — what we're doing and why (read first)

The live IRW ENEM tables (`enem_YYYY_1mil_{lc,ch,cn,mt}`) mix multiple exam rounds (regular +
*reaplicação* + sometimes Digital). This makes the person×item matrix **block-diagonal and
unlinked** — disjoint item pools, the reapplication block answered by <0.2% of students. Ben
approved re-processing so every table contains **only the MAIN application items**.

**Locked definitions:**
- **Main items = STANDARD regular-booklet items** (plain colors Azul/Amarela/Branca/Rosa/Cinza).
  Exclude accessibility variants (Ampliada/Superampliada/Braille/Ledor/Libras/Videoprova/Adaptada),
  Reaplicação, and Digital. → clean 45 for CH/CN/MT at density ≈ 1.0.
- **LC keeps BOTH languages** (English + Spanish), mapped per student `TP_LINGUA`; intentionally
  sparse (~50 items, density ≈ 0.9; issue #723).
- **Sample 1,000,000 from REGULAR-application examinees** (`set.seed(5150)`).
- Identification is principled (INEP dictionary `CO_PROVA` labels), verified equal to the
  majority-respondent split on 2023 (998,173 vs 1,827). Data-volume is only a fallback.

**Deliverable:** cleaned tables (`.csv` + `.Rdata`), schema `id | item | resp | position | booklet`.
Mateus has **no Redivis token** → Ben uploads/versions. Item text is a **later** phase.

---

## 2. Prerequisites (Mateus)

- **GitHub:** push this workspace's `ENEM/scripts/` + `irw-work-docs/` + the plan to a repo you
  control (your fork of `irw`, or a personal repo). FarmShare clones from there. (Raw data is NOT
  in git — re-downloaded on the cluster.)
- **Anthropic auth on FarmShare:** easiest is an `ANTHROPIC_API_KEY` (headless, no browser). Else
  OAuth via the OnDemand *desktop* browser.
- Know your FarmShare **scratch** path and storage quota (home dirs are small; use scratch).

## 3. One-time setup (OnDemand terminal)

```bash
module load R            # need R 4.x (check: R --version)
module load nodejs       # or use nvm; need Node 18+ for Claude Code (optional)
# optional: install Claude Code to drive interactively
npm install -g @anthropic-ai/claude-code
export ANTHROPIC_API_KEY=...    # if using API-key auth

git clone <your-repo-url> irw-enem && cd irw-enem

# R packages into a user library (first time; can be slow)
Rscript -e 'install.packages(c("tidyverse","vroom"), repos="https://cloud.r-project.org")'
python -m pip install --user pandas openpyxl
```

## 4. Download microdata (on a compute/transfer node, NOT the login node)

All years verified live (HTTP 200) at `download.inep.gov.br/microdados/microdados_enem_YYYY.zip`:

| Year | ~zip size | | Year | ~zip size |
|------|-----------|-|------|-----------|
| 2013 | 892 MB | | 2020 | (large) |
| 2014–2018 | ~0.6–0.9 GB | | 2021 | ~0.6 GB |
| 2019 | 659 MB | | 2022 | 620 MB |
| | | | 2023 | 549 MB |
| | | | 2024 | (split-file yr) |
| | | | 2025 | 630 MB (confirmed live) |

```bash
cd $SCRATCH/enem && for y in 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025; do
  wget -c "https://download.inep.gov.br/microdados/microdados_enem_${y}.zip"
  unzip -o "microdados_enem_${y}.zip" -d "extracted_${y}"
done
```
Each zip extracts to `DADOS/` (microdata + `ITENS_PROVA`) and `DICIONÁRIO/` (the dict xlsx).

## 5. Per-year pipeline (run under SLURM — big CSVs need RAM)

For each year: (a) derive booklet codes from the dictionary, (b) reprocess, (c) validate.

```bash
YEAR=2023; DIR=$SCRATCH/enem/extracted_$YEAR/DADOS
DICT=$(ls $SCRATCH/enem/extracted_$YEAR/DICION*/Dicion*_$YEAR.xlsx)

python ENEM/scripts/identify_regular_items.py --itens $DIR/ITENS_PROVA_$YEAR.csv \
   --dict "$DICT" --year $YEAR --out-dir ENEM/output/regular

ENEM_YEAR=$YEAR ENEM_DATA_DIR=$DIR IRW_ROOT=$PWD \
ENEM_CODES=ENEM/output/regular/enem_${YEAR}_prova_codes.csv \
   Rscript ENEM/scripts/reprocess_enem.R
```

SLURM wrapper (`sbatch`), tune mem/time to the year:
```bash
#!/bin/bash
#SBATCH -J enem -c 4 --mem=32G -t 02:00:00 -o enem_%x_%j.log
module load R
# ... the per-year commands above ...
```

**`reprocess_enem.R` auto-detects layout:** `single` (`MICRODADOS_ENEM_YYYY.csv`, 2013–2023, 2025)
vs `split` (`PARTICIPANTES_YYYY.csv` + `RESULTADOS_YYYY.csv`, 2024). Set `ENEM_DRY_N=200000` for a
fast logic check before the full run.

## 6. Validation (per table, before handing to Ben)

Expected: `resp ∈ {0,1}`; **CH/CN/MT = 45 items, density ≈ 1.0**; **LC ≈ 50 items, density ≈ 0.9**;
~1M ids (slightly fewer for LC). The script prints a QC line per table. Also confirm the retained
item set == `enem_YYYY_main_items.csv` and (spot-check) == the majority-respondent set.

## 7. Known unknowns / cautions
- **Pre-2017 formats:** `reprocess_enem.R` assumes standard position ranges (LC 1–45, CH 46–90,
  CN 91–135, MT 136–180) and column names. Verify against each year's dict/`ITENS_PROVA` before
  trusting output (the existing `irw/data/enem_2013.R` used different ranges). Do a `ENEM_DRY_N`
  run and eyeball the QC line first.
- **2017 & 2020** have ~3 pools (＋Digital); the standard-booklet rule keeps only paper-regular —
  confirm the dict labels Digital booklets so they're excluded.
- **Dict coverage** printed by the identifier; if it warns LOW COVERAGE (<0.2), fall back to the
  majority-respondent split.
- **Storage/quota:** work in `$SCRATCH`; ~9 GB zipped + tens of GB extracted across 13 years.
- Don't run heavy jobs on login nodes — always `srun`/`sbatch`.

## 8. After the runs
Collect `ENEM/output/regular/enem_*_1mil_*.{csv,Rdata}` + QC logs. Freeze each year's
`standard_prova_codes`/`regular_prova_codes` into the committed `irw/data/enem_YYYY.R` (self-contained,
per IRW convention) for the PR. Hand cleaned tables + QC to Ben for Redivis upload/versioning.
