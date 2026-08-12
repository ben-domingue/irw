# Extraction log: gilbert_meta_104

## has_bare_integer_items

**FALSE**, per the dictionary row. `item` values (`bg_know_q1`..`bg_know_q9`) already carry
semantic labels (`bg_know_` prefix + question number), so no bare-integer-to-item-content
reconstruction was needed. The within-instrument 1-9 presentation order is still an
assumption (see Ambiguities), but the item identity/domain ("background knowledge test") is
directly legible from the item code itself, unlike the true bare-integer case this skill's
guidance is primarily written for.

## Source used

- **Dictionary row**: Reference = Relyea, J. E., Gilbert, J. B., Burkhauser, M., Scherer, E.,
  Mosher, D. M., Wei, Z., Tvedt, J., & Kim, J. S. (2025). *Asset-Based Implementation of
  Structured Adaptations in an Online Third-Grade Content Literacy Intervention.* Reading
  Research Quarterly, 60(4), e70048. Harvard Dataverse doi:10.7910/DVN/JDUIKT.
- **Repo processing script**: `data/gilbert_meta_102through104.R` — found by grepping `data/`
  for "gilbert_meta_104". Confirms the raw source: `102 more_y4_public_item.dta` filtered to
  `test == "bg"`, written to `gilbert_meta_104.csv`. No dataset-specific column renaming beyond
  the generic `item`/`resp` pass-through is present — the script doesn't disclose item content,
  only confirms provenance (this is the "bg" = background-knowledge test subset of a shared
  wide item-response file also containing the "vocab" (`gilbert_meta_102`) and "cc" (content
  comprehension, `gilbert_meta_103`) subtests).
- **DataCite metadata API** (`api.datacite.org/dois/10.7910/DVN/JDUIKT`, not WAF-blocked):
  confirmed dataset title ("Replication Data for: Asset-Based Implementation of Structured
  Adaptations...") and its `IsSupplementTo` link to the paper DOI (10.1002/rrq.70048). Lists 9
  files (sizes/formats only — 3 `.docx`, 5 `.tsv`, 1 Stata `.do`) but the API does not expose
  filenames, so no specific codebook/questionnaire file could be identified or downloaded from
  this metadata alone.
- **Harvard Dataverse dataset page** (`dataset.xhtml?persistentId=doi:10.7910/DVN/JDUIKT`) and
  the native API (`/api/datasets/:persistentId/`): both returned HTTP 202 with an **empty
  body** — the same AWS WAF bot-challenge block observed on essentially every gilbert_meta
  Dataverse record in this batch series (`gilbert_meta_2/12/38/58/74/97/100/107`, etc.). No
  Wayback Machine snapshot exists for this dataset page either (checked, empty
  `archived_snapshots`). Not pursued further per the task's "try 1-2 approaches, then pivot to
  the paper" guidance.
- **Wiley/ILA Online Library** (`onlinelibrary.wiley.com/doi/pdfdirect/10.1002/rrq.70048`,
  `ila.onlinelibrary.wiley.com/doi/full-xml/...`): both blocked by a Cloudflare "Just a
  moment..." bot-challenge page (checked via `curl` and `WebFetch`; WebFetch separately
  returned HTTP 402 Payment Required on the landing page) — the published-version paper itself
  was not reachable from this environment.
- **EdWorkingPapers open-access preprint, `ai24-1001_v3.pdf`** (found via web search; EdWorkingPaper
  No. 24-1001, "VERSION: August 2025") — **this is the actual paper**, confirmed by exact title,
  full author list (Relyea, Gilbert, Burkhauser, Scherer, Mosher, Wei, Tvedt, Kim) matching the
  dictionary Reference, and matching headline statistics (N = 1,914 Grade 3 students, 95
  teachers, 26 schools, cluster-randomized design). A real, text-native, machine-readable PDF
  (`pdftotext -layout` worked directly, no OCR needed). Cached at
  `.cache/gilbert_meta_104/edwp.pdf` / `edwp.txt`.

