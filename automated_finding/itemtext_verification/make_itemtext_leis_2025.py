#!/usr/bin/env python3
"""Item text for leis_2025_english_motivation (Harvard Dataverse 10.7910/DVN/25QUO9;
article 10.65961/ajelt-2025-1-003). English administration.

Stems: the 20 item columns of sheet "Students Raw Data" carry the full English stem as
header. data/leis_2025_english_motivation.py codes them q01..q20 in sheet order; this
builder applies the same order to the same file (and asserts the shipped table's per-item
means equal the header columns' means, so a code/stem slip would fail).
Options: the paper's Methods -- "a Likert scale from 1 (strongly disagree) to 5 (strongly
agree)"; 2-4 unlabelled and left blank.
"""
import csv
import os
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "25quo9"
URL = "https://dataverse.harvard.edu/api/access/datafile/10409651?format=original"
T = "leis_2025_english_motivation"
INSTRUMENT = ("SDT-based English learning motivation questionnaire (after Agawa & Takeuchi "
              "2016): intrinsic motivation, identified regulation, external regulation, "
              "amotivation")
ANCHORS = {1: "Strongly disagree", 5: "Strongly agree"}
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def main():
    p = RAW / "data.xlsx"
    if not p.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    d = pd.read_excel(p, sheet_name="Students Raw Data")
    d = d[d["Timestamp"].notna()].reset_index(drop=True)
    stems = list(d.columns[5:25])
    resp = pd.read_csv(HERE / "irw_output" / f"{T}.csv")
    mu = resp.groupby("item")["resp"].mean()
    rows = []
    for i, c in enumerate(stems, 1):
        code = f"q{i:02d}"
        assert abs(mu[code] - d[c].mean()) < 1e-9, code
        for r in range(1, 6):
            rows.append({"table": T, "section_id": f"{T}_1", "item": code, "instrument": INSTRUMENT,
                         "instructions": "", "section_prompt": "",
                         "item_text": " ".join(c.split()), "correct_response": "",
                         "option_text": ANCHORS.get(r, ""), "resp": r})
    assert {x["item"] for x in rows} == set(resp["item"])
    with open(HERE / "itemtext_output" / f"{T}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{T}__items.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
