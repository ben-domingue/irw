# Extraction log: aip_vangsness_2019

## Source used
Dictionary row's URL for data (`https://osf.io/r7wcx/`) is the same OSF project used for
`ips_vangsness_2019` and `afps_vangsness_2019` (Vangsness, Voss, Maddox, Devereaux,
Martin, & Nystrom, 2022, *Frontiers in Psychology*, "Self-Report Measures of
Procrastination Exhibit Inconsistent Concurrent Validity, Predictive Validity, and
Psychometric Properties," DOI 10.17605/OSF.IO/R7WCX). Reused the materials already
cached for `ips_vangsness_2019` at `.cache/ips_vangsness_2019/` rather than refetching:
`procrastinationFullSurvey.pdf` (exported Qualtrics survey instrument, all 11
procrastination scales in the study), its `pdftotext -layout` conversion `survey.txt`,
`fullData.csv` (raw response data), and `Procrastination_full.Rmd` (scoring script) — no
new downloads were needed.

## Instrument name — discrepancy from the task brief
The task brief described `AIP` as "Aitken Procrastination Inventory." The survey PDF's
own block header (line 635 of `survey.txt`, `Start of Block: Adult Inventory of
Procrastination`) and the paper's own scale list (`survey.txt` line 14, "Standard: Adult
Inventory of Procrastination (13 Questions)") both literally label this instrument
**"Adult Inventory of Procrastination"** (McCown & Johnson, 1989) — not "Aitken
Procrastination Inventory." This is a well-known, commonly-cited procrastination scale
under that name. No occurrence of "Aitken" appears anywhere in the cached survey text or
`Procrastination_full.Rmd`. Used the source's own literal name: `instrument` =
"Adult Inventory of Procrastination (AIP; McCown & Johnson, 1989)".

## Structure discovered
The survey PDF's "Adult Inventory of Procrastination" block (`survey.txt` lines 635-753,
PDF pages 25-28) contains: one shared instructions paragraph (identical wording to the
IPS/AFPS blocks — this appears to be boilerplate framing text repeated ahead of every
procrastination-scale block in this Qualtrics survey), 10 distinct item stems each on a
5-point Likert response set, one exact repeat of the first item stem ("I often think that
'I don't get things done on time.'"), and one attention-check item ("Please select
'strongly agree' when responding to this item.") that is NOT part of the scored scale.

`fullData.csv`'s header confirms the column run `AIP_1` .. `AIP_11`, immediately followed
by `DR_2` (the attention check, exported as a separate column) before the next scale's
block — the same pattern used to disambiguate `IPS_1`..`IPS_9` from its own attention
check in the `ips_vangsness_2019` extraction. This confirms `AIP_1`..`AIP_11` map, in
presentation order, to the 11 non-attention-check items shown in the block — including
the literal repeat of item 1's wording as `AIP_11`. `Procrastination_full.Rmd` line 109
lists `SRkeys$AIP_comp` as exactly `AIP_1`..`AIP_11` (11 keys), and line 121 computes
`AIP_comp` as a plain `rowMeans`-style `apply(..., mean)` over those 11 columns with no
reverse-coding step — matching ground truth exactly: `item` = `AIP_1`..`AIP_11`, `resp` =
1-5.

As with `ips_vangsness_2019`, each AIP item is individually keyed in the source survey:
some show "Strongly agree (5) ... Strongly disagree (1)" (straight-keyed) and others show
"Strongly agree (1) ... Strongly disagree (5)" (reverse-keyed). Since the scoring script
applies no separate reverse-coding step, the `resp` values in the live IRW data already
reflect each item's own displayed numeric key, so `option_text` was mapped per item
according to that item's own displayed key rather than one canonical direction applied to
every item.

Straight-keyed items (5=Strongly agree ... 1=Strongly disagree): AIP_1, AIP_2, AIP_3,
AIP_5, AIP_6, AIP_8, AIP_11.
Reverse-keyed items (1=Strongly agree ... 5=Strongly disagree): AIP_4, AIP_7, AIP_9,
AIP_10.

## Structure of output
Single instrument, single instructions paragraph (transcribed literally, identical to the
`ips_vangsness_2019` instructions text since both blocks share the same header wording in
the source PDF). One `section_id` per item (`aip_vangsness_2019_AIP_1` ...
`aip_vangsness_2019_AIP_11`) with blank `section_prompt` — no testlet/passage grouping in
this instrument. `correct_response` left blank throughout (procrastination attitude
scale, no scoring key).

## has_bare_integer_items
FALSE, as flagged in the dictionary row — `item` values are already semantic codes
(`AIP_1`..`AIP_11`), directly matched against the survey PDF/CSV column names rather than
needing position-based reconstruction from bare integers.

## OCR / image-based extraction
None needed. `procrastinationFullSurvey.pdf` is a native (non-scanned) Qualtrics PDF
export — `pdftotext -layout` produced clean, directly-searchable text for the entire AIP
block (item stems, response-option labels, and per-item numeric keys all extracted as
selectable text, no OCR required). Re-verified the block directly against the PDF
(`pdftotext -f 27 -l 29 -layout`) to confirm the literal repeat of item 1's wording as
item 11 was a genuine feature of the source document, not a text-extraction artifact.

## Derived vs. directly-read values
- `item_text` (all 11 items, including the literal repeat at `AIP_11`): directly read,
  verbatim, from `survey.txt` / `procrastinationFullSurvey.pdf`.
- `instructions`: directly read, verbatim, from the same PDF block header (shared wording
  across procrastination-scale blocks in this survey).
- `option_text` labels: directly read from the PDF.
- The **assignment of `resp` value to `option_text` per item** (straight- vs.
  reverse-keyed) is directly read per item from the PDF (each item shows its own explicit
  numeric key next to each option), cross-checked against `Procrastination_full.Rmd`'s
  unweighted-mean `AIP_comp` scoring (no additional reverse-coding step downstream).
- The **item order / `AIP_1..AIP_11` <-> item-position mapping**, including the repeat at
  position 11, is derived from presentation order in the PDF, cross-checked against
  `fullData.csv`'s column order and the `DR_2` attention-check column sitting immediately
  after `AIP_11`.

## Source type used
Primary: OSF-hosted Qualtrics survey PDF export (`procrastinationFullSurvey.pdf`), the
same first-party instrument-administration document already cached for
`ips_vangsness_2019` — not the original McCown & Johnson (1989) AIP source paper (not
consulted; not needed since this study's own materials were complete). Secondary
cross-check sources: `fullData.csv` (raw column order) and `Procrastination_full.Rmd`
(scoring script, confirms 11-item unweighted mean, no reverse-coding step).

## Ambiguities
The one judgment call was the literal repeat of item 1's wording as item 11. Resolved
unambiguously: `fullData.csv` and `Procrastination_full.Rmd` both treat `AIP_11` as a real
scored column (part of the `AIP_comp` mean), distinct from the block's actual attention
check (`DR_2`, which follows `AIP_11` and is excluded from scoring) — so `AIP_11` was
extracted with the same item text as `AIP_1`, rather than being treated as an
attention-check row itself. This literal duplication appears to be a genuine feature of
the source instrument as administered in this study (possibly an internal-consistency
repeat), not a transcription error.

## Items not extracted
None — all 11 ground-truth items (`AIP_1`..`AIP_11`) matched and were extracted with full
item text, instructions, and per-item response-option mapping; validated exact item/resp
set match against the cached ground truth (`unique(item)` = `AIP_1`..`AIP_11`; `unique(resp)`
= 1-5).
