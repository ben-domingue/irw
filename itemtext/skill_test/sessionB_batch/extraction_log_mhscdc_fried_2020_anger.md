# Extraction log: mhscdc_fried_2020_anger

## Source used
Dictionary URL (https://osf.io/mvdpe/) points to the same OSF project as the sibling
table `mhscdc_fried_2020_dass` — Fried & Epskamp (2022), "Mental Health and Social
Contact During the COVID-19 Pandemic: An Ecological Momentary Assessment Study." Reused,
without refetching, the OSF "6. Measures" component materials already cached under
`.cache/mhscdc_fried_2020_dass/`:
- `Measures_Baseline.pdf` / `Measures_Baseline.txt` (participant-facing survey export,
  Baseline assessment) — primary source for `item_text` and `option_text`.
- `Codebook_Baseline.xlsx` — variable-level codebook mapping raw/clean column names to
  item text and response labels; used to directly confirm the `PreNN` <-> item mapping
  (see below), not just to corroborate wording.

## has_bare_integer_items
Dictionary row states `has_bare_integer_items: FALSE` — confirmed, and unlike the
sibling `_dass` table this is not even a generic `item_N` convention: ground-truth
`item` values are the literal raw column names `"Pre34".."Pre40"` used directly, with
no renumbering/offset applied at all.

## How the Pre34-Pre40 mapping was confirmed (not guessed)
Checked `data/mhscdc_fried_2020.r` directly. The anger table is built with:
```r
process_dass_data <- function(df, prefix, start_q, end_q, output_file) {
  dass_df <- df %>%
    select(id, starts_with("cov"), num_range(prefix, start_q:end_q)) %>%
    pivot_longer(cols = -c(id, starts_with("cov")), names_to = "item", values_to = "resp")
  ...
}
...
dass_df <- process_dass_data(bt_df, "Pre", 34, 40, "mhscdc_fried_2020_anger")
```
This is the plain `process_dass_data` function (not the offset/renumbering
`process_dass_data2` used for the DASS/loneliness/procrastination/tired tables) — it
`pivot_longer`s the raw `Pre34`..`Pre40` columns straight into `item` with no
transformation, so `item` in the live IRW table is exactly the raw column name. This was
cross-checked directly against ground truth (`item` values are literally `Pre34`..`Pre40`,
confirmed above) — not inferred from range/position matching.

The item-text mapping for each `PreNN` was then read directly out of
`Codebook_Baseline.xlsx`'s `cleandata_pre` column (values `Q34`..`Q40`, one row per raw
item), which explicitly lists, in the same row, the `Ethica Items` position/question-ID
(`52(Q#141)`..`58(Q#147)`), a `Label/Scale` of `"Anger"` on the first row of the block, and
the literal item text:

| `cleandata_pre` | Ethica position | item_text |
|---|---|---|
| Q34 | 52 (Q#141) | I flare up quickly but get over it quickly. |
| Q35 | 53 (Q#142) | When frustrated I let my irritation show. |
| Q36 | 54 (Q#143) | I sometimes feel like a powder keg ready to explode. |
| Q37 | 55 (Q#144) | I am an even-tempered person. |
| Q38 | 56 (Q#145) | Some of my friends think I'm a hothead. |
| Q39 | 57 (Q#146) | Sometimes I fly off the handle for no good reason. |
| Q40 | 58 (Q#147) | I have trouble controlling my temper. |

`Pre34` = codebook `Q34`, `Pre40` = codebook `Q40`, etc. — the same `Pre<N>` <->
`Q<N>` naming correspondence already established and used for the sibling `_dass` table
(where `Pre1`..`Pre21` matched codebook `Q1`..`Q21`). This is a direct row-level lookup in
the codebook, not a positional/order guess: each `cleandata_pre` cell literally states the
`QNN` label next to its corresponding item text.

Independently, the `Measures_Baseline.txt` participant-facing export shows the same 7
items (Ethica positions 52-58) as a contiguous block headed "51 (Q#205): Questionnaire 3"
and immediately followed by a new "59 (Q#228): Questionnaire 4" header — i.e. a
self-contained 7-item block, matching the 7-item count of `Pre34`-`Pre40` exactly. Item
order in the PDF export (52->53->...->58) was assumed to follow the same ascending order
as `Pre34`->`Pre40`, which is consistent with the codebook's explicit row-by-row `Q34`..`Q40`
labeling above (not merely assumed from raw position — the codebook ties each Q# to its
own item text directly).

## Instrument identification
The 7 items ("I flare up quickly but get over it quickly," "When frustrated I let my
irritation show," "I sometimes feel like a powder keg ready to explode," "I am an
even-tempered person" [reverse-worded], "Some of my friends think I'm a hothead,"
"Sometimes I fly off the handle for no good reason," "I have trouble controlling my
temper") are, verbatim, the 7-item **Anger subscale of the Buss-Perry Aggression
Questionnaire (AQ)** (Buss & Perry, 1992, *Journal of Personality and Social Psychology*),
a well-known published instrument. This identification is derived/inferred — no source
document in the OSF Measures materials names "Buss-Perry" or "Aggression Questionnaire"
explicitly; the codebook only labels the block `Label/Scale = "Anger"` and the raw
variable-name suffix is `_SAQ` (e.g. `141_SAQ`), consistent with but not proof of this
identity. The item text itself is an exact wording match to the published Buss-Perry AQ
Anger subscale, which is the basis for the `instrument` field value. Flagged here as
derived, per the "OCR/derived vs. directly-read" distinction below.

## Derived vs. directly-read values
- `item_text`: directly read (transcribed verbatim) from `Measures_Baseline.txt`
  (text-native `pdftotext -layout` export of `Measures_Baseline.pdf`), cross-checked
  word-for-word against `Codebook_Baseline.xlsx`'s `Item` column for the same 7 rows —
  both sources agree exactly except for the presence/absence of a comma after
  "frustrated" (PDF has none, codebook shows none either — no discrepancy found).
- `option_text`: directly read from the PDF's 5 response options as shown under the first
  item of the block (52 (Q#141)); the same 5-option scale is repeated identically for all
  7 items in this block, so it was not re-transcribed 7 times, but confirmed as identical
  by inspecting the raw text for the full block range (lines corresponding to items 52-58
  in `Measures_Baseline.txt`).
- `item` values (`Pre34`..`Pre40`): directly matched to ground truth; the *mapping* from
  `Pre<N>` to a specific Buss-Perry AQ item is a derived/reconstructed value (see above),
  based on the processing script's pass-through logic plus the codebook's direct
  `cleandata_pre` = `Q<N>` row-level lookup — not a literal field copied from one source
  as-is.
- `instrument` name ("Buss-Perry Aggression Questionnaire (AQ) - Anger subscale") —
  derived, not stated verbatim anywhere in the OSF materials (see "Instrument
  identification" above); confirmed via exact item-text match to the well-known published
  scale, same evidentiary standard used for the sibling `_dass` table's DASS-21
  identification.
- `resp`/`option_text` scale: directly read from the PDF's 5 response options (1-5),
  matching ground truth `resp` values 1-5 exactly.
- `correct_response`: left blank — a self-report personality/anger-trait scale has no
  scoring key/correct answer; structural no-value field, not derived or fabricated.
- `instructions` / `section_prompt`: both left blank (see below) — not derived or
  fabricated.

## OCR / image-based extraction
Not applicable. `Measures_Baseline.pdf`/`.txt` is a text-based (not scanned/image) PDF,
already extracted with `pdftotext -layout` for the sibling `_dass` extraction — reused
as-is here, no OCR involved. All 7 item stems and the 5 response-option strings were
read directly from that clean text output.

## Source type used
Primary: OSF-hosted "Measures" PDF/text export (`Measures_Baseline.pdf` /
`Measures_Baseline.txt`), the actual participant-facing Ethica survey-app screens shown
to participants — preferred for `item_text`/`option_text` transcription, consistent with
the sibling `_dass` table's approach. Secondary/corroborating: `Codebook_Baseline.xlsx`,
used both to confirm the `Pre<N>` <-> `Q<N>` <-> Ethica-position mapping (the decisive
evidence for which paper item each `Pre<N>` column refers to) and to cross-check item
wording.

## Discrepancy: no standalone `instructions` or `section_prompt` text found
As with the sibling `_dass` table, no standalone whole-instrument instructions/framing
text was found before the first anger item. The block header "51 (Q#205): Questionnaire
3" is a bare section-divider label with no participant-facing framing sentence beneath
it — the label itself was not treated as a `section_prompt` per the skill's rule that
bare section-divider labels are not substantive prompt text. `instructions` and
`section_prompt` were both left blank (`""`) rather than reconstructed from the known
published Buss-Perry AQ standard instructions ("Using the scale below, indicate how
uncharacteristic or characteristic each of the following statements is in describing
you...") — that exact text is not present in the actual source materials for this
dataset. Logged in `pending_index_notes.csv`.

## Items not extracted
None — all 7 ground-truth items (`Pre34`..`Pre40`) were extracted with full `item_text`
and all 5 `option_text`/`resp` pairs (1-5). Validated: `unique(item)` and `unique(resp)`
of `candidate_mhscdc_fried_2020_anger.rds` match `.gt_mhscdc_fried_2020_anger.rds`
exactly (7 items x 5 responses = 35 rows, item and resp sets identical).
