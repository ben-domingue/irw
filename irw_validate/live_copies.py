"""How many times does each `id`+`item` repeat? The shape, not the total.

    python3 -m irw_validate.live_copies TABLE [...] -o results/copies.csv
    python3 -m irw_validate.live_copies --from-file tables.txt -o out.csv --resume

`live_dup.py` answers "how many rows are excess". That number cannot tell apart
two tables that need opposite fixes:

    number_pattern_game   every pair appears exactly 30 times   -> 30 trials
    5personalityfactors   624,260 pairs once, 1,260 twice       -> duplication

Both are "mostly excess rows" by `excess_pair`. One is a design and deduping it
destroys 94% of the data; the other is a defect. The histogram of copies per
pair separates them at a glance, and it is an aggregate, so it costs no export
quota.

How to read it:

* **A single spike at n>1** -- every pair repeating the same number of times --
  is a design with n trials, nodes or waves, and an occasion column that was
  dropped or never carried. `ravens_deboeck2012` is 2x5,811 (two tree nodes);
  `motion` is 10x3,180; `number_pattern_game` is 30x9,088. **Never dedupe
  these.**
* **A long tapering tail from 1** -- most pairs once, fewer twice, fewer still
  three times -- is repeated measurement: a wave structure, an experience
  sample, a spaced-repetition trace. `KTEEM_Schoen_2019-2022` is 1..5 (four
  years of waves); `SAS_Deters_2022` is 1..14; the `duolingo_*` tables run to
  22. **Also not a dedupe.**
* **A dominant 1 with a small tail at exactly 2** is duplication or an id
  collision -- something happened to a handful of rows, not to the design.
  `5personalityfactors`, `realpic_souza2021` (4,116 and 28), the
  `PROMISPME_*_Proxy` tables (53,928 and 56).

**The shape alone is not enough**, and this module got that wrong first time
round. `florida_twins_behavior_cads` and `ravens_deboeck2012` have the identical
histogram -- every pair exactly twice, no singletons -- and need opposite
treatment. The second column is whether the copies ever *disagree*: ravens
conflicts on 2,977 of its 5,811 pairs because the two rows are two different
tree nodes; florida_twins conflicts on **0 of 78,146** because they are one
measurement written twice. The same cohort settles it -- the
separately-processed `florida_twins_cads` carries the same instrument and
disagrees on 51.6% of its repeated pairs.

So both columns, always: the histogram says whether repetition is systematic,
the conflict share says whether the repeats are separate measurements.

The trap this exists to close: `excess_exact > 0` does **not** mean a table
holds duplicates. In a repeated-measures design a person answering the same
item the same way twice is byte-identical and entirely real. Three of block H's
"dedupe then chase the residual" tables turned out to be this, and deduping
`number_pattern_game` on that verdict would have thrown away 255,155 real
trials.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import sys
import time

FIELDS = ["table", "ref", "n_pairs", "max_copies", "share_singletons",
          "modal_copies", "repeated_pairs", "conflicting_pairs", "conflict_share",
          "shape", "histogram", "error"]


def classify(hist: list[tuple[int, int]], conflict_share=None,
             repeated_pairs=0) -> str:
    """A first read. Advisory -- look at the histogram and the conflicts.

    **The shape alone is not enough, and mistaking that is how a real fix goes
    wrong.** `florida_twins_behavior_cads` and `ravens_deboeck2012` have the
    identical histogram -- every pair exactly twice, no singletons -- and need
    opposite treatment. What separates them is whether the two copies ever
    disagree: ravens conflicts on 2,977 of 5,811 pairs because its two rows are
    two different tree nodes, while florida_twins conflicts on **0 of 78,146**
    because its two rows are the same measurement written twice.

    Zero disagreement across tens of thousands of pairs is duplication. People
    vary when you measure them twice, and the same cohort proves it: the
    separately-processed `florida_twins_cads` holds the same instrument and
    disagrees on 51.6% of its repeated pairs.
    """
    if not hist:
        return ""
    total = sum(n for _, n in hist)
    ones = dict(hist).get(1, 0)
    unanimous = (conflict_share == 0 and repeated_pairs >= 1000)
    if len(hist) == 1 and hist[0][0] > 1:
        if unanimous:
            return (f"duplication: every pair repeats exactly {hist[0][0]}x and "
                    f"none of {repeated_pairs:,} ever disagrees")
        return f"design: every pair repeats exactly {hist[0][0]}x"
    if ones / total < 0.5:
        if unanimous:
            return (f"duplication: most pairs repeat but none of "
                    f"{repeated_pairs:,} disagrees")
        return "repeated measurement: most pairs repeat"
    if max(c for c, _ in hist) <= 2:
        return "duplication or id collision: a tail at 2 only"
    return "mixed: a tail beyond 2 with most pairs single"


def measure(redivis, idx: dict, table: str) -> dict:
    rec = {"table": table, "error": ""}
    try:
        refs = idx.get(table)
        if not refs:
            rec["error"] = "not found in any core shard (renamed, or not published)"
            return rec
        ref = refs[0]
        rec["ref"] = ref
        sql = f"""
        WITH g AS (
          SELECT CAST(`id` AS STRING) i, CAST(`item` AS STRING) it, COUNT(*) c,
                 COUNT(DISTINCT IFNULL(CAST(`resp` AS STRING),'<<NULL>>')) dr
          FROM `{ref}` GROUP BY i, it)
        SELECT c AS copies, COUNT(*) AS n_pairs, SUM(IF(dr > 1, 1, 0)) AS n_conflicting
        FROM g GROUP BY c ORDER BY c"""
        for attempt in range(4):
            try:
                rows = redivis.query(sql).to_arrow_table(progress=False).to_pylist()
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
        hist = [(r["copies"], r["n_pairs"]) for r in rows]
        total = sum(n for _, n in hist)
        rec["n_pairs"] = total
        rec["max_copies"] = max(c for c, _ in hist) if hist else ""
        rec["share_singletons"] = (round(dict(hist).get(1, 0) / total, 5)
                                   if total else "")
        rec["modal_copies"] = max(hist, key=lambda x: x[1])[0] if hist else ""
        # Repetition without disagreement is duplication; the shape cannot say
        # that on its own. See classify().
        rep = sum(r["n_pairs"] for r in rows if r["copies"] > 1)
        con = sum(r["n_conflicting"] for r in rows if r["copies"] > 1)
        rec["repeated_pairs"] = rep
        rec["conflicting_pairs"] = con
        rec["conflict_share"] = round(con / rep, 5) if rep else ""
        rec["shape"] = classify(hist, rec["conflict_share"], rep)
        rec["histogram"] = "|".join(f"{c}:{n}" for c, n in hist)
    except Exception as exc:
        rec["error"] = str(exc)[:300]
    return rec


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("tables", nargs="*")
    p.add_argument("--from-file", help="file of table names, one per line")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--resume", action="store_true")
    a = p.parse_args(argv)

    tables = list(a.tables)
    if a.from_file:
        tables += [ln.strip() for ln in open(a.from_file) if ln.strip()]
    if not tables:
        p.error("give table names, or --from-file")

    if hasattr(os, "nice") and os.nice(0) < 10:
        print("note: this machine runs other people's work -- consider nice -n 19",
              file=sys.stderr)

    src_root = pathlib.Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(src_root))
    import redivis_shim
    redivis_shim.install()
    from irw_validate.live_dup import _authenticate, shard_index
    redivis = _authenticate(src_root)
    idx = shard_index(redivis, pathlib.Path(a.out).parent / ".shard_index.json")

    done = set()
    if a.resume and os.path.exists(a.out):
        done = {r["table"] for r in csv.DictReader(open(a.out))}
    fresh = not os.path.exists(a.out) or not a.resume
    with open(a.out, "w" if fresh else "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if fresh:
            w.writeheader()
        for i, t in enumerate(tables, 1):
            if t in done:
                print(f"[{i}/{len(tables)}] {t} (done)")
                continue
            rec = measure(redivis, idx, t)
            w.writerow({k: rec.get(k, "") for k in FIELDS})
            f.flush()
            print(f"[{i}/{len(tables)}] {t} max={rec.get('max_copies')} "
                  f"singletons={rec.get('share_singletons')} "
                  f"conflict={rec.get('conflict_share')} "
                  f"{rec.get('shape', '')} {rec['error'][:50]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
