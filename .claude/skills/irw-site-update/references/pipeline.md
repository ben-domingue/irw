# metadata/ pipeline — script-by-script reference

Compiled 2026-07-27 from reading every script in `metadata/` (this repo IS
`ben-domingue/irw` — no separate clone needed) and confirmed/corrected with
Ben in conversation. Treat this as the record of that conversation, not an
independent source of truth — if it ever disagrees with the actual scripts,
the scripts win.

## Core pipeline (in run order)

| # | Script | Output | What it does |
|---|---|---|---|
| 01 | `01_metadata.R` | `metadata.csv` | Diffs current Redivis tables (`item_response_warehouse`/`_2`/`_3`/`_4`) against the last-known `irw_meta` metadata table; for genuinely new tables, computes `n_responses`/`n_categories`/`n_participants`/`n_items`/density via the Redivis API; adds `variables` (pipe-joined, lowercased var names) and a `longitudinal` flag (`grepl("wave"\|"date", variables)`). |
| 02 | `02_biblio.R` | `biblio.csv`, `comps_biblio.csv`, `nominal_biblio.csv`, `simsyn_biblio.csv` | One script, four passes (loops over a `dbs` list) — one per source (core/comps/nom/sim), each with its **own** Google Sheet dictionary URL. For each: reads that source's dictionary sheet, finds rows not yet in the corresponding Redivis biblio table (or missing `BibTex`), fetches BibTeX from `doi.org` when a DOI exists, else falls back to a Claude call (`anthropic_chat()`, `claude-haiku-4-5`, `ANTHROPIC_API_KEY`) to synthesize one from Reference/URL text. Strips non-`Public Reshare?` rows *before* ever calling the API. **Swapped from OpenAI/GPT-4o to Claude on 2026-07-27** at Ben's request — plain `httr` POST to `https://api.anthropic.com/v1/messages` (no R SDK exists for Anthropic), `x-api-key`/`anthropic-version: 2023-06-01` headers, single-turn, no thinking/tools. |
| 03 | `03_tags.R` | `tags.csv` | Snapshot of the single flat "IRW Tags" Google Sheet (no per-source variant — applies loosely across all sources, though in practice used for core). Selects columns `c(1,6:12,3)` = table, Age Range, Child Age, Sample, Construct type, Measurement tool, Item format, Primary Language(s), Construct Name. No synthesis. |
| 05 | `05_comps.R` | `comps_metadata.csv` | Same shape as 01 but for `irw_competitions` (pairwise-comparison/arena-style data — `winner`/`agent_a`/`agent_b` columns). Author's own comment: "a lot of the functionality outside of the f() function is not tested." Its own biblio-generation half is dead/commented-out code (02 covers comps biblio instead). |
| 06 | `06_nominal.R` | `nominal_metadata.csv` | Same shape as 01 but for `irw_nominal` (free-text/nominal responses — `text` column instead of `resp`). Same dead commented-out biblio block. |
| 07 | `07_simsyn.R` | `simsyn_metadata.csv` | Near-identical to 01, for `irw_simsyn`. Same dead commented-out biblio block. |
| 09 | `09_hero_status.R` | `irw_site/data/hero_stats.json` | No Redivis calls — pure local aggregation of `metadata.csv` for the site homepage hero (totals + a category_breakdown bucketed by aggregate `n_categories`, per-table not per-item, a documented approximation vs. the paper's item-level figures). **Must run after 01** since it reads `metadata.csv` directly off disk. Default output path is `../../irw_site/data/hero_stats.json` relative to `metadata/` — i.e. a sibling of this repo, `irw/irw_site`. |

## Out of scope for this skill (confirmed with Ben, 2026-07-27)

- **`04_tables.R`** (QC, uploads nothing) — cross-references table-name sets
  across Redivis/dictionary/biblio/metadata/tags for `core` only. Its
  presence-matrix idea (`x`) and the incomplete-coverage subset it derives
  (`zz`, via `n<4` then `nn<4` filtering) is exactly what
  `scripts/audit_tables.R` generalizes to all four sources. Ben: "we will
  use 04 for qc but let's get into those details downstream once structure
  is established" — i.e. this skill's audit workflow is meant to supersede
  it, but the exact relationship (replace vs. keep both) is still open.
- **`08_itemtext.R`** — itemtext readability metadata (word/char counts,
  Flesch-Kincaid), incremental-only. Belongs to the separate `itemtext/`
  pipeline area (see `itemtext/.claude/skills/irw-auto-itemtext/`), not this
  skill.
- **`metadata/hotfixes/`** — five one-off patch/diagnostic scripts, all
  marked `?` (unknown run-status) in `hotfixes/README.md`. Ben: ignore for
  now.

## Ground truth for table names

The `irw` R package (source at `../../Rpkg` relative to this repo, i.e.
`irw/Rpkg`, installed and current — confirmed `source=` param live in the
installed copy 2026-07-27) exports `irw_list_tables(source = "core")`, with
`source` one of `"core"`/`"sim"`/`"comp"`/`"nom"`. Internally
(`Rpkg/R/redivis-datasets.R`) it maps to:

- `core` → `item_response_warehouse:as2e`, `item_response_warehouse_2:epbx`,
  `item_response_warehouse_3:5xaj`, `item_response_warehouse_4:980f` (all
  under `datapages`)
- `sim` → `bdomingu/irw_simsyn:0btg`
- `comp` → `bdomingu/irw_competitions:cmd7`
- `nom` → `bdomingu/irw_nominal:614n`

This is the same accessor the `tags` and `itemtext` skills already depend on
(`irw::irw_list_tables()`/`irw::irw_list_itemtext_tables()`), so
`audit_tables.R` uses it too rather than re-querying Redivis raw (which is
what `01_metadata.R`/`04_tables.R` do inline, duplicating logic the package
already centralizes). There's also an unexported
`.irw_live_table_names(source)` / `.irw_filter_rows_to_live_tables(df,
source)` pair in the package doing the same live/table diffing — not used
here since they're internal (`@noRd`), but worth knowing they exist if this
skill's logic ever needs to move into the package itself.

`core` is large — `irw_list_tables(source="core")` took ~59s for 2233
tables in a 2026-07-27 timing test; `comp` took ~10s for 22 tables. Budget
~90s+ for a full default `audit_tables.R` run.

## Safeguards — what actually exists vs. what Ben originally described

Ben's original framing assumed an existing system: raw verbatim paper text
never published (only paraphrased/synthesized descriptions), a caching step
storing a hash rather than raw text, and similarity-flagged rows getting
`construct_description = NA` with `provenance = "pending review"` rather
than a published draft.

**Grepped `metadata/`, `tags/`, `itemtext/` for `construct_description`,
`pending review`/`pending_review`, `hash`, `similarity` (2026-07-27) — none
of that system exists in the codebase today.** The only hit was one aside in
`tags/.claude/skills/irw-auto-tag/SKILL.md` (line 123) naming
`metadata/03b_describe.R` as the hypothetical source of a "public-facing
paraphrased `construct_description`" field, explicitly caveated "(if it
exists)". That file does not exist (confirmed via `find`).

What *does* exist, and stands in for the missing system today:

1. **`03_tags.R`'s column selection is an accidental safeguard.** The "IRW
   Tags" sheet's actual column order (pulled live 2026-07-27):
   `table, Rater, Construct Name, Context Text, Item text available?, Age
   Range, Child Age, Sample, Construct type, Measurement tool, Item format,
   Primary Language(s), Notes`. Column 4, "Context Text", is explicitly a
   **verbatim excerpt** field per its own sheet-header instruction text
   ("Please excerpt the text passage from the paper..."). `03_tags.R`'s
   `tag[-1, c(1,6:12,3)]` selects columns 1,6,7,8,9,10,11,12,3 — column 4 is
   never included, so raw paper text never reaches the public `tags.csv`.
   This works *today* purely because of a hardcoded positional index, not an
   explicit check — reordering the sheet's columns would silently break it
   with no error anywhere. Anyone touching `03_tags.R`'s column selection
   should be told this explicitly first.
2. **`tags/.cache/` and `itemtext/.cache/<table>/`** store raw fetched
   source text/PDFs (not hashes), gitignored so they're not committed — but
   nothing in code stops that raw text from being *read and republished*
   later; the gitignore only prevents accidental commit of the cache
   directory itself, it isn't a publication guard.
3. **This skill's own stopgap**: `diff_csv.py` flags any added/changed cell
   over ~500 chars (warn) / ~2000 chars (FLAG) in any regenerated public
   CSV — a length heuristic, not hash- or similarity-based, with no
   `provenance` concept. Built specifically because the real system doesn't
   exist yet and *something* should catch an accidental large-text dump
   landing in a public CSV in the meantime.

Ben's direction (2026-07-27): "we should come back to safeguards. they may
not be actionable in present state but perhaps we can fix that as we build
out this skill." Read this as: the length-heuristic stopgap above is the
interim fix, and if/when a real description-generation step gets built
(e.g. an actual `03b_describe.R`), that's the point to design the real
hash-cache + similarity-flag + `provenance = "pending review"` system —
ask Ben what corpus similarity should be measured against and what
threshold should trigger a flag before building it; don't guess.
