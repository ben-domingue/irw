#!/usr/bin/env python3
"""Score the untagged arm of the 2026-09-01 run (2.3, #1722).

The tagged arm (score.py) measures accuracy against human gold. This arm cannot:
these tables have never been tagged, so there is no gold for six of the seven
columns. What it CAN measure is the two things the tagged arm gets wrong by
construction:

  reachability -- can the tagger obtain the source at all, on the population it
                  would actually run on? Every earlier number came from tables a
                  human had already tagged, which selects for reachable sources.
  age_range    -- real accuracy, because #1760's derivation supplies ground
                  truth from the table's own cov_age for any table that has one.

Everything else is reported as COVERAGE (did it commit) with no accuracy figure,
and that is the honest limit of this arm.

    python3 score_untagged.py preds_B1.json preds_B2.json ...
"""
import collections
import csv
import json
import sys

DERIVED = "/home/ben/Dropbox/projects/irw/src/tags/age_range_derived.csv"
SAMPLE = "/home/ben/Dropbox/projects/irw/src/tags/scoring/sample_untagged_2026-09-01.json"
COLS = ["age_range", "child_age", "sample", "construct_type",
        "measurement_tool", "item_format", "primary_languages", "construct_name"]


def main(paths):
    derived = {r["table"].strip().lower(): r["age range"]
               for r in csv.DictReader(open(DERIVED))}
    ws = {x["table"].strip().lower(): x["warehouse"] for x in json.load(open(SAMPLE))}

    preds = []
    for p in paths:
        preds.extend(json.load(open(p)))

    by_ws = collections.defaultdict(collections.Counter)
    reasons = collections.Counter()
    filled = collections.Counter()
    age = collections.Counter()
    age_wrong = []

    for pr in preds:
        t = pr["table"].strip().lower()
        w = ws.get(t, "?")
        by_ws[w]["n"] += 1
        if pr.get("status") != "tagged":
            by_ws[w]["abstained"] += 1
            reasons[pr.get("reason", "unspecified")] += 1
            continue
        by_ws[w]["tagged"] += 1
        for c in COLS:
            v = (pr.get(c) or "").strip()
            if v and v.upper() != "NA":
                filled[c] += 1
        gv = derived.get(t)
        if gv:
            age["gold"] += 1
            pv = (pr.get("age_range") or "").strip()
            if not pv:
                age["abstained"] += 1
            elif pv == gv:
                age["correct"] += 1
            else:
                age["wrong"] += 1
                age_wrong.append((pr["table"], gv, pv))

    n = len(preds)
    tagged = sum(c["tagged"] for c in by_ws.values())
    print(f"untagged arm: {n} tables | {tagged} tagged | {n - tagged} abstained "
          f"({100*(n-tagged)/n:.0f}%)\n")

    print("reachability by warehouse -- the population 2.3 would actually run on:")
    for w in sorted(by_ws):
        c = by_ws[w]
        print(f"  {w:28s} {c['n']:2d} drawn  {c['tagged']:2d} tagged  "
              f"{c['abstained']:2d} abstained  {100*c['tagged']/c['n']:5.1f}% reached")

    print("\nabstention reasons:")
    for r, k in reasons.most_common():
        print(f"  {r:16s} {k:3d}")

    print("\ncolumn coverage among tables it did reach (no accuracy: there is no gold):")
    for c in COLS:
        print(f"  {c:20s} {filled[c]:3d}/{tagged}  {100*filled[c]/tagged:5.1f}%"
              if tagged else f"  {c:20s}   --")

    print("\nage_range accuracy against the cov_age derivation (#1760) -- real gold:")
    if age["gold"]:
        ans = age["correct"] + age["wrong"]
        print(f"  tables with derived truth : {age['gold']}")
        print(f"  answered                  : {ans}")
        print(f"  correct                   : {age['correct']}"
              f"  ({100*age['correct']/ans:.1f}% of answered)" if ans else "")
        for t, g, p in age_wrong:
            print(f"    wrong: {t}  gold {g}  ->  predicted {p}")
    else:
        print("  none of the reached tables has a derived age range")


if __name__ == "__main__":
    main(sys.argv[1:])
