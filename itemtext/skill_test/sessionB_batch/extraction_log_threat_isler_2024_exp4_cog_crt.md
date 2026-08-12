# Extraction log: threat_isler_2024_exp4_cog_crt

## Source used
Dictionary URL for data (https://osf.io/grafm/) points to the OSF project for Isler,
Yilmaz, Maule & Gächter (2024), *Behavior Research Methods*, 56(8), 8379-8395,
"How to activate threat perceptions in behavior research: A simple technique for
inducing health and resource scarcity threats." The OSF project's data package
(`IYMG_Data_AnalysisFiles.zip`) contains one folder per experiment; `Experiment 4/`
holds `Experiment 4 Qualtrics File.qsf`, `Experiment 4 Materials.pdf`,
`Experiment 4 Data.dta/.xlsx`, and `Analysis codes.do`. `README.pdf` at the zip root
confirms this package belongs to this exact paper/DOI (10.3758/s13428-024-02481-6) and
describes the `.qsf` as the literal Qualtrics survey export.

This resumed a prior run that had already downloaded and unzipped the OSF package into
`.cache/threat_isler_2024_exp4_cog_crt/` (found `IYMG_Data_AnalysisFiles.zip`,
`README.pdf`, and an `unzipped/` tree, including `Experiment 4/pages/page-*.png` —
page-by-page renders of `Experiment 4 Materials.pdf`, apparently prepared for OCR — and
two empty `materials.txt`/`materials2.txt` stub files, presumably where OCR output was
going to be written before the run crashed). Rather than OCR the PNG renders, this run
used `Experiment 4 Qualtrics File.qsf` directly: it is Qualtrics's native JSON survey
export and contains the literal, machine-readable question/option text (`QuestionText`,
`Choices`) with no OCR risk, plus a `DataExportTag` (e.g. `"Q1 CRT1"`) and `Payload`
`Blocks` structure that ties questions to variable names. `Experiment 4 Materials.pdf`
was not needed once the `.qsf` proved sufficient. `pdftotext -layout` on the Materials
PDF returned nothing (print-to-PDF from Qualtrics survey — explains why a prior run had
already switched to page-image renders for OCR) but this was moot; the `.qsf` is the
authoritative source anyway.

## Structure discovered
The `.qsf`'s `SurveyElements` contains a `BL` (blocks) element with a block named `"CRT"`
(block ID with `Description: "CRT"`) holding, in order: `CRT Instructions` (QID1046),
`Q1 CRT1` (QID1048), `Q2 CRT2` (QID1050), `Q3 CRT3` (QID1052) — plus paired hidden
`*_T` timing questions for each. This block order (Q1→Q2→Q3) plus the `DataExportTag`
naming (`CRT1`/`CRT2`/`CRT3`) directly maps onto the ground-truth `item` values
`crt1`/`crt2`/`crt3`.

Two copies of the `Q1 CRT1` question text exist in the `.qsf` (`QuestionID`s `QID1048`
and `QID937`): a "bat and a ball" version and a "pencil and an eraser" version (identical
choice structure, £/pence phrasing). Checked which is actually administered by finding
the block each `QuestionID` belongs to: `QID937` is filed under a block literally named
`"Trash / Unused Questions"`; `QID1048` is filed under the live `"CRT"` block referenced
by the survey flow. So the administered item is the classic "bat and a ball" wording
(`QID1048`), not the "pencil and eraser" variant — confirmed unused, not a condition-
dependent alternate form.

`CRT Instructions` text ("Please try to correctly answer the next three questions.")
applies to all three items in the block, not to any single item, so it went in
`instructions` (table-level), not `section_prompt`. No testlet/shared-passage structure
exists beyond that, so `section_id` is one per item (`<table>_crt1` etc.) with blank
`section_prompt`, per the skill's "no real grouping" convention.

`correct_response`: confirmed against `Analysis codes.do` (also in the OSF package),
which scores `CRT_1_C = (CRT1==1)`, `CRT_2_C = (CRT2==1)`, `CRT_3_C = (CRT3==1)` — i.e.
Qualtrics choice code `1` is the scored-correct answer for all three items. This also
matches the classic Frederick (2005) CRT correct answers ("5 pence"/bat-and-ball,
"5 minutes"/widgets, "47 days"/lily pads), which the `.qsf`'s `Choices` dict places at
code `1` in each case — consistent, not coincidental (whoever built the Qualtrics survey
put the correct answer first in the option list, unlike Frederick's original ordering
which puts the intuitive-but-wrong answer first).

`option_text`/`resp` mapping is the literal Qualtrics `Choices` dict per item (codes
`1`-`4` as strings in the JSON, cast to integer `resp`), which is exactly the ground
truth's `resp` set `{1,2,3,4}`.

## OCR / image-based extraction
None used. A prior/partial run had rendered `Experiment 4 Materials.pdf` to per-page
PNGs (`.cache/.../Experiment 4/pages/page-*.png`), apparently anticipating an OCR pass,
but this run did not need it — item and option text came directly from the machine-
readable `.qsf` JSON export, which is a more reliable literal source than OCR of a
print-to-PDF survey rendering. No image-based transcription was performed or required.

## Derived vs. directly-read values
- `item_text`, `option_text`: directly read (Qualtrics `QuestionText`/`Choices` fields,
  with only inert HTML wrapped around them — e.g. `&nbsp;`, an empty `<div><style>...`
  block hiding the "Previous" button — stripped; no wording changed).
- `instructions`: directly read (`CRT Instructions` question's `QuestionText`).
- `resp`: directly read (Qualtrics numeric choice codes, matching ground truth exactly).
- `correct_response`: derived by cross-referencing two independent sources that agreed —
  (1) `Analysis codes.do`'s scoring logic (`CRT_k_C = (CRTk==1)`), and (2) the standard
  published Frederick (2005) CRT answer key for these three items. Not directly stated
  as a "correct_response" field anywhere in the `.qsf` itself.
- `section_id`: derived (constructed as `<table>_<item>`, one per item; no real
  section/testlet grouping in the source).
- `instrument`: derived label ("Cognitive Reflection Test (3-item CRT; Frederick, 2005)")
  — the paper's own text refers to this simply as "the CRT" / "cognitive reflection
  test"; the parenthetical citation to Frederick (2005) reflects the standard/widely-used
  name for this exact 3-item instrument, not paper-stated boilerplate.

## Source type used
Primary: Qualtrics `.qsf` survey export (machine-readable JSON), from the paper's own
OSF data-and-materials package. Secondary/corroborating: `Analysis codes.do` (Stata
scoring syntax) from the same package, used only to confirm `correct_response`. No PDF
text extraction, no OCR, no reliance on the paper's main-text body (the CRT is described
narratively there but without full item wording).

## has_bare_integer_items
FALSE, as stated in the dictionary row — ground-truth `item` values are already the
semantic codes `crt1`/`crt2`/`crt3`, not bare integers, so no positional reconstruction
was needed; the `.qsf`'s own `DataExportTag` naming (`Q1 CRT1`, `Q2 CRT2`, `Q3 CRT3`)
confirms the crt1/crt2/crt3 → bat-and-ball/widgets/lily-pads mapping directly.

## Items not extracted
None. All 3 ground-truth items (`crt1`, `crt2`, `crt3`) and all 4 ground-truth `resp`
values (`1`-`4`) were extracted and matched exactly against
`readRDS(".gt_threat_isler_2024_exp4_cog_crt.rds")` — validated as an **exact** match,
both `item` and `resp` sets identical, no discrepancy to log in
`pending_index_notes.csv`.
