#!/usr/bin/env python3
"""Item text for the four shen_2025 tables (10.7717/peerj.19707).

Stems: the SPSS variable labels of peerj-13-19707-s002.sav (every item column
carries its English stem; data/shen_2025_teacher_distress.py keeps the column
names S1, A1, ..., GD9 as `item`, so label and code come from the same
variable). Runs of whitespace inside a label are collapsed to one space and
"Ifeel"/"youthink"/"Doyou" style joins are left as deposited (they are in the
labels themselves). Anchors: the deposit has no item value labels; the four
anchor sets are those printed in peerj-13-19707-s003.doc ("Data Code"), which
is converted with LibreOffice and asserted to contain every anchor and stem.

Administered language: the Chinese versions of all four scales (paper,
Instruments). Neither the .sav (no CJK characters in any label) nor s001/s003
carries Chinese wording, so the English ships in the base fields with empty
_translated columns and language = Chinese (translated_substitute fallback).
"""
import csv
import io
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12296581/supplementaryFiles"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

SPECS = {
    "shen_2025_dass21": ("Depression Anxiety Stress Scales-21 (DASS-21), Chinese version",
                         ["S1", "A1", "D1", "A2", "D2", "S2", "A3", "S3", "A4", "D3", "S4", "S5",
                          "D4", "S6", "A5", "D5", "D6", "S7", "A6", "A7", "D7"],
                         {0: "not at all", 1: "some of the time", 2: "a good part of time",
                          3: "most of the time"}),
    "shen_2025_bsmas": ("Bergen Social Media Addiction Scale (BSMAS), Chinese version",
                        [f"SD{i}" for i in range(1, 7)],
                        {1: "very rarely", 2: "rarely", 3: "sometimes", 4: "often",
                         5: "very often"}),
    "shen_2025_sabas": ("Smartphone Application-Based Addiction Scale (SABAS), Chinese version",
                        [f"PD{i}" for i in range(1, 7)],
                        {1: "strongly disagree", 2: "disagree", 3: "slightly disagree",
                         4: "slightly agree", 5: "agree", 6: "strongly agree"}),
    "shen_2025_igds9sf": ("Internet Gaming Disorder Scale-Short Form (IGDS9-SF), Chinese version",
                          [f"GD{i}" for i in range(1, 10)],
                          {1: "never", 2: "rarely", 3: "sometimes", 4: "often", 5: "very often"}),
}


def ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main() -> None:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "d.sav").write_bytes(z.read("peerj-13-19707-s002.sav"))
        (td / "code.doc").write_bytes(z.read("peerj-13-19707-s003.doc"))
        _, meta = pyreadstat.read_sav(str(td / "d.sav"), metadataonly=True)
        subprocess.run(["soffice", "--headless", "--convert-to", "txt:Text", "--outdir",
                        str(td), str(td / "code.doc")], check=True, capture_output=True)
        code = ws((td / "code.txt").read_text(encoding="utf-8-sig"))
    labels = meta.column_names_to_labels
    assert not any(re.search(r"[一-鿿]", v or "") for v in labels.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, items, opts) in SPECS.items():
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        assert set(resp["item"]) == set(items), table
        assert set(resp["resp"]) <= set(opts), table
        for o in opts.values():
            assert o in code, (table, o)
        rows = []
        for item in items:
            stem = ws(labels[item])
            # the codebook prints "<code> <stem>"; compare ignoring spaces
            assert re.sub(r"\s", "", stem) in re.sub(r"\s", "", code), (table, item)
            for v, o in opts.items():
                rows.append([table, f"{table}_1", item, instrument, "Chinese", None, None,
                             stem, None, o, v, None, None, None, None])
        out = pd.DataFrame(rows, columns=COLS)
        out.to_csv(OUT_DIR / f"{table}__items.csv", index=False,
                   quoting=csv.QUOTE_NONNUMERIC, na_rep="NA")
        print(f"{table}__items.csv: {len(out)} rows, {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
