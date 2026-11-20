#!/usr/bin/env python3
##Rankings recount: count a ranked-choice table under its rule set in counting_rules.csv and compare every round with
##the published rounds (#3606). It generalises data/rankings/minneapolis/recount.py (#3166): the Minneapolis rule sets and the
##FairVote ones are rows of counting_rules.csv, and one counter reads the row. Ranked methods only (IRV, STV, sequential,
##with the rule set's own truncation): a row with a Condorcet method is not counted here. Nothing in irw_validate counts.
##
##Usage (from anywhere; the default files sit beside this script):
##  python3 recount.py --tables-dir <dir of IRW table CSVs> [--all | --prefix rcv_mpls_2023 | TABLE ...]
##      [--published-dir published_rounds] [--results recount_results.csv] [--rules RULE_SET] [--json-out <dir>]
##For each table the script reads <tables-dir>/<table>.csv (columns id, task, item, resp), its design row, the rule set
##that row joins (rules_jurisdiction, else jurisdiction, and the date window; the join of metadata/tests/test_rank_rules_join.py),
##counting_values.csv (writein_filed), and <published-dir>/<table>.csv. --all takes every file of the published folder.
##--rules counts under another named rule set, to see which rules the ballots used (a sensitivity run).
##
##Published rounds: one CSV per table, columns round,item,votes, copied as printed by the source, never adjusted.
##  <round>,<code>,<votes>      a candidate's tally at the START of the round (transfers show in the next round)
##  <round>,(write-in),<votes>  undeclared or pooled write-ins;  <round>,(exhausted),<votes>  exhausted ballots (optional)
##  1,(source),<url>            where the figures come from; one row per document, at least one
##  1,(threshold),<votes>       the threshold the source prints (optional)
##  1,(elected:<code>),         one row per elected candidate
##  <round>,(lot:<code>),       the candidate a draw settled in that round (see Ties)
##  1,(first_marks),            round 1 is the first marks as voted, from a page that prints no tabulation (see First marks)
##  1,(seat:<k>),               a sequential count with one page per seat: the rows after this one are seat k, rounds from 1 again
##A candidate that is not listed in a round has 0 votes there. Figures are compared exactly.
##
##What is compared: the elected set; every candidate and (write-in) in every round; (exhausted) and (threshold) when the file
##has them. A round is one in which votes are counted or moved (the ruling of 23 Oct 2026 on #3024), so a published column
##that repeats the figures of the one before it, a candidate on 0 votes aside, is folded into it, on the source side and on
##ours alike. A table whose rounds all match and whose winners match is `match`; anything else is a `warning`, never a failure:
##the first difference is recorded, with the reason when recount_reasons.csv gives one.
##First marks. A results page counts a ballot for its mark in first place as voted. A ballot whose first mark is an overvote
##or blank is left out of the page even when it counts for a later choice. Round 1 of the count here uses the first valid
##choice. With (first_marks), round 1 is compared with the marks in first place as voted; later rounds are compared as usual.
##Ties. A tie for fewest votes, or for the largest surplus, is never broken silently. The count stops with UNRESOLVED_TIE
##(a warning). To follow a draw the source shows, add the (lot:<code>) row of that round (rounds after folding). The status is
##then `match_by_lot` and not `match`.
##
##A table is read as ballots: one ballot is one id; the item at position p is the row with resp = p; a position with no row is a
##skipped ranking; (overvote) is an overvote; a ballot with no rows is counted from n_ballots_cast of the design row.
##Multiple seats (STV) use exact fractions with the rule set's truncation. The order inside a round, from Minneapolis ch. 167:
##  a. count; enough candidates at the threshold are elected and the count ends; so does as few continuing as seats left;
##     with one_seat_stop = two_continuing, two continuing end a one-seat count, the one with more elected
##  b. the surplus of every candidate over the threshold
##  c. the batch tests the row names; anyone defeated: the next round starts and the surplus waits
##  d. else the largest surplus is elected and transferred
##  e. else the fewest votes is defeated, and a defeat that leaves as many continuing as seats to fill is not transferred
##     (last_defeat_transfer says so)
##Every cell value dispatches explicitly. A value this counter does not know raises an error, recorded as a warning for that
##table. Exit code: 0 when every table was counted (a warning is not a failure), 2 when a file was missing or the input is bad.
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from math import floor
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent


## The counter -----------------------------------------------------------------------------------------------------

OVERVOTE = "(overvote)"
WRITEIN = "(write-in)"
REASONS = ("overvote", "skips", "duplicate", "no_continuing", "no_marks", "residual")

OVERVOTE_VALUES = {"pass_over", "exhaust", "exhaust_unless_one_continuing"}  # the last reads as exhaust from a table
SKIPPED_VALUES = {"pass_over", "exhaust"}
DUPLICATE_VALUES = {"pass_over", "exhaust", "skipped_ranking", "na"}
BATCH_VALUES = {"test1_next_higher_total_surpass", "test1_next_higher_total_equal_or_surpass",
                "test1_next_higher_total_surpass_unless_one_continuing_left",
                "test1_lowest_up_next_higher_total_equal_or_surpass",
                "all_but_two_defeated_together", "tied_lowest_no_possible_win_round1",
                "test2_sum_of_all_ranked_votes", "undeclared_writeins_defeated_round2",
                "writeins_defeated_alone_round1", "writeins_defeated_with_lowest_round1", "writeins_counted_only_if_declared",
                "tied_lowest_group_below_next_total",
                "filed_writeins_defeated_before_round1"}
