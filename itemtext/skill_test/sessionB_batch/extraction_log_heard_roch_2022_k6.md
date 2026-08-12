# Extraction log: heard_roch_2022_k6

## Source used
Dictionary row's URL for data (https://osf.io/4xzr8/) is the OSF project "HEARD Baby
Friendly Spaces" (Cox's Bazar, Bangladesh). Listed the project's `osfstorage` files via
the OSF v2 API (`https://api.osf.io/v2/nodes/4xzr8/files/osfstorage/`) rather than
scraping the JS-rendered project page (WebFetch on the OSF page itself returned only the
string "OSF" — no page content — so the API was used instead). Three files found:

- `HEARD BFS Baseline Psychometrics Limited Dataset.csv`
- `Final scales after psychometric analysis.docx`
- `HEARD BFS Baseline Questionnaire.pdf`

Downloaded the questionnaire PDF and the psychometrics docx, cached at
`.cache/heard_roch_2022_k6/HEARD_BFS_Baseline_Questionnaire.pdf` and
`.cache/heard_roch_2022_k6/Final_scales_after_psychometric_analysis.docx`. Text
extracted with `pdftotext -layout` (→ `questionnaire.txt`) and `python-docx` (paragraphs
→ `scales_docx.txt`; tables extracted separately, since python-docx's paragraph iterator
skips table cell text).

## Source type used
**Primary source: the actual administered interview instrument** (`HEARD BFS Baseline
Questionnaire.pdf`, "Version 1", dated March 13, 2021), items `KQ1a`-`KQ1f` under the
`K6+` heading (PDF pages 5-6). This is the literal interviewer script, in English, as
administered to respondents (the HEARD BFS enrolls Rohingya refugee mothers in Cox's
Bazar, but the OSF-hosted questionnaire itself is in English — no separate Bangla/Rohingya
translation document was found among the three OSF files; presumably interviewers
administered a verbal Bangla/Rohingya translation from this English source script, but
that translation isn't itself in the OSF materials).

**Secondary/cross-check source:** `Final scales after psychometric analysis.docx`, a
post-hoc scoring reference that also reproduces the K6 as a compact table (item number,
terse stem, and the 0-4 response-option columns). Used only to (a) independently confirm
item order/count and (b) cross-check the response-option wording — not as the primary
transcription source, since it's described as a psychometrics-analysis summary document,
not the fielded instrument.

## Structure discovered — item order and correspondence to ground truth
Both PDF and docx present the K6 in the same order, and it matches the standard K6 item
order:

| item (ground truth) | PDF code | Stem |
|---|---|---|
| KESS01_T1 | KQ1a | nervous |
| KESS02_T1 | KQ1b | hopeless |
| KESS03_T1 | KQ1c | restless or fidgety |
| KESS04_T1 | KQ1d | so depressed that nothing could cheer you up |
| KESS05_T1 | KQ1e | that everything was an effort |
| KESS06_T1 | KQ1f | worthless |

This is the standard published K6 item order, and it's independently confirmed by two
separate OSF documents (interview script + scoring-reference docx), so item identity is
not ambiguous despite the ground-truth `item` codes (`KESS0N_T1`) not literally appearing
in either source document (the source uses `KQ1a`-`KQ1f`, not `KESS01`-`KESS06`).

`_T1` suffix: confirmed as "Time 1" — this OSF project is titled "Baseline" (both file
names: "HEARD BFS Baseline Questionnaire.pdf", "...Baseline Psychometrics..."), consistent
with wave 1 of what the paper describes as a longitudinal Baby Friendly Spaces program
evaluation.

## Derived vs. directly-read values
- **`instructions`** — directly read, literal: "The next questions are also about how you
  have been feeling during the past 2 weeks." (precedes KQ1a in the PDF; also appears
  verbatim as the K6 section intro line in the docx). Applies to the whole K6 block, so
  placed in `instructions`, not `section_prompt` (single `section_id` used for the whole
  table — no testlet/passage grouping beyond the shared K6 framing sentence).
- **`item_text`** — directly read from the PDF interview script, trimmed to the terse
  question stem (e.g. "About how often during the past 2 weeks did you feel nervous?").
  The PDF's full script text repeats the response-option list inline in each item
  ("...would you say none of the time, a little of the time, ... or all of the time?" /
  "(IF NEC: none of the time, ...)") — this repeated option recital was NOT included in
  `item_text` since it duplicates the `option_text` rows and isn't part of the item stem
  itself (matches the terseness precedent from `firstborn_personality`, which also didn't
  fold response-scale boilerplate into `item_text`).
- **`option_text`/`resp` — DERIVED, not a direct read.** The source instrument codes
  responses 0-4 (`0=NONE of the time` ... `4=ALL of the time`, plus `77=(IF VOL) REFUSED`).
  The live ground-truth `resp` values are `1-5` (no 5-value analog of the raw `77`).
  Mapped raw→resp with a **+1 shift** (raw 0→resp 1, 1→2, 2→3, 3→4, 4→5), which is the
  standard IRW convention for converting a 0-based ordinal code to 1-based. This is an
  inference, not a value read directly off the page — flagging per the "derived value"
  requirement even though it's a very standard, low-risk transformation for a K6-style
  scale.
- **Response-option wording discrepancy between the two sources:** the PDF interview
  script's top end of scale is literally "ALL of the time"; the docx table's column
  header for the same scale point (in both the K6 table and the adjacent IDSS table) says
  "Almost all of the time". `option_text` uses the PDF's wording ("ALL of the time") since
  the PDF is the primary source (the actual administered script); this discrepancy is
  noted here rather than silently picking one.

## OCR / image-based extraction
Not applicable — the PDF is a native, digitally-typeset document (`pdftotext -layout`
extracted clean, well-formed text directly from the embedded text layer, no OCR needed).
No scanned/image-only pages were encountered.

## has_bare_integer_items
FALSE, as stated in the dictionary row — ground-truth `item` values are named codes
(`KESS01_T1`...`KESS06_T1`), not bare integers, so no position-based reconstruction of
item identity was needed beyond the item-order cross-check documented above (which was
done anyway, out of caution, since the source's own item codes `KQ1a`-`KQ1f` differ in
naming scheme from the ground truth's `KESS0N_T1`).

## Validation result
- `unique(item)` — **exact match** against ground truth (`KESS01_T1`...`KESS06_T1`).
- `unique(resp)` — **partial**: candidate produces `{1,2,3,4,5}`, matching all
  non-missing ground-truth values. Ground truth additionally contains `NA` for `resp`
  (16 of 3600 rows, spread thinly across items KESS02/03/04/05/06 — 1, 2, 6, 5, 2 rows
  respectively; no NA on KESS01). Interpreted as ordinary item-level non-response
  (missing data), not a real response category requiring its own `option_text` row, so
  no row was added for it. This is a real discrepancy against a strict set-equality
  check (`setdiff` would flag `NA` as "in live data, missing from items csv") — logged
  in `pending_index_notes.csv` per Step 6b rather than fabricating an "NA = refused"
  option_text row, since the source's own `77 = REFUSED` sentinel is a distinct coded
  value that doesn't actually appear in the live `resp` set at all (the live data's `NA`
  isn't disclosed anywhere as corresponding to the source's `77`).

## Items not extracted
None — all 6 ground-truth items matched and were extracted with full item_text and all
5 non-missing resp/option_text pairs.
