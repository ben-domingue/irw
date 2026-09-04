# ITEMTEXT_BATCH_ROUND_V1 (self-identification marker for CronList/CronDelete — do not remove this line)

You are firing as a recurring cron round of the IRW item-text batch-extraction pipeline. This is a
stateless firing — you have no memory of prior rounds. Everything you need is either in this prompt
or on disk. Follow this protocol exactly, once, then stop (do not loop internally).

Working directory: /home/ben/irw-wt/1709/itemtext/ — cd there first. Read
itemtext/BATCH_PROCESS.md if you need context beyond this prompt.

## Step 0 — Stop conditions (check BEFORE any extraction work)

Run: ls -d itemtables/batch_* 2>/dev/null | sort -V

Stop, self-cancel, and log if ANY of these hold:
- itemtables/batch_031 already exists (round cap reached)
- zero rows with status=="pending" in extraction_batches/queue_state.csv (queue exhausted)
- extraction_batches/circuit_breaker.flag exists (a prior round tripped it; human review pending)

SEPARATELY — the in-flight check, which is NOT a self-cancel (added 2026-09-03):

Run: awk -F, 'NR>1 && $2=="in_progress"' extraction_batches/queue_state.csv

If that prints ANY row, a round is already running (or died mid-round). **Stop
immediately. Do NOT claim tables, do NOT create a batch directory, and do NOT
self-cancel the cron job** — a live round will finish on its own and the next firing
should proceed normally. Append one line to extraction_batches/round_log.md saying
you stood down, which batch the in_progress rows belong to, and their timestamp.
Then stop.

The one exception: if those rows' timestamp is more than 2 hours old, the round that
claimed them is almost certainly dead. Say so in that log line and stop anyway —
reconciling them back to "pending" is a HUMAN decision, because a dead round may have
left half-written files in its batch directory. Never flip in_progress back to pending
on your own.

Why this exists: on 2026-09-03 a second round fired while batch_016 was still in
flight. None of the three stop conditions above covered it, and nothing in the
protocol would have prevented two orchestrators from rewriting queue_state.csv and
globbing each other's sidecars. It stood down only because a human was watching.

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

- cd to /home/ben/irw-wt/1709/itemtext/ and read
  .claude/skills/irw-auto-itemtext/SKILL.md in full (plus references/itemtext_standard.md) before
  doing anything, and follow it precisely.
