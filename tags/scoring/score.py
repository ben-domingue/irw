#!/usr/bin/env python3
"""Score blind auto-tagger output against the human gold set (#1721 / 2.2).

Gold (metadata/tags.csv) is POST-normalisation: tag_normalize.R splits, dedupes,
sorts and comma-joins the multi-select columns, and renames
"Internet-based (Mturkers, etc)" to "Internet-based". Predictions arrive in sheet
form, so both sides get the same treatment before comparison -- otherwise every
Internet-based row would score as wrong for no reason. Multi-selects compare as
SETS, so "A, B" == "B, A".

A blank prediction is an ABSTENTION, not an error. vocab.md explicitly tells the
tagger to leave a field blank rather than guess, so scoring blanks as wrong would
punish the behaviour we asked for. Three numbers per column instead:

    accuracy = correct / answered         is it right when it commits?
    coverage = answered / gold_available  how often does it commit?
    yield    = correct / gold_available   what you actually get

child_age is reported separately as well: gold is NA for ~80% of rows because the
column only applies to child-focused studies, so there NA is a real answer
meaning "not applicable" and a blank prediction against it is correct.

Set equality is strict, and for the multi-select columns it hides a distinction
that matters: predicting two of a construct's three facets scores the same zero
as naming an unrelated one. So those columns also get a breakdown of HOW they
miss -- subset, superset, partial overlap, or disjoint. sample and
construct_type report near-identical exact-match rates and are not alike:
construct_type mostly disagrees about granularity, while sample mostly picks a
different category outright, because its atoms overlap and vocab.md defines
none of them (see #1760).
"""
import csv, json, sys, html, collections

GOLD = "/home/ben/Dropbox/projects/irw/src/metadata/tags.csv"
COLS = [("age_range", "age range", False),
        ("child_age", "child age (for child-focused studies)", True),
        ("sample", "sample", True),
        ("construct_type", "construct type", True),
        ("measurement_tool", "measurement tool", False),
        ("item_format", "item format", False),
        ("primary_languages", "primary language(s)", True)]
RENAME = {"Internet-based (Mturkers, etc)": "Internet-based",
          "Internet-based (Mturkers": "Internet-based"}
DROP = {"etc)"}


def norm(v, multi):
    """Canonicalise a cell to a comparable frozen set, or None when empty/NA."""
    if v is None:
        return None
    v = html.unescape(str(v)).replace('"', '').strip()
    if v == "" or v.upper() == "NA":
        return None
    for a, b in RENAME.items():
        v = v.replace(a, b)
    atoms = [a.strip() for a in v.split(",")]
    atoms = [a for a in atoms if a and a not in DROP]
    if not atoms:
        return None
    return tuple(sorted(set(atoms)))


def _miss_kind(gv, pv):
    """How a multi-select prediction relates to gold -- not just right/wrong."""
    g, p = set(gv), set(pv)
    if g == p:
        return "exact"
    if p < g:
        return "subset"      # right atoms, missed some
    if p > g:
        return "superset"    # right atoms, added some
    if g & p:
        return "overlap"     # partly right
    return "disjoint"        # nothing in common


def run(pred_path, sample_path):
    gold = {r["table"].strip().lower(): r for r in csv.DictReader(open(GOLD))}
    preds = json.load(open(pred_path))
    sample = {x["table"]: x["warehouse"] for x in json.load(open(sample_path))}

    stats = {p: collections.Counter() for p, _, _ in COLS}
    confusion = {p: collections.Counter() for p, _, _ in COLS}
    per_ws = collections.defaultdict(collections.Counter)
    abst = []

    for pr in preds:
        t = pr["table"].strip().lower()
        ws = sample.get(pr["table"], "?")
        if pr.get("status") != "tagged":
            abst.append((pr["table"], pr.get("reason", ""), ws))
            per_ws[ws]["abstained"] += 1
            continue
        g = gold.get(t)
        if g is None:
            continue
        per_ws[ws]["tables"] += 1
        for pkey, gcol, multi in COLS:
            gv, pv = norm(g.get(gcol), multi), norm(pr.get(pkey), multi)
            s = stats[pkey]
            if pkey == "child_age":
                if gv is None and pv is None:
                    s["na_correct"] += 1
                    continue
                if gv is None and pv is not None:
                    s["na_false_positive"] += 1
                    continue
            if gv is None:
                s["no_gold"] += 1
                continue
            s["gold_available"] += 1
            per_ws[ws]["gold"] += 1
            if pv is None:
                s["abstained"] += 1
                continue
            s["answered"] += 1
            if pv == gv:
                s["correct"] += 1
                per_ws[ws]["correct"] += 1
            else:
                s["wrong"] += 1
                confusion[pkey][(", ".join(gv), ", ".join(pv))] += 1
            if multi:
                s[_miss_kind(gv, pv)] += 1
    return stats, confusion, per_ws, abst, preds


