#!/usr/bin/env python3
##Minneapolis ranked-choice recount: count a rankings table a second time and compare it with the city's certified results.
##Source of the rules: Minneapolis Code of Ordinances ch. 167 (ranked-choice voting). Each rule set below names the
##ordinance sections it follows and the official page of the text. The count reads only the IRW table (candidate codes,
##no names) and the city's results written as a small CSV of codes (format below).
##
##Usage:
##  python3 recount.py --rules mpls_2015plus --design ../design_tables.csv --tables-dir <dir> --official-dir <dir> \
##      [--prefix rcv_mpls_20231107_ | TABLE ...] [--no-truncation] [--json-out <dir>]
##
##Per table the script reads <tables-dir>/<table>.csv and <official-dir>/<table>.csv. The number of seats is the
##`seats` column of the table's design row (it must be filled in). One run uses one rule set, the one in force that year:
##  mpls_2009      2008-Or-028 as amended by 2009-Or-102
##  mpls_2013      2013-Or-055, before 2015-Or-065
##  mpls_2015plus  2015-Or-065 and later (sections 167.20, 167.60 and 167.70 are the same through 2023)
##
##Official CSV: columns round,item,votes, written from the city's round sheets or results page.
##  <round>,<code>,<votes>      a candidate's tally at the START of the round, as printed (transfers show in the next round)
##  <round>,(write-in),<votes>  undeclared write-ins;  <round>,(exhausted),<votes>  exhausted ballots (optional)
##  1,(threshold),<votes>       the threshold printed by the city (optional)
##  1,(elected:<code>),         one row per elected candidate
##  <round>,(lot:<code>),       the candidate a city draw settled in that round (see Ties)
##  1,(first_marks),            round 1 comes from a results page that prints first choices only (see First marks)
##A candidate that is not listed in a round has 0 votes there. A tally is compared at four decimals: ours is truncated to
##four places, as the ordinance truncates ("ignoring any remainder"), and must equal the printed number.
##
##What is compared: the number of rounds; every candidate, (write-in) and (exhausted, when the CSV has it) in every round;
##the threshold (when given); the set of elected candidates (the order of election is not compared).
##First marks. A results page counts a ballot for its mark in first place as voted. A ballot whose first mark is an
##overvote or blank is left out of the page even when it counts for a later choice. Round 1 of the count here uses the
##first valid choice, as the round sheets do. With the (first_marks) row, round 1 is compared with the marks in first place
##as voted, the count must end in round 1, and the winners must agree. The threshold row is not used in this mode.
##Ties. A tie for fewest votes, or for the largest surplus, is never broken silently. The count stops, prints
##TIE and UNRESOLVED_TIE, and the later rounds then differ. To follow the city's draw, add the (lot:<code>) row of that round.
##
##A table is read as ballots: one ballot is one id. The item at position p is the row with resp = p. A position with no
##row is a skipped ranking. (overvote) is an overvote. A repeated item stays where it was marked. (write-in) is an ordinary
##code. A ballot with no rows is not in the table and has no valid first choice, so the count leaves it out anyway.
##
##Multiple seats (STV) use exact fractions, and the surplus fraction and each transfer value are truncated to four
##decimals. With more than one seat the script also repeats the count without truncation and says whether that matches.
##Exit code: 0 every table matches, 1 something differs or a tie was not settled, 2 bad input.
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from dataclasses import dataclass, field, replace
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from math import floor
from pathlib import Path

OVERVOTE = "(overvote)"
WRITE_IN = "(write-in)"
EXHAUSTED = "(exhausted)"


## Rule sets ----------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class RuleSet:
    id: str
    overvote: str                   # "pass_over" or "exhaust": what a ballot does at an overvoted position
    skipped: str                    # the same, for a skipped (blank) position
    max_consecutive_skips: int | None  # a blank run longer than this exhausts the ballot; None = no limit
    duplicate: str                  # the same, for a candidate already marked higher on the ballot
    batch_tests: frozenset          # 1 = next higher current vote total, 2 = sum of all ranked-choice votes
    batch1_equal_defeats: bool      # test 1: a group whose reach EQUALS the next higher total is defeated (2009)
    writeins_defeated_after_round1: bool  # undeclared write-ins are defeated first; their votes count in test 1
    surplus_decimals: int | None    # surplus fraction and transfer value are truncated to this many places
    citation: str
    two_remain_elects_leader: bool = False  # one seat: when two remain, the one with more votes is elected (2009)


