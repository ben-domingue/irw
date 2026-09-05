# Item-text batch extraction — round protocol

How the `itemtables/batch_NNN/` extraction runs work, and how to start one.
Companion to `.claude/skills/irw-auto-itemtext/SKILL.md` (which covers per-table
extraction) — this file covers the batching layer. The round's own prompt is
`extraction_batches/round_prompt_v1.md`; the entry point is
`extraction_batches/run_round.sh`, which a human runs.

## State on disk

| Path | What it is |
|---|---|
| `extraction_batches/queue_state.csv` | `table,status,batch,timestamp`; status is `pending`/`in_progress`/`done`/`failed`/`blocked`/`excluded`. `failed` and `blocked` are BOTH "no CSV" but mean different things and are counted differently by the circuit breaker (Step 5, ruled 2026-09-03): `failed` is a fault or an unresolved access failure that an unchanged retry might get past, and it counts; `blocked` is a determinate verdict that an unchanged retry cannot change, and it does not count. `blocked` is not permanent the way `excluded` is -- it says a HUMAN action or a data change is needed first, so these are the pool to revisit when one happens. Seeded from the AVAILABLE rows of `availability_audit_full.csv`. **The only state that must persist between rounds.** `excluded` means do not extract, ever — see the standing exclusions below. |
| `extraction_batches/round_log.md` | One entry per round: counts, notable findings, open items. |
| `extraction_batches/circuit_breaker.flag` | Present = a round failed >30% and the loop stopped for human review. Delete it to resume. |
| `itemtables/batch_NNN/` | `{table}__items.csv` (validated output), `notes.csv`, `provenance.csv`, `verification_merged.csv`, `audit_report.csv`. |
| `mapping_verification.csv` | Permanent, cross-batch record of how each table's item↔text mapping was verified (`route`, `status`, `evidence`). One row per table, ever. Fed by each batch's `verification_merged.csv`. |
| `itemtables/pending_index_notes.csv` | Standing cumulative log of tables that could not be automated, for the index workbook. Columns `table,note,status`; `status` is one of `pending`/`blocked`/`excluded`/`note_only`/`resolved` (see SKILL.md Step 6b). Append across batches; never reset. |
| `itemtables/clean/` | Vetted tables staged for upload. **Only `*__items.csv` may live here** — an uploader walks recursively, and this directory exists because stray `.csv` files were once uploaded as tables. `red_up` now excludes non-`__items` files when the target is `irw_text` and names what it excluded, but keep the directory clean anyway. Ben clears it after uploading. |

Everything except `queue_state.csv` is rederived from disk each round, so a round
that dies partway (API limit, crash) is safely resumable — the next firing sees
what's missing and continues. Tables left `in_progress` by a dead round need
manual reconciliation back to `pending`.

## Standing exclusions — do NOT extract these

**`enem*` (52 tables): item text is being handled separately by Ben. Do not extract it.**
Recorded 2026-08-18. All 52 rows are marked `status=excluded` in `queue_state.csv` so no round can
claim them; do not flip them back to `pending`, and do not extract an `enem*` table even if asked to
process "everything remaining". They are the Brazilian national exam (ENEM) tables and they dominate
the corpus by volume — 2.12 billion of what were 2.44 billion pending responses, i.e. **87% of all
pending response volume** — so any statistic about queue coverage should say whether it includes
them. Post-exclusion the queue is 1,176 pending.

## Running a round

**Nothing schedules a round. You start one, when you are ready to triage what it
produces.** Decision (c) of `extraction_batches/HANDOFF.md`, settled 2026-09-04:

```bash
/home/ben/irw-queue-runner/itemtext/extraction_batches/run_round.sh
```

That script is the only entry point. It checks the guards (branch, clean tree,
circuit breaker, `in_progress` rows, pending count, batch cap), merges
`origin/main`, launches the round agent with `round_prompt_v1.md`, then pushes and
opens or reuses the standing PR. It writes a dated log under
`extraction_batches/cron_logs/` and also prints to your terminal; a failure exits
nonzero and says what to check.

**Why there is no scheduler, and why "add one later" is the wrong turn:**

- **The bottleneck is triage, not the trigger.** Roughly two thirds of the tables
  in a round need a human go/no-go, and at ~1,009 pending and 6 tables a round
  (halved from 12 on 2026-09-05) that is ~168 rounds. Any
  cadence faster than "when someone is ready to triage" just grows an unreviewed
  branch — which is also what makes the pre-round merge of `origin/main` start
  conflicting, and a failed merge stops the queue entirely. One round per triage
  session is the honest rate.
