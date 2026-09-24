# What actually writes item text, and what each path knows that the other doesn't

Established 2026-09-03 for #1709 (roadmap item 7). Every claim below was checked
against artifacts on disk, not against what a README or a SKILL.md says about
itself. Where I could only establish the doc and not the behaviour, it says so.

---

## Part 1 — The three writers

### A. The batch pipeline — the wiring is still true

`BATCH_PROCESS.md`'s round-trigger prompt does dispatch one agent per table, and
does tell each agent to `cd` to `itemtext/`, read
`.claude/skills/irw-auto-itemtext/SKILL.md` **in full** plus
`references/itemtext_standard.md` before doing anything, and process its one
table via **SKILL.md Steps 2-6**. Verified verbatim; unchanged.

**But the job was inert, and not for the reason on record.** #1709 attributes the
stop to the cron's session ending on 2026-08-18. That is true and not
sufficient: Step 0's stop condition was still `itemtables/batch_011 already
exists`, and batches 011-015 exist. Re-created unchanged, the job would have
self-cancelled on its first fire and the pipeline would have read as dead a
second time. Cap raised to `batch_031`; the restart is running from batch_016.

### B. `automated_finding` Step 3.5 — cites the skill, runs a narrower procedure

**It cites rather than restates — confirmed.** The section "Schema and extraction
rules — do not restate them here" defers the schema to `itemtext_standard.md` and
the extraction *judgment* rules (`instructions` vs `section_prompt`, blank rather
than invented stems, terseness matching, never padding an unlabeled scale point)
to Step 4 of the itemtext skill, explicitly refusing to fork a second copy.

**Its extraction does NOT follow Steps 2-6.** It follows a narrower procedure of
its own. Step by step, against the artifacts:

| skill step | batch path | Step 3.5 | is the difference legitimate? |
|---|---|---|---|
| 2 — `table_context.R` ground truth | required | **not run** | **Yes — and it is better.** Step 3.5 gates against the staged response CSV via `--resp-csv`/`--resp-dir`. `table_context.R` exports the whole table; not needing it is the single biggest quota saving in either path. |
| 3 — find the source paper | required | **not run** | Yes. It already has the deposit and the paper open. |
| 3b — instrument-mismatch check | required | **no equivalent** | Probably — the mismatch it guards against is one introduced by *finding* a paper later. |
| 4 — extract and structure | required | **delegated to the skill by citation** | Yes, by construction. |
| 5 — `validate_items.R` hard gate | required | **run**, with `--resp-csv` | Yes. |
| **5b — mapping verification** | **REQUIRED** | **absent** | **No. This is the gap.** |
| 6 — write output | required | run, to its own directory | Yes. |
| 6c — provenance | required | run, same columns, deliberately diffable | Yes. |
| 6d — normalize and audit | required | run | Yes. |

**The gate chains are not the same chain.** The task framing says Step 3.5 "runs
the same gate chain". It runs three of the six the batch round runs:

| gate | batch round | Step 3.5 |
|---|---|---|
| `normalize_nulls.R` | yes | yes |
| `validate_items.R` | yes (per-table) | yes (`--resp-csv`) |
| `audit_batch.R` | yes | yes (`--resp-dir`) |
| `verify_batch.R` | yes | **no** |
| `lint_verification.R` | yes | **no** |
| `irw-validate` | yes (added 2026-09-02) | **no** |
| `check_provenance.R` | yes (added 2026-09-02) | **no** |

The three it runs are the three that check a table against its **source**. The
four it skips are the ones that check the **mapping's own claim**, the **data
standard**, and the **public disclosure record**.

**Evidence, not inference:**

- `find automated_finding -name "verify_*.R" -o -name "verification*.csv"` → nothing.
- Grepping `automated_finding/.claude/skills/irw-automated-finding/SKILL.md` for
  `verify_batch|lint_verification|verify_template|Step 5b|irw-validate|check_provenance|mapping_verification`
  → **no hits at all.** The verification layer is not mentioned, so this is a
  wiring gap, not a documented exemption someone argued for.
- `itemtext_provenance.csv` holds 30 attempted tables: **25 `data_labels`, 5
  `paper_explicit`**.
- `mapping_verification.csv` — the permanent, cross-batch, "one row per table,
  ever" tracker — holds 140 rows and **not one of Step 3.5's 30 tables.**

**Why the 5 matter.** SKILL.md Step 6c states: *"Anything other than
`data_labels` must have a `mapping_verification.csv` row before it is promoted to
`clean/`."* Step 5b repeats it: *"`data_labels` tables are exempt… **Every other
`mapping_basis` requires this step**"*, and *"write the check as a script…
`verify_<table>.R`… for every table that is not `data_labels`."* The five
`paper_explicit` tables (`wang_2024_speaking_self_efficacy`,
`wang_2024_self_efficacy_sources`, `xue_2025_academic_procrastination`,
`xue_2025_academic_stress`, `xue_2025_coping_style`) shipped with
`uploaded=2026-08-29` and have neither.

In fairness: the rule's *letter* names `clean/`, which is the batch path's staging
directory and one Step 3.5 does not use, so nothing was defied. The rule simply
was never wired to the second path. And `paper_explicit` is close to one of Step
5b's two standing exemptions ("explicit code labels in the paper"), so the
*route* may genuinely have had nothing to add. The **row** is a different matter:
its absence means 30 shipped tables are invisible to the tracker that exists to
answer "how was this table's mapping checked?"

**One correction to the framing.** The cheapness gate no longer fails
translated-substitute sources. That bullet used to end "or a translated
substitute"; since the administered-language columns entered the schema on
2026-09-01 (#1774/#1777) the section says explicitly that **"a non-English
administration is not a reason to skip"** — read literally, the old wording would
have wrongly skipped seven correctly-extracted tables in the PLOS weekly batch
(#1783). Paywalled, positional and image-only still fail it, as described.

### C. The backfill scripts — schema work, not a third extractor. Confirmed.

- **`language_backfill/build_backfill.py`** consumes a translations JSON that is
  *handed to it*; it parses no source, opens no deposit, and reaches no network.
  It writes the administered base fields back **byte for byte as published**
  (normalising to NFC only for the lookup key, because the Serbian `sv-maia2_*`
  tables store decomposed Unicode), fills the parallel `_translated` columns, and
  **refuses to write a half-translated table** if any administered string is
  missing from the mapping. Not an extractor.
- **`language_backfill/round2/add_language.py`** sets `language` from a hardcoded
  17-entry dict, writes the four `_translated` columns, and then **asserts** that
  `item`, `resp`, `item_text`, `option_text`, `instructions`, `section_prompt`,
  `instrument`, `correct_response` and `section_id` are unchanged. It proves its
  own claim in code. Not an extractor.
- **`classify_administered_language.py`** (found alongside) is a *classifier* over
  already-published text, on positive evidence only — non-Latin script, or >3
  non-ASCII letters. Everything else is `NEEDS_REVIEW`; nothing is ever called
  non-English on the absence of English. Not an extractor either.

**The one thing worth naming:** the scripts don't author content, but the
workstream does. `backfill_provenance.csv` records 78 tables, **64
`machine_translation`** and 14 `official_instrument_english` — i.e. English this
project generated, which is exactly what `check_provenance.R` and the #1777
disclosure rule exist to catch. The scripts are plumbing; the translation content
is authored upstream of them and disclosed downstream.

**A small real inconsistency:** `build_backfill.py` writes `''` into an
unrecovered `_translated` field; `add_language.py` writes `'NA'`. Both describe
themselves as leaving the column "present and empty". Harmless if
`normalize_nulls.R` runs over both, worth one line of thought if it doesn't.

---

## Part 2 — What each path knows that the other doesn't

**Step 3 is the one moment when the raw deposit, the source paper and the
item-code derivation are all in hand.** The premise checks out, and the repo makes
the cost of losing it concrete:

- The triage CSV **is** deleted (SKILL.md Step 2: *"delete the local triage CSV —
  it's temporary"*), and `runs/` temp files with it.
- Raw downloads are not persisted: `itemtext/.cache/` is **gitignored**, so the
  batch path's cache is local-only — it does not exist in a fresh worktree, and
  did not exist in mine.
- So a later batch-path agent must re-find the paper from the dictionary DOI and
  reverse-engineer `data/<table>.py`.

**And that reverse-engineering is harder than "read the script", because the
script is not name-addressable.** One processing script routinely writes many
tables: `soderberg_2024_esm_school.py` produces the eight `soderberg_2024_*`
tables, `torok_2025_online_trust.py` the twelve `torok_2025_*`. Of the five Step
3.5 tables I spot-checked, **three had no `data/<table>.py` at all** — the file is
named for the study, not the table. An agent told to "read `data/<table>.py`" for
`soderberg_2024_peer_support` finds nothing and has to go looking.

**The knowledge at stake is the item-code derivation**, and the skill is emphatic
about its value — core model §3, *"the single most useful five minutes in the
whole process"*, classifying the derivation into four patterns. It also warns that
`data_labels` **does not** mean inference-free: *"it describes where the words came
from, not how the code was assigned."* That is precisely why the 10-of-50
positional/script-generated finding matters, and Step 3.5's 25 `data_labels`
tables do not get a free pass on the strength of that basis alone.

**What Step 3.5 persists about it today: a prose sentence.** 13 processing scripts
carry the structured `Item text:` docstring field — 6 `shipped`, 7 `not shipped`
with a reason. They are genuinely informative and the "not shipped" ones do exactly
the job intended (they stop the next pass re-deriving the answer). But they record
**where the text is**, not **how the code was assigned**, and they are free prose in
a docstring — not parseable, not joinable, not gated on. Nothing downstream reads
them.

*(I initially reported this field as absent entirely; my first grep only matched
`#` comments and the field lives in the module docstring. 13 files carry it.)*

