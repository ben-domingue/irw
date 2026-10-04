# ENEM adjustments: the 2013–2025 item-text review (#2462) and the 2024/2025 `id` fix (#2812)

> **DRAFT — the PR is not open yet.** Mateus is settling every change he intends
> to make first, then opening one PR. Keep this file current as classes land;
> the commit messages carry the full reasoning and this is the summary over
> them.

Santiago read all twelve years of ENEM item text and sent
`enem_text_check_2013_2025.csv`: **557 findings over 371 items, 121 of them
meaning-changing**. Structurally the tables were already sound — live matched
the repo cell by cell and the item sets matched the response tables exactly —
so everything here is content, not schema.

## What is fixed

| class | findings | commit |
|---|---|---|
| `misplaced` + `owner_missing_description` | 46 | `e2c67379` |
| script-marking half of `flattened`, plus the `instructions` watermark | ~20 | `d6b822ed` |
| `symbol` | 19 | `a801f199` + `a7329f01` (drawn glyphs, R16) |
| `tabs` | 159 | `b64af73e` |
| `number` | 23 | `e7b8bfcc` |
| rest of `flattened` (fractions, factorials) + R17 + R18 | ~58 | `d81a205e` |
| `essay_material` + `moved_word` + `figure_labels` (R19, R5) | 15 | `5b0fe400` |
| `stimulus_missing` — 45 figure descriptions (R5) | 46 | `bd435100` |

**Every `changes meaning` finding in the review is fixed — 176 of 176.** What
is left of the 557 is 114 `cosmetic`, 54 `noise` and 6 `structure`: page
numbers, ligatures, spacing inside words, option-letter residue. None of them
alters what an item means, and they are listed as known-open rather than
quietly dropped.

The `stimulus_missing` batch is the only change here that **adds generated
text**, and the only one that changes provenance: 2013 CH/LC, 2015 CH/LC and
2016 CH/LC move from `source_published` to `partly_generated`.
`itemtext/fixes/itemtext_issues_enem_2462.md` drafts issues-page entries for
**all eleven** ENEM tables that carry that status — the 2021 trio has owed one
since the 2026-09-11 ruling in #2226 and 2023 CN/MT since #1848, and neither
was ever written, so the backlog is discharged rather than grown.

### Figure descriptions on the wrong item (R13)

30 description blocks relocated across 2018/2020/2022. The `misplaced` and
`owner_missing_description` findings are the same defect from both ends: every
owner named is shipped, in the same area, and printed **earlier** than its
donor — position gap −1 to −3, never positive, 28 for 28.

Scaling R13 from 3 cases to 30 broke every assumption the original three
shared, so each operation now states what cannot be inferred: **which** block
(10 donors carry two, and in 7 the misplaced one is not the last), **where it
ends** (2022 CH 44230 prints its own question after the block), **where it
lands** (before the question, not appended — appending reproduced in the
recipient the exact shape R13 calls malformed), and **whether it lands at all**
(three recipients already had the content from the standard booklet via R14).

### Super/subscripts that were detected and then dropped

`48_mark_scripts.py`'s anchor used `str.split()`, which discards trailing
whitespace and so demanded the script be *adjacent* to its context. Every
exponent the booklet prints after a space was silently dropped. Beyond the
review's own list this recovered ionic charges (`H^+`, `e^−`), isotope mass
numbers (`^235U`) and the `d^2` of Newton's law.

### Symbols lost, mis-mapped or reordered

Three different defects, measured apart: **absent** from the text layer because
the glyph is vector artwork (6), **present but mis-mapped** (8), and **present
and correct but relocated** by content-stream order (5).

Two new passes came out of it — `56_reading_order.py`, which re-interleaves
text the content stream emitted out of visual order under a character-multiset
guard so it provably reorders and can never add or drop a character; and
`57_drawn_glyphs.py`, which recovers glyphs the booklet draws.

### New rule: R16, glyphs read from the drawing

