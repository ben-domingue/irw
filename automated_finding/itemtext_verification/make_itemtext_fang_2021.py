#!/usr/bin/env python3
"""Item text for fang_2021_pbc, fang_2021_pn, fang_2021_peb (10.7717/peerj.11635).

Source: the open-access article itself (PMC8216169, CC BY 4.0). Its Tables 2,
3 and 5 print every item against the same code the data file uses as a column
header, e.g. "PBC1. I take the initiative to go outdoors. 3.38 1.16"; this
script parses them out of the Europe PMC full-text XML, so code-to-text is
read off the page, not inferred from position. data/fang_2021_pro_environmental.py
keeps those headers (PBC1..PEB5) as the IRW item codes unchanged.

Appendix A1 (an image of the questionnaire, section D) gives the shared
instruction and the five anchors, transcribed by hand below:
"Please fill in the level of agreement to the best of your understanding on
the following statements." / Strongly disagree (1) / Disagree (2) / Neither
agree nor disagree (3) / Agree (4) / Strongly agree (5). The "(n)" after each
anchor is the resp code and is not part of option_text. The appendix image
lists the same stems in the same order as the tables.

Language: the respondents were fifth and sixth graders in Hsinchu, Taiwan; the
paper does not name the administration language and only an English rendering
is published, so the base fields hold that English (text_source
translated_substitute), `language` = Chinese, and the *_translated fields are
empty -- the standard's fallback shape.

fang_2021_sn is NOT built: the questionnaire and Table 4 have six social-norm
items while the data have five, and the data's SN codes do not line up with
the table's numbering (see the data script header).
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
XML = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8216169/fullTextXML"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
INSTR = ("Please fill in the level of agreement to the best of your "
         "understanding on the following statements.")
OPTIONS = [(1, "Strongly disagree"), (2, "Disagree"),
           (3, "Neither agree nor disagree"), (4, "Agree"), (5, "Strongly agree")]
TABLES = {
    "fang_2021_pbc": ("PBC", 4, "Perceived behavioral control (author-compiled, 4 items)"),
    "fang_2021_pn": ("PN", 3, "Personal norms (author-compiled, 3 items)"),
    "fang_2021_peb": ("PEB", 5, "Pro-environmental behavior (author-compiled, 5 items)"),
}


def paper_items():
    r = requests.get(XML, headers=UA, timeout=120)
    r.raise_for_status()
    out = {}
    for tw in re.findall(r"<table-wrap[ >].*?</table-wrap>", r.text, re.S):
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", tw))
        for code, stem in re.findall(
                r"\b((?:PBC|PN|SN|PEB)\d)\. (.+?) \d\.\d{2,3} \d\.\d{2,3}", txt):
            assert code not in out, code
            out[code] = stem.strip()
    return out


def main():
    items = paper_items()
    for table, (prefix, k, instrument) in TABLES.items():
        codes = [f"{prefix}{i}" for i in range(1, k + 1)]
        assert all(c in items for c in codes), (table, sorted(items))
        rows = []
        for c in codes:
            for resp, opt in OPTIONS:
                rows.append({
                    "table": table, "section_id": f"{table}_1", "item": c,
                    "instrument": instrument, "language": "Chinese",
                    "instructions": INSTR, "section_prompt": "",
                    "item_text": items[c], "correct_response": "",
                    "option_text": opt, "resp": resp,
                    "instructions_translated": "", "section_prompt_translated": "",
                    "item_text_translated": "", "option_text_translated": "",
                })
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert {r["item"] for r in rows} == set(resp["item"].astype(str)), table
        assert {float(r["resp"]) for r in rows} == set(resp["resp"].astype(float)), table
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows, {k} items")
        for c in codes:
            print(f"   {c}: {items[c]}")


if __name__ == "__main__":
    main()
