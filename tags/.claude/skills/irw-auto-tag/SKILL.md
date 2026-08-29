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

## Output: staging, not direct write

**There is no write-capable Sheets tool wired up for this skill.** Confirmed
2026-07-27: the Google Drive MCP tools 404 on both sheet IDs (not shared
with the connected account), and no `googlesheets4` / service-account
credential exists anywhere in this repo (`grep -ri
"googlesheets4\|gs4_auth\|service_account\|GOOGLE"` across the repo turns up
nothing). The user was asked how to handle this and chose **CSV staging**,
matching the pattern `automated_finding` already uses for its own
no-write-access queue sheet: stage rows in `tags/tags_queue_staging.csv`
(repo-tracked — **not** scratchpad or `/tmp`, which can't be found again
once the session ends) and tell the user what to paste into the sheet.
Don't claim the sheet was updated.

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

## Step 3 — Fetch the source text

```bash
python3 scripts/fetch_source.py table_a --doi 10.1037/a0022874   # prefer DOI when present
python3 scripts/fetch_source.py table_a --url https://...        # else use the dictionary URL
```
This resolves `https://doi.org/{doi}` (or fetches the URL directly),
caches the raw text under `.cache/` (gitignored — not committed), and
reports HTTP status / final URL / byte count. It does **not** decide
whether the content is paywalled — read the cached file yourself (`Read
.cache/{table}.txt`) and judge that. **If it's paywalled, login-gated, or
otherwise unreachable/unusable**, stop for that table and stage a row with
every field blank except `table`, `Rater`, and
`Notes = "cannot fully access due to paywall"` — don't guess content from
the Description/Reference text alone.

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
Sets `Rater = "claude-auto"` automatically. Refuses to add a table already
in `tags/tags_queue_staging.csv` unless `--force` is passed — this is the
local half of idempotency; `check_table_status.py` (Step 1) is the live-sheet
half.

## Step 6 — Hand off

Once a batch is staged, tell the user exactly what's in
`tags/tags_queue_staging.csv` and that it needs to be pasted into the "IRW
Tags" sheet by hand (no write path exists — see above). Don't delete the
staging file until the user confirms the rows actually made it into the
sheet.

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
