#!/usr/bin/env python3
"""Item text for the three usmani_2024 tables (10.1016/j.heliyon.2024.e37032).

The cheap case in Step 3.5: the Mendeley deposit's POSTDOCDATA.sav carries the
full English stem of every item as its SPSS variable label, and the five
anchors (1 = Strongly Disagree ... 5 = Strongly Agree) as value labels on every
item. data/usmani_2024_islamic_work_ethic.py keeps the .sav column names
(IWE1.., KS1.., PPGP1.., PPGAL1.., PPPP1..) unchanged as `item`, so each stem is
tied to its code by the file's own label, not by position.

Cross-check: the article's SI mmc1.doc is the questionnaire as administered
(English). Every stem is asserted equal to the questionnaire line printed under
the same block heading and number (whitespace-normalised), when the converted
text is available in runs/raw/usmani_2024/mmc1.txt.

Instructions: the questionnaire's line "Please select your desired response:"
(the rest of that line points at a pictured example and is not carried).
POPS is printed in three headed blocks; each is a section, and its heading is
the section_prompt, verbatim including the source's "EBHAVIOR" typo.
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
RAW = HERE / "runs" / "raw" / "usmani_2024"

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]
INSTR = "Please select your desired response:"
TABLES = {
    "usmani_2024_iwe": ("Islamic Work Ethic (short version)",
                        [("IWE", "")]),
    "usmani_2024_ks": ("Knowledge Sharing",
                       [("KS", "")]),
    "usmani_2024_pops": ("Perceptions of Organizational Politics Scale (POPS)",
                         [("PPGP", "GENERAL POLITICAL EBHAVIOR"),
                          ("PPGAL", "GO ALONG TO GET AHEAD"),
                          ("PPPP", "PAY AND PROMOTION")]),
}
QHEAD = {"IWE": "ISLAMIC WORK ETHICS", "KS": "KNOWLEDGE SHARING",
         "PPGP": "GENERAL POLITICAL EBHAVIOR", "PPGAL": "GO ALONG TO GET AHEAD",
         "PPPP": "PAY AND PROMOTION"}


def norm(s: str) -> str:
    return " ".join(s.replace("’", "'").split())


def questionnaire() -> dict:
    """{(block, k): stem} from the SI questionnaire text, if converted."""
    p = RAW / "mmc1.txt"
    if not p.exists():
        return {}
    lines = [l.strip().lstrip("﻿") for l in p.read_text(encoding="utf-8").splitlines()]
    out, block = {}, None
    heads = {v: k for k, v in QHEAD.items()}
    for i, l in enumerate(lines):
        if l in heads:
            block = heads[l]
        elif block and re.fullmatch(r"\d\d", l):
            out[(block, int(l))] = norm(lines[i + 1])
    return out


def main() -> None:
    d, meta = pyreadstat.read_sav(str(RAW / "POSTDOCDATA.sav"))
    vl, vv = meta.column_names_to_labels, meta.variable_value_labels
    q = questionnaire()
    if not q:
        print("WARNING: no questionnaire text, cross-check skipped", file=sys.stderr)
    checked = 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, blocks) in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        for prefix, heading in blocks:
            sec = f"{table}_{prefix.lower()}" if heading else f"{table}_1"
            items = sorted((c for c in resp["item"].unique()
                            if re.fullmatch(prefix + r"\d+", c)),
                           key=lambda s: int(s[len(prefix):]))
            for it in items:
                stem = norm(vl[it])
                if q:
                    assert norm(q[(prefix, int(it[len(prefix):]))]) == stem, it
                    checked += 1
                opts = vv[it]
                assert sorted(opts) == [1, 2, 3, 4, 5], it
                for r in range(1, 6):
                    rows.append({"table": table, "section_id": sec, "item": it,
                                 "instrument": instrument, "instructions": INSTR,
                                 "section_prompt": heading, "item_text": vl[it].strip(),
                                 "correct_response": "", "option_text": opts[r],
                                 "resp": r})
        assert {r["item"] for r in rows} == set(resp["item"])
        assert {r["resp"] for r in rows} == set(resp["resp"])
        path = OUT_DIR / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows, {resp['item'].nunique()} items")
    print(f"questionnaire cross-check: {checked}/39 stems equal")


if __name__ == "__main__":
    main()
