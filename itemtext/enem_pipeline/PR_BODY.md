Item text for **every remaining ENEM year**. 2023 shipped in #1848 / #2180; this is the other eleven, as `batch_enem_<YYYY>` per `EXTRACTION_RULES.md` R9.

**2,026 of 2,035 published items across 2013-2022 and 2024-2025.** The nine absent are every item INEP annulled.

| | |
|---|---|
| years | 2013, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024, 2025 |
| tables | 44 (11 years x 4 areas) |
| items | 2,026 of 2,035 published |
| gates | `normalize_nulls` / `lint_verification` / `check_provenance` / `audit_batch` all pass |
| `audit_batch` | 44 tables: 11 PASS, 33 WARN, **zero hard-gate failures** |
| translations | none ship (#2179) |
| uploaded | nothing — upload stays a separate manual step |

## Where the text comes from

Where INEP published an accessibility (LARANJA / Ledor) edition, the text is read from it, because INEP wrote verbal descriptions of figures, graphs and tables into that edition. **2013, 2015 and 2016 have no accessibility edition at all**, so those come from the standard AZUL booklet through a new `13_join.py --colour` path that requires exactly one `CO_PROVA` at that colour and reports rather than picks when the colour is ambiguous.

`item` is always `CO_ITEM` from `ITENS_PROVA` at the year's standard prova codes — never positional.

## The position convention is measured, not guessed

Each area's offset is derived as `printed_lo - CO_POSICAO_lo` and recorded in `join_report.json`; the gap filler reads that same number rather than re-deriving it. It comes out 0 for a continuous year, ±45 for 2017's per-area numbering, and for 2016 **CH −45 / CN −45 / LC +90 / MT 0** falls out with no special case — 2016 numbers `CO_POSICAO` in INEP's canonical LC/CH/CN/MT order while printing CH/CN on day 1 and LC/MT on day 2. Proven byte-identical on the years that already passed.

## Verification

Every year is checked against INEP's own printed-position key strings (`TX_GABARITO_{CN,CH,LC,MT}`), letter by letter, in every area of every available booklet. A wrong convention lands near chance (~9/45), so exact agreement over ~45 effectively random 5-way letters is decisive.

All exact **except 2017 LC on LARANJA at 43/45** — and that one is a defect in INEP's own accessibility key string, not here:

- `ITENS_PROVA` gives items 39670 and 29586 **D** and **B** in all five colours, LARANJA included;
- the AZUL and AMARELA key strings both give D and B, 45/45 each;
- the extracted option text is **character-identical** between LARANJA and AZUL for both items, so no reordering could justify E and C.

Three independent sources against one. `correct_response` is unchanged.

## Reproduction was measured

The same items were extracted independently from two different colour booklets with separately embedded font subsets and compared by `CO_ITEM`: **99.97% character agreement, zero substituted letters.**

That check is what found printed page furniture — barcodes, running heads, InDesign source filenames, the anti-fraud watermark, the essay draft page — sitting inside `item_text` / `option_text` in **112 items**. All of it is gone, removed by a reversible post-pass rather than by editing the pinned parser.

## Fonts: four pathologies, all repaired inside the PDF

Repaired by completing `/ToUnicode` in the file, so the pinned parser reads these years like any other and item boundaries cannot drift:

- **2015 / 2016 / 2018** embed Arial as a CID-keyed CFF with no glyph names. 2015 and 2016 needed **no new code** — the 2018 decoder applies unchanged.
- **2021** names glyphs by id in `/Differences`. The CMap is completed, never `/Differences` (patching that corrupts every lowercase `l` and `x`).
- **2021 / 2022** set notation in opaque SymbolMT subsets, resolved over the Adobe Symbol encoding.

For 2021, **545 of 770** surviving markers decoded that way, and the result self-checks: CN 88403 now reads `E° = -3,05 V ... I2 + 2 e- -> 2 I-`, where the booklet's own prose two lines earlier says *"potencial de redução igual a menos 3,05 volts"*.

- **MyriadPro** in 2015 had ten CIDs above its ASCII run that the decoder left as `U+FFFD` "rather than guessed". That default was worse than it looked: those are not decorations, they are **letters inside words**, and one item shipped reading `"Use \ufffdgua tratada ... recomenda\ufffd\ufffdes quanto \ufffd restri\ufffd\ufffdo"`. All ten are now resolved from word-level evidence (á, à, ã, ç, é, ó, õ, ú, the fi ligature, and one genuine bullet) and that line reads **"Use água tratada e siga sempre as recomendações quanto à restrição"**.

**There is now no `U+FFFD` anywhere in the corpus**, and no control character either.

## Five defect classes no gate can see

A green gate is not a correct item. Every fix in this group leaves
`item_set_match`, `resp_set_match`, the control-character count and the
missingness rate exactly where they were. Three were found by a **100-item
model-understanding check** (`52_risk_sample.py` + `50_model_check.py`), which
asks a model to answer items from the extracted text alone; two came from
Ben's sampling of the script markup.

**Stacked fractions (R12).** A printed fraction is a numerator, a drawn rule
and a denominator; extraction reads them in layout order and emits two tokens,
so 2013 MT 43849's `AC = 7/5 BD` shipped as `AC = 7 BD5`. Every character
genuine, nothing missing, arithmetic gone. The superscript pass cannot see
these by construction — a stacked numerator is printed at *full body size* —
so `53_stacked_fractions.py` measures the **bar**, which is a drawing. Bars are
deduped and screened for table rules both horizontally and vertically; both
sides must be number- or symbol-shaped; the rewrite happens only when the count
in the row equals the bar count. It declines and reports rather than guessing,
which is what keeps `ABO` from becoming `AB/O` and `Teste 1:` from becoming
`Teste/1`. 8 automatic rewrites, 9 hand-verified patches, 8 items.

**Misplaced figure descriptions (R13).** The accessibility editions sometimes
collect a description at the FOOT of a page, after the last item's options,
describing an item printed earlier or on the next page. 2018 CN 59858 asks how
much energy oxidising glucose releases and ended with a description of an
electrical circuit. All three found had an identifiable owner, already shipped
and carrying no description of its own, so the fix is a **move**, not a strip.

**Dropped tables (R14).** Those same editions sometimes keep the sentence
pointing at a table — *"O quadro apresenta a potência aproximada de
equipamentos elétricos"* — and lose the numbers. This matters because IRW item
text is read for **linguistic complexity**: a word count over an item whose
table vanished is a word count of the wrong item. Four items, all 2018,
recovered from INEP's own standard booklet, so no `gerada por IA` marking is
owed. Scoping was most of the work — 47 of 51 candidates are false positives,
because "quadro" is an ordinary Portuguese word, a Dias Gomes theatre scene
and a comic-strip panel before it is a table.

**Script markup**, from Ben's review. Three mechanisms, none the rule either of
us suspected: `body` was `max(span size)`, so a 12pt reaction arrow on a
9.75pt line made the *ordinary text* fail the script test and ship as `H_2^O`
and `C^6H5O−`; the baseline was the lowest edge on the line, normally the
subscripts' own; and `CTX = 24` truncation put a mid-word context in front of
a valid span for the start-boundary guard to reject. Ben's two greps go
**50 → 0** and **50 → 0**, with 644 markers restored. His §2 lead was checked
at source first: the 2013 PDF encodes every digit on that line as a real
5.22pt lowered subscript, so it was a defect, not a faithful rendering.

**Option-side exponents.** 2013 CN 23920 shipped a stem reading `6 × 10^23`
beside options reading `1,5 × 1025`. The context begins with the printed option
letter, which the parser has already stripped from `option_text`. Zero unmarked
`× 10NN` remain corpus-wide.

Also: 2025's booklets leak their InDesign filename with the newer `.indd`
extension (doubled, like that year's option letters); the furniture pass
matched only `.indb`.

## Verification of those classes

- `41_staleness.py` → **committed tables match a fresh pipeline build
  exactly**, after rebuilding all nine recipe years end to end. These are
  pipeline steps, not hand edits.
- the refusal gate in `31_assemble_batch.py` covers R13 and `.indd`: it
  **fails** on the pre-fix 2018 and 2020 tables and passes on the fixed ones.
- **0 cells differ once every `_` and `^` is removed** — marker placement
  moved, no character of text did.
- 24/24 sampled new markers map to genuine small spans in the source.
- the 73 items this work changed were re-answered from text alone:
  **67 of the 70 answerable correct**, and none of the three misses is a text
  defect — two are figure-dependent, one was the reader's error.

## Coverage and the deliberate omissions

**Nine items are excluded under R3** — every one annulled by INEP (`TX_GABARITO='X'`), so there is no correct answer to ship. `audit_batch.R` confirms this is right rather than a gap: those years report `n_items_live == n_items_candidate` with `item_set_match=TRUE`, i.e. the live tables exclude them too.

| year | area | item | INEP's reason |
|---|---|---|---|
| 2018 | MT | 30294 | Anulado |
| 2020 | CN | 32352, 44322 | Anulado |
| 2021 | MT | 117674 | Anulado |
| 2022 | MT | 39443 | anulado pedagogicamente |
| 2024 | CN | 61076 | Pedagógico |
| 2025 | CN | 141557, 141774 | Previamente exposto |
| 2025 | MT | 31350 | Previamente exposto |

**37 items ship `option_text = NA`** — the printed options carry no text that could be transcribed. Per the rule in #1848 nothing is generated to fill them: a generated option label would become a category label someone joins to `resp` for distractor analysis. `correct_response` and `resp_raw` keep the options addressable, and **no `option_text` cell is generated anywhere in this batch.**

I checked eight of the 37 against the printed page and the notes say which:

- **5 confirmed drawings** — 2013 CN 15947 and 2021 CN 62293 (circuit diagrams), 2016 CN 97711 (graph sketches), 2018 CN 111411 (chemical structures), 2013 CN 7867 (five graphs). Four of these previously had **no text at all** and were recovered here by locating the option labels geometrically.
- **3 confirmed *not* drawings** — 2015 MT 14712, 2016 MT 60291 and 2016 CN 86572 have **stacked-fraction** options (86572's are `1`, `4/7`, `10/27`, `14/81`, `4/81`). Those are a gap rather than a deliberate omission: they are legible in the source PDF and recoverable by hand. The notes file them separately from the drawings.
- The remaining **29** were classified from the wording of the stem, and the notes say plainly that this was not re-checked page by page. That heuristic is known to misfire — it read 86572 as a figure item because the stem mentions a circuit — so no claim is made about which kind each one is. What is certain for all 29 is that the extractor found no option text and none was invented.

On figure items the stem legitimately carries the figure's **own** labels (axis names, component letters), because those are printed text and no extractor can separate them from prose. 2013 CN 15947 ends `"...está representado em: A Fase Fase"`, where `Fase` labels a wire in the first diagram. The notes say so, so it is not mistaken for a transcription error.

## An anomaly scan, and the bug it found

Twelve shape-based detectors over all 2,026 items (`37_anomalies.py`) — they look for what a bad parse *looks like*, without knowing what the text should say.

**Six found nothing at all**, and those zeros are the structural guarantee: no option letters outside A–E, never more or fewer than one correct row per item, no item with some options `NA` and others not, no case where the key's option is blank while the others have text, no option carrying the next question's marker, no stem repeating itself.

One found a real bug. `one_option_much_longer` flagged option lengths like `[1,1,1,1,346]`: three items had INEP's figure-description block stuck on the end of **option E** instead of moved to the stem. That fix had been declared done in an earlier parser version, and its marker regex had four faults — it could not match the plural headers (`d[oaes]\b` fails on the following "s" in `"Descrição das figuras:"`), it forbade the newline in a header wrapped across a line, its 40-character window was too short, and being case-insensitive and unanchored it also matched ordinary prose (`"descrição do espaço, como em: ..."`). Parser v10 anchors to a line start and requires the capital; it matches **all 416** blocks the old regex found, misses none, and finds 26 more. 2018 CN 39342, 2018 MT 82123 and 2020 MT 59546 now have clean options.

The tell was never the marker — it was the option-length shape.

One detector fires on **1285 of 2026 items** and is simply wrong: "stem does not end in punctuation" is ENEM's house style, where the option completes the sentence (`"...o circuito equivalente a esse sistema é"`). Noted so nobody mistakes it for truncation.

## Known, disclosed, not blocking

- 2015 MT 14712 and 2016 MT 60291 ship `NA` option text because their options are **stacked fractions**, not drawings — disclosed as a gap, not as a figure item.
- 2021 CN 117867 keeps two raw `[UNDECODED-g34]` markers in `option_text`, where generated text is not permitted.
- 2020 day 1 `instructions` is thin because that cover page extracts to 195 characters at source.

## What the 33 WARNs are

Two classes, both already accepted for 2023: blank `option_text` on the bare-figure items above, and LC row-count anomalies. No WARN is a hard-gate failure — `item_set_match`, `resp_set_match`, `uses_raw_resp` and `canonical_nulls` are TRUE on all 44 tables and `pct_item_text_missing` is 0 on all 44.

## Not in this PR

Nothing uploads to Redivis; that stays manual and separate.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