**The reverse direction: what Step 3.5 knows that the batch path should copy.**
Gating against a staged CSV with `--resp-csv`/`--resp-dir` instead of live data is
strictly better, and it is the one route that cannot exhaust the export quota. The
batch path can't adopt it wholesale — its tables are already live, so live *is*
the ground truth — but the principle behind `table_sets.R` is the same one, and
Step 3.5 got there first.

---

## Part 3 — Recommended changes to SKILL.md (PROPOSED — not applied)

Not applied mid-run, deliberately: changing the extraction procedure while a batch
is in flight makes that batch uninterpretable. Ben rules.

### Recommendation 1 — persist the item-code mapping as a durable artifact. **Yes.**

Add to `irw-automated-finding` SKILL.md Step 3.5, as a required output alongside
`itemtext_provenance.csv`:

> **Record how the item codes were assigned, in `automated_finding/itemcode_map/<table>.json`.**
> You wrote `data/<table>.py`, so you know this outright — a later pass has to
> reconstruct it from a deleted deposit and a script that may not carry the
> table's name. Record the derivation pattern from core model §3
> (`source_column_name` / `number_preserving_rename` / `positional` /
> `script_generated`), the script that produced the table, and — when the pattern
> is `positional` or `script_generated` — **the ordered code→source-column list**,
> which is the artifact that cannot be rebuilt once the raw file is gone.
> Write it whether or not item text shipped. A skipped table is the case where
> this is worth most.