- **A round is a large token spend — quoted in tokens, not dollars.** This is
  subscription usage; nothing in the transcripts records a charge, and the dollar
  figures this bullet used to carry were tokens multiplied by list rates, not an
  invoice. Measured across four complete rounds (2026-09-04, orchestrator + 12
  subagents summed from the jsonl under `~/.claude/projects/`): **570–670K output,
  2.0–2.5M cache write, 42–54M cache read** per round. The cache reads dominate,
  and the **subagents are 85–94% of them** (and 35–40% of the output) — reading the
  orchestrator transcript alone understates a round about tenfold. At ~98 rounds
  the remaining queue is **~4–5 billion cache-read tokens**; an hourly cadence would
  be ~1.2B a day. Nothing should be able to spend that on a timer. The resource a
  fired round actually consumes is rate-limit headroom — which is what killed 8 of
  12 agents in batch_018 and 4 of 12 in batch_019.
- **Crontab is ruled out** as a standing preference across projects (2026-09-04).
  Its failure mode is not misfiring but failing *silently* on a laptop that has to
  be on and in the right state, with nothing reporting on it — the version-manifest
  entry ran zero times and said nothing.
- **GitHub Actions was considered and rejected for this job**, even though the
  version-manifest job moved there (#1905, #1907). Three reasons: the work is
  fetching publisher and repository sources, and a datacenter IP gets bot-walled
  far more than this laptop does — and a WAF block lands in `queue_state.csv` as
  `blocked`, which quietly removes a table from the queue for good; a cloud runner
  is cancelled and evicted more readily, and every death leaves a round's worth of
  rows `in_progress` that block all later rounds until a human reconciles them; and
  `--dangerously-skip-permissions` in a PUBLIC repo, with secrets in the
  environment and public logs, around an agent whose whole job is reading
  untrusted third-party files, is a different risk from the same flag on a machine
  Ben is sitting at. If the GitHub ergonomics are ever wanted, the answer is a
  **self-hosted runner on Ben's laptop** — residential IP, local credentials, local
  `.cache/` — not `ubuntu-latest`.

**Wall clock, for planning:** one agent per table means the round is only as fast as
its slowest table, and hard tables are exactly the slow ones. In batch_016 the
twelve agents ran **3.6 to 16.4 minutes** each and the round took roughly **40
minutes** end to end; batch_019 took 19. Budget 20–40 minutes, and do not start a
second round while one is running — the `in_progress` guard will refuse anyway.

Because each round is a **stateless context** with no memory of prior rounds, the
prompt is a complete, idempotent recipe — not a reference to "continue the batches."
## History

Batches 001–005 ran 2026-08-16 (50 tables extracted, 10 blocked). The loop
stopped at batch_005 when the circuit breaker tripped at 33% blocked — a
coincidental cluster of WAF-blocked and missing-file sources, not a pipeline
fault. Realized yield across those rounds: **50/60 = 83.3%** of tables the
availability audit called AVAILABLE produced a validated CSV.

Batches 006–010 ran 2026-08-17, the first rounds under the consolidated skill
(core model + required Step 5b): **58 of 60 written, 2 blocked (3.3%)**, audits
57 PASS / 3 WARN with every WARN explained and none an itemtext defect.
Verification arrived with the batches rather than by later sweep: 33 VERIFIED,
5 PARTIAL, 5 NO_ROUTE, 17 NOT_NEEDED. The yield jump over 001–005 is mostly the
"open the data file before believing there is no source" rule — several tables
that would previously have been blocked had labels all along.

Six response-data defects were found by extraction and filed as GitHub issues
(#1653, #1655, #1656, #1657 plus additions to #1642 and #1651). That is worth
planning for: **the extraction pass is, in practice, also an audit of the
response data**, because verifying an item mapping means reading the source file
and the processing script side by side.

---

## The round-trigger prompt

**The prompt lives in `extraction_batches/round_prompt_v1.md`, and that file is the
only copy.** `run_round.sh` reads it directly; adjust the batch cap in its Step 0
for the run you want.

A full copy used to be pasted here as well, and it drifted — by 2026-09-04 the copy
in this file still pointed the round at `src/itemtext/` (the wrong checkout, on an
unrelated branch) and still told the agent to cancel itself via
`CronList`/`CronDelete`, which the real prompt explicitly forbids. A round reading
the wrong one gets the wrong protocol and a stale `queue_state.csv`. So: one copy,
and a pointer here.

## Triage and staging (after a round, before upload)

Extraction leaves a batch validated but unshipped. Triage is the per-table go/no-go that
turns `itemtables/batch_NNN/` into an upload. Done for batches 001, 006 and 007; the shape
is the same each time.

0. **If the round hit a rate limit or spend cap, reconcile the batch directory against
   `queue_state.csv` first.** The harness reports an agent's *first* assistant message, not its
   last, so an agent killed on its closing message is indistinguishable from one that died before
   reading anything. In batch_019 two of three "failed" agents had in fact finished, one with a
   complete 65-row `__items.csv` and all four sidecars on disk. `run_round.sh` prints a warning
   when the transcript mentions a limit; when it does, `ls` the batch directory and classify on
   the gates rather than on the report. Orphaned `__items.csv` files with no provenance are
   quarantined, not promoted.
1. **Re-run the gates live** rather than trusting the round's own report —
   `normalize_nulls.R`, `audit_batch.R`, then `verify_batch.R` and `lint_verification.R`
   on the batch. The first two re-check against current live data, so a table that passed at
   extraction time can still surface something; `verify_batch.R` re-runs each table's own
   mapping evidence, and `lint_verification.R` catches a status that claims more than its
   evidence supports.
2. **Re-check the round's substantive claims yourself**, especially any table whose notes
   ask for it, any source override, and any positional mapping. With `verify_<table>.R` in
   place this should mean *reading and running* the script rather than rebuilding the
   analysis — if a script is thin or checks the wrong thing, that is itself the finding. Both triaged rounds turned
   up something this way: batch_006's audit error (a PLOS table that is an image), and
   batch_007's `baaziz_2023_sms2` file inconsistency. Cached sources under `.cache/<table>/`
   usually make this minutes of work, not hours.
3. **Decide per table: stage or hold.** Stage into `itemtables/clean/` — **only
   `*__items.csv` may go there**, since an uploader walks the directory recursively.
   Hold anything whose fate depends on an open decision (batch_006 held
   `APFCompact_Ptacek_2024_DASS-21` pending #1653, a duplicate-table question) and leave it
   in the batch folder. A table needing a *policy* call rather than a check — is this text
   good enough to ship — is the user's to make, not yours: ask, don't hold silently.
4. **Issues page**: draft, then apply directly, per SKILL.md Step 6c. Read the draft file's
   **REVIEW THESE TOO** section — it lists shipped tables that earned no draft, with their
   `notes.csv` text, because the drafter only sees `public_note` and three batch_009 tables
   were missed that way.
5. **Log it** in `round_log.md` under that batch: what was staged, what was held and why,
   which issues-page drafts were dropped, and what the re-checks found.
6. **Merge the standing PR without deleting the branch.** Rounds accumulate into one open PR
   from `itemtext/queue-rounds`; that is the point of it. #1904 was merged with `--delete-branch`,
   which removed `origin/itemtext/queue-rounds` — that broke the runner's push check (the commits
   of the next round would have stayed local, unpushed) and would have started a fresh PR per
   round. Use `gh pr merge --squash` with no `--delete-branch`, and do not press GitHub's
   "Delete branch" button afterwards.
7. **On the user's confirmation that the upload happened**, stamp `uploaded=<date>` in the
   batch's `provenance.csv` and in `mapping_verification.csv`, and delete the uploaded
   `__items.csv` files from the batch folder — sidecars stay, so the folder still documents
   every table the batch claimed. `clean/` is cleared by the user, not by you. **Never stamp
   ahead of confirmation**; a stamp that runs ahead of the actual upload is worse than none.

Both CSVs are CRLF, but **the quoting is not uniform and this line used to claim it was**: `batch_019/provenance.csv` and `mapping_verification.csv` are MINIMAL-quoted, while `batch_018/provenance.csv` is QUOTE_ALL. Do not assume either. Round-trip the file with the convention you intend to use and check the result is **byte-identical** before writing; if it is not, append or edit the target lines in place. Reserialising them with a default `csv.writer`
rewrites the whole file — check that a `QUOTE_ALL` + `\r\n` round-trip is byte-identical
before writing, or edit the target lines in place.

## Repo hygiene when committing a round

`git commit` writes **everything staged**, not just what you added. Background routines in this
repo (the automated_finding cron jobs) stage files of their own, and twice this session an
unrelated `automated_finding/` change was swept into an itemtext commit — once causing a merge
conflict on push. Before committing a round:

```bash
git add itemtext/itemtables/batch_<NNN> itemtext/extraction_batches itemtext/mapping_verification.csv
git diff --cached --name-only          # confirm ONLY what you meant is staged
```

Prefer naming paths over `git add -A`, and check `--cached` before every commit.

## Open items

Live status is in `extraction_batches/round_log.md`; outstanding *decisions* are GitHub issues on
ben-domingue/irw labelled `ITEMS` (#1643–#1652), so they stop drifting out of date in this file.
Response-data defects found by extraction carry the `data fix` label instead (#1642, #1653, #1655,
#1656, #1657).

As of 2026-08-17: queue is **108 done, 12 failed, 1,223 pending**. Batches 001–005 are uploaded
(47 tables) and 006–010 are extracted and verified but **not yet triaged or staged** — that review
is the natural next step, one batch at a time, as was done for 001–005.
