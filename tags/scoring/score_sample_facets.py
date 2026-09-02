#!/usr/bin/env python3
"""Score `sample` per FACET, which is the only way it can be scored at all
against the current gold (#1722, 2026-09-01).

#1760 established that `sample` is two questions in one column: SETTING (how
were these people reached) and FRAME (how broad was the sampling). The gold set
predates that split, and 12 of 34 gold rows carry no frame value at all -- the
raters answered one question. The tagger, following the rewritten vocab.md, now
answers both: it produced a frame value on 33 of 34 tables against 19 of 38
before.

Whole-cell exact match therefore PUNISHES the tagger for filling a facet the
gold leaves blank, and it fell from 44.4% to 18.2% between the two runs for
exactly that reason. That number is an artifact of comparing a two-facet answer
to a one-facet key, not a regression.

So: score each facet only on the tables where GOLD ANSWERED THAT FACET. A gold
blank is missing data for that facet, not a value of it.

    python3 score_sample_facets.py predictions_A.json [predictions_B.json ...]
"""
import collections
import csv
import json
import sys

GOLD = "/home/ben/Dropbox/projects/irw/src/metadata/tags.csv"
SETTING = {"Educational", "Clinical", "Program-based", "Internet-based", "Non-human"}
FRAME = {"Representative", "Targeted/specific", "General/non-specific"}


def atoms(v):
    if not v:
        return set()
    v = v.replace('"', "").replace("Internet-based (Mturkers, etc)", "Internet-based")
    return {a.strip() for a in v.split(",") if a.strip() and a.strip().upper() != "NA"}


def main(paths):
    gold = {r["table"].strip().lower(): r for r in csv.DictReader(open(GOLD))}
    for path in paths:
        preds = json.load(open(path))
        facets = {"setting": collections.Counter(), "frame": collections.Counter()}
        n = gold_frame = pred_frame = 0
        for p in preds:
            if p.get("status") != "tagged":
                continue
            g = gold.get(p["table"].strip().lower())
            if not g:
                continue
            n += 1
            ga, pa = atoms(g.get("sample")), atoms(p.get("sample"))
            gold_frame += bool(ga & FRAME)
            pred_frame += bool(pa & FRAME)
            for name, keys in (("setting", SETTING), ("frame", FRAME)):
                gk, pk = ga & keys, pa & keys
                if not gk:            # gold did not answer this facet
                    continue
                c = facets[name]
                c["n"] += 1
                c["exact"] += (gk == pk)
                c["tp"] += len(gk & pk)
                c["fp"] += len(pk - gk)
                c["fn"] += len(gk - pk)

        print(f"\n{path}  --  {n} tables with gold")
        print(f"  gold answers the frame facet on {gold_frame}/{n}; "
              f"the prediction does on {pred_frame}/{n}")
        for name in ("setting", "frame"):
            c = facets[name]
            if not c["n"]:
                continue
            prec = c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else 0.0
            rec = c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else 0.0
            print(f"  {name:8s} n={c['n']:3d}  exact {100*c['exact']/c['n']:5.1f}%"
                  f"   precision {100*prec:5.1f}%   recall {100*rec:5.1f}%")


if __name__ == "__main__":
    main(sys.argv[1:])
