# Extraction log: gilbert_meta_12

## has_bare_integer_items

**FALSE**, per the dictionary row. `item` values (`sci1`..`sci12`, `ss1`..`ss12`) already carry
semantic labels (subject-domain prefix + item number), so no bare-integer-to-item-content
reconstruction was needed -- the domain prefix directly identifies which 12-item subtest
(science vs. social studies) each item belongs to. The within-domain 1-12 ordering is still an
assumption (see Ambiguities) but is a much weaker inference than the bare-integer case this
skill's guidance is primarily written for.

## Source used

- **Dictionary row**: Reference = Kim, J. S., Relyea, J. E., Burkhauser, M. A., Scherer, E., &
  Rich, P. (2021). *Improving elementary grade students' science and social studies vocabulary
  knowledge depth, reading comprehension, and argumentative writing: A conceptual replication.*
  Educational Psychology Review, 33(4), 1935-1964. Harvard Dataverse doi:10.7910/DVN/HQEMN6.
- **Index-sheet dictionary description** (`tags/tagging_joao/data/IRW Data Dictionary - data
  index.csv`): `gilbert_meta_12` = "Vocabulary test following a literacy intervention for grade 2
  students" (and `gilbert_meta_11` = same wording for grade 1). This confirmed *which* of the
  paper's four vocabulary subtests (Grade 1 Science, Grade 1 Social Studies, Grade 2 Science,
  Grade 2 Social Studies) applies to this specific table before any item text was pulled.
- **Repo processing script** `data/gilbertmeta.R`: confirms `gilbert_meta_12` was produced by a
  generic batch post-processing routine (`irw_clean()` over a `datasets` list from an unrelated
  private `.Rdata` file, `bd addendum` section renaming `time`->`wave` and numbering outputs
  `gilbert_meta_<n>`) rather than a bespoke per-dataset script -- there is no dataset-specific
  code in this repo that documents which raw source column `sci1`..`sci12`/`ss1`..`ss12` came
  from. This is the same situation as `gilbert_meta_2`'s log (no per-table processing script
  found) and different from tables like `gilbert_meta_102through104.R`, which had one.
- **Harvard Dataverse dataset page** (`dataset.xhtml?persistentId=doi:10.7910/DVN/HQEMN6`):
  reachable at the HTTP level (curl/DataCite returned 200/202, no outright WAF block observed
  this time -- unlike `gilbert_meta_2/38/74/100/58` in this same batch), but `curl` and
  `WebFetch` both returned an **empty body** for the actual dataset/file-listing page, so no
  file list, codebook, or questionnaire could be enumerated from it directly.
- **DataCite metadata API** (`api.datacite.org/dois/10.7910/DVN/HQEMN6`, not WAF-affected):
  confirmed the dataset title ("Replication Data for: Improving Elementary Grade Students'...")
  and abstract ("dataset and a script to replicate analyses") but exposed no file list.
- **ERIC full-text PDF `ED640496.pdf`**: fetched via a Google-indexed hit, turned out to be a
  *different, unrelated* paper (Hwang, Cabell, & Joyner, 2023, "Does Cultivating Content
  Knowledge during Literacy Instruction Support Vocabulary and Comprehension...", Reading
  Psychology) that merely cites Kim et al. (2021) in its reference list -- checked and discarded,
  not used as a source. Cached at `.cache/gilbert_meta_12/ED640496.pdf`/`.txt` for the record.
- **The actual target paper, open-access submitted-version PDF via Unpaywall**
  (`api.unpaywall.org` resolved a CC-BY Harvard DASH copy at
  `https://dash.harvard.edu/bitstreams/1d8ee7c1-ebc7-479c-9c01-761d16b5a516/download`,
  handle `dash.harvard.edu/handle/1/42739746`) -- **this is the paper itself**, confirmed by
  title/citation block matching the dictionary Reference exactly. Cached as
  `.cache/gilbert_meta_12/kim2021_epr.pdf`/`.txt`. The Methods section ("Student Measures" ->
  "Networks of vocabulary knowledge depth", lines ~969-1000 of the extracted text) describes the
  semantic-association vocabulary task and states item text/scoring live in "Appendix S-C"/
  "Appendix S-D" of the **supplemental on-line materials** (not included in this submitted-version
  PDF body).
