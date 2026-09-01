# Auto-tagger scoring (issue #1721, sub-action 2.2)

Scores the `irw-auto-tag` skill against the gold set, per column.
Predictions were produced 2026-08-30. Reproduce with:

```bash
python3 score.py predictions_2026-08-30.json sample_2026-08-30.json
```

## Two scored runs, same predictions

`results_2026-08-30.txt` and `results_2026-09-01.txt` are the SAME 60 blind
predictions scored against gold before and after #1760. Nothing about the tagger
changed between them. What changed is what it was being marked against:

| column | 2026-08-30 | 2026-09-01 | why |
|---|---|---|---|
| `age_range` | 73.0% | **86.5%** | gold is now derived from each table's own `cov_age`; 10 of the 38 scored tables had their gold corrected |
| `sample` | 41.7% | **44.4%** | `General/non-specific` is the frame residual now, applied to both sides |
| others | unchanged | unchanged | |

**`age_range`'s 13.5-point gain is entirely gold.** The tagger was right more
often than the old gold said — which is the finding #1760 was opened to test,
now measured rather than argued. Cite the 2026-09-01 numbers; the earlier ones
scored against labels that have since been withdrawn.

## Partial credit, per atom

Exact match asks "did it name the whole answer". For a multi-select column whose
gold answer routinely has two or three facets, that is the wrong question:
naming two of three scores the same zero as naming something unrelated. So the
2026-09-01 run also reports micro-averaged per-atom precision and recall.

| column | exact | precision | recall | F1 |
|---|---|---|---|---|
| `primary_languages` | 90.9% | **100.0%** | 91.7% | 95.7% |
| `construct_type` | 64.9% | 80.0% | 69.6% | 74.4% |
| `child_age` | 75.0% | 80.0% | 100.0% | 88.9% |
| `sample` | 44.4% | 52.6% | 48.8% | 50.6% |

The two columns that look similar on exact match are not alike, and this is what
separates them. `construct_type` **under-tags**: when it names a facet it is
right 80% of the time, and it misses 30% of the facets gold holds. `sample` is
wrong in both directions at once, which is what a missing convention looks like
rather than a granularity disagreement.

`primary_languages` never names a language that is not there; it just misses
secondary ones. That is the least damaging failure shape available.

These are reported ALONGSIDE exact match, never instead of it — a bar set on F1
alone would pass a tagger that reliably names one facet of three.

**`sample` barely moved, and that is informative.** The frame rule removes a
contradiction from the gold but does not teach the tagger anything: these
predictions were written before the rule existed. The residual errors are now
diagnosable rather than mysterious — see `results_2026-09-01.txt`, where 8 of 20
are the tagger claiming `Representative` for a source that never claimed it, and
5 are it answering the SETTING facet when gold recorded the FRAME. Both are
things `vocab.md` now states, so `sample` needs the tagger re-run against the
current vocabulary before any shipping bar is set against it. 44.4% is a
pre-rule number.

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

### Set equality hides which way a multi-select column fails

`sample` and `construct_type` are scored on set equality, so predicting two of a
construct's three facets scores the same zero as naming an unrelated one. Those
two columns have similar exact-match rates and are not alike:

| column | n | exact | subset | superset | disjoint | shares >=1 atom |
|---|---|---|---|---|---|---|
| `primary_languages` | 33 | 90.9% | 3 | 0 | 0.0% | **100%** |
| `construct_type` | 37 | 64.9% | 5 | 2 | 16.2% | **83.8%** |
| `sample` | 36 | 41.7% | 3 | 0 | **50.0%** | 50.0% |

`construct_type` mostly disagrees about *granularity*: `preschool_sel_akt` gold
is `{Affective/mental health, Cognitive/educational, Developmental}` and the
tagger returned two of those three. `sample` mostly picks a *different category*:

    gold Targeted/specific     ->  pred Representative
    gold General/non-specific  ->  pred Representative
    gold Educational           ->  pred Targeted/specific

Is a national probability survey `General/non-specific` or `Representative`?
`vocab.md` lists the nine atoms and defines none of them. 2.1 (#1720) made these
vocabularies enforced but not defined, which is the same root cause as #1760.
So `sample`'s 41.7% is not a measure of model capability -- it measures asking a
model to match a convention nobody has written down.

Consequence for 2.3 (#1722): these two columns should not share a verdict. One
needs its vocabulary defined; the other mostly needs a scoring rule that credits
a partial match. Regenerate this table with `score.py`.
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

---

# The 2026-09-01 run (2.3, #1722)

Authorised by Ben to settle whether the #1760 rules make `sample` scorable and
whether the tagger reaches the population 2.3 would actually run on. Two arms,
eight blind subagents, ten tables each.

**Arm A — the same 38 tables, re-tagged against the rewritten `vocab.md`.**
Human gold exists, so this measures whether stating the setting/frame boundary
helps. `predictions_2026-09-01_rerun.json`, scored in
`results_rerun_2026-09-01.txt`.

**Arm B — 40 tables that have never been tagged**, `seed=1722`, ten each from
w2/w3/w4/w5 (`sample_untagged_2026-09-01.json`). No gold exists for six of the
seven columns, so this arm measures REACHABILITY and coverage — and real
accuracy for `age_range`, because #1760's derivation supplies ground truth from
each table's own `cov_age`. `score_untagged.py`,
`results_untagged_2026-09-01.txt`.

## The headline, and why the obvious reading of it is wrong

`sample`'s whole-cell exact match **fell**, 44.4% → 18.2%. It is an artifact.

Gold predates the two-facet split and answers one question: 12 of 34 gold rows
carry no frame value at all. The tagger, following the new rules, answers both —
it produced a frame value on **33 of 34** tables against **19 of 38** before. So
whole-cell matching now punishes it for filling a facet the key leaves blank,
and 15 of its 33 misses are supersets rather than wrong answers.

Scored per facet, on the tables where gold answered that facet
(`score_sample_facets.py`), the rules helped on both:

| facet | 2026-08-30 exact | 2026-09-01 exact | precision | recall |
|---|---|---|---|---|
| setting | 75.0% | **81.2%** | 87.5% | 87.5% |
| frame | 26.9% | **45.5%** | 52.4% | 47.8% |

Frame exact match nearly doubled. It is still the worst column in the corpus,
and the eight agents said why without being asked — see the amendment proposed
in `tags/decisions/1760_age_range_and_sample.md`.

## What Arm B found

- **75% of never-tagged tables were reached** (10 abstentions in 40), and **9 of
  the 10 failures are `fetch_failed`, not paywalls**.
- Reachability is not uniform: w3 100%, w4 90%, **w5 80%**, w2 **30%**. w5 had
  never been scored before and is the worst-*tagged* shard at 42.7% — this says
  its gap is not a reachability problem.
- w2's collapse is one fixable bug: figshare and Harvard Dataverse both answer
  `HTTP 202` (a pre-render/bot challenge) rather than content.
- **`age_range` scored 11/12 correct (91.7%) against derived ground truth** on
  the untagged population — the first accuracy figure in this project measured
  on the population the tagger would actually run on.
