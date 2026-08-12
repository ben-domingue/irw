# Extraction log: fad_dataset1

## Source used
- Paper: Liu, Q. L., Wang, F., Yan, W., Peng, K., Sui, J., & Hu, C. (2020). "Questionnaire Data From
  the Revision of a Chinese Version of Free Will and Determinism Plus Scale." *Journal of Open
  Psychology Data*, 8(1). DOI: 10.5334/jopd.49.
  (https://openpsychologydata.metajnl.com/articles/10.5334/jopd.49/)
- OSF companion record (same project as `fad_dataset2`, linked from the paper and the dictionary's
  "URL for data"): https://osf.io/t2nsw/ — fetched via `api.osf.io/v2/nodes/t2nsw/files/osfstorage/`,
  descending into the `data_codebook_rcode` subfolder (the top-level listing only shows a license
  icon and one folder).
- Files downloaded and cached at
  `itemtext/skill_test/sessionB_batch/.cache/fad_dataset1/`:
  - `FADGS_dataset1_clean.csv` — raw data file that `data/fad_dataset1.R` reads directly.
  - `FADGS_codebook_dataset1.xlsx` — dataset-1-specific codebook (separate file from dataset2/3's
    codebook), sheets `English_version` / `Chinese_version`, literal item wording, response labels,
    subscale scoring key.
- **Also read `data/fad_dataset1.R` directly** (the actual IRW processing script already in this
  repo, at `/home/ben/Dropbox/projects/irw/src/data/fad_dataset1.R`) — essential for the bare-integer
  mapping, see below.
- Reused the sibling `fad_dataset2` extraction's cached working directory pattern and its already-
  confirmed FAD+ item text/order (`.cache/fad_dataset2/build.R`) as a starting point, since both
  tables share the same 27-item FAD+ instrument — but did **not** blindly copy it without
  independently confirming dataset1's own CSV column order and dataset1's own codebook file (see
  below), since dataset1 is a separate raw file from dataset2/3.

## Bare-integer validation check (has_bare_integer_items = TRUE)
Ground truth: 27 bare-integer items ("1"-"27"), 5 resp values (1-5), N id = 56.

`data/fad_dataset1.R` (unlike `fad_dataset2.R`) is single-file, single-administration: it reads
`FADGS_dataset1_clean.csv`, filters to `check == 3`, drops
`dataset, session, gender, edu, faedu, moedu, faoccu, mooccu, check`, then `pivot_longer()`s every
remaining column except `id`/`age`, assigning `item_id = row_number()` over `unique(df$item)` — i.e.
the bare integer `item` is the positional order of the remaining wide columns in the raw CSV's
original left-to-right order.

`FADGS_dataset1_clean.csv`'s header row is:
`dataset, session, gender, age, edu, faEdu, moEdu, faOccu, moOccu, FD1, SD2, UP3, FW4, FD5, SD6, UP7,
FW8, FD9, SD10, UP11, FW12, FD13, SD14, UP15, FW16, FD17, SD18, UP19, UP20, FW21, check, SD22, FW23,
SD24, UP25, FW26, UP27`

After the script's `select(-dataset,-session,-gender,-edu,-faedu,-moedu,-faoccu,-mooccu,-check)`, the
remaining columns in order are: `age, FD1, SD2, UP3, FW4, FD5, SD6, UP7, FW8, FD9, SD10, UP11, FW12,
FD13, SD14, UP15, FW16, FD17, SD18, UP19, UP20, FW21, SD22, FW23, SD24, UP25, FW26, UP27` — with `age`
excluded from the pivot too, so **item 1 = FD1, item 2 = SD2, ... item 27 = UP27**, exactly 27 items,
identical labels and identical order to the first 27 items of `fad_dataset2` (which I had already
independently confirmed against `data/fad_dataset2.R` + row-count fingerprinting in a prior batch).
No retest wave and no DU items are present in this table (dataset 1 is the single-session
questionnaire-revision sample, distinct from dataset 2/3's test-retest sample).

**Independent cross-check**: every one of the 27 items has exactly 56 non-NA responses in the ground
truth (`table(gt$item)` all equal 56), consistent with `N id = 56` and every participant answering
every item once — no partial/subsample structure to worry about, unlike dataset2's retest split.

After building the candidate table, `unique(item)` and `unique(resp)` were checked in R against
`.gt_fad_dataset1.rds` directly: both matched exactly (27 items "1"-"27", resp 1:5).
**Validation: full pass** (see `## Structure of output` below for the exact R check output).

## Structure discovered
- Instrument: FAD+ (Free Will and Determinism Plus Scale; Paulhus & Carey, 2011), Chinese
  translation, 27 items across four subscales (Fatalistic Determinism, Scientific Determinism,
  Unpredictability, Free Will), same fixed interleaved presentation order as `fad_dataset2`
  (FD1, SD2, UP3, FW4, FD5, ...).
- A 28th slot in the presentation sequence ("check") is the attention-check item ("Please choose the
  option 'neither agree nor disagree'") — excluded from the live data by the script's
  `select(-check)`, correctly excluded here too.
- Single administration only — no retest wave, no Dualism/Anti-Reduction (DU) items in this dataset
  (those only appear in `fad_dataset2`'s retest subsample).
- Response scale: single instructions line for the whole survey, 5-point Likert, "1 = strongly
  disagree" ... "5 = strongly agree" (codebook has the same "Neith agree nor disagree" typo as
  dataset2/3's codebook; corrected to "Neither agree nor disagree" here), no reverse-scored items.

## Structure of output
- `instrument`: "Free Will and Determinism Plus Scale (FAD+; Paulhus & Carey, 2011), Chinese
  revision — Dataset 1" — table-wide, single instrument (no second sub-instrument here, unlike
  `fad_dataset2`).
- `instructions`: "For each statement below, choose a number from 1 to 5 to how much you agree or
  disagree." — transcribed verbatim from the dataset-1 codebook's `Item_content` column (identical
  text to dataset2/3's codebook).
- `section_id`: one section per item (`fad_dataset1_1` ... `fad_dataset1_27`), blank `section_prompt`
  throughout — no testlet/passage grouping beyond the table-wide instructions.
- `item_text`: transcribed verbatim from the dataset-1 codebook's `English_version` sheet, one short
  declarative sentence per item, matching the source's terseness exactly.
- `correct_response`: blank throughout (opinion/attitude scale, no scoring key).
- `option_text`/`resp`: 1=Strongly disagree, 2=Disagree, 3=Neither agree nor disagree, 4=Agree,
  5=Strongly agree, per the codebook's value-label column, applied identically to every item (uniform
  scale, codebook's own "NO REVERSE" note).

R validation output:
```
item match: TRUE
resp match: TRUE
n unique cand item: 27  gt item: 27
```

## OCR / image-based extraction
Not needed. All source text (paper HTML, OSF-hosted `.xlsx` codebook, `.R` processing script, `.csv`
data file) was machine-readable text/structured data fetched directly — no PDF-image or scanned
content was involved.

## Derived vs. directly-read values
- `item_text`, `option_text`/`resp` labels, and `instructions` text are all directly read (copy-typed)
  from `FADGS_codebook_dataset1.xlsx`'s `English_version` sheet — nothing paraphrased or invented.
- The **mapping** of bare-integer `item` id -> specific codebook item (which item is "1" vs "27") is
  *derived*, not directly read off a label in the source — it required replaying `data/fad_dataset1.R`'s
  exact `select()`/`pivot_longer()`/`row_number()` logic against `FADGS_dataset1_clean.csv`'s raw
  column order. This derivation is deterministic and directly readable off the CSV header (no
  ambiguity/inference needed the way dataset2's retest-vs-DU split required, since dataset1 has no
  extra item blocks to disambiguate), and it is additionally cross-checked against dataset2's
  already-confirmed identical item labels/order for the same 27-item FAD+ instrument.
- One verbatim source typo was corrected in transcription: the codebook value label "Neith agree nor
  disagree" was transcribed as "Neither agree nor disagree" (same typo present in both the
  dataset1 and dataset2/3 codebooks, obvious spreadsheet typo, not a wording choice).

## Source type used
Raw-data-file column headers (`data/fad_dataset1.R` + `FADGS_dataset1_clean.csv`) for the item-id
mapping, combined with a paper/OSF-supplementary codebook (`FADGS_codebook_dataset1.xlsx`, an Excel
appendix disclosed alongside the Journal of Open Psychology Data paper, specific to dataset 1) for the
literal item and response-option text. No PDF manual or website-only codebook was needed — everything
was in machine-readable OSF-hosted files.

## Ambiguities
None of note. Dataset1 is a simpler single-administration case than `fad_dataset2` (no retest wave,
no bundled second instrument), and its own dedicated codebook file made the item-id mapping
unambiguous without needing the row-count-fingerprint cross-check that `fad_dataset2` required.

## Items not extracted
None. All 27 ground-truth items were mapped to specific item text and validated exactly against
`irw::irw_fetch("fad_dataset1")` (via the cached ground-truth RDS). No `pending_index_notes.csv` row
was needed for this table — validation passed exactly, no discrepancy to log.
