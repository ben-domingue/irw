#!/usr/bin/env python3
"""Item text for the four kanwal_2024 tables (10.1016/j.heliyon.2024.e38987).

The cheap case in Step 3.5: the article's own supplement mmc2.docx, Table S1
"Survey Instrument", is a two-column table of item code and item wording for
every item, and its codes are the headers of the data file mmc1.csv, which
data/kanwal_2024_csr.py keeps unchanged as `item`. So each stem is tied to its
code by name, not by position.

Two deviations, both disclosed in provenance:
- Table S1 spells the green-shared-vision codes GRSV1-4; the data spell them
  GSRV1-4. They are the only four codes of that block in either file, matched
  by their number.
- Table S1's CSRN3 cell is cut off in the source ("... (e.g., choice of
  materials, eco-design, "). It is shipped as cut, trailing space trimmed,
  rather than completed from the original scale.

Anchors: Methods 4.3 says only that "1" denoted strong disagreement and "5"
strong agreement on a 5-point Likert scale; those two phrases are used for 1
and 5 and points 2-4 are left blank, not padded. No instructions are published.
Administered in English (Methods 4.3), so no language/_translated columns.
"""
import csv
import io
import zipfile
from pathlib import Path

import docx
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
RAW = HERE / "runs" / "raw" / "kanwal_2024_csr" / "mmc2.docx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11490784/supplementaryFiles"

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]

TABLES = {
    "kanwal_2024_csr": ("Perceived corporate social responsibility (CSR towards "
                        "employees, community, environment and customers)",
                        ("CSRE", "CSRC", "CSRN", "CSRU")),
    "kanwal_2024_goc": ("Green organizational climate", ("GOCL",)),
    "kanwal_2024_gsv": ("Green shared vision", ("GSRV",)),
    "kanwal_2024_wpeb": ("Workplace pro-environmental behavior", ("WPEB",)),
}
OPTIONS = {1: "strong disagreement", 2: "", 3: "", 4: "", 5: "strong agreement"}


def s1() -> dict:
    if RAW.exists():
        blob = RAW.read_bytes()
    else:
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        blob = zipfile.ZipFile(io.BytesIO(r.content)).read("mmc2.docx")
    doc = docx.Document(io.BytesIO(blob))
    t = doc.tables[0]
    assert [c.text for c in t.rows[0].cells] == ["Code", "Items"]
    out = {}
    for row in t.rows[1:]:
        code, text = (c.text.strip() for c in row.cells)
        code = code.replace("GRSV", "GSRV")  # S1 typo, see docstring
        assert code not in out, code
        out[code] = " ".join(text.split())
    return out


def main() -> None:
    stems = s1()
    assert len(stems) == 45, len(stems)
    used = set()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, prefixes) in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = sorted(resp["item"].unique(), key=lambda s: (prefixes.index(s[:4]), int(s[4:])))
        rows = []
        for it in items:
            stem = stems[it]  # KeyError = no tie by code
            used.add(it)
            for r, opt in OPTIONS.items():
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": instrument, "instructions": "",
                             "section_prompt": "", "item_text": stem,
                             "correct_response": "", "option_text": opt, "resp": r})
        assert {r["item"] for r in rows} == set(resp["item"])
        assert {r["resp"] for r in rows} == set(resp["resp"])
        path = OUT_DIR / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows, {len(items)} items")
    assert used == set(stems), set(stems) - used


if __name__ == "__main__":
    main()
