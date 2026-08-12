# ENEM re-run #2 — add `resp_raw`, produce nominal tables

**Written:** 2026-08-11. **Revised:** 2026-08-12.
**Increment on `FARMSHARE_RUNBOOK.md`**, which stays authoritative for setup, downloads, SLURM,
and the main/regular item logic. Read that first if starting cold; read this for what is
different on the second run.

**Owner:** Mateus Mazzaferro. **Redivis uploads:** Ben (Mateus has no token).
**Related:** PR #1556, issues #955, #723, #1353 (nominal branch), the IRW
[nominal standard](https://itemresponsewarehouse.org/nominal_standard.html).

---

## 0. Status and locked decisions

**Ben has already uploaded the 52 tables from the July run to Redivis.** PR #1556 is still open;
Ben said Mateus can either rewrite it or he can approve it and take a new one. **Decision:
rewrite #1556.**

**Consequence: this is a re-version of 52 live tables.** The additivity proof in §5 is mandatory.

### LOCKED — Path 1: `resp_raw` goes into the warehouse tables

The 52 warehouse tables are re-versioned with the added column; the nominal tables are the same
data with that column renamed `text`.

The rejected alternative was leaving the warehouse tables untouched and putting the letters only
in the nominal copies. **Rejected on precedent: every IRW dataset that has both a warehouse table
and a nominal table keeps the raw column in the warehouse table.** All six —

| dataset | raw column in its main warehouse table |
|---|---|
| `borges_brazil_residency_2024_cbt` | `resp_raw` |
| `himmelstein-berlin_numeracy-2025` | `resp_raw` |
| `much_tte_2025_concentrationtask` | `raw_resp` |
| `much_tte_2025_matrixreasoning` | `raw_resp` |
| `wilmer-mrmet-normative-data-set-2022` | `raw_resp` |
| `wilmer-rmet-normative-data-set-2022` | `raw_resp` |

The other nominal tables (`asap20train`, `persuade_learningagency`, `preference_inventory`,
`mirt_*`) have **no** main-warehouse counterpart — essays, preferences, simulated data with no
scored version. There is no IRW precedent for publishing a scored warehouse table while
withholding the raw column from it.

*Do not re-derive this from "it would duplicate the join logic" — that argument is false. The
re-run holds one frame per year containing both the score and the letter, so writing a second
output from it is a rename and a `write.table`. Both paths cost the same; the decision is
precedent, not effort.*

### LOCKED — the cluster does the work, Ben only checks and uploads

Anything that can run on FarmShare runs on FarmShare. **The cluster produces both sets — 52
warehouse tables and 52 nominal tables — in one pass**, and both ship in one handoff. Ben's job
is to inspect and upload. This also collapses what was previously a two-phase, two-round-trip
plan into a single delivery.

### LOCKED — compression

**Default `save()` (gzip). No `compress="xz"`.** Storage is not a constraint and Ben will likely
convert on ingest anyway. See §7 for the resulting sizes.

### Nothing is blocking

There are no open questions that need Ben before the cluster work starts.

---

## 1. Why a full re-run is unavoidable

`resp_raw` cannot be back-filled from the existing outputs. Where `resp == 1` the raw letter is
recoverable (it equals `TX_GABARITO`, and `ITENS_PROVA_YYYY.csv` is tiny). Where `resp == 0` it is
one of six remaining codes and is **not** recoverable. That is ~20% of rows. So: full reprocess
from INEP microdata, all thirteen years.

Nothing else about the pipeline changes. Same seed, same booklet codes, same item sets.

---

## 2. The code change

One line per area in each of the thirteen `irw/data/enem_YYYY.R` scripts. `raw` is already in
scope where `resp` is built — it is the column produced by `pivot_wider(names_from="type")` — so
this is only a matter of not dropping it.

In `process_area()`, change the tail from:

```r
  df |> mutate(resp = if_else(raw == key, 1, 0)) |>
    filter(item %in% std_set(area)) |>
    select(id, item, resp, position, booklet)
```

to:

```r
  df |> mutate(resp = if_else(raw == key, 1, 0)) |>
    filter(item %in% std_set(area)) |>
    select(id, item, resp, resp_raw = raw, position, booklet)
```

`resp` is untouched. The change is strictly additive.

**Column order** — `id, item, resp, resp_raw, position, booklet`. `resp_raw` is a response-level
column, so it belongs next to `resp`, ahead of `position`/`booklet`.

**Naming** — `resp_raw`, not `raw_resp`. Both exist in published tables; `resp_raw` is the one used
in `item_response_warehouse_2` and in the most recent additions.

**Type** — must stay `character`. Do not let it become a factor on write, and flag to Ben that the
Redivis variable type needs to be string; `.` and `*` will otherwise invite coercion.

---

## 3. LOCKED decision — the `.` and `*` codes

INEP does not use only `A`–`E`. Measured on `TX_RESPOSTAS_CH`, 2024, first 200k examinees:

```
A 1456789   C 1287179   B 1283939   E 1254442   D 1237405
.   49038  (0.79%, blank / omitted)
*    8723  (0.14%, double mark)
```

**Decisions:**

- `resp` stays `if_else(raw == key, 1, 0)`. `.` and `*` score **0**. This is what INEP does and
  what keeps CH/CN/MT density at 1.0 — the point of the reprocess. Do not change this.
- `resp_raw` carries `.` and `*` **verbatim**. No mapping, no dropping, no NA.
- Nominal `text` carries them verbatim too. **Do not** apply the rare-category filter (`tab > 2`)
  used in `much_tte_2025.R` and `wilmer.R` — those had open response sets; ENEM has a fixed
  alphabet and both codes are common in absolute terms (millions of rows).

Rationale: dropping is destructive and unrecoverable, keeping is filterable in one line.
Distinguishing an omit from a wrong answer is most of the value here — ENEM has real
position/speededness effects and omits are the evidence for them. NA would collapse `.` and `*`
into each other and lose the distinction.

### Expect Ben to challenge this — preempt it

On #1366 (`borges_brazil_*`, the closest analogue) Ben's first response to a new `resp_raw` column
was:

> `@saviranadela` can you look at the `resp_raw=X` values. are these missing do you think?

and the contributor converted them to NA in PR #1397. **He reads the raw alphabet and asks about
anomalous codes.** So state it up front in the issue comment rather than waiting to be asked: `.`
and `*` are documented INEP codes, not data errors; they are kept verbatim because that preserves
strictly more information than NA; and `resp` is unaffected either way.

**Tell Ben so it does not read as a bug:** `n_categories` for the nominal tables will be **7**, not
5, because `metadata/06_nominal.R` computes `numDistinct` on `text`. Say so in the Dict
description: `A B C D E`, plus `.` = blank, `*` = double mark.

---

## 4. QC to add to the run

Add to `process_area()`, **after** the LC language filter (so 2019-style `9` padding is already
gone) and before the return:

```r
ALPHABET <- c("A","B","C","D","E",".","*")
out <- df |> mutate(resp = if_else(raw == key, 1, 0)) |>
  filter(item %in% std_set(area)) |>
  select(id, item, resp, resp_raw = raw, position, booklet)

stopifnot(!any(is.na(out$resp_raw)))
tb  <- table(out$resp_raw)
bad <- setdiff(names(tb), ALPHABET)
if (length(bad) > 0)
  stop(sprintf("%s %s: unexpected raw codes: %s", year, area,
               paste(sprintf("%s(n=%d)", bad, tb[bad]), collapse=" ")))
cat(sprintf("  %s raw: %s\n", area,
            paste(sprintf("%s=%.4f", names(tb), tb/sum(tb)), collapse=" ")))
out
```

**The alphabet is not verified for every year.** The old `enem_2019.R` did
`str_remove_all(TX_RESPOSTAS_LC, '9')` — 2019 padded the not-taken language block with `9`. The
current scripts drop that hack and handle it via `item_lingua == tp_lingua`, which should remove
those rows anyway, but nobody has checked 2013–2018 or 2021/2025 for other codes. Fail loudly
rather than shipping a stray character into `text`.

Run `ENEM_DRY_N=200000` for all thirteen years and read the alphabet lines **before** the full
array. Cheap way to find a surprise year.

---

## 5. The validation that actually matters

The change must be **purely additive**. Prove it:

For each of the 52 tables, merge the new output against the corresponding published table on
`id + item` and confirm `resp` agrees on 100% of overlapping rows, with identical row counts and
identical item sets. Same seed, same code path, so it should be exact — a mismatch means
something drifted and needs investigating before handoff. **Do not "fix" a mismatch; stop and
report it.**

The July tables are in the Drive zip linked from the #955 comment; 2023 and 2024 are also in
`ENEM/output/regular/` on Mateus's laptop. This is the same check Ben asked for last round (old
vs. new cross-tab, zero off-diagonal) — reuse `ENEM/scripts/validate_enem_output.R`.

