# Rankings (`irw_rank`, `source = "rank"`)

Processing scripts and records for the **rankings** data family (`source = "rank"`): tables in which each respondent places a fixed set of options in order. The first source is FairVote's cast vote records from US ranked-choice elections; the layout is written to also hold Scottish, Australian and Irish ballot data and survey ranking questions.

**Status (2026-10-15).** Draft standard with seven reference tables (`examples/`: six FairVote contests and one Eurovision jury show); 18 Eurovision tables built from `eurovision_jurors.py`; 14 non-FairVote tables from the second batch (`voter_autrement.py`, `atsusaka_2024_rcv_survey.py`, `atsusaka_2025_ranking_questions.py`, `scottish_stv.py`; helpers in `rank_common.py`). The family is live: the Redivis dataset `irw_rank` (display name `IRW_rank`, reference id `93f5`; `IRW_RANK_DATASETS` in `metadata/redivis_config.R`, a shard list from day one) holds the first tables, both packages accept `source = "rank"` and ship a `rank_compress` helper (below), `red_up --dataset irw_rank` runs the validator and the design-row gate, `metadata/18_rankings.R` writes `rank_metadata`, and `metadata/02_biblio.R` reads the dictionary file. The site page (`rankings_standard.qmd`) is planned. Tables are built and checked locally with the two commands below, and a table counts as done when it passes the validator and has its rows in `design_tables.csv`, `candidates.csv` and the dictionary. The rulings that shaped this standard are logged at the end; the structural scouting that found the family is in `oneoff/structure-scouting-2026-10-13/`.