if __name__ == "__main__":
    stats, confusion, per_ws, abst, preds = run(sys.argv[1], sys.argv[2])
    tagged = sum(1 for p in preds if p.get("status") == "tagged")
    pct = 100 * len(abst) / len(preds) if preds else 0
    print(f"tables: {len(preds)} attempted | {tagged} tagged | {len(abst)} abstained "
          f"({pct:.0f}% of the sample had no usable source)\n")

    print(f"{'column':20s} {'gold':>5s} {'ans':>5s} {'ok':>4s} "
          f"{'accuracy':>9s} {'coverage':>9s} {'yield':>7s}")
    print("-" * 64)
    f = lambda n, d: f"{100*n/d:6.1f}%" if d else "     --"
    for pkey, _, _ in COLS:
        s = stats[pkey]
        ga, an, ok = s["gold_available"], s["answered"], s["correct"]
        print(f"{pkey:20s} {ga:5d} {an:5d} {ok:4d} "
              f"{f(ok,an):>9s} {f(an,ga):>9s} {f(ok,ga):>7s}")

    ca = stats["child_age"]
    print("\nchild_age, with NA read as the answer 'not a child-focused study':")
    print(f"  correctly left blank when gold is NA : {ca['na_correct']}")
    print(f"  wrongly filled when gold is NA       : {ca['na_false_positive']}")

    print("\nper-warehouse (all columns pooled, tagged tables only):")
    for ws in sorted(per_ws):
        c = per_ws[ws]
        if c["gold"]:
            print(f"  {ws:28s} {c['tables']:2d} tagged, {c['abstained']:2d} abstained  "
                  f"{c['correct']:3d}/{c['gold']:3d} = {100*c['correct']/c['gold']:5.1f}%")

    multi = [c for c in COLS if c[2]]
    print("\nmulti-select columns -- how they miss, not just whether:")
    print(f"  {'column':20s} {'n':>4s} {'exact':>8s} {'subset':>7s} {'super':>6s} "
          f"{'overlap':>8s} {'disjoint':>9s}  {'>=1 atom':>9s}")
    for pkey, _, _ in multi:
        s = stats[pkey]
        n = sum(s[k] for k in ("exact", "subset", "superset", "overlap", "disjoint"))
        if not n:
            continue
        shared = n - s["disjoint"]
        print(f"  {pkey:20s} {n:4d} {f(s['exact'],n):>8s} {s['subset']:7d} "
              f"{s['superset']:6d} {s['overlap']:8d} {f(s['disjoint'],n):>9s}  "
              f"{f(shared,n):>9s}")
    print("  A subset or superset is a granularity disagreement on a genuinely")
    print("  multi-faceted answer; a disjoint miss is a different answer entirely.")

    print("\nconfusions (gold -> predicted):")
    for pkey, _, _ in COLS:
        if not confusion[pkey]:
            continue
        print(f"  {pkey}:")
        for (g, p), n in confusion[pkey].most_common(6):
            print(f"     {n:2d}x  {g}  ->  {p}")

    if abst:
        print("\nabstained:")
        for t, r, ws in abst:
            print(f"  {t:52s} {r:14s} {ws}")
