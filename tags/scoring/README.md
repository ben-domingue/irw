# Auto-tagger scoring (issue #1721, sub-action 2.2)

Scores the `irw-auto-tag` skill against the human-tagged gold set, per column.
Run 2026-08-30. Reproduce with:

```bash
python3 score.py predictions_2026-08-30.json sample_2026-08-30.json
```

## Method

**Gold set.** `metadata/tags.csv` — 2,448 human-tagged tables. No new labelling.

**Sample.** 60 tables, 15 from each of the four core warehouses, drawn with
`random.seed(1723)` from tables that are both tagged and present in
`metadata.csv`. Stratifying deliberately over-samples w3 and w4, which are the
undertagged shards (27% and 35%) and might differ in character from w1 (99.9%).
Join on lowercased table names: 307 rows in `metadata.csv` are not lowercase and
would silently drop from a case-sensitive join.

**Blind.** Six subagents of ten tables each, forbidden from reading `tags.csv`,
from running `check_table_status.py`, and from opening the tags sheet — all three
expose human answers. They ran the skill's real Steps 2–4 (dictionary lookup,
source fetch, extraction against `references/vocab.md`) and were forbidden from
staging rows, so nothing was written.

**Model.** Sonnet. These are Sonnet numbers; a run under a stronger model would
likely differ, and the gap is not measured here.

## Scoring

Gold is post-normalisation (`tag_normalize.R` sorts, dedupes and renames
`Internet-based (Mturkers, etc)`), so predictions get the same treatment before
comparison. Multi-selects compare as sets, so `"A, B" == "B, A"`.

A blank prediction is an **abstention, not an error** — `vocab.md` tells the
tagger to leave a field blank rather than guess, so scoring blanks as wrong would
punish the behaviour we asked for. Hence three numbers:

| | |
|---|---|
| **accuracy** | correct / answered — is it right when it commits? |
| **coverage** | answered / gold available — how often does it commit? |
| **yield** | correct / gold available — what you actually get |

`child_age` is reported separately as well, because gold is NA for ~80% of rows:
there NA is a real answer meaning "not a child-focused study", so a blank
prediction against NA is correct rather than an abstention.

## Results

| column | accuracy | coverage | yield |
|---|---|---|---|
| `primary_languages` | **90.9%** | 91.7% | 83.3% |
| `measurement_tool` | **86.8%** | 100% | 86.8% |
| `item_format` | **90.9%** | 57.9% | 52.6% |
| `age_range` | 73.0% | 97.4% | 71.1% |
| `construct_type` | 64.9% | 100% | 64.9% |
| `sample` | **41.7%** | 94.7% | 39.5% |
| `child_age` | 75.0% | 66.7% | 50.0% (n=6) |

## What the numbers say

**37% of tables produced nothing.** 11 fetch failures, 9 paywalls, 2 with no
usable source — despite all 60 having a dictionary entry. This caps yield before
accuracy is even in play, and the 11 fetch failures are the fixable half.

**Vocabulary size does not predict difficulty.** `#1704` assumed the four
closed-vocabulary columns would be the easy ones. `primary_languages` has 91
distinct values and scores 90.9%; `age_range` has six and scores 73%. What
predicts difficulty is whether the answer is *stated* in the source or must be
*inferred* from it.

**`age_range` has one bug, not a distribution of errors.** Nine of its ten errors
are gold `Mixed` -> predicted `Adult (18+)`. Humans code a sample spanning e.g.
15–82 as `Mixed`; the tagger sees adults and commits. `vocab.md` never says this.
One rule should move this column to near ceiling.

**`sample` is the genuinely hard one.** Its errors are over-commitment: 13 of 21
are `General/non-specific` or `Targeted/specific` -> `Representative` or
`Educational`. Recruitment strategy is rarely stated outright, and the tagger
guesses a specific category where humans hedge.

**`item_format` abstains well.** 90.9% accurate but answers only 58% of the time
— the failure mode `vocab.md` asks for.

**`child_age` knows when not to answer.** 31 of 32 non-applicable rows correctly
left blank.

**Warehouse is the wrong axis.** w3 scores 81.8% with zero abstentions, but not
because w3 is easier: its sampled tables are single-instrument psychometric
papers that name their scale. w1's abstentions are large-scale assessment
programmes (PISA, ENEM) whose source is a data portal rather than a paper. The
real split is source shape, not shard.

## Suggested bar for 2.3

Ship per column, as #1722 argues:

- **Ship now** — `measurement_tool`, `primary_languages`, `item_format`
- **Ship after the `Mixed` rule is added to `vocab.md` and re-scored** — `age_range`
- **Do not ship** — `sample`, `construct_type`
- **Undecided, n too small** — `child_age`

## Caveats

- n=38 tagged tables; per-column counts are smaller still, and `child_age` has 6.
  These are directional, not tight estimates.
- Sonnet only.
- The gold set is itself human work of unmeasured consistency. A gold/gold
  disagreement rate between raters would tell us what ceiling to expect, and we
  do not have one.
