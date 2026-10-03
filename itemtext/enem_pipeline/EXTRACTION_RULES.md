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
- Text recovered from INEP's own standard booklet is not generated text
  and is not marked. R15 has the two conditions; anything outside them is
  generated text and belongs to this rule.

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
- A recovery that does not satisfy **both** of R15's conditions.
- Removing a rendering of a stimulus that already shipped, even in
  favour of a demonstrably correct one (R13's replace case).

## R14. A table the accessibility edition dropped is recovered from the standard one

The accessibility editions normally transcribe a table into prose --
`Descrição do quadro: ...`. Sometimes they do not: the stem still points at
the table (*"O quadro apresenta a potência aproximada de equipamentos
elétricos"*) and the numbers are simply gone. The standard edition prints them.

This matters because IRW item text is read for **linguistic complexity**, not
for answerability. A word count over an item whose table vanished is a word
count of the wrong item. (Conversely, an undescribed *figure* costs only
answerability, and under that framing is not a defect worth chasing.)

No gate sees it: the stem is shorter than it should be, and well-formed.

**Scope it by measuring, because the obvious filter is mostly false
positives.** Asking "which stems point at a quadro/tabela and carry no
transcription of it?" returns 51 stems. They sort out as:

- **2013 / 2015 / 2016** come from the standard booklet, which has no
  `Descrição` convention at all -- their tables are already inline as a column
  dump (2013 MT 42907 carries 51 digits; 2016 MT 53721, 268). All false
  positives, and they are the majority.
- Three more are ordinary Portuguese or an already-described table:
  *"Segundo quadro"* is a scene in a Dias Gomes play (2017 LC 31891),
  *"quadros"* are comic-strip panels (2022 LC 140567), and 2021 CN 84331's
  table is described as *"Descrição da imagem: Quadro intitulado ..."*.

Four real cases remain, all 2018 -- and 2018 is not an outlier (28% of its
items carry a `Descrição` block, against 23-36% across the accessibility
years), so this is scattered, not systematic.

Two things the ratio-based version of this scan got wrong, both worth
avoiding: measuring the printed stem WITHOUT cutting the option block reports
47 of 128 items as short when the true figure is 6; and the remaining ratio
outliers are dominated by graph axis numbers and source credits rather than
prose -- 2018 LC 87507's "gap" is a line of mojibake that the standard booklet
has and our text correctly does not.

`55_recover_tables.py` carries the four, each transcribed from the standard
booklet and citing its page, laid out the way that edition extracts (header
cells then values, column order) so the corpus stays internally consistent.
Every character is INEP's own, so **no `gerada por IA` marking is owed** --
this is the standard-booklet gap-filling R2 already prescribes, and R15 states
the conditions under which that holds.

Anchors tolerate an optional `_` or `^` between any two characters. Hard-coding
the markers couples this pass to `48_mark_scripts.py`, and a change there would
break the anchor silently.


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

- **misplaced** — belongs to another item; goes in `OPS` with the evidence;
- **option set** — `Descrição das alternativas` describes the five options, so
  it correctly follows the question;
- **own figure** — printed after the options but genuinely this item's; goes
  in `KEEP` with the evidence, *including* when the item is also an `OPS`
  donor whose own block survives the move.

Never strip a misplaced description without first looking for its owner.
`--apply` refuses to run if the audit turns up a case in neither list.

### What the full 2013–2025 read added (2026-10-02, #2462)

The first three cases were all the same easy shape: one block, at the end of
the donor, going to an owner that had none. Scaling to 30 blocks broke every
one of those assumptions, so each operation now states the four things that
cannot be inferred.

**Which block.** 10 of 27 donors carry two description blocks, one their own
and one misplaced, and in 7 the misplaced block is *not* the last. Taking the
last block would have corrupted both items in those cases — 2018 MT 111725's
page-foot blocks are the frequency quadro of QUESTÃO 156 followed by 157's own
cartesian-mesh figure. `cut_from` names the block verbatim.

**Where it ends.** A description is not always the tail of the stem. 2022 CH
44230 prints its own question *after* the block, so a cut that runs to the end
of the stem carries the question off with the figure. `cut_to` names the text
that follows; absent means the block genuinely runs to the end.

**Where it lands.** The relocated block goes where the booklet printed it:
after the stimulus, **before the sentence that asks the question**. Appending
it to the end of the recipient — what this pass did until 2026-10-02 —
reproduces in the recipient the exact shape this rule calls malformed, which
is why `KEEP` used to carry the recipient 89518. It also breaks back-
references: 2018 MT 15884's surviving description opens *"A mesma figura
anterior"*, which points at nothing unless the moved block precedes it. Where
the recipient is an LC item with an empty `TEXTO I`/`TEXTO II` slot, that slot
is the insert point and decides itself.

An anchor must span the **label** of an existing block, not just its body:
anchoring on the body inserts the new block between a label and the text it
introduces, leaving two `Descrição ...:` lines and an orphaned body.

**Whether it lands at all.** Sometimes the recipient already has the content by
another route, and then the block is removed from the donor without being
re-homed (`op="drop"`). All three cases are 2018 quadros that R14 already
recovered from the standard booklet, which is the edition the candidates in the
response tables actually sat — so the standard rendering is the one to keep and
the accessibility prose would merely state the same figures twice. The block
still has to leave the wrong item. Note that `55_recover_tables.py` runs
*after* this pass, so a drop is justified by the finished state of the year,
not by the state mid-pipeline.

### Replacing a corrupt rendering — NOT YET RULED

2022 CH 97262 is the one case where the recipient already held the block's
content but **wrongly**: its `TEXTO 2` is a scrambled dump of the infographic
with the percentages in one order and the labels in another, so read in
document order it pairs *Mulher sem cônjuge e com filho(s)* with 30,4 % where
the printed figure is 56,9 %. The item asks which factors intensify
discrimination, so the scramble inverts the answer. The relocated prose block
carries the correct pairings and **replaces** the dump.

This is the only operation in the pass that deletes shipped text, and deleting
a shipped rendering in favour of a better one is not covered by R2, R13, R14 or
R15. It is applied and flagged for an explicit ruling rather than treated as
settled; see R11. If the ruling goes the other way the fix is to keep both
renderings, which is a one-line change to that entry.

## R16. A glyph the booklet DRAWS is recovered from the drawing

Ruled 2026-10-02 (#2462): *"let's apply the same rule as for fractions — we are
not really generating, we are only looking and recovering in a feasible
manner."*

A radical, an equilibrium arrow, a capital delta and a minus sign are not
always characters. In these booklets they are sometimes **vector artwork**, so
the text layer has a hole where they are printed and extraction yields

    Utilize 1,7 como aproximação para 3.             (2013 MT 16538)
    Cl_2 (g) + 2 H_2O (l)  HClO (aq) + H_3O^+ (aq)   (2013 CN 29002)

No character is wrong and none is missing, so — as with R12 and R13 — no
content gate can see it, while the mathematics and the chemistry are gone.

R12 already settles the principle for the fraction bar: *"the only reliable
signal is the bar itself, which is a drawing, not text"*, and a fraction
restored from it is recovery. R16 states the same for a glyph. Reading
`page.get_drawings()` and writing the character INEP drew adds nothing the page
does not already say, so it owes no `(gerada por IA)` marking and no
`description_source=partly_generated` — the same reasoning as R15, one step
further out.

**It is `⇌`, not `→`.** The review that surfaced these called them "reaction
arrow lost". Writing `→` would ship a one-way reaction where INEP printed an
equilibrium, inverting the chemistry of three items. The geometry decides it:
an equilibrium arrow is **two antiparallel harpoons** — one shaft
left-to-right with its head at the right end, a second right-to-left with its
head at the left. Two parallel arrows would mean something else, so the
opposite-heads test is load-bearing, not decoration.

`57_drawn_glyphs.py` implements it, and the shape matters as much as the rule:

- **Geometry audits; an explicit table applies.** The audit is what makes the
  pass useful on a new year, and it refuses to run when a page carries a drawn
  glyph the table does not account for — R13's contract.
- **A drawing is a glyph only inside an intra-line text gap.** Over the 30
  booklets the pipeline reads, that takes the radical signature from 15 hits to
  3 and the one-drawing equilibrium from 6 to 5.
- **The gap alone is not enough.** A hook is a radical only with its
  **vinculum** — the separate zero-height line over the radicand; requiring it
  drops a diagram element between two "Eletricidade" labels. A harpoon is an
  equilibrium only with its **antiparallel partner**; requiring it drops a
  figure element between "SOLO" and a question header. A sweep that stops at
  the gap reports no false positives only because it has not looked.
- **Zero-height paths are real.** The vinculum has `rect.height == 0.0`, so the
  usual `height > 0.5` filter silently discards it.
- **Anchoring the geometry automatically to a shipped cell does not work**, and
  the table exists because of it. The spans adjoining a gap are often a
  fragment (`O (l) `, `+`) that recurs across items — attempting it offered to
  write a radical into two unrelated 2013 MT items and an arrow into two
  unrelated 2015 CN ones. Widening to the whole line needs pymupdf's line
  grouping, which splits a line *at* the gap; grouping by baseline instead
  scatters every sub- and superscript onto its own row, so the line reads
  `Cl (g) + 2 HO (l)` and cannot match a shipped `Cl_2 (g) + 2 H_2O (l)`.

Where a glyph is a **sub-path of a larger drawing** the audit cannot isolate it
and the table carries it alone, with the measurement: 2015 CN 25964's two
deltas are sub-paths of one stroked drawing and its two minus signs of another,
and they sit inside a figure rather than a text gap. That item's own prose
already reads `ΔH 1` and `ΔH_2`, so the restored labels agree with it.

## R17. A fraction side that is not a single token is parenthesised

Ruled 2026-10-03 (#2462).

`49_option_conventions.py` joins two printed lines with `/` and never
parenthesised the result, so a bar drawn over a *product* shipped as though it
covered only the first factor. That is not a presentation nicety — it changes
the value:

| cell | ships as | the page prints | shipped value | printed value |
|---|---|---|---|---|
| 2015 MT 60361 B | `9!/7! × 2!` | `9!/(7! × 2!)` | 144 | **36** |
| 2016 MT 39762 D | `…4!/2! . 2!` | `…4!/(2! . 2!)` | — | — |
| **2016 MT 39762 E** | `…4!/2! . 2!` | `…4!/(2! . 2!)` | 6 489 600 | **1 622 400** |

39762 E is the **keyed** option. Measured, not inferred: 39762's bar is 27.60pt
wide and spans the whole denominator, against 13.89pt for option C's genuine
`4!/2!`; 60361 B's single bar at x 55.05–90.48 covers `7! × 2!` entire, while
option D's `× 4!` sits *outside* its bar.

So: **a fraction side that is not a single token is parenthesised** —
`9!/(7! × 2!)`, `A/(A + B)`, `(62! 4!)/(10! 56!)`. A fractional exponent keeps
the form 2015 MT 27281 already ships, `^(1/3)`.

There was no prior precedent for `/(` in the corpus — the only occurrence was
the unit `kJ/(kg °C)` in 2016 CN 24399 — so this is a new convention rather
than an observed one. It is adopted because the alternative is text that reads
as a different number from the one printed.

## R18. Typographic emphasis lost in extraction is restored as `~~run~~`

Ruled 2026-10-03 (#2462).

Extraction keeps characters and discards their typeface, so an item whose
question turns on *which* words are emphasised becomes unanswerable. 2013 LC
43715 is the case: the booklet sets five verbs in `Arial-BoldMT` and the stem
asks about *"a escolha das formas verbais **em destaque**"*, pointing at a
highlight that is no longer there.

**Marker: `~~run~~`.** Plain ASCII, searchable and reversible — the properties
`48_mark_scripts.py`'s `^` and `_` were chosen for. The delimiter is forced by
what is already in the corpus: `~` and `` ` `` occur **zero** times across all
48 tables, while `*` occurs 125 times (footnote marks, and chemistry such as
`TiO2|S*`) and `**` 20 times.

**Mark every emphasised run in the cell, not only the ones the question needs.**
A mechanical rule is reproducible; "mark what the item depends on" is a
judgement that the next person will make differently.

**Scope is narrower than it looks.** Nine items have stems mentioning
*destaque*/*destacado*, but in eight of them the emphasis is ordinary
typographic convention — italicised work titles, foreign words, `TEXTO I`
labels — carrying nothing the question turns on, and those stems use the word
in its plain sense. Checking the fonts, not the wording, is what separates
them: only 43715 has emphasis the question depends on.

**Locating the runs needs no guesswork.** Extraction leaves a DOUBLE SPACE at
each font boundary (`carregamos  `, `dossiê  `), so the artifact marks where
the emphasis was.

## R15. Text recovered from INEP's own booklet is not generated text

Ruled 2026-09-21 (#2226), on the four 2018 items R14 recovered.

Filling a gap in an accessibility edition from INEP's own standard booklet is
gap-filling under R2, and owes **no inline `(gerada por IA)` and no
`description_source=partly_generated`**. Every character is INEP's, written by
INEP for the same application of the same exam. Marking it would put an AI
provenance flag on text no model wrote, which misstates the provenance in the
other direction — anyone filtering the corpus on generated text would drop
prose that is as printed as the stem around it.

The ruling covers a recovery only where **both** conditions hold:

1. **The source is the standard booklet for the same exam and year** — the
   other edition of the paper the candidates in the response tables actually
   sat, at that year's `standard_prova_codes` (R0).
2. **The stem already points at the missing content** — the item says a
   *quadro*, *tabela* or *gráfico* is there and only its contents are gone.
   The recovery restores what the item already claims and adds nothing the
   item does not call for.

Anything else is outside R15 and goes to R11 before it ships, not after:

- content reconstructed from any other source — another year, another booklet
  colour, a press reprint of the question, a model's own knowledge;
- content inserted where the stem does not call for it, which is authoring a
  stimulus rather than recovering one.

R15 is not a route around R5. It is the narrower statement that text INEP
wrote never entered R5's scope in the first place; anything that falls outside
these two conditions is generated text and carries R5's markings, if it is
ruled shippable at all.
