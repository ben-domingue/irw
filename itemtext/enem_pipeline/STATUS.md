# ENEM item text, all years — status

Updated 2026-09-15. Read `EXTRACTION_RULES.md` first; it is the contract.
Working output per year: `/scratch/users/mazzafe/itemtext_years/<YYYY>/`.

## Where each year stands

| year | state | note |
|---|---|---|
| 2023 | **SHIPPED** (#1848) | 0 glyph tokens in 800k chars; 174/174 printed keys |
| 2017 | **4/4 PASS** | 185/185 printed, **per_area**; rebuilt on v8, QC clean; microdata **315/315 on AZUL and AMARELA, 4/4 areas**. LARANJA LC reads 43/45 -- traced to **2 errors in INEP's own accessibility key string** (trap 31), not to our data |
| 2019 | 4/4 PASS | 185/185 printed + 320/320 microdata; rebuilt on v8, 0 orphans |
| 2020 | **4/4 PASS** | 183/183 printed; rebuilt on v8, QC clean; microdata **316/316 on AZUL and AMARELA, 4/4 areas** (LARANJA has key strings for 2 of 4) |
| 2024 | **DONE, 4/4 PASS** | **318/318 microdata on AZUL and AMARELA, 4/4 areas**; 4 gaps filled from **AMARELA**. NB the earlier "180/180 (LARANJA)" was a 2-of-4-area total: LARANJA has key strings for CH and MT only |
| 2025 | **DONE, 4/4 PASS** | 314/314 microdata; LC shared passage in `section_prompt` (ruled) |
| 2022 | **4/4 PASS** | 184/184 printed; rebuilt on v8; **0 garbled** after 23_decode_symbolmt.py; microdata **318/318 on AZUL and AMARELA, 4/4 areas** (LARANJA has key strings for 3 of 4) |
| 2018 | **4/4 PASS** | rebuilt on v8 from the repaired PDFs; **318/318 microdata on LARANJA, AZUL *and* AMARELA, 4/4 areas each**; 183/185 (CN 111411 unsegmentable in both booklets; MT 30294 no scorable key -> R3) |
| 2013 | **4/4 PASS, 185/185** | joined via the new `--colour AZUL` path; **320/320 microdata, 4/4 areas**; CN 15947 recovered as a bare-figure item (`option_text`=NA per Ben's rule) |
| 2015 | **4/4 PASS, 185/185, 0 U+FFFD** | repaired with `17_decode_2018.py` (now carrying a MyriadPro table, trap 42); **320/320 microdata, 4/4 areas**; LC 67408 (Spanish) unsegmentable in AZUL *and* CINZA; 25 MyriadPro bullet glyphs left U+FFFD in LC item 6830 (printed position 118) |
| 2016 | **4/4 PASS, 185/185** | third convention **measured, not named**: CH -45, CN -45, LC +90, MT 0; **320/320 on AZUL and 320/320 on AMARELA**, 4/4 areas each; CN 97711 recovered as a bare-figure item (`option_text`=NA) |
| 2021 | **4/4 PASS, 184/185** | goes through the PINNED parser via `25_repair_2021.py` (ToUnicode completed *in the PDF*, per trap 22); **318/318 microdata on AZUL and AMARELA, 4/4 areas** (LARANJA has key strings for MT only -> reads NOT VERIFIED, by design); CN 62293 recovered as a bare-figure item; MT 117674 has no scorable key -> R3. Notation: **545 of 770 markers DECODED** as SymbolMT (traps 32-33), 225 replaced by an inline AI-generated description, 2 left in `option_text` per Ben's rule |

Eight of thirteen years pass their gates. 2015, 2016 and 2021 wait on font
decoding; 2018's decoder is done and generalising it to 2015/2016 is the open
question there.

## The pipeline

    10_year_manifest.py       R0/R2/R3 for 13 years -> manifest.json
    11_fetch_missing.sh       rate-limit-aware fetch; INEP omits the intermediate cert
    12_parse_booklet_pdf.py   booklet PDF -> items + <out>.cover.txt
    12_parse_booklet_pdf.v2.py  PINNED, md5 d345acc79464ea31c90f534bada963ae
                                parsing rules only -- does NOT write the cover
    12_parse_booklet_pdf.v3.py  PINNED, md5 a1d184e0f25a6c88d613c3c36e7b7d99
                                USE THIS ONE: same rules plus <out>.cover.txt,
                                which is what populates `instructions` (R7).
                                v2 was pinned one step too early; a year parsed
                                with v2 gets correct items and a blank
                                `instructions`, so re-parse with v3 and re-join.
    13_join.py                position + TP_LINGUA -> CO_ITEM; R3/R6/R7
    14_fill_gaps.py           swapped items from a standard booklet, at the right colour
    15_validate_year.sbatch   R10 item/resp-set gate, 64G under sbatch
    16_verify_gabarito.py     printed keys vs TX_GABARITO at the joined item
    17_decode_2018.py         injects a ToUnicode CMap into 2018's PDFs so the
                              PINNED parser reads them unmodified. Root cause was
                              Type0/Identity-H CID fonts with no ToUnicode and a
                              stripped cmap, NOT a "+29 cipher" -- the codes ARE
                              Arial glyph ids, and Mac glyph order happens to be
                              ASCII+29 over CID 3-97 only.
    18_validate_decode_2018.py  measures a decode against an OUT-OF-SAMPLE
                              ceiling (clean 2020 booklets vs a 2019+2023
                              lexicon). 83.1% vs an 83.6% ceiling is meaningful;
                              a bare word rate is not.
    19_parse_dosvox.py        DOSVOX text -> the same 8-column contract, for
                              2023-2025. 2024/2025 pack two areas per file.
    20_verify_gabarito_microdata.py  STRONGEST position check. INEP's own key
                              strings from RESULTADOS/MICRODADOS TX_GABARITO_*,
                              which exist for EVERY CO_PROVA including the
                              accessibility booklet that 16_ cannot reach, and
                              need no download.
    21_gab_strings.py         extracts those key strings for any year, resolving
                              columns BY NAME (2019's sit at 27-30/39-43, not the
                              19-22/31-35 of 2024/2025).
    cut_pin.sh                cuts a pin and PROVES it matches the working file.
                              v2 and v3 were both pinned before their fixes
                              landed; three agents lost time to it.

**Run every year against the pinned v2 copy.** A shared parser was edited
mid-flight on 2026-09-15 while five agents were using it, and 8 items' text
boundaries moved between versions. That was the orchestrator's error.

## Traps found, all of which pass a count-based check

1. Two option layouts: letter+text inline, and letter alone on its own line.
2. Options set in two columns extract out of order (2019 MT 177 = A,D,B,E,C).
   The printed letter is authoritative; order is layout only.
3. Wrapped options begin with a bare capital and register as option candidates
   (2020 MT 84253) -- use the last ASCENDING A-E subsequence, not a window.
4. Bare-figure options extract as "A D" / "B E" / "C" -> R5, five options with
   NA text. Never generate an option label.
5. The LC language-block header stays in scope for the whole area unless reset;
   it covers printed positions 1-5 only. ITENS_PROVA's TP_LINGUA confirms it.
6. TP_LINGUA is 0=Inglês, 1=Espanhol, from INEP's own dictionary. Both blocks
   have 5 items, so a swap changes NO count anywhere.
7. Item order is permuted across booklet colours: fill gaps at the CO_PROVA of
   the colour actually parsed, found via TX_COR.
8. A CH stem line containing "matemática" flipped the tracked area to MT for
   the rest of the section. Section headers are CAPITALISED; item prose is not.
9. "QUESTÃO 108 ." with trailing punctuation missed the marker and merged two
   items, showing up only in the --expect count.
10. The position convention is NOT the same every year: 2017 is per-area,
    2018-2020 and 2023 continuous. Detect it, then CONFIRM with
    16_verify_gabarito.py.
    **Decide it ONCE.** It was implemented in three places and wrong in all
    three, each failing differently: the join shifted LC by +5 silently, the
    verifier could not express the offset so its ceiling was 142/175 whatever
    the join did, and the filler quietly filled 0 of 9. The convention is now
    decided in 13_join.py, written to join_report.json, and READ from there by
    14_fill_gaps.py. Do not re-derive it anywhere else.
12. Small format differences between years break regexes that look general:
    2022 prints "(opção: inglês)" with a colon where 2019/2023 have none, which
    cost 10 LC items; 2022's text layer also prints every option letter TWICE
    ("AA Descrição"), which yielded no candidate at all and rejected the item.
13. 16_verify_gabarito.py only checks standard_prova_codes, but most shipped
    items come from the ACCESSIBILITY booklet. 2022's agent wrote a companion
    check against the accessibility gabaritos (169/169). Both numbers matter.
11. Compute nodes cannot see the login node's /tmp. Everything a Slurm job
    reads goes on /scratch.
14. Booklet COLOUR is not guessable from the caderno number: 2024/2025 CD1 is
    AZUL but CD5 is AMARELO. Confirm against TX_COR or by text alignment before
    filling -- the wrong colour attaches real text to the wrong item and every
    count still agrees.
15. Hollow option markers mean TWO different things. Markers INTERLEAVED with
    their text is the normal long-option layout and segments correctly. Markers
    all CONTIGUOUS with the texts following as a block cannot be segmented (the
    options wrap across lines), and must be REPORTED. Emitting NA there looks
    like a deliberate R5 ruling, passes every gate, and silently drops the real
    options -- it did exactly that to 2022 MT 47309/86840/89637, 240 words.
16. A genuine shared passage exists in 2025 LC ("Texto para as Questões de 6 a
    10"). Marker-based segmentation swallows it into the PREVIOUS item's option
    E and leaves five items with no stimulus, with no count moving. Detect
    orphan text between an option block and the next marker.
17. The gabarito URL convention on download.inep.gov.br is
    YYYY_GB_impresso_D<day>_CD<caderno>.pdf. The LEIA-ME's
    ENEM_YYYY_P1_GAB_NN_DIA_N_COLOUR.pdf names do NOT resolve there.
18. LC's key string in TX_GABARITO_LC is 50 characters, not 45: 1-5 are
    TP_LINGUA 0, 6-10 are TP_LINGUA 1, 11-50 are the shared items. Reading it as
    45 scores ~26%, i.e. chance, and looks like a mapping error.
19. Agents writing to the same filename clobber each other: two wrote
    18_validate_decode.py. Namespace per-year deliverables.
20. Output CSVs carry bare empty fields, not the literal NA token R8 wants.
    normalize_nulls.R fixes this when the batch_enem_<YYYY>/ dir is assembled;
    it is not done by the join.
21. A pin proves it matched the working file WHEN CUT, not that it still does.
    v5 went stale within 8 minutes and "use the pin" silently diverged from
    "use the current parser" again. Run `cut_pin.sh --check` before any year.
22. Do NOT repair a broken font by rewriting `/Differences`. pypdf follows PDF
    1.7 5.9.1: where ToUnicode covers a code the encoding becomes chr(code), so
    patching a name that ToUnicode already covers corrupted EVERY lowercase l
    and x in the 2021 booklets (codes named /J and /question). COMPLETE the
    ToUnicode CMap instead and leave /Differences alone.
23. A glyph map must be FAMILY-SCOPED and its membership measured. Handing
    SymbolMT Arial's letters silently turns maths symbols into words. No
    wildcard fallback: a face with no evidence decodes nothing and is reported.
24. The per-font ASCII offset is NOT constant. Arial's Mac order gives +29 over
    gid 3-97; MyriadPro gives +31 because it puts `space` at gid 1. Derive it
    from the font, never assume Arial's.
25. 2022's SymbolMT is DECIDABLE without rendering: code = GID + 29 for GID
    3-97, GID + 63 for GID >= 98. Cross-validated 13/13 against an
    independently-derived 2018 table, and g167-169 / g183-185 are the
    parenlefttp/ex/bt + parenrighttp/ex/bt triples of a large parenthesis.
27. A marker regex for INEP's "Descrição d..." block MUST require the colon.
    Without it, ordinary option prose matches ("baseada na descrição dos
    hábitos alimentares") and the exclusion guard blocks a real move: 2019 LC
    76167 kept 4,275 characters of stimulus (TEXTO III + "Descrição da
    imagem :") orphaned in option E because option A's prose tripped the guard.
    A loose marker can also damage in the other direction, by moving real
    option text to the stem.
26. A "before vs after" word rate can invert misleadingly. Before decoding,
    2021 scored HIGHER -- because only the 33% of text in the good font existed
    at all, and it was headings and credits. Report coverage (tokens 2.99x)
    alongside rate, and score against an out-of-sample ceiling.

## What the gates do NOT catch

`validate_items.R` compares item sets and resp sets. It cannot see:
- garbled text (2021 CH and LC PASSED at 93% glyph tokens)
- a position offset within the set (2017 LC was off by +5 and passed resp sets)
- rows per item (2018 LC had 10 rows and two resp=1 per item, and passed)
- a blank `instructions` column (every year, until 2026-09-15)

So a green `validate_items` is necessary and nowhere near sufficient. Run
16_verify_gabarito.py and a text-quality check on every year.

## Parser version history, and why it matters

Every pin is a real behaviour change; a year built on an older pin may carry a
defect fixed later. ALWAYS `cut_pin.sh --check` before running a year.

| pin | md5 | what it added |
|---|---|---|
| v2 | d345acc7 | three option-layout rules; NO cover emission |
| v3 | a1d184e0 | (mis-cut: v2 + cover only, none of the 2022 fixes) |
| v4 | f79eae2a | opção colon, doubled letter, R5 NA token, furniture |
| v5 | 25c155e0 | doubled-alone/multi, prefer-doubled, R5 reachable |
| v6 | 73ac54e4 | interleaved vs contiguous hollow markers |
| v7 | 1047999d | Descrição-guarded R5 decision + orphan block moved to stem |
| **v8** | **2c1e6419** | **Descrição marker tightened to INEP's block-header form (requires the colon), so ordinary prose no longer matches** |

v2 and v3 were both cut BEFORE the fixes they were meant to contain. Three
agents lost time to it. `cut_pin.sh` now proves the copy matches when cut and
`--check` reports staleness after.

## Disclosures each year owes its READERS, not just us

These belong in the table's `note` and `public_note` when the
`batch_enem_<YYYY>/` directory is assembled, so a data user sees them without
reading this file:

- **2025 LC carries a shared passage in `section_prompt`** (ruled 2026-09-15).
  Items 157750, 157751, 157775, 157779 and 157781 share one 3,892-character
  crónica, "De próprio punho" by Ana Elisa Ribeiro, printed as "Texto para as
  Questões de 6 a 10". It sits once in `section_prompt` on `section_id`
  `enem_2025_1mil_lc_2`; each item's `item_text` is its own stem only. A reader
  grouping by `item_text` would otherwise see five unrelated stimuli.
- **Wording is INEP's accessibility edition, not the printed booklet** -- every
  year sourced from a LEDOR/LARANJA booklet or DOSVOX text. Already ruled
  2026-09-11 and required in every note.
- **No English ships** (`translation_source=not_translated`), and why.
- **Items INEP flags `IN_ITEM_ABAN` but that keep a valid key are kept**, named
  per year with INEP's `TX_MOTIVO_ABAN`.
- **Generated figure descriptions** carry `(gerada por IA)` inline and
  `description_source=partly_generated`, and owe an issues-page entry.
- Any year shipping R5 `NA` option text, and which items.

28. A RANGE test makes the offset branch UNREACHABLE. `13_join.py` chose
    between two named conventions with `cps[0] >= printed_lo`. For 2016 CH that
    is `46 >= 1` -- trivially true -- so it took the "continuous" branch and
    keyed on CO_POSICAO 46 while the booklet prints that item at 1. CH, CN and
    LC matched **0 of 140 items**. This is the SAME bug already documented for
    LC at trap 10, in a different branch. The fix is not a third named
    convention but a MEASURED offset (printed_lo minus CO_POSICAO_lo), which is
    0 for a continuous year and so reproduces every year that already passed
    -- verified byte-identical on 2017/2019/2020/2022. `14_fill_gaps.py` had
    the identical defect and the identical fix.

29. 20_verify_gabarito_microdata.py had the SAME false-pass that trap 13's
    sibling had in script 16, and it survived because only script 16 was fixed.
    Its `PRINTED_LO` was hardcoded to the 2017+ day order, so for 2013 two of
    four areas matched no printed position, scored n=0, were dropped from the
    denominator, and the summary printed **"90/90 EXACT"** on the strength of
    MT alone -- while CH scored 100% under the *other* convention, which should
    have been a screaming contradiction. A summary that aggregates per-area
    results MUST refuse to print a total until it can say how many areas it
    scored. The script now scans every offset (no day-order table at all) and
    reports "N of 4 areas scored".

30. Fixing a defect in one script does not fix its copies. The hardcoded
    2017+ day order `{LC:1, CH:46, CN:91, MT:136}` appeared in THREE scripts
    (13_join, 14_fill_gaps, 20_verify_gabarito_microdata). Script 16 was fixed
    weeks earlier with `--printed-order`; the other three kept the bug and one
    of them was the gate that was supposed to catch it. Grep for the constant,
    not for the symptom.

31. INEP's OWN key string can be wrong, and the gate will blame you for it.
    2017 LC scores 315/315 on AZUL and AMARELA but **43/45 on the LARANJA
    accessibility booklet**, at two positions: item 39670 (printed E vs
    TX_GABARITO D) and item 29586 (printed C vs B). It is not ours:
      - ITENS_PROVA gives D and B for those items in **all five** colours,
        LARANJA included;
      - AZUL's and AMARELA's key strings both give D and B, 45/45;
      - the extracted option TEXT is character-identical between LARANJA and
        AZUL for both items, so no reordering could justify E and C.
    Three independent sources against one. `correct_response` stays D and B.
    Before "fixing" a 2-of-45 mismatch, check whether the SOURCE disagrees
    with itself -- and note that a 43/45 is the signature of a data defect,
    whereas a wrong position convention lands near chance (about 9/45).

32. "Undecodable" was 71% wrong. 2021's 770 surviving `[UNDECODED-gNNN]`
    markers were reported as needing a font we do not have. In fact 545 of them
    (71%) were SymbolMT, and SymbolMT was already SOLVED for 2018 and 2022:
    code = GID+29 (GID 3-97) / GID+63 (>=98) over the Adobe Symbol encoding.
    The reason they survived is not that they were undecodable but that
    17_decode_2021.py's map is family-scoped to the Arial-order families -- so
    "unmapped" was being read as "unmappable". Before describing a glyph, check
    whether another year's decoder already covers its FAMILY.
    The decode is self-validating: CN 88403 now reads
    `E° = -3,05 V ... I2 + 2 e- -> 2 I-`, and the accessibility booklet's own
    prose two lines earlier reads "potencial de redução igual a menos 3,05
    volts". CN 84331's table reads `+ / ++ / -`, matching the legend it prints.

33. Scope the decode by MEASURING which family declares each gid, never by the
    gid alone. In 2021, g83 is declared by ArialMT, Arial-BoldMT *and*
    SymbolMT; g38 by SymbolMT *and* Arial-ItalicMT. `29_decode_2021_notation.py`
    decodes a gid only when the declaring families MINUS the already-handled
    Arial-order ones are exactly `{SymbolMT}` -- which admits g83 and refuses
    g38. Applying the SymbolMT rule to every gid would have produced plausible
    wrong characters for CambriaMath and MT-Extra (trap 23 again).

34. A regex for glyph residue must not match `http://g1.globo.com`. `/g\d+`
    reported residue in 2013 and 2015 that was three news-site URLs. The real
    corpus-wide residue is 2 markers, both in one 2021 item's `option_text`.

35. There are TWO response-CSV directories and the obvious one is wrong.
    `/scratch/users/mazzafe/enem_output/regular/` holds all 52 tables in one
    place with tidy names and is dated **2026-07-14 -- PRE-#1942**.
    `/scratch/users/mazzafe/fix1942_run/work/<YYYY>/` is dated 2026-09-08 and is
    the CORRECTED build R10 requires. Auditing item text against the first
    would validate it against exactly the data #1942 fixed, and every count
    would still look right. Check the mtime, not the filename.

36. An inline generated-text marker must be the EXACT token the gate greps for.
    check_provenance.R matches `\((AI-generated|gerada por IA)\)`, so
    "(descricao gerada por IA)" -- the words inside a longer parenthetical --
    does NOT match, and all three 2021 tables failed the #1848 gate while
    looking correct to a human reader. Write "(gerada por IA)" as its own
    parenthetical. Also keep the accents: the marker sits in Portuguese prose
    and an ASCII-safe spelling was what caused this.

37. "EE UU" is Spanish for Estados Unidos, and it cost a whole item.
    OPT_DOUBLE (`^([A-E])\1\s*(\S.*)$`) matched the line "EE UU ha propiciado
    que cada vez mas estadounidenses..." as a DOUBLED marker for option E.
    split_options then preferred doubled candidates whenever ANY existed, threw
    away the five real inline options A-E, and reported 2015 LC item 67408
    unsegmentable. Because the trigger is a word IN THE ITEM, it followed the
    item across booklets -- AZUL position 95, CINZA 92, ROSA 93 -- which looked
    exactly like a property of the item rather than a parser bug, and it was
    written up as such for two sessions. A layout preference must require
    enough evidence to BE that layout: v9 takes the doubled set only when it
    covers A-E or numbers five. Measured effect across all 57 booklets: 5 items
    change candidate selection, 3 are the 2015 fix, and the other 2 (2013 CN
    15947 in AZUL and ROSA) still report unparsed, so nothing regressed.

38. A basename is not a file identity. 2013 and 2015 BOTH ship
    `Caderno7_Azul_Dom.pdf`. A regression harness that resolved the source PDF
    by basename re-parsed 2015's booklet while labelling it 2013, and reported
    a 2013 difference that did not exist -- which nearly sent a correct parser
    change back for rework. Disambiguate by the year in the path.

39. A stem-language classifier cannot tell you what the OPTIONS are.
    37 items ship `option_text=NA`, and the note claimed all but two were
    "DRAWINGS" on the strength of a regex over the last 300 characters of the
    stem. It read 2016 CN 86572 as a figure item because the stem mentions a
    circuit -- the options are the fractions 1, 4/7, 10/27, 14/81, 4/81. The
    word that matches describes the STIMULUS, not the answer, and shortening
    the window breaks the genuine figure items instead ("...visualizada da
    posicao em que se esta enxergando esse cubo, e"). The fix is not a better
    regex: name the items actually checked against the page, and say plainly
    that the rest were not. `facts.json` now carries VERIFIED_FIGURE and
    VERIFIED_NOT_FIGURE, and the generated prose distinguishes what was
    verified from what was inferred.

40. Re-running the assembler UN-NORMALIZES the tables. `31_assemble_batch.py`
    copies the item CSVs out of /scratch, and `normalize_nulls.R` had been run
    on the REPO copies only -- so regenerating sidecars silently reverts the
    literal-NA convention on all 44 tables. Always re-run normalize_nulls after
    the assembler, and check `git status` for `__items.csv` before committing:
    if a sidecar-only change shows item CSVs as modified, this is why.

41. R0 applies to PROSE as well as to data. The pipeline never confuses
    CO_ITEM with a printed position -- R0 forbids it and every gate would
    catch it -- but my own notes did: the U+FFFD case was written up as
    "2015 LC 118" in STATUS, HANDOFF, RESUME and the PR body for three
    sessions. 118 is its printed position; the item is **CO_ITEM 6830**. It
    surfaced only because 36_preview.py looked "118" up as an item code and
    printed a bare "NOT FOUND", which read like missing data rather than a
    typo in a label. Two habits fall out of it:
      - a disclosure must name the item by CO_ITEM, never by position, and
        "one item" is not a disclosure a reader can act on -- the shipped
        note now names 6830;
      - a lookup miss must say WHY it missed. "NOT FOUND" sent a reader
        looking for a data problem; the message now says it is a preview bug
        and that a printed number was probably used where an item code belongs.

42. "Left unresolved rather than guessed" can be the WRONG default, and it
    hid behind a bad label. 17_decode_2018.py mapped MyriadPro's printable
    ASCII run and set the ten CIDs above it to U+FFFD, which was honest about
    uncertainty. But those ten are not ornaments -- nine are LETTERS, and one
    item shipped reading "Use \ufffdgua tratada ... recomenda\ufffd\ufffdes
    quanto \ufffd restri\ufffd\ufffdo". It was written up as "25 decorative
    bullet glyphs" for three sessions because the bullet was the only one ever
    looked at, and the count (25) made it sound like a rendering nit rather
    than missing letters in six words.
    All ten were recoverable the same way SymbolMT was -- from the words they
    sit inside, each attested by one to four complete Portuguese words
    ("Egua"=agua, "mIos"=maos, "certiFque-se"=certifique-se, "saUde"=saude).
    Two lessons: a U+FFFD inside a WORD is a different severity from one
    between words, and worth separating in any report; and a count of
    replacement characters says nothing about how much meaning was lost.
    Corpus-wide U+FFFD is now 0.

43. The orphan-Descricao fix was declared DONE while missing three items,
    because its marker regex had four separate faults and only the easy case
    was ever tested:
      - `d[oaes]\b` cannot match the PLURAL headers. After "do" the \b fails
        on the following "s", so "Descricao das figuras:" and "Descricao dos
        graficos:" never matched at all.
      - `[^\n:]{0,40}` forbids a newline, but INEP wraps: "Descricao da matriz
        A de cinco colunas e cinco \nlinhas:".
      - 40 characters is shorter than INEP's real headers.
      - case-insensitive and unanchored, it ALSO matched ordinary prose --
        2017 LC 90020's option D reads "descricao do espaco, como em: ...".
        Trap 27 added the colon requirement to stop exactly this and it was
        not sufficient, because prose contains colons too.
    v10 anchors to a line start and requires the capital D, which separates
    INEP's paragraph header from prose far more cleanly than the colon did.
    Proven strictly better before shipping: it matches all 416 blocks the old
    regex found, misses none of them, and finds 26 more.
    The symptom that exposed it was not the marker at all -- it was option
    lengths of [1,1,1,1,346]. Look for SHAPE, not for the thing you think is
    wrong.

44. Detectors that find nothing are worth reporting. The anomaly scan ran
    twelve detectors; six found zero items (option letters other than A-E, a
    row count other than one correct per item, mixed NA across options, the
    key's option blank while others have text, an option carrying the next
    question's marker, a stem repeating itself). Those zeros are the evidence
    that the structural invariants hold, and they are more reassuring than the
    six that fired. Report them, and beware the one that fired on 1285 of 2026
    items: "stem does not end in punctuation" is ENEM's house style, where the
    option completes the sentence, not a truncation.

45. A DERIVED ARTIFACT can be stale even when every script is current.
    2018 shipped a thorn where a minus belongs. 17_decode_2018.py had had the
    right override for days; the REPAIRED PDFs were made before it and were
    never regenerated, so parse, join, fill, strip and every gate faithfully
    carried the wrong glyph. cut_pin.sh checks that a PIN matches its script.
    NOTHING checked that an ARTIFACT matches the script that produced it, and
    no content gate can: a wrong glyph leaves item_set_match TRUE.
    41_staleness.py now compares artifact mtimes against their producing
    scripts, and 42_rebuild.py rebuilds a year end-to-end from the source PDFs
    so a full rebuild is cheap enough to be routine. Nine of eleven years
    rebuild byte-identical, which is what makes the tenth meaningful.

46. Hand-applying a fix to the batch directories is not applying it. The glyph
    repairs and the 880 stripped option letters were run on
    itemtext/itemtables/<batch>/ and then SILENTLY REVERTED by the next
    31_assemble_batch.py, which recopies the tables out of /scratch. Trap 40
    recorded this for normalize_nulls, where the damage was cosmetic; here it
    would have un-fixed a wrong minus sign. Every post-pass now runs inside
    42_rebuild.py, so whatever the assembler copies is already final.

47. The same letter printed twice reads as prose. 2022's LEDOR booklet sets
    each option as "A A exalta a investigacao filosofica" -- marker, space,
    marker again -- and OPT_INLINE kept the second one, so 176 of 184 items
    shipped every option prefixed with its own letter. A per-option strip
    would be a guess, because for A the duplicate is ambiguous with the
    Portuguese article and for E with the conjunction. The distribution
    settles it: an item has FIVE self-prefixed options or ZERO, never one to
    four. Rules keyed to a whole option set are safe where per-option rules
    are not -- the same shape as the doubled-marker fix in trap 37.

48. Reading the ORIGINAL source distinguishes our bug from theirs. 2015's
    yogh-for-lambda and 2016's kra are present in the unrepaired INEP PDFs, so
    they are defects in INEP's own /ToUnicode and we were reproducing them
    faithfully. That changes the remedy from "fix the decoder" to "normalise a
    known-bad source character, with the evidence written down" -- and it is a
    one-line check that should precede any decoder change.

49. A commit message can describe infrastructure that is not in the
    commit. The previous commit credited 41_staleness.py, 42_rebuild.py and
    "post-passes as pipeline steps" as the evidence for its fixes. None were
    committed: 31_assemble_batch.py copied a HARDCODED LIST of 16 filenames
    into each batch directory, and every script written after that list was
    frozen lived only outside the repo. Ben caught it by running
    `git diff -- '**/*.py'` and finding it empty. The lesson is not "write a
    better message" -- it is that a list of files to copy will always fall
    behind the directory it is copying from. The pipeline now lives in the
    repo once, at itemtext/enem_pipeline/, and the batch directories keep a
    build record instead of copies.

50. Geometric superscript detection is a five-bug problem, and every bug ships
    silently because the result still READS as text:
      - an f/o span split read as a subscript: "conf_orme", "transf_ormacao"
      - a ONE-CHARACTER anchor matching mid-word: "T"+"A" is a real
        temperature subscript and also the start of TANTOS, PATRIOTA, HUERTAS
      - adjacent script runs each marked: "10^-^4" for 10^-4
      - an alphabetic script that does not END at a token boundary
      - uppercase word splits, which the lowercase rule did not cover
    The rules that survived: a script must change case or follow a
    digit/symbol; an alphabetic script must start AND end at a token boundary;
    adjacent runs collapse. Every one of those was found by SAMPLING the
    output, never by a gate -- there is no structural check that can see
    "conf_orme". Sample the output of any heuristic before believing its count.

51. Scope a fix by asking what the SOURCE contains. INEP's accessibility
    booklets spell notation out in words, so they carry almost no superscript
    spans at all -- the 2019 LEDOR booklet has zero. That single measurement
    bounded the superscript work to the standard-booklet years instead of all
    eleven, and it is the same fact that explains why only those years have
    items whose stem is too short to answer.

## Open decisions for Mateus / Ben

- Nothing outstanding as of 2026-09-15: decoders for 2018 and 2021 authorised,
  figure items ruled (R5 hybrid), translations dropped (#2180).
- Report back anything a decoder cannot recover, with the diagnosis.
