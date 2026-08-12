# Extraction log: afps_vangsness_2019

## Source used
Same study/OSF project as the already-completed `ips_vangsness_2019` (Vangsness, Voss,
Maddox, Devereaux, Martin, & Nystrom, 2022, *Frontiers in Psychology*, "Self-Report
Measures of Procrastination Exhibit Inconsistent Concurrent Validity, Predictive
Validity, and Psychometric Properties," DOI 10.17605/OSF.IO/R7WCX). Reused the cached
combined OSF survey PDF `.cache/ips_vangsness_2019/procrastinationFullSurvey.pdf`
(exported Qualtrics document, 11 procrastination-scale blocks) and its `pdftotext -layout`
text dump `.cache/ips_vangsness_2019/survey.txt`, plus the same session's
`fullData.csv` and `Procrastination_full.Rmd` for column-order/scoring cross-checks. No
new fetch was performed.

## Structure discovered
`survey.txt`'s `Start of Block:`/`End of Block:` markers (lines 340-457) identify the
relevant block as **"Academic Functional Procrastination Scale"** — confirming AFPS
stands for Academic Functional Procrastination Scale, not "Adult Frustration with
Procrastination Scale" as speculated in the task prompt. The block contains: one shared
instructions paragraph (identical wording to the one used for several other scales in
this survey, e.g. Active Procrastination Scale), 9 real AFPS items, plus one 10th
non-scale item ("I am enrolled in a psychology course currently.") that is NOT part of
the 9-item scale.

`fullData.csv`'s header confirms the mapping: columns run
..., `DR_1`, `AFPS_1`, `AFPS_2`, ..., `AFPS_9`, `BI_1`, `GPS_1`, ... — the 10th block item
("I am enrolled...") exports as the separate `BI_1` column immediately after `AFPS_9`,
the same pattern seen in the IPS block (where the analogous filler/check item exported
as a separate `DR_4` column). This confirms `AFPS_1`..`AFPS_9` correspond 1:1, in
presentation order, to the 9 real scale items in the PDF, excluding the 10th filler item.
This matches ground truth exactly: `item` = `AFPS_1`..`AFPS_9`, `resp` = 1-5.

Unlike IPS, all 9 AFPS items in the source PDF display the identical response key:
"Strongly agree (5) / Somewhat agree (4) / Neither agree nor disagree (3) / Somewhat
disagree (2) / Strongly disagree (1)" — i.e. all 9 items are keyed the same direction, no
per-item reverse-scoring divergence within this scale (checked each item's displayed
numeric key individually in `survey.txt`, not assumed from the first item). Cross-checked
against `fullData.csv` raw values (e.g. row 5: all-5s across `AFPS_1`..`AFPS_9`, consistent
with a uniformly-keyed scale) and `Procrastination_full.Rmd` line 119
(`SRdata$AFPS_comp <- apply(SRdata[,SRkeys$AFPS_comp], MARGIN = 1, mean)` — plain
rowMeans, no reverse-coding step), confirming no additional flip happens downstream of
what's shown in the PDF.

## Structure of output
Single instrument, single instructions paragraph (transcribed literally from the survey
PDF block header — same instructions text also appears verbatim ahead of several other
scales in this multi-instrument survey; recorded once here, scoped to this table only).
One `section_id` per item (`afps_vangsness_2019_AFPS_1` ... `afps_vangsness_2019_AFPS_9`)
with blank `section_prompt` — no testlet/passage grouping, so a trivial per-item
`section_id` was used per the skill's join-key rule. `correct_response` left blank
throughout (procrastination belief scale, no scoring key). `instrument` = "Academic
Functional Procrastination Scale (AFPS)".

## has_bare_integer_items
FALSE, as flagged in the dictionary row — `item` values are already semantic codes
(`AFPS_1`..`AFPS_9`), directly matched against the survey PDF/CSV column names, no
position-based reconstruction from bare integers was needed.

## OCR / image-based extraction
None needed. Reused the same non-scanned, native-text Qualtrics PDF export as
`ips_vangsness_2019` — `pdftotext -layout` had already produced clean, directly-
searchable text for the entire document, including the AFPS block (item stems and
per-item numeric response keys all extracted as selectable text, no OCR required).

## Derived vs. directly-read values
- `item_text` (all 9 items): directly read, verbatim, from `survey.txt` /
  `procrastinationFullSurvey.pdf`, lines 340-457.
- `instructions`: directly read, verbatim, from the same PDF block header.
- `option_text` labels ("Strongly agree", "Somewhat agree", "Neither agree nor disagree",
  "Somewhat disagree", "Strongly disagree"): directly read from the PDF.
- The **assignment of `resp` value to `option_text`** is directly read from the PDF (each
  item shows its own explicit numeric key next to each option; all 9 items in this block
  happened to share the same key, confirmed by checking each item individually rather than
  assuming uniformity from the first item) — cross-checked against `fullData.csv` raw
  values and `Procrastination_full.Rmd`'s unweighted-mean `AFPS_comp` scoring as
  confirmation no additional reverse-coding step happens downstream.
- The **item order / `AFPS_1..AFPS_9` <-> item-position mapping** is derived from
  presentation order in the PDF, cross-checked against `fullData.csv`'s column order
  (Qualtrics export order = presentation order) and confirmed via the `BI_1` filler-item
  column sitting immediately after `AFPS_9`, ruling out the 10th block item ("I am
  enrolled in a psychology course currently.") being miscounted as one of the 9 scale
  items.
- **What AFPS stands for**: derived directly from the PDF's own
  `Start of Block: Academic Functional Procrastination Scale` marker — not assumed from
  the task prompt's speculative "Adult Frustration with Procrastination Scale" guess,
  which was incorrect.

## Source type used
Primary: OSF-hosted Qualtrics survey PDF export (`procrastinationFullSurvey.pdf`), the
same first-party instrument-administration document reused from the `ips_vangsness_2019`
extraction (cached at `.cache/ips_vangsness_2019/`, not refetched). Secondary
cross-check sources: `fullData.csv` (raw response values, column order) and
`Procrastination_full.Rmd` (scoring script, confirms no additional reverse-coding step).
The original published source of the AFPS instrument itself was not tracked down/consulted
(not needed — this study's own administered materials were complete, per Step 3's
guidance to prioritize what was actually administered).

## Ambiguities
The task prompt's guess that AFPS = "Adult Frustration with Procrastination Scale" was
incorrect; the source PDF's block header unambiguously labels it "Academic Functional
Procrastination Scale." No other ambiguity — distinguishing the 10th filler item
("I am enrolled in a psychology course currently.") from the 9 real AFPS items was
resolved unambiguously via the `BI_1` column-naming evidence above, the same pattern
already established for IPS/DR_4.

## Items not extracted
None — all 9 ground-truth items (`AFPS_1`..`AFPS_9`) matched and were extracted with
full item text, instructions, and response-option mapping.

## Validation result
Exact match. `unique(item)` = `AFPS_1`..`AFPS_9` (identical set/order to ground truth);
`unique(resp)` = 1,2,3,4,5 (identical values to ground truth; only a numeric/integer
storage-mode difference, no value mismatch).
