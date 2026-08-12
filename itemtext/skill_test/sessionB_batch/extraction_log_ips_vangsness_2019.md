# Extraction log: ips_vangsness_2019

## Source used
Dictionary row's URL for data (`https://osf.io/r7wcx/`) is the paper's own OSF project
(Vangsness, Voss, Maddox, Devereaux, Martin, & Nystrom, 2022, *Frontiers in Psychology*,
"Self-Report Measures of Procrastination Exhibit Inconsistent Concurrent Validity,
Predictive Validity, and Psychometric Properties," DOI 10.17605/OSF.IO/R7WCX). The paper
itself is open access (Frontiers; also on PMC, PMC8907120) but only quotes a single
example IPS item ("At the end of the day, I know I could have spent the time better.")
and references the OSF page for the full survey instrument. Listed the OSF project's
files via the OSF v2 API (`https://api.osf.io/v2/nodes/r7wcx/files/osfstorage/`) and
found `procrastinationFullSurvey.pdf` — the exported Qualtrics survey instrument,
including every block administered in the study (11 procrastination scales total, IPS
among them). Downloaded and cached at
`.cache/ips_vangsness_2019/procrastinationFullSurvey.pdf`, converted to text with
`pdftotext -layout` (`.cache/ips_vangsness_2019/survey.txt`) for searching. Also
downloaded `fullData.csv` (`.cache/ips_vangsness_2019/fullData.csv`) and the analysis
script `Procrastination_10-23-21-full.Rmd`
(`.cache/ips_vangsness_2019/Procrastination_full.Rmd`) to confirm the `IPS_1`..`IPS_9`
column-to-item-position mapping.

## Structure discovered
The survey PDF's "Irrational Procrastination Scale" block (pages 44-48 of the exported
Qualtrics document) contains: one shared instructions paragraph, 9 real IPS items (Steel,
2010) each on a 5-point Likert response set, plus one attention-check item ("Please
select 'neither agree nor disagree' when responding to this item.") that is NOT part of
the 9-item scale. `fullData.csv`'s header confirms this: columns run
..., `BI_2`, `IPS_1`, `IPS_2`, ..., `IPS_9`, `DR_4`, `PPS_1`, ... — the attention check is
exported as a separate `DR_4` column, immediately after `IPS_9` and before the next
scale's block, confirming `IPS_1`..`IPS_9` correspond 1:1, in order, to the 9 real IPS
items as presented in the PDF (excluding the attention check). This matches ground truth
exactly: `item` = `IPS_1`..`IPS_9`, `resp` = 1-5.

Each IPS item is independently keyed in the source survey — some items show
"Strongly agree (5) ... Strongly disagree (1)" (straight-keyed: higher score = more
procrastination) and others show "Strongly agree (1) ... Strongly disagree (5)"
(reverse-keyed items, e.g. "I spend my time wisely."). The `Procrastination_full.Rmd`
script computes `IPS_comp` as a plain rowMeans of `IPS_1`..`IPS_9` with no reverse-coding
step, confirming the reverse-keyed items were already recoded to the procrastination-
consistent direction at the Qualtrics/export stage — i.e. the `resp` value in the live
IRW data already reflects each item's per-item coding as literally shown in the survey
PDF choice options, not a single scale-position number applied uniformly across items.
`option_text` was mapped per item according to that item's own displayed
agree->disagree/disagree->agree numeric key, not a single canonical 1=disagree..5=agree
key applied to every item.

Straight-keyed items (5=Strongly agree ... 1=Strongly disagree): IPS_1, IPS_3, IPS_4,
IPS_5, IPS_7, IPS_8.
Reverse-keyed items (1=Strongly agree ... 5=Strongly disagree): IPS_2, IPS_6, IPS_9.

## Structure of output
Single instrument, single instructions paragraph (transcribed literally from the survey
PDF block header), one `section_id` per item (`ips_vangsness_2019_IPS_1` ...
`ips_vangsness_2019_IPS_9`) with blank `section_prompt` — no testlet/passage grouping in
this instrument, so a trivial per-item section_id was used per the skill's join-key rule
rather than omitting the column. `correct_response` left blank throughout (procrastination
attitude scale, no scoring key). `instrument` = "Irrational Procrastination Scale (IPS;
Steel, 2010)".

## has_bare_integer_items
FALSE, as flagged in the dictionary row — `item` values are already semantic codes
(`IPS_1`..`IPS_9`), directly matched against the survey PDF/CSV column names rather than
needing position-based reconstruction from bare integers.

## OCR / image-based extraction
None needed. `procrastinationFullSurvey.pdf` is a native (non-scanned) Qualtrics PDF
export — `pdftotext -layout` produced clean, directly-searchable text for the entire IPS
block (item stems, response-option labels, and per-item numeric keys all extracted as
selectable text, no OCR required).

## Derived vs. directly-read values
- `item_text` (all 9 items): directly read, verbatim, from `survey.txt` /
  `procrastinationFullSurvey.pdf`.
- `instructions`: directly read, verbatim, from the same PDF block header.
- `option_text` labels ("Strongly agree", "Somewhat agree", "Neither agree nor disagree",
  "Somewhat disagree", "Strongly disagree"): directly read from the PDF.
- The **assignment of `resp` value to `option_text` per item** (straight- vs.
  reverse-keyed) is directly read per item from the PDF (each item shows its own explicit
  numeric key next to each option), not derived/assumed — confirmed against `fullData.csv`
  raw values and the analysis script's unweighted-mean scoring (see above) as a
  cross-check that no additional reverse-coding step happens downstream.
- The **item order / `IPS_1..IPS_9` <-> item-position mapping** is derived from
  presentation order in the PDF, cross-checked against `fullData.csv`'s column order
  (which mirrors Qualtrics export order = presentation order) and confirmed via the
  `DR_4` attention-check column sitting immediately after `IPS_9`, ruling out the
  attention-check item being miscounted as one of the 9.

## Source type used
Primary: OSF-hosted Qualtrics survey PDF export (`procrastinationFullSurvey.pdf`), a
first-party instrument-administration document from the study's own OSF repository —
not the published Steel (2010) IPS source paper (not consulted; not needed since this
study's own materials were complete and it's standard practice per Step 3 to prioritize
what was actually administered over the original scale source). Secondary
cross-check sources: `fullData.csv` (raw response values, column order) and
`Procrastination_10-23-21-full.Rmd` (scoring script, confirms no additional reverse-coding
step).

## Ambiguities
None of substance. The only judgment call was distinguishing the attention-check item
from the 9 real IPS items, resolved unambiguously via the `DR_4` column-naming evidence
above.

## Items not extracted
None — all 9 ground-truth items (`IPS_1`..`IPS_9`) matched and were extracted with full
item text, instructions, and per-item response-option mapping; validated exact item/resp
set match against the cached ground truth (`unique(item)` = `IPS_1`..`IPS_9`; `unique(resp)`
= 1-5).
