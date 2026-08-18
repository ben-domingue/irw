---
name: irw-auto-itemtext
description: This skill should be used when the user asks to "generate item text for X", "process the itemtext queue", "extract items for this table", or otherwise references transcribing/extracting instrument, section, item, or response-option text for an IRW table from its source paper. Also applies when the user references itemtext/join.R, itemtext/upload.py, the itemtext index workbook, or the itemtext.html public schema.
---

# IRW Item Text Extraction

Transcribes the literal instrument/section/item/response-option text for an IRW table
from its source paper and writes it as a validated `{table}__items.csv`, ready for
`itemtext/upload.py`. The output format is defined in `references/itemtext_standard.md`
(copied verbatim from itemresponsewarehouse.org/itemtext.html) — read it before
extracting anything, don't re-derive the schema from a merged example alone.

## THE PRIME COMMANDMENT — `item` is the join key

**`item` must be common between the response table and the itemtext table.** The entire
purpose of an itemtext table is to be joinable to `irw::irw_fetch(table)` on `item`;
every `item` value must appear in the live data exactly as the live data spells it, and
the two sets must match. Nothing else in this skill outranks that. A beautifully
transcribed instrument whose `item` values don't line up is worthless — it cannot be
linked to a single response.

Consequences to keep in front of you:

- Take `item` values verbatim from Step 2's ground truth. Never invent, normalise,
  re-case, re-order, or "tidy" them, and never carry over the source file's own column
  names when the IRW table renamed them.
- `resp`/`option_text` is the second join axis and the same logic applies: shipping
  `raw_resp` (label strings) when the live table stores integers leaves the text
  unlinkable to any response. `raw_resp` is a genuine last resort for when no scoring key
  exists anywhere — not a default when the paper is merely silent. Read
  `data/<table>.py|R` first (Step 4) and verify with Step 5b route 9.
- This is what `validate_items.R` exists to enforce (Step 5), and why it is a hard gate
  rather than advice. Step 5b then checks the mapping *within* those matching sets.

Work from inside `itemtext/`. **All output — `{table}__items.csv` files,
`audit_confirmed.csv`, and `pending_index_notes.csv` — goes in `itemtext/itemtables/`,
not the `itemtext/` root.**

## The core model — read this before the steps

Everything below is one idea in four parts. The steps implement it; this section is what
they are implementing, consolidated after reviewing all 50 tables of batches 001-005.

### 1. An itemtext table is a JOIN, not a document

Its value is entirely in linking to `irw::irw_fetch(table)`. Two keys carry that link and
they fail independently:

| axis | what must hold | what breaks it |
|---|---|---|
| `item` ↔ `item_text` | every live `item` appears, spelled exactly as the live data spells it | invented/normalised codes; a positional rename nobody checked |
| `resp` ↔ `option_text` | every `resp` level a respondent actually used has a row for that item | option rows for one item only; a level omitted; `raw_resp` when the live table is numeric |

`validate_items.R` enforces both as SETS over the whole table, which is necessary and not
sufficient — an item can lack the levels its own respondents used and still pass, because
another item supplies those values. `audit_batch.R` closes that gap per item.

### 2. Sources rank, and the ranking is not negotiable

Use the highest available, and say which one you used:

1. **The source data file's own labels.** SPSS variable labels, value labels, spreadsheet
   column headers. This ties code to text at the source — no inference at all. **Check both
   levels**: `alsuhibani_2022_npi_s3`'s variable labels are bare column names while its
   *value* labels carry the forced-choice statements.
2. **The study's own paper or supplement**, where it reproduces items against codes.
3. **The published instrument** (canonical wording).
4. **A third-party reproduction** — clinical-assessment sites, handouts. Last resort, and
   see the grid trap in Step 4.

**Level 1 outranks the rest, but it is not infallible — cross-check it.** Both kinds of
label can be wrong, and batch_007 hit one of each.

*Value labels* can state the wrong direction. `baka2023_bpnsf`'s `.sav` says 1 = "Strongly
agree" … 7 = "Strongly disagree", but its satisfaction items correlate **+0.37** with the
same study's work-engagement mean (whose 0–6 Never..Always coding is unambiguous) while its
frustration items correlate negatively — which is only possible if the scale actually runs
1 = disagree … 7 = agree. The shipped anchors were reversed to match the data, and that
override is documented in provenance. Note the diagnostic needs BOTH halves: the correlation
pattern alone is consistent with either direction depending on which block is satisfaction,
so read the item content to fix which block is which before concluding anything.

*Variable labels* can be scrambled relative to the column NAME. When both encode item
identity, they must agree. In `bakker_2020_rses`'s
source file (PLOS 10.1371/journal.pone.0227958.s004) they don't: `satisfied301` is labelled
"I feel that I'm a person of worth", `goodqualities303` is labelled "All in all, I am
inclined to feel that I am a failure", and three columns carry no label at all — five of
seven labelled RSES columns contradict their own names, which otherwise follow canonical
order and numbering. An extraction that trusted those labels would ship five items wrong.
A one-minute sanity read of names against labels catches this; see issue #1654.

Two failures today came from skipping level 1 when it existed: `alsuhibani_2022_gcbs` was
built from the paper while the study's `.sav` labelled every item (which is how a wording
error got in), and `altahla_2024_whoqol` shipped a paraphrase while the source headers held
the canonical text. **Before concluding a source doesn't exist, open the data file.**

### 3. How the IRW `item` code was derived decides how much checking you owe

Read `data/<table>.py|R` and classify. This is the single most useful five minutes in the
whole process:

| pattern | example | what you owe |
|---|---|---|
| code IS the source column name | `mc1`, `HamD3Baixa`, `PADS1` | nothing — there is no mapping step |
| number-preserving rename | `LOC1`→`LOC_01`, `BBASAL_3`→`barthel_3` | read the dict; it is mechanical |
| **positional assignment** | `df.columns = ["id"] + ITEMS`, `f"{pfx}{i+1}"` over a column range | **diff shipped `item_text` against the source header at that position** |

10 of the 50 audited tables are positional, and every mapping defect found in review was
one of them. `data_labels` in provenance does NOT imply inference-free; it describes where
the words came from, not how the code was assigned.

### 4. Transcribe literally, and disclose every deviation

The output claims to be what the study administered. Three rules:

- **Don't silently normalise.** `ali_2021_isi` shipped canonical ISI wording while its
  source headers read "NOTICABLE" and "Difficult falling asleep", and the note claimed
  verbatim transcription. Correcting an obvious source typo is defensible; not saying so
  is not.
- **Don't invent structure.** Some instruments have no item stems (see Step 4), some have
  no option labels, some vary option wording by item. Blank is a valid, meaningful value.
- **Notes must survive an audit.** Several provenance notes reviewed today asserted things
  that were false — "transcribed verbatim" when normalised, "not a duplicate upload" when
  it was a strict subset, "the .sav has no item text" when only the variable labels lacked
  it. A wrong note is worse than no note, because it stops the next person looking.

## Output path: CSV-direct, not Sheets-fill

**Confirmed with the user (2026-07-27): this skill writes `{table}__items.csv` directly
— it does not create or fill the 4-tab per-table Google Sheets that the human workflow
uses.** Two reasons this was chosen over Sheets-fill, in case the decision needs
revisiting later:

1. No tool available to this skill can edit individual tabs of an existing multi-tab
   Google Sheet — only whole-file create/copy/read. The `irw-automated-finding` skill
   hit the identical gap and settled on writing CSVs directly rather than claiming a
   sheet was updated it couldn't actually touch; this skill follows the same precedent.
2. It matches the direction already taken elsewhere in this repo's automation: auto-fill
   and write directly, human spot-checks the output rather than reviewing an
   intermediate editable surface.

This means: **do not** attempt to write into the Sheet1 `instrument`/`sections`/`items`/
`responses` link columns for tables this skill processes, and don't create new per-table
spreadsheets. `join.R` still exists and still works the old way for anyone using the
manual Sheets-fill workflow on a different table — don't modify it.

## Before doing anything

1. Read `references/itemtext_standard.md` for the schema and the per-tab column layout.
2. Check whether a `{table}__items.csv` already exists locally in `itemtext/itemtables/`
   for the table in question — if so, don't reprocess without being told to redo it.
3. Note: there's no standing local cache directory yet. If you fetch a paywalled or
   rate-limited source PDF, save it under `itemtext/.cache/<table>/` (already gitignored)
   so a retry doesn't re-fetch it. Create the directory if it doesn't exist.

## Step 1 — Find a candidate table

If the user names a specific table, skip to Step 2.

For "process the queue", run:

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/list_candidates.R
```

This diffs `irw::irw_list_itemtext_tables()` (done) against `irw::irw_list_tables()`
(all), then removes anything already claimed or excluded via the index workbook's
`queue`, `tables_excluded`, `xz_todo`, `nj_todo` tabs, or already has populated links in
Sheet1 itself. On 2026-07-27 this returned 1233 open candidates out of 2233 total tables
(421 already done, 580 claimed/excluded) — expect similar order-of-magnitude numbers.
The four cross-check tabs have inconsistent internal schemas (some have headers, some
don't; column names differ) — the script does a raw substring match across each tab's
lines rather than assuming a shared structure, which is deliberate, not a shortcut to
fix later.

A "PRESENT -- inspect before proceeding" hit on any of those tabs doesn't necessarily
mean skip outright — e.g. `xz_todo`/`nj_todo` may just mean someone flagged it for
later, not that it's actively claimed. Use judgment; when genuinely unsure whether a
table is claimed, ask rather than duplicate someone's in-flight work.

## Step 2 — Get the ground truth and source-paper leads

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/table_context.R <table>
```

Prints, in one shot:
- The exact `item` and `resp` value sets from `irw::irw_fetch(table)` — this is the
  target the extraction must hit, not a nice-to-have. Every `item` and `resp` value you
  write must come from this set; never invent one.
- The dictionary row (Description, URL for data, Reference, DOI for paper) — same
  source used for dataset processing scripts.
- This table's current status in the index workbook (existing NOTES, whether Sheet1
  links are already populated, and presence on the four cross-check tabs). If links are
  already populated, the script prints a STOP — respect it.

## Step 3 — Get the source paper/instrument

