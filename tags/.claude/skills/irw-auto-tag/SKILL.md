---
name: irw-auto-tag
description: This skill should be used when the user asks to "tag this table", "process the tagging queue", "add IRW tags for X", or otherwise references filling in the "IRW Tags" Google Sheet (columns table/Rater/Construct Name/Context Text/Item text available?/Age Range/Child Age/Sample/Construct type/Measurement tool/Item format/Primary Language(s)/Notes) for newly added IRW tables. Also applies when asked to re-derive or check the sheet's controlled vocabularies.
---

# IRW Auto-Tag

Fills in the "IRW Tags" sheet — one row per IRW table describing its
construct, sample, and format — for tables that don't have a row yet. Works
from inside `tags/`.

Two sheets matter here and they are not interchangeable:

- **"IRW Tags"** (`1V3ef0sa7HKtJJd2cgqRAkEdfbpGWDD1JIyQa6HwVK7g`, gid
  `126134123`) — the sheet this skill fills in. **Core tables only.** Nominal
  tables have their own sheet, "IRW Tags Nominal"
  (`1v3toO6OPts_HIjcjHTOb9_v2Ne2oXZSTkGTeO6fUyrg`, gid `126134123`), same 13
  columns, staged via `tags/nominal_tags_staging.csv`; `comp` and `sim` have no
  tags by design. Check which source a table belongs to before staging a row —
  see `Rpkg/inst/developer/tags.md`.
- **"IRW Data Dictionary"** (`1nhPyvuAm3JO8c9oa1swPvQZghAvmnf4xlYgbvsFH99s`,
  gid `0`) — the *only* place to look up a table's paper/citation info. If a
  table isn't there, or has no usable info there, **do not search the open
  web for it** — stop and emit a blank row per Step 2 below.

Both sheets are public-viewable, so their CSV exports (used by every script
here) need no credentials. Writing to either sheet is a different story —
see "Output: staging, not direct write" below.

## Before doing anything

1. **Rater is set to `"claude-auto"` on every row this skill stages** — visibly
   distinguishable from human raters (`bd`, `arthur`, `savira`, `Mathias`,
   `Rubina`, `Xingyi`, ...) for audit/QC. Tell the user this is happening;
   don't silently pick a different value.
2. **Read `references/vocab.md`** before extracting any fields — it has the
   exact enums for Age Range / Child Age / Sample / Construct type /
   Measurement tool / Item format / Item text available?, plus the exact
   `Notes` strings to reuse (`no working link`,
   `cannot fully access due to paywall`). These enums were derived by
   enumerating the sheet's actual data, not read from Sheets API validation
   rules (no credential for that exists) — see that file's provenance
   section before trusting it blindly on a much later run.
3. **Idempotency**: never re-stage a table that already has a tags-sheet row
   (even a `claude-auto` one) unless the user explicitly asks to re-tag.
   Check both the live sheet (`check_table_status.py`) and the local staging
   file (`stage_tag_row.py` already refuses local duplicates on its own).
4. **Is this run being scored?** If so, stop and read "Step 1 is exactly what a
   measurement run must NOT do" below before doing anything else. A scored run
   follows this skill with one step removed, and getting that wrong silently
   produces an accuracy number that is measuring nothing.

## Output: staging, not direct write

**There is no write-capable Sheets tool wired up for this skill.** Confirmed
2026-07-27: the Google Drive MCP tools 404 on both sheet IDs (not shared
with the connected account), and no `googlesheets4` / service-account
credential exists anywhere in this repo (`grep -ri
"googlesheets4\|gs4_auth\|service_account\|GOOGLE"` across the repo turns up
nothing). The user was asked how to handle this and chose **CSV staging**,
matching the pattern `automated_finding` already uses for its own
no-write-access queue sheet: write rows to `tags/tags_auto.csv`
(repo-tracked — **not** scratchpad or `/tmp`, which can't be found again
once the session ends). Don't claim the sheet was updated: it isn't, and
it doesn't need to be. Since #1723 that file is a real pipeline input —
`03_tags.R` unions it into `tags.csv` on every run, so rows reach the
published Redivis table without anyone touching the Sheet.

