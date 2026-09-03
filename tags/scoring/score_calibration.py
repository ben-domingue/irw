"""Report reachability, per-column fill and abstention for a blind batch (#1704).

There is no gold for these tables -- that is what makes them the target -- so
this scores nothing. It answers the one question the calibration was run to
answer: does the tagger reach w3 and w4 the way #1802 showed it reaches w5?

Reachability and fill are reported SEPARATELY and by shard. A table can be
reached and still leave a column blank, and vocab.md asks for exactly that when
the source does not support a value, so a low fill rate on one column is not a
reachability failure and must not be read as one.

Usage:
    python3 score_calibration.py preds_K*.json
    python3 score_calibration.py --baseline predictions_pilot_w5.json preds_K*.json
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

# Written by the agents. The first four are what #1704 clears for publication;
# the last three are kept for later measurement and blanked before staging.
PUBLISHED = ["primary_languages", "item_format", "sample_setting", "measurement_tool"]
HELD = ["construct_type", "sample_frame", "construct_name", "age_range", "child_age"]

# vocab.md's eight `sample` atoms, split into the two facets #1760 separated.
# Only the SETTING facet publishes; FRAME scored 59.1% per-atom precision under
# the amended rules and is held. Both lists are whitelists rather than one list
# and a complement, so a value outside the vocabulary is reported instead of
# being silently counted as a setting atom.
FRAME_ATOMS = {"Representative", "Targeted/specific", "General/non-specific"}
SETTING_ATOMS = {"Educational", "Clinical", "Program-based", "Non-human",
                 "Internet-based", "Internet-based (Mturkers, etc)",
                 # Added to vocab.md 2026-09-03 (#1704). A setting atom, so it
                 # belongs to the facet that publishes -- omitting it here
                 # understates setting fill rather than erroring, which is what
                 # the unknown-atom warning below exists to catch.
                 "Workplace"}
UNKNOWN_ATOMS = set()

# `Internet-based (Mturkers, etc)` is the sheet form; 03_tags.R renames it on
# export. Both spellings are the same setting atom here.


def facets(sample_value):
    """Split a `sample` cell into (setting atoms, frame atoms)."""
    atoms = [a.strip() for a in (sample_value or "").split(",") if a.strip()]
    UNKNOWN_ATOMS.update(a for a in atoms
                         if a not in FRAME_ATOMS and a not in SETTING_ATOMS)
    return ([a for a in atoms if a in SETTING_ATOMS],
            [a for a in atoms if a in FRAME_ATOMS])


def load(paths):
    rows = []
    for p in paths:
        for r in json.loads(Path(p).read_text()):
            r.setdefault("shard", "?")
            r.setdefault("fetch_outcome", "")
            setting, frame = facets(r.get("sample", ""))
            r["sample_setting"] = ", ".join(setting)
            r["sample_frame"] = ", ".join(frame)
            r["_batch"] = Path(p).stem
            rows.append(r)
    return rows


def filled(row, col):
    return bool((row.get(col) or "").strip())


def pct(a, b):
    return f"{100 * a / b:5.1f}%" if b else "    --"


def report(rows, label):
    shards = sorted({r["shard"] for r in rows})
    print(f"\n=== {label}: {len(rows)} tables ===")

    print("\nreachability -- did the tagger get a usable source at all")
    print(f"{'shard':<8}{'n':>5}{'reached':>10}{'abstained':>11}")
    for s in shards + ["ALL"]:
        sub = [r for r in rows if s == "ALL" or r["shard"] == s]
        reached = sum(1 for r in sub if r.get("status") == "tagged")
        print(f"{s:<8}{len(sub):>5}{pct(reached, len(sub)):>10}"
              f"{len(sub) - reached:>11}")

    print("\nwhy the unreached were unreached")
    for s in shards:
        sub = [r for r in rows if r["shard"] == s]
        tally = Counter(r["fetch_outcome"] for r in sub)
        print(f"  {s}: " + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    print("\nper-column fill, of ALL sampled tables (not of those reached)")
    header = f"{'column':<20}" + "".join(f"{s:>9}" for s in shards) + f"{'ALL':>9}"
    print(header)
    for col in PUBLISHED + ["--"] + HELD:
        if col == "--":
            print("  " + "-" * (len(header) - 2) + "   (held, not published)")
            continue
        cells = ""
        for s in shards + ["ALL"]:
            sub = [r for r in rows if s == "ALL" or r["shard"] == s]
            cells += f"{pct(sum(1 for r in sub if filled(r, col)), len(sub)):>9}"
        print(f"{col:<20}{cells}")

    by_batch = defaultdict(list)
    for r in rows:
        by_batch[r["_batch"]].append(r)
    print("\nby batch -- an outlier here is one agent, not one shard")
    for b, sub in sorted(by_batch.items()):
        reached = sum(1 for r in sub if r.get("status") == "tagged")
        print(f"  {b:<12}{len(sub):>4} tables   reached {pct(reached, len(sub))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("preds", nargs="+")
    ap.add_argument("--baseline", help="a prior run to print alongside, e.g. the w5 pilot")
    args = ap.parse_args()

    if args.baseline:
        base = load([args.baseline])
        for r in base:
            r["shard"] = r.get("shard") or "w5"
        report(base, f"baseline {Path(args.baseline).stem}")
    report(load(args.preds), "calibration")

    if UNKNOWN_ATOMS:
        print("\nWARNING -- `sample` values outside vocab.md's eight atoms, "
              "counted in neither facet:")
        for a in sorted(UNKNOWN_ATOMS):
            print(f"  {a!r}")


if __name__ == "__main__":
    main()