TEST1_VALUES = ("test1_next_higher_total_surpass", "test1_next_higher_total_equal_or_surpass",
                "test1_next_higher_total_surpass_unless_one_continuing_left",
                "test1_lowest_up_next_higher_total_equal_or_surpass")
THRESHOLD_VALUES = {"floor(votes_cast/(seats+1))+1", "majority_of_active_ballots_round1_only",
                    "majority_of_active_ballots_every_count"}
THRESHOLD_NOTES = {"first_round_decided_at_maximum_possible_threshold"}  # can only end the count early with the same winners
SURPLUS_VALUES = {"fractional_all_votes_truncated", "fractional_all_votes_truncated_together",
                  "fractional_largest_first_one_per_round", "seat_by_seat_restart", "na"}
LAST_DEFEAT_VALUES = {"not_when_continuing_equals_seats_to_fill", "city_sheet_no_transfer", "transferred", "na"}
ONE_SEAT_STOP_VALUES = {"one_continuing", "two_continuing", "na"}


def _choice(row: dict, col: str, known: set[str]) -> str:
    v = row[col]
    if v not in known:
        raise ValueError(f"{row.get('rule_set')}: {col} = {v!r} is not a value this counter knows")
    return v


@dataclass(frozen=True)
class Cells:
    rule_set: str
    overvote: str
    skip_limit: int | None  # a run of skipped rankings longer than this stops the ballot; None = no limit
    duplicate: str
    batch: frozenset[str]
    threshold: str
    surplus: str
    decimals: int | None
    last_defeat: str
    one_seat_stop: str

    @property
    def writein_filed_test(self) -> bool:
        return "filed_writeins_defeated_before_round1" in self.batch

    @property
    def writein_undeclared(self) -> bool:
        return "undeclared_writeins_defeated_round2" in self.batch

    @property
    def writein_declared_test(self) -> bool:
        return "writeins_counted_only_if_declared" in self.batch

    @property
    def writein_alone(self) -> bool:
        return "writeins_defeated_alone_round1" in self.batch


def parse_cells(row: dict) -> Cells:
    overvote = _choice(row, "overvote", OVERVOTE_VALUES)
    skipped = _choice(row, "skipped", SKIPPED_VALUES)
    mcs = row["max_consecutive_skips"]
    if mcs == "none":
        limit = None
    elif mcs.isdigit():
        limit = int(mcs)
    else:
        raise ValueError(f"{row.get('rule_set')}: max_consecutive_skips = {mcs!r} is not a value this counter knows")
    if skipped == "exhaust" and limit != 0:
        raise ValueError(f"{row.get('rule_set')}: skipped = exhaust needs max_consecutive_skips = 0, not {mcs!r}")
    if skipped == "pass_over" and limit == 0:
        raise ValueError(f"{row.get('rule_set')}: skipped = pass_over cannot have max_consecutive_skips = 0")
    duplicate = _choice(row, "duplicate", DUPLICATE_VALUES)
    be = row["batch_elimination"]
    batch = frozenset() if be == "none" else frozenset(be.split("+"))
    if not batch <= BATCH_VALUES:
        raise ValueError(f"{row.get('rule_set')}: batch_elimination = {be!r} is not a value this counter knows")
    parts = [p.strip() for p in row["threshold"].split(";")]
    if parts[0] not in THRESHOLD_VALUES or not set(parts[1:]) <= THRESHOLD_NOTES:
        raise ValueError(f"{row.get('rule_set')}: threshold = {row['threshold']!r} is not a value this counter knows")
    surplus = _choice(row, "surplus_transfer", SURPLUS_VALUES)
    sd = row["surplus_decimals"]
    if sd != "na" and not sd.isdigit():
        raise ValueError(f"{row.get('rule_set')}: surplus_decimals = {sd!r} is not a value this counter knows")
    return Cells(row["rule_set"], overvote, limit, duplicate, batch, parts[0], surplus,
                 None if sd == "na" else int(sd), _choice(row, "last_defeat_transfer", LAST_DEFEAT_VALUES),
                 _choice(row, "one_seat_stop", ONE_SEAT_STOP_VALUES))


def walk(ballot: tuple, continuing: set[str], c: Cells, writein_passed: bool) -> tuple[str | None, str]:
    """(the candidate the ballot counts for, "") or (None, why it stopped). writein_passed: "(write-in)" is no candidate
    here and is passed over without being a skip (no write-in candidate filed for the race)."""
    last = max((i for i, x in enumerate(ballot) if x is not None), default=-1)
    seen: set[str] = set()
    run = 0

    def skipped() -> bool:
        nonlocal run
        run += 1
        return c.skip_limit is not None and run > c.skip_limit

    for x in ballot[:last + 1]:
        if x is None:
            if skipped():
                return None, "skips"
            continue
        if x == OVERVOTE:
            if c.overvote != "pass_over":
                # exhaust_unless_one_continuing: the (overvote) token does not say which candidates it holds, so a count
                # from a table cannot apply the exception, and the difference shows against the published rounds
                return None, "overvote"
            run = 0
            continue
        if x in seen:  # a second write-in mark too: one token stands for the write-in line
            if c.duplicate == "exhaust":
                return None, "duplicate"
            if c.duplicate == "skipped_ranking":
                if skipped():
                    return None, "skips"
            elif c.duplicate == "pass_over":
                run = 0
            continue
        seen.add(x)
        if x == WRITEIN and writein_passed:
            run = 0
            continue
        if x in continuing:
            return x, ""
        run = 0  # a defeated or elected candidate's ranking is not blank
    return None, "no_continuing"