Then run `misc/validate_irw.R`. Expected: no errors, one soft NOTE that `position`, `booklet`, and
now `resp_raw` lack a `cov_` prefix.

---

## 6. Nominal tables — produced on the cluster

**Timeline, so this does not get garbled:**

| When | What exists |
|---|---|
| **Today** | 52 warehouse tables on Redivis, **five** columns, **no `resp_raw`**. |
| **After the re-run** | 52 warehouse tables (six columns) **and** 52 nominal tables, both as local files on the cluster. |
| **After Ben uploads** | Warehouse tables re-versioned; nominal tables live in `irw_nominal`. |

No table with `resp_raw` exists anywhere right now.

Per the standard, `text` is "the nominal version of `resp`" — the response, **not** the item stem.
Item text is a separate subsystem (`itemtext/`, `metadata/08_itemtext.R`, Phase 2 / #1403).

`resp` is retained alongside `text` (confirmed in `borges_brazil.R`, `himmelstein.R`, `wilmer.R`,
`asap20.R`). So the ENEM nominal table is the warehouse table with one column renamed:

| id | item | resp | **text** | position | booklet |
|---|---|---|---|---|---|
| 210059085130 | 48324 | 1 | C | 136 | 1211 |
| 210059085130 | 141582 | 0 | . | 138 | 1211 |

### On the cluster

After each year's four areas are written, emit the nominal copies from the same frames:

```r
nom <- df
names(nom)[names(nom) == "resp_raw"] <- "text"
save(nom, file = sprintf("nominal/enem_%d_1mil_%s.Rdata", year, suf))
```

**Ship `.Rdata`, not the pipe-delimited text the other nominal scripts write.** Those datasets are
small; 52 ENEM tables as `write.table(sep="|")` would be ~90 GB. This is the same reason the July
handoff was `.Rdata` rather than CSV. Note the deviation in the issue comment.

### In the repo

Commit `irw/data/nominal/enem.R` as the conventional `irw_fetch` wrapper — it matches six of the
eight existing nominal scripts and is the reproducible path once the warehouse tables are live:

```r
# ENEM nominal tables: text = the letter the examinee marked (A-E, . = blank, * = double mark).
# resp is retained as the scored 0/1.
# NB: the delivered files were generated on FarmShare from the same frames as the warehouse
# tables, to avoid a ~63 GB round trip. This wrapper reproduces them from the published tables.
for (y in 2013:2025) for (a in c("lc","ch","cn","mt")) {
  nm <- sprintf("enem_%d_1mil_%s", y, a)
  df <- irw::irw_fetch(nm)
  df$text <- df$resp_raw
  df$resp_raw <- NULL
  write.table(df, nm, quote=FALSE, row.names=FALSE, sep="|")
}
```

`quote=FALSE` with `sep="|"` is safe — `text` is a single character from a fixed alphabet, never a
pipe.

**Offer Ben the alternative without making it a blocker:** since the nominal set is byte-identical
to the warehouse set except for one header, he can skip ingesting it and derive it inside Redivis
instead. His call; the files will be there either way.

---

## 7. Storage

Measured on the real `enem_2023_1mil_mt` table (44,913,825 rows) with a simulated `resp_raw` at
the observed marginal distribution:

| | per table | × 52 |
|---|---|---|
| current 5-column, gzip | 28.3 MB | ~1.5 GB |
| 6-column, gzip (**what we are doing**) | 53.8 MB | ~2.8 GB |

Plus the nominal set at the same size: **~5.6 GB total handoff.** Fine for Drive. A near-random
single-character column is what gzip is worst at, which is why it nearly doubles; xz would have
held it near the old size but adds a compatibility unknown on Ben's ingest for no benefit we need.

---

## 8. Run sequence

**[C]** cluster · **[M]** Mateus off-cluster · **[B]** Ben

1. **[C]** `FARMSHARE_RUNBOOK.md` §2–4: setup, re-download microdata. **`$SCRATCH` was last
   populated 2026-07-13 and has very likely been purged — budget the full ~9 GB re-download.**
2. **[C]** Apply §2 + §4 + §6 to all thirteen `irw/data/enem_YYYY.R`.
3. **[C]** `ENEM_DRY_N=200000`, all thirteen years. Read every alphabet line. **Stop and report if
   any year shows a code outside `A B C D E . *`.**
4. **[C]** Full SLURM array. Runbook §5, `-t 02:00:00 --mem=32G -c 4`, default gzip.
5. **[C]** Validate per §5 — additivity against the published tables, then `validate_irw.R`.
6. **[M]** Zip and upload to Drive: 52 warehouse `.Rdata` + 52 nominal `.Rdata`, QC logs, per-year
   alphabet tallies, the additivity report.
7. **[M]** Rewrite PR #1556: the thirteen scripts, `data/nominal/enem.R`, header comments, and the
   schema line in the PR body.
8. **[M]** Dict rows. **Two different sheets** — see §9.
9. **[M]** Comment on #955 (warehouse re-version) and on #1353 (nominal set).
10. **[B]** Re-version the 52 warehouse tables; upload the 52 nominal tables to `irw_nominal`.
11. **[B]** Refresh metadata — **see the gotcha in §9**; a plain `01_metadata.R` run silently skips
    re-versioned tables. Then `06_nominal.R` for the nominal set.

---

## 9. Gotchas, sheets, and housekeeping

### The metadata refresh will silently skip these tables

`metadata/01_metadata.R` is **incremental**:

```r
toadd <- new.tables %in% old.tables
...
nms <- new.tables[!toadd]     # only these get recomputed
```

A **re-versioned** table keeps its name, so it is in `old.tables`, so it is skipped. The 52 enem
rows would keep their existing `variables` value — `id| item| resp| position| booklet` — and never
learn about `resp_raw`. There is an `08_itemtext_recompute.R` for the item-text pipeline but no
equivalent for `01`.

**Ben needs to force it**, most simply by deleting the 52 enem rows from the `metadata` table
before running `01_metadata.R`. Put this in the issue comment; the symptom is quiet.

`n_categories` stays **2** for the warehouse tables (`resp` unchanged), so the 40 existing enem
rows in `metadata/hotfixes/n_categories.csv` remain correct.

### Two different Dict sheets

- **Warehouse tables** → the main IRW Dict, sheet `1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s`
  (rows 70–121 already exist from July; update the variable list and add the `.`/`*` note).
- **Nominal tables** → the **separate nominal Dict**, sheet
  `12tM4vADKcUm5LGOGRwQ5_HKkdYa3mZUaKbFUqgs2U_w` (from #1353). 52 new rows. Columns:
  `table, table lower, Description, URL (for data), Reference, DOI (for paper), Original License,
  Custom License, Public Reshare?, Derived_License, Notes, Contributor, Date`.

Also update Tags rows for the warehouse tables.

### Precedent for how nominal work gets submitted

- #1353 is Ben's nominal tracking issue (label `nominal`); nominal data lives in its own Redivis
  dataset. Individual datasets got their own issues under it (#1366 borges, #1335
  preference_inventory, #1186 persuade).
- Data is attached to the GitHub issue when small (borges was a zip attachment). ENEM is far too
  big — Drive, as in July.
- PR bodies are usually minimal; #1397 ("changed X resp raw to NA") had an empty body and touched
  one file. Mateus's PR descriptions are far more thorough than the norm, which is fine.
- Fixes to the raw column go in the **main** `data/<dataset>.R` script, not in `data/nominal/`.

### `runkit/` must not reach the PR

These runbooks are carried to the cluster in a `runkit/` directory on the working branch so the
cluster session can read them and commit script changes alongside. **Delete `runkit/` before
finalizing the PR** — it is scratch, not repo content, and PR #1556 already removes
`data/enem_reprocess/` on exactly that principle.

```bash
git rm -r --cached runkit && echo "runkit/" >> .gitignore
```

### Housekeeping in the thirteen scripts

- Every script's header points at `enem_reprocess/identify_regular_items.py` and "see that
  directory for the full reprocessing writeup." **PR #1556 deletes `data/enem_reprocess/`** — the
  reference is dangling. Fix it in each file.
- Add `resp_raw` to the schema line in each header block.
- The PR body and the existing #955 comment both state the five-column schema. Both need updating.

---

## 10. Effort

**Easy:** the code change (one `select()` line × 13 files), the QC block, the nominal emit, the
wrapper. Perhaps an hour of editing.

**Not hard, but not free:** a second full FarmShare cycle — re-download, thirteen-year array,
revalidation, packaging. A day of mostly-unattended wall time. Then 52 nominal Dict rows by hand.

**The actual risks:** (a) 52 *live* tables are being re-versioned, so the additivity proof in §5 is
mandatory; (b) a pre-2017 year uses a raw code nobody has checked for — which step 3 is designed
to surface cheaply, before the expensive run.

---

## 11. For a fresh Claude Code session on FarmShare — read this first

You have no memory of the conversation that produced this document. Everything you need is here
and in the files below. Do not re-derive decisions marked LOCKED.

**Read, in order:**

1. `FARMSHARE_RUNBOOK.md` — setup, downloads, SLURM, main/regular item logic. Still authoritative.
2. **This file** — what is different on the second run.
3. `AGENT_HANDOFF_ENEM.md` — wider ENEM/IRW project context.
4. `ENEM_PROJECT_LOG.md` — running history.

**The job in one paragraph:** the 52 published ENEM tables
(`enem_{2013..2025}_1mil_{lc,ch,cn,mt}`) score each response 0/1 against the answer key and discard
the letter the student actually marked. Ben approved keeping it. Add a `resp_raw` column carrying
that letter verbatim, and emit a parallel set of nominal tables where the same column is named
`text`. `resp` does not change. This requires a full reprocess from INEP microdata across thirteen
years, because `resp_raw` cannot be back-filled (§1).

**Ground rules:**

- Mateus runs nothing on his laptop. All compute is FarmShare, under `sbatch`/`srun`, never a
  login node.
- Mateus has **no Redivis token**. Ben uploads and versions everything.
- Ben's time is the scarce resource. Anything that can run on the cluster runs on the cluster.
- `resp` must come out bit-identical to the published tables. If it does not, **stop and report** —
  do not fix it.
