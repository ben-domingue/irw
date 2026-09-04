"""Draw the 40-table head-to-head frame for the two-path comparison (#1704).

Twenty tables where no gold exists -- the population the tagger would actually
run on, so reachability, abstention and fill are what can be measured -- and
twenty human-tagged tables where accuracy can be.

Both halves are stratified by warehouse rather than drawn from the pool. The
2026-09-01 Arm B run found reachability varying from 30% (w2) to 100% (w3), so
a pooled draw of twenty would confound the two paths with the shard mix each
happened to get. Stratifying is the only way forty tables can separate anything.

  untagged   5 each from w2, w3, w4, w5   (w1 is 99.9% tagged; nothing to draw)
  gold       5 each from w1, w2, w3, w4   (w5 has only 16 eligible tables)

The two halves are then SHUFFLED TOGETHER and written without a population
label. That is what blinds the comparison: Path A's documented Step 1 tells it
to run `check_table_status.py` and consult existing rows, so an arm that knew
which twenty were gold could read the answer it is being scored against. Both
arms get the same unlabelled forty. The key stays here.

Gold for `age_range` is NOT the sheet. ~90% of its `Mixed` labels are
contradicted by the table's own `cov_age` (#1760), so the key records the
`age_range_derived.csv` value where one exists and leaves it absent otherwise.

Usage:
    python3 draw_comparison.py --seed 20260903
"""

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SUBSTANTIVE = ["sample", "construct type", "measurement tool", "item format",
               "primary language(s)", "construct name"]
AGE = ["age range", "child age (for child-focused studies)"]
# The four columns #1704 clears for publication. Gold must answer all four for a
# table to be usable in the accuracy half.
PUBLISHED = ["primary language(s)", "item format", "sample", "measurement tool"]

SHARD = {"item_response_warehouse": "w1", "item_response_warehouse_2": "w2",
         "item_response_warehouse_3": "w3", "item_response_warehouse_4": "w4",
         "item_response_warehouse_5": "w5", "item_response_warehouse_6": "w6"}


def blank(v):
    return v is None or v.strip() in ("", "NA")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--per-shard", type=int, default=5)
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()

    meta = {r["table"].lower(): SHARD.get(r["dataset"], r["dataset"])
            for r in csv.DictReader((REPO / "metadata/metadata.csv").open())}
    tags = {r["table"].lower(): r
            for r in csv.DictReader((REPO / "metadata/tags.csv").open())}
    auto = {r["table"].lower()
            for r in csv.DictReader((REPO / "tags/tags_auto.csv").open())}
    derived = {r["table"].lower(): r
               for r in csv.DictReader((REPO / "tags/age_range_derived.csv").open())}

    untagged, gold = defaultdict(list), defaultdict(list)
    for table, shard in sorted(meta.items()):
        row = tags.get(table)
        if row is None:
            untagged[shard].append(table)                       # no tag row
        elif not any(not blank(row[c]) for c in SUBSTANTIVE):
            if any(not blank(row[c]) for c in AGE):
                untagged[shard].append(table)                   # derived age only
        elif table not in auto and all(not blank(row[c]) for c in PUBLISHED):
            gold[shard].append(table)                           # human-tagged

    rng = random.Random(args.seed)
    drawn = []
    for label, pool, shards in [("untagged", untagged, ["w2", "w3", "w4", "w5"]),
                                ("gold", gold, ["w1", "w2", "w3", "w4"])]:
        for s in shards:
            picks = rng.sample(sorted(pool[s]), args.per_shard)
            drawn += [{"table": t, "shard": s, "population": label} for t in picks]
            print(f"{label:<9}{s}  {args.per_shard} of {len(pool[s])}")

    rng.shuffle(drawn)   # the arms must not be able to tell the halves apart

    out = Path(args.outdir)
    (out / "compare_worklist.json").write_text(json.dumps(
        [{"table": d["table"]} for d in drawn], indent=1) + "\n")

    key = []
    for d in drawn:
        row = tags.get(d["table"], {})
        entry = dict(d)
        if d["population"] == "gold":
            entry["gold"] = {c: row.get(c, "") for c in PUBLISHED + ["construct type"]}
        dv = derived.get(d["table"])
        # The only trustworthy age_range gold, and only where cov_age supplied one.
        entry["age_range_derived"] = dv["age range"] if dv else None
        key.append(entry)
    (out / "compare_key.json").write_text(json.dumps(key, indent=1) + "\n")

    print(f"\n{len(drawn)} tables, seed={args.seed}, shuffled")
    print("worklist (unlabelled, given to both arms): compare_worklist.json")
    print("key (population + gold + derived age):     compare_key.json")
    print("age_range gold available for",
          sum(1 for k in key if k["age_range_derived"]), "of", len(key))
    print("population mix:", dict(Counter(d["population"] for d in drawn)))


if __name__ == "__main__":
    main()