Ruled by Mateus 2026-10-02 — *"let's apply the same rule as for fractions — we
are not really generating, we are only looking and recovering in a feasible
manner."* R12 already settles this for the fraction bar; R16 states it for a
glyph, so a radical read off its hook-and-vinculum and an equilibrium arrow
read off its two harpoons owe no AI-provenance marking.

**One thing worth flagging:** the review described these as *"reaction arrow
lost"*. The printed glyph is `⇌`, **not** `→` — each is two antiparallel
harpoons, and all three stems corroborate it (`pK_a`, the three equilibrium
constants, *"em equilíbrio no sangue"*). Writing `→` would have shipped a
one-way reaction where INEP printed an equilibrium, inverting the chemistry of
three items.

### A keyed answer was wrong in the shipped text

**2016 MT 39762 option E** shipped as `...4!/2! . 2!`, which reads as
6 489 600. The printed bar spans the whole denominator, giving 1 622 400 —
and E is the key. 2016 MT 39762 D and 2015 MT 60361 B had the same defect.
The cause is mechanical: `49_option_conventions.py` joins two printed lines
with `/` and never parenthesises a side that is a product. Hence **R17** — a
fraction side that is not a single token is parenthesised, `9!/(7! × 2!)`.

**R18** restores typographic emphasis as `~~run~~`. 2013 LC 43715 asks about
*"a escolha das formas verbais em destaque"*; without the marking the item
points at an invisible highlight. The delimiter is `~~` because `~` and
`` ` `` are the only characters absent from all 48 tables, while `*` already
occurs 125 times. The runs come from font evidence (Arial-BoldMT on the five
verbs and the title, Arial-ItalicMT on *dossiê*), not from reading the prose.

Both rules are applied by a new pass, `58_verified_patches.py`, which runs
**last** — every `old` string in it is copied from the *shipped* cell, so
anchoring it to an earlier pass would be anchoring to text that does not exist
yet. Matching is scoped to (year, area, item, column, option letter) and
requires exactly one occurrence, so a stale anchor reports instead of silently
missing.

### A third wrong-kind script, found while verifying

Not in the review: **2021 CN 117627** shipped water as `H^2O`. Span geometry
settles it — on that line the base sits at y0 182.61 and the `2` at 189.00,
*below* the baseline, while the charge marks `+` and `−` on the same line sit
at 183.10, *above* it. The AFC cathode is ½O₂ + H₂O + 2e⁻ → 2OH⁻. A
corpus-wide scan for a script marked between two letters of one token returns
that cell and no other, so it was patched rather than made a rule.

### The Redação section that four items swallowed (R19)

In the day-1 booklet the essay section is printed straight after the final
Linguagens question, with no question number and no `QUESTÃO` header to stop
at. The parser closes an item when it meets the *next* question header — so for
the **last** question of the area there is nothing to close against, and the
whole essay apparatus landed inside that one item. Those four items were
shipping with **65–79 % of their text belonging to a different task**, and any
model reading the cell read two unrelated prompts as one.

Four items, and a scan of every `item_text` in every year confirms there are no
others: 2017 LC 60715, 2019 LC 76167, 2021 LC 120165, 2022 LC 86703. The
`instructions` column is deliberately left alone — the booklet *cover*
legitimately says the day-1 caderno contains the essay proposal.

`59_strip_essay_section.py` anchors on what to **keep**, not what to cut,
because the essay material has no reliable opening marker and 2017's own
stimulus already carries `TEXTO I`/`TEXTO II` labels, so cutting on `TEXTO`
would split the item in half. Every keep-anchor was confirmed by checking that
the item's **keyed option completes the question grammatically**.

Since the pass deletes text it fails closed twice — the removed span must carry
an essay signal *and* match a per-item character count measured when the entry
was written. The second check is the one that matters, and testing is what
established that: an anchor aimed deliberately **earlier** still leaves the
essay material inside the removed span, so the signal test alone passes it and
real item text is deleted. With the length check that case is refused even
under `--apply`.

### Options that were never text (R5)

**2016 MT 39198** shipped its five options as `B\nC`, `A B`, `C A BC`, `A BC`,
`A B\nC` — permutations of three bare letters, with the keyed option
indistinguishable from the rest. **2020 CN 62745** shipped the same four
circuit labels reordered five times. In both the options *are* diagrams, and
what the extractor found was label residue scraped from inside the artwork in
content-stream order.

Both are now NA, with **no generated descriptions**. This is R5 enforcement
rather than a new rule: R5 already says that when the printed options are bare
figures the `option_text` is NA, and that an `option_text` is never generated.
Fifty items across the twelve years already ship that way, so this follows the
corpus convention instead of adding an exception — and it needs no AI text and
no provenance change.

### A word that moved between two items

2015 MT 29167 and 29359 are one defect seen from both ends. The participle
*substituídas* was cut from 29167's stem, leaving `duas antenas que serão  por
uma nova` with a double space — and the missing token is physically present in
a **different item**, 29359's option E, which is that item's **keyed** option.
The word is not reconstructed from guesswork: the gap's grammar requires a
participle, the item's own next sentence says *"as antenas que serão
substituídas"*, and the stray copy is sitting in the other item. Both ends are
fixed together.

2016 MT 24747 is the same shape in algebra. Option A is a stacked fraction
whose numerator and option letter were swept into the stem, so the item ended
`...fonte sonora, é / A / 500 . 81` while option A held only `. D^2`. Read off
the page, the printed option is 500·81 over A·D². **R17 is load-bearing here**:
written flat as `500 . 81/A . D^2` it reads 500·(81/A)·D², which moves D² into
the numerator and inverts the physics, since cost is inversely proportional to
the square of the distance.

### Ben's `instructions` lead

Ben flagged `enem_2021_1mil_mt`'s `instructions` as holding garbled watermark
text. Confirmed, and broader than stated: the field is **contaminated, not
garbage** — a 2-line, 247-character prefix with the genuine cover intact after
it — and it is **all four** 2021 tables. The column was never skipped; the
existing rule was written for 2022, where the watermark extracts as legible
repeated `ENEM 2022` tokens, while 2021's extracts character-interleaved so the
literal string never occurs.

## Also in this PR: #2812, the 2024/2025 `id`

Ben raised this separately while sourcing codebooks for #2787. From 2024 INEP
ships `PARTICIPANTES_<year>.csv` and `RESULTADOS_<year>.csv` instead of one
`MICRODADOS` file, and the year scripts joined them with `bind_cols()` on a
row-count check. There is no key — PARTICIPANTES is keyed `NU_INSCRICAO`,
RESULTADOS `NU_SEQUENCIAL`.

**He is right, and it turns out to be measurable rather than only inferable.**
One detail in the issue is off, and it is the detail that makes the test
possible: the two files *do* share columns — the test-location ones
(`CO_MUNICIPIO_PROVA`, `NO_MUNICIPIO_PROVA`, `CO_UF_PROVA`, `SG_UF_PROVA`) plus
`NU_ANO`. If row *i* of each file were the same candidate, their test
municipality would have to agree.

| | agreement | expected at random |
|---|---|---|
| 2024, all 4 332 944 rows | **0.51 %** | 0.54 % |
| 2025, first 200 000 rows | **0.56 %** | — |

Indistinguishable from chance, so each candidate's answers were carrying a
stranger's registration number. The mechanism is visible in the keys:
PARTICIPANTES is ordered by `NU_INSCRICAO` (`…233, …234, …235`) while
`NU_SEQUENCIAL` is a scrambled permutation of 1…N. The 2024 Leia-Me's LGPD
rationale fits — the split is deliberate and the files are not meant to be
linked.

Fixed with the issue's option 1: `id` comes from RESULTADOS' own
`NU_SEQUENCIAL` and PARTICIPANTES is no longer read. Nothing in the build ever
used a column from it (`TX_GABARITO` comes from `ITENS_PROVA`). Applied to all
thirteen year scripts, whose loader block is byte-identical, so a future
split-file year cannot reintroduce it; 2013–2023 keep taking the MICRODADOS
branch unchanged.

**It is a relabel, not a different sample.** `sample()` under `set.seed(5150)`
draws the same *positions* and the row order still comes from RESULTADOS, so
the same candidates are kept. Confirmed by rebuilding both years and comparing
against the pre-fix tables row for row.

Two things this PR does **not** finish:

- the sixteen live `enem_2024/2025_1mil_*` tables need regenerating and
  re-uploading before `id` means what it says;
- `metadata/column_docs.csv` still records `id <- NU_INSCRICAO` for those eight
  tables. That row was **already wrong before this fix**:
  `14_column_docs.py` reports the first rename it finds in a script, and for
  2024/2025 that is the MICRODADOS branch, which never runs for those years.
  Making the scan report every candidate was tried and reverted — because the
  loader block is shared it marks all thirteen ENEM years ambiguous, including
  the eleven where `NU_INSCRICAO` is correct, and churns ~800 rows in unrelated
  tables. A branch-aware fix belongs in #2763.

**One more thing worth flagging:** `NU_SEQUENCIAL` is a within-year surrogate.
2024 and 2025 both begin `206403, 3604651, 1461268`, so INEP appears to reuse
the shuffle — the same number is a different person in each year, and it must
not be used to follow anyone across years.

## Judgement calls, decided rather than escalated

Three things were carried as open questions while the work was in flight. All
three are now settled, so nothing here is waiting on a reviewer.

**R20 — a rendering that inverts its own item is replaced, not kept alongside.**
2022 CH 97262 is the only edit in this PR that **deletes** shipped text. Its
`TEXTO 2` held a scrambled dump of its infographic — percentages in one order,
labels in another — so read in document order it pairs single mothers with
30,4 % where the printed figure is 56,9 %, and black or brown single mothers
with 21,0 % instead of 64,4 %. The item asks which factors *intensify*
discrimination, so the scramble inverts the answer.

The reasoning that settles it: these are not two views of one content, one of
them is false. Keeping both would not hedge the risk — it would ship a correct
rendering and an item-inverting one in the same cell and leave the reader to
guess which governs. The rule is scoped narrowly so it cannot become a licence
to tidy: only where a rendering is demonstrably **wrong about its own figure**,
shown by comparison against that figure; the replacement must be INEP's own
words, never generated; and the disagreeing numbers are recorded per operation
so the claim is checkable. R11's escalation bullet is narrowed to match —
anything short of demonstrably-wrong still escalates.

**Two images now get two insertion points.** 2013 CH 25217 and 2013 LC 51365
each carry two figures, and both descriptions were going in at one anchor,
which put the second description before the *first* image's credit line. Each
is now split, so a description sits with the figure it describes. The text is
unchanged and still twice-verified; only its position moved.

**R21 — transcribe the marks that are there; never add one that is not.**
2013 CH 44785 reproduces a 1934 caption whose acute and grave are printed as
displaced apostrophes (`Havera' … a' poderosa influencia`). The transcription
renders those as `Haverá` and `à` but leaves `influencia` unaccented, which
review flagged as inconsistent. It isn't: the first two marks *are* on the
page and merely mis-positioned, so transcribing them where the language puts
them is recovery, on the same basis as R12 and R16. `influencia` has no mark to
transcribe — that is pre-1943 orthography, and adding a circumflex would emend
INEP's source and silently modernise a period artefact the exam reproduces on
purpose. One rule applied twice: transcription normalises *where* a diacritic
sits, never *whether* it exists.

## Three corrections to the review itself

Offered so the harness can be fixed, not as criticism — the review caught real
defects that no gate in this repo could see.

1. **`owner_missing_description` looks under-inclusive.** Of the 10 owners it
   names but does not separately flag as missing a description, **8 carry no
   description at all** by the same test that flagged the other 18. All 8 are
   in 2018 CN and MT while all 18 flagged ones are CH and LC, which suggests
   that check did not cover CN/MT. The fix is unaffected — the move supplies
   the description either way — but 18 understates it.
2. **The `watermark` scan missed half its cases.** It reports 2021 CN and MT.
   All four 2021 tables are affected; CH and LC carry a differently-spaced
   variant (`1 NE2 0 2 ME`) that evidently fell outside the pattern. 2 should
   be 4.
3. **`43554 → 86222` does not reproduce.** Donor 43554 carries no stray
   description and owner 86222 already has the equipment table inline —
   `55_recover_tables.py` fixed it under R14 before the review ran. The quoted
   text matches neither current table, so that finding read a pre-recovery
   snapshot.

## The 2024/2025 response tables

`id` is fixed in the build scripts here, but the sixteen published tables still
carry the old value until they are replaced. Regenerated tables, `.Rdata` only
(each file loads a single `df`), matching the format used for the 2013–2025
reprocess:

**[enem_2024_2025_1mil_idfix_rdata.zip — 789 MB](PASTE_DRIVE_LINK_HERE)**

Eight `regular` (`id | item | resp | resp_raw | position | booklet`) and eight
`nominal` (`… | text | …`), plus a README restating the evidence. Everything
except `id` is unchanged, verified byte-identical against the pre-fix tables.

## Gates (R10, all of them)

Every commit was gated before it landed, against the **#1942-corrected**
response CSVs on Slurm. Across the four batches in this PR:

| batch | validate_items | audit_batch | errors |
|---|---|---|---|
| 58 verified patches (`d81a205e`) | 24/24 | 6/6 | 0 |
| 15 meaning-changing (`5b0fe400`) | 28/28 | 7/7 | 0 |
| 45 stimulus descriptions (`bd435100`) | 16/16 | 4/4 | 0 |
| three rulings (`a1a383a3`) | 4/4 | 1/1 | 0 |

`item_set_match` and `resp_set_match` TRUE throughout. `regress48` 0 on all
five checks including Ben's S1 and S2, `lint_verification` 44 rows with no
problems, `41_staleness` clean and reporting that the committed tables match a
fresh pipeline build exactly, the R13 audit 0 unclassified.

Corpus-wide the character inventory gained exactly **two** code points across
all of #2462 and lost none: U+20D7, the combining arrow for 2022 CN 85445's
vector labels, and U+007E, R18's `~~` emphasis delimiter. `π`, `√`, `⇌` and `ℓ`
all already occurred.

Two traps worth recording for whoever diffs these tables next. An item occupies
~5 rows — one per option — and `item_text` is duplicated across them, so
merging old against new on `item` produces a cross product: it reported 44,308
changed items where the truth was 25. Diff **positionally**, after asserting
that row count, column set and item order are unchanged. And the `_` count
moves in both directions, because a stacked fraction's **bar** extracts as a
literal `__`: flattening three at 2021 CN 117627 removes six underscores while
the water fix adds one.

## Also fixed along the way

Three latent bugs that this work surfaced rather than caused:

- `31_assemble_batch.py` hardcoded `uploaded: ""`, so re-assembling a shipped
  year silently cleared the `uploaded=2026-09-24` stamp #2405 applied — it
  would have reported published tables as never uploaded.
- `KEEP_LATE_DESC` was a hand-copied duplicate of `54`'s `KEEP` and had drifted
  in both directions, so the `UNFIXED` gate refused a correctly-built 2018. It
  is now imported from the one place it lives.
- Every pin lookup globbed the pipeline directory while the pins are committed
  under `pins/`, so from a clean checkout `cut_pin.sh --check` reported
  `no pin exists` and the batch build record came out **empty**. All four call
  sites read `pins/` now; proven inert by a full rebuild of all nine recipe
  years coming out byte-identical, 36 of 36 tables.
