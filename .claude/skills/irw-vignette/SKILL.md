---
name: irw-vignette
description: Use this skill when asked to create a new IRW vignette — a Quarto analysis page for itemresponsewarehouse.org — scaffolding the compute script, running a pilot, and writing the .qmd page following the site's established compute/render split and canonical scaffold. Applies to phrases like "start a new vignette", "scaffold a vignette for X", "write a vignette replicating <paper>", or "assumption-audit vignette for Y". Does NOT cover editing vignettes/index.qmd, navbar/_quarto.yml changes, or merging to main — those are explicitly out of scope here.
---

# IRW Vignette Authoring

Scaffolds a new vignette in **`github.com/datapages/irw`** — the IRW
*website* repo (Quarto site, itemresponsewarehouse.org). This is a
**separate repository from `ben-domingue/irw` (this one)**. Nothing this
skill does touches `data/`, `metadata/`, or anything else in this repo.

Read `CLAUDE.md` and `vignettes/dimensionality.qmd` +
`vignettes/dimensionality_compute.R` in the website repo before scaffolding
anything — they're the canonical, fully-harmonized example of every pattern
below. Don't paraphrase from memory of this file; read the live files, they
may have moved on since this was written.

## Before doing anything

**Always ask where the files go, every time — never assume a path from a
previous run.** The local checkout path for `datapages/irw` varies (Ben
uses different worktrees/checkouts for different vignettes). Ask:

1. Where is the local checkout of `datapages/irw` to write into? If none
   exists, ask whether to clone it or set up a worktree — don't default to
   either.
2. What's the vignette about — genre (Tutorial / Assumption audit across
   IRW / Replicating a published finding / Cross-dataset analysis — see
   `vignettes/index.qmd` for current examples of each), and the actual
   question or paper. Don't infer a genre from a vague prompt; ask.
3. Proposed vignette name (snake_case, matching existing files like
   `dimensionality`, `local_dependence`, `gender_dif`) — confirm it before
   creating any files or branch.

## Workflow

### 1. Branch

One branch per vignette, named `<name>-vignette`, off `main`, inside the
checkout from step 1 above. For a compute-heavy vignette (many tables,
long fit times), ask whether the user wants an isolated git worktree for
active development — some existing vignette branches used one, then
removed it once stable; the branch itself is always kept regardless, until
merged.

### 2. Domain-judgment gate — ask, don't invent

Three things must come from the user, not from a plausible guess:

- **Dataset selection criteria** — the actual `irw_filter()` arguments
  (item-count range, participant minimum, construct restrictions) and the
  *reason* for each threshold (compute cost, statistical requirement,
  scope of the claim being tested).
- **The statistical method** — what model/test gets fit per table, what
  summary statistic(s) come out of it, and any flagging threshold. This is
  the actual content of the vignette; a wrong guess here produces a
  vignette that looks plausible but tests the wrong thing.
- **Limitations content** — real caveats specific to what the method does
  and doesn't handle. Not boilerplate ("this is exploratory, not
  confirmatory" is fine *if true* — confirm it, don't assume it).

Also ask for 1-3 "known-good" pilot tables if the genre calls for one (a
case with an obvious expected answer, e.g. `dimensionality_compute.R`'s
`psychtools_bfi` / `4thgrade_math_sirt` pair) — these make the pilot a real
sanity check rather than just a smaller random sample.

### 3. Compute script

Copy `templates/vignette_compute_template.R` (next to this SKILL.md) to
`vignettes/<name>_compute.R` in the target checkout and fill in every
`TODO(agent)` block using the answers from step 2. Non-negotiable shape,
already in the template:

- `library(irw)` + whatever modeling packages the method needs.
- Fixed `set.seed()`.
- `PILOT <- TRUE/FALSE` flag; when `TRUE`, run on known-good tables plus a
  small random top-up (`PILOT_N_TABLES`).
- Per-table fit wrapped in `tryCatch` — one bad table logs and drops, never
  crashes the batch.
- Incremental per-table caching to `<name>_data/fits/<table>.rds` so a
  crashed/interrupted run resumes instead of restarting.
