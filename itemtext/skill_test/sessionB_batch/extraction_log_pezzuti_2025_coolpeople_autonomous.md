# Extraction log: pezzuti_2025_coolpeople_autonomous

## Source type used
The journal PDF (`https://www.apa.org/pubs/journals/releases/xge-xge0001799.pdf`) is
blocked by bot protection (Incapsula) when fetched programmatically, and the OSF
project page itself (`https://osf.io/m7gps/overview?view_only=...`) renders as a JS
single-page app that WebFetch can't read. Went around both via the OSF v2 REST API
(`https://api.osf.io/v2/nodes/m7gps/files/osfstorage/?view_only=...`), which lists the
project's 8 files (all `.sav`/`.sps`, no separate "materials" PDF/codebook). Downloaded
`Data_main experiment_13 countries_July 2 2024.sav` (18 MB, the main cross-country study
this table's data comes from) and read its **SPSS variable labels** with `pyreadstat`
(`metadataonly=True`, no row data touched) — these variable/value labels are the
Qualtrics-exported literal item and response-anchor text, not a paraphrase. This is a
"source type: study's own raw-data file metadata" extraction, not the published paper
text (the paper itself doesn't reprint full item wording; it only names the instrument
as an adapted Portrait Values Questionnaire).

Cached under `.cache/pezzuti_2025_coolpeople_autonomous/`:
- `osf_filelist.json` — OSF API file listing
- `Data_main experiment_13 countries.sav` — source of the variable/value labels
- `xge-xge0001799.pdf` — failed fetch (Incapsula HTML block page, not the real PDF;
  kept only as evidence of the block, not used as a source)

## OCR / image-based extraction
None. All text came directly from machine-readable SPSS variable/value-label metadata
(`pyreadstat.read_sav(..., metadataonly=True)`), not from an image or scanned PDF, so no
OCR was involved and no OCR-transcription risk applies here.

## Derived vs. directly-read values
- `item_text` for all 4 items — **directly read**, verbatim, from each variable's
  `column_names_to_labels` entry in the `.sav` file (e.g. `autonomous2`'s label ends
  "... - This person likes doing things in his/her own way."). Not derived or
  paraphrased.
- `option_text` for resp=1 ("Strongly disagree") and resp=7 ("Strongly agree") —
  directly read from each variable's value-label dictionary (`{1.0: 'strongly
  disagree1', ..., 7.0: 'strongly agree7'}`); the trailing digit in the raw label
  (e.g. "strongly disagree1") is a Qualtrics anchor-numbering artifact, stripped and
  title-cased for `option_text`, not a re-derivation of meaning.
- `option_text` for resp 2-6 — left blank; the value labels for those points are just
  the bare numeral strings ("2","3",...,"6"), i.e. unlabeled intermediate scale points
  in the original instrument, so blank is the literal transcription, not a gap.
- `instructions` — directly read from the shared prefix of all four variables' labels
  ("Indicate the extent that you agree or disagree that the following statements apply
  to [QID313-ChoiceTextEntryValue], the person you nominated. ... Please respond to the
  items based on what you know about this person or the image the person projects."),
  with one **derived** substitution: the Qualtrics piped-text placeholder
  `[QID313-ChoiceTextEntryValue]` (which Qualtrics would have replaced with the actual
  name/description the participant typed in an earlier question) was replaced with the
  literal bracketed placeholder `[target person]` for readability, since the raw
  merge-field code is not what any participant actually saw on screen. This is the only
  non-verbatim edit made to any transcribed text in this table.
- `instrument` label — **derived**, not quoted from any single source string. The paper's
  abstract/press coverage describes the measure only as "the Portrait Values
  Questionnaire, which measures attributes including autonomy..."; the `.sav` file names
  the underlying construct via a summary-score variable labeled "factor that represents
  how autonomous the target seems" but doesn't name the instrument. Combined both into a
  descriptive instrument label rather than inventing a formal scale name not stated
  anywhere in the source.
- `correct_response` — blank for all rows (personality/perception rating scale, no
  scoring key).
- `section_id`/`section_prompt` — no testlet/passage grouping in the source; used one
  trivial `<table>_1` section_id with blank `section_prompt`, per the skill's rule for
  instruments without real section structure.

## has_bare_integer_items
FALSE, confirmed. Ground-truth `item` values are already semantic string codes
(`autonomous1`..`autonomous4`), not bare integers, so no item-to-text position-mapping
reconstruction was needed — each `.sav` variable name mapped directly and unambiguously
to its own ground-truth `item` value.

## Ambiguities / discrepancies
None material. One point worth flagging: `autonomous1`'s item content ("This person is
good at thinking up new ideas and being creative") reads more like a
creativity/self-direction-thought item than "free/independent" per se — this is expected
and correct, not an error: Schwartz's Portrait Values Questionnaire "Self-Direction"
value type (which the paper's "autonomous" dimension operationalizes) canonically
combines both a creativity/new-ideas item and an independence/own-decisions item, and
`autonomous2`-`autonomous4` (own way, own decisions, free to plan) are unambiguously the
independence-flavored items. No re-labeling or reordering was applied.

## Items not extracted
None — all 4 ground-truth items (`autonomous1`..`autonomous4`) and all 7 ground-truth
resp values (1-7) were extracted and matched exactly.

## Validation result
Exact match: `unique(candidate$item)` == `unique(irw::irw_fetch(table)$item)` and
`unique(candidate$resp)` == `unique(irw::irw_fetch(table)$resp)` (verified against the
cached ground truth `.gt_pezzuti_2025_coolpeople_autonomous.rds`; the only mismatch
initially observed was an R integer-vs-double type difference in `resp`, not a value
difference, and was resolved by writing `resp` as numeric).
