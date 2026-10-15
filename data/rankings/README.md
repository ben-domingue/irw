# Rankings (`irw_rankings`, draft family)

Processing scripts and records for the **rankings** data family (`source = "rank"`): tables in which each respondent places a fixed set of options in order. The first source is FairVote's cast vote records from US ranked-choice elections; the layout is written to also hold Scottish, Australian and Irish ballot data and survey ranking questions.

**Status (2026-10-15).** Draft standard with seven reference tables (`examples/`: six FairVote contests and one Eurovision jury show); 15 Eurovision tables built from `eurovision_jurors.py` (three more held under the 100-id floor). The family has no Redivis dataset yet, and nothing here is reachable from the packages or the site: Ben's ruling is to register the dataset, the package `source = "rank"` and the site page together once a decent number of tables exist. Until then, tables are built and checked locally with the two commands below, and a table counts as done when it passes the validator and has its rows in `design_tables.csv`, `candidates.csv` and the dictionary. The rulings that shaped this standard are logged at the end; the structural scouting that found the family is in `oneoff/structure-scouting-2026-10-13/`.

```
python3 data/rankings/fairvote_cvr.py build <raw dir> <out dir> <table> [...]   # build FairVote tables
python3 data/rankings/eurovision_jurors.py build <raw dir> <out dir> --all        # build Eurovision juror tables
python3 -m irw_validate.rankings --design data/rankings/design_tables.csv <out dir>/*.csv
```

## Scope

A table belongs here when each respondent orders a fixed set of named options: ranked-choice ballots (instant-runoff, single transferable vote, sequential), rank-order lists (school or job choice), survey questions that ask for a ranking, and judging panels where each judge ranks every entry (Eurovision jurors). The family is defined by the act of ranking, not by what is ranked (Ben, 2026-10-15). The options are the same things for every respondent and each appears once per ranking. The response is a **position**, not a score.