_PASS = dict(overvote="pass_over", skipped="pass_over", max_consecutive_skips=None, duplicate="pass_over")

RULE_SETS = {
    "mpls_2009": RuleSet(
        "mpls_2009", overvote="exhaust", skipped="pass_over", max_consecutive_skips=1, duplicate="exhaust",
        batch_tests=frozenset({1}), batch1_equal_defeats=True, writeins_defeated_after_round1=False,
        surplus_decimals=4, two_remain_elects_leader=True,
        citation="Minneapolis Code of Ordinances ch. 167, added by 2008-Or-028 (18 Apr 2008) and amended by "
                 "2009-Or-102 (2 Oct 2009): 167.20 (definitions), 167.50(c), 167.60(a)(1)b, c and d and (a)(2), 167.70(a)(1)c, d and e and (a)(2). "
                 "https://lims.minneapolismn.gov/download/GetArchivedAttachment/302817 and "
                 "https://lims.minneapolismn.gov/download/GetArchivedAttachment/302997",
    ),
    "mpls_2013": RuleSet(
        "mpls_2013", **_PASS,
        batch_tests=frozenset({1}), batch1_equal_defeats=False, writeins_defeated_after_round1=True,
        surplus_decimals=4,
        citation="Minneapolis Code of Ordinances ch. 167 as amended by 2013-Or-055 (24 May 2013), before 2015-Or-065: "
                 "167.20, 167.45, 167.60(b), (c)(1)b, c and d and (c)(2), 167.70(b), (c)(1)c, d and e and (c)(2). "
                 "https://lims.minneapolismn.gov/download/GetArchivedAttachment/303473 and "
                 "https://library.municode.com/mn/minneapolis/codes/code_of_ordinances/247847?nodeId=COOR_TIT8.5EL_CH167MUELRUCO",
    ),
    "mpls_2015plus": RuleSet(
        "mpls_2015plus", **_PASS,
        batch_tests=frozenset({1, 2}), batch1_equal_defeats=False, writeins_defeated_after_round1=True,
        surplus_decimals=4,
        citation="Minneapolis Code of Ordinances ch. 167 as amended by 2015-Or-065 (24 Jul 2015), unchanged in these "
                 "sections since: 167.20, 167.45, 167.60(b), (c)(1)b, c and d and (c)(2), 167.70(b), (c)(1)c, d and e and (c)(2). "
                 "https://mcclibraryfunctions.azurewebsites.us/api/ordinanceDownload/11490/726918/pdf and "
                 "https://library.municode.com/mn/minneapolis/codes/code_of_ordinances/307350?nodeId=COOR_TIT8.5EL_CH167MUELRUCO",
    ),
}


def next_choice(ballot: tuple, continuing: set, rules: RuleSet) -> str | None:
    """The candidate this ballot counts for, or None when the ballot is exhausted.

    Walks the marks in order and returns the first code in `continuing`. A blank (None), an overvote and a code
    already seen higher on the ballot are passed over or exhaust the ballot, as the rule set says. A blank run
    longer than max_consecutive_skips exhausts the ballot.
    """
    seen: set = set()
    blanks = 0
    for x in ballot:
        if x is None:
            blanks += 1
            if rules.skipped == "exhaust" or (rules.max_consecutive_skips is not None and blanks > rules.max_consecutive_skips):
                return None
            continue
        blanks = 0
        if x == OVERVOTE:
            if rules.overvote == "exhaust":
                return None
            continue
        if x in seen:
            if rules.duplicate == "exhaust":
                return None
            continue
        seen.add(x)
        if x in continuing:
            return x
    return None


