# Extraction log: fad_dataset2

## Source used
- Paper: Liu, Q. L., Wang, F., Yan, W., Peng, K., Sui, J., & Hu, C. (2020). "Questionnaire Data From
  the Revision of a Chinese Version of Free Will and Determinism Plus Scale." *Journal of Open
  Psychology Data*, 8(1). DOI: 10.5334/jopd.49.
  (https://openpsychologydata.metajnl.com/articles/10.5334/jopd.49/)
- OSF companion record (linked from the paper and from the dictionary's "URL for data"):
  https://osf.io/t2nsw/ — fetched via the OSF v2 API (`api.osf.io/v2/nodes/t2nsw/files/osfstorage/`)
  since the OSF project page itself is JS-rendered and returns no content to a plain fetch.
- Files downloaded and cached at
  `itemtext/skill_test/sessionB_batch/.cache/fad_dataset2/`:
  - `FADGS_dataset2_clean.csv`, `FADGS_dataset3_clean.csv` — the two raw CSVs the IRW processing
    script (`data/fad_dataset2.R`) row-binds together to build this table.
  - `FADGS_codebook_dataset2&3.xlsx` (saved locally as `FADGS_codebook_dataset2_3.xlsx`) — item-level
    codebook with two sheets (`English_version`, `Chinese_version`), literal item wording, response
    labels, and subscale scoring key.
  - `Readme.txt` — OSF project readme, confirms file/codebook pairing and links the preprint
    (https://psyarxiv.com/7ngey/).
- **Also read `data/fad_dataset2.R` directly** (the actual IRW processing script already in this
  repo, at `/home/ben/Dropbox/projects/irw/src/data/fad_dataset2.R`) — this was essential, see below.

## Bare-integer validation check (has_bare_integer_items = TRUE)
Ground truth: 59 bare-integer items ("1"-"59"), 5 resp values (1-5), N id = 584.

Rather than guessing item order from range-plausibility alone, I read the actual processing script
(`data/fad_dataset2.R`) that produced this table. It:
1. Row-binds `FADGS_dataset2_clean.csv` + `FADGS_dataset3_clean.csv`.
2. Filters to rows where `check == 3 & is.na(recheck)` (valid attention-check responses).
3. Drops demographic/session/attention-check columns (`dataset, session, check, gender, edu, faedu,
   moedu, faoccu, mooccu, native, resession, regender, reedu, reage, recheck`).
4. `pivot_longer()`s everything except `id`/`age`, then assigns `item_id = row_number()` over
   `unique(df$item)` — i.e., the bare integer `item` is just positional order of the remaining wide
   columns, in their original left-to-right CSV order.

I reproduced this transform locally in base R (`.cache/fad_dataset2/build.R` early section) on the
downloaded CSVs and printed the resulting 59-column order. Result, confirmed programmatically:
- **Items 1-27**: session-1 FAD+ items in codebook order — `fd1, sd2, up3, fw4, fd5, sd6, up7, fw8,
  fd9, sd10, up11, fw12, fd13, sd14, up15, fw16, fd17, sd18, up19, up20, fw21, sd22, fw23, sd24, up25,
  fw26, up27` (the "check" column itself is excluded, consistent with the codebook's own item-number
  gap between FW21 and SD22).
- **Items 28-54**: the retest ("re-") administration of the *same* 27 items, same order
  (`refd1...reup27`).
- **Items 55-59**: `du28, du29, du30, du31, du32` — five "Dualism/anti-reduction" items (translated
  from the Free Will Inventory, Nadelhoffer et al. 2014) appended only to the retest wave.
- 27 + 27 + 5 = 59. Exact match.

**Independent cross-check of the row-count structure** (not just column order): I compared per-item
row counts in the ground-truth RDS against my local reconstruction. Items 1-27 have 584 non-NA
responses each (matches N id = 584, i.e. every participant answered every original item); items 28-59
(retest items *and* DU items alike) have exactly 125 non-NA responses each — consistent with only the
125-person retest subsample having both the retest FAD+ items and the DU items, which independently
confirms DU28-32 belongs with the retest wave rather than session 1. This row-count fingerprint check,
not just resp-range plausibility, is what pins down the item ordering.

After building the candidate table on this basis, `unique(item)` and `unique(resp)` were checked
against `.gt_fad_dataset2.rds` directly in R: `item` matched exactly (both length-59 sets identical as
character vectors); `resp` matched in value (1:5 vs 1:5) modulo integer-vs-numeric class, which is not
a real mismatch. **Validation: full pass.**

## Structure discovered
- Original instrument: FAD+ (Free Will and Determinism Plus Scale; Paulhus & Carey, 2011), Chinese
  translation, 27 items across four subscales (Fatalistic Determinism, Scientific Determinism,
  Unpredictability, Free Will) — item numbering in the codebook interleaves subscales in a fixed
  presentation order (FD1, SD2, UP3, FW4, FD5, ...), which the codebook's own labels preserve.
- A 28th slot in the presentation sequence is an attention-check item ("Please choose the option
  'neither agree nor disagree'") — excluded from the live `item`/`resp` data by the processing
  script's `select(-check, -recheck)`, and correctly excluded here too.
- Same 27 items re-administered at retest (items 28-54 here).
- 5 additional items (DU28-32) from a different instrument (Dualism/Anti-Reduction, translated from
  the Free Will Inventory) bundled into the retest wave only.
- Response scale: single instructions line applies to the whole survey (FAD+ items and DU items alike
  — no separate instruction text is given for the DU items in the codebook, only a source citation),
  5-point Likert, "1 = strongly disagree" ... "5 = strongly agree", no reverse-scored items.

## Structure of output
- `instrument`: single string describing both the FAD+ Chinese revision and the appended
  Dualism/Anti-Reduction items, since the table mixes two source instruments (same pattern used for
  `firstborn_personality`, which also merges two instruments in one table).
- `instructions`: one literal line ("For each statement below, choose a number from 1 to 5 to how much
  you agree or disagree."), applied table-wide since it's the only participant-facing instruction
  disclosed and covers both item blocks.
- `section_id`: one section per item (`fad_dataset2_1` ... `fad_dataset2_54`) with blank
  `section_prompt` for the 54 FAD+ items (no shared passage/testlet framing beyond the table-wide
  instructions) — per SKILL.md's "no section prompt" default when there's no real grouping. The 5 DU
  items (55-59) share one section_id (`fad_dataset2_du`) with `section_prompt` set to the codebook's
  citation line ("Dualism/anti-reduction (translated from the Free Will Inventory by Chuan-Peng Hu &
  Qing-Lan Liu, Nadelhoffer et al., 2014)"), since that framing text is specific to just those 5 items,
  not the whole table, and is genuinely shared across all five.
- `item_text`: transcribed verbatim from the codebook's `English_version` sheet (not re-translated
  from Chinese — the paper's own English gloss was used, matching its terseness exactly, one short
  declarative sentence per item as given).
- `correct_response`: blank throughout (opinion/attitude scale, no scoring key).
- `option_text`/`resp`: 1=Strongly disagree, 2=Disagree, 3=Neither agree nor disagree, 4=Agree,
  5=Strongly agree, per the codebook's value-label column, applied identically to every item (uniform
  scale, no reverse-coding per the codebook's "NO REVERSE" note).

## OCR / image-based extraction
Not needed. All source text (paper HTML, OSF-hosted `.xlsx` codebook, `.R` processing script, `.csv`
data files) was machine-readable text/structured data fetched directly — no PDF-image or scanned
content was involved.

## Derived vs. directly-read values
- `item_text`, `option_text`/`resp` labels, and `instructions` text are all directly read (copy-typed)
  from the codebook's `English_version` sheet — nothing paraphrased or invented.
- The **mapping** of bare-integer `item` id -> specific codebook item (which item is "1" vs "28" vs
  "55") is *derived*, not directly read off a label in the source — it required replaying the
  IRW processing script's exact `select()`/`pivot_longer()`/`row_number()` logic against the raw CSV
  column order, since the live table only carries integer item ids. This derivation is deterministic
  (confirmed by reproducing it locally) and cross-checked against the independent row-count fingerprint
  described above, so it is not a guess, but it is worth flagging as inference rather than a literal
  read of an "item 1 = ..." label in the source.
- One verbatim source typo was corrected in transcription: the codebook value label "neith agree nor
  disagree" was transcribed as "Neither agree nor disagree" (obvious typo in the source spreadsheet,
  not a wording choice). `item_text` for du29 was left as-is including the source's own truncation
  ("...biological machin") since that's the literal codebook text.

## Source type used
Raw-data-file column headers (`data/fad_dataset2.R` + `FADGS_dataset2_clean.csv` /
`FADGS_dataset3_clean.csv`) for the item-id mapping, combined with a paper/OSF-supplementary codebook
(`FADGS_codebook_dataset2&3.xlsx`, an Excel appendix disclosed alongside the Journal of Open Psychology
Data paper) for the literal item and response-option text. No PDF manual or website-only codebook was
needed — everything was in machine-readable OSF-hosted files.

## Ambiguities
- Whether the DU28-32 citation line belongs in `section_prompt` (chosen here) vs. folded into a
  composite `instructions` value that varies by section: SKILL.md's rule that item-count/source-
  specific framing text should live in `section_prompt`, not `instructions`, when it's scoped to a
  subset of items, was followed. `firstborn_personality` set a loose precedent for letting
  `instructions` vary by section instead, but that table's two sub-instruments each had genuine
  distinct *participant-facing* instructions; here only one instruction line is disclosed for the
  whole table, so it was kept single and the DU-specific citation was placed in `section_prompt`
  instead.
- The retest items (28-54) are literally identical wording to items 1-27 — this is not an error, it's
  the test-retest design; both must appear as distinct rows since they are distinct `item` ids in the
  live data.

## Items not extracted
None. All 59 ground-truth items were mapped to specific item text and validated exactly against
`irw::irw_fetch("fad_dataset2")` (via the cached ground-truth RDS). No `pending_index_notes.csv` row
was needed for this table — validation passed exactly, no discrepancy to log.