Rationale: it converts the one-sentence TODO bullet into something the batch path
can consume; it is near-free at Step 3 and expensive-to-impossible later; and it
targets exactly the class that produced **every mapping defect found in review**.
Making it a file rather than prose also lets a future `verify_<table>.R` cite it
and `lint_verification.R` check it. The natural companion is a note in
`irw-auto-itemtext` SKILL.md Step 5b: if an `itemcode_map/` entry exists, it
settles the derivation and the statistical routes are unnecessary.

Scope caveat: this pays off only if something later reads it. Recommended with
that string attached — if it is not wired into the batch path's Step 2, it becomes
another artifact nobody consumes.

### Recommendation 2 — close the verification gap. **Yes, and it is the more urgent of the two.**

Step 3.5 should, for **every table whose `mapping_basis` is not `data_labels`**:

1. write a `mapping_verification.csv` row (`VERIFIED`/`PARTIAL`/`NO_ROUTE`/`NOT_NEEDED`)
   — so the permanent tracker stops having a hole where a whole pipeline should be;
2. write `verify_<table>.R` from `references/verify_template.R`, and run
   `lint_verification.R` over the result;
3. run `irw-validate` and `check_provenance.R` — both were added to the batch flow
   on 2026-09-02 *because of defects found in already-published tables*
   (`dup_item_resp`, `resp_ambiguous`, #1816/#1827), and both are cheap.

For a `data_labels` table a `NOT_NEEDED` row is enough, matching the batch path.
Even that is an improvement: it would put all 30 tables in the tracker.

### Recommendation 3 — make the `Item text:` header field parseable. **Minor.**

It is doing real work and 13 scripts carry it. Fix the format (`Item text:
shipped|not_shipped|partial — <reason>`) so a sweep can count it instead of
grepping prose. Low priority next to 1 and 2.

---

## Part 4 — What remains UNKNOWN

Stated as unknown rather than reasoned past.

1. **Whether Step 3.5's extraction *judgment* actually follows SKILL.md Step 4.** I
   established that it *cites* it and that its outputs passed the three gates it
   runs. I did not compare shipped rows against sources for any of the 30 tables.
   Citation is not compliance, and no gate in its chain tests Step 4's judgment
   rules.
2. **Whether the 5 `paper_explicit` mappings are correct.** They lack the evidence
   artifact by which the question would be answered. Unverified is not wrong — the
   point is that nothing on disk can currently tell you which.
3. **Whether the 25 `data_labels` tables are inference-free at the code level.**
   Core model §3 says the basis does not settle it. Their scripts may make it
   obvious; I did not read all 13.
4. **The skip side of the cheapness gate.** #1770's 24 skipped tables
   (8 `estevez_2021_*`, 16 `chen_2024_*`) rest on a claim about `.sav` labels that
   was never independently checked — and the SKILL.md now documents that this exact
   failure already happened once, a verdict written from the variable-label level
   alone while value labels were present for all 82 items. Out of scope here, and
   still open.
5. **Whether an `itemcode_map/` artifact would have caught the defects.** The
   10-of-50 finding says the defects were in positional/script-generated tables. It
   does not follow that recording the derivation would have prevented them, and I
   did not test the counterfactual against the specific defects.
6. **Anything about the batch path's *current* yield.** The ~92% figure is from
   batches 001-011. Batch_016 onward is running now; nothing in this document rests
   on its results.
7. **The provenance of the backfill's 64 machine translations** — which engine, and
   with what review. `backfill_provenance.csv` records *that* they are machine
   translations, and the disclosure rule is satisfied; I did not establish how they
   were produced.
