# Item-text batch extraction — round protocol

How the `itemtables/batch_NNN/` extraction runs work, and the exact prompt to
restart them. Companion to `.claude/skills/irw-auto-itemtext/SKILL.md` (which
covers per-table extraction) — this file covers the batching/scheduling layer.

## State on disk

| Path | What it is |
|---|---|
| `extraction_batches/queue_state.csv` | `table,status,batch,timestamp`; status is `pending`/`in_progress`/`done`/`failed`/`excluded`. Seeded from the AVAILABLE rows of `availability_audit_full.csv`. **The only state that must persist between rounds.** `excluded` means do not extract, ever — see the standing exclusions below. |
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

## Scheduling

Rounds are driven by a **session-scoped `CronCreate` job** (`recurring: true`),
the same pattern the availability audit used. Two consequences worth knowing:

- The job lives only in the Claude session that created it and **dies when that
  session closes**. Restarting means recreating it with the prompt below.
- A cron job cannot cancel itself implicitly — the protocol has the agent call
  `CronList` → `CronDelete` on its own marker string when a stop condition hits.

Cadence used: `7,22,37,52 * * * *` (every 15 min). A 12-table round takes well
under 10 minutes wall-clock with 4-way parallelism, so 15 minutes leaves headroom
without rounds overlapping.

Because each firing is a **stateless context** with no memory of prior rounds,
the prompt must be a complete, idempotent recipe — not a reference to "continue
the batches."

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

Paste verbatim into `CronCreate` (`recurring: true`, cron `7,22,37,52 * * * *`).
Adjust the batch cap in Step 0 for the run you want.

