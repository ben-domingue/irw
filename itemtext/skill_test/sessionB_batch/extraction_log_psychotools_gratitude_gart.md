# Extraction log: psychotools_gratitude_gart

## Source used
Two sources, cross-checked against each other:
1. R package documentation: `psychotools::YouthGratitude` help page (`?YouthGratitude`,
   installed from CRAN, `Rd2txt`'d via `tools::Rd_db("psychotools")`). This gives literal
   item wording for all 28 variables in the package's example dataset, including all 16
   GRAT-short form items (`losd_1`-`losd_6`, `sa_1`-`sa_6`, `ao_1`-`ao_4`) plus scale
   descriptions (GRAT: 1-9; GQ-6: 1-7; GAC: 1-5) and notes that `losd_1` ("Life has been
   good to me.") was dropped from the paper's factor analyses for loading lowly, but is
   still present as a raw item in the data.
2. The source paper itself: Froh, Fan, Emmons, Bono, Huebner, & Watkins (2011),
   *Psychological Assessment*, 23(2), 311-324 — open-access copy fetched from
   `https://emmons.faculty.ucdavis.edu/wp-content/uploads/sites/90/2015/08/2011_1-measuring-grat-in-youth.pdf`
   (cached at `.cache/psychotools_gratitude_gart/froh2011.pdf` /
   `froh2011.txt` after `pdftotext -layout`). Body text (p. ~710-712) states the GRAT-short
   form response format: "a Likert scale from 1 (I strongly disagree) to 9 (I strongly
   agree with the statement)." Appendix B reproduces literal item text for LOSD-Item1
   through LOSD-Item5, SA-Item1-6, and AO-Item1-4 — this matches the psychotools help text
   verbatim for the retained items, confirming the package's item wording. Appendix B's
   LOSD numbering is renumbered 1-5 (because `losd_1`/"Life has been good to me" was
   dropped from analysis and excluded from the appendix table), so the psychotools help
   page — which retains the original 1-6 numbering matching the live `item` values exactly
   — was used as the authoritative source for `item_text`, with the paper's appendix used
   only as corroboration for items 2-6 of LOSD and all of SA/AO.

## Source type used
Directly-read literal text: R package help documentation (`Rd2txt` output, a maintained,
citable source distributed by the original data contributors Jeff Froh and Jinyan Fan)
plus the open-access journal PDF's body text and appendix table, converted to plain text
with `pdftotext -layout`. No OCR was needed — both sources were native-text (Rd/PDF-text),
not scanned images.

## OCR / image-based extraction
None. The PDF was a native-text PDF (`pdftotext -layout` extracted clean text directly);
no OCR was performed and no image-based transcription was needed.

## Structure discovered
Ground truth: 16 items, `ao_1`-`ao_4`, `losd_1`-`losd_6`, `sa_1`-`sa_6`, resp 1-9. This
matches the psychotools `YouthGratitude` package's GRAT-short form columns exactly (all
16, including `losd_1` which the paper excluded from its own analyses but which is still
a live item in the IRW data). Confirmed `ao` = "Appreciation of Others", `losd` = "Lack of
a Sense of Deprivation", `sa` = "Simple Appreciation" — the three GRAT-short form
subscales, per both the package help page's Details section and the paper's Appendix B
note.

## Structure of output
Three sections (`psychotools_gratitude_gart_ao`, `_losd`, `_sa`), one per GRAT subscale.
`section_prompt` left blank for all — the subscale grouping is not a shared-passage/
testlet structure, just an organizational grouping, so there is no literal shared prompt
text to record; `section_id` is still populated per the skill's rule to always have a join
key. `instructions` is one sentence, quoted directly from the paper's Method section,
describing the 9-point response format (no separate task-framing instruction is disclosed
in the source beyond this). `option_text` populated only for the scale endpoints (resp=1:
"I strongly disagree"; resp=9: "I strongly agree with the statement") and left blank for
resp 2-8 — the source discloses only the two endpoint anchors for this 9-point scale, not
verbal labels for intermediate points, matching the terseness of the source (same pattern
used in the `firstborn_personality` model example for its unlabeled midpoints).
`correct_response` left blank throughout — this is a self-report gratitude disposition
measure with no scoring key/correct answer.

## Derived vs. directly-read values
All `item_text` values are directly-read literal transcriptions from the psychotools help
page (itself sourced from the original data contributors), cross-checked word-for-word
against the paper's Appendix B for the items it reproduces (SA-1-6, AO-1-4, LOSD-2-6).
`losd_1`'s text ("Life has been good to me.") is directly-read from the psychotools help
page only, since it is absent from the paper's own appendix table (dropped from their
factor analyses) — not derived/inferred. `instructions` is a direct quote from the paper's
body text. `option_text` for resp=1/9 are direct quotes of the paper's stated Likert
anchors. Nothing in this table was derived/inferred/reconstructed from indirect cues; all
16 items had directly disclosed literal text in at least one of the two sources.

## has_bare_integer_items
FALSE, confirmed. All 16 `item` values in the live data are named/labeled codes
(`ao_1`-`ao_4`, `losd_1`-`losd_6`, `sa_1`-`sa_6`), not bare integers, so no
position-based reconstruction of item identity was needed — each `item` value mapped
directly and unambiguously to a psychotools help-page variable name and its literal text.

## Ambiguities
None of consequence. The only minor wrinkle is `losd_1`'s absence from the paper's own
appendix/analyses (see above), resolved via the package help page as primary source since
it retains the original numbering matching the live data's `item` values.

## Items not extracted
None — all 16 ground-truth items were extracted with literal item text, and the full 1-9
resp range was covered with anchor text at both endpoints. Validated: `unique(item)` and
`unique(resp)` (values, ignoring numeric/integer class) both match
`.gt_psychotools_gratitude_gart.rds` exactly.
