# Extraction log: eammi_grahe_2018_disability_identity

## Source used
Reused the cached EAMMi2 materials fetched for the sibling table `eammi_grahe_2018_moa1`
(same OSF project, https://osf.io/qtqpb/overview), stored at
`itemtext/.cache/eammi_grahe_2018_moa1/`:

- `EAMMi2-Data1.2-Codebook.xlsx` — the project's own data dictionary (Variable Name /
  Question text / instructions / responses / Survey Question ID), read with `openpyxl`.
- `EAMMI2_Survey_withcodes.txt` — `pdftotext -layout` extraction of the Qualtrics survey
  PDF (`EAMMI2_Survey_withcodes.pdf`), showing the literal matrix-question layout as
  presented to respondents.

Both sources agree exactly and independently confirm the same structure.

## Locating "Question 10"
Ground-truth items are `Q10_1`..`Q10_15` — Qualtrics question-block numbering (the 10th
question block in the survey), not a descriptive prefix like the other EAMMi2 sibling
tables use. Searched the survey text for "Q10" specifically (survey txt, lines 963-1039):

> Q10 If applicable, please rate your degree of agreement with each of the following
> statements.
> Strongly disagree (1) | Disagree (2) | Neither agree nor disagree (3) | Agree (4) |
> Strongly agree (5)

followed by 15 numbered statement rows, (1) through (15), each a matrix-row item on that
same 5-point scale — item text and order below.

The codebook independently confirms this: rows `Q10_1`..`Q10_15` each have "Question
text" = the literal statement, "instructions" column = "If applicable, please rate your
degree of agreement with each of the following statements." (identical for all 15 rows,
i.e. one shared instruction for the block), and "responses" = "1-strongly disagree, 5
strongly agree". The two sources' item order and item count match exactly (15 items,
`Q10_1`..`Q10_15`), and the codebook's `Survey Question ID` field literally encodes
`{"ImportId":"QID10_N"}` for each row, corroborating that "Q10" = Qualtrics question ID
10 = this disability-identity block.

## The 15 items (verbatim, in Q10_1..Q10_15 order)
1. My disability interferes with becoming successful.
2. I don't think of myself as a disabled person.
3. I lack confidence because of my disability.
4. I am proud to be a disabled person.
5. Sometimes I am ashamed to be disabled.
6. Being disabled has not reduced my enjoyment of life.
7. My friendships are limited by my disability.
8. My disability is a source of personal strength.
9. Without my disability I could accomplish more.
10. Having a disability has not been a problem for me.
11. I can live a normal life with my disability.
12. I am a better person because of my disability.
13. My disability is an important part of who I am.
14. I am proud of my disability.
15. My disability enriches my life.

## Structure of output
Single section (`eammi_grahe_2018_disability_identity_1`, blank `section_prompt`) — the
whole Q10 block is one Qualtrics matrix question, no sub-grouping/testlet structure, so
there's nothing to split out beyond the whole-table `instructions`.

`instrument` = "EAMMi2 Disability Identity Items (Q10)". No published/named scale
citation for this specific item set was found in the codebook or survey PDF (unlike
`moa1`, where the project's own variable prefix and codebook both named it "Markers of
Adulthood Scale (MOA)") — this label is descriptive, built from the table name and
Qualtrics block number, not a verbatim instrument title from the source. Flagging this as
an ambiguity below rather than guessing a published scale name (e.g. a Disability
Identity Scale by another author) without source confirmation.

`instructions` = "If applicable, please rate your degree of agreement with each of the
following statements." — literal, identical wording in both the survey PDF and the
codebook's per-row "instructions" column, applies to the whole table, recorded once.

`option_text` — all 5 scale points have literal verbal anchors in the source (unlike
`moa1`'s partially-unlabeled scale): "Strongly disagree" (1), "Disagree" (2), "Neither
agree nor disagree" (3), "Agree" (4), "Strongly agree" (5). Matches the codebook's
"1-strongly disagree, 5 strongly agree" summary and the survey PDF's literal column
headers one-to-one.

`correct_response` left blank for all rows — self-report attitude/identity scale, no
scoring key.

## OCR / image-based extraction
None. The survey PDF (`EAMMI2_Survey_withcodes.pdf`) is a native, text-layer PDF
(Qualtrics print-export), extracted with `pdftotext -layout`, not an image/scan — no OCR
was used or needed. The codebook is a native `.xlsx` file read directly with `openpyxl`.

## Derived vs. directly-read values
`item_text`, `instructions`, and `option_text` are all directly read/transcribed
verbatim from the survey PDF and independently corroborated by the codebook (both
sources give identical wording, so no reconstruction was needed). The only derived
element is `instrument` (see "Structure of output" above — a descriptive label, not a
transcribed title) and the trivial single `section_id` (structural placeholder per the
skill's rule for instruments with no real testlet grouping, not sourced text).

## Source type used
Primary: original data-collector's own OSF-hosted survey instrument PDF
(`EAMMI2_Survey_withcodes.pdf`) and data dictionary (`EAMMi2-Data1.2-Codebook.xlsx`),
both first-party materials from the dataset's own OSF repository (https://osf.io/qtqpb/) —
not the published paper, not a secondary/paraphrased description.
`has_bare_integer_items` is FALSE for this table (items already have semantic labels,
`Q10_1`..`Q10_15`, per the dictionary row), and that held true throughout — no
bare-integer reconstruction/ordering judgment call was needed; the codebook's
`Survey Question ID` field ties each `Q10_N` directly to its literal item text with no
positional guessing required.

## Ambiguities
- No formal/published instrument name for this 15-item disability-identity item set was
  found in either cached source; `instrument` field is a descriptive label built from the
  table/block identifier rather than a verbatim citation. Not logged to
  `pending_index_notes.csv` since it doesn't affect item/resp validation — flagging here
  for a human to confirm/replace if a published scale name is known.

## Items not extracted
None — all 15 ground-truth items (`Q10_1`..`Q10_15`) were extracted with full
`item_text` and `option_text`.

## Validation
`unique(candidate$item)` and `unique(candidate$resp)` match
`readRDS(".gt_eammi_grahe_2018_disability_identity.rds")` exactly (`setequal()` checks
both TRUE, confirmed programmatically in `build_eammi_grahe_2018_disability_identity.R`):
15 items (`Q10_1`..`Q10_15`), resp {1,2,3,4,5}. Exact match, no discrepancy to log in
`pending_index_notes.csv`.