- `furrr::future_map()` over tables, `plan(multisession, workers = min(4,
  detectCores() %/% 2))`.
- Combine step, then a single `saveRDS()` to
  `<name>_data/<name>_results.rds` containing at minimum: `summary`,
  `candidate_tables`, `n_all_candidates`, `pilot`, `date_run`, `session`.
- `irw_save_bibtex()` for the tables actually used, writing
  `<name>_data/references.bib`; append hand-written entries only for
  methods papers the user actually cited — ask, don't fabricate a citation.

Both the compute script and the resulting `.rds` cache get committed to
git — the cache is checked-in data, not a build artifact to `.gitignore`.

### 4. Pilot run

Set `PILOT <- TRUE`, run `Rscript vignettes/<name>_compute.R` from the
target repo's root. Requires `REDIVIS_API_TOKEN` in the environment (data
pages fetch live from Redivis; nothing renders without it) and `renv`
packages restored (`renv::restore()` if this is a fresh checkout).
Report back to the user: how many candidate tables matched the filter, how
many pilot tables produced usable results, and any per-table failures
logged during the run — before touching the `.qmd` or moving to a full
batch.

### 5. Vignette page

Copy `templates/vignette_template.qmd` to `vignettes/<name>.qmd` and fill
in every `TODO(agent)` block. Fixed structure, do not reorder or rename
sections:

`## Motivation` → `## Data and methods` → `## Results` → `## Limitations`
→ `## Reproducibility` → `## References`

Key points already baked into the template:

- Frontmatter sets `execute: {echo: true, ...}` and `code-fold: true` —
  this **locally overrides** the site-wide `echo: false` default in
  `_quarto.yml`. Vignettes are the one place code is shown. Never edit
  `_quarto.yml`'s site-wide default to achieve this.
- Setup chunk: loads the cache if present, sets `cache_ok`, and
  `knitr::opts_chunk$set(eval = cache_ok)` so every downstream chunk
  silently no-ops when the cache is missing — plus a matching empty-schema
  `tibble()` fallback so the page still parses.
- `cache-warning` and `pilot-warning` callout chunks (verbatim pattern,
  just re-point the `Rscript` path) so a page can be pushed for review
  before, or during, a full multi-hour batch.
- AI-disclosure `callout-note` — keep it (this skill is doing the
  authoring), delete it only if a human is writing this one largely
  by hand.
- Named palette variables (`irw_blue`, `irw_red`, `irw_grey`) — never
  scatter literal hex strings through the page.
- `ggplot2` + `ggplotly(tooltip = "text")` with a `text=` aesthetic
  showing table name, for any figure with more than one dataset per point;
  `knitr::kable()` for tables.
- Motivation section should link sibling vignettes that share the
  assumption/method — verify those `.qmd` files actually exist in
  `vignettes/` before linking them, don't guess file names.

### 6. Render check

`quarto render vignettes/<name>.qmd` (or `quarto preview`) from the target
repo root against the pilot cache before reporting done. Confirm both the
cache-missing and pilot-warning states actually render as expected if
easy to check (e.g. temporarily rename the cache file).

## Explicitly out of scope

- **`vignettes/index.qmd`** — no card, no edits. Tell the user the
  vignette still needs one added there; don't write it yourself even as a
  suggestion diff. (A separate assistant workflow already handles
  site/navbar integration — this skill is scoped to the vignette page
  itself.)
- **`_quarto.yml`** — never edit the site-wide navbar or execute defaults.
- **Merging to `main`** — never do this without explicit human sign-off.
  Some vignettes are gated on a named collaborator's review, not just the
  requesting user's — ask if unsure whose sign-off is needed.

## Key `irw` R package functions

From `github.com/itemresponsewarehouse/Rpkg`:

- `irw_filter(...)` — select candidate tables by `n_items`,
  `n_participants`, etc.
- `irw_fetch(table)` — pull one table long-format from Redivis.
- `irw_long2resp(df)` — reshape long-format responses to a wide
  item-response matrix.
- `irw_tags(tables = ...)` — `construct_type` / `item_format` metadata for
  by-construct breakdowns.
- `irw_save_bibtex(tables, output_file = ...)` — citation generation for
  the tables actually used.
