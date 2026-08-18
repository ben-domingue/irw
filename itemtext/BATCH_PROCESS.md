# Item-text batch extraction — round protocol

How the `itemtables/batch_NNN/` extraction runs work, and the exact prompt to
restart them. Companion to `.claude/skills/irw-auto-itemtext/SKILL.md` (which
covers per-table extraction) — this file covers the batching/scheduling layer.

## State on disk

| Path | What it is |
|---|---|
| `extraction_batches/queue_state.csv` | `table,status,batch,timestamp`; status is `pending`/`in_progress`/`done`/`failed`. Seeded from the AVAILABLE rows of `availability_audit_full.csv`. **The only state that must persist between rounds.** |
| `extraction_batches/round_log.md` | One entry per round: counts, notable findings, open items. |
| `extraction_batches/circuit_breaker.flag` | Present = a round failed >30% and the loop stopped for human review. Delete it to resume. |
| `itemtables/batch_NNN/` | `{table}__items.csv` (validated output), `notes.csv`, `provenance.csv`, `audit_report.csv`. |
| `itemtables/clean/` | Vetted tables staged for upload. **Only `*__items.csv` may live here** — its `upload_text.py` walks recursively and treats every `.csv` as a table. Ben clears it after uploading. |

Everything except `queue_state.csv` is rederived from disk each round, so a round
that dies partway (API limit, crash) is safely resumable — the next firing sees
what's missing and continues. Tables left `in_progress` by a dead round need
manual reconciliation back to `pending`.

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
  is nearly empty — don't stall).
- Immediately rewrite queue_state.csv marking exactly those tables status="in_progress",
  batch="batch_<NNN>", timestamp=<now ISO 8601>, BEFORE dispatching, so nothing is double-claimed.

## Step 2 — Dispatch extraction (parallel subagents)

Split into groups of 3. Dispatch one Agent call per group (subagent_type "general-purpose"), all
in the same message so they run in parallel. Each subagent prompt must tell it to:

- cd to /home/ben/Dropbox/projects/irw/src/itemtext/ and read
  .claude/skills/irw-auto-itemtext/SKILL.md in full (plus references/itemtext_standard.md) before
  doing anything, and follow it precisely.
- Process its 3 assigned tables ONE AT A TIME via SKILL.md Steps 2-6:
  table_context.R for ground truth (respect a STOP) -> find the source paper (Step 3, including
  Step 3b's instrument-mismatch check) -> extract/structure (Step 4, literal transcript, match the
  source's terseness) -> validate_items.R as a HARD GATE (Step 5) -> Step 5b mapping verification
  (REQUIRED, see below) -> on pass write itemtables/batch_<NNN>/<table>__items.csv (Step 6). On a
  block, write NO CSV and log why. One retry max on transient failures. A partial/honest "couldn't
  automate this one" is a correct outcome per SKILL.md, not a failure.
- Do SKILL.md Step 5b for every table whose mapping_basis is not `data_labels`, and append its row
  to itemtext/mapping_verification.csv (table,batch,mapping_basis,uploaded,route,status,evidence).
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
- Write itemtables/batch_<NNN>/notes_group<K>.csv (header table,note) with a row for every table
  that didn't get a clean pass, including passes carrying a real caveat.
- Write itemtables/batch_<NNN>/provenance_group<K>.csv (header
  table,mapping_basis,text_source,source_ref,note,public_note,uploaded) with a row for EVERY table,
  clean or not. Vocabularies are defined in SKILL.md Step 6c. Record mapping_basis=unknown honestly
  rather than guessing.
- NOT touch itemtables/pilot/pending_index_notes.csv (a separate, older file).

Wait for all groups to finish.

## Step 3 — Merge sidecars

Merge notes_group*.csv into notes.csv and provenance_group*.csv into provenance.csv (header once,
data rows concatenated), then delete the per-group files.

## Step 4 — Normalize and audit

Rscript .claude/skills/irw-auto-itemtext/scripts/normalize_nulls.R itemtables/batch_<NNN>
Rscript .claude/skills/irw-auto-itemtext/scripts/audit_batch.R    itemtables/batch_<NNN>

## Step 5 — Update queue state and check the circuit breaker

- Table wrote a CSV AND audit_batch.R says PASS or WARN -> status="done". No CSV, or FAIL/ERROR ->
  status="failed". Never leave a table in_progress.
- If >30% of this round's tables ended up failed: write extraction_batches/circuit_breaker.flag
  explaining what happened, self-cancel exactly as in Step 0, log it, and stop.

## Step 6 — Log, then re-check the cap

- Append an entry to extraction_batches/round_log.md: batch id, timestamp, table count,
  pass/fail counts, and anything notable (systemic access issues, Step 3b instrument mismatches,
  dictionary/metadata problems found).
- If this round completed itemtables/batch_011, self-cancel now and log "cap reached".
- Otherwise end normally; the next firing picks up the next batch.

Never run upload.py or clean/upload_text.py — uploading is a separate, explicit, human-triggered step.
```

## Open items

See the tail of `extraction_batches/round_log.md` — kept there so the
list stays next to the run history rather than drifting out of date here.
