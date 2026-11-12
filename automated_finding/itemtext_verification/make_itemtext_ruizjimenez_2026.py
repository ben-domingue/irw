#!/usr/bin/env python3
"""Item text for ruizjimenez_2026_health_eval (Zenodo 10.5281/zenodo.23880944, FEDER UPO-1381076).

Mapping basis: data_labels. Each item code is the .sav variable name (P6N_1..P6N_12) and its
variable label in FEDER2020_encuesta_datos.sav is the Spanish statement, so code and wording are
tied by the data file itself, not by order.

Text source: study_materials. The statements are written by the study team (a survey of
Spanish nationals on public healthcare, not a published scale). The instructions are the
"Pregunta" line of the deposit's Spanish codebook (FEDER2020_codebook_ES.pdf); the English
translations of statements, instructions and anchors are the depositors' own, from
FEDER2020_codebook_EN.pdf, not IRW's. Anchors: 1 and 10 carry labels; 2-9 are unlabelled
("valores intermedios ... sin etiqueta propia") and are left blank.

Run: SAV=<FEDER2020_encuesta_datos.sav> CODEBOOK_EN=<..._codebook_EN.pdf>
     CODEBOOK_ES=<..._codebook_ES.pdf> RESP_DIR=<irw_output> OUT_DIR=<itemtext_output>
     python3 make_itemtext_ruizjimenez_2026.py
"""
import csv
import os
import re
import subprocess
from pathlib import Path

import pandas as pd
import pyreadstat

T = "ruizjimenez_2026_health_eval"
INST = ("Assessment of the current state of public healthcare (P6), FEDER UPO-1381076 survey "
        "on deservingness criteria in public services (Ruiz Jimenez et al., 2023 fieldwork)")
INSTR_ES = ("¿Cómo valora la situación actual de cada uno de los siguientes aspectos en una escala de 1 a 10, "
            "donde 1 quiere decir que lo valora muy negativamente y 10 que lo valora muy positivamente?")
INSTR_EN = ("How do you rate the current situation of each of the following aspects on a scale from 1 to 10, "
            "where 1 means you rate it very negatively and 10 very positively?")
EN = [
    "Universality of current public healthcare: everyone is attended regardless of origin or income.",
    "Free provision of current public healthcare, funded by everyone’s taxes.",
    "Quality of current diagnostic and treatment equipment in public hospitals.",
    "Quantity of current diagnostic and treatment equipment in public hospitals.",
    "Quality of professionals in current public healthcare.",
    "Number of professionals in current public healthcare.",
    "Current territorial health coverage: there is sufficient care in all territories.",
    "Ease of carrying out administrative procedures at present.",
    "Current waiting times to be seen in specialised care (traumatology, dermatology, etc.).",
    "Current waiting times for diagnostic tests (scan, X-ray, biopsy, etc.).",
    "Current level of investment in public healthcare.",
    "Differences in the services currently offered by public healthcare in each Autonomous Community.",
]
ANCHOR = {1: ("Muy negativamente", "Very negatively"), 10: ("Muy positivamente", "Very positively")}


def flat(s):
    return re.sub(r"\s+", "", s)


def main():
    _, meta = pyreadstat.read_sav(os.environ["SAV"], metadataonly=True)
    en_txt = flat(subprocess.run(["pdftotext", os.environ["CODEBOOK_EN"], "-"], capture_output=True, text=True).stdout)
    es_txt = flat(subprocess.run(["pdftotext", os.environ["CODEBOOK_ES"], "-"], capture_output=True, text=True).stdout)
    assert flat(INSTR_EN) in en_txt and flat(INSTR_ES) in es_txt
    for s in EN:
        assert flat(s) in en_txt, s
    rows = []
    for i, en in enumerate(EN, start=1):
        item = f"P6N_{i}"
        es = meta.column_names_to_labels[item].strip()
        vl = meta.variable_value_labels[item]
        assert vl[1.0].endswith("Muy negativamente") and vl[10.0].endswith("Muy positivamente")
        for v in range(1, 11):
            opt_es, opt_en = ANCHOR.get(v, ("", ""))
            rows.append({"table": T, "section_id": f"{T}_1", "item": item, "instrument": INST,
                         "language": "Spanish", "instructions": INSTR_ES, "section_prompt": "",
                         "item_text": es, "correct_response": "", "option_text": opt_es, "resp": v,
                         "instructions_translated": INSTR_EN, "section_prompt_translated": "",
                         "item_text_translated": en, "option_text_translated": opt_en})
    resp = pd.read_csv(Path(os.environ["RESP_DIR"]) / f"{T}.csv")
    assert {r["item"] for r in rows} == set(resp["item"])
    assert {r["resp"] for r in rows} == set(resp["resp"])
    out = Path(os.environ["OUT_DIR"]) / f"{T}__items.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} rows")


if __name__ == "__main__":
    main()
