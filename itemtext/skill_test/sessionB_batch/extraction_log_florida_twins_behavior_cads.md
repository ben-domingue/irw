# Extraction log: florida_twins_behavior_cads

## Source type used
Reused the already-cached and already-converted source from the prior (non-batch)
session's `florida_twins_behavior_rcads` extraction: `Behavior and Environment Survey
Codebook` (Schatschneider, Lonigan & Taylor, 2021, LDbase,
http://ldbase.org/documents/c4669c5b-9853-45be-a33f-9dff7102de20), the same document
`tables.csv`'s Reference/URL fields point to for this table. Did not refetch from
LDbase. Cached files reused from `itemtext/skill_test/sessionB/.cache/
florida_twins_behavior_rcads/codebook.doc` / `codebook.txt`. Source type: a Word-doc
survey codebook (not a journal paper), containing verbatim instrument text and
checkbox-table item layouts, transcribed to plain text via
`libreoffice --headless --convert-to txt`.

## OCR / image-based extraction
No OCR was needed — this is a born-digital Word document (`.doc`), not a scanned image,
so text extraction was via format conversion (LibreOffice), not OCR. However, the
`.txt` conversion cached from the prior RCADS session **lost the response-scale anchor
labels** for this table's CADS-Parent section: the plain-text dump showed only bare
column headers `1  2  3  4` with no visible label text, because the anchor labels sat in
a merged/nested HTML-table cell that the `.txt` filter collapsed. To recover the labels,
re-converted the same cached `codebook.doc` to `.html` (`libreoffice --headless
--convert-to html`), which preserved the table cell structure, and confirmed the CADS —
Parent Version item blocks are headed by the same anchor labels used elsewhere in this
codebook for CADS-family scales: `NOT AT ALL` (1), `JUST A LITTLE` (2), `PRETTY MUCH/
PRETTY OFTEN` (3), `VERY MUCH/VERY OFTEN` (4) — verified this is not a guess/reuse from
the Youth-version block by finding the literal repeated header table on the Parent
Version's own pages (this header block repeats before every ~8-item page, e.g. before
items 1-8, 9-18, 19-28, etc., each time showing the same four labels). Item stems
themselves were legible without this re-conversion; only the anchor labels required it.

## Investigation: CADS vs. RCADS relationship
The two sibling tables are **genuinely different instruments sharing this one codebook
document**, not the same scale under different naming. The codebook's own table of
contents and section headers make this explicit:
- `RCADS` = Revised Child(ren's) Anxiety and Depression Scale (Chorpita et al., 2000) —
  clinical anxiety/depression symptom-frequency scale. This is `florida_twins_behavior_
  rcads` (94 items = 47 self + 47 parent, extracted in the prior session).
- `CADS` = Child and Adolescent Dispositions Scale — a **temperament/personality**
  instrument (Prosociality/Sympathy, Respect for Rules, Sociability, Negative
  Emotionality, Daring, and — parent-version-only — Positive Emotionality facets), with
  a Youth self-report form (`cadsyv[#]`, 57 items) and a separate Parent form
  (`cads_[#]`, 57 items, codebook section "CADS – Parent Version", lines ~2436-2666 of
  the cached `.txt`). This table, `florida_twins_behavior_cads`, matches the ground-truth
  item names (`cads_1`...`cads_57`, underscore-prefixed) to the **Parent-report** form
  exactly — same underscore-vs-no-underscore self/parent naming convention already
  established for `rcads`/`rcads_` in the sibling table.
The 57-vs-47 item-count difference flagged in the task brief is explained by this: CADS
and RCADS are different instruments with different published item counts, not a
subset/superset of the same scale.

## Structure discovered
- All 57 ground-truth items (`cads_1`...`cads_57`) matched 1:1 by item number to the
  codebook's "CADS – Parent Version" item list (57 items, numbered 1-57 in the document
  itself).
- Single `instructions` block applies to all 57 items (quoted from the codebook page
  header, immediately before the first item): "These questions are about your twins'
  personality. When you answer these questions, please think about the last 12 months
  and check the box that you feel best describes each of your twins."
- No testlet/passage grouping — one `section_id` (`florida_twins_behavior_cads_1`) with
  blank `section_prompt`, per the skill's rule for instruments without shared-context
  item groups.
- `resp` 1-4 maps onto the instrument's own literal anchor labels: 1=NOT AT ALL,
  2=JUST A LITTLE, 3=PRETTY MUCH/PRETTY OFTEN, 4=VERY MUCH/VERY OFTEN (as printed
  verbatim in the codebook's repeating table header for this section — see OCR note
  above).
- `correct_response` left blank for all items — CADS is a personality/temperament
  descriptor scale with no scoring key.
- `has_bare_integer_items` is **FALSE** for this table (confirmed): ground-truth `item`
  values are semantic codes (`cads_1`...`cads_57`), not bare integers, so no
  position/order reconstruction judgment call was needed to map `item` to the
  paper's item numbering — the codebook's own item numbers (`1)`...`57)`) line up
  directly with the `_N` suffix in each `item` value.

## Derived vs. directly-read values
All `item_text` and `option_text` values were directly read/transcribed from the
codebook's literal item stems and anchor labels — none were derived/computed. One
adjacent artifact in the source worth flagging as NOT used: the codebook lists a derived
scoring variable `ncads_44` (item 44 reverse-scored: anchors relabeled `4 3 2 1` for use
in composite-score calculation, e.g. in `P_cads_neg`). This is a derived/reverse-coded
scoring variable, not a distinct ground-truth item (ground truth has no `ncads_44`
item), so it was not extracted or represented in the output — `cads_44`'s `item_text`
and `option_text` here reflect the item exactly as presented to respondents (1=NOT AT
ALL ... 4=VERY MUCH/VERY OFTEN), matching the live `resp` coding.

## Ambiguities
None of substance. Item stems for a handful of items wrap across two lines in the
source Word-table layout (e.g. item 4: "Does your child do things to help other people
his/her age / without being asked?"); reassembled these from the surrounding raw text,
same approach documented in the prior RCADS extraction log.

## Items not extracted
None — all 57 ground-truth items matched and were extracted with literal item text and
response-option labels. Validated exact `item` and `resp` set match against
`.gt_florida_twins_behavior_cads.rds` (57 items x 4 resp levels = 228 rows in
`candidate_florida_twins_behavior_cads.rds`).