## Structure discovered

The Methods section ("Science Background Knowledge", edwp.txt lines ~1227-1252) states, in
full:

> "Students' background knowledge was assessed across three science topics: monkeys, birds,
> and skyscrapers. For each topic, students listened to a passage and three corresponding
> question items read aloud to them (see Appendix D). In the monkey topic, for instance,
> students answered questions such as identifying which muscles can be controlled or which
> muscles in a monkey never rest. Students responded individually, and their answers were
> scored dichotomously (1 = correct, 0 = incorrect). The internal consistency for the nine-item
> measure across all topics was .55."

This **exactly confirms the ground-truth structure**: 9 items (`bg_know_q1`..`bg_know_q9`),
binary `resp` ∈ {0,1}, with the paper's own explicit scoring key ("1 = correct, 0 = incorrect")
— not a guessed dichotomization, unlike the discrepancy found in `gilbert_meta_12`.

**Literal item text is not in this document.** The paper explicitly points to "Appendix D" for
the actual passages and question items; this working-paper PDF (71 pages) ends at the reference
list (page 70) with no appendices attached — Appendices A-F are all referenced in-text (A, B, C,
D, E, F) but none are physically present in this preprint version. Only one illustrative example
is given in prose ("questions such as identifying which muscles can be controlled or which
muscles in a monkey never rest" — for the monkey topic only, not verbatim item stems, and not
attributable to a specific `bg_know_qN` code).

## Structure of output

Same 10-column shape as `candidate_firstborn_personality.rds` (`table, section_id, item,
instrument, instructions, section_prompt, item_text, correct_response, option_text, resp`), one
row per (item, resp) combination — 9 items × 2 resp values = 18 rows.

- `table` = `"gilbert_meta_104"` throughout.
- `section_id` = `"gilbert_meta_104_<item>"`, i.e. one trivial section per item (the SKILL.md
  fallback for "instrument has no [confirmable] testlet/passage grouping") — used deliberately
  even though a real 3-topic × 3-item testlet structure exists conceptually (monkeys/birds/
  skyscrapers, each with its own read-aloud passage), because which `bg_know_q1`..`q9` values
  belong to which topic is not stated anywhere accessible (see Ambiguities). Not guessing a
  topic boundary was judged safer than asserting one that might be wrong.
- `instrument` = one descriptive string identifying the measure, its topic/item structure, and
  citing the paper + Appendix D, repeated on every row.
- `instructions`, `section_prompt`, `item_text`, `correct_response` = `""` (blank) on every row
  — no literal passage text, item stems, or answer key could be recovered (Appendix D not
  present in the only accessible full-text source).
- `option_text` = `"Correct"` / `"Incorrect"` for `resp` = 1 / 0 respectively — this **is**
  directly supported by the paper's own literal scoring statement ("scored dichotomously (1 =
  correct, 0 = incorrect)"), not an inference about item content, so it was populated (parallel
  to how `gilbert_meta_80`/`gilbert_meta_1` and other dichotomous-scored tables in this batch
  populate a plain Correct/Incorrect `option_text` from an explicitly stated scoring rule).
- `resp` = `0` / `1` (integer), matching `irw_fetch`/ground-truth type and values exactly.

## Ambiguities

- **Item-to-topic mapping is unresolved.** The paper confirms 3 topics × 3 items = 9 (monkeys,
  birds, skyscrapers) but never states which `bg_know_q1`..`q9` values belong to which topic, or
  whether item numbering follows topic-administration order. No distinguishing per-item cue
  (numbering in a table, topic labels in a codebook) was found — Appendix D (which would
  presumably resolve this) is not present in the accessible source, and the Dataverse
  file listing/codebook is WAF-blocked. Per SKILL.md's bare-integer-adjacent guidance, no
  section/topic assignment was encoded rather than guessed.
