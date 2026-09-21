# RESUME — ENEM item text, PR #2226

**The single entry point. Read this first, then `EXTRACTION_RULES.md`
(the contract) and `STATUS.md` (per-year state and 67 documented traps).**

Last updated **2026-09-21**. Branch `mateus/itemtext-enem-allyears`,
HEAD **`667b1fcc`**, pushed, working tree clean. Nothing running.

---

## 1. Where this stands in one paragraph

Item text for every remaining ENEM year — 2013, 2015–2022, 2024, 2025 — as
44 tables, 2,026 of 2,035 published items. 2023 shipped earlier in #1848.
PR **#2226 is open** (not a draft; Ben is actively reviewing). Everything is
committed and every gate passes. **Nothing is uploaded to Redivis**; upload is
a separate manual step that has not been taken.

## 2. Current verification state

```
41_staleness.py    committed tables match a fresh pipeline build exactly
audit_batch        44 tables: 11 PASS, 33 WARN, 0 ERROR   (Slurm, ~1h25m)
lint_verification  44 rows, no problems
check_provenance   exit 0
UNFIXED gate       0 failures across all 48 committed files
content            0 control chars, 0 U+FFFD, 0 page furniture,
                   0 unmarked "x 10NN", Ben's S1 and S2 both 0
```

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
| Ben's response to the 2026-09-21 comment | Ben — nothing to do until he replies |
| Redivis upload, **after merge** | manual: `red_up itemtables` |
| the three 2021 tables carry `description_source=partly_generated` and owe a line on the public issues page (ruling 2026-09-11) | after merge |

Mateus posts PR comments. The last one was posted at his explicit request;
**do not post on his behalf without being asked.**

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
  EXTRACTION_RULES.md  R0-R14, the contract
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
