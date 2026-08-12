# Extraction log: pezzuti_2025_coolpeople_main_individualism_usa

## Source type used
Study's own raw-data file metadata (SPSS variable/value labels), same approach used
successfully for the sibling table `pezzuti_2025_coolpeople_autonomous`. The journal PDF
(`https://www.apa.org/pubs/journals/releases/xge-xge0001799.pdf`) is blocked by bot
protection (Incapsula) when fetched programmatically, and the OSF project page
(`https://osf.io/m7gps/overview?view_only=...`) renders as a JS single-page app that
WebFetch can't read. Reused the already-cached OSF v2 REST API file listing
(`osf_filelist.json`) and the already-downloaded
`Data_main experiment_13 countries_July 2 2024.sav` (18 MB) — this table's
`main_individualism_usa` name refers to the same "main experiment, 13 countries" study as
`pezzuti_2025_coolpeople_autonomous`, filtered to the USA subsample (`cov_country == "USA"`
in the ground truth), not a separate raw file. Read the file's own variable/value labels
with `pyreadstat.read_sav(..., metadataonly=True)` (no row data touched) — these are the
Qualtrics-exported literal item and response-anchor text, not a paraphrase.

Cached under `.cache/pezzuti_2025_coolpeople_main_individualism_usa/` (copied from the
sibling table's cache, same underlying file):
- `osf_filelist.json` — OSF API file listing
- `Data_main experiment_13 countries.sav` — source of the variable/value labels

## OCR / image-based extraction
None. All text came directly from machine-readable SPSS variable/value-label metadata
(`pyreadstat.read_sav(..., metadataonly=True)`), not from an image or scanned PDF, so no
OCR was involved and no OCR-transcription risk applies here.

## Derived vs. directly-read values
- `item_text` for all 8 items — **directly read**, verbatim, from each variable's
  `column_names_to_labels` entry in the `.sav` file (e.g. `individualism1_jpsp`'s label
  is "Indicate the extent to which you agree or disagree with the following statements. -
  I'd rather depend on myself than others."). The shared instructional stem was split off
  into `instructions` (see below); only the item-specific clause after the dash was kept
  in `item_text`. Not derived or paraphrased otherwise.
- `instructions` — directly read, the identical shared prefix across all 8 variables'
  labels: "Indicate the extent to which you agree or disagree with the following
  statements." (verbatim, no edits — unlike the sibling `autonomous` table, there was no
  piped-text placeholder to substitute here).
- `option_text` for resp=1 ("Strongly Disagree") and resp=7 ("Strongly Agree") —
  directly read from each variable's value-label dictionary (all 8 items share identical
  labels: `{1.0: 'strongly disagree1', 2.0: '2', ..., 7.0: 'strongly agree7'}`); the
  trailing digit in the raw label (e.g. "strongly disagree1") is a Qualtrics
  anchor-numbering artifact, stripped and title-cased for `option_text`, not a
  re-derivation of meaning.
- `option_text` for resp 2-6 — left blank; the value labels for those points are just the
  bare numeral strings ("2","3",...,"6"), i.e. unlabeled intermediate scale points in the
  original instrument, so blank is the literal transcription, not a gap.
- `instrument` label — **derived**, not quoted from any single source string. Neither the
  `.sav` file nor the OSF materials name the instrument directly on these 8 variables (the
  `_jpsp` variable-name suffix is the only naming hint). Content cross-check confirms
  these 8 items are the Horizontal Individualism (items 1-4: "rather depend on myself",
  "rely on myself... rarely rely on others", "do my own thing", "personal identity...
  independent of others") and Vertical Individualism (items 5-8: "do my job better than
  others", "winning is everything", "competition is the law of nature", "get tense and
  aroused" when outperformed) subscales of Triandis, H. C., & Gelfand, M. J. (1998).
  "Converging measurement of horizontal and vertical individualism and collectivism."
  *Journal of Personality and Social Psychology*, 74(1), 118-128 — matching the `_jpsp`
  suffix hint exactly (this is the JPSP paper) and matching the item wording verbatim
  against the published INDCOL scale (not the Singelis 1994 self-construal scale or the
  Triandis & Gelfand full 16-item INDCOL, of which these 8 are the "individualism" half).
  Combined this identification into a descriptive instrument label since no single source
  string names it directly.
- `correct_response` — blank for all rows (attitude/self-report Likert scale, no scoring
  key).
- `section_id`/`section_prompt` — no testlet/passage grouping in the source; used one
  trivial `<table>_1` section_id with blank `section_prompt`, per the skill's rule for
  instruments without real section structure.

## has_bare_integer_items
FALSE, confirmed. Ground-truth `item` values are already semantic string codes
(`individualism1_jpsp`..`individualism8_jpsp`), not bare integers, so no
item-to-text position-mapping reconstruction was needed — each `.sav` variable name
mapped directly and unambiguously to its own ground-truth `item` value.

## Ambiguities / discrepancies
None material. The `main_individualism_usa` table name (vs. the sibling
`coolpeople_autonomous`, which has no country qualifier) suggested this might be a
distinct raw file or subsample-specific instrument variant; confirmed via the ground
truth's `cov_country` column that it is simply the USA rows filtered from the same
13-country main-experiment dataset, with the identical instrument/items/instructions
applying regardless of country — no separate USA-specific raw file or wording exists.

## Items not extracted
None — all 8 ground-truth items (`individualism1_jpsp`..`individualism8_jpsp`) and all 7
ground-truth resp values (1-7) were extracted and matched exactly.

## Validation result
Exact match: `unique(candidate$item)` == `unique(irw::irw_fetch(table)$item)` (verified
against cached ground truth `.gt_pezzuti_2025_coolpeople_main_individualism_usa.rds`) and
`unique(candidate$resp)` == `unique(irw::irw_fetch(table)$resp)`. No pending_index_notes.csv
entry needed.
