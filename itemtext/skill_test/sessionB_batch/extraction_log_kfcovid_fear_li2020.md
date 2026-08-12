# Extraction log: kfcovid_fear_li2020

## Source used
Dictionary row's "URL (for data)" (https://osf.io/m2v3h/) is an OSF node containing exactly
one file, `Knowledge and Fear of COVID-19 and Perceived Stress.xlsb` (downloaded via the OSF
API's `osfstorage` listing and its `download` link; cached at
`.cache/kfcovid_fear_li2020/data.xlsb`). This is the authors' own analysis workbook, not a
generic raw-data dump: it has sheets `Demographics`, `Descriptive Statistics`, `Correlations`,
`Reliab Analysis`, `Survey 1`, `Survey 2`, `Survey 3`, `Codebook`, `DataSet`.

- `Codebook` sheet: one row per survey item, columns `Code / Survey / Question or Statement /
  Set of Possible Responses` — gives every item's raw variable code (`Q101`...`Q106`, and a
  typo'd `Q017` for the 7th item — see Ambiguities), its literal statement text, and its
  response-scale coding.
- `Survey 2` sheet: a clean, presentation-order table of just the Fear-of-COVID-19 items —
  columns `Statements / Choice of Options / Average Score` — with the 5-point Likert coding
  spelled out per row ("1=strongly disagree, 2=disagree, 3=neither agree nor disagree,
  4=agree, 5=strongly agree").
- `DataSet` sheet: the actual response-level data, with column headers `Q101...Q107` (all
  seven items correctly labeled here, confirming `Q017` in `Codebook` was a typo — see below).

Also fetched the open-access paper via PMC (https://pmc.ncbi.nlm.nih.gov/articles/PMC7546663/,
DOI 10.1016/j.dib.2020.106395) for corroborating text: "The second questionnaire was the
FCV-19S Scale and consisted of seven items." and "Both the FCV-19S and PSS-4 used a five-point
Likert scale." The paper body does not reproduce item text itself — the OSF workbook is where
the actual instrument content lives, consistent with SKILL.md's expectation that item text
often lives in a companion/supplementary file rather than the main paper body.

## Bare-integer item validation (has_bare_integer_items = TRUE)
Ground-truth `item` values are `"101".."107"`. Per SKILL.md, resp-range plausibility alone is
not sufficient — cross-checked instead against:
1. **`DataSet` sheet column headers** — the response-level data itself has columns literally
   named `Q101, Q102, Q103, Q104, Q105, Q106, Q107`. These are the authors' own variable codes,
   directly tying each ground-truth `item` value to a specific `Codebook`/`Survey 2` row — not
   an inference from position alone.
2. **`Codebook` sheet row order** — for Q101-Q106 the `Code` column matches directly. The 7th
   FCV-19S row is labeled `Q017` in `Codebook` (evidently a fat-fingered `07`→`017`/digit-swap
   typo by the authors), but its position (7th and last row of the `Survey 2` = 2 block, right
   after Q106) and its statement text ("My heart races or palpitates when I think about getting
   coronavirus-19.") both identify it as item 107 — and `DataSet`'s own column header for that
   same variable is spelled correctly as `Q107`, resolving the ambiguity independently of
   position alone.
3. **Content cross-check against the published FCV-19S** (Ahorsu et al., 2020) — the 7
   statements and their order in `Survey 2` exactly match the well-known published Fear of
   COVID-19 Scale in its standard item order (afraid of COVID → uncomfortable thinking about it
   → clammy hands → afraid of losing life → nervous/anxious from news → can't sleep worrying →
   heart races/palpitates). No wording deviation, translation, or adaptation was found; this is
   the scale used verbatim.

Result: **101-107 map, in order, one-to-one with the 7 `Survey 2` statements** (Q101→101 ...
Q107→107). All three checks (variable-code match, sheet-order match, and published-scale
content match) agree — this is not resp-range-only reasoning.

## Structure discovered
Single instrument, single non-testlet section (`kfcovid_fear_li2020_fcv19s`) — the 7 FCV-19S
items form one flat Likert battery with no shared passage/testlet grouping, so `section_prompt`
is blank per SKILL.md's "no real grouping → single trivial section_id, blank section_prompt"
rule. `instructions` combines the paper's own framing sentence ("The FCV-19S ... consisted of
seven items" / "used a five-point Likert scale") with the `Codebook`'s literal response-scale
coding, since no participant-facing preamble ("Please indicate...") was disclosed anywhere in
the paper or the OSF workbook — only the item statements and the numeric-to-label scale mapping
were disclosed, so the instructions field is limited to what was actually disclosed rather than
inventing standard FCV-19S administration language that wasn't present in this source.

`correct_response` is blank for all items — FCV-19S is a self-report attitude/fear scale with
no scoring key (no right/wrong answers).

## Structure of output
One row per (item, resp) = 7 items x 5 response levels = 35 rows. `option_text` uses the
`Codebook` sheet's exact capitalization ("Strongly Disagree", "Disagree", "Neither agree nor
disagree", "Agree", "Strongly agree") rather than `Survey 2`'s all-lowercase variant of the same
text — the two sheets disagree only in capitalization, not content; `Codebook` was picked as
the source of record since it's the canonical variable-level codebook.

## OCR / image-based extraction
Not needed. All text was read directly from the `.xlsb` workbook's cell values (via
`pandas.read_excel(..., engine="pyxlsb")`) and from the PMC HTML full text — no image, scan, or
PDF-rasterized page was involved anywhere in this extraction.

## Derived vs. directly-read values
None of `item_text`, `option_text`, `instrument`, or the item->101-107 mapping was derived or
computed — all were read directly from the `Codebook`/`Survey 2`/`DataSet` sheet cells or the
PMC paper text. The only compositional step was `instructions`, which concatenates two directly
quoted/paraphrased-from-source fragments (the paper's item-count/scale-type sentence and the
codebook's response-scale coding) rather than inventing new wording; this is noted above rather
than presented as a literal single quoted span.

## Source type used
Raw-data-file (companion OSF Excel workbook) — specifically its `Codebook` and `Survey 2` tabs,
which function as an author-provided item/response codebook — corroborated by the paper's own
HTML full text (PMC open-access copy) for framing language. Not a PDF manual, not a scanned
appendix, no OCR involved.

## Ambiguities
- `Codebook`'s `Code` column has a typo for the 7th FCV-19S item (`Q017` instead of `Q107`);
  resolved via `DataSet`'s correctly-spelled `Q107` column header and the item's position/content
  match — see validation section above. Logged here in case anyone re-derives from `Codebook`
  alone and hits the same apparent mismatch.
- `Codebook` and `Survey 2` give the response-scale labels in different capitalization
  ("Strongly Disagree" vs. "strongly disagree"); `Codebook`'s Title Case was used as the
  transcribed `option_text`, `Survey 2`'s lowercase variant was not used but is an equally valid
  reading of the same underlying scale.
- No participant-facing instructional preamble (e.g. "please rate the following statements") was
  found in either the paper or the OSF workbook; `instructions` is therefore built only from what
  the paper/workbook actually state about the instrument (item count + scale type + scale
  coding), not a reconstruction of the standard FCV-19S administration script.

## Items not extracted
None — all 7 ground-truth items (101-107) and all 5 ground-truth resp values (1-5) were
extracted and matched exactly against `.gt_kfcovid_fear_li2020.rds`
(`identical(sort(unique(item)), ...)` and `identical(sort(unique(resp)), ...)` both TRUE).