Use the DOI/URL from Step 2 to find the paper. **Item-level text often lives in a
supplementary/appendix file rather than the main paper body** — check for supplementary
material links (journal site, OSF/Dryad/Figshare companion records, a "Supporting
Information" section) before concluding the text isn't available. If the paper is
paywalled, try an open-access route (PMC, author's institutional repository, the
dataset's own repository page) before giving up.

Cache anything fetched (PDF or scraped page text) under `itemtext/.cache/<table>/` so a
retry on a rate-limited or slow source doesn't refetch it.

**If the dictionary URL points at a CRAN package** (MPsychoR, psychTools, psychotools,
PCMRS, etc.), check the package's own `Rd_db()` documentation before searching for a
paper — it's faster and more authoritative than reconstructing item wording from a paper
citation:
```r
library(tools)
db <- Rd_db("MPsychoR")
Rd2txt(db[["Dataset.Rd"]])
```
This has recovered full verbatim item wording directly for several tables across this
skill's use.

**If a source codebook is an old binary `.doc` file (not `.docx`)**, Python's
`zipfile`-based `.docx` parser can't read it — convert it first:
```bash
soffice --headless --convert-to txt file.doc
```
LibreOffice is available in this environment; this has recovered otherwise-inaccessible
codebook text (e.g. old Florida Twin Project codebooks) that would otherwise look like a
dead end.

### Step 3b — Verify the table name/description actually matches what you found

Before extracting, check that the instrument you're about to transcribe is the one the
table is actually built from — don't assume the table name or dictionary Description
names the right instrument just because it's the obvious reading of the source paper.
A paper commonly administers several instruments (a named scale plus demographic/
comorbidity checklists, or several scales in the same battery), and the table name can
end up describing the wrong one. Cross-check the live `item`/`resp` values from Step 2
against what you're about to transcribe: does the item count, response range, and item
content actually match the named instrument, or does it look like a different measure
from the same study? Real examples hit in testing: a table named for a kinesiophobia
scale (TSK-17) whose live items were actually a baseline comorbidity checklist from the
same paper's Table I; a table named for the Insomnia Severity Index whose live items
were actually that study's PHQ-9; a table named for the FAD-Plus whose live items were
actually the Rosenberg Self-Esteem Scale administered alongside it. In each case the
live data matched a *different* instrument in the same source than the one implied by
the table name. A subtler variant: a table named for the Reading the Mind in the Eyes
Test (RMET) whose live items were actually the Imposing Memory Task, a distinct
secondary Theory-of-Mind measure from the same paper — here both instruments were
independently plausible names for the paper's ToM battery, so the mismatch only showed
up by checking the live item content (story-vignette text, not eye-photo trials) against
what RMET items actually look like, not by the name alone looking obviously wrong.

If you find a mismatch: extract against what the live data actually is (not what the
name implies), set the `instrument` field to the correct instrument name, and log it via
Step 6b so the table name/dictionary Description can be corrected — don't force-fit the
extraction to match the table's name.

## Step 4 — Extract and structure

Build the 4-tab structure (see `references/itemtext_standard.md` for exact columns),
in memory or as a scratch CSV — you don't have to actually create Sheets tabs, just
produce data shaped like them before merging:

- **instrument/instructions** — full instrument name + literal instructions text that
  applies to the entire table regardless of `section_id`.
- **section_id/section_prompt** — only for testlets/shared-passage items, and scoped to
  just the items sharing that `section_id` (e.g. a passage or context given before a
  testlet). If the instrument has no such grouping, still emit one `section_id` per item
  (e.g. `<table>_1`) with a blank `section_prompt`, rather than omitting the column — the
  merge step needs a join key. Never record the same span of source text in both
  `instructions` and `section_prompt` — decide which one it belongs to (whole-table
  framing goes in `instructions`; testlet/passage-specific text goes in `section_prompt`
  only, even if it reads like instructional language) and record it once. See
  `references/itemtext_standard.md` for the full rule. **When a table has more than one
  `section_id`, check whether the framing text actually differs by section before
  defaulting to `instructions`** — e.g. a self-report and parent-report block of the same
  instrument often share near-identical wording that differs only in a few words ("how
  you feel" vs. "how your child feels"). If the wording varies at all across sections,
  that's decisive: it's section-specific and belongs in `section_prompt` for each section,
  never in `instructions`, even if it reads like generic whole-table framing at a glance.
  Only text that is truly identical across every section (or a genuinely single-section
  table with no other candidate text) should go in `instructions`.
- **Some instruments have no item stems at all — do not invent them.** In a
  four-statement-group instrument (SHAI/HAI-18, BDI, and forced-choice scales like the
  NPI-13), an "item" *is* a set of complete alternative statements you choose between;
  there is no question stem. The correct shape is `item_text` **blank** for every row with
  all the words in `option_text` (`aguirre_camacho_2021_shai`,
  `alsuhibani_2022_npi_s3`). `audit_batch.R` will report `100% of rows have blank
  item_text` — that WARN is the expected, correct result here, not something to fix.
  Clinician-rated scales are the neighbouring case and *do* have stems: the domain name is
  the stem and the severity anchors are the options (`alves_2017_hamd17`:
  "Anxiety - Psychic" / "No difficulty", "Tension and irritability", …).

  **The trap:** clinical-assessment websites re-render these instruments as a tidy grid
  with an invented stem per row and the four statements squeezed into short column
  headers. That grid is a *paraphrase*, and transcribing it silently loses wording — a
  first pass at `aguirre_camacho_2021_shai` built from one produced stems that don't exist
  in the instrument, dropped "(of my age)" from item 2, and flattened item 12's "I usually
  think that I am seriously ill" to "Usually". It passed `validate_items.R` and
  `audit_batch.R` cleanly, and was only caught by a human spot-check. **If a source
  presents an instrument as a grid of stems × short anchors, find the instrument's own
  prose form before transcribing.**
- **item/item_text/correct_response** — `item` values must be exactly the ones from
  Step 2's ground truth, not invented. `correct_response` blank when there's no scoring
  key; semicolon-separated when multiple answers are correct (e.g. `A;C`). **When the
  ground-truth `item` values are bare integers** (e.g. `1`, `2`, `3` rather than named
  codes like `q1_anx`), you have to reconstruct which paper item each integer refers to
  — usually by position/order in the instrument. Confirming that `resp`'s type and range
  look plausible for that item (e.g. "a 1–5 Likert item exists") is not sufficient
  validation on its own, since many items in the same instrument share the same response
  range and would pass that check regardless of which one you picked. Before assigning
  `item_text` to a specific bare-integer `item`, cross-check the paper's stated item
  count and presentation order, and any distinguishing wording/position cues (item
  numbering in a table/appendix, subscale grouping, reverse-scored markers) — don't rely
  on range-matching alone. If the mapping is genuinely ambiguous, say so and log it per
  Step 6b rather than guessing.
- **resp/option_text** — `resp` values must be exactly the ones from Step 2's ground
  truth. Map extracted option text onto that existing numeric/ordinal coding — for a
  standard Likert-style instrument this is usually the ascending order the paper
  presents options in, but check against the instrument's known scoring convention
  rather than assuming. When the scoring key can't be recovered (the source only gives
  a categorical/lettered code with no way to tie it to the existing numeric `resp`), put
  the raw option in a `raw_resp` column instead of forcing it into `resp` — see
  `gilbert_meta_11` for a real example of this pattern.

  **Before falling back to `raw_resp`, read the IRW processing script** —
  `data/<table>.py` or `data/<table>.R`. The paper is the authority on what participants
  saw, but the processing script is the authority on **what the integers in the IRW table
  mean**, and it very often contains the literal label→number mapping the paper omits.
  `alasmari_2025_ai_trust_confidence` shipped with `raw_resp` on the grounds that the paper
  never states its 1–4 coding direction, while `data/alasmari_2025_ai_trust_confidence.py`
  defines `RESP_MAP = {not confident: 1, neutral: 2, somewhat confident: 3, very confident:
  4}` outright — and its sibling table from the same paper had already used its own script's
  mapping correctly. Check the script whenever `resp` is numeric but the source only
  discloses labels; `raw_resp` is for when neither source can tie them together.

**Match the source's terseness.** Transcribe `instructions`, `section_prompt`,
`item_text`, and `option_text` at the same level of brevity as the source material. If
the paper's instructions are one short sentence, keep it one short sentence — don't
expand it into an explanatory paraphrase. If item stems are terse phrases (e.g. "Felt
nervous"), keep them terse; don't pad them into full explanatory sentences or add
clarifying boilerplate that isn't in the original text. The goal is a literal transcript,
not a rewrite for clarity.

Merge the four pieces (`items` as the base, then `sections`, `instrument`, `responses`,
each via `merge(..., all.x=TRUE)` on shared key columns) into one data frame — this is
what becomes `{table}__items.csv`.

## Step 5 — Validate before writing anything final

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/validate_items.R <table> <candidate_items.csv>
```

This is the non-negotiable gate — same logic as `join.R`, but reports the actual
mismatched values instead of just TRUE/FALSE. It checks:
- Required columns present.
- `unique(item)` matches `irw::irw_fetch(table)$item` exactly.
- `unique(resp)` matches `irw::irw_fetch(table)$resp` exactly (skipped, by design, when
  the table uses `raw_resp` instead because no scoring key was recoverable).

**Also check row count per item** (`table(gt$item)` on the live data) even when the item
*set* matches exactly — a matching set doesn't rule out one item code silently standing
in for two different questions. This caught a real case where one item had 4x the row
count of every other item because it was quietly conflating two distinct questions under
one code; content review alone didn't surface it, the row-count anomaly did.

**Do not force a match.** If the paper discloses a different item count than the live
data (e.g. `fivpei_perrig_2023_attdiff`: 28 items per the paper vs. 21 in the data, noted
in the index sheet), or text can't be fully recovered for every item, emit whatever
partial/defensible structure you have and record the discrepancy per Step 6b — don't
pad, guess, or drop items silently to make the counts line up.

Only once this passes (or the discrepancy is deliberately accepted and logged) does the
CSV get written as `itemtext/itemtables/<table>__items.csv`.

### Step 5b — Verify the item↔text and option↔resp mappings against the data (REQUIRED)

Everything in Step 5 checks *sets*. If `item_text` for items 3 and 5 were swapped, the
item set, the resp set, the row counts and the whole audit still pass — and the table
ships a plausible, confidently-wrong mapping that no downstream check will ever catch.
So mapping is verified separately, against numbers, and the outcome is recorded.

The two mapping axes are defined in the core model above; routes 1–8 below verify
`item_text`↔`item`, route 9 verifies `option_text`↔`resp`, and route 6's reverse-keying
signal touches both. Verify whichever axis carried inference — usually the first, but any
table built from a categorical source whose IRW `resp` is numeric has made a decision on
the second too. **Start by classifying the code derivation (core model §3): if it is
positional, the header diff settles the table faster than any statistical route.**

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/item_stats.R <table>
```

That prints per-item n, mean, SD and floor/ceiling % from the live data, in the shape
papers publish them. Then look for something in the source to match it against, in
descending order of strength:

1. **Per-item descriptive statistics.** Most validation papers have a table of per-item
   M (SD), floor/ceiling %, item-total correlations or factor loadings. Match it in order.
   Means usually identify each item outright; when two items' means are within ~0.02
   (which happens — `item_stats.R` flags it), **floor/ceiling % is what breaks the tie**.
   Do not declare a match on means alone in that case. Worked example:
   `aguirre_camacho_2021_champion`, where the paper's Table 4 pinned all 8 items and
   separated the near-tied 3-vs-5 and 6-vs-7 pairs.
2. **Per-item response ranges**, whenever an instrument's items do *not* all share one
   scale. The pattern of which items take which range is a structural signature, and it
   needs no published statistics at all. Worked example: `alves_2017_hamd17` — HDRS-17
   assigns 0–4 to items 1,2,3,7–11,15 and 0–2 to the rest, and the live data matched all
   17. Also how the two `abdullah_2024_bsq_*` tables were corroborated.
3. **Subscale totals.** If the paper reports subscale means/SDs/ranges, sum the live
   items you assigned to each subscale and compare. This pins subscale *membership* and
   the numbering at subscale boundaries, but not order within a subscale — record it as
   partial. Worked example: `aguirre_camacho_2021_shai`.
4. **A parameter the item text itself implies.** If each item's text states quantities
   that imply a difficulty/rate/dose, compute it and check the responses track it. This
   is the strongest route when it applies. Worked example: `allen_2025_delaydiscount`,
   where each Kirby MCQ item implies `k=(LDR-SIR)/(SIR*delay)`; the proportion choosing
   the delayed reward correlated with k at Spearman +0.96 across 27 items.
5. **Subscale block structure**, via
   `Rscript .claude/skills/irw-auto-itemtext/scripts/mapping_structure.R <table> <group1> <group2> …`.
   Most multi-subscale instruments have a published, fixed item-number→subscale
   assignment, which is a testable prediction about the data: same-subscale items should
   intercorrelate most. Worked examples: `alexander_2017_dsi` (21/23 — good enough to
   verify a `reconstructed` mapping), `algner2022_mimi16` (15/16). **Know when this test
   is underpowered**: it cannot separate facets that are nearly collinear, and a low
   score then is NOT evidence of a bad mapping — `alsuhibani_2022_gcbs` scored 8/15 only
   because the GCBS is dominated by a general factor (rival-facet r = 0.45–0.64), and
   `algner2022_uwes` scored 6/9 because UWES dedication and absorption overlap. Say which
   it is rather than reporting the fraction bare.
6. **Keying polarity.** On a scale with reverse-worded items whose data are still raw, the
   sign pattern in the correlation matrix reveals each item's polarity class. Worked
   example: `algner2022_cse`, where CSE1 correlated +0.31…+0.45 with every odd item and
   −0.06…−0.36 with every even one, exactly the canonical CSES odd-positive/even-negative
   keying. Verifies polarity per item, not order within a polarity class. Same idea pins
   the reverse-keyed triple {3,4,26} in `altahla_2024_whoqol`.
7. **A marker item.** Some instruments have one item whose distribution is unmistakable —
   EPDS item 10 (self-harm) must be the least endorsed in any community sample
   (`almuqbil_2022_epds`: 0.44 with 73.9% at zero, against 0.80–1.77 for the rest). Pins
   that one item.
8. **Semantic coherence of the response distribution**, when the resp scale is
   diagnostic of content (frequencies, counts, difficulty). Rules out a random
   permutation; doesn't prove adjacent items aren't swapped. Worked example:
   `ahmed_2019_food_consumption`, where days-per-week consumption ordered maize 5.01 >
   … > milk 1.20 exactly as food groups should.
9. **Response-frequency matching**, for the *other* mapping axis — `option_text`↔`resp`
   rather than `item_text`↔`item`. Whenever the source data file stores **labels** while
   the IRW table stores **integers**, count each label per item in the source and each
   integer per item in the live table: a correct mapping matches cell for cell, and a
   flipped direction or any permuted level breaks it immediately. This is decisive, not
   circumstantial. Worked example: `alasmari_2025_ai_trust_confidence`, whose raw S1
   `.xlsx` holds "not confident"/"neutral"/… and whose live table holds 1–4 — all 16
   item × level counts matched exactly (e.g. 25/83/156/71 raw vs 25/83/156/71 live),
   confirming `neutral = 2` sits between "not confident" and "somewhat confident" rather
   than at an end.

   **Use this to check the processing script rather than trust it.** `data/<table>.py|R`
   tells you what the mapping is *meant* to be; only the counts show what actually
   produced the live data. Reach for it any time a table was built from a categorical
   source, and especially before converting a `raw_resp` table to `resp`.

**Check for two exemptions first — both are stronger than any statistic and cost nothing:**

- **Self-describing item codes.** If the code names its own content (`TLXEffort`,
  `increase_cancer_risk`, `afraid`, or a Stroop stimulus word like `ALCOHOL`), a
  permutation is impossible without being self-evident. 7 of the 50 audited tables were
  exempt on this ground alone.
- **Explicit code labels in the paper.** If the paper's item table prefixes each item with
  the very code the data uses (`alomari_2025_student_questionnaire`: "Q1: I believe that
  this teaching model…" against columns `Q1`..`Q15`), the tie is a label match, not an
  order inference.

**Prefer the source labels over every statistical route, and check them at both levels.**
A `.sav`/`.xlsx` that labels its columns ties code to text at the source, which is stronger
than any inference this step can test. Three things make that tie verifiable rather than
assumed, and all three are cheap:

- **Check variable labels AND value labels.** `alsuhibani_2022_npi_s3`'s variable labels are
  bare column names, while its *value* labels carry the paired forced-choice statements. "The
  file has no item text" is a claim about the level you looked at.
- **Read how the processing script derives the IRW code**, because that is where the tie can
  break. Three patterns, in ascending risk: the code IS the source column name (nothing to get
  wrong); a number-preserving rename (`LOC1` -> `LOC_01`, `BBASAL_3` -> `barthel_3`, mechanical,
  just read the dict); or **positional assignment** (`df.columns = ["id"] + ITEMS + ...`, or
  `f"{prefix}{i+1}"` over a column-index range), where the code keeps no trace of the source
  name and a shifted range is undetectable from the output alone. 10 of the 50 audited tables
  are positional, and every mapping defect found in the batch_003/005 review was one of them.
  For positional codes, diff the shipped `item_text` against the source header at that position
  — mechanical, and it settles the table outright.
- **Watch for truncation and artifacts.** Label fields have hard caps and long items hit them:
  **SPSS truncates variable labels at 255 characters** (9 labels in
  `amarilla_2020_hip_fracture`'s file sit at the cap, e.g. `RMH3_BASAL` ends mid-phrase at
  "...felt calm & peaceful? (prior"), and **Stata truncates at 80** — which bites much sooner.
  When a `.dta` label is truncated, the study's own **do-file** usually carries the full text in
  its `label variable` statements, and that is still a level-1 source; `audretsch_2021_
  entrepreneurial_ecosystems` was recovered that way from its S3 File. So for long items the
  label may be a *prefix*, and anything shipped beyond it came from somewhere you must name. Labels also carry wave suffixes ("prior hip fracture"),
  leading numbering ("1. "), A-/B- markers, and spreadsheet concatenation artifacts — strip
  those deliberately, and say so in provenance.

And before reaching for statistics at all, **re-check whether the source data file has
variable labels** — the sweep found `alsuhibani_2022_gcbs` had been extracted from the
paper as `paper_explicit` when the study's own `.sav` files labelled every GCBS item, which
both settled the mapping and caught a wording error ('rumors' where the study wrote
'rumours').

Two traps:

- **Match the right subset.** A paper's per-item table almost always describes one wave
  (usually baseline) or one subsample, while the IRW table may pool several.
  `item_stats.R` splits by wave for this reason. Pooled-vs-single-wave comparison
  produces spurious near-misses — `champion` reads 3.60 pooled vs 3.62 at wave 0.
- **Expect small residuals** where the paper analyzed an imputed file and the IRW script
  dropped imputed cells, or vice versa. Order and relative spacing are the signal, not
  the third decimal.

`data_labels` tables are exempt: when the source file's own variable labels tie code to
text, the mapping is authoritative at the source and there is nothing for statistics to
add. **Every other `mapping_basis` requires this step.** Record the outcome as a row in
`itemtext/mapping_verification.csv` (`table,batch,mapping_basis,uploaded,route,status,evidence`)
with `status` one of `VERIFIED` / `PARTIAL` / `NO_ROUTE` / `NOT_NEEDED`, and `evidence`
stating the actual numbers compared. **`NO_ROUTE` is a legitimate outcome** — a source
with no per-item statistics, no range structure and no subscale totals cannot be checked,
and saying so is required rather than letting "couldn't check" read as "checked". A
`NO_ROUTE` table on an inferred `mapping_basis` should carry a `public_note` and is a
candidate for holding back from upload (see `abdullah_2024_hpbbloat_stress`).

## Step 6 — Write the output

```r
write.csv(items, file = "itemtables/<table>__items.csv", row.names = FALSE)
```

Written into `itemtext/itemtables/` (not the `itemtext/` root) — this is where
`upload.py` expects to find files (`python3 upload.py itemtables` uploads everything in
that directory). Don't upload automatically; that's a separate, explicit step (see
"Uploading", below) since it pushes to the shared `bdomingu/IRW_text:next` Redivis
dataset.

### Step 6b — Logging discrepancies (no Sheets-write tool available)

There is no tool that can write into the index workbook's NOTES column directly — same
gap as Step 1's cross-check tabs, just on the write side. When validation surfaces a
real discrepancy (item-count mismatch, partial coverage, source inaccessible), append a
row to `itemtext/itemtables/pending_index_notes.csv` (columns: `table,note`; create the
file with a header if it doesn't exist yet) and tell the user what to paste into Sheet1's
NOTES column — don't claim the index sheet was updated. This is a standing, cumulative
file like `automated_finding/license_blocked_candidates.csv` — append to it across
batches, don't delete it once a batch is written up; only remove a row once the user
confirms they've pasted it into the actual sheet.

### Step 6c — Record how the item text was matched to the item codes

**Every extraction must record its provenance**, because neither `validate_items.R`
nor `audit_batch.R` can tell a verified mapping from a guessed one — both only check
that the *set* of item/resp values matches. A table whose item text came verbatim from
the source data file's own variable labels and a table whose text was aligned by
assuming the paper lists items in code order look identical to both scripts. Without a
structured record, that difference survives only as prose in `notes.csv`, if at all.

Append a row to `itemtables/batch_<NNN>/provenance.csv` (columns:
`table,mapping_basis,text_source,source_ref,note,public_note,uploaded`; create with a
header if it doesn't exist) for **every** table, not just problematic ones. `uploaded`
is a date, filled in only once a table has actually been pushed to Redivis — it's what
distinguishes a table that was promoted out of the batch folder from one that went
missing.

`mapping_basis` — how each `item` code was tied to its `item_text`:
- `data_labels` — the source data file's own variable labels / column headers tie code
  to text. No inference. This is the strongest case and worth actively seeking: `.sav`,
  `.xlsx` and Google Forms exports frequently carry it (see `agogue_2020`, and most of
  the `alsuhibani_2022_*` / `amarilla_2020_*` / `ali_2021_*` tables).
- `paper_explicit` — the paper reproduces items alongside numbering/codes that match
  the live data's codes.
- `paper_order` — the paper lists the items but ties them to nothing; alignment is
  *inferred* from presentation order. Defensible, but say so.
- `reconstructed` — codes carry no ordering information (bare integers, or a renumbered
  final form); the mapping was rebuilt from other evidence.
- `unknown` — not established. Use this honestly rather than guessing; it marks the
  table for re-checking.

`mapping_basis` records *how* the mapping was arrived at; Step 5b records whether it was
then **checked against the data**. They are independent, and the pair is what tells you
how much to trust a table: `paper_explicit` + `NO_ROUTE` can still be a numeric
correspondence nobody verified (this was true of `aguirre_camacho_2021_champion` until its
Table 4 was matched), while `paper_order` + `VERIFIED` is solid. Anything other than
`data_labels` must have a `mapping_verification.csv` row before it is promoted to `clean/`.

`text_source` — where the words themselves came from:
- `study_materials` — this study's own paper, supplement, questionnaire, or data file.
- `canonical_instrument` — the published original instrument, not this study's materials.
- `translated_substitute` — a different language version than the one administered.
- `unknown`.

`public_note`, when non-empty, is a one-sentence caveat written for the public issues
page, used verbatim and always emitted regardless of the other fields — use it for
caveats orthogonal to provenance (e.g. `aguirre_camacho_2021_champion`, whose item text
is correctly sourced but whose scale anchors are in a different language than its items).

Then generate draft callouts for the public page:
```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/draft_issues_qmd.R itemtables/batch_<NNN>
```
This writes `fixes/itemtext_issues_draft.md`. It never edits
`../irw_site/itemtext_issues.qmd` directly — what to tell the public about a dataset is
an editorial call, so a human reviews and pastes.

### Step 6c-bis — The checklist this all reduces to

Before a table leaves your hands, all of these are true and recorded:

1. `validate_items.R` passes (item set, resp set) — hard gate, Step 5.
2. You know which of the three code-derivation patterns applies (core model §3), and for
   positional codes you diffed shipped text against the source header at that position.
3. You used the highest available source (core model §2) and **opened the data file** before
   concluding a better source didn't exist.
4. Every item has an option row for every `resp` level its own respondents used — or the
   gap is a known response-data defect and you said so.
5. `section_id` is a single trivial `<table>_1` unless there is real testlet/passage
   grouping with genuine `section_prompt` text.
6. `item_text` blank where the instrument has no stems; `option_text` blank where no labels
   exist; neither padded with numbers.
7. `resp` is used, not `raw_resp`, unless no scoring key exists anywhere including
   `data/<table>.py|R`.
8. Every deviation from literal transcription is named in provenance, and every claim in
   the note is one you actually checked.
9. A `mapping_verification.csv` row exists unless `mapping_basis` is `data_labels`.
10. `normalize_nulls.R` then `audit_batch.R` run clean, or each WARN is explained.

### Step 6d — Normalize and audit before the batch is considered done

```bash
Rscript .claude/skills/irw-auto-itemtext/scripts/normalize_nulls.R itemtables/batch_<NNN>
Rscript .claude/skills/irw-auto-itemtext/scripts/audit_batch.R    itemtables/batch_<NNN>
```

**Re-run both after ANY later edit to a CSV**, including a one-line fix made with a
script. Python's `csv` writer and R's `write.csv` disagree about absent values — a
`DictWriter` round-trip turns the bare `NA` token into a quoted `"NA"` string, which
`read.csv` silently reads back as the same value, so nothing downstream complains. Every
manual repair in this pipeline so far has needed a normalize pass afterwards, and one
(a spelling fix to `alsuhibani_2022_gcbs`) sat unnormalized in `batch_004` until a later
sweep caught it.

`normalize_nulls.R` makes the on-disk representation of absent values match the
convention across the 422 published tables (the `NA` token, as `write.csv` emits it).
`audit_batch.R` re-checks the whole batch against live data and flags row-count
anomalies, coverage gaps, and `option_text` padded with its own `resp` value.

**Note for uploads:** `upload.py` walks a directory recursively and treats *every*
`.csv` as a table, so `notes.csv`, `provenance.csv` and `audit_report.csv` would be
uploaded as if they were data. Upload from a filtered directory containing only
`*__items.csv`, never by pointing it at a batch folder.

## Idempotency & caching

- Never reprocess a table that already has a local `itemtables/{table}__items.csv` or an
  already-populated Sheet1 row, unless told to redo it. **Exception: Audit mode (below)
  deliberately targets already-done tables — that guard protects the queue workflow from
  duplicating in-flight human work and doesn't apply there.**
- Cache fetched PDFs/pages under `itemtext/.cache/<table>/` (gitignored) so retries on
  paywalled/rate-limited sources don't refetch.

## Audit mode — reprocessing tables that already have itemtext

Triggered by **"audit itemtext for X"** / **"audit the itemtext batch"**. Unlike the
queue workflow, this deliberately reprocesses tables that already have a curated Redivis
itemtext entry, to check whether that curation has drifted from the live
`irw::irw_fetch(table)` data. Motivated by
[ben-domingue/irw#1594](https://github.com/ben-domingue/irw/issues/1594) and a follow-up
audit that both found: every time a from-scratch extraction disagreed with existing
curation, the curation was the stale one, not the extraction.

1. **Candidate list** = `irw::irw_list_itemtext_tables()` directly — the ~421 tables that
   already have an itemtext entry. Don't run `list_candidates.R`'s queue diff or check
   Sheet1/index-workbook status for these; that machinery exists to avoid duplicating
   unclaimed human work on new tables and isn't relevant here.
2. **Extract** — same as Steps 2–4 above (fetch the live `item`/`resp` target via
   `table_context.R`, find the source paper, extract and structure). Write the result to
   a staging path, not `itemtext/itemtables/<table>__items.csv` — e.g.
   `itemtext/audit_staging/<table>__items.csv` — so it can never be picked up by a stray
   `python3 upload.py itemtables` before review.
3. **Diff** — run:
   ```bash
   Rscript .claude/skills/irw-auto-itemtext/scripts/diff_itemtext.R <table> itemtext/audit_staging/<table>__items.csv itemtext/audit_pending_review/<table>_diff.md
   ```
   This compares the staged extraction against `irw::irw_itemtext(table)` (current
   curation) using the same edit-ratio/Jaccard/resp-set-alignment/swap-tolerant
   instructions-section_prompt logic validated across the 100-table eval, and prints a
   suggested classification (`confirm` or `review`) plus an itemized mismatch list. This
   split is mechanical (similarity thresholds) — treat it as a starting triage, not a
   final answer; every `review` result needs the human judgment call in step 4 below,
   reading the actual mismatches rather than trusting the label. **When eyeballing
   `irw::irw_itemtext()` or `irw::irw_fetch()` output manually (outside the scripts
   above)**, always use `nrow()`/explicit `unique()` on the exact columns needed rather
   than scanning a bare `print()` or `head()` — a tibble's default print truncates to 10
   rows, and a truncated view has caused both a false "mismatch" alarm (an alphabetically-
   first subset of items looked like the wrong instrument until the full set was pulled)
   and an overstated real finding (claiming a field was "entirely missing" when a
   truncated print just hadn't shown the populated rows).
4. **Route the result into one of four statuses** (not just confirm/review — a `review`
   result always resolves into exactly one of green/yellow/red/gray):
   - 🟢 **Green** — `confirm`, or a `review` where the mismatches turn out to be noise
     (e.g. cosmetic wording, not substance). Append one row to
     `itemtext/itemtables/audit_confirmed.csv` (columns `table,date,note`; create with a
     header if it doesn't exist) and stop — no Redivis write, no further action unless
     re-audited later.
   - 🔴 **Red** — the diff shows a genuine, evidence-backed problem with the *curated*
     version (fresh extraction matches a live `irw::irw_fetch(table)` check where curation
     has a gap — missing items, missing `resp` categories, a stale resp range, items that
     don't exist in live data, etc.) that needs human review and likely replacement. File
     a GitHub issue (`gh issue create --repo ben-domingue/irw --label "data fix" --label
     "ITEMS"`, title `` `table_name` <short description> ``, body with Summary/Evidence/
     Recommended fix sections — see #1594/#1600-1607 for the template) **and** list it in
     the batch report. **If the problem looks like it could be systemic** (a mislabeled
     instrument, a swapped dictionary field) rather than a one-off, check sibling tables
     from the same paper/project before writing the issue — every apparent mislabel found
     across this skill's use turned out to be isolated to the one table once siblings were
     checked, so note in the issue whether you verified that (and how), rather than
     leaving it open-ended. **Never run `upload.py` on an audit-mode table without the user's
     explicit per-table or per-batch approval first** — filing the issue is not the same
     as approval to replace; `upload.py` replaces a table's entire content on conflict (no
     row-level merge), so nothing gets auto-uploaded. Only after explicit approval, copy
     the approved tables' CSVs from `audit_staging/` into a clean temp directory and run
     `python3 upload.py <tempdir>`.
   - 🟡 **Yellow** — the curated version is fine to keep as-is, but there's a specific,
     articulable limitation worth telling website users about (e.g. some items aren't
     documented in the one source checked, a translation is independently-derived rather
     than verbatim-sourced) — distinct from red because there's no evidence the curated
     content is *wrong*, just an honest caveat about what was and wasn't confirmed. Draft
     the exact `.qmd` `.callout-warning` block for `itemtext_issues.qmd` (match the
     existing page's format — see batch01_pilot.md for a worked example) and include it in
     the batch report for later extraction to the website; don't edit
     `itemtext_issues.qmd` directly as part of this routine.
   - ⚪ **Gray** — could not be independently confirmed at all (source blocked, no primary
     material found, or a same-instrument-different-source-language ambiguity like
     `mpsycho_rogers_ocd`'s wording variant) and there's *no evidence either way* — not
     confirmed clean (so not green) and no specific issue to document (so not yellow).
     Log via Step 6b (`itemtext/itemtables/pending_index_notes.csv`) as a candidate for
     retry later with a different source, not as a resolved outcome.
5. **Batch report**: write one `itemtext/audit_batch_reports/batchNN_<label>.md` per
   audit-mode run, using `batch01_pilot.md` as the template — a summary count table, then
   one section per status with the per-table detail (including yellow's ready-to-paste
   website text and red's issue links).

## Batch behavior

- **"Generate item text for X"** — Steps 2–6 for that one table.
- **"Process the itemtext queue"** — Step 1 to get open candidates, then work through
  them one at a time (Steps 2–6 each). Given Step 3's paper/PDF lookup is the slow,
  judgment-heavy part, don't try to batch dozens unattended — process a handful, report
  what landed vs. what's in the "couldn't fully automate" bucket, and let the user
  redirect before continuing.
- **"Audit itemtext"** — same pacing caveat as the queue: Step 3's lookup is still the
  slow part, so process a handful of already-done tables per session (start with a small
  pilot batch before committing to all ~421), write the batch report (green/yellow/red/gray
  breakdown per the Audit mode section above), and let the user redirect rather than
  trying to reprocess everything unattended.

## Expect a real "couldn't fully automate this one" bucket

The validation gate in Step 5 exists precisely because full automation isn't feasible
for every table — some papers simply don't disclose full item text (see
`tables_excluded`'s existing `"couldn't find item text"` entries), some disclose a
different item count than what's in the live data, and some only give categorical
scoring with no recoverable numeric key. **Don't treat anything short of 100% coverage
as a failure of the skill** — a partial extraction with an honest discrepancy note in
`itemtables/pending_index_notes.csv` is a correct outcome, not an incomplete one. Move
on to the next candidate rather than forcing a fabricated match.

## Uploading (separate, explicit step — don't do this automatically)

```bash
python3 upload.py itemtables
```

Uploads every `*.csv` in `itemtext/itemtables/` to `bdomingu/IRW_text:next` on Redivis
(prompts before overwriting anything already there). Only run this when the user
explicitly asks to upload — it's a shared-system write, same caution as any other
Redivis upload in this repo.
