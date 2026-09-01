# #1770 — verifying the two skip verdicts of the 2026-08-29 batch

The first live run of item text at processing time (Step 3.5) skipped 24 tables
on two factual claims about their source `.sav` files. Neither claim had been
checked. This directory holds the check and what came out of it.

`verify_labels.py` reopens both files, confirms each against its Zenodo md5,
and dumps `meta.column_names_to_labels` and `meta.variable_value_labels`.

## Result

| | claim | verdict |
|---|---|---|
| `chen_2024_fitness_coach_creativity` (16 tables) | "no value labels and only one stray variable label (`TS1`)" | **skip stands** — no shipped item has either kind of label. Two details wrong: five variable labels, not one (`TS1` + the four covariates, which carry the questionnaire's own numbered questions), and `TS1`'s reads `thrillseeking 需求刺激，se`. |
| `estevez_2021_homework_motivation` (8 tables) | "no variable labels and no value labels for any item … only the four Z-score columns carry any label at all" | **overturned on the value-label half.** 86 of 99 columns carry value labels, including **all 82 shipped items**. Variable labels: two, not four, and both on Z-score columns — so the *stems* are genuinely absent and remain in the paper's instrument appendix. |

Also corrected in the `estevez` script header from the same dump: the study
covers **13** schools, not 7 (`CENTRO` runs 1–13, all observed), and `GENERO`,
`CURSO` and every `CENTRO` code are named by the file's own value labels — the
header had said the deposit does not say which gender code is which.

## What is here

`build_items.py` writes one `<table>__items.csv` per estevez table: the value
labels as `option_text`, `item_text` blank (the stems are a second hop, into
the paper), `section_id = <table>_1`. 77 items share one 1–5 anchor set
(TOTALMENTE FALSO … TOTALMENTE CIERTO); the five homework-block items carry
item-specific sets, which independently corroborate the structural inference
the script header flagged about `Cantid.deb` / `Tiemp.deb` / `Aprov.tiem.deb`.

Gates, run 2026-09-01 against the regenerated response CSVs:

- `normalize_nulls.R` — 8/8 normalized
- `validate_items.R --resp-csv` — **8/8 PASS**, item sets and resp sets match exactly
- `audit_batch.R --resp-dir` — 8 WARN, all of them `100% of rows have blank item_text`

**Not uploaded.** Shipping `option_text` with no `item_text` where the stems
exist but are one hop away is a precedent call, not a mechanical one — it is
the open question on #1770. The CSVs here are gated and ready if the answer is
yes; a later pass with the paper in hand can fill `item_text` and re-merge.
