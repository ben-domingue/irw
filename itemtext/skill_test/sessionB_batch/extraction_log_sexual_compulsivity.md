# Extraction log: sexual_compulsivity

## Source used
Dictionary row's URL for data (`http://openpsychometrics.org/_rawdata/`) + Reference
filename gave `http://openpsychometrics.org/_rawdata/SCS.zip`, downloaded directly
(same pattern as `firstborn_personality`/`fisher_temperment`). Cached at
`.cache/sexual_compulsivity/SCS.zip`, unzipped to `.cache/sexual_compulsivity/SCS/`
containing `data.csv` (raw responses, columns `Q1`..`Q10`,`score`,`gender`,`age`) and
`codebook.txt` (literal item text, 4-point response scale anchors, and a note that
`score` is a computed sum column, not a live item).

This is the openpsychometrics.org online administration of the **Sexual Compulsivity
Scale** (SCS; Kalichman & Rompa, 1995) — a well-known, publicly documented 10-item
sexual-compulsivity measure.

## Structure discovered
Ground truth: `item` = `"1"`..`"10"` (bare integers), `resp` = `1,2,3,4`. Codebook
lists exactly 10 questions, `Q1`..`Q10`, each with full literal text, followed by a
4-point Likert key: `1=Not at all like me, 2=Slightly like me, 3=Mainly like me,
4=Very much like me`. `data.csv`'s column order is `Q1,Q2,...,Q10,score,gender,age` —
`score` (`SUM(Q1..Q10)`) and `gender`/`age` are covariates/derived, not live items, and
are correctly absent from the ground-truth `item` set. Item count (10) and resp range
(1-4) both match ground truth exactly.

## Bare-integer validation check
`has_bare_integer_items=TRUE`, so per the skill, range-plausibility alone isn't
sufficient — position/order must be cross-checked. Ran: compared the codebook's
declared item order (`Q1`..`Q10`, in the order printed in `codebook.txt`) against the
column order of `Q1`..`Q10` in `data.csv` from the same zip. **They match exactly** —
`Qn` in the codebook is column `n` in the raw data, which is the standard
openpsychometrics.org convention (also confirmed working this way in
`firstborn_personality`/`fisher_temperment`). Since the live IRW `item` values are
bare integers `1`..`10` with no other distinguishing metadata, and this dataset has
only one flat block of items (no subscales, no reverse-scored subset called out), the
straightforward `item == Qn`'s numeric suffix mapping is the only defensible
interpretation and is corroborated by the direct column-position match. Result: PASS.

## Structure of output
Single section (`sexual_compulsivity_1`, blank `section_prompt` — no testlet/passage
grouping, flat 10-item Likert scale). One `instructions` string quoted (near-verbatim,
trimmed of the "The questions were rated on a likert scale (...)" trailing colon) from
the codebook, applying to the whole instrument. `item_text` is the literal Q1-Q10
sentence for each item, kept terse (single first-person statement, no expansion).
`option_text` for all 4 scale points taken directly from the codebook's parenthetical
key. `correct_response` blank throughout (self-report personality-style scale, no
scoring key/correct answer).

## OCR / image-based extraction
Not needed. Both the item text and the response-scale anchors came directly from a
plain-text `codebook.txt` inside the downloaded zip — no PDF, scanned image, or manual
transcription from a rendered page was involved anywhere in this extraction.

## Derived vs. directly-read values
None of the extracted fields were derived or computed — every `item_text` and
`option_text` value is a direct, literal copy from `codebook.txt`. The only "derived"
value skipped over deliberately was `score` (`SUM(Q1..Q10)`), which is explicitly a
computed column per the codebook and correctly excluded from item text since it is not
one of the 10 live items in the ground-truth data.

## Source type used
Raw-data-file column headers + accompanying website codebook (`codebook.txt` bundled
in the same zip as the raw CSV at the dataset's own openpsychometrics.org URL) — no
separate PDF manual or journal paper/appendix was needed or consulted.

## Ambiguities
None of substance. The mapping from bare integer `item` to `Qn` question text is
unambiguous given the exact column-order match between codebook and raw data file.

## Items not extracted
None — all 10 ground-truth items extracted and validated. `unique(item)` and
`unique(resp)` from `candidate_sexual_compulsivity.rds` match
`.gt_sexual_compulsivity.rds` exactly (item: `"1".."10"`; resp: `1,2,3,4`, numeric
value set identical — the only mismatch when comparing with `identical()` directly was
an integer-vs-double type difference in the `resp` column, not a value discrepancy).
