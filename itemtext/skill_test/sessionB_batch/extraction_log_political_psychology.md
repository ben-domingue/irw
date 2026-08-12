# Extraction log: political_psychology

## Source used
Dictionary URL (https://osf.io/3pwvb/) and DOI (10.5334/jopd.54) both point to the same
OSF project ("Year Long Longitudinal Study (United States)", Brandt, Turner-Zwinkels &
Kubin 2021, *Journal of Open Psychology Data* 9(1)). Fetched and cached under
`.cache/political_psychology/`:
- `paper.pdf` — open-access data paper
  (https://openpsychologydata.metajnl.com/articles/54/files/submission/proof/54-1-461-2-10-20210923.pdf)
- `codebook1.html` — full `rcodebook`-style HTML codebook from the OSF "Data and
  Codebook" folder (item labels, response-option labels, missingness per variable)
- `yllanon.csv` — the actual raw long-format data file linked from the OSF "Data and
  Codebook" folder (only column headers/first rows used, to recover the CSV's literal
  column order; not used as a data source otherwise)
- `wave2.docx` — one wave's Qualtrics Word-format materials (from the "Materials - Word
  Format" folder), used to confirm literal item wording/response anchors matched the
  codebook exactly and to find the per-wave intro framing text
- **`data/political_psychology.R`** — the repo's own IRW processing script for this
  table. This was the decisive source (see below), found via
  `grep -rl "political_psychology" data/`.

## Source type used
Primarily **source code + raw data column headers**, not just the paper/codebook. The
processing script's `pivot_longer(cols = !c(id, date))` turns column order into `item`
ID order via `unique(df$item)` (first-appearance order == column order), so the mapping
from bare-integer `item` to construct is fully mechanical once the exact input column
order is known. Text content (item stems, response-option labels) came from the codebook
and was cross-checked against `wave2.docx`.

## Bare-integer check (has_bare_integer_items = TRUE)
Per SKILL.md's bare-integer rule, range-plausibility alone was explicitly avoided.
Instead:
1. Read `data/political_psychology.R` in full. It reads `yllanon.csv`, lowercases names,
   drops `enddate, wave, check, gender, ethnic, edu, inc, state, relig, age, responseid,
   duration (in seconds)`, computes `date` from `startdate`, drops `startdate`, then
   `pivot_longer(cols = !c(id, date))`, then assigns `item_id = row_number()` over
   `unique(df$item)` (first appearance = original column order).
2. Downloaded the actual `yllanon.csv` from OSF to read its literal header row (not
   assumed from the codebook's alphabetized "keywords" metadata list, which is a
   different, non-column order): `StartDate,EndDate,Duration (in seconds),ResponseId,
   def,crime,terror,poor,health,econ,abort,unemploy,blkaid,adopt,imm,vaccines,guns,djt,
   interest,friends_1..5,tense,death,ewry,values,ideo,partyid,votereport,gender,ethnic,
   edu,inc,age,state,relig,wave,voting,climate,check,beh_att_1,beh_att_2,beh_att_3,
   beh_identity,virusthreat,quarantine,sickleave,fourth,id`.
3. Applying the script's `select()` drops and the trailing `date` append gives this exact
   `item` 1-37 order: `def, crime, terror, poor, health, econ, abort, unemploy, blkaid,
   adopt, imm, vaccines, guns, djt, interest, friends_1, friends_2, friends_3, friends_4,
   friends_5, tense, death, ewry, values, ideo, partyid, votereport, voting, climate,
   beh_att_1, beh_att_2, beh_att_3, beh_identity, virusthreat, quarantine, sickleave,
   fourth`.
4. **Cross-validated against the cached ground truth's per-item `resp` ranges**, which is
   a much stronger check than range-plausibility because several variables in this
   instrument have distinctive, non-generic ranges after the script's own recoding:
   `abort` and `djt` are recoded to 1-4 (not 1-7), `votereport` and `voting` are recoded
   to 1-3. If the column-order mapping above were wrong, these distinctive ranges would
   land on the wrong item IDs. Checked: item 7 -> `1,2,3,4` (abort) ✓, item 14 ->
   `1,2,3,4` (djt) ✓, item 27 -> `1,2,3` (votereport) ✓, item 28 -> `1,2,3` (voting) ✓,
   items 25/26/29/30-37 (ideo, partyid, climate, beh_att_1-3, beh_identity, virusthreat,
   quarantine, sickleave, fourth) all -> full `1,2,3,4,5,6,7` ✓. All 37 items' observed
   resp sets in the ground truth matched what the recode logic predicts for that
   variable, so no ambiguity was resolved by range-plausibility alone — every item's
   *distinctive* range was used as the check.
5. Result: **item mapping confirmed with no discrepancy.** `unique(item)` in the
   candidate output matches the ground-truth `1`-`37` set exactly, and per-item `resp`
   sets match exactly (verified in the build script's own validation step, printed
   `item match: TRUE`, `resp match: TRUE`).

## OCR / image-based extraction
None needed. `paper.pdf` has a native text layer (extracted cleanly with `pdftotext`);
`codebook1.html` and `wave2.docx` are native text/markup, not scanned images.

## Derived vs. directly-read values
- **`instructions`** ("This survey consists of one section where you will complete items
  about your political attitudes.") is directly read from `wave2.docx`'s per-wave intro
  block, used as representative wording for the standard framing given before the item
  battery each wave; exact consent/payment boilerplate around it (varies by wave) was
  excluded since it isn't part of the item-answering task itself.
- **`votereport` resp=3 option_text** ("I did not vote / I planned to vote, but I
  forgot") is a **derived, non-literal combination**, not literal source text. The
  script recodes original codes 4 (`I did not vote`) and 5 (`I planned to vote, but I
  forgot`) both into `resp = 3`; `option_text` reflects both merged source options rather
  than a single verbatim string, flagged here per the terseness/literal-transcript rule.
- **`voting` option_text** (`Donald Trump` / `Hillary Clinton` / `A different candidate`)
  is inferred: the raw CSV stores this variable as free text `'trump'/'clinton'/'other'`
  (confirmed from `yllanon.csv`'s literal cell values), which the script maps to 1/2/3.
  The codebook's own label set for a variable named `voting` uses a different 6-category
  scheme (a stale/inherited variable label, most likely for a difference source table),
  so `'other'` was matched to the closest wording available, "A different candidate",
  by analogy with the near-identical `votereport` item rather than transcribed verbatim.
- All other `item_text` and `option_text` values are directly transcribed from
  `codebook1.html`'s per-variable label/level text, cross-checked against `wave2.docx`
  and found to match exactly (literal wording, including source typos preserved as-is,
  e.g. "near futures", "has gone seriously off track", "youself").
- Unlabeled Likert scale points (2, 3, 5, 6 on the 7-point items; 2/3/5/6 not present on
  4-point items) have blank `option_text`, matching the codebook which only gives verbal
  anchors at the labeled points (endpoints + midpoint, or just endpoints for `interest`)
  — not invented.

## Structure of output
- One `section_id` per item (`political_psychology_<n>`) with blank `section_prompt`,
  except two genuine shared-stem testlets:
  - `political_psychology_friends` (items 16-20, `friends_1..5`): shared stem "How
    willing would you be to be friends with people from the following groups?", with
    `item_text` holding just the target group (Liberals/Conservatives/Moderates/
    Republicans/Democrats).
  - `political_psychology_behpetition` (items 30-32, `beh_att_1..3`): shared stem "How
    likely would you be to sign a petition in support of the following issues?", with
    `item_text` holding just the issue (increase aid to the poor / stimulate the economy
    / spending on healthcare).
- `instrument` is the same literal string for all rows (per SKILL.md: applies to the
  whole table regardless of `section_id`).
- 245 output rows = one row per (item, resp) pair actually observed in the ground truth
  for that item (37 items x mostly 7 resp levels, minus the 1-4-only items `abort`,
  `djt`, `votereport`, `voting`).

## Ambiguities
- `voting` option_text for "other" (see Derived section above) — best-effort match to
  codebook wording for an analogous variable, not a literal transcript of a label that
  exists for this exact variable/coding.
- `votereport` resp=3 is a merged category from two distinct source response options.
- The instrument doesn't have one single overarching name in the source; "Year Long
  Longitudinal Study of Americans (2019-2020): core wave battery" is drawn from the
  OSF/codebook title (`Year Long Longitudinal Study (United States)` /
  `Year Long Longitudinal Study of Americans (2019-2020)`) with "core wave battery"
  appended to distinguish it from the one-off demographic/COVID/behavioral-intention
  items also collected in this study but outside this table's 37-item core.
- `check` (attention-check item) was correctly excluded — it is dropped by
  `select(-check)` in `data/political_psychology.R` before the pivot, consistent with it
  not appearing among the 37 items.

## Items not extracted
None. All 37 ground-truth items were mapped, matched, and given item_text; all 245
(item, resp) pairs present in the ground truth got an output row. `resp` values match
`irw::irw_fetch("political_psychology")$resp` exactly (verified against the cached
ground truth, not a live fetch, per the batch instructions).
