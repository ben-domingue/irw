# ENEM item-text extraction rules

The rules every year must follow, so 13 years come out the same way and a
later reader can tell whether a table was built correctly. Derived from the
2023 pilot (#1848) and the rulings in `itemtext/BATCH_PROCESS.md`.

Anything not covered here is a question for the user, not a judgement call for
whoever is extracting. **When a year does not fit these rules, stop and report
it — do not improvise a convention.**

## R0. The join key is INEP's, never ours

`item` is always `CO_ITEM`, taken from `ITENS_PROVA_<YYYY>.csv` by joining the
booklet's own printed position to that file's `CO_POSICAO`, restricted to the
year's `standard_prova_codes` as declared in `data/enem_<YYYY>.R`.

- Never assign item codes positionally (`enumerate`, `item_{i+1}`).
- Never invent, guess or carry over a code from another year.
- The item set of the finished table must equal the live table's item set
  exactly. `validate_items.R` is the gate and it is not advisory.

`standard_prova_codes` is NOT the accessibility booklet. In 2023 the published
set is 1191-1194/1201-1204/1211-1214/1221-1224; the accessibility booklet is
1197/1207/1217/1227. Read the codes out of the year script; do not assume.

## R1. Source order

1. **Accessibility edition where the year has one** — DOSVOX plain text for
   2023-2025, the LEDOR/LARANJA booklet PDF for 2017-2022. Chosen because INEP
   wrote verbal descriptions of figures, graphs and tables into it: 13 of 90
   items in 2020 and 20 of 90 in 2022 carry an INEP-authored "Descrição d...".
   The standard booklet carries 0 and 1 respectively, so using it would mean
   writing 130-200 descriptions ourselves across ten years.
2. **Standard booklet PDF** for 2013-2016, which have no accessibility edition
   at all, and for the items the accessibility booklet swaps away (R2).

The accessibility wording is NOT the printed wording: notation is spelled out
("gramas por mol" for g/mol, "Q indice 2" for a subscript) and credits move.
In 2023 only 2 of 44 MT and 5 of 45 CN items matched the printed booklet word
for word. Ruled 2026-09-11: ship it as is and say so in every `note` and
`public_note`. Carry that disclosure every year, worded for the year's source.

## R2. Diff the booklets BEFORE joining

The accessibility booklet swaps items rather than dropping them. For each area:

    std  = items in ITENS_PROVA at the year's standard_prova_codes
    acc  = items in the accessibility CO_PROVA
    std - acc  -> must come from the standard booklet PDF
    acc - std  -> NOT in the response tables; do not ship

Known counts: 2017:9, 2018:12, 2019:3, 2020:16, 2021:14, 2022:5, 2024:4,
2025:3. Recompute per year rather than trusting this list, and report a year
whose count differs.

## R3. Annulled and set-aside items

- `TX_GABARITO` not in A-E: no scorable key, dropped from the response tables
  by #1942, so no text ships. Do not include it.
- `IN_ITEM_ABAN = 1` with a valid key: KEPT and disclosed (ruled 2026-09-11).
  Name it in `note` and `public_note` with INEP's `TX_MOTIVO_ABAN`. Check this
  flag every year; the key-only rule misses it. 21 such items sit in the
  published tables across 2014, 2019, 2021, 2022, 2023 and 2025.

## R4. Foreign-language items (LC only)

The five English and five Spanish items are the object of study. Keep the
stimulus verbatim in `item_text` as administered. `language` names the
administration (Portuguese), not the language of an individual cell.

LC carries 50 items over 45 positions: positions 1-5 appear twice,
disambiguated by `TP_LINGUA` (0=English, 1=Spanish) and by the booklet's own
"(opcao ingles)"/"(opcao espanhol)". Both blocks ship; each candidate answered
one, which is why those ten items show ~50% response counts and that is
correct, not missingness.

## R5. Figures with no text

Ruled by the user 2026-09-15, following 2023:

- Stimulus is a figure the source does not describe: write a description in
  `item_text`, mark it inline `(gerada por IA)`, set
  `description_source=partly_generated`. Owes an issues-page entry.
- The printed OPTIONS are bare figures with no text: `option_text` and
  `option_text_translated` are NA. A generated label on a response category
  would be joined to responses as if it were printed. `correct_response` and
  `resp_raw` keep the options addressable.
- Never generate an `option_text`.

## R6. No translations

`translation_source=not_translated`; all four `_translated` columns blank
(#2179, #2180). The note must say why: INEP states no licence for the provas,
so the gov.br footer's CC Atribuição-SemDerivações 3.0 applies and a
translation is a derivative it does not permit. No English in any base field.

## R7. Columns and values

`table, section_id, item, instrument, instructions, section_prompt, item_text,
correct_response, option_text, resp, item_text_translated,
option_text_translated, instructions_translated, section_prompt_translated,
language, resp_raw` — the 2023 order, kept for every year.

- `resp` 0/1: 1 on the option whose letter equals `TX_GABARITO`.
- `resp_raw` the printed letter A-E. Spelling per #2094, never `raw_resp`.
- `correct_response` `TX_GABARITO`.
- `section_id` `<table>_1`, `section_prompt` NA, unless a year genuinely has
  shared passages — verify, do not assume 2023's answer.

  **RULED 2026-09-15 by the user: a shared passage goes in `section_prompt`,
  not repeated into each item's `item_text`.** 2025 LC prints "Texto para as
  Questões de 6 a 10" above a 3,892-character crónica serving five items. Those
  five items get their own `section_id` and carry the passage ONCE in
  `section_prompt`; `item_text` holds only each item's own stem. Repeating it
  into five `item_text` fields would make one passage look like five different
  stimuli to anyone counting, diffing or grouping item text.

  A shared passage is the case R7 reserves `section_prompt` for, so this is the
  schema working as intended rather than an exception to it. Detect it as orphan
  text between an option block and the next question marker: marker-based
  segmentation otherwise swallows the passage into the PREVIOUS item's option E
  and leaves the five items with no stimulus, and no count anywhere moves.
- `instructions` the booklet cover. Strip screen-reader-only lines (the 2023
  "soletrar" line): candidates in the response tables never read them.
- Five option rows per item, in A-E order.

## R8. File hygiene, which has already gone wrong once

- Write with R's `write.csv`, then run `normalize_nulls.R` and confirm
  "0 of N normalized". The literal `NA` token is the corpus convention.
- **Never rewrite a shared index CSV.** `pending_index_notes.csv` and
  `mapping_verification.csv` are append-only. Rewriting them flipped CRLF to
  LF once and turned a 4-row addition into ~1,800 changed lines that conflicted
  with every other open itemtext PR (#1848, fixed by Ben in b4e4cfc).
- Preserve each file's existing line endings and quoting. Check the bytes; some
  of these files are CRLF and `file` does not say so.
- Diff-size check before committing: a 4-row addition must show as 4 added
  lines. If it shows hundreds, the formatting was changed and must be redone.

## R9. Per-year layout

    itemtext/itemtables/batch_enem_<YYYY>/
      enem_<YYYY>_1mil_{ch,cn,lc,mt}__items.csv
      provenance.csv  notes.csv  verification_merged.csv  audit_report.csv
      scripts/        (the year's build scripts + README)

Batch named `batch_enem_<YYYY>`, not a number: the queue runner allocates
numbers sequentially and would collide. The `batch` column equals the
directory name. `queue_state.csv` rows go `excluded` -> `done` with batch and
timestamp — never to `pending`.

## R10. Gates, all of them, before any commit

    validate_items.R <table> <items_csv> --resp-csv <corrected response CSV>
    lint_verification.R itemtables/batch_enem_<YYYY>
    check_provenance.R
    normalize_nulls.R itemtables/batch_enem_<YYYY>
    audit_batch.R itemtables/batch_enem_<YYYY> --resp-dir <corrected CSVs>

`validate_items` and `audit_batch` read 45M-row CSVs and need tens of GB: run
them under sbatch at 64-96G, never on a login node.

**Everything a Slurm job reads must be on shared storage.** Per-year working
output goes in `/scratch/users/<user>/itemtext_years/<YYYY>/`. A compute node
cannot see the login node's `/tmp`, and the failure mode is "cannot open the
connection" on all four tables at once, which reads like a data problem and is
not one.

Response CSVs are the #1942-corrected build, not the pre-fix ones.

## R11. What to escalate rather than decide

- A year whose booklet-diff count differs from R2's list.
- A year with no accessibility edition where R2 expected one, or vice versa.
- Any item whose text cannot be recovered from either booklet.
- A year where LC's 50-over-45 structure does not hold.
- Any case where following a rule here would require inventing an item code,
  an option letter, or a `resp` value.

## R12. Stacked fractions are restored from the bar, not from the text

A printed fraction is a numerator, a drawn rule and a denominator. Text
extraction reads them in layout order and emits two ordinary tokens, so `7/5`
becomes `7 5` and `OR = (1/4) OM` becomes `OR = 1 4 OM`. No character is wrong
and nothing is missing, so **every content gate stays green while the
arithmetic is gone**.

R12 exists because a stacked numerator is printed at *full body size* on a
raised baseline. The size test in `48_mark_scripts.py` cannot see it by
construction. The only reliable signal is the bar, which is a drawing.

`53_stacked_fractions.py` restores them, and its rule is deliberately narrow —
a missed fraction is better than an invented one:

1. A bar is a drawn rect no taller than 1.8pt, 3–70pt wide, clear of the
   header and footer bands. Identical rects are deduped: the same rule is
   sometimes stroked twice, and that is one bar.
2. Any two bars sharing a baseline are a table rule, not a fraction.
3. Text must sit tightly above **and** below, each no wider than 1.25× the bar
   and centred on it within 30%. Word bboxes carry the font's ascender and
   descender, so the numerator's box dips *below* the bar and the
   denominator's rises *above* it — the tolerances must allow for that or
   nothing matches.
4. The flattened form must actually occur in that page's reading order, with
   token boundaries on both outer edges.
5. The shipped row is located by an exact context substring, so the rewrite is
   anchored to the item the bar was measured in.
6. Rewrite only where the flattened form occurs in the row exactly as often as
   the page has bars for that pair. **Any mismatch is reported, not guessed.**

Steps 4 and 6 are what keep `ABO` from becoming `AB/O`, an axis label reading
`anos x` from becoming `s/x`, and `Teste 1:` from becoming `Teste/1`.

Two traps inside the rule itself, both silent:

- The page text is normalised to single spaces, but **the stored stem keeps the
  line break the fraction was printed across** (`'54\n100'`). Matching stored
  text with the page pattern finds nothing while reporting success.
- Rewriting the first matching row is not enough. An item is five rows, one per
  option, each carrying the same stem.

Where the rule declines — side-by-side fractions on one printed line, or a
reading order that separates the numerator from its denominator entirely — the
fix goes in `PATCH_STEM` with the page it was read off cited. Nothing goes in
that table that cannot be verified that way.

## R13. A figure description may belong to a different item

The accessibility editions usually set a figure description inline. Some are
collected **at the foot of the page**, after the last item's options, and those
describe an item printed earlier on the page or on the next one. A parser that
attaches trailing text to the item it follows puts them on the wrong item.

Again no gate can see it: the stem is longer than it should be, not shorter.
2018 CN 59858 asks about the energy released by oxidising glucose and its stem
ended with a description of an electrical circuit.

The audit in `54_relocate_descriptions.py` flags any stem whose last
`Descrição ...:` block starts in its final 45% *and* follows a question closer
— a well-formed item describes its figure before asking about it. Three things
trip it and only the first is a defect:

- **misplaced** — belongs to another item; goes in `MOVES` with the evidence;
- **option set** — `Descrição das alternativas` describes the five options, so
  it correctly follows the question;
- **own figure** — printed after the options but genuinely this item's.

Never strip a misplaced description without first looking for its owner. All
three found so far had one, each already shipped and each carrying no
description of its own, so the fix was a move. `--apply` refuses to run if the
audit turns up a case in neither list.
