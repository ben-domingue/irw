Both your §1 and §2 are fixed, and chasing them turned up three more classes
of the same shape. Everything below is at `cec811bd`.

## §2 is a defect, and your one-span test is what settled it

The 2013 source encodes **every** digit on that line as a genuine 5.22pt
lowered subscript span, including all four we shipped bare:

```
'4 FeS'      9.00      '2' 5.22 SMALL lowered
' (g) + 2 H' 9.00      '2' 5.22 SMALL lowered   <- shipped as H2O
'(SO'        9.00      '4' 5.22 SMALL lowered
')'          9.00      '3' 5.22 SMALL lowered   <- shipped bare
```

## The cause is not the clause either of us suspected

Not *"changes case or follows a digit/symbol"*. Three separate mechanisms:

**§1** — `body` was `max(span size)`. On `C6H5OH + H2O →` the reaction arrow
is set at 12pt against 9.75pt text, so `body` came out 12 and the script test
`size >= body*0.85` classified the **ordinary text** as script. The body text
also sits above the subscripts' bottom edge, which was serving as the
baseline, so it scored as *raised*. That is `H_2^O`. On the `⇌` lines a 12pt
kra poisons the line the same way, which is why `C6H5O−` came out `C^6H5O−`
with the **digit** flipped too. One glyph mis-sizing a whole line, in both
directions — your instinct was right even though the mechanism wasn't the
rule.

Body size is now the **character-weighted mode** of the line, and the baseline
comes only from body-size spans.

**§2a** — `CTX = 24` cut the left context for `H2O`'s subscript to
`"S2 (s) + 15 O2 (g) + 2 H"`, whose first character lands inside `FeS`. The
start-boundary guard — the one added for `T_ANTOS` — then rejected a valid,
24-character-anchored span. It now applies only to untruncated contexts.

**§2b** — the dedupe collapsed any same-kind mark within 6 characters, eating
the second subscript of `(SO_4)_3` and `H_2SO_4`.

| check | before | after |
|---|---|---|
| §1 spurious `^` after subscript | 50 | **0** |
| §2 unmarked trailing digits | 50 | **0** |
| trap 50's three shapes | 0/0/0 | 0/0/0 |
| `H_3O^+` intact | 10 | 10 |
| markers | 1 599 | 2 484 |

`0 cells differ once every _ and ^ is removed` — marker placement moved, no
character of text did. 24/24 sampled new markers map to real small spans.

## Three more classes, same shape

Found by taking your third suggestion further: 100 items, risk-weighted by how
much our pipeline had touched them, answered from the extracted text alone.

**Stacked fractions.** 2013 MT 43849's `AC = 7/5 BD` shipped as `AC = 7 BD5`.
Every character genuine, arithmetic gone. The superscript pass cannot see
these by construction — a stacked numerator is at *full body size* — so the
new pass measures the **bar**, which is a drawing, not text. It declines and
reports rather than guessing, which is what keeps `ABO` from becoming `AB/O`
and `Teste 1:` from becoming `Teste/1`.

**Misplaced figure descriptions.** Your accessibility editions sometimes park
a description at the foot of a page, after the last item's options, describing
an item printed earlier or on the next one. 2018 CN 59858 asks how much energy
oxidising glucose releases and ended with a description of an electrical
circuit. All three had an identifiable owner that carried no description of
its own, so they were **moved**, not stripped.

**Dropped tables.** Same editions, opposite failure: the sentence pointing at
the table survives — *"O quadro apresenta a potência aproximada de
equipamentos elétricos"* — and the numbers don't. Four items, all 2018,
recovered from your standard booklet. Worth saying that scoping this was most
of the work: 47 of 51 candidates are false positives, because "quadro" is an
ordinary Portuguese word, a Dias Gomes theatre scene and a comic-strip panel
before it is a table.

And one I'd have missed without the check: 2013 CN 23920 shipped a stem
reading `6 × 10^23` beside options reading `1,5 × 1025`, because the context
begins with the printed option letter that the parser had already stripped.

## On the check itself

Re-answering the 73 items this work changed: **67 of the 70 answerable
correct**. None of the three misses is a text defect — two are figure-
dependent, one was my own reasoning. I'd still read this as "the text carries
its meaning", not as a score: same model family, not independent.

Worth flagging that answerability is not really the bar here. IRW item text is
read for linguistic complexity, so a figure nobody described costs little,
while a lost table or a spliced-in paragraph changes what is being measured.
That is why the dropped tables got fixed and the undescribed figures did not.

## Things I got wrong on the way, for the record

Trap 50 is about this pass shipping bugs silently, and it happened again:

- my new dedupe didn't advance its cursor on a collapse, so a three-span run
  kept its third span — caught by reading my own diff, not by a test;
- exact abutment missed **overlapping** marks: `Ce4+` arrives as a 2-char span
  `4+` plus a 1-char `+`, and shipped `Ce^4^+`. The suite caught that one. The
  rule that survives is an end cursor, with five shapes unit-tested;
- round-tripping through Python's csv writer rewrote all 48 tables — 24 000
  diff lines — because these are written by R (character columns quoted,
  numeric and NA bare, header always quoted);
- `31_assemble_batch.py`'s copy source still pointed at `out_v8` and bare year
  roots, so running it would have reverted all of the above for the third
  time. To your earlier question about what stops it happening again: `out_rb`
  is now the canonical source, because that is what `41_staleness.py` compares
  against. The refusal gate alone would not have caught it — a reverted
  fraction or subscript leaves text that reads perfectly well;
- a length ratio called 47 of 128 items "short" before I cut the option block
  from the printed side; the real figure was 6, and those are mostly graph
  axis numbers and source credits.

Rules R12–R14 in `EXTRACTION_RULES.md`, traps 52–67 in `STATUS.md`.

## State

44 tables. `audit_batch` 11 PASS / 33 WARN / **0 ERROR**, unchanged.
`lint_verification` 44 rows clean, `check_provenance` exit 0, 0 control
characters, 0 U+FFFD, 0 page furniture. `41_staleness.py`: committed tables
match a fresh pipeline build exactly.
