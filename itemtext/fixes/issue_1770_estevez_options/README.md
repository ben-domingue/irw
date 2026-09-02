# #1770 — verifying the two skip verdicts of the 2026-08-29 batch

The first live run of item text at processing time (Step 3.5) skipped 24 tables
on two factual claims about their source `.sav` files. Neither claim had been
checked. This directory holds the check and what came out of it.

`verify_labels.py` reopens both files, confirms each against its Zenodo md5,
and dumps `meta.column_names_to_labels` and `meta.variable_value_labels`.

## Result

| | claim | verdict |
|---|---|---|
| `chen_2024_fitness_coach_creativity` (16 tables) | "no value labels and only one stray variable label (`TS1`)" | **skip stands** — zero value labels on any of the 99 columns, and the one variable label on a shipped item column (`TS1`) is a truncated construct name, not a stem. Two details wrong: five variable labels, not one (`TS1` + the four covariates, which carry the questionnaire's own numbered questions), and `TS1`'s reads `thrillseeking 需求刺激，se`. |
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

**Not uploaded — decided 2026-09-01 on #1770, and #1770 is closed.**
Option-only item text does *not* ship where the stems exist and are one hop
away. The case against, item by item: 77 of the 82 items get
`TOTALMENTE FALSO … TOTALMENTE CIERTO`, a generic agreement scale an analyst
already infers from `resp ∈ 1..5`; `Tiemp.deb` gets usable bin edges but not
its referent, because "time spent on *what*" comes from the table name and the
deposit description, not from any row we would ship; `EDE5` gets direction and
frame with no referent. So 1 item of 82 gains something, 0 gain their question,
and 8 tables would enter the corpus figures as "has item text" — the very
denominator #1709 corrected.

This is the opposite of the forced-choice case (`alsuhibani_2022_npi_s3`,
`aguirre_camacho_2021_shai`), where blank `item_text` is correct because no
stem exists anywhere. Here the stem exists; it is in the paper's appendix.

The 418 gated rows stay here as raw material — the right half of a complete
instrument. A later pass that lifts the stems from that appendix gets
`item_text` + `option_text` together and can merge without redoing this.
