#!/usr/bin/env python3
"""Item text for adebiyi_2026_representational_fluency (figshare 10.6084/m9.figshare.34032243).

Cheap case: the deposit's Instruments_CognitiveLoadErrorPatternsAWPS.pdf prints
the Representational Fluency Task as "Problem1".."Problem4", each with its
"Task:" line, and the data CSV's headers are "Fluency1 (word→eq)" ..
"Fluency4 (word→diagram)", which data/adebiyi_2026_representational_fluency.py
cuts to Fluency1-4. Code k is tied to Problem k by the number in both. The
direction tags in the headers agree with Problems 1, 2 and 4 (word->equation,
equation->words, words->drawing); Problem 3 asks for an area expression from a
described rectangle, which the header tags "eqn→diagram" -- noted, not changed.

item_text = "<problem> Task: <task>" verbatim (whitespace-normalised).
Responses are scored 0/1 with no published key or anchors, so option_text and
correct_response are blank. English administration (Nigeria).
"""
import csv
import re
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP = HERE / "irw_output" / "adebiyi_2026_representational_fluency.csv"
PDF = HERE / "runs" / "raw" / "adebiyi_2026" / "instruments.pdf"
TABLE = "adebiyi_2026_representational_fluency"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def main():
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True,
                         text=True, check=True).stdout
    rft = txt.split("Representational Fluency Task (RFT)")[1]
    instr, body = rft.split("Problem1:", 1)
    instr = " ".join(instr.split())
    body = "Problem1:" + body
    parts = re.findall(r"Problem(\d):\s*(.*?)\s*Task:\s*(.*?)(?=Problem\d:|\Z)", body, re.S)
    assert [p[0] for p in parts] == ["1", "2", "3", "4"], parts
    resp = pd.read_csv(RESP)
    rows = []
    for n, prob, task in parts:
        item = f"Fluency{n}"
        text = f"{' '.join(prob.split())} Task: {' '.join(task.split())}"
        for r in (0, 1):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": item,
                         "instrument": "Representational Fluency Task (RFT)",
                         "instructions": instr, "section_prompt": "", "item_text": text,
                         "correct_response": "", "option_text": "", "resp": r})
    assert {r["item"] for r in rows} == set(resp["item"])
    assert {r["resp"] for r in rows} == set(resp["resp"])
    p = OUT_DIR / f"{TABLE}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows")
    for r in rows[::2]:
        print(" ", r["item"], "|", r["item_text"])
    print("  instructions:", instr)


if __name__ == "__main__":
    main()