## The count ----------------------------------------------------------------------------------------------------
##Each pass of the loop in tabulate() is one round. The order inside a round follows ch. 167.60(c) (one seat) and
##167.70(c) (several seats):
##  a. count; if enough candidates are at the threshold, they are elected and the count ends (it also ends when only as
##     many candidates continue as seats are still to fill; in 2009, with one seat, when two continue and one has more
##     votes, that one is elected and nobody else is defeated)
##  b. the surplus of every continuing candidate over the threshold is calculated
##  c. batch elimination (rules.batch_tests), and the undeclared write-ins in round 1 when the rule set says so; if anyone
##     is defeated, the next round starts and the surplus waits
##  d. else the continuing candidate with the largest surplus is elected and the surplus is transferred
##  e. else the continuing candidate with the fewest votes is defeated
##Conventions. A round's tallies are the counts at its start: continuing candidates, elected candidates with the votes
##they keep, and no defeated candidate (except in the last round, where nothing is transferred from them). The threshold
##is floor(V / (seats + 1)) + 1, with V the ballots that have a valid first choice, fixed after round 1. Weights are
##fractions. A defeated candidate's ballots move on at their current weight. An elected candidate's surplus fraction is
##(votes - threshold) / votes, truncated to rules.surplus_decimals (None = exact). Each of the candidate's ballots gets the weight
##trunc(surplus fraction * its weight) and moves to its next continuing candidate. The candidate keeps the rest, so
##kept + moved = what the candidate had, and tallies + exhausted = V in every round.
##Batch test 1: for each distinct total v that has a higher total h, the group is every continuing candidate with a
##total <= v. The group is defeated when its votes + all surplus (+ undeclared write-in votes, from 2013) are below h
##(or equal h, in 2009), and at least as many candidates as seats still to fill remain. Batch test 2 (2015 on): a
##candidate with fewer rankings anywhere on any ballot than the lowest of the top-x current totals (x = seats still to
##fill) is defeated. Skipped: the pre-count against the maximum possible threshold (167.60(b), 167.70(b)). It only ends
##the count early with the winners round 1 gives.

@dataclass
class Round:
    number: int
    tallies: dict
    exhausted: Fraction
    defeated: list = field(default_factory=list)
    elected: list = field(default_factory=list)


@dataclass
class Result:
    threshold: int
    rounds: list
    elected: list
    flags: list


def _trunc(x: Fraction, decimals: int | None) -> Fraction:
    if decimals is None:
        return x
    s = 10 ** decimals
    return Fraction(floor(x * s), s)