If direct write is ever wanted later, it needs a Google service-account (or
OAuth) credential the user provisions themselves — that's not something to
build speculatively; ask again when it's actually requested.

## Step 1 — Find candidate tables

**Batch** (whole untagged queue):
```bash
Rscript scripts/list_untagged_tables.R                 # every untagged table
Rscript scripts/list_untagged_tables.R --sample 20      # a manageable batch
Rscript scripts/list_untagged_tables.R --out queue.txt
```
Needs R with the `irw` and `gsheet` packages (diffs `irw::irw_list_tables()`
against the tags sheet, case-insensitive — same logic as `tags/src.R`).

**Ad hoc** (one named table): skip straight to Step 2 with that table name.

Either way, run `check_table_status.py` first and drop anything already
tagged:
```bash
python3 scripts/check_table_status.py table_a table_b table_c
```

### Step 1 is exactly what a measurement run must NOT do

**If this run is being scored, skip this step entirely.** Everything Step 1
touches — `check_table_status.py`, the live sheet, `metadata/tags.csv`,
`tags/tags_auto.csv` — holds the answers a scoring run is being marked
against. On a table that already has a row, consulting them is reading the
answer key, and the resulting accuracy number means nothing.

This is not hypothetical and it is not a rule anyone broke. **Every scoring run
this project has done has suppressed Step 1** — #1721, #1722, #1786, #1796,
#1802 — and until 2026-09-03 no document said so, which made the skill and the
scoring harness look like two different processes rather than one process run
two ways. They are not: the harness is this skill, run blind and then gated per
column. See `tags/decisions/1704_two_tagging_paths.md`.

So there are two modes, and the difference between them is this step alone:

| | Step 1 | idempotency | what it is for |
|---|---|---|---|
| **production** | run it | required — never re-stage a tagged table | filling the gap |
| **measurement** | **skip it** | irrelevant; nothing is staged | finding out how good the tagger is |

A measurement run also stages nothing at all — no `stage_tag_row.py`, no edit to
`tags_auto.csv` — so the idempotency Step 1 provides is not needed there. Steps
2, 3 and 4 are identical in both modes, and that is the point: the mode changes
what the tagger is allowed to *see*, never how it extracts.

## Step 2 — Resolve the source from the Data Dictionary

```bash
python3 scripts/lookup_dictionary.py table_a table_b
```
For each table this returns `description`, `url`, `reference`, `doi`, and a
`no_data` flag. **If `no_data` is true** (no dictionary match, or every one
of those four fields is empty), stop for that table — go straight to Step 5
and stage a row with every field blank except `table`, `Rater`, and
`Notes = "no working link"`. Don't fetch anything or guess at content.

`description`/`reference` are useful context even without a `doi` (CRAN
package docs, OSF pages without a DOI, etc.) — don't require a DOI to
proceed.

