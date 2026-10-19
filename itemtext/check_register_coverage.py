"""Which rights-register rows can actually match anything?

The register has two matcher columns and two consumers, and neither consumer
can do anything with a row whose matchers are empty:

  `irw_validate/rights.py`  reads `match_item_text` against an `__items`
                            table's text columns and `match_item_code`
                            against `item` in a response table. An empty cell
                            becomes `stems = []` / `code = None`, so a row
                            with both empty is inert -- it can never match.
  `itemtext/sweep_instrument_rights.py`
                            uses `match_item_text` only. Its item-code surface
                            is an explicit stub ("Not yet wired to the response
                            shards"), because the remedy for an already
                            published item code is an open question. So a row
                            with no text patterns is invisible to the sweep
                            whatever its code pattern says.

That makes a `block` row with no text patterns and no code pattern a record of
a decision rather than an enforceable gate. This counts them, so the gap is a
number someone can act on instead of a thing rediscovered per batch. Two forks
working the #3077 backlog on 2026-10-18 each reported catching blocked
instruments "only by reading stems"; for most block rows, reading is the only
way there is.

This is a REPORT, not a gate. It is deliberately not a test: the register's own
rule 2 is that "a miss is not an all-clear", so an inert row is a known
limitation of the design, not a bug in a given row -- and writing a matcher is
a judgment call with real false-positive cost (`TAS` is both Trust-in-AI and
technology anxiety; `alkouri_2025_icu_stressors` matches the PSS by name and
is not the PSS). Deciding which of these to write patterns for is a rights
ruling, so it belongs to whoever owns those.

    python check_register_coverage.py
    python check_register_coverage.py --verdict block --list
    python check_register_coverage.py --csv ../automated_finding/runs/cov.csv
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(HERE, "instrument_rights_register.csv")


def text_patterns(row) -> list[str]:
    return [p.strip() for p in (row.get("match_item_text") or "").split("|")
            if p.strip()]


def code_pattern(row):
    """The compiled code regex, or None -- including when the cell is prose.

    `rights.py` swallows `re.error` and carries on with the text half, so a
    cell like "ghq1..ghq28 (a note, not a pattern" contributes nothing. Treat
    it as absent here too, or the count overstates coverage."""
    raw = (row.get("match_item_code") or "").strip()
    if not raw:
        return None
    try:
        return re.compile(raw, re.I)
    except re.error:
        return None


def classify(row) -> str:
    has_text = bool(text_patterns(row))
    has_code = code_pattern(row) is not None
    if has_text and has_code:
        return "both surfaces"
    if has_text:
        return "item text only (invisible on a response table)"
    if has_code:
        return "item code only (invisible to the sweep and to __items)"
    return "INERT -- matches nothing on either surface"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--register", default=REGISTER)
    ap.add_argument("--verdict", help="report only this verdict")
    ap.add_argument("--list", action="store_true",
                    help="name every inert row, not just the count")
    ap.add_argument("--csv", help="write the per-row classification here")
    a = ap.parse_args()

    rows = list(csv.DictReader(open(a.register, newline="", encoding="utf-8")))
    if a.verdict:
        rows = [r for r in rows if (r.get("verdict") or "").strip() == a.verdict]

    by_verdict = collections.defaultdict(collections.Counter)
    inert = collections.defaultdict(list)
    for r in rows:
        v = (r.get("verdict") or "").strip() or "(blank)"
        k = classify(r)
        by_verdict[v][k] += 1
        if k.startswith("INERT"):
            inert[v].append(r["instrument"])

    print(f"{len(rows)} register row(s) in {os.path.basename(a.register)}\n")
    order = ["both surfaces",
             "item text only (invisible on a response table)",
             "item code only (invisible to the sweep and to __items)",
             "INERT -- matches nothing on either surface"]
    for v in sorted(by_verdict, key=lambda x: -sum(by_verdict[x].values())):
        tot = sum(by_verdict[v].values())
        print(f"{v}  ({tot} rows)")
        for k in order:
            n = by_verdict[v][k]
            if n:
                print(f"    {n:4}  {k}")
        print()

    blocked_inert = len(inert.get("block", []))
    if blocked_inert:
        print(f"{blocked_inert} of the block rows are inert: the register "
              f"records the decision, but no automated check can reach it.")
        if a.list:
            for name in sorted(inert["block"]):
                print(f"    {' '.join(name.split())[:100]}")

    if a.csv:
        os.makedirs(os.path.dirname(a.csv) or ".", exist_ok=True)
        with open(a.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["instrument", "family", "verdict", "coverage",
                        "n_text_patterns", "has_code_pattern"])
            for r in rows:
                w.writerow([" ".join((r["instrument"] or "").split()),
                            r.get("family", ""), r.get("verdict", ""),
                            classify(r), len(text_patterns(r)),
                            code_pattern(r) is not None])
        print(f"\nwrote {len(rows)} row(s) to {a.csv}")


if __name__ == "__main__":
    main()
