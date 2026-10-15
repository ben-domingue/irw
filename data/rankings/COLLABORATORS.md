# Building rankings tables: a brief for collaborators

This folder holds a draft IRW data family for rankings (ranked-choice ballots and other data where people put a fixed set of options in order). `README.md` is the standard; this page is how to help build it. Expect to need Python 3.10+ with `pandas`, a checkout of this repository, and about ten minutes per table once set up.

## What you are producing

For each file you take on, three things:

1. **A table** (`<table>.csv`) that passes the validator.
2. **Its design record row** in `design_tables.csv`, with the three fields a script cannot fill (`seats`, `write_in_allowed`, `candidate_order`) looked up from the jurisdiction's own election documentation, and `evidence` saying where.
3. **Its status** in `candidates.csv` set to `built`, or `held: <reason>` if something stops you.

The six tables in `examples/` are the answer key: Genola 2021 (sequential, small), Eastpointe 2019 (proportional, many duplicate marks), Takoma Park 2022 Ward 4 (one candidate, ballots marked twice), Alaska 2022 House District 10 (rich ballot-level columns), Burlington 2006 (older wave), New York City 2021 Council District 49 (large; the file lists ballots from outside the district). If your table disagrees in shape with these, the table is wrong before the standard is.

## The FairVote pool

Every FairVote file converts with one command, so the work is not writing code. Pick rows from `candidates.csv` whose status is `todo`, then:

```
python3 data/rankings/fairvote_cvr.py build raw/ out/ rcv_oakland_20101102_mayor rcv_oakland_20101102_council2
python3 -m irw_validate.rankings --design data/rankings/design_tables.csv out/*.csv
```

The first command downloads the source file into `raw/` (by Dataverse file id, from `fairvote_manifest.csv`), writes the table into `out/`, and writes or replaces the table's design row. The second checks the table against the standard and its design row. A passing table prints `passes`; anything else prints the rule it broke and what to do.

Then open `design_tables.csv`, find your rows, and fill `seats`, `write_in_allowed` and `candidate_order` from the jurisdiction's election page (a city clerk's results page, a state election division's RCV page, or the statute). Put the URL or document name in `evidence`. The same value usually holds for every contest of that jurisdiction and year, so it is efficient to take one jurisdiction-year at a time. Leave `unknown` where you cannot find it; never guess.

Finally set the `status` of each row in `candidates.csv` to `built` and open a pull request with the design and ledger rows (tables themselves stay out of git except the six examples; they go to Redivis later).

## Reporting a quirk

The deposits have no codebook, so the standard describes what has been seen, not what exists. When the script prints a `WARN` about a suspected token, or a file has a column the README's list does not mention, or the validator blocks a table that looks right to you, do not work around it. Post in the family's tracking issue, [#3024](https://github.com/ben-domingue/irw/issues/3024), with the file name, the exact value or column, and three example rows. Rulings get recorded in the README's rulings log, and `KNOWN_TOKENS` or the column list in `fairvote_cvr.py` gets updated in one PR, so the next person does not meet the same thing.

The things most likely to come up:

- A new spelling of write-in or overvote, or a token nobody has seen (`undervote` is already treated as a skip).
- A file whose `rank` columns are not `rank1..rankK` (none so far).
- A contest with more than 99 candidates (the code width goes to three digits automatically; just say so).
- A New York City style file where most ballots are empty because the contest was not on them: expected, see `n_ballots_eligible_est`.

## Other sources

Scottish council elections, Australian Senate preferences, the 2002 Irish electronic ballots and PrefLib each need their own script, and the first of each settles a rule (weighted profiles for Scotland, candidate-major pivoting for Australia). Those are a second batch and are listed as pools in `candidates.csv`; ask before starting one so the rule gets settled once.

## What not to do

- Do not store a candidate's name anywhere: not in the table, a note, a commit message or the design record. The codes are reproducible from the public file.
- Do not renumber positions, drop duplicate marks, or drop overvote rows. The table is the ballot as marked.
- Do not run any code that ships with a deposit, and do not edit `README.md` rules on your own; propose the change in the issue.
