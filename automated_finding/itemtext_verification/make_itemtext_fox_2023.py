#!/usr/bin/env python3
"""Item text for fox_2023_bct and fox_2023_gad7 (OSF sfuz9, doi 10.17605/OSF.IO/SFUZ9;
paper 10.12688/routledgeopenres.17925.2). English administration (Australia / New Zealand).

Cheap case: the deposit's "Study 1 Data Dictionary.csv" / "Study 2 Data Dictionary.csv"
give, per variable, the question text (`description`) and the response levels (`levels`,
"1 = Strongly disagree, 2 = ..."). data/fox_2023_conspiracy_stress.py keeps the variable
names as item, so text is tied to code by name. The builder asserts both studies'
dictionaries agree on every shipped item and that every observed resp is a listed level.
fox_2023_pss10 is deliberately not built (PSS: rights register `block`).
"""
import csv
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW = Path(__import__("os").environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "sfuz9"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
META = {"fox_2023_bct": ("Belief in specific conspiracy theories (15 items, study-specific)",
                         "Please indicate how much you agree or disagree with each of the following statements."),
        "fox_2023_gad7": ("Generalized Anxiety Disorder 7-item scale (GAD-7)",
                          "Over the last two weeks, how often have you been bothered by the following problems?")}


def levels(s: str) -> dict:
    """'1 = Strongly disagree, 2 = ... 3 = Neither agree nor disagree 4 = Somewhat agree' ->
    {1: ..., 4: ...}; the dictionary drops a comma before one level, so split on the
    '<digit> =' boundaries rather than on commas."""
    out = {}
    for part in re.split(r",?\s*(?=\d\s*=)", s.strip()):
        m = re.match(r"(\d)\s*=\s*(.+)$", part.strip())
        if m:
            out[int(m.group(1))] = " ".join(m.group(2).split()).strip(" .,")
    return out


def main():
    d1 = pd.read_csv(RAW / "Study 1 Data Dictionary.csv").set_index("variable")
    d2 = pd.read_csv(RAW / "Study 2 Data Dictionary.csv").set_index("variable")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, instructions) in META.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        for it in sorted(resp["item"].unique(), key=lambda s: int(re.search(r"_(\d+)", s).group(1))):
            if d1.loc[it, "description"].strip() != d2.loc[it, "description"].strip():
                # Two known differences: BCT_3_Sim ("someones" / "someone's") and
                # BCT_14_Climate (Study 2 adds "financial" before "interests"). Study 1's
                # wording ships; the BCT_14 variant is on the public issues page.
                assert it in ("BCT_3_Sim", "BCT_14_Climate"), it
                print(f"  {it}: Study 2 wording differs -> {d2.loc[it, 'description'].strip()!r}")
            assert levels(d1.loc[it, "levels"]) == levels(d2.loc[it, "levels"]), it
            opts = levels(d1.loc[it, "levels"])
            observed = set(resp.loc[resp["item"] == it, "resp"])
            assert observed <= set(opts), (it, observed, opts)
            for r, o in sorted(opts.items()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": instrument, "instructions": instructions,
                             "section_prompt": "", "item_text": " ".join(d1.loc[it, "description"].split()),
                             "correct_response": "", "option_text": o, "resp": r})
        assert {r["item"] for r in rows} == set(resp["item"])
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {resp['item'].nunique()} items")
        for r in rows[::len(opts)][:3]:
            print("  ", r["item"], "|", r["item_text"][:70], "|", r["option_text"])


if __name__ == "__main__":
    main()
