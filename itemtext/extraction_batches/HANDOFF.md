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
| runner | `itemtext/extraction_batches/round_cron.sh`, hourly at `:13` from the user crontab |
| review | a **standing PR** from `itemtext/queue-rounds` → `main`, opened by the runner and left open; rounds accumulate into it |
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

**c. Scheduling of itemtext rounds — crontab is RULED OUT; the runner is paused pending a replacement.**

Sequence matters here, so read it in order rather than assuming the last state:

1. Ruled that morning: crontab + `claude -p`. Built as `extraction_batches/round_cron.sh`,
   shaped after this repo's existing crons — dated log, guards before any work, a GitHub issue
   on failure. It is the **first unattended agent in this repo**; the others run deterministic
   scripts.
2. **It ran, once, and it worked.** batch_019: 19 minutes, exit 0, 7 tables written with
   `audit_batch` 7 PASS / 0 WARN, 4 determinate blocks, 1 failure. Every guard behaved. All 7
   survived a live re-run of the gates at triage; 6 shipped.
3. Ben then **cancelled** it and said a different system is wanted. Two reasons were given: an
   API monthly spend cap, and the cron being too complicated for the value. **The spend cap is
   no longer a reason — Ben is working around it** (stated 2026-09-04). So the remaining
   argument is complexity alone, and it is weaker than when it was made: the round worked, and
   the one real defect found since (the self-edit bug, below) is fixed.

**Current state: paused, not dismantled.**
- `extraction_batches/circuit_breaker.flag` is set as a DELIBERATE PAUSE, not a tripped breaker.
  The file says so itself. Delete it to resume.
- The crontab line `13 * * * * .../round_cron.sh` is **still installed and should be removed** —
  it is one of two IRW crontab entries still to migrate (the other is the weekly metadata
  pipeline, `0 6 * * 1`). The flag is the immediate stop; removing the line is the durable one.
  An agent cannot do it: the permission classifier blocks crontab edits, so that step is Ben's.
  `crontab -e`, delete the line.
- The cap is `batch_020`, so even unpaused it would run one more round and stop.

**Crontab is out, as a standing preference across projects.** Ben ruled on 2026-09-04: "i have
had no luck with crontab across a variety of different projects now." It was earned — the
version-manifest job was installed as a crontab entry on 2026-09-03 and ran **zero** times,
refusing silently because the live checkout was never on `main`. The failure mode is not
misfiring, it is failing *quietly* on a laptop that has to be on and in the right state, with
nothing reporting on it. **Do not propose a crontab here.**

The direction is **GitHub Actions**, which is what #1705 chose for the version manifest (#1905,
#1907; first Actions run `d0a42d7`) — a scheduled workflow plus `workflow_dispatch`, opening an
auto-merged PR because `GITHUB_TOKEN` does not inherit Ben's `enforce_admins: false` bypass on
`main`. Local systemd timers are weaker: `Linger=no`, so they only fire while he is logged in.

**This job is not a straight lift, which is why it is still open.** The manifest job only reads a
remote API and commits a file. A round needs Redivis credentials, the R and Python toolchain,
~19 minutes, and 12 parallel `claude` subagents. Whether that fits an Actions runner — and what
it costs there — is the thing to work out.

**What the round cannot do, under any scheduler:** publish. It writes `__items.csv` into a batch
directory and stops. Triage, staging into `clean/` and upload are all manual. That property is
what bounded the risk of running it unattended, and it is the thing to preserve in whatever
replaces it.

**The self-edit bug, fixed — do not reintroduce it.** `round_cron.sh` merges `origin/main` into
the worktree it lives in, so a merge carrying a change to the script rewrites the file bash is
executing. git rewrites in place keeping the inode, and bash reads scripts lazily in 8KB blocks
by byte offset, so this really does corrupt — reproduced as `unexpected EOF while looking for
matching quote`. It bit once, harmlessly, on 2026-09-04. The fix is a snapshot re-exec at the top
of the script. Any replacement that both self-updates and runs from the updated file needs the
same guard.

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

1. Settle (c) above — REOPENED. The crontab line is installed but the queue is paused by
   `circuit_breaker.flag`; delete the flag to resume as-is, or replace the scheduler first.
2. ~~Raise the cap~~ **done 2026-09-04: the cap is now `batch_020` in Step 0 of both
   `BATCH_PROCESS.md` and `round_prompt_v1.md`, which allows two more rounds (019, 020).** Re-raise
   it before any run beyond that. The off-by-one: the cap self-cancels after *completing* that batch.
3. ~~Confirm~~ **checked 2026-09-04: no `circuit_breaker.flag`, 0 `in_progress` rows, no `clean/`.**
4. Install the crontab line in (c) above — `round_cron.sh` reads `round_prompt_v1.md` itself.
   Hourly at `:13`; the old 15-minute cadence was calibrated for a retired groups-of-3 dispatch
   and caused an overlap.
