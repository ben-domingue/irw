# Minneapolis ranked-choice tables: build and check scripts

These four scripts repeat the steps that built and checked the Minneapolis tables in `data/rankings/` (2009, 2013, 2017, 2020 special, 2021, 2023), except that checks 2 and 4 below do not fully cover 2009. The fifth, `recount.py`, has moved to `data/rankings/recount.py` (#3606), where one counter reads every rule set of `counting_rules.csv`. They are the general form of the tools used for the pull requests; on the 2023 slice they give the same tables, ballot comparison, totals and recount as the first run. They are handed over so that anyone can repeat the work for one election, or check a table once more.

**Location.** The maintainer asked for these scripts in `data/rankings/` (#3060). They sit in their own folder so that this README does not clash with `data/rankings/README.md`; they can move next to `fairvote_cvr.py` if that is preferred.

Each script is self-contained, as the repository's contributor notes ask: no shared module, one purpose per file, a `##` header comment that says what it reads and writes. They need Python 3.11 or newer and the standard library. The validator step of `build_tables.py` also needs `pandas`, because it runs `irw_validate.rankings`. Only `compare_city_cvr.py` with `--format xlsx` needs `openpyxl`.

## No names

No script holds a candidate name. Tables carry codes (`c01`, `c02`, ...). Where a script has to read names, it reads them from the public FairVote file at run time (`compare_city_cvr.py` also reads the city's file and the spelling map you give it) and prints no name unless you ask. `compare_city_cvr.py` shows only a count per rule for name notes, and prints name strings and sample ballots only with `--show N`. Never paste `--show` output into public text. The city's results enter as codes. Two things need name spellings and stay outside this repository: parsing the city's own result documents into the official CSV, and the spelling map for the city's cast vote record. Both are files you make and keep yourself.

## The scripts

| script | what it does | reads | writes |
|---|---|---|---|
| `build_tables.py` | Runs `fairvote_cvr.py build` for one election, checks every raw file against the manifest, runs `irw_validate.rankings` on the tables | `fairvote_manifest.csv`, raw files (downloaded if missing) | tables, design rows (through `fairvote_cvr.py`) |
| `compare_city_cvr.py` | Compares a FairVote raw file with the city's own cast vote record, ballot by ballot, as a multiset | one raw file, one city file, optional spelling map | nothing (a report) |
| `ballot_totals.py` | Counts ballots, ballots with marks, overvotes, duplicate marks and write-ins in the raw files; compares with the design rows and with the total the city prints | raw files, `design_tables.csv` | nothing (a report) |
| `../recount.py` | Counts the table a second time under its rule set and compares every round with the city's official results. Needs `seats` filled in the design rows (`fill_design_fields.py`) | tables, `design_tables.csv` (with `seats`), `counting_rules.csv`, `../published_rounds/<table>.csv` | a results file (optional JSON) |
| `fill_design_fields.py` | Fills `seats`, `write_in_allowed`, `candidate_order` and `evidence` in `design_tables.csv` from an evidence file, after every quote has been found in a saved copy of its source | `design_tables.csv`, evidence file, saved sources | `design_tables.csv` |

Every script but the recount exits 0 when its checks pass, 1 when something differs, and 2 on bad input; the recount exits 0 when every table was counted (a difference is a warning with its first figure, not a failure) and 2 on bad input. Run `--help` for the options.

## Repeat one election end to end

The example is the 2023 City Council election (13 wards). Run from the repository root, ideally in a scratch copy, because a build rewrites `design_tables.csv`.

```
M=data/rankings/minneapolis

# 1. Build the tables and check the sources and the validator
python3 $M/build_tables.py raw out --prefix rcv_mpls_20231107_

# 2. The ballots in each raw file against the city's cast vote record (one contest per call)
python3 $M/compare_city_cvr.py --raw raw/Minneapolis_20231107_CityCouncilW6.tab \
    --city <city cast vote record for Ward 6>.csv --empty-is-skip

# 3. Ballot counts against the design rows and the totals the city prints
python3 $M/ballot_totals.py --design data/rankings/design_tables.csv --raw-dir raw \
    --prefix rcv_mpls_20231107_ --expect rcv_mpls_20231107_councilw6=5186

# 4. Human fields of the design rows, with every quote checked against the saved sources.
#    Do this before the recount: the build leaves seats as unknown and the recount reads it.
#    The evidence file is written by hand, in the format given in the header of fill_design_fields.py.
#    The sources folder holds the saved pages and PDFs the quotes come from.
python3 $M/fill_design_fields.py --design data/rankings/design_tables.csv \
    --evidence <slice>.evidence.toml --sources <folder of saved sources>

# 5. Recount against the city's official results (one CSV of codes per table in data/rankings/published_rounds/)
python3 data/rankings/recount.py --tables-dir out --prefix rcv_mpls_20231107_
```

The rule set is the one the table's design row joins in `counting_rules.csv`: `mpls_2009` for 2009, `mpls_2013` for 2013, `mpls_2015plus` for 2017 and later. Each of those rows names the ordinance sections and the official page of the text.

## The official CSV

The city's rounds are one small CSV per table in `data/rankings/published_rounds/`, with the columns `round,item,votes` and a `(source)` row with the URL of the city document it is written from. The format, with the rows for the elected, the draw and first-choice pages, is in the header of `data/rankings/recount.py` and in `data/rankings/published_rounds/README.md`. Nothing is adjusted when the CSV is made: a number is copied as printed.

## What the scripts check

The numbering follows the checks used for every slice. Checks that need a person, a second program or the repository's own CI are listed as outside this folder.

| check | in plain words | where |
|---|---|---|
| 1 source integrity | Each raw file has the size the manifest gives. Its sha256 is recorded so a later run can show it is the same file. | `build_tables.py` |
| 2 city cast vote record | The FairVote file and the city's own file hold the same ballots, after the documented spelling and token rules. Every string that needed a rule is listed. Not for 2009: the script does not read the city's 2009 sheets (`.xls`, typed write-ins). | `compare_city_cvr.py` |
| 3 ballot totals | The number of ballots equals the total the city prints, and the counts equal the design row. | `ballot_totals.py` |
| 4 recount | Counting the table under the ordinance gives the city's number in every round, including exhausted ballots and the threshold, and the same winners. For 2009 the last round follows the city's sheet (the final defeat moves no votes), so the ordinance text's reading of that step is not tested here; in `(first_marks)` mode the threshold is not compared. | `../recount.py` |
| 5, 6 second count | A second counting program, written from the ordinance text without sight of the first program's code, gives the same tallies in every round (2009: except the last round of Board of Estimate and Taxation and Park Board at-large). | outside this folder |
| 7 rule sensitivity | Replaying the same table under another rule set shows which rules the ballots actually used. Run `../recount.py` with `--rules` naming another rule set. | `../recount.py` |
| 8 validator | `irw_validate.rankings` passes with the design rows. | `build_tables.py` |
| 9 slice gate | Only the four allowed files change, every other row equals upstream, no name or local path is in the diff. | outside this folder |
| 10 quotes | Every quoted source text in the design rows is found in a saved copy of the source. | `fill_design_fields.py` |
| 11 repository tests | The Python steps of `.github/workflows/tests.yml`. | repository CI |
| 12 fresh rebuild | A rebuild in a scratch copy from freshly downloaded files gives byte-identical tables and design counts. Compare the sha256 of the tables. | `build_tables.py`, then `sha256sum` |
| 13 review | A second person re-derives a sample of values and reads the diff. | outside this folder |

## Rules of the recount

The count follows Minneapolis Code of Ordinances chapter 167, sections 167.60 (one seat) and 167.70 (several seats). The three rule sets (`mpls_2009`, `mpls_2013`, `mpls_2015plus` in `counting_rules.csv`, each with its citation there) differ in these points:

- what an overvote, a skipped position or a repeated candidate does to a ballot (in 2009 an overvote, a repeated candidate and a run of more than one skipped position exhaust the ballot; later all three are passed over);
- which batch eliminations apply (test 1 from 2009, test 2 from 2015);
- whether undeclared write-ins are defeated first and count toward test 1 (from 2013);
- whether a group whose total equals the next higher total is defeated (2009 only), and whether two remaining candidates end a one-seat count (2009 only);
- for several seats, the surplus fraction and each transfer value are truncated to four decimals.

A tie is never broken silently. The count stops, flags `TIE` and `UNRESOLVED_TIE`, and the table is a warning. To follow a draw the city held, add a `(lot:<code>)` row to the official CSV.

On the 2009 data, three contests differ from the city's sheets: Board of Estimate and Taxation by one ballot and Park Board at-large by two, both holding write-ins that the FairVote file merges into one token, and Ward 13, where the city's results page disagrees with its own sheet (10 write-ins against 6). The reasons are in item 7 and the Ward 13 note of the 2009 comment on #3024. The script reports the differences and adjusts nothing.
