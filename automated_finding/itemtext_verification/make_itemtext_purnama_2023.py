#!/usr/bin/env python3
"""Item text for purnama_2023_{program_benefit,threat,constraints,digital_need,
environment,attitude} (Dryad 10.5061/dryad.jdfn2z3f0; article
10.12688/f1000research.125318.2).

Cheap case. SPSS_SEM_ok.sav labels every item variable (var1a .. var6i) with its English
statement, and data/purnama_2023_dengue.py keeps those variable names as `item`, so the
label ties text to code by name. Data_Description.docx (the deposit's codebook, a table of
composite | indicator | definition) gives the same statements; the builder asserts that
every label is the codebook's definition or a prefix of it (SPSS cut var6i short) and
ships the codebook wording. Options: README.md -- "1, 2 3, 4, and 5 represent strongly
disagree, disagree, neutral, agree, and strongly agree".

Language: a Google Form survey of adult residents of Denpasar (Bali, Indonesia). Neither
the article nor the deposit names the form's language and only this English wording is
published, so the documented fallback applies: English in the base fields, language =
Indonesian (inferred from the setting), no _translated columns,
text_source = translated_substitute, translation_source = study_supplied.
"""
import csv
import os
import re
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "10.5061_dryad.jdfn2z3f0"
OUT_DIR = Path(os.environ.get("ITEMTEXT_OUT_DIR", HERE / "itemtext_output"))
RESP_DIR = Path(os.environ.get("IRW_RESP_DIR", HERE / "irw_output"))
COMPOSITES = {
    "purnama_2023_program_benefit": ("var1", "Perception of program benefits"),
    "purnama_2023_threat": ("var2", "Perception of being threatened with dengue"),
    "purnama_2023_constraints": ("var3", "Perception of program constraints"),
    "purnama_2023_digital_need": ("var4", "Perception of digital technology needs"),
    "purnama_2023_environment": ("var5", "Perception of environmental factors"),
    "purnama_2023_attitude": ("var6", "Attitude towards dengue control"),
}
OPTIONS = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree",
           5: "Strongly agree"}
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]


def norm(s: str) -> str:
    return " ".join(s.replace("’", "'").split())


def codebook() -> dict:
    """indicator (lower-case, star stripped) -> definition, from the docx table."""
    x = zipfile.ZipFile(RAW / "Data_Description.docx").read("word/document.xml").decode()
    rows = []
    for tr in re.findall(r"<w:tr[ >].*?</w:tr>", x, flags=re.S):
        cells = [norm(re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", " ", tc)))
                 for tc in re.findall(r"<w:tc>.*?</w:tc>", tr, flags=re.S)]
        rows.append(cells)
    out = {}
    for r in rows:
        if len(r) >= 3 and re.fullmatch(r"Var\d[a-i]\*?", r[1]):
            out[r[1].rstrip("*").lower()] = r[2]
    return out


def main() -> None:
    cb = codebook()
    assert len(cb) == 46, len(cb)
    _, meta = pyreadstat.read_sav(str(RAW / "SPSS_SEM_ok.sav"), metadataonly=True)
    for var, lab in meta.column_names_to_labels.items():
        lab = norm(lab)
        assert cb[var] == lab or cb[var].startswith(lab), (var, lab, cb[var])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pre, composite) in COMPOSITES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = sorted(resp["item"].unique())
        assert all(i.startswith(pre) for i in items)
        assert set(resp["resp"]) <= set(OPTIONS)
        rows = []
        for it in items:
            for k, lab in OPTIONS.items():
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": ("Attitude towards dengue control efforts "
                                            f"questionnaire (Purnama et al. 2023): {composite}"),
                             "language": "Indonesian", "instructions": "",
                             "section_prompt": "", "item_text": cb[it],
                             "correct_response": "", "option_text": lab, "resp": k})
        assert {r["item"] for r in rows} == set(resp["item"])
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(items)} items")


if __name__ == "__main__":
    main()