```
python3 data/rankings/fairvote_cvr.py build <raw dir> <out dir> <table> [...]   # build FairVote tables
python3 data/rankings/eurovision_jurors.py build <raw dir> <out dir> --all        # build Eurovision juror tables
python3 data/rankings/voter_autrement.py build <raw dir> <out dir> --all          # French voting experiments 2017/2022/2024
python3 data/rankings/atsusaka_2024_rcv_survey.py build <raw dir> <out dir> --all # Alaska/Oakland ballot-order surveys
python3 data/rankings/atsusaka_2025_ranking_questions.py build <raw dir> <out dir>
python3 data/rankings/scottish_stv.py build <raw dir> <out dir> 4_cands/aberdeen_2017_ward11.csv
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
- **Duplicate marks are kept as recorded.** A candidate marked at positions 1 and 2 gives two rows with the same `item` and different `resp`. Counting rules for duplicates differ by jurisdiction (most treat the later mark as a skip); the user applies theirs, the table does not. This is the one departure from one row per `id × item`, and it is the reason a core-style pivot of a rankings table needs care. The package helpers `irw_rank_compress()` (R) and `irw.rank_compress()` (Python) drop an item's later marks and renumber positions `1..k` within each ranking; the reserved values are never dropped.
- **One position, one row.** Within `id × task`, `resp` values are unique (an overvote is already one row).
- **`(overvote)`** is a row at the position where more than one candidate was marked; the source does not say which, so nothing else can be stored. **`(write-in)`** is a row with that item unless the source names the written-in candidate. Both are the one string in every table, like `(not shown)` in conjoint.
- **One contest per table**: one option set, one electorate, one date (ruling 4). A survey with several ranking questions is one table with `task` distinguishing them.

### Candidate codes

Candidate names are personal names in public records and are **not stored anywhere in the IRW** (Ben, 2026-10-15). Within a contest, the distinct names as printed in the source file are sorted case-insensitively (`key = (name.casefold(), name)`) and coded `c01`, `c02`, … with zero-padding to at least two digits (three when a contest has 100 or more candidates). The reserved values are excluded from the sort. Anyone holding the public source file can rebuild the mapping from this rule and the script; no name is written to the table, the script header, the design record or the dictionary. The validator (R4) refuses an item that looks like a personal name. Party, incumbency and other candidate attributes are not kept; if they are ever wanted they would be an item-level table built from the same rule, not names in `item`.

Options that are not people (policies, schools, products in a survey ranking) are stored as the text shown, as in other families. A party list in a list election is coded like a candidate (Voter Autrement 2024: five of the 38 official list labels carry a politician's name), and a covariate that names a candidate (a reported official vote) carries the same code as `item`.

## Intake rules

- **Licence:** CC0, CC BY, CC BY-SA or CC BY-NC, as elsewhere in IRW (a no-derivatives licence is not accepted). FairVote's three collections are CC0 1.0 throughout. Public election records are public records in their own right; the deposit's licence is what the dictionary carries.
- **At least 50 ballots with marks** per table. The core floor is 100 respondents; rankings use 50 rankers because a ranking over three or more objects contributes several positions, so 50 rankings carry at least as much information as 100 single responses on a short instrument (Ben, 2026-10-15). The validator warns below 50.
- **No voter identifiers.** A source's ballot ID or row index is dropped at re-keying.
- **Table names:** election tables are `rcv_<jurisdiction>_<yyyymmdd>_<office>`, lowercase, at most 40 characters, with the abbreviations in `fairvote_cvr.py` (`nyc`, `sf`, `mpls`, `council`, `boe`, `hd`, `bp`, …). Other rankings use the usual `author_year_topic`.
- **Size.** The largest FairVote files (New York City, San Francisco) are 100–125 MB wide and 2–3× that long, so they need the token upload path.
- **Uploading.** `red_up --dataset irw_rank <dir>`: a rankings table has `id`/`item`/`resp`, so only the destination tells `red_up` to run `irw_validate.rankings` (R1–R8 against `design_tables.csv`) instead of the core validator; a table with no design row is refused. New tables go to the newest shard (`RANK_DEFAULT` in `red_up/targets.py`).
- **Downloads are untrusted.** Scripts read only the files named in their header; nothing shipped with a deposit is executed.

## Records kept for every table

- **A script**, or for FairVote the table's row in `fairvote_manifest.csv` (the one script `fairvote_cvr.py` builds every FairVote table from its manifest row). A non-FairVote table gets its own script with the usual IRW header: citation, deposit DOI and licence, files read, what was dropped, and any count discrepancy with the source.
- **A design record:** one row in `design_tables.csv` (below). `fairvote_cvr.py` writes it; other scripts append theirs.
- **A dictionary row,** staged with `automated_finding/stage_dict_row.py --source rank`, which writes to `dictionary_auto_rank.csv`. `metadata/02_biblio.R` reads that file alone (no sheet, as conjoint) and publishes `rank_biblio`.
- **A row in `candidates.csv`,** the ledger of every file or deposit considered (claims and quirks go to tracking issue #3024), with status `todo`, `built`, `uploaded` or `held: <reason>`.
- **A processing note** in `metadata/data_notes.csv`, once the table is on Redivis.

## Design record (`design_tables.csv`)

The tables share a layout but not a meaning: how many positions a ballot offered, how many seats were filled and which counting rule applied all change what a ranking means. One row per table; when no source states a fact the value is `unknown`, never a guess. `metadata/18_rankings.R` joins every column but `evidence` into `rank_metadata` (the record's `n_duplicate_marks` as `design_n_duplicate_marks`, beside the live count) and reports a record whose counts disagree with the live table.

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
| floor | fewer than 50 ids warns (the rankings floor; core uses 100) |

It also reports duplicate marks, ballots with a gap, and the marks-per-ballot distribution. (R5 is reserved for the ballot-weight rule, below.)

## Source formats known so far

- **Position-major** (FairVote): one row per ballot, `rank1..rankK` holding names or tokens. Tokens observed: `skipped`, `overvote`, `writein` / `Write-in` / `Write-In`; `undervote` is treated as a skip. Any other lowercase single-word value is reported by the script as a suspected token and should be added to `KNOWN_TOKENS` after checking. Ballot-level columns seen: `ballotID`, `Index`, `Cast.Vote.Record` (row keys, dropped); `precinct(s)`, `ward`, `Ballot.Style`, `ballot_type`, `countingGroup`, `district`, `districtType`, `votingLocation`, `tally_type` (kept as `cov_`); `source_file` (dropped).
- **Candidate-major** (Australian Electoral Commission Senate formal preferences): one row per ballot, one column per candidate holding the preference number. Same layout after pivoting; a script for it is a second batch.
- **Jury-major** (MIRoVision Eurovision jurors): one row per voting jury × entry, one column per juror holding the rank. `eurovision_jurors.py` pivots it; a juror never ranks their own country's entry, so that entry is simply absent from their rows (not a skip).
- **Weighted profiles** (Scottish council elections, PrefLib): one row per distinct ranking with a count. **R5 (proposed 2026-10-15, awaiting Ben):** expand to one `id` per ballot, no weight column. `id` is one ballot everywhere else in the family, `n_ballots_with_marks` must equal the id count (R8), and a council ward is at most a few tens of thousands of ballots, so the cost is rows, not meaning. `scottish_stv.py` does this; the first table (`rcv_aberdeen_20170504_ward11`, 64 distinct rankings, 6,116 ballots) is built and held until the ruling and the licence are settled.
- **Candidate-major scored** (Voter Autrement 2017): one row per participant, one column per candidate holding a score 11 = first .. 1 = last, blank = not ranked; position = 12 - score. **Candidate-major ranked** (Voter Autrement 2022): the same with the rank itself, 0 = not ranked.
- **Ranking strings** (Voter Autrement 2024): `"1. LIST ; 2. LIST ; ..."` in one cell, split on `" ; "`; a two-choice file (`first_choice`, `second_choice`) is a two-position ranking.
- **Survey rank widgets** (Qualtrics, YouGov .sav): one column per option holding its position, not ranked as blank, `-99` or NaN; a `_DO` column or `*_row_rnd` variable gives the randomised display order (kept as `trial_display_order` when per respondent). The widget forces a permutation, so a repeated position is a data error, not an overvote: those rankings are dropped and counted in the design record's `evidence` (12 of 550 in one Atsusaka & Kim 2025 question).

## Using the tables

- A person × item pivot is not safe without first handling duplicate marks and gaps: run `irw_rank_compress()` / `irw.rank_compress()` first. `irw_fetch(dedup = TRUE)` and `irw.fetch(dedup=True)` leave rankings tables alone for the same reason.
- Plackett–Luce and Mallows fits want each ballot's ordered list of items by `resp`; overvote rows and write-in rows are usually dropped first.
- Exhaustion and truncation analyses need `n_positions` and `n_candidates` from the design record, and `n_ballots_with_marks` as the denominator, not `n_ballots_cast`.

## Rulings log

- **2026-10-15 (Ben).** (1) Duplicate marks are kept as recorded, not collapsed. (2) No renumbering after skips; a package helper will compress on request. (3) A new family, not a layout inside competitions. (4) One table per contest. (5) FairVote first; the second batch should be an international pool (Scotland or Australia) rather than the survey deposits, because the cross-source harmonisation is what the family is for. Candidate names are not stored; alphabetical codes. The Redivis dataset, packages and site are deferred until there are enough tables. Non-English ballot data is a separate scouting task.
- **2026-10-15 (Ben), later.** Options that are not people keep their label as shown (country codes, song or policy text); only personal names are coded. Eurovision per-juror rankings are in scope: the family is about rankings, not the objects ranked. SUSHI is skipped (its originator forbids redistribution). Scouting memos: `oneoff/rankings-nonenglish-scouting-2026-10-15/`.
- **2026-10-15 (second batch, agent; rulings owed).** Built from the non-FairVote pool so as not to overlap the collaborators' FairVote slices (#3024): ten Voter Autrement tables (ODbL 1.0, **held**: ODbL is not on the intake list above), three Atsusaka survey tables (CC0, uploaded), one Scottish ward (**held**: repository states no licence; R5 expansion proposed). Survey experiments get `method = survey`, `seats = na`, `date` = the election they ran alongside (or the fielding month). A task-level `trial_display_order` records a per-respondent randomised ballot order as codes joined by `|`.
- **2026-10-15 (Ben), floor.** The id floor for this family is 50 rankers, not the core 100, because each ranker over three or more objects contributes several positions. The three Eurovision semi-finals held under the old floor (2021 sf1, 2022 sf1, 2022 sf2: 95, 95 and 75 jurors) were built and uploaded under this rule.
