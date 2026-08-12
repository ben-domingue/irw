# Extraction log: assessment_time_fournier_2025_pmpuq

## Source type used
**Standard/original instrument text, cross-referenced** — not a literal transcript pulled
from this specific study's own materials, because this specific study's OSF project does
not disclose a questionnaire/materials document (see "OSF search" below). The PMPUQ-SV is
a well-known, publicly published 15-item scale (Problematic Mobile Phone Use
Questionnaire, Short Version; Billieux et al.). Item wording and response-scale anchors
were taken from Appendix A (English version) of López-Fernández, Kuss, Griffiths, Billieux
et al., "Measurement Invariance of the Short Version of the Problematic Mobile Phone Use
Questionnaire (PMPUQ–SV) across Eight Languages," *Int. J. Environ. Res. Public Health*
2018, 15(6), 1213 (PMC6025621), which reproduces the full 15-item English wording and
1–4 scoring key verbatim in its Appendix A.

## OSF search (this study's own materials — Step 3)
Dictionary URL `https://osf.io/6v5qb/files/osfstorage` was crawled via the OSF v2 API
(`api.osf.io/v2/nodes/6v5qb/files/osfstorage/` and the underlying `files.de-1.osf.io`
waterbutler endpoints). Full tree:
```
/Development phase/Pilot data/        (files, raw+processed CSVs)
/Development phase/Non-pilot data/    Anonymized raw non-pilot data.csv
                                       Anonymized processed non-pilot data.csv
/Evaluation phase/Pilot data/         (files, raw+processed CSVs)
/Evaluation phase/Non-pilot data/     Anonymized raw non-pilot data.csv
                                       Anonymized processed non-pilot data.csv
                                       Test-retest reliability evidence ... .csv (x2)
```
No component/child nodes exist (`GET .../children/` returned `total: 0`). No
questionnaire, materials, codebook, or PDF was present anywhere in the OSF storage tree —
only raw/processed response-data CSVs. Cached the two "processed" CSVs (dev + eval,
non-pilot) at `.cache/assessment_time_fournier_2025_pmpuq/dev_processed_nonpilot.csv` and
`eval_processed_nonpilot.csv`.

These CSVs **do** corroborate structure: column headers include
`PMPUQ.SV.15_1`..`PMPUQ.SV.15_15` (alongside `UPPS.P.20.R_*`, `BSCS.13_*`, `GAD.7_*`,
`PHQ.9_*`), confirming (a) this is the same 15-item PMPUQ-SV in the same 1–15
presentation-order numbering as the IRW `item` values (`pmpuq.sv.15_1`..`_15`), and
(b) it was administered alongside other short scales as part of a broader
assessment-time/short-form-development battery — matching the dictionary reference
(Fournier et al., paper on reducing assessment time via short-form development, e.g. the
companion UPPS-P-20-R paper: Fournier, Heeren, Baggio, Clark, Verdejo-García, Perales, &
Billieux, *Collabra: Psychology*, 2026). The source paper PDF itself
(`fournier_2026_uppsp20r_paper.pdf`, cached) was checked and does not reproduce PMPUQ-SV
item wording either — it is cited only as one of several convergent-validity measures,
not the paper's focal instrument.

## Structure discovered
- 15 items, presentation order 1–15 matches the standard PMPUQ-SV item order (and the
  live IRW item numbering `pmpuq.sv.15_1`..`_15`).
- Three subscales of 5 items each, per the standard instrument (not encoded as separate
  `section_id`s here — no shared passage/context text exists per subscale beyond the
  single overall instructions block, so one trivial `section_id`
  (`assessment_time_fournier_2025_pmpuq_1`) covers all 15 items with blank
  `section_prompt`, per the skill's rule for instruments without real testlet grouping):
  - Dependence: items 1, 4, 7, 10, 13
  - Dangerous use: items 2, 5, 8, 11, 14
  - Prohibited use: items 3, 6, 9, 12, 15
- Response scale: 1 = "Strongly agree", 2 = "Agree", 3 = "Disagree", 4 = "Strongly
  disagree" — matches ground truth `resp` values 1–4 exactly, in this exact order (not
  reversed).
- `instructions` (applies to whole instrument, from Appendix A): "In relation with your
  mobile phone/smartphone, please answer these questions on a scale from 1 to 4, the
  numbers corresponding to: 1 'Strongly agree', 2 'Agree', 3 'Disagree', 4 'Strongly
  disagree'. The statement suits you:" — kept as terse as the source (a short framing
  sentence plus the lead-in stem), not expanded.

## has_bare_integer_items
FALSE, as noted in the dictionary row — the ground-truth `item` values are already
semantic codes (`pmpuq.sv.15_1`..`_15`), not bare integers, so no positional
reconstruction/inference was needed to assign item identity (the code already names the
instrument and item number); only the item *text* for each named item had to be sourced
externally.

## OCR / image-based extraction
None. All source text (item wording, response anchors, OSF file listing) was extracted
from machine-readable HTML/PDF text (PMC HTML article, OSF JSON API, downloaded CSV
headers) — no OCR was required or used.

## Derived vs. directly-read values
- `item`, `resp`: directly read from ground truth (`irw_fetch`-equivalent cached RDS),
  not derived.
- `item_text`, `option_text`, `instructions`: directly read (transcribed verbatim) from
  López-Fernández et al. (2018) Appendix A — an external validation-literature source,
  not this study's own materials (none were found). This is the one non-literal-to-source
  substitution in this extraction: the *exact* wording as presented to Fournier et al.'s
  2025 participants was not independently confirmed, only inferred from (a) the
  well-established, publicly standard nature of the PMPUQ-SV and (b) the OSF data CSVs'
  column-header naming, which matches this specific 15-item/1-15-order scale exactly.
- `correct_response`: left blank — no scoring key exists for this self-report attitude/
  behavior scale (some items are reverse-keyed for subscale scoring, but that's a scoring
  convention, not a "correct answer").
- `section_id`/`section_prompt`: derived per the skill's rule for instruments without real
  testlet/passage grouping (single trivial `section_id`, blank `section_prompt`), not
  read from any source.

## Ambiguities / discrepancy
None material — full 15/15 item match, full 4/4 resp match. The only caveat (not a
discrepancy against ground truth, but worth flagging) is documented above: item/option
text comes from a cross-referenced validation-literature source rather than a materials
file specific to this OSF record, since no such file exists in this study's OSF storage.
Not logged to `pending_index_notes.csv` since it isn't a partial/count/mapping
discrepancy — it's a full, validated match with the source-type caveat recorded here per
the SKILL.md instruction to log discrepancies, not simply omitted.

## Items not extracted
None — all 15 ground-truth items matched and were extracted; validated exact item/resp
set match against the cached ground truth for `assessment_time_fournier_2025_pmpuq`
(`unique(item)`: 15/15 match; `unique(resp)`: 4/4 match, values 1–4).
