# Extraction log: mhscdc_fried_2020_ps

## Source used
Dictionary URL (https://osf.io/mvdpe/) points to the OSF project for Fried & Epskamp
(2022), "Mental Health and Social Contact During the COVID-19 Pandemic: An Ecological
Momentary Assessment Study." Reused the already-cached OSF "6. Measures" materials from
the sibling `mhscdc_fried_2020_dass` table, under `.cache/mhscdc_fried_2020_dass/`
(no new download needed):
- `Measures_Baseline.pdf` / `Measures_Baseline.txt` (participant-facing survey export,
  Baseline assessment; `.txt` is a cached `pdftotext -layout` extraction)
- `Codebook_Baseline.xlsx`, `Codebook_Post.xlsx` (variable-level codebooks) — checked but
  not needed as primary source (see below)

`item_text` and `option_text` were transcribed literally from `Measures_Baseline.pdf`
(via `Measures_Baseline.txt`), items 90(Q#206) through 99(Q#216), the block headed by
item 89(Q#151) "Questionnaire 7".

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` — confirmed. Ground-truth `item`
values are `"Pre68"`..`"Pre77"` — the raw/literal column names from the original data
export, not a renumbered "item_N" convention and not bare integers.

The `Pre68`..`Pre77` <-> paper-item mapping was NOT guessed or inferred by
range/position-matching alone. It was confirmed directly from
`data/mhscdc_fried_2020.r` (this repo's own processing script for this dataset):
```r
dass_df <- process_dass_data(bt_df, "Pre", 68, 77, "mhscdc_fried_2020_ps")
```
`process_dass_data()` (the non-"2" variant, also used for `_anger`, `_se`,
`_mindfullness`, `_motivation`, `_smartphone`) does `select(..., num_range(prefix,
start_q:end_q)) %>% pivot_longer(...)` — i.e. it keeps the raw `"Pre<N>"` column name
AS the `item` value verbatim, with no renumbering or offset (unlike `process_dass_data2`,
used for `_dass`/`_procrastination`, which does renumber to `item_1..item_N`). This was
cross-checked against `.gt_mhscdc_fried_2020_ps.rds`: `unique(item)` is exactly
`"Pre68".."Pre77"`, confirming the raw-column-name convention held here.

Then, to map `Pre68`..`Pre77` to specific paper item text (since the *document's own*
running item-index in `Measures_Baseline.pdf`, e.g. 89/90/.../99, is a different ordinal
than "PreN" — the full export interleaves non-`Pre*` columns such as demographics and
attention checks), positional bracketing against three independent cues was used, all of
which agree:
1. **Item-count match**: the block between the "Questionnaire 6" header (doc index 76,
   confirmed = Mindfulness = `Pre56`-`Pre67`, 12 items, per the script) and the next
   "Questionnaire 8" header (doc index 100, = Tiredness, a separate IRW table) is
   "Questionnaire 7" (doc index 89 header, items 90-99 = 10 items) — matching PS's
   10-item range `Pre68`-`Pre77` exactly, and sitting in the correct sequential position
   (mindfulness immediately precedes PS in both the script's Pre-numbering and the
   document's block order).
2. **Content match**: the 10 items transcribed (doc index 90-99) are, word-for-word and
   in the same order, the canonical published Perceived Stress Scale (PSS-10; Cohen,
   Kamarck, & Mermelstein, 1983) — "upset because of something unexpected" / "unable to
   control important things" / "felt nervous and stressed" / "confident ... handle
   personal problems" / "things going your way" / "could not cope" / "control
   irritations" / "on top of things" / "angered ... outside of your control" /
   "difficulties piling up" — confirming the instrument identity independent of the
   `Pre*` mapping.
3. **Response-scale match**: the block's 5 response options are numbered 1-5 in the
   document's radio-button listing, matching ground-truth `resp` 1-5 exactly (see
   "Derived vs. directly-read values" below for the 0-4 vs 1-5 note).

## Derived vs. directly-read values
- `item_text`, `option_text`: directly read (transcribed verbatim) from
  `Measures_Baseline.pdf` / `Measures_Baseline.txt`, not derived or paraphrased.
- `item` values (`Pre68`..`Pre77`): directly matched against ground truth (raw column
  names, no transformation); the *mapping* from `Pre68..Pre77` to specific PSS-10 item
  text is a derived/reconstructed value (see above), based on the processing script's
  raw-column-passthrough logic plus positional/content/response-scale corroboration —
  not a literal field copied from one source.
- `instrument` name ("Perceived Stress Scale (PSS-10)"): derived — not stated verbatim
  as a title anywhere in the OSF measures documents (the survey export only labels it
  "Questionnaire 7"), but confirmed as the correct instrument identity by exact
  item-text match against the well-known published PSS-10.
- `resp`/`option_text` scale: directly read from the PDF's 5 response options as
  presented (options numbered 1-5 in the radio-button list; each option's own printed
  label text additionally embeds the canonical PSS-10 "0"-"4" numeral, e.g. option 1's
  full printed text is "0 Never", option 5's is "4 Very often"). The value written to
  `resp` is the **selectable position** (1-5), matching ground truth exactly; the
  embedded "0"-"4" numerals were kept as part of the verbatim `option_text` string
  rather than stripped, since that is literally what was printed to participants. This
  is effectively a +1 shift of the canonical PSS-10 0-4 scoring onto this platform's
  1-5 radio-button coding (the same platform-numbering pattern seen elsewhere in this
  study), not a different response scale.
- `correct_response`: left blank — PSS-10 is a self-report scale with no scoring key/
  correct answer; not derived from any source, this is a structural no-value field.
- `instructions`: left blank (see below) — not derived or fabricated.

## OCR / image-based extraction
Not applicable. `Measures_Baseline.pdf` is a text-based (not scanned/image) PDF; the
already-cached `Measures_Baseline.txt` (`pdftotext -layout` output, produced for the
sibling `_dass` table) provided clean, directly copy-pasteable text with no OCR needed.
All 10 item stems and all 5 response-option strings were extracted this way and spot-
checked by eye against the raw text output; three item stems (90, 91, 93, 95, 98, 99)
wrap across two lines in the PDF layout (long "In the last month, how often..." stems)
but were reassembled without alteration.

## Source type used
Primary: OSF-hosted "Measures" PDF (`Measures_Baseline.pdf`), a text-native export of
the Ethica survey-app screens shown to participants — the actual participant-facing
instrument text, preferred over the codebook for `item_text`/`option_text`
transcription. `Codebook_Baseline.xlsx` was checked but not needed as a primary or
corroborating source here (unlike `_dass`, no ambiguity existed in the raw-column
mapping since `process_dass_data()`'s passthrough behavior was unambiguous from the
script alone); item-count/content/response-scale cross-checks (see above) were
sufficient corroboration in place of a codebook lookup.

## Discrepancy: no standalone `instructions` text found
No standalone whole-instrument instructions/framing text was found anywhere in
`Measures_Baseline.pdf` before the first PS item. Item 89(Q#151) is only a bare
section-divider label, "Questionnaire 7", with no participant-facing framing sentence
captured under it — each item stem instead repeats its own time-frame reminder ("In the
last month, how often have you ..."). Per the "match the source's terseness" rule and
the "don't fabricate" instruction, `instructions` was left blank (`""`) rather than
reconstructed from the well-known published PSS-10 standard instructions ("The
questions in this scale ask you about your feelings and thoughts during the last
month...") — that text is not present in the actual source materials for this dataset.
Same pattern as the sibling `_dass`, `_anger`, and `_procrastination` tables. Logged in
`pending_index_notes.csv`.

## Items not extracted
None — all 10 ground-truth items (`Pre68`..`Pre77`) were extracted with full
`item_text` and all 5 `option_text`/`resp` pairs. Validated: `unique(item)` and
`unique(resp)` of `candidate_mhscdc_fried_2020_ps.rds` match
`.gt_mhscdc_fried_2020_ps.rds` exactly (10 items, resp 1-5, 50 total item x resp rows).