def ballots_of(table_rows: Iterable[dict], n_positions: int, n_ballots: int) -> Counter:
    """Identical ballots grouped: {(item or None per position): count}, empty ballots included as all None."""
    marks: dict[str, dict[int, str]] = defaultdict(dict)
    for r in table_rows:
        b, pos = marks[str(r["id"])], int(r["resp"])
        if pos in b:
            raise ValueError(f"ballot {r['id']}: two rows at position {pos}")
        b[pos] = r["item"]
    top = max((p for b in marks.values() for p in b), default=0)
    width = max(n_positions, top)
    groups = Counter(tuple(b.get(p) for p in range(1, width + 1)) for b in marks.values())
    empty = n_ballots - len(marks)
    if empty < 0:
        raise ValueError(f"{len(marks)} ballots in the table, {n_ballots} cast")
    if empty:
        groups[(None,) * width] += empty
    return groups


def _trunc(x: Fraction, decimals: int) -> Fraction:
    s = 10 ** decimals
    return Fraction(floor(x * s), s)


def _pick(tied: list[str], rnd: int, lots: dict[int, str], flags: list[str]) -> str | None:
    if len(tied) == 1:
        return tied[0]
    flags.append(f"TIE {rnd} {','.join(tied)}")
    chosen = lots.get(rnd)
    if chosen in tied:
        flags.append(f"LOT {rnd} {chosen}")
        return chosen
    if chosen is not None:
        flags.append(f"BAD_LOT {rnd} {chosen}")
    flags.append(f"UNRESOLVED_TIE {rnd}")
    return None


def _round(number: int, tal: dict[str, Fraction], kept: dict[str, Fraction], inactive: dict[str, Fraction],
           threshold: Fraction | None, after: bool) -> dict:
    t = {**kept, **tal}
    return {"number": number, "tallies": {k: t[k] for k in sorted(t)}, "threshold": threshold,
            "inactive": {k: inactive[k] for k in REASONS}, "defeated": [], "elected": [], "after_decision": after}


def _seat_by_seat(row: dict, groups: Counter, design: dict, inputs: dict, count_on: bool) -> dict:
    """surplus_transfer = seat_by_seat_restart with several seats: one count per seat, each a one-seat count of the same
    ballots with every candidate already elected left out, all others back in. A mark for an elected candidate is passed
    over like a defeated candidate's. Round numbers run on within the table; each round carries its `seat`."""
    seats = int(design["seats"])
    elected: list[str] = []
    rounds: list[dict] = []
    flags: list[str] = []
    k = decided = 0
    for seat in range(1, seats + 1):
        one = {**row, "surplus_transfer": "na", "surplus_decimals": "na"}
        lots = (inputs.get("lots") or {}).get(f"seat{seat}", {})
        res = _ranked(one, groups, {**design, "seats": "1"}, {**inputs, "lots": lots, "_out": set(elected)}, count_on)
        for r in res["rounds"]:
            k += 1
            rounds.append({**r, "number": k, "seat": seat})
        flags += [f"SEAT {seat} {f}" for f in res["flags"]]
        if not res["elected"]:
            break
        elected += res["elected"]
        decided = k - len(res["rounds"]) + res["elected_at"]
    return {"table": design["table"], "rule_set": row["rule_set"], "method": "ranked", "rounds": rounds, "elected": elected,
            "elected_at": decided if len(elected) == seats else None, "initial": None, "flags": flags}