- **Springer ESM (Electronic Supplementary Material) file, fetched directly** at
  `https://static-content.springer.com/esm/art%3A10.1007%2Fs10648-021-09609-6/MediaObjects/10648_2021_9609_MOESM1_ESM.docx`
  (HTTP 200, a `.docx`) -- **this is the actual supplemental appendix**, containing Appendix S-A
  through S-E, including S-C ("Student Assessment Instruments" -- full vocabulary-item text for
  all four Grade x Domain subtests) and S-D (the 0-4 point scoring rubric). Extracted with
  `pandoc -t plain`. Cached as `.cache/gilbert_meta_12/supp1.docx`/`.txt`
  (and `supp1_extract/` for the raw docx XML, used to check for bold/highlight formatting that
  might mark correct answers -- none was found; see Ambiguities).
- A second ESM candidate URL (`MOESM1_ESM.pdf`, guessed by analogy) returned HTTP 403 and was not
  used -- the `.docx` above was sufficient and is the actual ESM1 file.

## Structure discovered

Appendix S-C ("Student Assessment Instruments") contains four parallel 12-item vocabulary
subtests, one per Grade x Domain combination, each formatted identically: a target word, a
practice-example 4-option row (constant across all four subtests: book/fox/classroom/boat, not
scored), then 12 numbered items each phrased "Circle two words that go with [word]." followed by
a 4-word option table. Per the dictionary description, `gilbert_meta_12` = the **Grade 2** pair
of subtests (Science + Social Studies).

- **Grade 2 Science Vocabulary** (12 target words, in the appendix's presentation order):
  carnivore, extinct, fossil, hypothesis, brutal, evidence, theory, hunter, organism, trait,
  paleontologist, reptile.
- **Grade 2 Social Studies Vocabulary** (12 target words, in order): inventor, hire, experiment,
  approve, prototype, establish, manufacture, discrimination, laboratory, engineer, foundation,
  ingenious.
- Each item's 4 literal answer-choice words were also recovered (e.g. item 1/carnivore:
  fruit / care / meat / prey) -- see Ambiguities for why these were **not** placed in the
  `option_text` field.
- Per the main paper body (Student Measures section): each set of 12 items included 7
  domain-specific taught words + 5 untaught-but-related words; task = "circle two words that go
  with" the target; **scored 0 to 4** per item (partial credit for 1-2 correct/incorrect
  selections -- Appendix S-D's Table S2 gives the full 0/1/2/3/4 rubric based on how many of the
  student's selected words were from the correct pair). Cronbach's alpha .91 (science) / .90
  (social studies).
- **This directly conflicts with the live IRW data's `resp` domain, which is binary {0,1}, not
  the paper's stated 0-4 scale.** See Discrepancies below -- this is the single most important
  finding of this extraction and is *not* glossed over.

## Discrepancies (Step 5/6b — logged, not forced)

- **Scoring scale mismatch**: source paper explicitly states each of these items is "scored 0 to
  4" (Appendix S-D gives the full rubric). Ground truth `resp` for `gilbert_meta_12` is binary
  `{0, 1}` only. The live IRW table is evidently a **dichotomized derivative** of the paper's
  0-4 partial-credit score (e.g. possibly full-credit-only=1 vs. anything-else=0, or some other
  threshold), consistent with how `gilbert_meta_2` and other tables in this family show similar
  simplification relative to the richer scoring described in the source papers. **No source
  located states the exact dichotomization rule**, so `option_text` (which would normally encode
  the resp<->option correspondence) was deliberately left blank rather than guessed -- populating
  it would require asserting, e.g., "resp=1 means both selected words were correct," which is
  plausible but not confirmed by any accessible document.
