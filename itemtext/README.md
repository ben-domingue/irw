# itemtext/

Item text for IRW tables: the wording, response options and instructions,
published on Redivis as `<table>__items` tables. Per-table extraction is
documented in `.claude/skills/irw-auto-itemtext/SKILL.md`, the batching layer in
`BATCH_PROCESS.md`. Uploading is done with `red_up` (see `../red_up/README.md`).

## Layout

| Location | Holds |
|---|---|
| `itemtables/batch_NNN/` | One extraction round each: `<table>__items.csv` (removed once uploaded), `provenance.csv`, `verify_<table>.R`, `verification_merged.csv` |
| `extraction_batches/` | Round protocol state: `queue_state.csv`, `round_log.md` (live status), round prompts |
| `fixes/` | Corrections to already-shipped tables, plus parked builds (see `fixes/README.md`) |
| `language_backfill/` | The 2026-09-01 administered-language backfill (irw#1777) |
| `reaudit/` | Works out what is still worth extracting now that the original extraction queue is used up (built from the live corpus) |
| `quarantine/` | Item-text files pulled out of their batches, each with a README explaining why |
| `audit_batch_reports/` | Per-batch reports from the 2026-08 audit-mode runs |
| `tests/` | Tests for the scripts here |
| `archive/` | Finished workstreams and one-time reports, kept for provenance: the v9 correction workstream, the 2026-08-29 audit-queue status, the 2026-08-14 status report, the availability pilot, the skill evaluation, and the #1709 comparison of item-text writers |

## Standing records (top level)

- `availability_audit_full.csv`: the availability verdict for each table (AVAILABLE, BLOCKED, and so on)
- `mapping_verification.csv`: the item-code-to-text mapping check for each shipped table
- `instrument_rights_register.csv`: instruments whose rights holders restrict distribution of the wording
- `provenance_vocab.csv`: the controlled vocabulary `check_provenance.R` enforces
- `live_tables.csv`: which `__items` tables are live, rewritten by `refresh_live_tables.py`
- `dataverse_api_route.md`: notes on the Dataverse route, cited by `sibling_consistency_sweep.py`

## Scripts (top level)

- `join.R <table>`: joins a response table to its item text
- `check_provenance.R`: validates every `provenance.csv` against `provenance_vocab.csv`
- `check_label_claims.py`: screens `data_labels` mapping claims (#1745)
- `clear_uploaded_itemtables.py`: removes uploaded `__items.csv` files and keeps their sidecars (#1956)
- `refresh_live_tables.py`: snapshots the live tables into `live_tables.csv`
- `sibling_consistency_sweep.py`: flags availability verdicts that a sibling table contradicts (#1751)
- `sweep_instrument_rights.py`: sweeps the corpus for wording from blocked instruments
