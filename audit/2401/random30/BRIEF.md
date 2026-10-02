# Random-30 base-rate check: brief for each agent

**Purpose.** Measure how often a table drawn at random from the live IRW (4,596 tables) has a problem worth acting on. The earlier pilot (`../pilot/REPORT.md`) used hand-picked tables that already had known problems, so it can't give a rate. The sample is in `sample.csv` (seed 2401). You check only the slots you were assigned.

**Strictly read-only.** Write only inside `/home/ben/Dropbox/projects/irw/src/audit/2401/random30/`. Do not edit anything else, file or comment on GitHub issues, upload, withdraw, commit or push.

Read first: `../RULES.md` (the draft rules) and `../pilot/REPORT.md` § "Rule changes", which **overrides** RULES.md where they differ. Most importantly:
- one row per *finding*, not per table;
- the outcome codes `already_remedied` and `script_drift` exist;
- tables over ~200k rows get aggregate checks only.

## The bar: what counts as a finding
A finding counts only if it **changes an analysis** (values wrong, rows that shouldn't be there, missing rows, a covariate that is wrong) **or is a rights problem** with shipped item-text wording (including the `*_translated` columns), or is a user-relevant source caveat that meets #2529's test. Anything below that bar isn't worth recording: cosmetic column order, naming, `imputed_values` warnings on 0/1 items, and the like. A clean table gets one `no_action` row.

## Checks per table (cap about 15 minutes per table)
1. **Current state.** Is the table live, and does it have item text (`sample.csv`)? Is it already in `itemtext/withdrawals.csv`, `metadata/table_changes.csv`, `metadata/data_notes.csv`, or the `dup_id_item`/`cov_age` results in `irw_validate/results/`?
2. **Data, on live data.**
   - Row count vs `metadata/metadata.csv`.
   - Per-item resp range and distinct values. Look for sentinel codes (-99, 99, 999), impossible values, or one item on a different scale.
   - dup id+item without an occasion column.
   - `cov_*` ranges (age within 0–120, etc.).
   - Tables under ~200k rows may be read in full after `import redivis_shim; redivis_shim.install()` (at `src/redivis_shim.py`) and run through the `irw_validate` upload profile (see `irw_validate/README.md`, `cli.py`). Larger ones get aggregate SQL only: see `irw_validate/live_dup.py` and `live_cov_range.py` for how to query. Never `irw_fetch` a big table.
3. **Rights (only if the table has item text).** Run `itemtext/instrument_rights_register.csv` against the live item text **and** the `_translated` columns. Note that `irw_validate.rights.check_*` needs the register passed in explicitly. **Skip item text for `enem*` tables:** a collaborator owns those, and they are out of scope.
4. **Source caveat.** Read the `data/` processing script header (grep for the table name) for a stated defect, mean-fill, id fallback, or pooled forms. Apply #2529's test (`gh issue view 2529`; examples in `metadata/data_notes.csv`).
5. Also **record without investigating**: anything that looks like a script not reproducing the live table (`script_drift`), or a sample under 100 respondents.

## Outputs
- One dossier per table: `dossiers/<table>.md`, half a page. Cover each check, what it showed, and the outcome(s).
- One CSV of worklist rows for your slots: `fragments/<your_label>.csv`. Columns: `table, strand, source, claim, checks_run, evidence, proposed_outcome, confidence, group, minutes, redivis_reads`. Use `source=random30` and one row per finding.
- A final report (under 150 words): for each table, `clean`, or its findings with outcome and confidence.
