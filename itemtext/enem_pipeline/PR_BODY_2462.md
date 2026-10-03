# ENEM item text: adjustments from the 2013–2025 review (#2462)

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

### Ben's `instructions` lead

Ben flagged `enem_2021_1mil_mt`'s `instructions` as holding garbled watermark
text. Confirmed, and broader than stated: the field is **contaminated, not
garbage** — a 2-line, 247-character prefix with the genuine cover intact after
it — and it is **all four** 2021 tables. The column was never skipped; the
existing rule was written for 2022, where the watermark extracts as legible
repeated `ENEM 2022` tokens, while 2021's extracts character-interleaved so the
literal string never occurs.

## For Ben — one ruling needed

**2022 CH 97262** is the only edit here that **deletes** shipped text. Its
`TEXTO 2` held a scrambled dump of its infographic: percentages in one order,
labels in another, so read in document order it pairs single mothers with
30,4 % where the printed figure is 56,9 %, and black or brown single mothers
with 21,0 % instead of 64,4 %. The item asks which factors *intensify*
discrimination, so the scramble inverted the answer. The relocated prose block
carries the correct pairings and replaces the dump.

No existing rule covers removing a shipped rendering in favour of a correct
one, so `EXTRACTION_RULES.md` records it as **NOT YET RULED** with a matching
R11 escalation bullet. It is applied and flagged rather than treated as
settled. If the ruling goes the other way, keeping both renderings is a
one-line change.

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

## Gates (R10, all of them)

`validate_items` and `audit_batch` on Slurm against the **#1942-corrected**
response CSVs: OK on every table of every year touched, with `item_set_match`
and `resp_set_match` TRUE throughout and `audit_report.csv` unchanged.
`regress48` 0 on all five checks including Ben's S1 and S2.
`lint_verification` clean, `check_provenance` exit 0, the R13 audit 0
unclassified, `provenance.csv` byte-identical in every batch.

Corpus-wide, the character inventory gained exactly **two** code points across
all of this work and lost none: U+20D7, the combining arrow for 2022 CN
85445's vector labels, and U+007E, R18's `~~` emphasis delimiter. `π`, `√`,
`⇌` and `ℓ` all already occurred in the corpus.

Two traps worth recording for whoever diffs these tables next. An item
occupies ~5 rows — one per option — and `item_text` is duplicated across them,
so merging old against new on `item` produces a cross product: it reported
44,308 changed items where the truth was 25. Diff **positionally**, after
asserting that row count, column set and item order are unchanged. And the
`_` count moves in both directions, because a stacked fraction's **bar**
extracts as a literal `__`: flattening three of them at 2021 CN 117627 removes
six underscores while the water fix adds one.

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
