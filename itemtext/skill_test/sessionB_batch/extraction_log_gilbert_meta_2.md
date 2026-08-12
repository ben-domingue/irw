# Extraction log: gilbert_meta_2

## Source used

- **Repo processing script**: `data/content_literacy_intervention.R` — found by grepping `data/`
  for "gilbert" and "kim". This script reads `item_response_public.dta` (Stata file from
  Harvard Dataverse doi:10.7910/DVN/LAWFFU) and does:
  ```r
  df <- df |> select(s_id, s_q_num, s_correct, s_itt_consented) |>
    rename(item = s_q_num, resp = s_correct, treatment = s_itt_consented)
  ...
  save(df, file="content_literacy_intervention.Rdata") ##this was updated to 'gilbert_meta_2'
  ```
  This is the authoritative link confirming `gilbert_meta_2`'s `item` column is the raw
  data's `s_q_num` (question number, 1–20) and `resp` is `s_correct` (0/1 scored correct/
  incorrect) — i.e. item numbering is the actual assessment item order used by the study
  authors, not an artifact of processing.
- **Dictionary row**: Reference = Kim, Burkhauser, Relyea, Gilbert, Scherer, Fitzgerald,
  Mosher, & McIntyre (2023), *A longitudinal randomized trial of a sustained content
  literacy intervention from first to second grade: Transfer effects on students' reading
  comprehension*, JEP 115(1), 73. Dataverse doi:10.7910/DVN/LAWFFU.
- **Gilbert, J. B. (2022)**, *Estimating Treatment Effects with the Explanatory Item
  Response Model*, EdWorkingPaper 22-677 (files.eric.ed.gov/fulltext/ED672207.pdf) — an
  empirical-application section reanalyzes this exact dataset (2,174 students, 30 schools,
  20 items) and states directly: *"The assessment included three reading passages followed
  by a total of 20 multiple choice items"* — cross-checked against the live `irw_fetch`
  item count of 20. Cached at `.cache/gilbert_meta_2/ED672207.pdf` / `.txt`.
- **Mosher, Burkhauser, & Kim (2024)**, *Improving Second-Grade Reading Comprehension
  Through a Sustained Content Literacy Intervention...*, JEP 116(4), 550
  (dash.harvard.edu bitstream, same MORE study/author group) — describes the same
  20-item domain-specific reading comprehension transfer measure in detail: 3 passages
  (near-transfer: sea ammonites/paleontology topic; mid-transfer: Pompeii archeology;
  far-transfer: genealogists), 7 items per near- and mid-transfer passage, 6 items on the
  far-transfer passage (one item dropped for poor item function from an original 7, citing
  Kim et al. 2022), 3 answer choices per item with one correct answer, Cronbach's alpha
  .78. Cached at `.cache/gilbert_meta_2/second_grade_670bb198.pdf` / `.txt`.