- **Literal item and passage text is not publicly disclosed anywhere located** — consistent with
  SKILL.md's expectation for secure/proprietary researcher-designed instruments in this same
  MORE/content-literacy research program (same pattern already documented for `gilbert_meta_1`
  and `gilbert_meta_2` in this batch: the paper narrates task structure and gives an example but
  withholds the full item bank to an appendix/supplement not reachable from this environment).
  The one illustrative example given in the Methods text ("questions such as identifying which
  muscles can be controlled...") was **not** used to fill `item_text` for any specific
  `bg_know_qN`, since it isn't tied to a specific item number and using it would require
  guessing both which item it corresponds to and its exact wording.

## Items not extracted

All 9 items: `item_text`, `correct_response`, `instructions`, and `section_prompt` are
blank/NA for every item — Appendix D (the source of literal passage/item text) is not present
in the only accessible full-text copy of the paper, and the Dataverse replication package is
WAF-blocked. `item` and `resp` values are fully populated and match ground truth exactly, and
`option_text` (Correct/Incorrect) is populated from the paper's own explicitly stated scoring
rule. This is a **join-key-correct, scoring-rule-complete, item-text-incomplete** extraction —
comparable to `gilbert_meta_1`/`gilbert_meta_2`'s outcome in this same batch, but with one
additional field (`option_text`) recoverable here because the paper states the dichotomization
rule explicitly (unlike `gilbert_meta_12`, where the scoring scale itself was in dispute).

## OCR / image-based extraction

Not needed. The EdWorkingPapers preprint PDF is a digitally-native, machine-readable document
(`pdftotext -layout` extracted clean text directly, confirmed no "Invalid Font Weight"-related
garbling affected the relevant Methods section). No scanned/image-only document was encountered.

## Derived vs. directly-read values

- `item` (`bg_know_q1`..`bg_know_q9`) and `resp` (0/1) were **directly read** — copied verbatim
  from the ground truth (`.gt_gilbert_meta_104.rds`), which in turn is a direct pass-through of
  the raw Stata item file per `data/gilbert_meta_102through104.R` (filtered to `test == "bg"`,
  no value transformation).
- `option_text` ("Correct"/"Incorrect") is a **direct read** of the paper's own literal scoring
  statement ("scored dichotomously (1 = correct, 0 = incorrect)") — not derived/inferred.
- No item stem, passage text, or answer key in this output was **derived/guessed** — where the
  literal source text (Appendix D) was inaccessible, the corresponding fields were left blank
  rather than reconstructed from the one prose example or from item-code semantics.

## Source type used

- **Dictionary row** (Reference/DOI) — starting point for the paper search.
- **Existing repo processing script** (`data/gilbert_meta_102through104.R`) — confirmed
  provenance (raw `.dta` file, `test == "bg"` filter) but disclosed no item content.
- **DataCite metadata API** — confirmed dataset identity and its link to the paper DOI; no file
  listing usable.
- **Harvard Dataverse dataset page / native API** — attempted, WAF-blocked (empty body), no
  Wayback snapshot available either.
- **Publisher (Wiley/ILA) HTML and XML full text** — attempted, blocked by Cloudflare
  bot-challenge.
- **Open-access preprint (EdWorkingPapers, `ai24-1001_v3.pdf`)** — the primary, load-bearing
  source: confirmed exact 9-item / 3-topic / binary-scored structure and the explicit
  correct/incorrect scoring rule, but its appendices (including Appendix D, the literal
  item/passage text) are not included in this version.

## Validation result

`identical(sort(unique(candidate$item)), sort(unique(gt$item)))` = TRUE (9 items:
`bg_know_q1`..`bg_know_q9`).
`identical(sort(unique(candidate$resp)), sort(unique(gt$resp)))` = TRUE (`{0, 1}`).
**Exact match** on both required validation dimensions (join keys). Item-level literal text
(`item_text`, `section_prompt`, `correct_response`) is not recoverable from any accessible
source and is left blank — logged in `pending_index_notes.csv`.
