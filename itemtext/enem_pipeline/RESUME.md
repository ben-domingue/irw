# RESUME — ENEM item text, PR #2226

Last updated 2026-09-20 12:10. Branch `mateus/itemtext-enem-allyears`,
HEAD **57411171**, pushed. Working tree clean.

## State: everything is committed and verified

    41_staleness.py   -> committed tables match a fresh pipeline build exactly
    UNFIXED gate      -> 0 failures
    lint_verification -> 44 rows, no problems
    check_provenance  -> exit 0
    Ben's S1 / S2     -> 0 / 0 on the committed tables
    trap 50's shapes  -> 0 / 0 / 0

Nothing is uploaded. Upload is a separate manual step (`red_up itemtables`).

## THE ONE THING STILL RUNNING

`audit_batch` on Slurm, **job 1733101**, output
`/scratch/users/mazzafe/itemtext_audit-1733101.out`.

    grep -c Auditing /scratch/users/mazzafe/itemtext_audit-1733101.out   # of 44
    grep AUDIT_DONE  /scratch/users/mazzafe/itemtext_audit-1733101.out

It was at 22/44 when the last session ended and takes ~2.5 h (45M-row response
CSVs per table). **It is auditing the tables as they were BEFORE the script-
marker sync**, so when it finishes, compare its verdicts to the previous run's
and re-run only if a verdict changed. Resubmit with:

    sbatch /tmp/.../scratchpad/audit.sbatch      # if that scratchpad is gone:
    # 96G, 6h, loops years 2013 2015 2016 2017 2018 2019 2020 2021 2022 2024 2025
    # Rscript itemtext/.claude/skills/irw-auto-itemtext/scripts/audit_batch.R \
    #     itemtext/itemtables/batch_enem_$y --resp-dir /scratch/users/mazzafe/itemtext_resp_flat

`/scratch/users/mazzafe/itemtext_resp_flat` is a flat symlink farm over the
#1942-CORRECTED response CSVs in `/scratch/users/mazzafe/fix1942_run/work/*/`.
Do not use `/scratch/users/mazzafe/enem_output/regular` — those are pre-#1942.

## THE ONE THING WAITING ON MATEUS

A reply to Ben is drafted and **not posted**. Mateus posts it himself.

    ~/enem/itemtext_run/allyears/REPLY_COMBINED.md     <- post this one
    ~/enem/itemtext_run/allyears/REPLY_BEN_SCRIPTS.md  <- its first half
    ~/enem/itemtext_run/allyears/REPLY_TO_BEN_v2.md    <- its second half

It needs one edit before posting: it still says the 100-item check found
"one defect"; the commit and MODEL_CHECK_100.md have the corrected reading
(43849 is figure-dependent too, so 72/74 = 97% with no miss traceable to our
text). REPLY_COMBINED.md already carries the corrected version — check it
reads consistently end to end.

## What changed in HEAD (57411171)

Three defect classes, all invisible to every content gate:

1. stacked fractions        -> `53_stacked_fractions.py` (R12)
2. misplaced descriptions   -> `54_relocate_descriptions.py` (R13)
3. script markup            -> `48_mark_scripts.py` v6, from Ben's review

Plus `_rcsv.py` (writes R's CSV dialect byte-exactly — do NOT use
csv.DictWriter on these files, it rewrites all 48) and `_rawedit.py`.

`30_collect_facts.py` now points the assembler at `out_rb`. It used to point
at `out_v8` and bare year roots, which would have reverted everything above.

## If you pick this up cold

    cat STATUS.md              # traps 1-64, the whole failure history
    cat EXTRACTION_RULES.md    # R0-R13, the contract
    cat MODEL_CHECK_100.md     # the 100-item check and its six misses
    python3 41_staleness.py    # is what's committed what the pipeline makes?

## Open, not started

- 2015 MT 62901's card-figure fractions: `6/8` fixed, `4/3` deliberately left
  (2 occurrences in text, 1 bar — the card list is a scrambled figure).
  Disclosed, not fixed.
- After merge: Redivis upload is manual; the three 2021 tables carry
  `description_source=partly_generated` and owe a line on the public issues
  page (ruling 2026-09-11).
