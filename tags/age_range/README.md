# tags/age_range/

Derives the `age range` tag from each table's `cov_age` data instead of the
hand-tagged sheet (Rule A of `../decisions/1760_age_range_and_sample.md`).

| File | Role |
|---|---|
| `derive_age_range.py` | Writes the files below. `python tags/age_range/derive_age_range.py` |
| `age_range_derived.csv` | **Live input.** `metadata/03_tags.R` reads it (`file.derived`) and its values outrank the sheet's. The tag scorers in `../scoring/` also read it. If you move it, update those paths: 03_tags.R skips a missing file without saying so |
| `age_range_audit.csv` | Every table considered, with its numbers and verdict |
| `age_range_quarantine.csv` | Tables held back for a human look, with the reason |
| `age_unit_confirmed.csv` | Tables whose age unit was confirmed as years by hand |
| `report_age_range_diff.py` | Diffs the derived tags against `metadata/tags.csv`. Writes `age_range_dry_run.{md,csv}` |
