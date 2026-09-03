"""Draw a random sample from the reachable-untagged population (#1704, item 2).

The population is defined exactly as the issue's "Corrected 2026-09-03" block
defines it, and this script reproduces that block's table before sampling so a
drift in `tags.csv` shows up as a changed count rather than as a silently
different frame:

    no tag row at all              1,031
  + tag row, but only a derived    +  393   (age range / child age only)
    age value in it
  = reachable untagged             1,424

`metadata.csv` and `tags.csv` are joined on LOWERCASED table names -- 307 rows
in `metadata.csv` are not lowercase and drop silently from a case-sensitive
join -- and the literal string "NA" counts as blank, not as a value.

The warehouse shard comes from `metadata.csv`'s `dataset` column.

Usage:
    python3 sample_untagged.py --shards 3,4 --n 150 --seed 1704 --out sample.json
    python3 sample_untagged.py --census          # print the table, sample nothing
"""

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
METADATA = REPO / "metadata" / "metadata.csv"
TAGS = REPO / "metadata" / "tags.csv"

# The columns a human or the tagger fills in. A row carrying none of these is
# substantively untagged however many age values the derivation put in it.
SUBSTANTIVE = [
    "sample",
    "construct type",
    "measurement tool",
    "item format",
    "primary language(s)",
    "construct name",
]
AGE = ["age range", "child age (for child-focused studies)"]

SHARD_LABEL = {
    "item_response_warehouse": "w1",
    "item_response_warehouse_2": "w2",
    "item_response_warehouse_3": "w3",
    "item_response_warehouse_4": "w4",
    "item_response_warehouse_5": "w5",
    "item_response_warehouse_6": "w6",
}


def blank(value):
    return value is None or value.strip() in ("", "NA")


def classify():
    """Every table in metadata.csv, bucketed into the issue's populations."""
    shard = {}
    for row in csv.DictReader(METADATA.open()):
        shard[row["table"].lower()] = SHARD_LABEL.get(row["dataset"], row["dataset"])

    tagged = {}
    for row in csv.DictReader(TAGS.open()):
        tagged[row["table"].lower()] = row

    buckets = defaultdict(list)
    for table, w in sorted(shard.items()):
        row = tagged.get(table)
        if row is None:
            bucket = "no_tag_row"
        elif any(not blank(row[c]) for c in SUBSTANTIVE):
            bucket = "tagged"
        elif any(not blank(row[c]) for c in AGE):
            bucket = "derived_age_only"
        else:
            bucket = "empty_row"
        buckets[bucket].append((table, w))
    return buckets


def census(buckets):
    shards = ["w1", "w2", "w3", "w4", "w5", "w6"]
    order = ["tagged", "derived_age_only", "no_tag_row", "empty_row"]
    print(f"{'population':<20}{'total':>7}" + "".join(f"{s:>7}" for s in shards))
    for bucket in order:
        counts = Counter(w for _, w in buckets[bucket])
        row = "".join(f"{counts.get(s, 0):>7}" for s in shards)
        print(f"{bucket:<20}{len(buckets[bucket]):>7}{row}")
    target = buckets["no_tag_row"] + buckets["derived_age_only"]
    counts = Counter(w for _, w in target)
    row = "".join(f"{counts.get(s, 0):>7}" for s in shards)
    print(f"{'REACHABLE UNTAGGED':<20}{len(target):>7}{row}")
    return target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", default="", help="comma-separated, e.g. 3,4")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--seed", type=int, required=False)
    ap.add_argument("--out")
    ap.add_argument("--census", action="store_true")
    args = ap.parse_args()

    buckets = classify()
    target = census(buckets)
    if args.census or not args.n:
        return

    if args.seed is None:
        sys.exit("--seed is required: the draw has to be reproducible")

    wanted = {f"w{s.strip()}" for s in args.shards.split(",") if s.strip()}
    frame = [(t, w) for t, w in target if not wanted or w in wanted]
    frame.sort()  # a stable frame order is what makes the seed mean anything
    print(f"\nframe: {len(frame)} tables in {sorted(wanted) or 'all shards'}")

    if args.n > len(frame):
        sys.exit(f"asked for {args.n} of {len(frame)}")
    drawn = random.Random(args.seed).sample(frame, args.n)
    drawn.sort()
    print(f"drawn: {args.n} with seed={args.seed} -> {dict(Counter(w for _, w in drawn))}")

    if args.out:
        payload = [{"table": t, "shard": w} for t, w in drawn]
        Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