def _held_at_threshold(row: dict, c: Cells, groups: Counter, design: dict, inputs: dict) -> dict:
    """The two surplus values under which an elected candidate counts as the threshold once the surplus has moved; what
    truncation leaves behind is the residual.
    fractional_all_votes_truncated_together: everyone at the threshold is elected in that round and every surplus moves at
    once, unless those elected and those continuing are then no more than the seats: the continuing are elected in that
    round, nothing moves, and one last table shows the elected held at the threshold.
    fractional_largest_first_one_per_round: if as many continuing candidates are above the threshold as seats remain, they
    are elected and the count ends; else the one with the most votes at the threshold is elected and that surplus moves.
    With nobody at the threshold the candidate with the fewest votes is defeated. A final defeat is moved or not as
    last_defeat_transfer says; then all continuing are elected."""
    together = c.surplus == "fractional_all_votes_truncated_together"
    seats = int(design["seats"])
    lots = {int(k): v for k, v in (inputs.get("lots") or {}).items()}
    writein_passed = c.writein_declared_test and inputs.get("writein_filed") is False
    empty_key = next((b for b in groups if all(x is None for x in b)), None)
    cont = {x for b in groups for x in b if x is not None and x != OVERVOTE and not (x == WRITEIN and writein_passed)}
    live = []
    for b, n in groups.items():
        h, why = walk(b, cont, c, writein_passed)
        live.append([b, n, h, Fraction(1), "no_marks" if b == empty_key else why])
    rounds: list[dict] = []
    flags: list[str] = []
    elected: list[str] = []
    fixed: Fraction | None = None
    residual = Fraction(0)
    rnd = 0

    def move_surplus(k: str, v: Fraction) -> Fraction:
        sf = _trunc((v - fixed) / v, c.decimals)
        carried = Fraction(0)
        for g in live:
            if g[2] == k:
                g[3] = _trunc(sf * g[3], c.decimals)
                carried += g[1] * g[3]
        return (v - fixed) - carried

    def transfer(gone: set[str]) -> None:
        for g in live:
            if g[2] in gone:
                g[2], g[4] = walk(g[0], cont, c, writein_passed)

    while True:
        rnd += 1
        tal = {k: sum((g[1] * g[3] for g in live if g[2] == k), Fraction(0)) for k in cont}
        ina = {k: Fraction(0) for k in REASONS}
        for _, n, h, w, why in live:
            if h is None:
                ina[why] += n * w
        ina["residual"] = residual
        if rnd == 1:
            active = sum(tal.values())
            if active == 0:
                raise ValueError(f"{design['table']}: no ballot counts for a candidate in round 1")
            fixed = Fraction(int(active) // (seats + 1) + 1)
        rd = _round(rnd, tal, {k: fixed for k in elected}, ina, fixed, False)
        rounds.append(rd)
        still = seats - len(elected)
        if still == 0:  # the table that shows the last surplus moved
            break
        over = sorted(k for k in cont if tal[k] >= fixed)
        if len(cont) <= still:
            if len(cont) < still:
                flags.append(f"FEWER_CONTINUING_THAN_SEATS {rnd}")
            rd["elected"] = sorted(cont)
            elected += rd["elected"]
            if together and over:  # nothing moves; the last table shows those over the threshold held at it
                residual += sum(tal[k] - fixed for k in over)
                rounds.append(_round(rnd + 1, {k: tal[k] for k in cont if k not in over},
                                          {k: fixed for k in elected if k not in cont or k in over},
                                          {**ina, "residual": residual}, fixed, False))
            break
        if together and over:
            rd["elected"] = over
            elected += over
            cont -= set(over)
            for k in over:
                residual += move_surplus(k, tal[k])
            transfer(set(over))
            continue
        if not together:
            above = sorted(k for k in over if tal[k] > fixed)
            if len(above) == still:
                rd["elected"] = above
                elected += above
                break
            if over:
                top = max(tal[k] for k in over)
                e = _pick(sorted(k for k in over if tal[k] == top), rnd, lots, flags)
                if e is None:
                    break
                rd["elected"] = [e]
                elected.append(e)
                cont.discard(e)
                residual += move_surplus(e, tal[e])
                transfer({e})
                continue
        low = min(tal.values())
        loser = _pick(sorted(k for k in cont if tal[k] == low), rnd, lots, flags)
        if loser is None:
            break
        rd["defeated"] = [loser]
        cont.discard(loser)
        if len(cont) == still and c.last_defeat != "transferred":
            rd["elected"] = sorted(cont)
            elected += rd["elected"]
            break
        transfer({loser})
    decided = max((r["number"] for r in rounds if r["elected"]), default=None)
    return {"table": design["table"], "rule_set": c.rule_set, "method": "ranked", "rounds": rounds, "elected": elected,
            "elected_at": decided if len(elected) == seats else None, "initial": None, "flags": flags}


def _ranked(row: dict, groups: Counter, design: dict, inputs: dict, count_on: bool) -> dict:
    c = parse_cells(row)
    seats = int(design["seats"])
    if seats < 1:
        raise ValueError(f"seats must be at least 1, got {seats}")
    if c.surplus == "seat_by_seat_restart" and seats > 1:
        return _seat_by_seat(row, groups, design, inputs, count_on)
    if c.surplus in ("fractional_all_votes_truncated_together", "fractional_largest_first_one_per_round") and seats > 1:
        return _held_at_threshold(row, c, groups, design, inputs)
    lots = {int(k): v for k, v in (inputs.get("lots") or {}).items()}
    has_writein = any(WRITEIN in b for b in groups)
    filed = inputs.get("writein_filed")
    if (c.writein_filed_test or c.writein_declared_test) and has_writein and filed is None:
        raise ValueError(f"{c.rule_set}: whether a write-in candidate filed is unknown, and a write-in mark is present")
    writein_passed = (c.writein_filed_test or c.writein_declared_test) and filed is False
    if c.duplicate == "na":  # the ballot paper gives each candidate one square
        for b in groups:
            codes = [x for x in b if x is not None and x != OVERVOTE]
            if len(codes) != len(set(codes)):
                raise ValueError(f"{c.rule_set}: duplicate = na, and a ballot ranks a candidate twice")
    empty_key = next((b for b in groups if all(x is None for x in b)), None)
    cont = {x for b in groups for x in b if x is not None and x != OVERVOTE and not (x == WRITEIN and writein_passed)}
    cont -= inputs.get("_out", set())  # candidates elected to an earlier seat (seat_by_seat_restart)
    marks: Counter[str] = Counter()  # every mark of every ballot, repeats included (test 2)
    for b, n in groups.items():
        for x in b:
            if x is not None and x != OVERVOTE:
                marks[x] += n
    live = []  # [ballot, count, holder, weight, why]
    for b, n in groups.items():
        h, why = walk(b, cont, c, writein_passed)
        live.append([b, n, h, Fraction(1), "no_marks" if b == empty_key else why])

    def move(out: set[str]) -> None:
        for g in live:
            if g[2] in out:
                g[2], why2 = walk(g[0], cont, c, writein_passed)
                g[4] = why2

    def tally() -> tuple[dict[str, Fraction], dict[str, Fraction]]:
        tal = {k: Fraction(0) for k in cont}
        ina = {k: Fraction(0) for k in REASONS}
        for _, n, h, w, why in live:
            if h is None:
                ina[why] += n * w
            else:
                tal[h] += n * w
        return tal, ina

    flags: list[str] = []
    initial = None
    # filed_writeins_defeated_before_round1 (README): the initial count, all write-ins pooled as one candidate
    if c.writein_filed_test and filed is True:
        tal, ina = tally()
        active = sum(tal.values())
        real = {k: v for k, v in tal.items() if k != WRITEIN}
        if active and not any(2 * v > active for v in real.values()):
            wi = tal.get(WRITEIN, Fraction(0))
            lead = max(real.values(), default=Fraction(0))
            if wi < lead and 200 * (lead - wi) >= lead + wi:
                initial = _round(0, {**tal, WRITEIN: wi}, {}, ina, None, False)
                initial["defeated"] = [WRITEIN]
                cont.discard(WRITEIN)
                move({WRITEIN})
            else:
                flags.append("WRITEIN_INDIVIDUAL 1")
                initial = _round(0, tal, {}, ina, None, False)
                return {"table": design["table"], "rule_set": c.rule_set, "method": "ranked", "rounds": [],
                        "elected": [], "elected_at": None, "initial": initial, "flags": flags}

    wi_alone = c.writein_alone  # the write-in line goes by itself at the end of round 1, and nothing else does then
    wi_lowest = "writeins_defeated_with_lowest_round1" in c.batch  # with the one candidate with the fewest votes
    wi_out = c.writein_undeclared or wi_alone or wi_lowest  # defeated at the end of round 1, never elected, not a candidate
    wi_group = c.writein_filed_test  # the pooled group is never elected by a majority

    def electable(k: str) -> bool:
        return not ((wi_out or wi_group) and k == WRITEIN)

    rounds: list[dict] = []
    elected: list[str] = []
    elected_at = None
    kept: dict[str, Fraction] = {}
    fixed: Fraction | None = None
    decided = False
    rnd = 0
    while True:
        rnd += 1
        tal, ina = tally()
        active = sum(tal.values())
        if rnd == 1:
            if active == 0:
                raise ValueError(f"{design['table']}: no ballot counts for a candidate in round 1")
            if c.threshold == "floor(votes_cast/(seats+1))+1":
                fixed = Fraction(int(active) // (seats + 1) + 1)
        standing = active + sum(kept.values())
        if c.threshold == "floor(votes_cast/(seats+1))+1":
            th = fixed
        elif c.threshold == "majority_of_active_ballots_every_count":
            th = Fraction(floor(standing / 2) + 1)
        else:  # majority_of_active_ballots_round1_only: more than one half, in the first round only
            th = Fraction(floor(active / 2) + 1) if rnd == 1 else None
        rd = _round(rnd, tal, kept, ina, th, decided)
        rounds.append(rd)
        real = sorted(k for k in cont if electable(k))
        over = [k for k in real if th is not None and tal[k] >= th]
        still = seats - len(elected)

        if decided:  # count_on: the winner stays in the count; two left ends it
            if len(cont) <= 2:
                break
        else:
            winners = None
            if len(over) == still and over:
                winners = over
            elif seats == 1 and c.one_seat_stop == "two_continuing" and len(cont) == 2 and len(real) == 2:
                if tal[real[0]] != tal[real[1]]:
                    winners = [max(real, key=tal.get)]
                else:
                    loser = _pick(real, rnd, lots, flags)
                    if loser is None:
                        break
                    rd["defeated"] = [loser]
                    winners = [k for k in real if k != loser]
            elif len(real) <= still:
                if len(real) < still:
                    flags.append(f"FEWER_CONTINUING_THAN_SEATS {rnd}")
                winners = real
            if winners is not None:
                rd["elected"] = sorted(winners)
                elected += rd["elected"]
                elected_at = rnd
                if not (count_on and seats == 1 and len(cont) > 2):
                    break
                decided = True

        surplus = {k: tal[k] - th for k in over if th is not None and tal[k] > th} if seats > 1 else {}
        defeat: set[str] = set()
        wi_cont = wi_out and WRITEIN in cont
        if rnd == 1 and wi_cont:
            defeat.add(WRITEIN)
        pool = [k for k in real]
        if decided:
            still_now = 1  # one seat, counting on: the winner stays
        else:
            still_now = still
        lone_writein_round = rnd == 1 and wi_alone and wi_cont
        for test in TEST1_VALUES:
            if test in c.batch and not lone_writein_round:
                vals = sorted({tal[k] for k in pool})
                extra = tal[WRITEIN] if wi_cont else Fraction(0)
                leave = 2 if "one_continuing_left" in test or decided else still_now  # counting on stops at two continuing
                found = set()
                for v, higher in zip(vals, vals[1:]):
                    grp = [k for k in pool if tal[k] <= v]
                    reach = sum(tal[k] for k in grp) + extra + sum(surplus.values())
                    below = reach < higher if "equal_or_surpass" in test else reach <= higher
                    if below and len(pool) - len(grp) >= leave:
                        found.update(grp)
                    elif not below and "lowest_up" in test:  # the group grows from the lowest and stops at the first step that fails
                        break
                defeat.update(found)
        if "all_but_two_defeated_together" in c.batch:
            defeat.update(sorted(pool, key=lambda k: (-tal[k], k))[2:])
        if "tied_lowest_no_possible_win_round1" in c.batch and rnd == 1 and not defeat:
            low = min(tal[k] for k in pool)
            if sum(1 for k in pool if tal[k] == low) > 1:
                raise ValueError(f"{c.rule_set}: a tie for the fewest votes in round 1; whether those candidates can still win is a test the text gives by example only")
        if "test2_sum_of_all_ranked_votes" in c.batch:
            ref = sorted((tal[k] for k in pool), reverse=True)[still_now - 1]
            defeat.update(k for k in pool if marks[k] < ref)

        if not defeat and surplus:
            if c.surplus != "fractional_all_votes_truncated" or c.decimals is None:
                raise ValueError(f"{c.rule_set}: a surplus arises, and surplus_transfer is {c.surplus!r}")
            top = max(surplus.values())
            e = _pick(sorted(k for k, s in surplus.items() if s == top), rnd, lots, flags)
            if e is None:
                break
            sf = _trunc(surplus[e] / tal[e], c.decimals)
            rd["elected"] = [e]
            elected.append(e)
            keep = Fraction(0)
            for g in live:
                if g[2] == e:
                    new = _trunc(sf * g[3], c.decimals)
                    keep += g[1] * (g[3] - new)
                    g[3] = new
            kept[e] = keep
            cont.discard(e)
            move({e})
            continue

        if not defeat or (rnd == 1 and wi_lowest and defeat == {WRITEIN}):
            low = min(tal[k] for k in pool)
            tied = sorted(k for k in pool if tal[k] == low)
            higher = [tal[k] for k in pool if tal[k] > low]
            if ("tied_lowest_group_below_next_total" in c.batch and len(tied) > 1 and higher
                    and sum(tal[k] for k in tied) < min(higher) and len(pool) - len(tied) >= still_now):
                defeat = defeat | set(tied)  # no lot: the order among them cannot change the outcome
            else:
                loser = _pick(tied, rnd, lots, flags)
                if loser is None:
                    break
                defeat = defeat | {loser}
        rd["defeated"] = sorted(defeat)
        rest = [k for k in pool if k not in defeat]
        if not decided and len(rest) <= still and c.last_defeat != "transferred":
            if c.last_defeat not in ("not_when_continuing_equals_seats_to_fill", "city_sheet_no_transfer"):
                raise ValueError(f"{c.rule_set}: a final defeat is reached, and last_defeat_transfer is {c.last_defeat!r}")
            rd["elected"] = sorted(rest)
            elected += rd["elected"]
            elected_at = rnd
            break
        cont -= defeat
        move(defeat)

    return {"table": design["table"], "rule_set": c.rule_set, "method": "ranked", "rounds": rounds,
            "elected": elected, "elected_at": elected_at, "initial": initial, "flags": flags}




def count(row: dict, groups: Counter, design: dict, inputs: dict | None = None, count_on: bool = False) -> dict:
    """The count of one ranked table under one row of counting_rules.csv. `groups` is {(item or None per position): count},
    ballots with no marks included; `design` has table, seats, n_positions, n_ballots_cast. `inputs`: lots ({round: code},
    or {"seat<k>": {round: code}} for a sequential count), writein_filed (True, False or None). `count_on` keeps counting a
    one-seat race after its winner is known, until two candidates continue, as some sources publish those rounds."""
    if row.get("condorcet_method", "na") != "na":
        raise ValueError(f"{row['rule_set']}: condorcet_method = {row['condorcet_method']!r}; this counter counts ranked rules only")
    return _ranked(row, groups, design, inputs or {}, count_on)


## Files ----------------------------------------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_table(path: Path) -> Iterable[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            yield {"id": r["id"], "task": r.get("task", "1"), "item": r["item"], "resp": r["resp"]}


def rule_row(design: dict, rules: list[dict]) -> dict:
    """The one row of counting_rules.csv whose jurisdiction is the design row's rules_jurisdiction (else jurisdiction)
    and whose window holds the table's date (valid_from <= date < valid_to; empty valid_to is open)."""
    key = (design.get("rules_jurisdiction") or "").strip() or design["jurisdiction"]
    hit = [r for r in rules if r["jurisdiction"] == key and r["valid_from"] <= design["date"]
           and (not r["valid_to"] or design["date"] < r["valid_to"])]
    if len(hit) != 1:
        raise ValueError(f"{design['table']}: {len(hit)} rule sets join key {key!r} on {design['date']}")
    return hit[0]


@dataclass
class Published:
    sources: list
    rounds: dict            # seat -> [{"tallies": {item: Fraction}, "exhausted": Fraction | None}], round 1 first
    threshold: Fraction | None
    elected: list
    lots: dict              # seat -> {round: code}
    first_marks: bool
    seated: bool            # the file has (seat:k) rows


def _number(path: Path, rnd: int, item: str, raw: str) -> Fraction:
    try:
        return Fraction(Decimal(raw.strip()))
    except InvalidOperation:
        raise ValueError(f"{path.name}: round {rnd} {item}: votes {raw!r} is not a number") from None


def read_published(path: Path) -> Published:
    tallies: dict = defaultdict(dict)       # (seat, round) -> {item: Fraction}
    exhausted: dict = {}
    sources, elected, lots = [], [], defaultdict(dict)
    threshold, first_marks, seated, seat = None, False, False, 1
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            item, rnd, raw = r["item"].strip(), int(r["round"]), (r["votes"] or "").strip()
            if item == "(source)":
                sources.append(raw)
            elif item.startswith("(seat:") and item.endswith(")"):
                seated, seat = True, int(item[6:-1])
            elif item.startswith("(elected:") and item.endswith(")"):
                elected.append(item[9:-1])
            elif item.startswith("(lot:") and item.endswith(")"):
                if rnd in lots[seat]:
                    raise ValueError(f"{path.name}: round {rnd} has two (lot:...) rows")
                lots[seat][rnd] = item[5:-1]
            elif item == "(first_marks)":
                first_marks = True
            elif item == "(threshold)":
                if threshold is not None:
                    raise ValueError(f"{path.name}: (threshold) is listed twice")
                threshold = _number(path, rnd, item, raw)
            elif item == "(exhausted)":
                if (seat, rnd) in exhausted:
                    raise ValueError(f"{path.name}: round {rnd} lists (exhausted) twice")
                exhausted[seat, rnd] = _number(path, rnd, item, raw)
                tallies[seat, rnd]
            else:
                if item in tallies[seat, rnd]:
                    raise ValueError(f"{path.name}: round {rnd} lists {item} twice")
                tallies[seat, rnd][item] = _number(path, rnd, item, raw)
    rounds: dict = {}
    for s in sorted({s for s, _ in tallies}):
        n = max(k for t, k in tallies if t == s)
        if sorted(k for t, k in tallies if t == s) != list(range(1, n + 1)):
            raise ValueError(f"{path.name}: rounds of seat {s} are not numbered 1..{n}")
        rounds[s] = [{"tallies": tallies[s, k], "exhausted": exhausted.get((s, k))} for k in range(1, n + 1)]
    return Published(sources, rounds, threshold, elected, dict(lots), first_marks, seated)


## Comparing ---------------------------------------------------------------------------------------------------------

def _show(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{float(x):.4f}".rstrip("0").rstrip(".")


def fold(rounds: list) -> list:
    """Drop a round whose figures repeat the round before it (a candidate on 0 votes aside): it moves nothing."""
    out: list = []
    for r in rounds:
        if out and _nonzero(r) == _nonzero(out[-1]):
            continue
        out.append(r)
    return out


def _nonzero(r: dict) -> dict:
    return {c: v for c, v in r["tallies"].items() if v != 0}


def _inactive(rd: dict) -> Fraction:
    return sum(rd["inactive"].values(), Fraction(0))


def compare(ours: dict, pub: Published, groups: Counter) -> dict:
    """Differences between our count and the published rounds: winners, round 1, every round. [] means a match."""
    diffs: list = []
    first_ok = True
    by_seat: dict = defaultdict(list)
    for rd in ours["rounds"]:
        by_seat[rd.get("seat", 1)].append(rd)
    ours_n = pub_n = 0
    for seat, theirs_all in sorted(pub.rounds.items()):
        mine_all = by_seat.get(seat, [])
        base = _inactive(mine_all[0]) if mine_all else Fraction(0)
        mine = fold([{"tallies": rd["tallies"], "exhausted": _inactive(rd) - base, "after": rd["after_decision"]}
                     for rd in mine_all])
        theirs = fold(theirs_all)
        while len(mine) > len(theirs) and mine[-1]["after"]:  # counted on past the decision, which the source does not print
            mine.pop()
        ours_n, pub_n = ours_n + len(mine), pub_n + len(theirs)
        tag = f"seat {seat} " if pub.seated else ""
        if len(mine) != len(theirs) and not (pub.first_marks and len(theirs) == 1):
            diffs.append(f"{tag}rounds: ours {len(mine)}, published {len(theirs)}")
        for k, (m, t) in enumerate(zip(mine, theirs), 1):
            marks_round = pub.first_marks and k == 1
            if marks_round:
                first = Counter()
                for ballot, n in groups.items():
                    if ballot and ballot[0] not in (None, OVERVOTE):
                        first[ballot[0]] += n
                got = {c: Fraction(n) for c, n in first.items()}
            else:
                got = m["tallies"]
            for c in sorted(set(got) | set(t["tallies"])):
                a, b = got.get(c, Fraction(0)), t["tallies"].get(c, Fraction(0))
                if a != b:
                    diffs.append(f"{tag}{'first marks' if marks_round else f'round {k}'} {c}: ours {_show(a)}, published {_show(b)}")
                    first_ok = first_ok and k != 1
            if t["exhausted"] is not None and not marks_round and m["exhausted"] != t["exhausted"]:
                diffs.append(f"{tag}round {k} (exhausted): ours {_show(m['exhausted'])}, published {_show(t['exhausted'])}")
        if pub.first_marks and len(theirs) == 1 and len(mine) > 1:
            diffs.append(f"published count ends in round 1, ours took {len(mine)} rounds")
    if pub.threshold is not None and not pub.first_marks:
        ours_th = ours["rounds"][0]["threshold"] if ours["rounds"] else None
        if ours_th != pub.threshold:
            diffs.append(f"threshold: ours {_show(ours_th) if ours_th is not None else 'none'}, published {_show(pub.threshold)}")
    winners = sorted(ours["elected"]) == sorted(pub.elected)
    if not winners:
        diffs.append(f"elected: ours {sorted(ours['elected'])}, published {sorted(pub.elected)}")
    return {"winners": winners, "first_round": first_ok, "diffs": diffs, "our_rounds": ours_n, "published_rounds": pub_n}


## Running ---------------------------------------------------------------------------------------------------------

WINNERS = {"yes": "match", "no": "DIFFER", "": "not counted"}
RESULT_COLUMNS = ["table", "rule_set", "seats", "published_rounds", "our_rounds", "winners_match", "first_round_match",
                  "every_figure_match", "status", "differences", "first_difference", "flags", "class", "reason"]


def recount_table(table: str, design: dict, rules: list[dict], values: list[dict], tables_dir: Path, published_dir: Path,
                  only_rule_set: str | None = None, json_out: Path | None = None) -> dict:
    """One line of the results file. A count that cannot be made is a warning with the cause; a missing file raises OSError."""
    pub = read_published(published_dir / f"{table}.csv")
    row = {r["rule_set"]: r for r in rules}[only_rule_set] if only_rule_set else rule_row(design, rules)
    out = {c: "" for c in RESULT_COLUMNS}
    out |= {"table": table, "rule_set": row["rule_set"], "seats": design["seats"]}
    path = tables_dir / f"{table}.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        if not design["seats"].isdigit():
            raise ValueError(f"seats is {design['seats']!r} in the design row")
        seats = int(design["seats"])
        groups = ballots_of(read_table(path), int(design["n_positions"]), int(design["n_ballots_cast"]))
        inputs: dict = {}
        for v in values:
            if v["table"] == table and v["quantity"] == "writein_filed":
                inputs["writein_filed"] = {"yes": True, "no": False}[v["value"]]
        if pub.seated:
            inputs["lots"] = {f"seat{s}": l for s, l in pub.lots.items()}
        else:
            inputs["lots"] = pub.lots.get(1, {})
        count_on = pub.seated or (seats == 1 and len(fold(pub.rounds.get(1, []))) > 1)
        res = count(row, groups, {**design, "table": table}, inputs, count_on)
    except (ValueError, KeyError) as e:
        out |= {"published_rounds": sum(len(fold(r)) for r in pub.rounds.values()), "every_figure_match": "no", "status": "warning",
                "flags": "CANNOT_COUNT", "differences": "", "first_difference": f"cannot count: {e}"}
        return out
    cmp = compare(res, pub, groups)
    flags = list(res["flags"])
    unresolved = any("UNRESOLVED_TIE" in f for f in flags)
    by_lot = any(f.startswith("LOT ") or " LOT " in f for f in flags)
    matched = not cmp["diffs"] and not unresolved
    out |= {"published_rounds": cmp["published_rounds"], "our_rounds": cmp["our_rounds"],
            "winners_match": "yes" if cmp["winners"] else "no", "first_round_match": "yes" if cmp["first_round"] and not unresolved else "no",
            "every_figure_match": "yes" if matched else "no",
            "status": "warning" if not matched else ("match_by_lot" if by_lot else "match"),
            "differences": len(cmp["diffs"]), "first_difference": cmp["diffs"][0] if cmp["diffs"] else "",
            "flags": "; ".join(flags)}
    if json_out:
        json_out.mkdir(parents=True, exist_ok=True)
        (json_out / f"{table}.json").write_text(json.dumps(res, default=lambda x: f"{x.numerator}/{x.denominator}",
                                                           indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Recount ranked-choice tables against their published rounds.")
    ap.add_argument("tables", nargs="*", help="table names")
    ap.add_argument("--all", action="store_true", help="every table with a file in the published folder")
    ap.add_argument("--prefix", default="", help="the published tables whose name starts with this")
    ap.add_argument("--tables-dir", required=True, type=Path)
    ap.add_argument("--published-dir", type=Path, default=HERE / "published_rounds")
    ap.add_argument("--design", type=Path, default=HERE / "design_tables.csv")
    ap.add_argument("--counting-rules", type=Path, default=HERE / "counting_rules.csv")
    ap.add_argument("--counting-values", type=Path, default=HERE / "counting_values.csv")
    ap.add_argument("--reasons", type=Path, default=HERE / "recount_reasons.csv",
                    help="table,class,reason: why a table is known to differ (read when present)")
    ap.add_argument("--rules", help="count every table under this rule set instead of the one its design row joins")
    ap.add_argument("--results", type=Path, help="write one line per table to this CSV")
    ap.add_argument("--json-out", type=Path, help="write <table>.json (exact tallies) into this folder")
    args = ap.parse_args(argv)

    design = {r["table"]: r for r in read_csv(args.design)}
    rules, values = read_csv(args.counting_rules), read_csv(args.counting_values)
    reasons = {r["table"]: r for r in read_csv(args.reasons)} if args.reasons.exists() else {}
    if args.rules and args.rules not in {r["rule_set"] for r in rules}:
        ap.error(f"--rules {args.rules!r} is not a rule_set of {args.counting_rules.name}")
    names = list(args.tables)
    if args.all or args.prefix:
        names += sorted(p.stem for p in args.published_dir.glob("*.csv") if p.stem.startswith(args.prefix))
    if not names:
        print("no tables selected: give table names, --prefix or --all", file=sys.stderr)
        return 2
    lines, missing = [], 0
    for t in names:
        try:
            if t not in design:
                raise ValueError(f"{t}: no design row")
            line = recount_table(t, design[t], rules, values, args.tables_dir, args.published_dir, args.rules, args.json_out)
        except (OSError, ValueError) as e:
            print(f"{t}: cannot start ({e})", file=sys.stderr)
            missing += 1
            continue
        if line["status"] == "warning":
            line["class"] = reasons.get(t, {}).get("class", "unexplained")
            line["reason"] = reasons.get(t, {}).get("reason", "")
        lines.append(line)
        if line["status"] == "warning":
            print(f"WARNING {t} ({line['rule_set']}): {line['first_difference']}"
                  f" [{line['differences'] or 0} differences, winners {WINNERS[line['winners_match']]}, {line['class']}]")
    if args.results:
        with open(args.results, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, RESULT_COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(lines, key=lambda r: r["table"]))
    n = len(lines)
    stat = Counter(r["status"] for r in lines)
    print(f"recount: {n} table(s): {stat['match']} match, {stat['match_by_lot']} match by lot, {stat['warning']} warnings; "
          f"winners match on {sum(r['winners_match'] == 'yes' for r in lines)}/{n}; {missing} not counted")
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
