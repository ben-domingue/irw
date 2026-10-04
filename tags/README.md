# tags/

Table tags (construct, sample, measurement tool, age range, …). How tags reach
the published `tags.csv` is in [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
section 3: the hand-maintained Sheet, unioned with automated rows at export.
The vocabulary is enforced by `TAG_VOCAB` in `metadata/tag_normalize.R`.

| Path | Holds |
|---|---|
| `tags_auto.csv` | Automated tag rows, unioned with the Sheet by `metadata/03_tags.R`; a human row wins |
| `nominal_tags_staging.csv` | An empty paste scaffold for the nominal tags Sheet. Deliberately **not** read by `03_tags.R` (see the comment there) |
| `.claude/skills/irw-auto-tag/` | The tagging skill (also reachable as `../.claude/skills/irw-auto-tag`, a symlink) |
| `scoring/` | Calibration and scoring runs for the automated tagger |
| `decisions/` | Written rulings on tag questions, by issue number |
| `age_range/`, `itemtext_language/` | Topic folders for one tag column or derived field each |
| `src.R` | Ad hoc helper that reads the nominal tags Sheet against the live table list |
| `tagging_joao/` | An earlier (2025) OpenAI-based tagger, superseded by the skill |
| `archive/` | Finished work kept for the record |