- **`correct_response` left blank for all items**: the appendix's answer-choice tables have no
  bold/underline/highlight distinguishing the two correct words from the two distractors (checked
  the raw docx XML run-properties directly -- all four options in every item share identical
  formatting). Semantic plausibility alone (e.g. guessing "meat" and "prey" are the intended
  matches for "carnivore") was **not** used to fill this field, per this skill's fabrication
  guardrail -- even though it would likely be correct for many items, it is a judgment call, not
  a transcription, and the task explicitly says not to substitute inference for literal source
  text when the source itself doesn't state it.
  - Partial corroboration, noted but not acted on: `pending_index_notes.csv`'s existing
    `gilbert_meta_100` entry (a different table, different Dataverse DOI, same MORE
    grade-2-science semantic-association instrument reused across studies) records a worked
    example from a *different* paper (Gilbert et al. 2025) giving target="carnivore",
    options=fruit/care/meat/prey, correct=meat+prey -- which matches this extraction's
    independently-recovered option set for `sci1` exactly. This cross-confirms the option set is
    the right one, but it's still only one item's answer key from a different source, so
    `correct_response` remains blank throughout for consistency rather than partially filled.

## Structure of output

Same 10-column shape as `candidate_firstborn_personality.rds` (`table, section_id, item,
instrument, instructions, section_prompt, item_text, correct_response, option_text, resp`), one
row per (item, resp) combination -- 24 items x 2 resp values = 48 rows.

- `table` = `"gilbert_meta_12"` throughout.
- `section_id` = `"gilbert_meta_12_sci"` for `sci1`..`sci12`, `"gilbert_meta_12_ss"` for
  `ss1`..`ss12` -- a real, source-confirmed grouping (the two Grade-2 subtests are literally
  presented as separate labeled Parts in Appendix S-C), not the SKILL.md trivial-fallback case.
- `instrument` = one descriptive string identifying the semantic-association / vocabulary
  knowledge depth measure and citing the paper + Appendix S-C, repeated on every row.
- `instructions` = `""` (blank) on every row -- no distinct table-wide directions sentence exists
  separately from the per-item stem in the source (unlike the argumentative-writing sections in
  the same appendix, which do have an explicit "Directions: ..." paragraph). See Ambiguities.
- `section_prompt` = the literal Part header from Appendix S-C ("PART I. Grade 2 Science
  Vocabulary." / "PART I. Grade 2 Social Studies Vocabulary."), constant within each section_id.
- `item_text` = literal, terse transcription of each item's stem, e.g. "Circle two words that go
  with carnivore." -- matches the source's own terseness (one short imperative sentence per item,
  no added explanation).