Not here: a comparison between two fixed things (competitions family); profiles assembled at random from attributes (conjoint family); a Q-sort, where positions are forced into a fixed shape with ties (a cousin, not in scope); a single pick from a list (core or nominal). Best-worst scaling belongs with the conjoint discrete-choice rules (#2978).

## Layout

One row per respondent × task × marked position. The core column names are kept so core tooling reads the table, but `resp` is a rank.

| column | |
|---|---|
| `id` | the ballot or respondent, re-keyed 1..n in source order. Never a voter identifier (cast vote records have none; a survey's panel ID is dropped). |
| `task` | which ranking, when a respondent gave more than one (several contests on one ballot, several ranking questions). `1` throughout a one-contest table. |
| `item` | the option ranked: a **candidate code** (`c01`, `c02`, …, below), the reserved values `(write-in)` and `(overvote)`, or, for options that are not people, the option text as shown. |
| `resp` | the position marked, `1` = first choice, **as recorded**. Positions are not renumbered after a skip: a ballot marked at positions 1 and 3 keeps `resp` 1 and 3. |
| `cov_<name>` | ballot- or respondent-level columns from the source, as text, repeated on every row of the ballot: `cov_precinct`, `cov_ballot_style`, `cov_counting_group`, `cov_district`, `cov_voting_location`. |
| `trial_<name>` | task-level details, if any (question order, survey arm). |

Rules:

- **Skipped positions are not rows.** A skip is visible as a gap in `resp`. A ballot with no marks has no rows; the design record keeps `n_ballots_cast` and `n_ballots_with_marks` so denominators survive.
- **Duplicate marks are kept as recorded.** A candidate marked at positions 1 and 2 gives two rows with the same `item` and different `resp`. Counting rules for duplicates differ by jurisdiction (most treat the later mark as a skip); the user applies theirs, the table does not. This is the one departure from one row per `id × item`, and it is the reason a core-style pivot of a rankings table needs care. A package helper that compresses positions and drops repeated marks is planned with the package work.
- **One position, one row.** Within `id × task`, `resp` values are unique (an overvote is already one row).
- **`(overvote)`** is a row at the position where more than one candidate was marked; the source does not say which, so nothing else can be stored. **`(write-in)`** is a row with that item unless the source names the written-in candidate. Both are the one string in every table, like `(not shown)` in conjoint.
- **One contest per table**: one option set, one electorate, one date (ruling 4). A survey with several ranking questions is one table with `task` distinguishing them.

### Candidate codes

Candidate names are personal names in public records and are **not stored anywhere in the IRW** (Ben, 2026-10-15). Within a contest, the distinct names as printed in the source file are sorted case-insensitively (`key = (name.casefold(), name)`) and coded `c01`, `c02`, … with zero-padding to at least two digits (three when a contest has 100 or more candidates). The reserved values are excluded from the sort. Anyone holding the public source file can rebuild the mapping from this rule and the script; no name is written to the table, the script header, the design record or the dictionary. The validator (R4) refuses an item that looks like a personal name. Party, incumbency and other candidate attributes are not kept; if they are ever wanted they would be an item-level table built from the same rule, not names in `item`.

Options that are not people (policies, schools, products in a survey ranking) are stored as the text shown, as in other families.

## Intake rules

- **Licence:** CC0, CC BY, CC BY-SA or CC BY-NC, as elsewhere in IRW (a no-derivatives licence is not accepted). FairVote's three collections are CC0 1.0 throughout. Public election records are public records in their own right; the deposit's licence is what the dictionary carries.
- **At least 100 ballots with marks** per table (the 100-respondent floor).
- **No voter identifiers.** A source's ballot ID or row index is dropped at re-keying.
- **Table names:** election tables are `rcv_<jurisdiction>_<yyyymmdd>_<office>`, lowercase, at most 40 characters, with the abbreviations in `fairvote_cvr.py` (`nyc`, `sf`, `mpls`, `council`, `boe`, `hd`, `bp`, …). Other rankings use the usual `author_year_topic`.
- **Size.** The largest FairVote files (New York City, San Francisco) are 100–125 MB wide and 2–3× that long, so they need the token upload path when the family goes to Redivis.
- **Downloads are untrusted.** Scripts read only the files named in their header; nothing shipped with a deposit is executed.

## Records kept for every table

- **A script**, or for FairVote the table's row in `fairvote_manifest.csv` (the one script `fairvote_cvr.py` builds every FairVote table from its manifest row). A non-FairVote table gets its own script with the usual IRW header: citation, deposit DOI and licence, files read, what was dropped, and any count discrepancy with the source.
- **A design record:** one row in `design_tables.csv` (below). `fairvote_cvr.py` writes it; other scripts append theirs.
- **A dictionary row,** staged with `automated_finding/stage_dict_row.py --source rank`, which writes to `dictionary_auto_rank.csv`. `metadata/02_biblio.R` does not read that file yet (deferred with the Redivis work).
- **A row in `candidates.csv`,** the ledger of every file or deposit considered (claims and quirks go to tracking issue #3024), with status `todo`, `built`, `uploaded` or `held: <reason>`.
- **A processing note** in `metadata/data_notes.csv` is deferred until the tables are on Redivis.

## Design record (`design_tables.csv`)

The tables share a layout but not a meaning: how many positions a ballot offered, how many seats were filled and which counting rule applied all change what a ranking means. One row per table; when no source states a fact the value is `unknown`, never a guess.

| column | |
|---|---|
| `source_file`, `collection` | the file converted and the deposit DOI |
| `jurisdiction`, `date`, `office` | from the file name; `date` ISO |
| `method` | `irv` (single winner), `stv` (proportional, multi-winner), `sequential` (multi-winner by repeated IRV), `survey`, `rank_order_list`, `jury` (a judging panel), or `unknown`. For FairVote, from which collection the file sits in. |
| `seats` | number of winners; `unknown` until filled from the jurisdiction's own documentation; `na` for a jury ranking |
| `n_positions` | positions offered on the ballot (K in `rank1..rankK`) |
| `n_candidates` | distinct candidate codes, excluding reserved values |
| `n_ballots_cast` | rows in the source file |
| `n_ballots_eligible_est` | ballots whose precinct has at least one marked ballot; equals `n_ballots_cast` when the file has no precinct column. New York City's exports list every ballot of the primary, including precincts where the contest was not on the ballot (District 49: 213 of 312 precincts have no marked ballot), so `n_ballots_cast` overstates the electorate there. The estimate is a floor on undervoting, not a turnout figure: precincts can straddle districts. |
| `n_ballots_with_marks` | ballots with at least one row; equals the table's number of ids |
| `n_duplicate_marks`, `n_overvotes`, `n_writeins` | counts of those rows |
| `write_in_allowed` | `yes` when the file has write-in marks, else `unknown` until documented |
| `candidate_order` | `fixed`, `rotated` (ballot order randomised across styles), or `unknown` |
| `evidence` | where each value came from |

`seats`, `write_in_allowed` and `candidate_order` are the fields that need a person: they come from the jurisdiction's election page or statute, and the same value usually holds for every contest of one jurisdiction and year. That is the collaborator task (`COLLABORATORS.md`).

## Validator (`irw_validate/rankings.py`)

| rule | |
|---|---|
| R1 | `id`, `task`, `item`, `resp` present, none missing |
| R2 | `resp` and `task` are positive integers |
| R3 | within `id × task`, no repeated `resp` |
| R4 | `item` is non-empty; the only parenthesised values are `(write-in)` and `(overvote)`; candidate codes have one width; no value looks like a personal name |
| R6 | columns are the four above plus `cov_` and `trial_`; a `cov_` column is constant within a ballot |
| R7 | with `--design`: a design row exists and no `resp` exceeds `n_positions` |
| R8 | with `--design`: the table's candidate-code count and id count match `n_candidates` and `n_ballots_with_marks` |
| floor | fewer than 100 ids warns |

It also reports duplicate marks, ballots with a gap, and the marks-per-ballot distribution. (R5 is reserved for the ballot-weight rule, below.)

## Source formats known so far

- **Position-major** (FairVote): one row per ballot, `rank1..rankK` holding names or tokens. Tokens observed: `skipped`, `overvote`, `writein` / `Write-in` / `Write-In`; `undervote` is treated as a skip. Any other lowercase single-word value is reported by the script as a suspected token and should be added to `KNOWN_TOKENS` after checking. Ballot-level columns seen: `ballotID`, `Index`, `Cast.Vote.Record` (row keys, dropped); `precinct(s)`, `ward`, `Ballot.Style`, `ballot_type`, `countingGroup`, `district`, `districtType`, `votingLocation`, `tally_type` (kept as `cov_`); `source_file` (dropped).
- **Candidate-major** (Australian Electoral Commission Senate formal preferences): one row per ballot, one column per candidate holding the preference number. Same layout after pivoting; a script for it is a second batch.
- **Jury-major** (MIRoVision Eurovision jurors): one row per voting jury × entry, one column per juror holding the rank. `eurovision_jurors.py` pivots it; a juror never ranks their own country's entry, so that entry is simply absent from their rows (not a skip).
- **Weighted profiles** (Scottish council elections, PrefLib): one row per distinct ranking with a count. **Open (R5):** expand to one `id` per ballot, or carry a `cov_weight`. Not ruled yet; the first Scottish table settles it.

## Using the tables

- A person × item pivot is not safe without first handling duplicate marks and gaps; a helper is planned with the package work.
- Plackett–Luce and Mallows fits want each ballot's ordered list of items by `resp`; overvote rows and write-in rows are usually dropped first.
- Exhaustion and truncation analyses need `n_positions` and `n_candidates` from the design record, and `n_ballots_with_marks` as the denominator, not `n_ballots_cast`.

## Rulings log

- **2026-10-15 (Ben).** (1) Duplicate marks are kept as recorded, not collapsed. (2) No renumbering after skips; a package helper will compress on request. (3) A new family, not a layout inside competitions. (4) One table per contest. (5) FairVote first; the second batch should be an international pool (Scotland or Australia) rather than the survey deposits, because the cross-source harmonisation is what the family is for. Candidate names are not stored; alphabetical codes. The Redivis dataset, packages and site are deferred until there are enough tables. Non-English ballot data is a separate scouting task.
- **2026-10-15 (Ben), later.** Options that are not people keep their label as shown (country codes, song or policy text); only personal names are coded. Eurovision per-juror rankings are in scope: the family is about rankings, not the objects ranked. SUSHI is skipped (its originator forbids redistribution). Scouting memos: `oneoff/rankings-nonenglish-scouting-2026-10-15/`.