def tabulate(ballots: list, seats: int, rules: RuleSet, writein_code: str = WRITE_IN,
             tie_resolution: dict | None = None) -> Result:
    if seats < 1:
        raise ValueError(f"seats must be at least 1, got {seats}")
    resolution = tie_resolution or {}
    wi_out = rules.writeins_defeated_after_round1
    equal_defeats = rules.batch1_equal_defeats

    groups = Counter(tuple(b) for b in ballots)  # identical ballots always travel together
    cont = {x for b in groups for x in b if x is not None and x != OVERVOTE}
    marks: Counter = Counter()
    for b, n in groups.items():
        for x in b:
            if x is not None and x != OVERVOTE:
                marks[x] += n
    live = []  # [ballot, count, holder, weight]; a ballot with no valid first choice is not counted at all
    for b, n in groups.items():
        h = next_choice(b, cont, rules)
        if h is not None:
            live.append([b, n, h, Fraction(1)])
    votes = sum(g[1] for g in live)
    if votes == 0:
        raise ValueError("no ballot has a valid first choice")  # nothing to count; never elect on 0 votes
    threshold = votes // (seats + 1) + 1

    rounds: list = []
    flags: list = []
    elected: list = []
    kept: dict = {}

    def move(holders_in: set) -> None:
        for g in live:
            if g[2] in holders_in:
                g[2] = next_choice(g[0], cont, rules)

    rnd = 0
    while True:
        rnd += 1
        tal = {c: Fraction(0) for c in cont}
        exhausted = Fraction(0)
        for _, n, h, w in live:
            if h is None:
                exhausted += n * w
            else:
                tal[h] += n * w
        rd = Round(rnd, {**kept, **tal}, exhausted)
        rounds.append(rd)
        if sum(rd.tallies.values()) + exhausted != votes:
            raise ValueError(f"round {rnd}: votes are not conserved")

        real = sorted(c for c in cont if not (wi_out and c == writein_code))
        over = [c for c in real if tal[c] >= threshold]
        still = seats - len(elected)  # seats still to fill
        winners = None
        if len(elected) + len(over) == seats:
            winners = over
        elif rules.two_remain_elects_leader and seats == 1 and len(real) == 2 and tal[real[0]] != tal[real[1]]:
            winners = [max(real, key=tal.get)]  # 2009: two remain, the most votes is elected; a tie goes to the lot
        elif len(real) <= still:
            if len(real) < still:
                flags.append(f"FEWER_CONTINUING_THAN_SEATS {rnd}")
            winners = real
        if winners is not None:
            rd.elected = sorted(winners)
            elected += rd.elected
            break

        surplus = {c: tal[c] - threshold for c in over if tal[c] > threshold}
        defeat: set = set()
        wi_cont = wi_out and writein_code in cont
        if rnd == 1 and wi_cont:
            defeat.add(writein_code)
        if 1 in rules.batch_tests:
            vals = sorted({tal[c] for c in real})
            extra = tal[writein_code] if wi_cont else Fraction(0)
            for v, higher in zip(vals, vals[1:]):
                grp = [c for c in real if tal[c] <= v]
                # a member with a surplus already puts the group at or over the next higher total, so counting
                # the surplus of group members twice never changes the outcome
                reach = sum(tal[c] for c in grp) + extra + sum(surplus.values())
                if (reach <= higher if equal_defeats else reach < higher) and len(real) - len(grp) >= still:
                    defeat.update(grp)
        if 2 in rules.batch_tests:
            ref = sorted((tal[c] for c in real), reverse=True)[still - 1]
            defeat.update(c for c in real if marks[c] < ref)

        def pick(tied: list) -> str | None:
            if len(tied) == 1:
                return tied[0]
            flags.append(f"TIE {rnd} {','.join(tied)}")
            chosen = resolution.get(rnd)
            if chosen in tied:
                flags.append(f"TIE_RESOLUTION_USED {rnd} {chosen}")
                return chosen
            if chosen is not None:
                flags.append(f"BAD_TIE_RESOLUTION {rnd} {chosen}")
            flags.append(f"UNRESOLVED_TIE {rnd}")
            return None

        if not defeat and surplus:
            top = max(surplus.values())
            e = pick(sorted(c for c, s in surplus.items() if s == top))
            if e is None:
                break
            sf = _trunc((tal[e] - threshold) / tal[e], rules.surplus_decimals)
            rd.elected = [e]
            elected.append(e)
            keep = Fraction(0)
            for g in live:
                if g[2] == e:
                    new = _trunc(sf * g[3], rules.surplus_decimals)
                    keep += g[1] * (g[3] - new)
                    g[3] = new
            kept[e] = keep
            cont.discard(e)
            move({e})
            continue

        if not defeat:
            low = min(tal[c] for c in real)
            loser = pick([c for c in real if tal[c] == low])
            if loser is None:
                break
            defeat = {loser}
        rd.defeated = sorted(defeat)
        rest = [c for c in real if c not in defeat]
        if len(rest) <= still:  # final round: the defeated keep their votes, the rest are elected
            rd.elected = rest
            elected += rest
            break
        cont -= defeat
        move(defeat)

    return Result(threshold, rounds, elected, flags)


def result_to_json(r: Result) -> dict:
    """Tallies as exact "p/q" strings, keys sorted by code."""
    return {
        "threshold": r.threshold,
        "rounds": [{"tallies": {c: f"{v.numerator}/{v.denominator}" for c, v in sorted(rd.tallies.items())},
                    "exhausted": f"{rd.exhausted.numerator}/{rd.exhausted.denominator}",
                    "defeated": rd.defeated, "elected": rd.elected} for rd in r.rounds],
        "elected": r.elected,
        "flags": r.flags,
    }


