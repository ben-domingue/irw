# Extraction log: psychtools_athenstaedt

## Source used
Dictionary URL for this table points to the CRAN `psychTools` package (William Revelle's
`psych`/`psychTools` ecosystem) — **not** the lowercase `psychotools` package used
elsewhere in this batch (different package, different maintainer, confirmed before
installing). Installed `psychTools` 2.6.4 from CRAN and loaded its bundled `Athenstaedt`
dataset, `Athenstaedt.dictionary`, and `Athenstaedt.keys` objects, plus the package's
`Athenstaedt.Rd` help page (via `tools::Rd_db("psychTools")`).

`Athenstaedt.dictionary` is a 80-row data.frame with `rownames`/`ItemLabel` = `Sex`,
`V1`...`V74`, `MR1`, `MR2`, `Femininity`, `Masulinity`, `MF`, and a column `Item` holding
the literal English item text (e.g. `V1` = "To pay attention to ones appearance in the
office", `V74` = "Put on Make-up"). This is the package's own documented mapping from the
raw data's column names to the item content, sourced (per `Athenstaedt.Rd`'s `Source:`
field) from "Ursala Athenstaedt, personal communication, 2022" — i.e. the original
author supplied the item key directly to the package maintainer, not a third-party
reconstruction.

Also attempted the source paper (Athenstaedt, 2003, *Psychology of Women Quarterly*,
DOI 10.1111/1471-6402.00111) via SAGE Journals and ResearchGate for corroboration and for
literal instructions/response-anchor text — both paywalled (SAGE returned only the
journal homepage shell to WebFetch; ResearchGate returned HTTP 403). No open-access
route (PMC, author repository) was found. Did not fabricate instructions or anchor text
to compensate.

## Source type used
Package documentation / bundled data dictionary (`psychTools::Athenstaedt.dictionary`),
not the paper itself. The paper was checked but is paywalled and yielded no accessible
full text.

## Structure discovered
Ground truth: 74 items, `"V1"`..`"V74"` (no gaps — confirmed exact match), resp 1-7.
`Athenstaedt.dictionary` covers `V1`-`V74` plus a `Sex` row and several derived-scale rows
(`MR1`, `MR2`, `Femininity`, `Masulinity`, `MF`) that are NOT in the ground-truth item set
and were correctly excluded (they're computed composite scores, not raw items).

All 74 item texts describe concrete behaviors/activities (e.g. "Mow the Lawn", "Talk about
Politics", "Do the Ironing") rather than trait adjectives — despite the paper's title
referencing "traits in addition to behaviors," none of the 74 raw items in this specific
released dataset are trait-adjective items; `Athenstaedt.keys` (Femininity/Masculinity/MF
scoring keys, all built purely from `V`-prefixed items) confirms this. Because there is no
trait/behavior split *within* this item set, one flat `section_id` was used
(`psychtools_athenstaedt_1`) rather than splitting into sections.

## V1-V74 identity confirmation (bare-integer-adjacent check)
Per the task's instruction to treat this with bare-integer rigor despite
`has_bare_integer_items: FALSE`: identity here is a **direct name match**, not a
positional/order reconstruction. `rownames(Athenstaedt.dictionary)` contains `"V1"`
through `"V74"` verbatim, and these are the exact same strings as `colnames(Athenstaedt)`
(the package's raw data.frame) and the exact same strings as the ground-truth `item`
values (`unique(gt$item)`). There was no need to infer order/position — the dictionary
authoritatively keys item text to the literal `V<n>` identifier used in both the raw data
and the ground truth, sourced from the original author. Confidence is high, comparable to
a named-code table rather than a genuine bare-integer reconstruction case.

One discrepancy noted and resolved: `Athenstaedt.Rd`'s prose `Format:` section (a
manually-written free-text block, not machine-generated from the dictionary object) lists
`V1 = "Gender (Male = 1, Female = 2)"`, `V2 = "To pay attention to ones appearance..."`,
..., `V75 = "Put on Make-up"` — i.e. shifted by one position relative to
`Athenstaedt.dictionary` (which has `V1 = "To pay attention..."`, `V74 = "Put on
Make-up"`, matching the ground truth's `V1`-`V74` exactly with no `V75`). Treated this as
a copy-paste/off-by-one bug in the free-text help documentation (likely from an earlier
column layout that included a separate `Sex`/`gender` column before `V1`) and used the
structured `Athenstaedt.dictionary` object as authoritative, since its rownames directly
match the ground-truth item identifiers with no shift.

## OCR / image-based extraction
None. All text came from a machine-readable R package data object (`Athenstaedt.dictionary`
data.frame) and R help/Rd documentation — no PDF text extraction or OCR was performed or
needed.

## Derived vs. directly-read values
- `item_text` — directly read from `Athenstaedt.dictionary$Item`, verbatim (including the
  source's own minor inconsistencies, e.g. "Frquently Ask Colleagues Questions" for V63,
  "Masulinity" as a rowname elsewhere — not corrected/normalized, transcribed as-is).
- `section_id` — derived/assigned (`psychtools_athenstaedt_1`), not from any source text,
  per SKILL.md's rule to emit a trivial single section_id when there is no real
  testlet/passage grouping.
- `instrument` — a descriptive label built from the package's own `Title:` field
  ("Gender Role Self Concept data from Athenstaedt (2003)") plus "Behavior Inventory" to
  reflect the item content; NOT a literal instrument title quoted from the paper (the
  paper's own name for the instrument, if any, was unrecoverable behind the paywall).
- `instructions` — left `NA`, not derived. Could not recover literal participant
  instructions or the response-scale framing question (e.g. "how well does this describe
  you" / "how often do you do this") from any accessible source. Not fabricated.
- `option_text` — left `NA` for all 7 response points. The response scale is confirmed to
  run 1-7 (ground truth) but no literal anchor labels (e.g. "not at all" / "very much") were
  found in the package documentation or an accessible version of the paper. Per
  `itemtext_standard.md`, `option_text` "may legitimately be missing" — used here rather
  than guessing plausible-sounding anchors.
- `correct_response` — blank (`""`) for all rows; this is a self-report behavior/trait
  inventory with no scoring key.

## Ambiguities
- Whether the underlying rating scale is a frequency scale ("how often do you do this"),
  a self-descriptiveness scale ("how much does this describe you"), or something else is
  unknown without the paper's method section — `instructions`/`option_text` left blank
  rather than guessing which framing.
- Package `Title:`/dataset description was used for `instrument` in lieu of a paper-sourced
  instrument name; flagged above as derived, not literal.

## Items not extracted
None at the item level — all 74 ground-truth items (`V1`-`V74`) got `item_text`.
`instructions` and `option_text` were not recoverable for any item (paywalled paper, no
open-access route found) and are logged as a discrepancy below.

## Validation result
Exact match. `unique(candidate$item)` == `unique(gt$item)` (74 items, `V1`-`V74`) and
`unique(candidate$resp)` == `unique(gt$resp)` (1-7), checked directly against the cached
ground truth (`setequal()` both TRUE). No `irw::irw_fetch()` call was made per the
benchmark instructions; ground truth came from the cached
`.gt_psychtools_athenstaedt.rds`.
