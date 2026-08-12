# Extraction log: psychotools_gratitude_gac

## Source used
Same two sources as the already-completed `psychotools_gratitude_gart` table (same paper,
same R package), reused from cache:
1. R package documentation: `psychotools::YouthGratitude` help page (`?YouthGratitude`,
   read via `tools::Rd_db("psychotools")` / `Rd2txt`). This gives literal item wording for
   all 28 variables in the package's example dataset, including the 3 GAC items
   (`gac_1`, `gac_2`, `gac_3`), and a Details section confirming "GAC: Gratitude Adjective
   Checklist (1-5)."
2. The source paper: Froh, Fan, Emmons, Bono, Huebner, & Watkins (2011), *Psychological
   Assessment*, 23(2), 311-324 — reused cached copy at
   `.cache/psychotools_gratitude_gart/froh2011.pdf` / `froh2011.txt` (already fetched and
   `pdftotext -layout`'d for the gart extraction; no new fetch needed). Body text (p. ~9,
   "Gratitude Adjective Checklist (GAC)" section and the Method section) states: "A second
   self-report scale, the Gratitude Adjective Checklist (GAC; McCullough et al., 2002) is
   the sum of the affect adjectives grateful, thankful, and appreciative," and later:
   "The GAC is a 3-item measure of gratitude using a Likert scale from 1 (very slightly or
   not at all) to 5 (extremely) followed each item. ... Students in the present study were
   asked to rate the amount they experienced each feeling 'during the past few weeks.'"

## Source type used
Directly-read literal text from both sources: the psychotools `Rd2txt` help output (a
maintained, citable source distributed by the original data contributors Jeff Froh and
Jinyan Fan — same provenance as `gart`) for the three item stems (`gac_1`="Grateful.",
`gac_2`="Thankful.", `gac_3`="Appreciative."), and the paper's own body text (native-text
PDF, `pdftotext -layout`, no OCR) for the response-scale anchors and the instructions
text (task framing + timeframe), neither of which is stated in the package help page.

## OCR / image-based extraction
None. Both sources were native-text (Rd/PDF-text); no OCR was needed and no image-based
transcription was performed.

## Structure discovered
Ground truth: 3 items (`gac_1`, `gac_2`, `gac_3`), resp 1-5. Matches the psychotools
`YouthGratitude` package's GAC columns exactly. The psychotools help page's Details
section explicitly labels this "GAC: Gratitude Adjective Checklist (1-5)," and the paper
confirms this is McCullough, Emmons, & Tsang's (2002) 3-adjective checklist (grateful,
thankful, appreciative), scored on a 1 (very slightly or not at all) to 5 (extremely)
scale.

## Structure of output
One section (`psychotools_gratitude_gac_1`) — the 3 GAC items are a single flat checklist
with no subscale/testlet grouping, so `section_id` is populated per the skill's join-key
rule but `section_prompt` is left blank throughout (no shared passage/context text beyond
the whole-instrument instructions, which belong in `instructions` instead).
`instructions` is a single sentence combining the paper's two disclosed pieces of
task-level framing — the response-scale definition ("using a Likert scale from 1 (very
slightly or not at all) to 5 (extremely) followed each item") and the timeframe given to
participants ("rate the amount they experienced each feeling 'during the past few
weeks'") — both literal quotes from the paper, since GAC's timeframe is explicitly
noted in the paper as study-specific/adjustable (the GAC "can be used to measure gratitude
as an emotion, mood, or disposition depending on the timeframe specified in the
instructions"), so it belongs in `instructions`, not treated as a fixed instrument
property. `item_text` is the literal adjective for each item ("Grateful.", "Thankful.",
"Appreciative."), taken verbatim from the psychotools help page — terse single-word (plus
period) stems, matching the source's own terseness; not expanded into a sentence.
`option_text` populated only for the scale endpoints (resp=1: "Very slightly or not at
all"; resp=5: "Extremely") and left blank for resp 2-4 — the paper discloses only the two
endpoint anchors for this 5-point scale, not verbal labels for intermediate points (same
pattern as `gart`'s 9-point scale and the `firstborn_personality` model example's
unlabeled midpoints). `correct_response` left blank throughout — self-report gratitude
measure, no scoring key.

## has_bare_integer_items
FALSE, confirmed. All 3 `item` values in the live data are named/labeled codes
(`gac_1`, `gac_2`, `gac_3`), not bare integers — each mapped directly and unambiguously
to a psychotools help-page variable name and its literal text; no position-based
reconstruction was needed.

## Derived vs. directly-read values
All `item_text` values are directly-read literal transcriptions from the psychotools help
page. `instructions` is a direct quote/light combination of two adjacent sentences from
the paper's body text (the response-scale definition and the stated timeframe) — not
paraphrased or reworded, just concatenated since both apply instrument-wide and neither
is section- or item-specific. `option_text` for resp=1/5 are direct quotes of the paper's
stated Likert anchors. `instrument` name ("Gratitude Adjective Checklist (GAC;
McCullough, Emmons, & Tsang, 2002)") is directly read from the paper's own naming/citation
of the source instrument, not invented. Nothing in this table was derived/inferred from
indirect cues; all 3 items had directly disclosed literal text.

## Ambiguities
None of consequence. One minor judgment call: the GAC's timeframe phrase ("during the past
few weeks") is study-specific per the paper's own framing (the instrument is described as
usable with a variable timeframe depending on instructions given), so it was placed in
`instructions` rather than treated as a fixed instrument-level fact — this matches how the
skill's boundary rule treats task-level framing text.

## Items not extracted
None — all 3 ground-truth items were extracted with literal item text, and the full 1-5
resp range was covered with anchor text at both endpoints. Validated: `unique(item)` and
`unique(resp)` (values, ignoring numeric/integer class) both match exactly against
`.gt_psychotools_gratitude_gac.rds`.

## Validation result
EXACT MATCH. `sort(unique(item))` == `c("gac_1","gac_2","gac_3")` for both candidate and
ground truth; `sort(unique(resp))` == `1:5` for both. No discrepancy to log in
`pending_index_notes.csv`.