**The dictionary can be wrong, and it is wrong in a specific way.** A row can
point at a real, on-topic source whose sample size matches exactly, while naming
an instrument that source never mentions (#1864). When Step 3's text and this
description disagree about *which instrument the table is*, do not pick a
winner — see "When the dictionary and the source disagree" in `vocab.md`. The
short version: leave `construct_name` and `construct type` blank, tag the
population and format fields from the source, and say so in `Notes`.

## Step 3 — Fetch the source text

```bash
python3 scripts/fetch_source.py table_a --doi 10.1037/a0022874 --url https://...
```
Pass **both** when the dictionary has both — they are tried in order, not
as alternatives. Given a DOI the script asks OpenAlex where an open copy
lives and tries those locations (PDFs first, extracted to text) before
falling back to resolving the DOI itself, then the URL. It caches under
`.cache/` (gitignored — not committed).

It reports `oa_status` from OpenAlex, and **that is what you judge a
paywall on — not the fetch failing.** Those are different findings:

| Outcome | What it means | What to do |
|---|---|---|
| `OK ... content=N_chars_visible` | Got prose that is not a blocker page | Read `.cache/{table}.txt` and continue to Step 4 |
| `OK ... content=repository_metadata:N_chars_visible` | **A catalogue record, not a paper** — the deposit's own title, description, keywords and file list, reached through the repository's API because its web page answers a bot challenge | Read it, but tag only what it actually says. It will usually support `construct_name` and sometimes `construct type`; it almost never states a sample or an age range, and vocab.md's rule against inferring those still binds |
| `UNREACHABLE oa_status=closed` | No open copy exists | Stage `Notes = "cannot fully access due to paywall"` |
| `UNREACHABLE oa_status=gold\|green\|hybrid\|bronze\|diamond` | An open copy **exists** and something else blocked us — a WAF, a captcha, a JS-only page, a dead link | **Not a paywall.** Stage `Notes = "no working link"`, and it is worth reporting: these are fixable |
| `UNREACHABLE oa_status=not_checked` | **No DOI**, so OpenAlex was never asked, and the URL refused us — typically a government or institutional data portal answering 403 | **Not a paywall**, and you cannot show it is one: with no DOI there is no open-access status to appeal to. Stage `Notes = "no working link"` |
| `OK ... content=low_prose_density:N_sentences_per_1k:M_chars_visible` | Long, blocker-free, and **probably furniture** — a CMS or JavaScript shell whose visible text is menus and metadata rather than the work | **Read it before trusting it.** Tag only what the text actually states; if it turns out to be chrome, treat it as `no working link` rather than tagging from the surrounding page |

**Data repositories are asked through their APIs** (#1786). Their web pages
serve a challenge or a JavaScript shell — Dataverse returns HTTP 202 with a
zero-byte body regardless of user agent, and every OSF project page is the same
4.2kB of CSS. OSF, Dataverse, figshare and Mendeley now go through
`api.osf.io/v2`, `api/datasets/:persistentId`, `api.figshare.com` and Mendeley's
`public-api`. **OSF matters most by volume: 1,065 of the dictionary's 4,330 rows
name it**, more than the other three combined. Where the deposit names the
paper it backs, that DOI is adopted and followed down the ordinary path, so the
usual outcome is the *article*, not the catalogue record. This was worth 8 of
the 10 unreachable tables in the 2.3 blind run.

The script rejects blocker pages rather than caching them, and prints the
reason per candidate (`blocker:recaptcha`, `too_short:3_chars_visible`,
`http_403`). This matters because raw byte count cannot tell an article
from a challenge page: the reCAPTCHA interstitial served for a fully
open-access PeerJ paper was 21kB, and OSF's JavaScript shell is a
consistent 4.2kB. Both used to cache and read as "the source".

Still read the cached file and judge it yourself — the script screens out
blockers, it does not confirm the text is the *right* paper. A dictionary
`doi` can point at a different article than the `reference` field names.

Cached text persists across runs specifically so a paywalled or
rate-limited source isn't re-hit on every retry.

## Step 4 — Extract fields

Read the cached source text and produce, per `references/vocab.md`'s exact
enums where applicable:

| Field | Notes |
|---|---|
| Construct Name | The instrument/scale's formal name if the source gives one |
| Context Text | **Verbatim excerpt** from the source describing the construct/instrument — this sheet is internal, so quoting directly is fine. Don't confuse this with the public-facing paraphrased `construct_description` from `metadata/03b_describe.R` (if it exists) — that's a different, paraphrased field for a different audience |
| Item text available? | Yes/No/blank — see vocab.md |
| Age Range | enum, vocab.md |
| Child Age (for child-focused studies) | enum, vocab.md — only when child-relevant |
| Sample | enum, multi-select, vocab.md |
| Construct type | enum, multi-select, vocab.md |
| Measurement tool | enum, vocab.md |
| Item format | enum, vocab.md |
| Primary Language(s) | ISO 639-2 codes, comma-separated — see vocab.md's freeform-field caveat |
| Notes | blank unless one of the two exact conventions above applies |

**Never write a value outside the enum for a controlled field.** If the
source doesn't clearly support a confident choice, leave that field blank —
this matches how the sheet's human raters already treat these columns.

## Step 5 — Stage the row

```bash
echo '{"table": "table_a", "construct_name": "...", "context_text": "...",
       "item_text_available": "Yes", "age_range": "Adult (18+)",
       "sample": "General/non-specific", "construct_type": "Affective/mental health",
       "measurement_tool": "Survey/questionnaire",
       "item_format": "Likert Scale/selected response",
       "primary_languages": "eng", "notes": ""}' \
  | python3 scripts/stage_tag_row.py
```
Sets `Rater = "claude-auto"` automatically, which is load-bearing: `03_tags.R`
**halts** if any row in this file has a different Rater, on the grounds that a
human row placed here would be silently outranked by the Sheet and lost.
Refuses to add a table already in `tags/tags_auto.csv` unless `--force` is
passed — the local half of idempotency; `check_table_status.py` (Step 1) is the
live-sheet half.

## Step 6 — Hand off

Open a pull request with the new rows in `tags/tags_auto.csv`. **Merging is the
accept** — no pasting, and nothing to confirm afterwards.

### Columns publish per column, against a measured bar

**Staging a value is not deciding to publish it.** Every column this skill fills
is held to a per-atom precision bar — currently 90% — measured against the human
gold set by `tags/scoring/`, and a column that has not cleared it is written by
the tagger, kept in the predictions for later measurement, and **blanked before
the rows are staged**. Selection is an act performed at assembly, deliberately
and once, not something each tagging run decides for itself.

As of 2026-09-03 that means `primary language(s)`, `item format`, `measurement
tool` and the SETTING facet of `sample` publish; `construct type` and
`sample`'s FRAME facet do not. Those two are not broken — they are measured, and
they are under the bar: on the 2026-09-03 comparison `construct type` scored
50.0% per-atom precision and the frame facet 57.1%.

Do not read the current list off this paragraph and assume it is live. **Quote
`tags/scoring/` and the most recent results file**, the way `status.json` rather
than prose is what you quote for coverage.

The gate has earned itself once already: #1802 withheld 44 of 60 `primary
language(s)` rows after four agents disclosed, unprompted, that they had
inferred the language from the study's *country* — the move the `age range`
rule forbids and which `vocab.md` had never addressed for language.

Since #1723 the file is unioned into `tags.csv` by `03_tags.R`, with three rules
worth knowing:

- **A human row in the Sheet always wins**, keyed on `table`. If someone has
  already tagged a table by hand, the auto row for it is dropped at export.
- **That is also the retirement path.** A superseded auto row stops being
  published whether or not anyone remembers to delete it, so leaving stale rows
  in the file is untidy rather than dangerous. Delete them in the same PR when
  you notice them.
- **Sentinel rows are staged but never published.** The blank rows Steps 2 and 5
  tell you to write for a paywalled source or a dead link — `table`, `Rater` and
  `Notes` only — are dropped at the union. Neither `Rater` nor `Notes` survives
  `KEEP_COLS`, so publishing one would put a bare table name in the public tags
  table: it would assert the table is tagged while saying nothing about it, and
  `audit_tables.R` would count it as covered, so it could never resurface as
  needing tags. Keep writing them — they still live in `tags_auto.csv`, and that
  file plus the Sheet is what stops the tagger re-attempting a paywalled source.
  They just stop at the export boundary. (Added after the first live union on
  2026-08-31 published 5 of them; `tests/test_tags_union.R` now covers both the
  drop and the fact that a *partially* tagged row still publishes.)

Auto rows face the same `TAG_VOCAB` enforcement as human rows, so a value
outside the controlled vocabulary halts the pipeline instead of publishing.
Run `Rscript tests/test_tags_union.R` from `metadata/` to check the union
offline before opening the PR.

## Batch behavior

Both modes share Steps 2-6 unchanged:
- **Whole queue**: Step 1's batch form, then loop the rest per table.
- **Single table**: skip straight to Step 2 with the one table name (still
  run `check_table_status.py` first).

## Re-deriving the controlled vocabulary

```bash
python3 scripts/derive_vocab.py
```
Enumerates actual non-empty values per controlled column straight from the
live sheet (see `references/vocab.md`'s provenance section for why this is
the best available proxy for the sheet's real dropdown rules). Diff its
output against `references/vocab.md` and update that file by hand if they've
drifted.
