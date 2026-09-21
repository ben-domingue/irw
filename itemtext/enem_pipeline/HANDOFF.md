# ENEM item text — handoff

**Superseded as the entry point: read `RESUME.md` first.** It carries the
current state, the verification results, what is waiting on whom, and the
traps most likely to bite. This file is the longer narrative of how the
thirteen years were built, kept for the detail RESUME.md compresses.

Then `STATUS.md` (per-year state + traps 1-67) and `EXTRACTION_RULES.md`
(R0-R14, the contract every year must satisfy).

Last updated 2026-09-16. Everything below was observed, not predicted.

## Where the corpus stands

**All 13 years now pass the gate.** Every year below was verified against
INEP's own printed-position key strings with `20_verify_gabarito_microdata.py`
(the strong check: it reaches the accessibility booklet and needs no download).

| year | gate | position verified against INEP key strings | ready to ship? |
|---|---|---|---|
| 2023 | shipped (#1848) | 174/174 printed | live on Redivis |
| 2013 | 4/4 PASS | 320/320, 4/4 areas (AZUL) | yes, **185/185** |
| 2015 | 4/4 PASS | 320/320, 4/4 areas (AZUL) | yes, 184/185 (LC 67408 open) |
| 2016 | 4/4 PASS | 320/320 AZUL **and** 320/320 AMARELA, 4/4 each | yes, **185/185** |
| 2017 | 4/4 PASS | 315/315 AZUL + AMARELA, 4/4 each (LARANJA LC 43/45 = INEP's own key-string defect, trap 31) | yes |
| 2018 | 4/4 PASS | 318/318 on LARANJA, AZUL **and** AMARELA, 4/4 each | yes, 184/185 (max) |
| 2019 | 4/4 PASS | 320/320 on all three booklets, 4/4 each | yes |
| 2020 | 4/4 PASS | 316/316 AZUL + AMARELA, 4/4 (LARANJA: 2 of 4) | yes |
| 2021 | 4/4 PASS | 318/318 AZUL + AMARELA, 4/4 (LARANJA: MT only) | yes, 184/185 (max) |
| 2022 | 4/4 PASS | 318/318 AZUL + AMARELA, 4/4 (LARANJA: 3 of 4) | yes |
| 2024 | 4/4 PASS | 318/318 AZUL + AMARELA, 4/4 (LARANJA: 2 of 4) | yes |
| 2025 | 4/4 PASS | 314/314 on all three booklets, 4/4 each | yes |

NOTHING is committed to git and nothing is uploaded. That is deliberate.

**The output directory is NOT the same shape for every year.** Read the
authoritative path from this table before assembling anything -- 2025 has TWO
candidate directories and picking the wrong one silently drops the ruled
`section_prompt` handling:

| year | authoritative directory (under `/scratch/users/mazzafe/itemtext_years/`) | items |
|---|---|---|
| 2013 | `2013/` | 184 |
| 2015 | `2015/` | 184 |
| 2016 | `2016/` | 184 |
| 2017 | `2017/` | 185 |
| 2018 | `2018/out_v8/` | 183 |
| 2019 | `2019/` | 185 |
| 2020 | `2020/` | 183 |
| 2021 | `2021/out_v8/` | 183 |
| 2022 | `2022/` | 184 |
| 2024 | `2024/items/` | 184 |
| 2025 | `2025/items_sp/`  <- `items_sp`, NOT `items` | 182 |

2,021 items over these eleven years, plus 2023's 174 already shipped.
Every table: 0 control characters and 0 U+FFFD.

### Items that do not extract: NONE, across 13 years

As of 2026-09-16 every published item that has a scorable key has text.

The four bare-figure-option items were recovered under Ben's rule (#1848):
their five options are DRAWINGS, so `option_text` is the literal `NA` and the
real extracted stem stays in `item_text`. No text was generated for them.
  2013 CN 15947 (circuit diagrams) | 2016 CN 97711 (graph sketches)
  2018 CN 111411 (chemical structures) | 2021 CN 62293 (circuit diagrams)

The last genuine failure, **2015 LC 67408**, turned out to be a parser bug and
not a property of the item: the stem contains "EE UU" (Spanish for Estados
Unidos) and `OPT_DOUBLE` read it as a doubled marker for option E, which
discarded the five real inline options. Because the trigger is a word inside
the item, it followed the item across AZUL/CINZA/ROSA and read as unfixable.
Parser pin **v9** requires a doubled candidate set to cover A-E before it
outvotes inline candidates. Measured across all 57 booklets: 5 items change
candidate selection, 3 are this fix, and the other 2 still report unparsed.
2015 LC is now 50/50 and its `item_set_match` is TRUE.

**Nine rows are excluded under R3** -- every one annulled by INEP with
`TX_GABARITO='X'`, so there is no correct answer to ship, and each matches the
manifest's own `no_scorable_key_not_shipped`:

| year | area | item | INEP's reason |
|---|---|---|---|
| 2018 | MT | 30294 | Anulado |
| 2020 | CN | 32352 | Anulado |
| 2020 | MT | 44322 | Anulado |
| 2021 | MT | 117674 | Anulado |
| 2022 | MT | 39443 | anulado pedagogicamente |
| 2024 | CN | 61076 | Pedagógico |
| 2025 | CN | 141557, 141774 | Previamente exposto |
| 2025 | MT | 31350 | Previamente exposto |

audit_batch.R confirms this is correct rather than a coverage gap: those years
report `n_items_live == n_items_candidate` with `item_set_match=TRUE`, i.e. the
live IRW tables exclude the annulled items too.

**2,026 items over these eleven years, plus 2023's 174 already shipped.**

## NEXT STEPS, in priority order

All 13 years now parse, join, fill and pass the key-string gate. What remains is
packaging, plus three confirmations.

### 1. DONE 2026-09-16: batches assembled, all R10 gates green
`~/irw/itemtext/itemtables/batch_enem_<YYYY>/` for the eleven unshipped years,
on branch `mateus/itemtext-enem-allyears`. Built by
`30_collect_facts.py` -> `facts.json` -> `31_assemble_batch.py`, so every count
and item code in the sidecar prose is read off the tables rather than typed.

normalize_nulls.R / lint_verification.R / check_provenance.R / audit_batch.R
all pass. 48 tables: 12 PASS, 36 WARN, and ZERO hard-gate failures --
`item_set_match`, `resp_set_match`, `uses_raw_resp`, `canonical_nulls` TRUE on
all 48 and `pct_item_text_missing` 0 on all 48. The WARNs are the two classes
Ben already accepted for 2023: blank option_text on bare-figure items, and LC
row-count anomalies.

NOT COMMITTED and NOT uploaded. `validate_items.R` was not run; audit_batch
covers the item and resp sets, which is what the join gate needs.

### 2. DONE 2026-09-16: microdata gate run for ALL 13 years
Every year is now verified against INEP's printed-position key strings, not
just against the printed gabarito PDF. 2017/2020/2022 were the last three.
One MISMATCH in the whole corpus: 2017 LC on LARANJA, 43/45, traced to two
errors in INEP's own accessibility key string (STATUS.md trap 31). Our
`correct_response` is right and was not changed.

The gate itself was broken until today (traps 29, 30): its `PRINTED_LO` was
hardcoded to the 2017+ day order, so untested areas scored n=0, dropped out of
the denominator, and a single passing area printed as "EXACT". 2019/2024/2025
were re-run on the fixed gate and hold at 100%; 2024's headline moved from a
false "180/180 (LARANJA)" to an honest "318/318 on AZUL+AMARELA, 4/4 areas".

### 3. DONE 2026-09-16: the figure items, and 2021's notation
Both rulings implemented -- see "Decisions" below. Corpus-wide glyph residue is
now **2 markers**, both in one 2021 item's `option_text`.

### 4. Two quality passes that came out of a cross-booklet check
`26_strip_page_furniture.py` (pinned v8) removed printed page furniture --
barcodes, running heads, InDesign filenames, the essay draft page -- from
`item_text`/`option_text`/`instructions` in every year. It was found by
extracting 2016 CH/CN from AZUL *and* BRANCA and diffing by CO_ITEM; the two
booklets disagreed precisely because the furniture is booklet-specific, which a
single-booklet check cannot see. Re-run it after any re-parse; it is idempotent.

## Decisions — RULED, and what is still open

### RULED 2026-09-16 by Mateus, both now implemented

1. **Bare-figure options -> `option_text` = NA.** Following Ben's rule in
   #1848 ("generated descriptions go in `item_text` only, always marked, never
   in `option_text`"), which he had already applied by blanking `option_text`
   on 2023's `78578` and `125902`. Four items recovered; no text generated.
   2013 and 2016 reached **185/185**; 2018 and 2021 reached their maximum.

2. **2021's notation: decode what is decidable, describe the rest, mark it
   clearly.** Mateus: "there could be some description, analogous to what the
   accessibility booklets do, but make sure it is noted as a description
   clearly so it does not get erroneously computed as item text."
   Result: **545 of 770 markers (71%) were DECODED**, not described -- they
   were SymbolMT, already solved for 2018/2022 (traps 32-33). The remaining
   225 became an inline, Portuguese, explicitly-AI-marked note. `option_text`
   was never written to.

### Still open

3. **2015 LC 67408** -- the corpus's one missing item. Clean A-E prose that
   defeats the pinned parser in all three colours. Recoverable; needs a parser
   change, which must not be done mid-flight without a full re-run and re-gate.

4. **The 12 described notation gids** (`237` negative charge, `314` reaction
   arrow, `307` phi, `1859` g, `2029` v, `4231` ff, `38` arrow, `2288`
   subscript, and `34`/`540`/`1828`/`3032` unidentified). Context forces most
   of them, but their FONT attribution does not (MT-Extra / CambriaMath / high
   Arial gids), so they were described rather than asserted. Supplying the real
   CambriaMath and MT-Extra faces would settle them.

5. **2020 day-1 `instructions`** is 17 words: the cover text extracts to 195
   characters at source. Ship thin, or set it to NA? Not our defect either way.

6. **The licence question** is narrowed to the generated figure descriptions,
   and Ben said to ignore it for now (2026-09-14).

## Pipeline

    10_year_manifest.py        R0/R2/R3 for 13 years -> manifest.json
    11_fetch_missing.sh        rate-limit-aware fetch; INEP omits its TLS intermediate
    12_parse_booklet_pdf.py    booklet PDF -> items + <out>.cover.txt
    12_parse_booklet_pdf.v6.py PINNED. ALWAYS run `cut_pin.sh --check` first
    13_join.py                 position+TP_LINGUA -> CO_ITEM; R3/R6/R7; section_prompt
    14_fill_gaps.py            swapped items from a standard booklet, right colour
    15_validate_year.sbatch    R10 gate, 64G, logs val_<name>_<jobid>_<task>.out
    16_verify_gabarito.py      printed keys vs TX_GABARITO
    17_decode_2018.py          repairs 2018/2015/2016 PDFs (injects ToUnicode)
    17_decode_2021.py          repairs 2021 (outline-matched glyph map)
    18_validate_decode*.py     decode quality vs an OUT-OF-SAMPLE ceiling
    19_parse_dosvox.py         DOSVOX text -> the same contract (2023-2025)
    20_verify_gabarito_microdata.py  STRONGEST check; reaches the accessibility
                               booklet; needs no download
    20_geom_options.py         recovers option labels geometrically when a figure
                               absorbs a letter (supplement, not a second parser)
    21_gab_strings.py          extracts the key strings for any year, by column NAME
    cut_pin.sh [--check]       cuts a pin and PROVES it matches; --check for staleness


New since 2026-09-15:
  `13_join.py --colour <TX_COR>`  standard-booklet path for years with no
      accessibility edition (2013, 2015, 2016). Requires exactly ONE CO_PROVA
      at that colour for the area, so an ambiguous colour is reported, not
      picked. Pinned **v10**.
  `25_repair_2021.py`  completes 2021's /ToUnicode inside the PDF using
      17_decode_2021.py's derived map, so the PINNED parser reads 2021 like
      every other year. Pinned **v1**.
  `17_decode_2018.py repair <in> <out>`  works UNCHANGED on 2015 and 2016 --
      same pathology, same Arial CID order. No new decoder was needed.
  `cut_pin.sh <version> [script.py]`  now pins any script, and REFUSES a
      version tag that looks like a filename (it silently pinned the wrong
      file once).

The position convention is now MEASURED, not chosen from a list: `13_join.py`
derives `printed_lo - CO_POSICAO_lo` per area and records it as
`derived_offset` in `join_report.json`; `14_fill_gaps.py` reads that same
number instead of re-deriving it. 0 for a continuous year, +45/-45 for
per-area, and 2016's CH -45 / CN -45 / LC +90 / MT 0 falls out with no special
case. Verified byte-identical on 2017/2019/2020/2022.

## The one thing to internalise

`validate_items.R` compares item sets and resp sets. It CANNOT see garbled text
(2021 CH/LC passed at 93% glyph tokens), a position offset within the set (2017
LC was off by +5 and passed), rows per item (2018 LC had 10 rows and two resp=1
and passed), a blank `instructions`, an option letter emitted as its own option
text, or a figure description in the wrong field. Every serious defect found in
this project passed the gate. Run the gabarito check and a text-quality check on
every year, and read STATUS.md's trap list before trusting a green run.
