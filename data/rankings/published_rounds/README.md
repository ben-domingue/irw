# Published rounds

One CSV per ranked-choice table: the rounds the jurisdiction published, copied as printed, so that `data/rankings/recount.py` can count the table under its rule set in `counting_rules.csv` and compare every figure (#3606). The Minneapolis files (88) are the round sheets and results pages the checks of #3166 used; the FairVote ones (387) are the county, city and state reports behind the replay of #3461. A table whose jurisdiction published no rounds has no file here.

## Format

The format of the Minneapolis rounds files of #3166: columns `round,item,votes`, items are the table's candidate codes (`c01`, no names), `(write-in)` and `(exhausted)`.

| row | meaning |
|---|---|
| `<round>,<code>,<votes>` | a candidate's tally at the start of the round, as printed (a candidate not listed has 0) |
| `<round>,(write-in),<votes>` | the write-in line; `<round>,(exhausted),<votes>` the exhausted ballots (optional) |
| `1,(source),<url>` | where the figures come from; one row per document, at least one |
| `1,(threshold),<votes>` | the threshold the source prints (optional) |
| `1,(elected:<code>),` | one row per elected candidate |
| `<round>,(lot:<code>),` | the candidate a draw settled in that round, where the count reaches a tie |
| `1,(first_marks),` | round 1 is the first marks as voted, from a page that prints no tabulation |
| `1,(seat:<k>),` | a sequential count whose source prints one page per seat: the rows after this one are seat `k`, rounds from 1 again |

A number is copied as printed (`4401`, `1234.5600`) and nothing is adjusted. Where the source prints a column that repeats the one before it, both are kept; `recount.py` folds such a column into the one before it on both sides, because a round is one in which votes are counted or moved (the ruling of 23 October 2026 on #3024).

One FairVote file records a printed write-in line under a candidate code: `rcv_burlington_20060307_mayor`, where the deposit's builder codes that spelling of the line as a candidate.

## Checks

`metadata/tests/test_rank_published_rounds.py` runs in CI and is offline: each file is well formed, has a source URL, and its table joins a design row and exactly one ranked rule set. It does not recount.

The recount runs by hand, because it needs the tables:

```
python3 data/rankings/fairvote_cvr.py build <raw dir> <table dir> <tables...>   # the FairVote tables
python3 data/rankings/recount.py --tables-dir <table dir> --all --results data/rankings/recount_results.csv
```

A difference is a warning with its first figure, never a failure. `recount_results.csv` is the result of one full run, one line per table. Its `status` is `match` (the winners and every figure), `match_by_lot` (the same, where the count reached a tie that the source's draw settles) or `warning`. `recount_reasons.csv` gives the reason where one is known, which is copied to a warning's `class` and `reason` columns; a warning with no row there is `unexplained`. The classes:

| class | meaning |
|---|---|
| `same_outcome_source_differs` | the source holds a different set of ballots than the deposit, or a rule the table cannot show; the winners match |
| `writein_pooling` | the source and the deposit pool or split the write-ins differently; the winners match |
| `official_page_error` | the source's own pages disagree with each other or with the jurisdiction's later statement |
| `rule_question` | the source follows a reading of the rules that no saved text settles |
| `seats_unknown` | the design row's `seats` is `unknown`, so the table is not counted |
| `unexplained` | a difference with no known reason |
