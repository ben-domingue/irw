# RESUME — ENEM item text

**The single entry point. Read this first, then `EXTRACTION_RULES.md`
(the contract) and `STATUS.md` (per-year state and the documented traps).**

Last updated **2026-10-02**. Branch `mateus/enem-itemtext-adjustments`.

---

## 1. Where this stands in one paragraph

The twelve years of item text SHIPPED. PR **#2226 merged 2026-09-24** (squash
`c72193df`), and #2405 stamped `uploaded=2026-09-24` on all 44 tables, so the
Redivis step is **done** — do not re-run it. The work now in flight is
**#2462**, Santiago's full read of 2013–2025: 557 findings over 371 items, 121
of them meaning-changing, in `~/enem_text_check_2013_2025.csv`.

**That review is being worked class by class, meaning-changing first, and the
PR is deliberately NOT open yet** — Mateus wants every change he intends to
make settled first, then one PR along the lines of "ENEM adjustments".

### #2462 progress

| class | findings | state |
|---|---|---|
| `misplaced` + `owner_missing_description` | 46 | done — `e2c67379`, 30 blocks relocated |
| script half of `flattened`, + Ben's watermark lead | ~20 | done — `d6b822ed` |
| `symbol` | 19 | done — `a801f199` + the drawn-glyph commit |
| `number` | 23 | **open.** Geometry CANNOT separate these; needs an explicit per-item patch table. See §7. |
| rest of `flattened` (fractions, factorials) | ~50 | open — `53_stacked_fractions.py` work |
| `figure_labels`, `essay_material`, `moved_word` | 15 | open |
| cosmetic / noise / incomplete | ~380 | open |

Three new passes and one new rule came out of it: `56_reading_order.py`
(spans emitted out of visual order), `57_drawn_glyphs.py` (glyphs the booklet
draws rather than sets as text) and **R16**, which is the ruling that reading a
glyph off `get_drawings()` is recovery rather than generation.

## 2. Current verification state

```
validate_items     20/20 OK + 16/16 OK on the years #2462 touched (Slurm)
audit_batch        item_set_match and resp_set_match TRUE everywhere, 0 ERROR
lint_verification  36 rows, no problems
check_provenance   exit 0
UNFIXED gate       0 failures
54 audit           0 unclassified
content            Ben's S1 and S2 both 0; regress48 0 on all five checks
character set      no code point added or removed by #2462 except U+20D7
```

**A REBUILD WRITES A YEAR'S TABLES BEFORE ITS POST-PASSES RUN.** If a rebuild
is killed mid-year, that year's tables look complete and freshly dated while
53/54/55/56/57 never ran — so earlier fixes appear REVERTED. This happened once
and nearly reached a commit. Always check

```bash
grep -c "rebuilt ->" <rebuild log>      # must equal the number of years
```

before trusting a build, and start long rebuilds with `nohup setsid` so a
session disconnect cannot kill them.

Re-run the cheap ones any time:

```bash
cd ~/enem/itemtext_run/allyears
python3 41_staleness.py                     # the one that matters
python3 /tmp/.../regress48.py _rb           # also in itemtext/enem_pipeline/
Rscript ~/irw/itemtext/.claude/skills/irw-auto-itemtext/scripts/lint_verification.R \
    $(ls -d ~/irw/itemtext/itemtables/batch_enem_20{13,15,16,17,18,19,20,21,22,24,25})
```

`audit_batch` is the expensive one (45M-row response CSVs per table, ~1h25m at
96G on Slurm). It needs `--resp-dir /scratch/users/mazzafe/itemtext_resp_flat`,
a flat symlink farm over the **#1942-CORRECTED** CSVs in
`/scratch/users/mazzafe/fix1942_run/work/*/`. The similarly named
`/scratch/users/mazzafe/enem_output/regular` is **pre-#1942 and wrong**.

## 3. What is waiting on someone

| what | who |
|---|---|
| **2022 CH 97262** — the only edit so far that DELETES shipped text. Its `TEXTO 2` was a scrambled percentage dump that inverted the item's answer; it was replaced with the correctly-paired prose. `EXTRACTION_RULES.md` records it as **NOT YET RULED** with an R11 bullet. Reverting is a one-line change. | Ben, in the #2462 PR |
| the three 2021 tables carry `description_source=partly_generated` and owe a line on the public issues page (ruling 2026-09-11) | still outstanding from #2226 |
| whether to keep pushing through #2462's remaining ~480 findings in one PR or split | Mateus |

