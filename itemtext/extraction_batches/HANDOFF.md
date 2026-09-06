# Item-text extraction — pick up here

Written 2026-09-03 at the end of the queue-restart session (#1709). Read this before
`BATCH_PROCESS.md`; it says where things stand and what is waiting on a human. The full
narrative is in `round_log.md` under batch_016, batch_017 and batch_018.

---

## Where the work lives

| | |
|---|---|
| worktree | `/home/ben/irw-queue-runner` — **use this, not `src`** (the old `/home/ben/irw-queue` is retired: 36 commits behind, stale cap) |
| branch | `itemtext/queue-rounds` (pushed; the wrapper merges `origin/main` in before each round) |
| runner | `itemtext/extraction_batches/run_round.sh` — **run it by hand, one round per triage session.** Nothing schedules it |
| review | a **standing PR** from `itemtext/queue-rounds` → `main`, opened by the runner and left open; rounds accumulate into it. **Merge it without deleting the branch** |
| staged for upload | `itemtext/itemtables/clean/` |
| protocol the cron reads | `itemtext/extraction_batches/round_prompt_v1.md` |

`src` is Ben's working checkout and moved branch three times during the session, twice mid-round.
A round that reads a reparked tree gets the wrong protocol and a stale `queue_state.csv`. That is
why this worktree exists. The old `/home/ben/irw-wt/1709` worktree is retired.

## Queue state at handoff

**1,177 pending · 151 done · 11 failed · 8 blocked · 54 excluded.** (The three `cdm_timss*`
tables moved from done to blocked on the #1891 ruling, 2026-09-04.)

Two rounds ran today: **batch_017** (12 written, 0 blocked) and **batch_018** (11 written, 1
blocked). Both capped deliberately as a trial; the cron self-cancelled at `batch_018` and
**nothing is running now**.

At 12 tables/round the remaining queue is roughly **98 more rounds**. The binding constraint is
not runtime — it is triage, at ~8 tables per round needing a human-supervised go/no-go.

---

## 1. Decisions waiting on you

**a. ~~[#1891](https://github.com/ben-domingue/irw/issues/1891) — TIMSS rights.~~ RULED 2026-09-04.**
IRW does not ship item wording carrying a **stated** non-commercial restriction — `datastandard.md`'s
NC rule now applies to item text as well as response data. All three `cdm_timss*` extractions are
**declined and removed**, 2003 included: its page says "in the public domain" *and* "non-commercial
… only", and the restriction governs. Checking the live IEA pages also showed **2011 carries the same
clause as 2007** with no public-domain statement, so the earlier "a ruling on 2007 does not transfer"
note does not hold. The rule fires on a quotable restriction only — never on an inference that a
scale is copyrighted or reproduced without an explicit grant, which was considered and rejected as
too broad. Written into `references/itemtext_standard.md` § Rights and BATCH_PROCESS Step 2.
Two follow-ons: a bounded audit of published tables sourced from publisher-administered
instruments, and the mixed-licence question (a table's dictionary `License` describes the response
data, not the wording) recorded there rather than made a schema change.

**b. `carver_2017_puggs_pilot1_attitudes` — ship pre-revision wording or not?** It carries the S3
questionnaire's English. Two agents independently established that the back-translation review
*preceded* the pilots and changed "diet" → "eating habits", so **S3 is one revision behind the
administered form** despite being titled "used in the first pilot study". Its mapping is sound and
its gates are green. Switching the wording base to the S4 Code Book is a re-extraction of one table.

**c. ~~Scheduling of itemtext rounds.~~ SETTLED 2026-09-04: there is no scheduler. Rounds are run
by hand, one per triage session.**

Read the sequence rather than assuming the last state:

1. Ruled the morning of 2026-09-04: crontab + `claude -p`, built as `round_cron.sh`. It is the
   **first unattended agent in this repo**; the others run deterministic scripts.
2. **It ran, once, and it worked.** batch_019: 19 minutes, exit 0, 7 tables written with
   `audit_batch` 7 PASS / 0 WARN, 4 determinate blocks, 1 failure. Every guard behaved. All 7
   survived a live re-run of the gates at triage; 6 shipped.
3. Ben cancelled it the same day and asked for a different system. **Crontab is out as a standing
   preference across projects** — "i have had no luck with crontab across a variety of different
   projects now." Earned: the version-manifest crontab entry ran **zero** times and said nothing,
   refusing silently because the live checkout was never on `main`. The failure mode is not
   misfiring, it is failing *quietly*. **Do not propose a crontab here.**
4. GitHub Actions — the answer for the version manifest (#1705, #1905, #1907) — was worked out
   properly for this job and **rejected**. It is not a straight lift, and the reasons are not
   about plumbing:

   - **The bottleneck is triage, not the trigger.** ~8 of 12 tables per round need a human
     go/no-go; at ~1,165 pending that is ~98 rounds. Any cadence faster than "when someone is
     ready to triage" grows an unreviewed branch, and the further it drifts from `main` the more
     likely the pre-round merge conflicts — which stops the queue outright.
   - **Spend, measured — in tokens.** Four complete rounds (2026-09-04, orchestrator + 12
     subagents summed from the jsonl under `~/.claude/projects/`): **570–670K output, 2.0–2.5M
     cache write, 42–54M cache read** per round. Cache reads dominate and the subagents are
     85–94% of them, so the orchestrator transcript alone understates a round about tenfold. At
     ~98 rounds the queue is **~4–5 billion cache-read tokens**; hourly would be ~1.2B a day.
     Nothing should spend that on a timer. **Quoted in tokens deliberately:** this is
     subscription usage, nothing in the transcripts records a charge, and the dollar figures this
     line used to carry were tokens × list rates rather than an invoice. What a round really
     consumes here is rate-limit headroom — an `ANTHROPIC_API_KEY` in CI would convert it into
     metered per-fire spend, and a `CLAUDE_CODE_OAUTH_TOKEN` would keep the exact rate limits that
     killed 8/12 agents in batch_018 and 4/12 in batch_019, unattended.
   - **A datacenter IP is the wrong place for this work.** The round's expensive step is fetching
     publisher, OSF, Dataverse, Europe PMC and CRAN sources. A Harvard Dataverse AWS WAF challenge
     already blocked three tables from *this* laptop. From Azure runner space it gets worse — and
     the damage is silent: it lands as `blocked`, and a wrong `blocked` quietly removes a table
     from the queue forever.
   - **Stuck rounds get more common, not less.** A cloud runner is cancelled, timed out and
     evicted more readily than the laptop; every death leaves 12 rows `in_progress`, which blocks
     every later round until a human reconciles. A concurrency group and `if: always()` cleanup
     bound it but cannot prevent it.
   - **`--dangerously-skip-permissions` does not transfer.** That posture was decided for a
     machine Ben controls and watches. In Actions it would run in a **public** repo, with
     `REDIVIS_API_TOKEN` and `GITHUB_TOKEN` in the environment and **public logs**, around an
     agent whose whole job is reading untrusted third-party files. `GITHUB_TOKEN` with
     `pull-requests: write` on a repo where `main` requires zero approving reviews is the same
     auto-merge capability the manifest job uses — so "the round cannot publish" would no longer
     bound the blast radius the way it does locally.

   Actions *would* have deleted real problems, and that is worth recording: a fresh checkout makes
   the self-snapshot `exec`, the dirty-worktree guard and the wrong-branch guard all unnecessary.
   It also throws away `.cache/<table>/` (gitignored; the cached sources that make triage minutes
   rather than hours). **If the GitHub ergonomics are ever wanted, the answer is a self-hosted
   runner on Ben's laptop** — residential IP, local credentials, local cache — not `ubuntu-latest`.

**Current state.**
- `extraction_batches/run_round.sh` (renamed from `round_cron.sh`) is the entry point. Run it
  when you sit down to triage. It still keeps every guard, still cannot publish, still reads the
  cap out of Step 0 of `round_prompt_v1.md`, and no longer opens a GitHub issue on failure —
  it exits nonzero and tells you, because you are the one who started it.
- **The crontab line `13 * * * * .../round_cron.sh` is still installed and must be removed.**
  An agent cannot do it — the permission classifier blocks crontab edits — so this step is Ben's:
  `crontab -e`, delete the line. It now points at a path that no longer exists, so it would fail
  hourly and silently until it is gone.
- `circuit_breaker.flag` is still set as a DELIBERATE PAUSE, not a trip. Once the crontab line is
  gone the flag has no job to do; delete it then.
- The cap is `batch_020`, so the next run does one round and stops. Raise it in Step 0 of
  `round_prompt_v1.md` for more.
- The runner worktree was found parked on `itemtext/handoff-scheduling-state` on 2026-09-04, not
  on `itemtext/queue-rounds`. The branch guard would refuse to run a round until that is put back.

**What the round cannot do, under any trigger:** publish. It writes `__items.csv` into a batch
directory and stops. Triage, staging into `clean/` and upload are all manual. That property is
what bounds the risk of `--dangerously-skip-permissions`, and it is not negotiable.

**The self-edit bug, fixed — do not reintroduce it.** `run_round.sh` merges `origin/main` into the
worktree it lives in, so a merge carrying a change to the script rewrites the file bash is
executing. git rewrites in place keeping the inode, and bash reads scripts lazily in 8KB blocks by
byte offset, so this really does corrupt — reproduced as `unexpected EOF while looking for matching
quote`. It bit once, harmlessly, on 2026-09-04. The fix is the snapshot re-exec at the top of the
script. Any replacement that both self-updates and runs from the updated file needs the same guard.

**d. Seven permission-blocked tables** (six `dwyer_2025_genomics_*`, `rd_ppsl7as_ghasemy_2024_sl`),
recorded `blocked` in `pending_index_notes.csv`. A rights question, not an access one.

**e. 27 stale rows on Sheet1 of the index workbook** — tables already published whose sheet rows
were never linked back. Your Google Sheet; nobody has touched it.

## 2. Open work items on #1709

- **7.3** ([#1745](https://github.com/ben-domingue/irw/issues/1745)) — 23 `data_labels` mapping
  claims never checked. **Today's backfill makes this urgent**: of five non-`data_labels` Step 3.5
  tables checked, **5 of 5** had an overstated `mapping_basis`.
- **7.4** ([#1770](https://github.com/ben-domingue/irw/issues/1770)) — verify the SKIP side of Step
  3.5's cheapness gate, 24 tables skipped on an unchecked claim.
- **7.2** — Stanford API key for #1406. You said you're on it.
- The `itemcode_map/` proposal was **dropped** (recoverable from `data/<table>.py`); Step 3.5's
  verification gap was **closed** (#1885).

## 3. Findings from today that need someone

| finding | where |
|---|---|
| `anh_2026_*` deposit: ~45 items across **six** constructs all within 0.04 of the scale midpoint, SD≈1.0 | round_log batch_017 |
| `anh_2026_finbehavior` (already live) needs the Portuguese/Vietnamese language backfill — closes a `NEEDS_REVIEW` row | `language_backfill/audit_2026-09-01.csv` |
| Both `campos_2023_*` tables **pool two administered languages** (Finnish + Portuguese); schema assumes one | round_log batch_017 |
| `cdm_timss07` Description says **Australia**; CDM's docs say **Austria** (698 students) — 5th dictionary defect | #1891 |
| `chanal_2020_anglais` + 4 siblings: Description says self-concept, data are the **motivation** questionnaire | `pending_index_notes.csv` |
| `instrument` string differs between `carver` siblings | round_log batch_018 |
| TIMSS `resp` encoding differs between `cdm_timss03` and `cdm_timss07` | round_log batch_018 |

Five `data fix` issues were filed from batch_016: #1875–#1879.

## 4. Gotchas learned the hard way today

- **Count CSV records with a parser, never `wc -l`.** These files carry embedded newlines in quoted
  fields; `wc -l` reported a table at 104 rows when it had 52, which looks exactly like the doubling
  failure `red_up` guards against. It can also mask a real one.
- **Delete sidecars BY NAME.** `rm -f verification_*.csv` matches `verification_merged.csv` — the
  file Step 3 just told you to create. This destroyed batch_016's nine verification rows; they were
  recoverable only because each agent could be resumed. Fixed in the protocol.
- **`validate_items.R` now takes `--table-sets`** so the hard gate no longer needs a full export.
  Use it on published tables.
- **Released-item PDFs are often rasterised.** `pdftotext` returns only header metadata, so a
  text-only pass concludes "no wording" and blocks incorrectly. Three agents hit this on TIMSS.
- **A spend-limit kill leaves orphaned `__items.csv` files** with no provenance. At merge time those
  are indistinguishable from finished tables. Quarantine them; do not mark the tables `failed`
  (nothing was determined about them, and it would trip the breaker on a false premise).
- **Processing scripts are frequently not named after their table.** `neurips_2020` →
  `data/neurlps_2020.R` (a typo); one script often writes 5–12 tables. Grep, don't guess.

## 5. To restart the queue

1. ~~Settle (c)~~ **SETTLED: run `extraction_batches/run_round.sh` by hand.** Two things must
   happen first: Ben removes the crontab line (`crontab -e`), and the runner worktree goes back
   onto `itemtext/queue-rounds`. Then delete `circuit_breaker.flag`.
2. ~~Raise the cap~~ **done 2026-09-04: the cap is now `batch_020` in Step 0 of both
   `BATCH_PROCESS.md` and `round_prompt_v1.md`, which allows two more rounds (019, 020).** Re-raise
   it before any run beyond that. The off-by-one: the cap self-cancels after *completing* that batch.
3. ~~Confirm~~ **checked 2026-09-04: no `circuit_breaker.flag`, 0 `in_progress` rows, no `clean/`.**
4. Run `extraction_batches/run_round.sh`. It reads `round_prompt_v1.md` itself. One round, then
   triage what it produced before running another.