- Attempted but did not yield item-level text: main JEP 2023 paper PDF (cepr.harvard.edu
  copy returned HTTP 403/Access Denied to both `curl` and `WebFetch`); Harvard Dataverse
  dataset file listing page (`dataset.xhtml?persistentId=...`) returned no fetchable
  content via WebFetch — no codebook/readme file could be enumerated or inspected this way.
  A related but distinct Kim et al. Grade-1-only pilot report (ED662409.pdf, "Improving
  Reading Comprehension, Science Domain Knowledge...") was also fetched and checked; it
  describes a different outcome measure (MAP) for a different (Grade 1 only, N=674) study
  and was not used as a source for item content.

## Structure discovered

- 20 scored items (`item` = raw `s_q_num`, values 1–20), each binary-scored `resp` ∈ {0,1}
  (`s_correct`) — matches `irw_fetch(gilbert_meta_2)` exactly (20 items, resp {0,1}).
- Underlying instrument: a researcher-designed, non-standardized 20-item multiple-choice
  (3 options each) reading comprehension "transfer" assessment, administered at the end of
  the Grade 2 intervention year, built around 3 reading passages testing near-, mid-, and
  far-transfer of domain knowledge taught during the MORE intervention (paleontology →
  sea-ammonite passage → Pompeii-archeology passage → genealogist passage).
- Passage/item split per the companion paper: 7 near-transfer items + 7 mid-transfer items
  + 6 far-transfer items = 20. This confirms the *count* structure but **not** which of the
  1–20 item numbers belong to which passage or in what order they were numbered/administered
  — no source located states this explicitly (see Ambiguities).

## Structure of output

Same 10-column shape as `candidate_firstborn_personality.rds` (`table, section_id, item,
instrument, instructions, section_prompt, item_text, correct_response, option_text, resp`),
one row per (item, resp) combination — 20 items × 2 resp values = 40 rows.

- `table` = `"gilbert_meta_2"` throughout.
- `section_id` = `"gilbert_meta_2_<item>"`, i.e. one trivial section per item (the SKILL.md
  fallback for "instrument has no [confirmable] testlet/passage grouping") — used
  deliberately here even though a 3-passage grouping *does* exist conceptually, because the
  item→passage assignment could not be confirmed (see Ambiguities). Not guessing a section
  boundary was judged safer than asserting one that might be wrong.
- `instrument` = one descriptive string (MORE domain-specific reading comprehension
  transfer assessment, with citations) repeated on every row.
- `instructions`, `section_prompt`, `item_text`, `correct_response`, `option_text` = `""`
  (empty string, matching the model file's convention for missing values) on every row —
  none of these literal-text fields could be recovered from any located public source.
- `resp` = `0` / `1` (integer), matching `irw_fetch` type/values exactly.

## Ambiguities

- **Item ↔ passage mapping is unresolved.** The companion paper (Mosher et al. 2024)
  confirms 7/7/6 items across 3 passages but never states which `s_q_num` values 1–20
  correspond to which passage, or whether item numbering follows passage-administration
  order (near→mid→far) or some other scheme (e.g. interleaved, or ordered by a released
  item bank). Per SKILL.md's bare-integer guidance, range/count plausibility alone is not
  sufficient validation, and no distinguishing per-item cue (numbering in a table, subscale
  labels) was found — so no section/passage assignment was encoded, rather than guessing.
- **Literal item and option text is not publicly disclosed anywhere located** — consistent
  with SKILL.md's expectation that this happens for secure/proprietary researcher-designed
  instruments. The main JEP 2023 paper (which might contain example items or an appendix)
  could not be accessed — the only located full-text copy (cepr.harvard.edu) returned
  HTTP 403 to both `curl` and `WebFetch`, and no open-access alternative (PMC, author
  repository) was found in search results.
- Whether the exact same 20-item instrument in `gilbert_meta_2` (N≈2,174 per the EIRM
  reanalysis) is identical item-for-item to the one described in Mosher et al. 2024
  (N=2,156, "at the end of the second-grade unit") is treated as highly likely but not
  proven identical — same MORE study, author group, item count (20), passage count (3),
  and topics, but the two papers report slightly different analytic-sample Ns, consistent
  with ordinary missing-data handling rather than a different instrument. Not certain
  enough to justify inventing item_text from a "probably-the-same" source description.

## Items not extracted

All 20 items: `item_text`, `option_text`, and `correct_response` are blank/NA for every
item. `item` and `resp` values are fully populated and match ground truth exactly (this is
a join-key-correct, content-incomplete extraction, per SKILL.md's "couldn't fully automate"
bucket — not a partial/dropped-item discrepancy like `fivpei_perrig_2023_attdiff`).

## OCR / image-based extraction

Not needed. All sources consulted were digitally-native, machine-readable text (Stata
`.dta` via the repo's own R script, and PDFs with an extractable text layer via
`pdftotext`/WebFetch's built-in extraction) — no image-only PDF or scanned page was
encountered, so no OCR step was required.

## Derived vs. directly-read values

- `item` (1–20) and `resp` (0/1) were **directly read** — copied verbatim from the ground
  truth (`irw_fetch`/`.gt_gilbert_meta_2.rds`), which in turn is a direct rename of the raw
  `s_q_num`/`s_correct` columns per `data/content_literacy_intervention.R` (no transformation
  of the values themselves, only a column rename).
- No item, response option, or scoring value in this output was **derived/computed** (e.g.
  no recoding, no reverse-scoring, no inferred midpoint) — item_text/option_text/
  correct_response are simply blank because no literal source text for them could be found,
  not because a value was estimated and might be wrong.

## Source type used

- **Existing repo processing script**: `data/content_literacy_intervention.R` — used to
  confirm the `item`=`s_q_num`/`resp`=`s_correct` mapping and the Dataverse source file.
- **Raw-data-file column headers** (indirectly, via the script above): `s_q_num`,
  `s_correct` from `item_response_public.dta`.
- **Paper appendix / working-paper text** (PDF, text layer extracted with `pdftotext` and
  WebFetch): Gilbert (2022) EdWorkingPaper 22-677 (empirical-application section) and
  Mosher, Burkhauser, & Kim (2024) JEP paper (Method section) — used for instrument
  structure (3 passages, 20 items, 7/7/6 split, 3-option MC, topics/passage names).
- **Website codebook / Dataverse file listing**: attempted, not usable — no file listing or
  codebook content was retrievable via WebFetch for the Dataverse dataset page.
- Main JEP 2023 paper PDF (the table's actual Reference): located (cepr.harvard.edu) but
  inaccessible (HTTP 403 to curl and WebFetch) — not used as a direct source; the two
  companion documents above (same dataset/study family, one of them a direct reanalysis of
  this exact file) were used instead.

## Bare-integer validation check (has_bare_integer_items = TRUE)

Per SKILL.md: range/count plausibility alone ("a 20-item 0/1 test exists") is not
sufficient for bare-integer items. Checks actually run:

1. **Provenance check (passed)**: traced `item` back to its literal source-data column
   (`s_q_num`) via the repo's own processing script, confirming `item` values 1–20 are the
   assessment's *actual* question-number field in the raw data, not an index assigned
   during IRW processing (e.g. not `row_number()` over columns in arbitrary order).
2. **Item-count cross-check (passed)**: paper-stated item count (20, per both Gilbert 2022
   and Mosher et al. 2024) matches `irw_fetch(gilbert_meta_2)`'s 20 unique items exactly.
3. **Resp-value cross-check (passed)**: paper states the outcome is scored right/wrong
   (multiple-choice with one correct answer per item) — consistent with the live data's
   `resp` ∈ {0,1} and with `s_correct` as the source column name.
4. **Item→passage/order cross-check (not resolved — logged, not guessed)**: attempted to
   further confirm which specific items 1–20 belong to which of the 3 passages (the
   "distinguishing wording/position cue" SKILL.md asks for), but no source located states
   this. Per SKILL.md, this was left unassigned (all items in their own trivial
   `section_id`) rather than guessed.

**Overall result: item and resp columns validate exactly against ground truth (both
`identical()` after fixing an integer/double type mismatch on `resp`); item-level text
content could not be recovered from any accessible public source and is left blank,
logged in `pending_index_notes.csv`.**
