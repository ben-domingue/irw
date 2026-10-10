#!/usr/bin/env python3
"""Item text for the nine moreno_jorquera_2025_amtb_* tables (Harvard Dataverse
10.7910/DVN/KOQP5C; article 10.5334/glo.113, Glocality, CC BY 4.0).

Administered wording: every item column header of AMTB+Dataset.xlsx, sheet
"Likert completo", is "<n>. <Chilean-Spanish stem>". data/moreno_jorquera_2025_amtb.py
renames that column to amtb_<n>, so item amtb_<n> = the header numbered n; the
stem after "<n>. " is item_text, unchanged except for whitespace.

English: the article's Table 17 ("AMTB Version Presented to Students") lists the
authors' English translation of the same 43 numbered items with each item's
mode, mean and SD over the 136 respondents. Item n's English is the Table 17 row
numbered n; the builder checks every published mean against the mean of the
shipped column amtb_<n> (to 3 decimals) before writing, so a numbering slip
cannot pass silently.

Options: the Methods give the 1-7 agreement scale in English only ("1 being
strongly disagree, 4 neither agree nor disagree, and 7 strongly agree"); the
administered Spanish anchors are not in the deposit or the article, so
option_text is blank and the three labelled anchors go in option_text_translated
(2, 3, 5, 6 are unlabelled and stay blank).
"""
import csv
import os
import re
import subprocess
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw" / "moreno_jorquera_2025"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
XLSX_URL = "https://dataverse.harvard.edu/api/access/datafile/13255558"
PDF_URL = "https://glocality.eu/articles/113/files/6954e820e28e0.pdf"
P = "moreno_jorquera_2025_amtb_"
TABLES = {
    "interest": [1, 9, 27, 36], "intensity": [6, 14, 24, 33, 40],
    "teacher": [2, 10, 18, 28, 37, 43], "att_learn": [3, 11, 19, 29, 38],
    "att_people": [16, 20, 23, 30], "integr": [4, 12, 21, 31],
    "desire": [5, 13, 22, 32, 39, 42], "course": [8, 17, 26, 35, 41],
    "instrum": [7, 15, 25, 34],
}
ANCHORS = {1: "Strongly disagree", 4: "Neither agree nor disagree", 7: "Strongly agree"}
INSTRUMENT = ("Attitude/Motivation Test Battery (AMTB), 43-item Mexican Spanish version "
              "(Sandoval-Pineda 2011) with Chilean lexical adaptations")
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]


def get(name, url):
    p = RAW / name
    if not p.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def table17(pdf):
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True,
                         text=True, check=True).stdout
    lines = txt.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().startswith("1. I would like to speak"))
    end = next(i for i, l in enumerate(lines) if "The overall sample mean (n = 136)" in l)
    items, cur = {}, None
    for l in lines[start:end]:
        left = l[:84].rstrip()
        m = re.match(r"\s*(\d{1,2})\.\s+(.*?)\s+(\d)\s+(\d\.\d{3})\s+(\d\.\d{3})?", l)
        if m:
            cur = int(m.group(1))
            items[cur] = {"text": m.group(2).strip(), "mean": float(m.group(4))}
            continue
        s = left.strip()
        if cur and s and not re.search(r"MODE|MEAN|Moreno|Gloc|DOI|^\d+$", s) and len(l) - len(l.lstrip()) < 4:
            items[cur]["text"] += " " + s
    assert sorted(items) == list(range(1, 44)), sorted(items)
    return items


def main():
    xlsx = get("AMTB.xlsx", XLSX_URL)
    pdf = get("glo_113.pdf", PDF_URL)
    d = pd.read_excel(xlsx, "Likert completo")
    es = {}
    for c in d.columns[1:44]:
        m = re.fullmatch(r"\s*(\d+)\.\s*(.+)", c, re.S)
        es[int(m.group(1))] = (c, " ".join(m.group(2).split()))
    assert sorted(es) == list(range(1, 44))
    en = table17(pdf)
    for n in range(1, 44):  # the published per-item mean pins English item n to column n
        mu = round(d[es[n][0]].mean(), 3)
        assert abs(mu - en[n]["mean"]) < 0.0015, (n, mu, en[n]["mean"])
    print("Table 17 means match the deposit's columns for all 43 items")
    out_dir = HERE / "itemtext_output"
    for suf, nums in TABLES.items():
        table = P + suf
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        rows = []
        for n in nums:
            for r in range(1, 8):
                rows.append({"table": table, "section_id": f"{table}_1", "item": f"amtb_{n}",
                             "instrument": INSTRUMENT, "language": "Spanish",
                             "instructions": "", "instructions_translated": "",
                             "section_prompt": "", "item_text": es[n][1],
                             "item_text_translated": " ".join(en[n]["text"].split()),
                             "correct_response": "", "option_text": "",
                             "option_text_translated": ANCHORS.get(r, ""), "resp": r})
        assert {x["item"] for x in rows} == set(resp["item"])
        assert set(resp["resp"]) <= set(range(1, 8))
        with open(out_dir / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{table}__items.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
