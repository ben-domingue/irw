"""Put the two tagging paths' output side by side on the same 40 tables (#1704).

Neither path is modified by this script. It exists because they cannot be
compared without an adapter, and that fact is one of the findings:

  * `score.py` skips any prediction whose `status` is not `"tagged"`, and takes
    a second file mapping each table to a `warehouse`. The skill's own output --
    the payload `stage_tag_row.py` consumes -- models neither field. Run
    `score.py` over it unadapted and every row is silently skipped.
  * `score_sample_facets.py` has the same `status` guard.

So Path B's scoring machinery cannot read Path A's output at all. The adapter
below is small, which is the point: what separates the paths at the output
boundary is two bookkeeping fields, not a different answer.

`status` is recomputed identically for BOTH arms -- tagged iff any tag field is
non-blank -- rather than trusted from Path B's self-report, so the two arms are
held to one definition. Where Path B's self-reported status disagrees with the
recomputed one, that is printed rather than silently resolved.

`age_range` is scored against `tags/age_range_derived.csv`, never the sheet:
~90% of the sheet's `Mixed` labels are contradicted by the table's own
`cov_age` (#1760), so the sheet is not gold for that column.

TWO THINGS THIS RUN CANNOT MEASURE, both disclosed rather than worked around:

1. REACHED and ANSWERED are not the same event, and the arms report them
   unequally. Agents in both arms filled fields from the Data Dictionary's
   description sentence when the fetch itself had failed -- Step 2 permits it
   ("useful context even without a doi") -- so a table can be `tagged` with no
   source ever read. Path B records `fetch_outcome` and this is visible in its
   output; the skill's payload has no such field, so PATH A CANNOT DISTINGUISH
   A TAG READ FROM THE PAPER FROM A TAG READ FROM THE CATALOGUE BLURB. That is
   reported as an asymmetry, not averaged away.

2. Both arms ran in one worktree and therefore shared `.cache/`. fetch_source.py
   caches by table name, so whichever arm reached a table first warmed the cache
   for the other. Per-ARM reachability is consequently not identifiable here.
   What is identifiable is per-TABLE reachability -- which the cache measures
   directly, path-independently, and is reported below -- and each arm's
   willingness to commit a value given the same fetched text. Since both paths
   invoke the SAME fetcher, per-arm reachability was never the live question;
   the confound costs little, but it is real and it is stated.

Usage:
    python3 compare_paths.py --key compare_key.json \
        --arm-a armA_1.json armA_2.json --arm-b armB_1.json armB_2.json ...
"""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

TAG_FIELDS = ["age_range", "child_age", "sample", "construct_type",
              "measurement_tool", "item_format", "primary_languages",
              "construct_name"]
PUBLISHED = ["primary_languages", "item_format", "sample_setting", "measurement_tool"]
HELD = ["construct_type", "sample_frame", "construct_name", "age_range", "child_age"]

FRAME_ATOMS = {"Representative", "Targeted/specific", "General/non-specific"}
SETTING_ATOMS = {"Educational", "Clinical", "Program-based", "Non-human",
                 "Internet-based", "Internet-based (Mturkers, etc)"}


def blank(v):
    return not (v or "").strip() or (v or "").strip().upper() == "NA"


def facets(value):
    atoms = [a.strip() for a in (value or "").split(",") if a.strip()]
    # `Internet-based (Mturkers, etc)` carries a literal comma; rejoin it.
    fixed, i = [], 0
    while i < len(atoms):
        if atoms[i] == "Internet-based (Mturkers" and i + 1 < len(atoms):
            fixed.append("Internet-based"); i += 2
        else:
            fixed.append(atoms[i]); i += 1
    return ([a for a in fixed if a in SETTING_ATOMS],
            [a for a in fixed if a in FRAME_ATOMS])