## Reading a table and the official CSV ------------------------------------------------------------------------

def read_ballots(path: Path) -> list:
    """Ballots of an IRW rankings table: a tuple of items by position 1..n, None where nothing is marked."""
    marks: dict = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            b = marks.setdefault((r.get("task", "1"), r["id"]), {})
            pos = int(r["resp"])
            if pos in b:
                raise ValueError(f"{path.name}: ballot {r['id']} has two rows at position {pos}")
            b[pos] = r["item"]
    n = max((p for b in marks.values() for p in b), default=0)
    return [tuple(b.get(p) for p in range(1, n + 1)) for b in marks.values()]


@dataclass
class Official:
    rounds: list                    # one {item: Fraction} per round, items without (exhausted)
    exhausted: list                 # one Fraction or None per round
    threshold: Fraction | None
    elected: list
    lots: dict                      # round -> code
    first_marks: bool


def read_official(path: Path) -> Official:
    by_round: dict = {}
    ex: dict = {}
    threshold, elected, lots, first_marks = None, [], {}, False
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            item, rnd, raw = r["item"].strip(), int(r["round"]), (r["votes"] or "").strip()
            if item.startswith("(elected:") and item.endswith(")"):
                elected.append(item[9:-1])
            elif item.startswith("(lot:") and item.endswith(")"):
                if rnd in lots:
                    raise ValueError(f"{path.name}: round {rnd} has two (lot:...) rows")
                lots[rnd] = item[5:-1]
            elif item == "(first_marks)":
                first_marks = True
            else:
                try:
                    v = Fraction(Decimal(raw))
                except InvalidOperation:
                    raise ValueError(f"{path.name}: round {rnd} {item}: votes {raw!r} is not a number") from None
                if item == "(threshold)":
                    if threshold is not None:
                        raise ValueError(f"{path.name}: (threshold) is listed twice")
                    threshold = v
                elif item == EXHAUSTED:
                    if rnd in ex:
                        raise ValueError(f"{path.name}: round {rnd} lists {item} twice")
                    ex[rnd] = v
                    by_round.setdefault(rnd, {})
                else:
                    if item in by_round.get(rnd, {}):
                        raise ValueError(f"{path.name}: round {rnd} lists {item} twice")
                    by_round.setdefault(rnd, {})[item] = v
    n = max(by_round, default=0)
    if sorted(by_round) != list(range(1, n + 1)):
        raise ValueError(f"{path.name}: rounds are not numbered 1..{n}")
    return Official([by_round[k] for k in range(1, n + 1)], [ex.get(k) for k in range(1, n + 1)], threshold, elected,
                    lots, first_marks)


## Comparing -------------------------------------------------------------------------------------------------

