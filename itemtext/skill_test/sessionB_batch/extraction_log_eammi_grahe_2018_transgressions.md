# Extraction log: eammi_grahe_2018_transgressions

## Source used
Reused the cached EAMMi2 materials already fetched for the sibling table
`eammi_grahe_2018_moa1` (`itemtext/.cache/eammi_grahe_2018_moa1/`), no refetch needed:

- `EAMMI2_Survey_withcodes.pdf` / `.txt` — the Qualtrics survey instrument PDF with QIDs,
  extracted via `pdftotext -layout`. This is the primary source: it contains the literal
  matrix-question layout, including the "transgres" block at line 825 of the `.txt`.
- `EAMMi2-Data1.2-Codebook.xlsx` — the project's own data dictionary, read with `readxl`.
  Rows 203-206 (`Variable Name` = `transgres_1`..`transgres_4`) independently confirm the
  same item wording, question text, and response coding.

Both sources agree exactly, so this is a high-confidence, literally-sourced extraction.

## What "transgres" measures
Not a forgiveness/willingness-to-forgive scale (initial guess in the task brief was
wrong) — it's an **interpersonal transgressions frequency scale**: how often, in the
past two weeks, other people have done four specific negative things *to* the
respondent. It's the mirror-image counterpart to an earlier `freq`/`common` block in the
same survey (lines 754-773 of the `.txt`) which asks about someone getting upset *at*
the respondent — but `transgres_1`..`4` is its own distinct matrix question (survey PDF
line 825, codebook rows 203-206), not part of that other block.

Survey PDF text (line 825, `EAMMI2_Survey_withcodes.txt`):
> "How often has it occurred that in the last 2 weeks (14 days) that someone has done
> the following to YOU."
> not at all (1) / very rarely (2) / occasionally (3) / sometimes (4) / rather often (5)
> / quite often (6) / constantly (7)
> - lied to you (1)
> - spread rumors or gossiped about you (2)
> - got even with you for something that happened previously (3)
> - degraded you in public (4)

Codebook (rows 203-206) independently confirms: `Variable Name` = `transgres_1`..
`transgres_4`, `Question text` = "How often has it occurred that in the last 2 weeks (14
days) that someone has done the following to YOU." (identical for all four rows, with
the item-specific stem in the `...3` column: "lied to you", "spread rumors or gossiped
about you", "got even with you for something that happened previously", "degraded you
in public"), `responses` = "1-not at all, 7 constantly" for all four, `Survey Question
ID` = `QID51_1`..`QID51_4`.

## Structure of output
- `instrument` = "EAMMi2 Interpersonal Transgressions Scale" (descriptive label; the
  project's codebook/PDF don't give this 4-item matrix question a standalone named
  scale title beyond the `transgres` variable-name prefix, so this is a constructed
  label from the variable prefix + content, not a literal instrument title found in the
  source — flagged here since it's the one non-literal field).
- `instructions` = the literal matrix-question stem quoted above, applies to all 4
  items and both response-scale ends, so recorded once in `instructions`.
- Single trivial `section_id` (`eammi_grahe_2018_transgressions_1`) with blank
  `section_prompt` — no testlet/passage grouping beyond the shared instructions already
  captured above.
- `item_text` for each of the 4 items is the literal stem transcribed above.
- `option_text` for the 7-point scale: not at all / very rarely / occasionally /
  sometimes / rather often / quite often / constantly (literal anchor labels, matching
  resp 1-7 in ascending order per both the PDF and codebook's "1-not at all, 7
  constantly" scoring statement).
- `correct_response` left blank for all rows — self-report frequency scale, no scoring
  key.

## has_bare_integer_items
FALSE, confirmed. Ground-truth `item` values are already semantic codes
(`transgres_1`..`transgres_4`), directly matched to the codebook's `Variable Name`
column and the PDF's numbered sub-items — no positional/bare-integer reconstruction
judgment call was needed.

## OCR / image-based extraction
None. Both source files are native/text-layer (Qualtrics print-export PDF and a native
`.xlsx`), extracted with `pdftotext -layout` and `readxl` respectively — no OCR used or
needed.

## Derived vs. directly-read values
Everything except the `instrument` label is transcribed verbatim from the survey PDF and
independently corroborated by the codebook. The `instrument` field ("EAMMi2
Interpersonal Transgressions Scale") is a constructed descriptive label, not a literal
title found in either source — noted above.

## Source type used
Primary: original data-collector's own OSF-hosted survey instrument PDF
(`EAMMI2_Survey_withcodes.pdf`) and data dictionary (`EAMMi2-Data1.2-Codebook.xlsx`),
both first-party materials from the dataset's own OSF repository (reused from the
`eammi_grahe_2018_moa1` cache, same OSF project) — not the published paper, not a
secondary/paraphrased description.

## Validation
`unique(candidate$item)` == `{transgres_1, transgres_2, transgres_3, transgres_4}` and
`unique(candidate$resp)` == `{1,2,3,4,5,6,7}`, both matching
`.gt_eammi_grahe_2018_transgressions.rds` exactly (`setequal()` checks both TRUE,
confirmed programmatically). **Exact match** — no discrepancies to log in
`pending_index_notes.csv`.