Redivis upload for the 44 tables is **DONE** (#2405, uploaded=2026-09-24).
Anything re-touched by #2462 will need re-uploading after that PR merges.

Mateus posts PR comments. **Do not post on his behalf without being asked**,
and he is NOT replying to Santiago directly — the three corrections to that
review go in the PR body instead:

- the `owner_missing_description` detector appears to have covered only CH and
  LC; 8 further owners in 2018 CN/MT are missing a description by the same
  test, so its 18 understates it;
- the `watermark` scan found 2021 CN and MT only. All FOUR 2021 tables were
  affected; CH and LC carry a differently-spaced variant (`1 NE2 0 2 ME`);
- `43554 -> 86222` does not reproduce — `55_recover_tables.py` had already
  fixed it under R14, so that finding read a pre-recovery snapshot.

## 4. What the work actually was

Thirteen years of booklets, joined to INEP's microdata. The hard parts, all
documented as rules:

- **R0–R11** — the original contract: join on `CO_ITEM` never position;
  measured position offsets; annulled items excluded; no translations; gates.
- **R12 stacked fractions** — `AC = 7/5 BD` extracts as `AC = 7 BD5`. A
  stacked numerator is printed at *full body size*, so the superscript pass
  cannot see it; the only signal is the drawn **bar**.
- **R13 misplaced descriptions** — accessibility editions sometimes park a
  figure description at the foot of a page, describing a *different* item.
- **R14 dropped tables** — the same editions sometimes keep the sentence
  pointing at a table and lose the numbers. Recovered from the standard
  booklet.
- **R15 recovery is not generation** — Ben's ruling of 2026-09-21: text taken
  from INEP's own standard booklet owes no `(gerada por IA)` marking, on two
  conditions — same exam and year, and the stem already points at the missing
  content. Anything wider goes to R11 before it ships.

Four font pathologies were repaired inside the PDFs (CID-keyed CFF with no
glyph names; `/gNNN` names with incomplete ToUnicode; SymbolMT over Adobe
Symbol; MyriadPro's ten CIDs above its ASCII run).

## 5. The five things most likely to bite the next session

These are the ones that cost real time. Full list: traps 1–67 in `STATUS.md`.

1. **A green gate is not a correct item.** Every defect found in the last two
   rounds left `item_set_match`, `resp_set_match`, the control-character count
   and the missingness rate untouched. The instruments that actually found
   them were Ben's sampling and the model-answering check — not gates.
2. **These CSVs are written by R.** Character columns quoted, numeric and `NA`
   bare, header always quoted. Python's csv writer cannot reproduce that and
   rewrites every line: a three-cell fix once became a 24,000-line diff across
   48 files. Use `_rcsv.py` (`quoted_columns()` + `write_r_csv()`), which
   round-trips all 48 byte-identical, or `_rawedit.py`'s `rewrite_field()`.
3. **`out_rb` is the canonical build.** It is what `41_staleness.py` compares
   the repo against. `30_collect_facts.py` used to point the assembler at
   `out_v8` and bare year roots, which would have reverted three rounds of
   fixes. The refusal gate cannot catch that: a reverted fraction or subscript
   leaves text that reads perfectly well.
4. **Post-passes interact.** `48_mark_scripts.py` inserts characters into the
   very text `53_stacked_fractions.py` uses as its row-locating context. Run
   the *full* gate set after changing any pass, not just that pass's gate.
5. **Sample the output of any heuristic before believing its count.**
   `48_mark_scripts.py` has now shipped seven bugs, every one silently,
   because the result still reads as text. Two of the most recent were caught
   by reading a diff, not by a test.

## 6. What the goal actually is

**IRW item text is read for reading and linguistic complexity, not for
answerability.** That reorders priorities and is easy to forget:

- **High**: truncated stems, lost clauses, text spliced in from another item,
  page furniture, garbled glyphs, duplicated option letters — anything that
  changes the character stream.
- **Low**: a figure nobody described, a numeric relation living in a diagram.
  Plenty of items ship `option_text = NA` under R5 and that is fine.

The model-answering check is still the best defect detector, but read its
misses as *candidates*, not verdicts — figure-dependent items fail for reasons
that are nobody's fault.

## 7. Known, disclosed, not fixed

- **2015 MT 62901** — the card figure's `4/3` is left flattened (2 occurrences
  in text, 1 measured bar). The prose is faithful; only the figure's spatial
  layout is lost, which does not matter under §6.
- **2017 LARANJA LC 43/45** — a defect in INEP's own accessibility key string;
  three independent sources agree against it. `correct_response` unchanged.
- **9 items excluded (R3)** — every one annulled by INEP (`TX_GABARITO='X'`).
- **16 items (0.8%)** with stems under 180 characters, because the stimulus is
  a cartoon or charge the source never describes.
- **2018 CN 89518** — INEP's own prose description of the circuit is ambiguous
  ("two branches in parallel" reads as 4 kΩ; the key implies 6 kΩ).
- **`F072 → ρ`** ships the spec reading with the uncertainty written down.

## 8. Layout

```
~/enem/itemtext_run/allyears/          the working pipeline (source of truth)
  RESUME.md          this file
  EXTRACTION_RULES.md  R0-R15, the contract
  STATUS.md          per-year state + traps 1-67
  MODEL_CHECK_100.md the 100-item check and its six misses
  PR_BODY.md         the PR body as posted
  REPLY_COMBINED.md  the 2026-09-21 comment as posted
  NN_*.py            the passes; NN_*.vN.py are immutable pins

~/irw/itemtext/enem_pipeline/          mirrored into the repo, once
  pins/                                the pinned versions each build used
~/irw/itemtext/itemtables/batch_enem_<YYYY>/
  *__items.csv  audit_report.csv  verification_merged.csv
  scripts/README.md                    which pins built THIS year, with md5s

/scratch/users/mazzafe/itemtext_years/<YYYY>/out_rb/   the canonical build
/scratch/users/mazzafe/itemtext_resp_flat/             response CSVs for audit_batch
```

Rebuild everything from the source PDFs in about six minutes:

```bash
cd ~/enem/itemtext_run/allyears && python3 42_rebuild.py --all
python3 41_staleness.py        # must say "match a fresh pipeline build exactly"
```

## 9. Working agreement

Stop and report every ~10–20 minutes; never go quiet. Ask before launching
anything slow, and when it is approved launch it disconnect-proof (`sbatch`,
or `setsid`+`nohup` with output on `/scratch`) with a watcher reporting back.
Check the PR for new comments each round. Read the clock with `date` rather
than estimating elapsed time from turn count — that estimate has been wrong by
15× in both directions.
