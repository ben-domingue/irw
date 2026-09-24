#!/usr/bin/env python3
"""Item text for che_mood_2024_pvhs (peerj.17134, PMC10977085).

Stems: the paper's Table 2 prints every item against its code pL1..pL10 -- the
same codes the deposit's column headers carry, which the processing script
keeps (only the spaces in "pL  9" are removed). Each cell holds the English and
then, after a <break/>, the administered Malay in italics. Parsed from the
Europe PMC full-text XML rather than retyped.

Anchors: the 1-5 labels are from the paper's Methods (English) and from the
Malay scale sheet in Supplemental Information 2 (peerj-12-17134-s002.docx):
Sangat tidak setuju / Tidak setuju / Tidak pasti / Setuju / Sangat setuju.
S2 is the final 8-item form; the anchor row is the same 1-5 agreement scale
the Methods describe for the 10-item validation form.

Administered language is Malay (the validation form is the Malay pVHS-M), so
the base fields hold the Malay and the authors' own English goes in the
*_translated fields. Non-breaking spaces in the pL6 English cell are
normalised to plain spaces; nothing else is altered (pL4's "(KMM)" is the
paper's own spelling and is kept).

pL5 and pL9 are stored UNREVERSED in the deposit (alpha check in
data/che_mood_2024_pvhs.py), so resp 1 = Sangat tidak setuju for every item.
"""
import csv
import re
import time
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
XML = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10977085/fullTextXML"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "che_mood_2024_pvhs"

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

INSTRUMENT = ("Pregnancy Vaccine Hesitancy Scale, Malay version (pVHS-M), "
              "10-item validation form")
ANCHORS = [(1, "Sangat tidak setuju", "strongly disagree"),
           (2, "Tidak setuju", "disagree"),
           (3, "Tidak pasti", "not sure"),
           (4, "Setuju", "agree"),
           (5, "Sangat setuju", "strongly agree")]


def fetch_xml() -> str:
    for attempt in range(5):
        r = requests.get(XML, headers=UA, timeout=120)
        if r.ok and "<article" in r.text:
            return r.text
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{XML} failed after 5 attempts")


def clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def table2(xml: str) -> dict:
    i = xml.find('<table-wrap position="float" id="table-2"')
    assert i > 0, "Table 2 not found"
    body = xml[i:xml.find("</table-wrap>", i)]
    body = body[body.find("<tbody"):]
    out = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        code = clean(tds[0])
        en, ms = tds[1].split("<break/>")
        out[code] = (clean(ms), clean(en))
    assert list(out) == [f"pL{i}" for i in range(1, 11)], list(out)
    return out


def main():
    items = table2(fetch_xml())
    rows = []
    for code, (ms, en) in items.items():
        for resp, opt_ms, opt_en in ANCHORS:
            rows.append({
                "table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                "instrument": INSTRUMENT, "language": "Malay",
                "instructions": None, "section_prompt": None,
                "item_text": ms, "correct_response": None,
                "option_text": opt_ms, "resp": resp,
                "instructions_translated": None,
                "section_prompt_translated": None,
                "item_text_translated": en, "option_text_translated": opt_en,
            })

    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert {r["item"] for r in rows} == set(resp["item"].astype(str))
    assert {float(r["resp"]) for r in rows} == set(resp["resp"].astype(float))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{TABLE}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    for code, (ms, en) in items.items():
        print(f"  {code:5s} {ms}\n        {en}")
    print(f"{path.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