def load_arm(paths, arm, key):
    rows, disagree = [], []
    for p in paths:
        for r in json.loads(Path(p).read_text()):
            t = r["table"].strip().lower()
            k = key.get(t, {})
            rec = {f: (r.get(f) or "").strip() for f in TAG_FIELDS}
            rec["table"], rec["arm"] = t, arm
            rec["shard"] = k.get("shard", "?")
            rec["population"] = k.get("population", "?")
            rec["notes"] = (r.get("notes") or "").strip()
            rec["status"] = "tagged" if any(not blank(rec[f]) for f in TAG_FIELDS) \
                else "abstained"
            rec["reason"] = (r.get("reason") or rec["notes"]).strip()
            rec["fetch_outcome"] = (r.get("fetch_outcome") or "").strip()
            setting, frame = facets(rec["sample"])
            rec["sample_setting"], rec["sample_frame"] = ", ".join(setting), ", ".join(frame)
            if r.get("status") and r["status"] != rec["status"]:
                disagree.append((t, arm, r["status"], rec["status"]))
            rows.append(rec)
    return rows, disagree


def pct(a, b):
    return f"{100*a/b:5.1f}%" if b else "    --"


def table(rows_by_arm, groups, group_of, title, arms):
    print(f"\n{title}")
    print(f"{'':<22}" + "".join(f"{a:>22}" for a in arms))
    print(f"{'':<22}" + "".join(f"{'reached':>11}{'abstain':>11}" for a in arms))
    for g in groups:
        line = f"{g:<22}"
        for a in arms:
            sub = [r for r in rows_by_arm[a] if group_of(r) == g]
            n = sum(1 for r in sub if r["status"] == "tagged")
            line += f"{pct(n, len(sub)):>11}{len(sub)-n:>11}"
        print(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--arm-a", nargs="+", required=True)
    ap.add_argument("--arm-b", nargs="+", required=True)
    args = ap.parse_args()

    key = {k["table"].strip().lower(): k
           for k in json.loads(Path(args.key).read_text())}
    a_rows, d1 = load_arm(args.arm_a, "A skill", key)
    b_rows, d2 = load_arm(args.arm_b, "B harness", key)
    arms = ["A skill", "B harness"]
    by_arm = {"A skill": a_rows, "B harness": b_rows}

    for a in arms:
        print(f"{a}: {len(by_arm[a])} rows, {len({r['table'] for r in by_arm[a]})} distinct tables")

    table(by_arm, ["untagged", "gold"], lambda r: r["population"],
          "ANSWERED (any field non-blank) by population", arms)
    table(by_arm, ["w1", "w2", "w3", "w4", "w5"], lambda r: r["shard"],
          "ANSWERED (any field) by shard", arms)

    # Path-independent: did fetch_source.py ever land a source for this table?
    # The cache is shared between the arms, so this is a property of the TABLE.
    cache = REPO / "tags/.claude/skills/irw-auto-tag/.cache"
    cached = {f.stem for f in cache.glob("*.txt")} if cache.exists() else set()
    print("\nSOURCE ACTUALLY FETCHED, per table (from .cache/, path-independent)")
    for grp, of in [("untagged", "population"), ("gold", "population")]:
        tabs = {k["table"] for k in key.values() if k[of] == grp}
        print(f"  {grp:<10}{pct(len(tabs & cached), len(tabs)):>8}  "
              f"({len(tabs & cached)} of {len(tabs)})")
    for sh in ["w1", "w2", "w3", "w4", "w5"]:
        tabs = {k["table"] for k in key.values() if k["shard"] == sh}
        if tabs:
            print(f"  {sh:<10}{pct(len(tabs & cached), len(tabs)):>8}  "
                  f"({len(tabs & cached)} of {len(tabs)})")

    print("\nTAGGED WITHOUT A FETCHED SOURCE -- values taken from the dictionary")
    for a in arms:
        n = [r for r in by_arm[a]
             if r["status"] == "tagged" and r["table"] not in cached]
        print(f"  {a:<12}{len(n):>3}   " + ", ".join(r["table"] for r in n[:6]))
    print("  Path A's payload has no fetch_outcome field, so on its own output")
    print("  this distinction is not recoverable at all -- see the docstring.")

    print("\nFETCH OUTCOME as each arm reported it (Path A: field not modelled)")
    for a in arms:
        tally = Counter(r["fetch_outcome"] or "(not reported)" for r in by_arm[a])
        print(f"  {a:<12}" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    print("\nABSTENTION reasons")
    for a in arms:
        sub = [r for r in by_arm[a] if r["status"] == "abstained"]
        print(f"  {a}: {len(sub)}")
        for r in sub:
            print(f"     {r['table']:<44}{r['shard']}  {r['reason'][:60] or '(none given)'}")

    print("\nPER-COLUMN FILL, of all 40 (blank = abstention, which vocab.md asks for)")
    print(f"{'column':<20}" + "".join(f"{a:>12}" for a in arms) + f"{'delta':>9}")
    for col in PUBLISHED + ["--"] + HELD:
        if col == "--":
            print("  " + "-"*54 + "  (held, not published)")
            continue
        vals = []
        line = f"{col:<20}"
        for a in arms:
            n = sum(1 for r in by_arm[a] if not blank(r[col]))
            vals.append(100*n/len(by_arm[a]))
            line += f"{pct(n, len(by_arm[a])):>12}"
        print(line + f"{vals[1]-vals[0]:>+8.1f}")

    print("\nAGREEMENT between the arms, table by table, on the four published columns")
    common = {r["table"] for r in a_rows} & {r["table"] for r in b_rows}
    amap = {r["table"]: r for r in a_rows}
    bmap = {r["table"]: r for r in b_rows}
    for col in PUBLISHED:
        both = [t for t in common
                if not blank(amap[t][col]) and not blank(bmap[t][col])]
        same = [t for t in both
                if {x.strip() for x in amap[t][col].split(",")}
                == {x.strip() for x in bmap[t][col].split(",")}]
        print(f"  {col:<20} both answered {len(both):>3}   identical {pct(len(same), len(both))}")

    print("\nage_range vs the cov_age derivation (the only trustworthy gold for it)")
    for a in arms:
        n = ok = 0
        for r in by_arm[a]:
            d = key.get(r["table"], {}).get("age_range_derived")
            if not d or blank(r["age_range"]):
                continue
            n += 1
            ok += (r["age_range"].strip() == d.strip())
        print(f"  {a:<12} answered {n:>3} of the 20 with a derived value   correct {pct(ok, n)}")

    for t, arm, said, got in d1 + d2:
        print(f"\nNOTE status self-report disagrees: {t} ({arm}) said {said!r}, fields say {got!r}")

    out = Path(args.arm_a[0]).parent
    for arm, rows, name in [("A", a_rows, "armA_as_preds.json"),
                            ("B", b_rows, "armB_as_preds.json")]:
        (out / name).write_text(json.dumps(
            [{k: r[k] for k in ["table", "status", "reason"] + TAG_FIELDS}
             for r in rows], indent=1) + "\n")
    # score.py wants a {table, warehouse} sidecar; build it from the key.
    ws = {"w1": "item_response_warehouse", "w2": "item_response_warehouse_2",
          "w3": "item_response_warehouse_3", "w4": "item_response_warehouse_4",
          "w5": "item_response_warehouse_5"}
    (out / "compare_sample_for_score.json").write_text(json.dumps(
        [{"table": k["table"], "warehouse": ws[k["shard"]]}
         for k in key.values()], indent=1) + "\n")
    print("\nwrote armA_as_preds.json, armB_as_preds.json, compare_sample_for_score.json")
    print("now run score.py and score_sample_facets.py over BOTH adapted files")


if __name__ == "__main__":
    main()
