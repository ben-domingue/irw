# Extraction log: gilbert_meta_74

## Source used
Dictionary URL is a Harvard Dataverse landing page
(`doi:10.7910/DVN/ZF1LKZ`); `WebFetch` returned empty content on every Dataverse
URL tried (dataset.xhtml, citation page, dataverse_json export, search API) — the
Dataverse UI is a JS-rendered SPA that this fetch tool cannot render, so the
dataset's own file listing/codebook was never actually reached. Fell back to the
published paper per Step 3's "try an open-access route" guidance:
`tandfonline.com` full text returned HTTP 403 (paywalled), but an open
EdWorkingPaper preprint (No. 23-868, "VERSION: May 2024", same title/authors,
forthcoming in *Applied Measurement in Education*) was found via web search at
`https://edworkingpapers.com/ai23-868` -> PDF at
`https://edworkingpapers.com/sites/default/files/ai23-868.pdf`. Cached at
`.cache/gilbert_meta_74/ai23-868.pdf` (42 pages, read via the PDF-capable Read
tool in two 20-page chunks).

Confirmed this is the correct source for `gilbert_meta_74` (not just the same
paper family) via a hard numeric match: the paper states the item-level analytic
subsample is students who completed both Grade 2 and Grade 3 vocabulary tests,
"n = 1225" — this equals `length(unique(gt$id))` in the cached ground truth
exactly (1225). Also: "12 items" in the paper == 12 bare-integer items in ground
truth.

Also checked this repo's `data/` directory for an existing processing script
(per task instructions) — found `data/gilbertmeta.R`, which is the generic
post-processing script that split ~113 datasets out of a combined
`datasets_list.Rdata` object (from a *different* paper, the IL-HTE meta-analysis,
arXiv:2405.00161) into individual `gilbert_meta_N` tables. It confirms the
`gilbert_meta_*` naming convention and the `wave`/`treat` column renaming logic,
but contains no dataset-specific content (item text, word lists) for study #74
specifically — it's a generic loop, not evidence about this table's item content.
No table-specific script exists.

## Structure discovered
The paper (p. 18-19) directly describes the instrument: a researcher-designed
"vocabulary knowledge depth" assessment with exactly 12 items. Each item names a
target word and asks students to pick the 2 of 4 answer choices that best go with
it (worked example given verbatim: target word **carnivore**, choices "fruit",
"care", "meat", "prey", correct = "meat"/"prey"). Scored dichotomously: 1 if both
correct words selected, 0 for any other pattern — this matches the ground truth's
binary resp coding exactly. The 12 items split into 7 "taught" words (explicitly
taught via the MORE intervention) and 5 "untaught" words (conceptually related,
encountered incidentally e.g. in read-alouds) — this taught/untaught split is the
paper's own `itemtype` covariate used in its models, not something inferred.

Figure 3 (p. 38, "Item-Level Growth Trajectories Derived from Model 3") discloses
all 12 actual target words by name, color-coded taught vs. untaught:
- Taught (7): Fossil, Paleontologist, Hunter, Extinct, Evidence, Brutal, Theory
- Untaught (5): Reptile, Carnivore, Hypothesis, Organism, Trait

This confirms the full word pool and the 7/5 taught/untaught split stated in the
text (12 total). However, Figure 3's word positions are ordered by *posttest
difficulty* for visualization purposes (a growth-trajectory plot), not by test
presentation order or item number — the paper never numbers the 12 items 1-12 or
states a presentation order anywhere in the main text. The Online Supplemental
Materials (OSM), referenced multiple times (internal-consistency stats, CFA fit
stats, an item-specific growth-rate table with empirical Bayes estimates) would
very likely contain this, but it is hosted by the journal (Taylor & Francis) and
not reachable — the tandfonline.com article page 403'd on every fetch attempt, so
the OSM link itself was never resolved.

