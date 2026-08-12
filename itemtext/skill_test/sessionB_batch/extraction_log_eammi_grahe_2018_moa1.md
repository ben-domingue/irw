# Extraction log: eammi_grahe_2018_moa1

## Source used
Went to the EAMMi2 OSF project itself (https://osf.io/qtqpb/overview, plus the parent
project https://osf.io/te54b/ and its "Materials" component https://osf.io/zuv2c/, found
via the OSF v2 API `https://api.osf.io/v2/nodes/<id>/files/osfstorage/` since the OSF web
UI is JS-rendered and returns no content to WebFetch). Two files, fetched via their
`links.download` URLs and cached under `.cache/eammi_grahe_2018_moa1/`:

- `EAMMi2-Data1.2-Codebook.xlsx` — the project's own data dictionary (Variable Name /
  Question text / instructions / responses / Survey Question ID), read with `readxl`.
- `EAMMI2_Survey_withcodes.pdf` — the actual Qualtrics survey instrument PDF with QIDs,
  converted to text with `pdftotext -layout` (`EAMMI2_Survey_withcodes.txt`, same
  directory). This is the primary source for `item_text` and `option_text` below — it
  shows the literal matrix-question layout as presented to respondents, not just the
  codebook's paraphrase.

Both sources agree exactly and independently confirm the same structure, so this is a
high-confidence, literally-sourced extraction, not a reconstruction.

## Structure discovered: what "moa1#1" vs "moa1#2" are
The survey PDF (`EAMMI2_Survey_withcodes.txt`, lines 45-87) shows `moa1` is a single
Qualtrics matrix question with the same 10 "markers of adulthood" milestone items rated
on **two different response scales side by side**:

- **`moa1#1_*` = Importance rating** — "Please consider ... the degree this is an
  important milestone in achieving adulthood" — 4-point scale: 1=not, 2=slightly,
  3=quite, 4=very (matches ground truth resp {1,2,3,4} for these 10 items exactly).
- **`moa1#2_*` = Achievement rating** — "... the degree to which you have achieved this
  milestone in your lifetime" — 3-point scale: 1=not, 2=somewhat, 3=yes (matches ground
  truth resp {1,2,3} for these 10 items exactly).

So `#1`/`#2` are not two administrations or two subscales with different content — they
are the same 10 milestone items rated twice, once for importance and once for
achievement, sharing one combined `instructions` block. (There is also a parallel
`moa2#1`/`moa2#2` block, a different 10-item set, immediately following in the same
survey — not part of this table, not extracted.)

## The 10 items (identical wording under both `#1` and `#2`)
1. Financially independent
2. No longer living in parents' household
3. Finished with education
4. Married
5. Have at least one child
6. Settled into a long-term career
7. Avoid becoming drunk
8. Avoid illegal drugs
9. Use contraception if sexually active and not trying to conceive a child
10. Committed to long-term love relationship

## Structure of output
`instrument` = "Markers of Adulthood Scale (MOA)" (project's own scale name; matches the
`moa1` variable prefix). `instructions` (literal, from both codebook and survey PDF,
identical wording in both sources): "Please consider each of the following. Please
consider both the degree this is an important milestone in achieving adulthood and the
degree to which you have achieved this milestone in your lifetime." — applies to the
whole table (both `#1` and `#2` items), so recorded once in `instructions`, not
duplicated into `section_prompt`.

Two sections, distinguished only by which of the two literal column headers in the
survey matrix applies:
- `eammi_grahe_2018_moa1_imp` (the 10 `moa1#1_*` items) — `section_prompt` = "Importance"
  (literal column header).
- `eammi_grahe_2018_moa1_ach` (the 10 `moa1#2_*` items) — `section_prompt` = "Achievement"
  (literal column header).

`option_text` for the 4-point importance scale: not / slightly / quite / very (literal
anchor labels from the survey PDF, e.g. "not (1)", "slightly (2)", "quite (3)", "very
(4)"). `option_text` for the 3-point achievement scale: not / somewhat / yes (literal
anchor labels, "not (1)", "somewhat (2)", "yes (3)").

`correct_response` left blank for all rows — this is a self-report attitude/experience
scale with no scoring key.

## OCR / image-based extraction
None. The survey PDF (`EAMMI2_Survey_withcodes.pdf`) is a native, text-layer PDF
(Qualtrics print-export), extracted with `pdftotext -layout`, not an image/scan — no OCR
was used or needed. The codebook is a native `.xlsx` file read directly with `readxl`.

## Derived vs. directly-read values
Nothing in this table is derived/reconstructed. `item_text`, `option_text`, and
`instructions` are all transcribed verbatim from the survey PDF's matrix-question layout
and independently corroborated by the codebook's paraphrase of the same content
(codebook's "responses" column literally reads "1 -not important, 4 important" for `#1`
items and "1 - no, 2 - somewhat, 3- yes" for `#2` items, matching the PDF's anchor labels
one-to-one). `section_id`/`section_prompt` are a light structural choice (splitting the
one Qualtrics matrix question into two sections by rating dimension) but the label text
itself ("Importance"/"Achievement") is copied verbatim from the survey PDF's column
headers, not invented.

## Source type used
Primary: original data-collector's own OSF-hosted survey instrument PDF
(`EAMMI2_Survey_withcodes.pdf`) and data dictionary (`EAMMi2-Data1.2-Codebook.xlsx`),
both first-party materials from the dataset's own OSF repository — not the published
paper, not a secondary/paraphrased description. `has_bare_integer_items` is FALSE for
this table (items already have semantic labels, e.g. `moa1#1_1`), and that held true
throughout — no bare-integer reconstruction/ordering judgment call was needed.

## Items not extracted
None — all 20 ground-truth items (`moa1#1_1`..`moa1#1_10`, `moa1#2_1`..`moa1#2_10`) were
extracted with full `item_text` and `option_text`, and `correct_response` intentionally
blank (no scoring key exists for this instrument).

## Validation
`unique(candidate$item)` and `unique(candidate$resp)` (per-item: `#1_*` items resp
{1,2,3,4}, `#2_*` items resp {1,2,3}; combined table-level resp {1,2,3,4}) match
`readRDS(".gt_eammi_grahe_2018_moa1.rds")` exactly — confirmed programmatically
(`setequal()` checks both TRUE) in `build_eammi_grahe_2018_moa1.R`, and the `item` column
was round-tripped through `saveRDS`/`readRDS` to confirm the literal `#` character
survives (`moa1#1_1`, etc. — confirmed present in the saved `.rds`).
