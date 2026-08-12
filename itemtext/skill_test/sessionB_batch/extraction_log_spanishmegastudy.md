# Extraction log: spanishmegastudy

## Source used
Figshare article 10.6084/m9.figshare.14073899 ("Supplementary files for The predictors of
general knowledge: Data from a Spanish megastudy"). The Figshare REST API
(`https://api.figshare.com/v2/articles/14073899`, used because the HTML article page
returned HTTP 403 to a plain fetch) listed three files: `answers.csv` (~111MB, raw
response-level data — not needed, ground truth already derived from this), `items.csv`
(~170KB, the item bank), `users.csv` (not needed). Downloaded `items.csv` directly via
`https://ndownloader.figshare.com/files/26562689`, cached at
`.cache/spanishmegastudy/items.csv` (and cleaned copy `items_clean.rds`).

Also fetched the accepted-manuscript PDF from the corresponding author's site
(`https://jonandoni.com/wp-content/uploads/2021/07/buades-sitjar-et-al-brm-accepted-2021.pdf`,
cached at `.cache/spanishmegastudy/paper.pdf`, text-extracted to `paper.txt` via
`pdftotext -layout`) to get the literal participant instructions and confirm the
item-identifier scheme (see below).

## Structure discovered
`items.csv` is a semicolon-delimited file with one row per item: `id_item, category,
question, correct_answer, incorrect_answer_a, incorrect_answer_b, incorrect_answer_c,
visualizations`. 1270 rows, `id_item` running 1..1270 with no gaps or duplicates.

Text fields used a broken escaping convention — internal double quotes were exported as
literal backslash characters instead of `\"` or `""` (e.g. `\El Coloso de Rodas\` should
read `"El Coloso de Rodas"`). Confirmed the pattern is consistent (167 rows affected, all
with an even number of backslashes, i.e. always paired) and normalized by replacing
literal `\` with `"` in `question`/`correct_answer`/`incorrect_answer_*`. This is a
formatting cleanup of the source's own text, not content alteration.

## Bare-integer item validation
`items.csv$id_item` is not a presentation-order index requiring reconstruction — it is
the megastudy's own persistent item identifier. Confirmed via the paper text (p.14, data
description section): *"answers.csv, which contains the information of the 2,894,040
responses from the participants in each question — i.e., their identifier, order of
[presentation,] ... "* and the mixed-effects model section: *"the participant's ID and
the item's ID were used as random effects ... (1| id_user) + (1| id_item)"*. The paper
explicitly names `id_item` as the item identifier used throughout `answers.csv`
(the response-level file the ground truth was built from) and `items.csv` alike, not an
arbitrary row order. `unique(items.csv$id_item)` == `1:1270`, an exact set match against
ground-truth `unique(item)`. This is a direct ID-field match, not an order/position
inference — the strongest form of the check the skill asks for.

## Structure of output
- One `instrument` row: "Spanish General Knowledge Megastudy: 1,270-item multiple-choice
  general-knowledge trivia quiz (Buades-Sitjar et al., 2022)".
- `instructions` quoted (near-verbatim, trimmed of the trailing sentence about post-game
  feedback which is not task instructions) from the paper's Procedure section, p.13-14:
  the literal instructions participants saw before the 60-question game (translated to
  English in the paper itself — the live game was presumably in Spanish, but this is the
  only instructions text the paper discloses).
- One `section_id` per item (`spanishmegastudy_<id_item>`), `section_prompt` blank — each
  question is an independent multiple-choice item with no shared passage/testlet
  structure, so per the skill's guidance a trivial per-item section was used rather than
  grouping by `category` (the item bank's topic label, e.g. "arquitectura", "biologia" —
  considered as a section grouping but rejected because it is a topical tag, not a shared
  *prompt* text, and inventing a `section_prompt` from a bare category label would not be
  a literal transcription).
- `item_text` = literal `question` field (Spanish, as presented to participants).
- `correct_response` = literal `correct_answer` field.
- `option_text`/`resp`: the live IRW data's `resp` is binary (0/1, "hit"/error per the
  paper's own scoring), not the specific one-of-four option chosen — the raw
  `answers.csv` records correctness, not which distractor was picked. `option_text` was
  therefore set to minimal binary labels "Incorrect"/"Correct" matching resp 0/1,
  rather than trying to force the four multiple-choice answer texts onto a two-valued
  `resp`. The three incorrect-answer-option texts (`incorrect_answer_a/b/c`) were not
  used in the output for this reason — they exist in the source but have no valid `resp`
  value to attach to under the binary hit/error coding actually used in the live data.

## OCR / image-based extraction
Not needed. `items.csv` is a structured, machine-readable CSV supplementary file
containing all 1270 question/answer texts as plain UTF-8 text fields — no OCR or
image-based reading was required anywhere in this extraction.

## Derived vs. directly-read values
No values were derived or computed. `item` (`id_item`), `item_text` (`question`), and
`correct_response` (`correct_answer`) were read directly from `items.csv`. `resp` values
(0/1) and their `option_text` labels ("Incorrect"/"Correct") are a direct restatement of
the live data's own coding (confirmed 0/1 from ground truth and from the paper's
description of `answers.csv`'s "hit"/error scoring) — not inferred or computed from
anything else. `instructions` and `instrument` are literal/near-literal quotes from the
paper text, not paraphrases.

## Source type used
Spreadsheet item bank (`items.csv`, a Figshare-hosted CSV supplementary data file) for
item/answer text, plus a paper appendix/methods-section PDF (author's self-archived
accepted manuscript) for the literal instructions text and the `id_item` identifier
confirmation.

## Ambiguities
- The paper's instructions text is the English translation given in the manuscript; the
  live study almost certainly ran in Spanish (all item/answer text is Spanish), but no
  Spanish-language version of the instructions screen was found in the supplementary
  files or paper, so the English translation is what's recorded.
- `option_text` "Incorrect"/"Correct" is a minimal descriptive label for the binary
  `resp` coding, not verbatim source text (the source never displays those words to
  participants — this is a scoring-key label, matching the same approach used for
  binary-scored items elsewhere in this project).

## Items not extracted
None. All 1270 ground-truth items (`item` = "1".."1270") were matched and extracted with
full `item_text`/`correct_response` text; both ground-truth `resp` values (0, 1) covered.
Validated with an exact set-equality check (`setequal`) of `unique(item)` and
`unique(resp)` between the candidate output and `.gt_spanishmegastudy.rds` — both passed.
No entry was added to `pending_index_notes.csv` since there is no discrepancy to log.
