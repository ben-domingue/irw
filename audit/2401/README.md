# audit/2401/

The workstream folder for [#2401](https://github.com/ben-domingue/irw/issues/2401),
the retroactive audit of published tables (paused 2026-09-11). Not a pipeline
stage: nothing scheduled reads it.

| Path | Holds |
|---|---|
| `RULES.md` | The audit's rules, frozen at a date. Rulings made after that date apply only to tables not yet reviewed |
| `detectors/` | Corpus-wide flags from the automated detectors (`irw_validate/live_detectors.py`) and their calibration |
| `pilot/`, `random30/` | The pilot and the random-sample pass: worklists, per-table dossiers, reports |
| `triage/` | Triage of detector flags |
| `repairs/` | Specs and builders for staged fixes, plus the `table_changes` rows waiting on a release |
| `BATCH_1.md`, `UPLOADS.md` | What was staged for Ben, and what he confirmed uploaded |

Some builders in `repairs/` write to a staging directory outside the repo
(`~/irw-stage/2401-audit/`), so they reproduce only on the machine that ran
them.