def _show(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{float(x):.4f}".rstrip("0").rstrip(".")


def compare(ours: Result, off: Official, ballots: list, seats: int) -> list:
    """Differences between our count and the official results; an empty list is an exact match."""
    out: list = []
    if off.first_marks:
        if len(ours.rounds) != 1:
            out.append(f"won on first choices per the city, but our count took {len(ours.rounds)} rounds")
        first = Counter(b[0] for b in ballots if b and b[0] not in (None, OVERVOTE))
        city = off.rounds[0] if off.rounds else {}
        for c in sorted(set(first) | set(city)):
            a, b = Fraction(first.get(c, 0)), city.get(c, Fraction(0))
            if a != b:
                out.append(f"first marks {c}: ours {_show(a)}, city {_show(b)}")
    else:
        if off.threshold is not None and ours.threshold != off.threshold:
            out.append(f"threshold: ours {ours.threshold}, city {_show(off.threshold)}")
        if len(ours.rounds) != len(off.rounds):
            out.append(f"rounds: ours {len(ours.rounds)}, city {len(off.rounds)}")
        for k, (r, o) in enumerate(zip(ours.rounds, off.rounds), 1):
            for c in sorted(set(r.tallies) | set(o)):
                a, b = _trunc(r.tallies.get(c, Fraction(0)), 4), o.get(c, Fraction(0))
                if a != b:
                    out.append(f"round {k} {c}: ours {_show(a)}, city {_show(b)}")
            if off.exhausted[k - 1] is not None:
                a, b = _trunc(r.exhausted, 4), off.exhausted[k - 1]
                if a != b:
                    out.append(f"round {k} {EXHAUSTED}: ours {_show(a)}, city {_show(b)}")
    if set(ours.elected) != set(off.elected) or len(ours.elected) != len(off.elected):
        out.append(f"elected: ours {sorted(ours.elected)}, city {sorted(off.elected)}")
    return out


def recount_one(ballots: list, seats: int, rules: RuleSet, off: Official) -> tuple:
    res = tabulate(ballots, seats, rules, tie_resolution=off.lots)
    return res, compare(res, off, ballots, seats)


## Command line ----------------------------------------------------------------------------------------------

def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Recount Minneapolis ranked-choice tables against the city's results.")
    ap.add_argument("tables", nargs="*", help="table names (default: every design row that starts with --prefix)")
    ap.add_argument("--rules", required=True, choices=sorted(RULE_SETS))
    ap.add_argument("--design", required=True, type=Path, help="design_tables.csv (gives the seats of each table)")
    ap.add_argument("--tables-dir", required=True, type=Path)
    ap.add_argument("--official-dir", required=True, type=Path)
    ap.add_argument("--prefix", default="", help="select the design rows whose table starts with this")
    ap.add_argument("--no-truncation", action="store_true", help="use exact fractions in the main count")
    ap.add_argument("--json-out", type=Path, help="write <table>.json (exact tallies) into this folder")
    args = ap.parse_args(argv)

    with open(args.design, newline="", encoding="utf-8") as f:
        design = {r["table"]: r for r in csv.DictReader(f)}
    names = args.tables or sorted(t for t in design if args.prefix and t.startswith(args.prefix))
    if not names:
        print("no tables selected: give table names or --prefix", file=sys.stderr)
        return 2
    rules = RULE_SETS[args.rules]
    if args.no_truncation:
        rules = replace(rules, surplus_decimals=None)
    print(f"recount: rule set {rules.id}, {len(names)} table(s)\n{rules.citation}")
    bad = unsettled = 0
    for t in names:
        try:
            seats = int(design[t]["seats"])
            ballots = read_ballots(args.tables_dir / f"{t}.csv")
            off = read_official(args.official_dir / f"{t}.csv")
        except (KeyError, ValueError, OSError) as e:
            print(f"{t}: cannot start ({e!r})", file=sys.stderr)
            return 2
        try:
            res, diffs = recount_one(ballots, seats, rules, off)
        except ValueError as e:  # e.g. no ballot has a valid first choice
            print(f"{t}: cannot recount ({e})", file=sys.stderr)
            return 2
        line = f"{t}: {seats} seat(s), {len(res.rounds)} round(s), " + ("exact" if not diffs else f"{len(diffs)} DIFFERENCES")
        if seats > 1 and rules.surplus_decimals is not None:
            alt = recount_one(ballots, seats, replace(rules, surplus_decimals=None), off)[1]
            line += f", without truncation {'exact' if not alt else 'NOT exact'}"
        if res.flags:
            line += f", flags {res.flags}"
        print(line)
        for d in diffs:
            print(f"    {d}")
        bad += bool(diffs)
        unsettled += any(f.startswith("UNRESOLVED_TIE") for f in res.flags)
        if args.json_out:
            args.json_out.mkdir(parents=True, exist_ok=True)
            (args.json_out / f"{t}.json").write_text(json.dumps(result_to_json(res), indent=1, sort_keys=True) + "\n",
                                                     encoding="utf-8")
    print(f"{len(names) - bad}/{len(names)} tables exact")
    return 1 if bad or unsettled else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
