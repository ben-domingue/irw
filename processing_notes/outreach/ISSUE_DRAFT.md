# Systematic permissions outreach: turn one-off emails into a tracked programme

Today IRW emails rights-holders ad hoc, one candidate at a time, whenever a
batch happens to trip over a block. That loses on three counts: the same
instrument gets rediscovered round after round, nothing records a *no* so we
re-ask, and the highest-value asks never get made because nobody ranks them.

This issue proposes running it as a programme: identify every case where an
email would help, draft per-class language, send in batches, and record every
response in a tracked file.

## Scope: three distinct classes, three different asks

These need separate templates — they ask for different things from different
people, and conflating them is why one template has never been enough.

### Class A — instrument wording rights (NEW; the big one)

`itemtext/instrument_rights_register.csv` has **107 entries: 71 `block`,
1 `escalate`, 7 `ship_with_note`, 27 `ship`.** Only 10 of the 107 rest on
silence; **97 carry a quotable clause**, so this is a field that has decided,
not one that forgot. The ask is narrow and worth stating plainly in the email:
*may IRW redistribute the item wording alongside response data, under CC BY,
with attribution* — not a licence to the instrument, not commercial use.

The blocked set is not homogeneous and must be triaged before drafting:

- **Commercial licensors** (Mind Garden, MHS, Hogrefe, PAR, Deakin/HLQ,
  Morisky/MMAS-8, CD-RISC). Redistribution *is* the product. Expect no; a
  recorded no is still worth having, and some offer research carve-outs.
- **Controlled distributors** (PROMIS/HealthMeasures, WHO, IEA/TIMSS/PIRLS).
  They restrict to control versioning and translation quality, not revenue.
  A structured ask that promises version-pinning and no derivative
  translations is plausibly winnable.
- **Single academic authors** who reserved rights or never opened them. The
  most winnable tier, and the one where a short personal email from a named
  professor has a real chance.

**A first-pass regex put ~26 in the academic tier, but it is wrong** — it
misclassified CD-RISC, MMAS-8 and PID-5, all of which are commercial. The
triage is a human/manual pass, not a heuristic, and is step 1 below.

### Class B — data licensing (EXISTING; template already in use)

`automated_finding/license_blocked_candidates.csv` holds **28 standing rows** —
structurally strong deposits with no verifiable open licence. This is exactly
what the file was built for and what `processing_notes/Licensing.txt` already
covers. What is missing is not language but **cadence and recording**: rows
accumulate and get emailed erratically. Note the existing template's OSF
paragraph needs swapping per host (Zenodo, figshare, Dataverse, Mendeley).

Adjacent, same template: **17 OSF candidates blocked only on a missing
licence** (TODO, 2026-08-29) and the standing ANES 2016 ask (sent
2026-08-29, no reply — this programme should own the follow-up).

### Class C — data clarification (no template exists)

Not permission; we need a fact only the authors hold. Each unblocks specific,
already-identified data:

- **Roy 2024** (`10.1371/journal.pone.0315687`) — the PSS-4 block cannot be
  reconciled with the analysed score (`pss_sc` = sum(`pss*_new`) for 99.9% of
  rows, sum(`pss1..4`) for 5.6%, and neither identity nor reversal relates the
  two blocks above chance). Also its ISI block is 100% empty in the deposit.
- **Enders 2022** (`10.1371/journal.pone.0276082`) — an undocumented second
  PSS-4 administration; if it is a retest, that is a free second wave on 2,054
  respondents.
- **Sánchez 2020** (`10.1371/journal.pone.0236940`) — what do the `PS*` codes
  0/1/2 mean? Decides 1,174 responses.
- **`zenodo.16310936`** — the posted values are partially imputed; the raw file
  would be worth ~590k responses.
- **Two anonymous-author deposits** (`zenodo.20475015`, `10.7910/DVN/YCXDBI`) —
  clean data, no name for `authorname_year_construct`.

### Class D — disclosure, not a request

**`zenodo.10069489` publishes 3,130 real personal email addresses** in a public
CC BY deposit. The depositors should be told regardless of whether IRW ever
uses it. This is a notification and should not wait on the programme.

## Prioritise by tables unlocked, not by ease

`itemtext/sweep_instrument_rights.py` already reports, per blocked instrument,
the tables it reaches on both surfaces (item text *and* item codes in response
tables). **Run it to get a tables-gated count per instrument and rank the Class
A queue by it.** An instrument gating twenty live tables earns an email; one
gating a single table can wait. Its own docstring is explicit that a hit is a
lead and a miss is a lower bound, so the counts are for ranking only.

Relevant scale: `check_provenance.R` currently reports **336 held tables** —
extracted, gated, never shipped. Rights is not the only reason, but it is a
large one, and that number is the prize.

## Recording: one tracked file, every outcome, including silence

New `processing_notes/outreach/outreach_log.csv`, standing and cumulative (same
class as `license_blocked_candidates.csv` — never deleted):

```
date_sent,class,target,instrument_or_table,recipient_role,doi,url,
template_used,followed_up,date_response,outcome,terms,notes
```

- `class` — A/B/C/D.
- `recipient_role` — never a personal name or address in the tracked file;
  "corresponding author", "licensing office", "depositor".
- `outcome` — `granted` / `granted_with_terms` / `refused` / `no_response` /
  `bounced` / `redirected`.
- **A `refused` and a `no_response` are both results and both get recorded.**
  Not recording them is why the same instrument gets re-asked.

On a grant, the answer flows to the record that already governs the decision:
a Class A grant becomes a register row flipped to `ship` with the clause and
source quoted; a Class B grant becomes `Permission via Email` in the biblio
`Original License`, per the existing convention. **The outreach log never
becomes a second source of truth for licence state** — it records the
correspondence, the register and biblio record the rights.

Set a single follow-up rule (one nudge at 3 weeks, then `no_response` and stop)
so silence terminates rather than lingering.

## Phasing

1. **Triage the 72 block/escalate register rows** into commercial /
   controlled / academic by hand. Output: a `tier` column on the register.
2. **Run `sweep_instrument_rights.py`** and attach a tables-gated count to each.
3. **Draft three templates** (A, B-adapted, C) and have Ben approve wording
   before anything sends.
4. **Send Class D immediately** — it is a disclosure and should not queue.
5. **Batch-send** top-ranked Class A, then work the 28 Class B rows at a steady
   cadence, then Class C.
6. Fold responses back into the register / biblio as they arrive.

## What is explicitly NOT automated

Nothing sends mail from a script. These go out over a named person's signature
to third parties, several of them commercial licensors — volume here means
*batched and tracked*, not machine-sent. Claude prepares the queue, the ranking
and the drafts; Ben sends and pastes replies back.