## Bare-integer validation check (has_bare_integer_items = TRUE)
Checked the paper's stated item count (12) against the ground truth's bare
integer item set (`"1".."12"`, 12 distinct values) — **counts match exactly**.
Also cross-checked N: paper's analytic sample "n = 1225" == ground truth's
`length(unique(id))` = 1225 exactly, and the paper's dichotomous 0/1 scoring
matches ground truth's resp values.

However, per SKILL.md's explicit warning, count/range plausibility is *not*
sufficient to assign specific `item_text` to specific bare-integer `item` codes
— and here there genuinely is no order/numbering cue available in the accessible
source (no numbered list, no appendix table, no item-order statement; Figure 3's
ordering is by difficulty, not by item ID, and mixing the two would be exactly
the kind of guess the skill instructions warn against). The word-to-integer
mapping is therefore treated as **genuinely ambiguous** and not guessed. See
`pending_index_notes.csv`.

## Structure of output
- One `instrument` name and one `instructions` string (task format + generic
  scoring rule, both paraphrasing the paper's own description of the item type,
  since the paper doesn't quote verbatim on-screen/on-paper instructions given to
  students) applied to all 12 items/24 rows.
- One trivial `section_id` per item (`gilbert_meta_74_<n>`), blank
  `section_prompt` — no shared passage/testlet structure; each item is an
  independent target-word probe.
- `item_text` and `correct_response` left blank (`""`) for all 12 items — the
  specific word-to-item-number mapping is not recoverable from the accessible
  source (see above).
- `option_text`/`resp`: two rows per item, `resp=0` -> "Incorrect (any other
  response pattern)", `resp=1` -> "Correct (selected both target-associated
  words)". This is the one thing that generalizes safely to every item without
  knowing the specific word, since the paper states the dichotomous scoring rule
  applies uniformly to all 12 items.

## Ambiguities
- Word-to-item-number mapping (see above) — logged to `pending_index_notes.csv`.
- The `instructions` text is a paraphrase of the paper's *description* of the
  item format (not a literal quote of on-instrument instructions to students,
  which the paper doesn't reproduce) — kept short/terse to match the source's own
  terseness rather than expanding it.
- 73 of 29,400 ground-truth rows (0.25%, all at wave 2) have `resp = NA`. Treated
  as ordinary missing/unadministered responses, not a third response category —
  consistent with the task's stated ground-truth resp value set of {0, 1}, and
  excluded from the validation comparison (`unique(gt$resp)` minus `NA`).

## OCR / image-based extraction
Not needed. The source PDF (EdWorkingPaper preprint) has a normal text layer;
all content, including the Figure 3 word labels, was read as extracted text via
the PDF-capable Read tool. Figure 3's word labels were read directly as image
content shown alongside extracted page text (the Read tool renders each PDF page
visually) — legible printed labels, not an OCR pass on scanned material.

## Derived vs. directly-read values
None of the values in the output were derived/computed. `instrument`,
`instructions`, and the `option_text` correct/incorrect labels are direct
paraphrases/transcriptions of statements on p. 18-19 of the source PDF. No
`item_text`/`correct_response` values were written at all (left blank) rather
than derived from indirect cues, per the ambiguity above.

## Source type used
Paper appendix/body text (open-access EdWorkingPaper preprint PDF, No. 23-868) —
specifically the "Empirical Application" section (pp. 18-19) and Figure 3 (p. 38).
Not a PDF manual, not a website codebook, not raw-data column headers (Dataverse
was unreachable), and no existing repo processing script had dataset-specific
content (see "Source used" above).

## Items not extracted
All 12 ground-truth items are present in the output with correct `item`/`resp`
values (validated exactly against ground truth). But `item_text` and
`correct_response` are blank for all 12 — the specific vocabulary word tested by
each bare-integer item ID could not be determined from any accessible source.
The word pool (12 words, 7 taught / 5 untaught, with one fully-worked example
item for "carnivore") is real and disclosed, but not assignable to specific item
IDs. This is the "couldn't fully automate this one" bucket described in
SKILL.md — a partial extraction with an honest ambiguity, not a failure.