```
# ITEMTEXT_BATCH_ROUND_V1 (self-identification marker for CronList/CronDelete — do not remove this line)

You are firing as a recurring cron round of the IRW item-text batch-extraction pipeline. This is a
stateless firing — you have no memory of prior rounds. Everything you need is either in this prompt
or on disk. Follow this protocol exactly, once, then stop (do not loop internally).

Working directory: /home/ben/Dropbox/projects/irw/src/itemtext/ — cd there first. Read
itemtext/BATCH_PROCESS.md if you need context beyond this prompt.

## Step 0 — Stop conditions (check BEFORE any extraction work)

Run: ls -d itemtables/batch_* 2>/dev/null | sort -V

Stop, self-cancel, and log if ANY of these hold:
- itemtables/batch_011 already exists (round cap reached)
- zero rows with status=="pending" in extraction_batches/queue_state.csv (queue exhausted)
- extraction_batches/circuit_breaker.flag exists (a prior round tripped it; human review pending)

To self-cancel: call CronList, find the job whose prompt contains "ITEMTEXT_BATCH_ROUND_V1", call
CronDelete on its id, append one line to extraction_batches/round_log.md saying which stop
condition fired and when, then stop. Do nothing else.

## Step 1 — Claim this round's tables

- Next batch number = highest existing itemtables/batch_NNN + 1, zero-padded to 3 digits.
  mkdir -p itemtables/batch_<NNN>
- Take the first 12 rows with status=="pending" from queue_state.csv (fewer is fine if the queue
  is nearly empty — don't stall). ONLY status=="pending" rows are eligible: rows marked
  "excluded" are off-limits permanently (currently the 52 enem* tables, whose item text Ben is
  handling separately). Never re-mark an excluded row as pending.
- Immediately rewrite queue_state.csv marking exactly those tables status="in_progress",
  batch="batch_<NNN>", timestamp=<now ISO 8601>, BEFORE dispatching, so nothing is double-claimed.

## Step 2 — Dispatch extraction (parallel subagents)

**Dispatch ONE AGENT PER TABLE** (subagent_type "general-purpose"), all in the same message so
they run in parallel. Twelve agents sits under the concurrency cap, so this costs no wall clock.

This replaces the earlier groups-of-3, which lost three tables to every single failure:
batch_010's group 3 was killed by a content-filter error before it read anything, and all three
tables passed on individual retry — the trip was spurious, not about the data. One table per agent
makes the blast radius of an infrastructure failure exactly one table, and a retry is a re-dispatch
of that one prompt.

Give each agent a distinct sidecar suffix (`notes_<table>.csv`, `provenance_<table>.csv`,
`verification_<table>.csv`) so they cannot collide, and glob for those suffixes at merge time.

**Tell each agent to namespace its SCRATCH files too, under `itemtext/.cache/<table>/`.** The
session scratchpad is shared across parallel agents: in batch_011 two agents independently reported
that a sibling overwrote their `cand.csv` mid-run, and one spent a retry chasing the spurious
validation failure that caused. Both caught it — but a collision on a candidate CSV is exactly the
failure that could ship one table's rows under another table's name, and neither `validate_items.R`
nor `audit_batch.R` would notice, because each only compares the file in front of it against the
live data that file claims to describe.

**The ground-truth step is the expensive one — treat it that way.** Every `table_context.R` and
`irw_fetch` call EXPORTS THE WHOLE TABLE. In batch_011 twelve agents pointed at the corpus's largest
tables exhausted a 200GB/30-day Redivis export quota account-wide (see round_log 2026-08-18). Prefer
`irw::irw_table_sets()` — or `scripts/table_sets.R`, now a thin CLI wrapper over it: it answers the
same item/resp-set question with server-side aggregate queries and is not subject to the export
limit. `audit_batch.R` uses the same route.

That quota window has since rolled over and exports work again, but the arithmetic that made
exhaustion inevitable has not changed: the core warehouse is 181.8GB against a 200GB/30-day cap, so
one full pass spends ~91% of a month's allowance. The durable fix is an export billing project on
the datapages datasets, which is still outstanding. Until then, treat the query route as the default
and an export as a decision.

The misreporting half of that incident IS fixed. Rpkg#121 landed (irw >= 1.0.1): an export-quota
failure used to surface as "table does not exist in IRW", which sent four agents chasing a phantom
missing table, and `irw_fetch()` now names an account-wide export limit as such. **"does not exist
in IRW" can again be taken at face value** — it means all four core datasources genuinely returned
not-found.

When several tables in a round come from ONE source file (common — five `butt_2022_*`, five
`buzgova_2023_*`, four `baka2023_*` in recent rounds), tell each agent explicitly which sibling
tables belong to another agent and must not be touched. Two agents independently deriving the same
convention from the same file is useful corroboration; two agents writing the same files is a race.
Each subagent prompt must tell it to:

- cd to /home/ben/Dropbox/projects/irw/src/itemtext/ and read
  .claude/skills/irw-auto-itemtext/SKILL.md in full (plus references/itemtext_standard.md) before
  doing anything, and follow it precisely.
- Process its ONE assigned table via SKILL.md Steps 2-6:
  table_context.R for ground truth (respect a STOP) -> find the source paper (Step 3, including
  Step 3b's instrument-mismatch check) -> extract/structure (Step 4, literal transcript, match the
  source's terseness) -> validate_items.R as a HARD GATE (Step 5) -> Step 5b mapping verification
  (REQUIRED, see below) -> on pass write itemtables/batch_<NNN>/<table>__items.csv (Step 6). On a
  block, write NO CSV and log why. One retry max on transient failures. A partial/honest "couldn't
  automate this one" is a correct outcome per SKILL.md, not a failure.
- Do SKILL.md Step 5b for every table whose mapping_basis is not `data_labels`, and record it in
  the per-table verification sidecar below. Do NOT write to itemtext/mapping_verification.csv
  directly — concurrent agents would clobber each other; the orchestrator merges the sidecars.
  validate_items.R and audit_batch.R only compare SETS -- they cannot catch item_text mapped to the
  wrong item code, which is the one error that silently ships wrong content. Step 5b lists eight
  routes (per-item statistics, response-range fingerprint, implied parameter, subscale blocks,
  keying polarity, marker item, subscale totals, semantic coherence) plus two exemptions
  (self-describing codes, explicit code labels in the paper) and the two scripts item_stats.R and
  mapping_structure.R. status=NO_ROUTE is a legitimate, expected outcome -- record it rather than
  leaving a table looking checked.
- Prefer sources that carry embedded labels — .sav/.xlsx/Forms exports very often tie each item
  code to its text directly, which makes the mapping authoritative instead of inferred. Useful
  access tricks: Europe PMC's supplementaryFiles zip endpoint when PMC/publisher links are
  bot-walled; python-docx table parsing (LibreOffice silently drops Word table cells);
  Rd_db() for CRAN packages; soffice --convert-to txt for legacy .doc.
- NEVER pad an unlabeled scale point with its own number — leave option_text blank.
- Write itemtables/batch_<NNN>/notes_<table>.csv (header table,note) if its table didn't get a
  clean pass, including a pass carrying a real caveat.
- Write itemtables/batch_<NNN>/provenance_<table>.csv (header
  table,mapping_basis,text_source,source_ref,note,public_note,uploaded) with a row for its table,
  clean or not. Vocabularies are defined in SKILL.md Step 6c. Record mapping_basis=unknown honestly
  rather than guessing.
- Write itemtables/batch_<NNN>/verification_<table>.csv (header
  table,batch,mapping_basis,uploaded,route,status,evidence) for every table whose mapping_basis is
  NOT data_labels, per SKILL.md Step 5b. status is VERIFIED/PARTIAL/NO_ROUTE, and `evidence` must
  contain the actual numbers compared, not a description of intent. This sidecar is why
  verification now arrives WITH the batch instead of being reconstructed weeks later by a sweep.
  **VERIFIED means the route distinguishes every item from every other item.** Pinning a polarity
  class, a subscale or some positions is PARTIAL. State in the evidence what the route does NOT
  establish, then choose the status to match that sentence.
- **Also write itemtables/batch_<NNN>/verify_<table>.R — a re-runnable version of that evidence.**
  Copy .claude/skills/irw-auto-itemtext/references/verify_template.R. It must fetch its own data,
  print the numbers it compares, and end with exactly "VERDICT: PASS" or "VERDICT: FAIL". Verify the
  MAPPING, not the plumbing: re-checking item counts is not evidence, because validate_items.R
  already did it and the result merely looks like evidence. Skip only for data_labels tables, where
  the source file itself ties code to text.
- NOT touch itemtables/pilot/pending_index_notes.csv (a separate, older file).

Wait for all agents to finish.

## Step 3 — Merge sidecars

Merge notes_*.csv into notes.csv, provenance_*.csv into provenance.csv, and verification_*.csv
into verification_merged.csv (header once, data rows concatenated), then delete the per-table files.
Leave the verify_<table>.R scripts in place — they are the batch's re-runnable evidence and triage
executes them.

Then merge verification_merged.csv into the permanent `itemtext/mapping_verification.csv`, and add a
NOT_NEEDED row for every written table that has no verification row because its mapping_basis is
data_labels. Every written table must end up with exactly one tracker row.

## Step 4 — Normalize and audit

Rscript .claude/skills/irw-auto-itemtext/scripts/normalize_nulls.R    itemtables/batch_<NNN>
Rscript .claude/skills/irw-auto-itemtext/scripts/audit_batch.R        itemtables/batch_<NNN>
Rscript .claude/skills/irw-auto-itemtext/scripts/verify_batch.R       itemtables/batch_<NNN>
Rscript .claude/skills/irw-auto-itemtext/scripts/lint_verification.R  itemtables/batch_<NNN>

# Added 2026-09-02. The four gates above check a table against its SOURCE -- do the
# item and resp sets match, does the mapping reproduce. These two check it against
# the STANDARD and against the corpus, which nothing in this batch flow did.
irw-validate itemtables/batch_<NNN>/*__items.csv
Rscript check_provenance.R ../../irw_site/itemtext_issues.qmd

A verify FAIL or NO VERDICT, or a lint ERROR, means a table's own claim did not reproduce: mark that
table failed rather than done, and say so in the round_log entry.

An `irw-validate` ERROR means the table breaks the data standard regardless of how well
its mapping reproduces. Two of its checks exist because of defects found in already-published
tables on 2026-09-02:

- `dup_item_resp` — the same `item`+`resp` twice with identical option text. That is a
  doubled upload; four live tables carried it (#1816), one of them serving every item twice
  for a day.
- `resp_ambiguous` — one `resp` value carrying two different option labels, i.e. two
  opposite scale directions merged into one table. `afps_vangsness_2019` says a response of
  1 means both "Strongly agree" and "Strongly disagree" (#1827). Note that per-item
  direction differences are legitimate and are NOT flagged — `aip_vangsness_2019` has four
  reverse-worded items labelled the other way round and passes, correctly.

`check_provenance.R` fails on a `translation_source` value outside
`itemtext/provenance_vocab.csv`, and reports any `machine_translation` table with no entry
on the public issues page. A table shipping English this project generated is disclosed —
ratified 2026-09-02, after 60 such tables were found with no public note at all (#1777).

## Step 5 — Update queue state and check the circuit breaker

- Table wrote a CSV AND audit_batch.R says PASS or WARN -> status="done". No CSV, or FAIL/ERROR ->
  status="failed". Never leave a table in_progress.
- If >30% of this round's tables ended up failed: write extraction_batches/circuit_breaker.flag
  explaining what happened, self-cancel exactly as in Step 0, log it, and stop.

## Step 5b — Verify the round's own claims before trusting them

The subagents are careful but not infallible, and their reports are the only thing the orchestrator
sees. **Independently re-check any claim that (a) overrides a source, (b) reports a defect in the
response data, or (c) is about to be filed publicly or written into a note.** This is cheap — one
`irw_fetch` and a few lines of R — and in practice it has changed the answer:

- An agent reported that all nine items of `anh_2026_finbehavior` have a mean of *exactly* 3.000.
  They run 2.980–3.016. Still notable, but the note as written would have been false.
- An agent overrode a `.sav`'s value labels on `baka2023_bpnsf`. Re-checking confirmed it — and
  showed the correlation evidence alone was ambiguous until item content fixed which block was
  which, so the note had to say that too.
- I filed issue #1654 concluding a file's column names were right and its labels scrambled. The
  next round's agent showed the opposite, with item means at floor/ceiling settling it. The issue
  had to be corrected and closed.

Rule of thumb: an agent's *finding* is a lead; the orchestrator's job is to confirm it before it
becomes a public artifact. Where the check confirms, say so and record the numbers.

## Step 5c — Explain every audit WARN in notes.csv

`audit_batch.R` WARNs are frequently correct-but-expected (blank `item_text` on a forced-choice
instrument, applicability-driven missingness on a matrix item, an item nobody used every level of).
Leaving them unexplained means the next reviewer re-derives the explanation. Append the reason to
that table's `notes.csv` row, and say plainly whether it is an itemtext defect or a property of the
response data — several WARNs this session pointed at data defects worth their own GitHub issue.

## Step 6 — Log, then re-check the cap

- Append an entry to extraction_batches/round_log.md: batch id, timestamp, table count,
  pass/fail counts, and anything notable (systemic access issues, Step 3b instrument mismatches,
  dictionary/metadata problems found).
- If this round completed itemtables/batch_011, self-cancel now and log "cap reached".
- Otherwise end normally; the next firing picks up the next batch.

Never run red_up — uploading is a separate, explicit, human-triggered step.
```

## Triage and staging (after a round, before upload)

Extraction leaves a batch validated but unshipped. Triage is the per-table go/no-go that
turns `itemtables/batch_NNN/` into an upload. Done for batches 001, 006 and 007; the shape
is the same each time.

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
6. **On the user's confirmation that the upload happened**, stamp `uploaded=<date>` in the
   batch's `provenance.csv` and in `mapping_verification.csv`, and delete the uploaded
   `__items.csv` files from the batch folder — sidecars stay, so the folder still documents
   every table the batch claimed. `clean/` is cleared by the user, not by you. **Never stamp
   ahead of confirmation**; a stamp that runs ahead of the actual upload is worse than none.

Both CSVs are CRLF with every field quoted. Reserialising them with a default `csv.writer`
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
