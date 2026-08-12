# Extraction log: alsecypiamh_wu_2022_nei

## has_bare_integer_items
FALSE, per dictionary row. Ground-truth `item` values are already semantic codes
(`NEI1`-`NEI5`), not bare integers, so no positional reconstruction against the paper's
item order was needed/attempted -- the item identity is given directly by the item
code itself; what's missing is the item *text*, not the item-to-code mapping.

## Source type used
Mixed: (1) cached prior-session material, (2) OSF project file listing (fetched live via
OSF API through `WebFetch`, not `irw::irw_fetch`), (3) `.sav` variable-name metadata read
directly with `pyreadstat` in Python, (4) web search for the published paper's abstract/
metadata (full text paywalled, never opened). No PDF or paper full text was read for this
table -- see "Paper access" below.

## Cache check (per task instructions)
`.cache/alsecypiamh_wu_2022_nei/` already contained `jora12944-sup-0001-Supinfo.docx`
from a prior crashed attempt. Converted with `pandoc -f docx -t plain` (regex-based
`<w:t>` extraction was tried first and produced garbled/interleaved XML-tag text --
abandoned in favor of `pandoc`, which is a proper docx parser). This file is Supplement 1
to the *published* Journal of Research on Adolescence (JORA) paper: Wu, Y., Yan, W., Wu,
Y., & Peng, K. (2024). "Adaptation and validation of the Claremont Purpose Scale to
measure Chinese adolescents' purpose in life." *JORA*, 34(3), 776-790.
https://doi.org/10.1111/jora.12944. It contains the full bilingual (English/Chinese)
12-item Claremont Purpose Scale (CPS) text -- **not** the NEI measure. This paper is the
peer-reviewed publication of the same OSF project (`osf.io/jqzbx`) named in this table's
dictionary row ("A large-scale evaluation of Chinese youth purpose and its associations
with mental health," 2024-04-18 registration) -- confirmed by fetching the OSF node
directly (title/description match the JORA abstract; project has 0 child components and
no linked preprint).

## OSF project file inventory
Queried `https://api.osf.io/v2/nodes/jqzbx/files/osfstorage/` directly (not scraped HTML,
which returned an empty JS shell via `WebFetch`). The project's storage contains exactly
one folder, "Adaptation and validation of the Claremont Purpose Scale...", with 4 files:
- `CPS Pre-Study.sav` (N=34, CPS items only)
- `CPS Study 1.sav` (N=1691, CPS items + demographics only)
- `CPS Study 2.sav` (N=7842, 92 variables -- **this is the file that contains NEI**)
- `jora12944-sup-0001-Supinfo.docx` (already cached; CPS item text, both language versions)

Downloaded `CPS Study 2.sav` and `CPS Pre-Study.sav` fresh (`CPS Study 1.sav` already
implied not needed) and read with `pyreadstat.read_sav()` in Python (R's `haven`/`foreign`
were an alternative not needed since pyreadstat was available).

## What was confirmed
- `CPS Study 2.sav` has exactly N=7842 rows -- matches ground truth's `length(unique(id))
  == 7842` exactly. This is unambiguously the source dataset for this IRW table.
- Its column list includes both a composite `NEI` column (used for the composite scale
  score) and five item-level columns `NEI1`..`NEI5`, matching ground truth's 5 items
  exactly.
- `pyreadstat`'s `column_names_to_labels` (from the .sav's variable metadata) gives:
  `NEI -> "Negative Emotions"`. This is the .sav file's own author-supplied label for the
  composite variable, not an inference -- high confidence this is what NEI stands for
  ("Negative Emotions [Index/Inventory]"). A parallel `PEI` column is labeled "Positive
  Emotions", confirming a paired positive/negative emotion-checklist design (5 items
  each), consistent with `resp` being binary (0/1) -- i.e., a checklist rather than a
  Likert-type scale.
- The five item-level columns `NEI1`-`NEI5` themselves have **no** variable label
  (`column_names_to_labels` returns `None`/blank for all five) -- the .sav file does not
  carry literal item wording, only the composite-level label.

## What was NOT recovered -- item-level text for NEI1-NEI5
No source available in this environment discloses the literal wording of the 5 NEI items
or what response option "0" vs. "1" was labeled as (e.g. "No"/"Yes", "Did not feel this
way"/"Felt this way", etc.):
- The cached/OSF supplementary docx covers only the CPS instrument (Supplement 1), not
  the study's other convergent/predictive-validity measures (PEI, NEI, Dep, SDQ_Pro,
  Empathy, SWEMWBS, etc. -- all present as composite + item columns in `CPS Study 2.sav`
  but none of the item-level columns for *any* of these ancillary measures carry a label
  in the .sav metadata).
- The JORA paper itself (10.1111/jora.12944) is paywalled -- `WebFetch` on the Wiley URL
  returned HTTP 402 Payment Required. No PMC, institutional-repository, or other
  open-access full-text copy was found via web search (PubMed lists only a subscription
  "Ovid Technologies" full-text link, no PMC link).
- The OSF project (`osf.io/jqzbx`) has no child components and no linked preprint (both
  confirmed via the OSF API), so there is no separate open preprint PDF to check either.

## Considered and explicitly rejected: guessing the source instrument
Given the "Positive/Negative Emotions, 5 items each, binary yes/no" structure, the
Bradburn (1969) Affect Balance Scale (ABS) is a structurally plausible match (it is
exactly 5 positive + 5 negative items, yes/no format, and is a long-established
instrument sometimes adapted into Chinese-language wellbeing batteries). **This was not
used or written into the output.** Nothing in the OSF project, the cached docx, or the
paper's (paywalled) abstract confirms Wu et al. actually used the Bradburn ABS rather
than some other researcher-adapted or study-specific 5-item checklist -- per this skill's
explicit instruction not to guess/fabricate item text, this candidate instrument name is
recorded here only as a lead for a human to verify against the paper body, not asserted
in `candidate_alsecypiamh_wu_2022_nei.rds`.

## Structure of output
Single trivial `section_id` (`alsecypiamh_wu_2022_nei_1`) for all 5 items -- no testlet/
passage grouping disclosed or plausible for a short emotion checklist. `instrument` field
populated with the confirmed construct name + citation (this much is directly sourced,
not guessed). `instructions`, `section_prompt`, `item_text`, `correct_response`, and
`option_text` all left blank for every row, since none of that literal text was
recoverable. `item` and `resp` columns are drawn directly from the ground-truth value
sets (`NEI1`-`NEI5`; `0`,`1`) per the non-negotiable rule -- never invented.

## Validation
`unique(item)` and `unique(resp)` on the candidate exactly match
`readRDS(".gt_alsecypiamh_wu_2022_nei.rds")` (5 items `NEI1`-`NEI5`; resp `{0,1}`).
Structural/ID-level match is exact; item-text-level content is the acknowledged gap.

## OCR / image-based extraction
Not applicable -- no image-based or scanned source was used. The one document consulted
in depth (`jora12944-sup-0001-Supinfo.docx`) is a native Word file with embedded text
(tables), extracted cleanly via `pandoc -f docx -t plain`; it did not contain the NEI
measure at all (see above), so no OCR step was ever invoked for this table.

## Derived vs. directly-read values
- **Directly read** (not derived/inferred): `item` and `resp` value sets (ground truth);
  N=7842 in `CPS Study 2.sav` (file metadata, matches ground truth `id` count); the
  `NEI`/`PEI` composite variable labels "Negative Emotions"/"Positive Emotions" (.sav
  column-label metadata, author-supplied).
- **Derived/inferred, not written into the output as literal text**: that NEI1-NEI5 are
  a 5-item binary checklist (inferred structurally from the 5 item-level columns + the
  0/1 coding + the "Negative Emotions" composite label -- reasonable but not itself a
  literal quoted source). The Bradburn ABS hypothesis (explicitly not used, see above).
- **Nothing was derived and presented as if directly read** -- item_text/option_text
  were left blank rather than back-filled from either inference.

## Items not extracted
All 5 items (`NEI1`-`NEI5`): item identity and resp coding are confirmed exact, but
literal item wording and response-option labels are not recoverable from any source
accessible in this environment. Logged to `pending_index_notes.csv`.
