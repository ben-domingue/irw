# ENEM Re-processing run kit

Reprocess all ENEM IRW tables (2013–2025) so each contains ONLY the main
(standard regular-application) items — dropping reaplicação / digital / accessibility
substitutes. Result: clean, fully-dense tables (CH/CN/MT = 45 items, density ≈ 1.0;
LC keeps both languages, ~50 items, density ≈ 0.9 per issue #723).

## Files
- `FARMSHARE_RUNBOOK.md` — **start here**: setup, downloads, per-year pipeline, SLURM, validation, and locked decisions/context.
- `REPROCESS_PLAN.md` — the approved plan (full context).
- `identify_regular_items.py` — derive a year's main-item set + booklet codes from the INEP microdata dictionary.
- `reprocess_enem.R` — year-parameterized reprocessing; auto-detects single vs split microdata layout; validated on 2023 & 2024.

## Quick start (per year, on FarmShare)
```bash
YEAR=2023; DIR=$SCRATCH/enem/extracted_$YEAR/DADOS
DICT=$(ls $SCRATCH/enem/extracted_$YEAR/DICION*/Dicion*_$YEAR.xlsx)
python identify_regular_items.py --itens $DIR/ITENS_PROVA_$YEAR.csv --dict "$DICT" --year $YEAR --out-dir out/regular
ENEM_YEAR=$YEAR ENEM_DATA_DIR=$DIR IRW_ROOT=$PWD ENEM_CODES=out/regular/enem_${YEAR}_prova_codes.csv Rscript reprocess_enem.R
```
See the runbook for details, SLURM wrapper, and per-year caveats.
