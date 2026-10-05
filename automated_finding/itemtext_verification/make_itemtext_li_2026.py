#!/usr/bin/env python3
"""Item text for li_2026_psmus (10.7717/peerj.21138).

Stems: peerj-14-21138-s002.docx, "Items of Problematic Social Media Use Scale",
a list numbered 1-15. Anchors: peerj-14-21138-s004.docx (codebook), "Item 1-15:
1 - Strongly disagree ... 8 - Strongly agree". Both are parsed from the docx
here, not retyped. data/li_2026_psmus.py keeps the xlsx headers Item1..Item15
as `item`; ItemK is tied to the stem numbered K (number match; checked against
the deposit's five 3-item subscale sums by verify_li_2026_psmus.R).

Administered to Chinese college students; the SI carries only English, so the
English ships in the base fields with empty _translated columns and
language = Chinese (translated_substitute fallback).
"""
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

import docx
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13175062/supplementaryFiles"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]
TABLE = "li_2026_psmus"


def paras(z, name):
    d = docx.Document(io.BytesIO(z.read(name)))
    return [re.sub(r"\s+", " ", p.text).strip() for p in d.paragraphs if p.text.strip()]


def main() -> None:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    s2 = paras(z, "peerj-14-21138-s002.docx")
    assert s2[0].startswith("Items of Problematic Social Media Use Scale"), s2[0]
    stems = {}
    for p in s2[1:]:
        m = re.match(r"^(\d+)\.\s*(.+)$", p)
        if m:
            stems[int(m.group(1))] = m.group(2)
    if len(stems) != 15:   # Word auto-numbering: the number is not in the text
        stems = {k + 1: p for k, p in enumerate(s2[1:16])}
    assert sorted(stems) == list(range(1, 16)), stems
    s4 = paras(z, "peerj-14-21138-s004.docx")
    i = s4.index("Item 1-15:")
    block = " ".join(s4[i + 1:])
    opts = {int(k): v.strip() for k, v in
            re.findall(r"(\d)\s*[–-]\s*(.+?)(?=\s+\d\s*[–-]|$)", block)}
    assert sorted(opts) == list(range(1, 9)), opts

    resp = pd.read_csv(HERE / "irw_output" / f"{TABLE}.csv")
    items = [f"Item{k}" for k in range(1, 16)]
    assert set(resp["item"]) == set(items) and set(resp["resp"]) <= set(opts)
    rows = []
    for k in range(1, 16):
        for v, o in opts.items():
            rows.append([TABLE, f"{TABLE}_1", f"Item{k}",
                         "Problematic Social Media Use Scale (PSMUS)", "Chinese", None, None,
                         stems[k], None, o, v, None, None, None, None])
    out = pd.DataFrame(rows, columns=COLS)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_DIR / f"{TABLE}__items.csv", index=False,
               quoting=csv.QUOTE_NONNUMERIC, na_rep="NA")
    print(f"{TABLE}__items.csv: {len(out)} rows, {out['item'].nunique()} items")
    for k in (1, 15):
        print(f"  Item{k}: {stems[k]}")


if __name__ == "__main__":
    main()
