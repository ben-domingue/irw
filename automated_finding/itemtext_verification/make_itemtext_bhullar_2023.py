#!/usr/bin/env python3
"""Item text for bhullar_2023_{expected_benefits,farming_concerns}
(10.1371/journal.pone.0265634; Figshare 10.6084/m9.figshare.19354313, CC BY
4.0).

Source, level 1: the two deposited .sav files (beef N=471, poultry N=426;
same questionnaire) label every item variable with its code and wording,
e.g. B1 = "B1. I wil be able to earn more money.". The response tables keep
the variable names as item codes (data/bhullar_2023_sa_farmers.py), so code
and text are tied at the source. The script asserts the two files carry
identical labels and strips the leading "<code>. " from each. Labels are
otherwise verbatim, typos included ("I wil be able", "Current level of
debt..", "farming purposes..").

Response anchors from the article's Measures: expected benefits "1 = very
unlikely; 5 = very likely", farming concerns "1 = very low; 5 = very high";
levels 2-4 are unlabelled there and ship with blank option_text (the .sav has
no value labels). No stem or instructions are in the deposit or the article,
so instructions are blank.

Rights: both blocks are the authors' adaptations of their own group's earlier
farmer measures ("adapted from Morgan and colleagues' study"); no named
instrument. Language: the article says "The study survey was prepared in the
English language" and enumerators translated orally for farmers with limited
schooling -- the written wording is English, so no language column.

Run: RESP_DIR=<dir> [RAW_DIR=<dir with beef.sav, poultry.sav>] python3 make_itemtext_bhullar_2023.py
"""
import csv
import os
import re
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
RAW_DIR = os.environ.get("RAW_DIR")
FILES = {"beef": "https://ndownloader.figshare.com/files/34376336",
         "poultry": "https://ndownloader.figshare.com/files/34376339"}
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt", "item_text",
        "correct_response", "option_text", "resp"]
TABLES = {
    "bhullar_2023_expected_benefits": (
        ["B1", "B2", "B3", "B4", "B5", "B6b", "B7", "B8"], {1: "very unlikely", 5: "very likely"},
        "Expected benefits of cattle/poultry farming (Bhullar et al. 2023, South African smallholder farmer survey)"),
    "bhullar_2023_farming_concerns": (
        [f"C{i}" for i in range(1, 37)], {1: "very low", 5: "very high"},
        "Farming concerns (Bhullar et al. 2023, South African smallholder farmer survey)"),
}


def labels(study):
    if RAW_DIR:
        path = os.path.join(RAW_DIR, f"{study}.sav")
    else:
        r = requests.get(FILES[study], headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        f = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
        f.write(r.content)
        f.close()
        path = f.name
    _, meta = pyreadstat.read_sav(path, metadataonly=True)
    return meta.column_names_to_labels


def main():
    lb, lp = labels("beef"), labels("poultry")
    for table, (codes, opts, inst) in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        for code in codes:
            assert lb[code] == lp[code], code
            m = re.match(rf"^{re.escape(code)}\.\s*(.+)$", lb[code])
            assert m, lb[code]
            for v in sorted(resp["resp"].unique()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": inst,
                             "instructions": "", "section_prompt": "", "item_text": m.group(1).strip(),
                             "correct_response": "", "option_text": opts.get(int(v), ""), "resp": int(v)})
        assert {r["item"] for r in rows} == set(resp["item"]), table
        assert {r["resp"] for r in rows} == set(resp["resp"]), table
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{table}__items.csv: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