- `correct_response` = `""` (blank) for all rows -- see Discrepancies.
- `option_text` = `""` (blank) for all rows -- see Discrepancies (scoring-scale mismatch means the
  resp<->option correspondence can't be stated without guessing).
- `resp` = `0` / `1` (integer), matching `irw_fetch`/ground-truth type and values exactly.

## Ambiguities

- **Within-domain item-number-to-word ordering** (`sci1`=carnivore, `sci2`=extinct, ... in
  appendix presentation order) is assumed but not independently confirmed against a raw-data
  codebook or variable-label file (none was found for this specific DOI/dataset -- the Dataverse
  file listing was unreachable, see Source section). This is a reasonable, low-risk assumption
  (paper presents exactly 12 items per domain in a fixed numbered list, and the table's own
  `sci`/`ss` prefix + count already independently confirms domain and count), but it is weaker
  than a script-confirmed mapping like `gilbert_meta_2`'s `s_q_num`. Flagged here rather than
  silently assumed.
- **No literal general "instructions" text found** distinct from the per-item stem. The Methods
  section of the main paper paraphrases the task ("students were prompted to 'circle two words
  that go with' the target word") but this is authors' narrative description, not verbatim
  student-facing instructions -- the literal instruction is embedded in each item's own stem
  ("Circle two words that go with X."), so a separate `instructions` value was not fabricated.
- **`option_text`/`correct_response` intentionally left blank** -- see Discrepancies section
  above for the two independent reasons (scoring-scale mismatch, no marked answer key in source).

## OCR / image-based extraction

Not needed. All sources were digitally-native, machine-readable text: the DASH-hosted submitted
manuscript PDF (`pdftotext -layout`) and the Springer ESM `.docx` (extracted via `pandoc -t
plain`, and cross-checked against the raw docx XML for formatting cues). No scanned/image-only
document was encountered.

## Derived vs. directly-read values

- `item` (`sci1`..`sci12`, `ss1`..`ss12`) and `resp` (0/1) were **directly read** from
  `.gt_gilbert_meta_12.rds` / ground truth -- copied verbatim, not transformed.
- `item_text` values are **directly read** (literal transcription) from Appendix S-C of the
  Springer ESM `.docx` -- not paraphrased or expanded.
- `section_id`/`section_prompt` assignment (sci vs. ss) is a **direct read** of the item's
  `sci`/`ss` prefix mapped onto the paper's own "PART I. Grade 2 Science/Social Studies
  Vocabulary" headers -- not derived/guessed.
- The within-domain 1-12 item ordering is a **light inference** (appendix list order = data
  item-number order) -- see Ambiguities; not from a directly-read source-data variable name.
- `correct_response` and `option_text` were **deliberately left blank rather than derived** --
  the raw 4-option text per item *was* recovered but not entered into `option_text`, because doing
  so would require asserting an unconfirmed resp<->option correspondence (see Discrepancies). No
  value in the output was estimated/computed and might silently be wrong; everything populated is
  either a direct read or explicitly flagged as an assumption.

## Source type used

- **Dictionary/index-sheet row** (table description) -- used to disambiguate which of the paper's
  four vocabulary subtests applies to this specific `gilbert_meta_12` table (Grade 2, not Grade 1).
- **Repo processing script** (`data/gilbertmeta.R`) -- confirmed no bespoke per-table item mapping
  exists in this repo; the table was produced by a generic batch export routine.
- **Dataverse dataset page / DataCite metadata API** -- attempted; no usable file listing.
- **Paper full text** (open-access CC-BY submitted-version PDF, resolved via the Unpaywall API,
  hosted on Harvard DASH) -- used for the Methods description of the task, scoring scale, and
  pointer to the appendix.
- **Journal Electronic Supplementary Material (ESM), fetched directly from Springer's static
  content server as a `.docx`** -- this is the primary, load-bearing source: it contains the
  literal item text (Appendix S-C) and the scoring rubric (Appendix S-D) that made this
  extraction possible.

## Items not extracted (partially)

All 24 items: `item_text` is fully populated and literal. `option_text` and `correct_response`
are blank/NA for every item -- not because the raw option text/answer key doesn't exist (it does,
in Appendix S-C, but see Discrepancies for why it wasn't safe to encode without guessing the
resp<->option correspondence or the correct-pair marking). `item` and `resp` values are fully
populated and match ground truth exactly. This is a **join-key-correct, item-text-complete,
scoring-detail-incomplete** extraction -- a stronger outcome than `gilbert_meta_2`'s (which had no
recoverable item_text at all) but still not a full 100%-field extraction, per SKILL.md's explicit
allowance for partial/honest extractions.

## Validation result

`identical(sort(unique(candidate$item)), sort(unique(gt$item)))` = TRUE (24 items).
`identical(sort(unique(candidate$resp)), sort(unique(gt$resp)))` = TRUE (`{0, 1}`).
**Exact match** on both required validation dimensions.