- Process its ONE assigned table via SKILL.md Steps 2-6:
  table_context.R for ground truth (respect a STOP) -> find the source paper (Step 3, including
  Step 3b's instrument-mismatch check) -> extract/structure (Step 4, literal transcript, match the
  source's terseness) -> validate_items.R as a HARD GATE (Step 5), run it with **--table-sets** on
  a published table so the gate uses server-side aggregates instead of exporting the whole table -> Step 5b mapping verification
  (REQUIRED, see below) -> on pass write itemtables/batch_<NNN>/<table>__items.csv (Step 6). On a
  block, write NO CSV and log why. One retry max on transient failures. A partial/honest "couldn't
  automate this one" is a correct outcome per SKILL.md, not a failure.
- **On a block, state the retry test explicitly in notes_<table>.csv and in your report**: would an
  unchanged retry, right now, plausibly produce a different result? Say YES (an unresolved access
  failure -- 403, timeout, quota, source not located, no verdict reached) or NO (a determinate
  verdict -- no wording published, licence bars reuse, images only, gated behind registration or
  author contact, or a data defect that makes item text unattachable), and say what would have to
  change for the answer to become different. The orchestrator uses this at Step 5 to decide
  `failed` vs `blocked`, and those are counted differently by the circuit breaker. Do not guess:
  if you cannot tell, say so and it will be treated as `failed`, which merely costs a retry.
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

**Delete them BY NAME, never with `rm -f verification_*.csv`.** That glob also matches
`verification_merged.csv` -- the file this step just told you to create, and the exact filename
`lint_verification.R` requires inside a batch directory. Running the documented cleanup literally
destroys the merge output: it happened at batch_016's round close and took all nine verification
rows with it. They were recoverable only because each agent still held its evidence string and
could be resumed to rewrite its own file; nothing on disk could have rebuilt them, and an evidence
string reconstructed from memory would be worse than a missing one. Delete the exact filenames you
merged, or write the merge to a name outside the glob and rename it afterwards.
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
Rscript check_provenance.R /home/ben/Dropbox/projects/irw/irw_site/itemtext_issues.qmd

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

- Table wrote a CSV AND audit_batch.R says PASS or WARN -> status="done".
- Otherwise classify it. **Ruled 2026-09-03: a table that produced no CSV is NOT automatically a
  failure.** Use the retry test, which is the whole distinction:

  > *Would an unchanged retry, right now, plausibly produce a different result?*

  - **YES -> status="failed".** A fault or an unresolved access failure: a gate FAIL or ERROR, a
    crash, a verify FAIL or missing VERDICT, a lint ERROR, an HTTP 403/timeout/connection error,
    an exhausted export quota, "couldn't find the source" with no verdict reached. These COUNT
    toward the circuit breaker, because a cluster of them is what a systemic breakage looks like.
  - **NO -> status="blocked".** A determinate verdict: the source publishes no item wording, the
    licence bars reuse, the wording exists only as images, the pool is gated behind a human action
    such as registration or author contact, or a data defect makes item text unattachable at all
    (e.g. a transposed table whose item axis holds respondent IDs). An unchanged retry fails
    identically; changing the outcome needs a HUMAN action or a data change. These do NOT count
    toward the circuit breaker.

  Never leave a table in_progress. When in doubt between the two, choose "failed" — it costs a
  retry, whereas a wrong "blocked" quietly removes a table from the queue forever.

- **Circuit breaker: if >30% of this round's tables ended up `failed` (NOT `blocked`)**: write
  extraction_batches/circuit_breaker.flag explaining what happened, self-cancel exactly as in
  Step 0, log it, and stop.

- Always log BOTH numbers in the round entry — written / blocked / failed — plus the round's
  yield. A high `blocked` rate is a fact about which tables the queue served up, not about
  pipeline health, but it is worth watching: the queue is worked in table order and the head of
  the queue holds the corpus's large closed-source datasets. Every `blocked` table also gets a
  row in itemtables/pending_index_notes.csv saying what would have to change.

  WHY THIS SPLIT EXISTS. The breaker is there to stop a BROKEN pipeline burning rounds
  unattended. Before 2026-09-03 it counted every no-CSV table, so a table the extractor correctly
  DECLINED was indistinguishable from one where the extractor broke. It fired twice on correct
  behaviour -- batch_005 (33%, recorded then as "not a pipeline fault") and batch_016 (33.3%,
  8 clean extractions plus 4 determinate source blocks). SKILL.md calls an honest "couldn't
  automate this one" a correct outcome, and the 110-table blind study found declining-rather-than-
  guessing to be the extractor's validated property; a threshold that halts on it trains future
  rounds toward guessing. But blocks are not simply ignorable either: a network or quota outage
  surfaces as a wave of "couldn't reach the source", which is why unresolved access failures stay
  on the counting side.

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
- If this round completed itemtables/batch_031, self-cancel now and log "cap reached".
- Otherwise end normally; the next firing picks up the next batch.

Never run red_up — uploading is a separate, explicit, human-triggered step.

NOTE ON PATHS (2026-09-03 restart): this round runs from a WORKTREE, not src.
`irw_site` is NOT a sibling of the worktree -- use the absolute path above for
check_provenance.R. Do not `cd` into /home/ben/Dropbox/projects/irw/src and do not
switch branches there; it is checked out on an unrelated branch. Commit round output
on branch itemtext/1709-restart-queue, naming paths explicitly per BATCH_PROCESS.md's
repo-hygiene section, and push after each round.
