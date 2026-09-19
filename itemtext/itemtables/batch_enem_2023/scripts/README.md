# ENEM 2023 item-text build scripts

How `../enem_2023_1mil_{ch,cn,lc,mt}__items.csv` were produced, kept so the
batch can be re-derived rather than trusted. Nothing here runs automatically;
the `enem*` tables are a standing exclusion in the item-text skill (see
`SKILL.md`) precisely because this path is hand-built.

## Order

| script | does |
|---|---|
| `01_pdf_sourced_2023.py` | the four items the accessibility booklet replaces with other items (54804, 78578, 81742, 125902), transcribed from the standard AZUL PDF, plus a replacement description for the one figure INEP declined to describe (60332) |
| `02_parse_dosvox_2023.py` | parses the four DOSVOX screen-reader plain-text files into item stems and options, keyed on the file's own `QUESTÃO` position |
| `03_join_2023.py` | joins position → `CO_ITEM` via `ITENS_PROVA_2023.csv` at the regular LARANJA booklet, attaches `TX_GABARITO` as `correct_response`, emits the four `__items.csv` |
| `04_validate.sbatch` | the original item/resp-set gate run, against the PRE-#1942 response CSVs |
| `05_audit.sbatch`, `05_log_discrepancies.py` | batch audit and the discrepancy rows for `pending_index_notes.csv` |
| `06_lc_counts.sbatch` | LC elective-block row counts (the 422,321 / 577,679 split) |
| `08_validate_corrected.sbatch` | re-run of the gate against the #1942-CORRECTED tables; this is the one that counts |
| `09_audit_batch.sbatch` | generates `../audit_report.csv` |

`03` was edited after it ran, on review (#1848): it now emits `resp_raw` (not
`raw_resp`) and blanks `option_text` / `option_text_translated` for 78578 and
125902, whose printed options carry no text. The committed `__items.csv` had the
same two changes, and the drop of annulled item 14887, applied directly, so this
edited `03` has not itself been re-run.

`04` is kept alongside `08` on purpose: it is the record of what was actually
run before #1942 landed, and its log names the pre-fix CSV paths.

## Why sbatch and not a plain shell

`read.csv` on a 45M-row / ~1.4GB response CSV needs tens of GB, so the
validation and audit steps run under Slurm at 64–96G. Both read local CSVs via
`--resp-csv` / `--resp-dir` rather than Redivis: there is no API token on this
machine, and the account's 200GB/30-day export quota was exhausted once
already (2026-08-18).

## Paths

The paths are absolute and specific to Stanford FarmShare — `$HOME/enem/` for
the extracted microdata, `/scratch/users/<user>/fix1942_run/work/2023/` for the
corrected response CSVs. They are left as they ran rather than parameterised,
so the log lines and these scripts agree.
