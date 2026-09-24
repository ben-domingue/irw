#!/usr/bin/env python3
"""Item text for the PMC batch 3 tables built by data/sison_2022_hiv_testing.py
and data/zhang_2024_smoking.py -- the cheap case in Step 3.5 for both.

sison_2022_hiv_testing_stigma / sison_2022_provider_mistrust
    Text: the Dataverse deposit's own "Coding manual.docx" (doi:10.7910/DVN/PFUMZM),
    whose table pairs each variable name (q16, q18..q23) with its statement and
    its seven 0-6 anchors. The response script keeps those variable names as the
    item codes, unrenamed, so code and text are tied at the source. The survey
    was offered in English and Tagalog (paper, Methods); only the English is in
    the deposit, so `language` lists both and the base fields hold the English.

zhang_2024_smoking_rationalisation / zhang_2024_ftcd
    Text: the SPSS file's own variable labels (stems) and value labels (options),
    12889_2024_19295_MOESM2_ESM.sav. Item codes are the .sav variable names,
    unrenamed. Administered in Chinese; the labels are the authors' English, so
    `language` = Chinese and the English sits in the base fields as a translated
    substitute (itemtext_standard.md, "The fallback").
"""
import csv
import tempfile
import time
import zipfile
from io import BytesIO
from pathlib import Path

import docx
import pandas as pd
import pyreadstat
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
MANUAL = "https://dataverse.harvard.edu/api/access/datafile/6081969"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11229221/supplementaryFiles"
SAV = "12889_2024_19295_MOESM2_ESM.sav"

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]


def row(table, item, instrument, language, item_text, resp, option_text):
    r = {c: "" for c in COLS}
    r.update(table=table, section_id=f"{table}_1", item=item,
             instrument=instrument, language=language, item_text=item_text,
             option_text=option_text, resp=resp)
    return r


def write(table, rows):
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    got_items = {r["item"] for r in rows}
    want_items = set(resp["item"].astype(str))
    assert got_items == want_items, (table, got_items ^ want_items)
    # Per item, not just per table: every observed resp needs an option row.
    for it, grp in resp.groupby("item"):
        have = {float(r["resp"]) for r in rows if r["item"] == it}
        missing = set(grp["resp"].astype(float)) - have
        assert not missing, f"{table}/{it}: observed resp without option row {missing}"
    got_resp = {float(r["resp"]) for r in rows}
    want_resp = set(resp["resp"].astype(float))
    assert got_resp == want_resp, (table, got_resp ^ want_resp)
    assert all(r["item_text"] for r in rows), f"{table}: blank item_text"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{table}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows, {len(got_items)} items")


def sison():
    r = requests.get(MANUAL, headers=UA, timeout=120)
    r.raise_for_status()
    doc = docx.Document(BytesIO(r.content))
    manual = {}
    for t in doc.tables:
        for tr in t.rows:
            cells = [c.text.strip() for c in tr.cells]
            manual[cells[0]] = cells
    lang = "English; Tagalog"
    specs = [("sison_2022_hiv_testing_stigma", ["q16", "q22", "q23"],
              "Anticipated HIV testing stigma (author-constructed, 3 items)"),
             ("sison_2022_provider_mistrust", ["q18", "q19", "q20", "q21"],
              "Provider mistrust (author-constructed, 4 items)")]
    for table, items, instrument in specs:
        rows = []
        for it in items:
            _, stem, _, coding = manual[it]
            # Coding column is "0 – Strongly disagree\n1 – Disagree\n..." -- the
            # leading code is the resp value, not part of the anchor.
            opts = []
            for line in coding.splitlines():
                code, text = line.split("–", 1)
                opts.append((int(code.strip()), text.strip()))
            assert [c for c, _ in opts] == list(range(7)), (it, opts)
            for code, text in opts:
                rows.append(row(table, it, instrument, lang, stem, code, text))
        write(table, rows)


def zhang():
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            break
        time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError("supplementaryFiles did not return a zip")
    with zipfile.ZipFile(BytesIO(r.content)) as z, \
            tempfile.NamedTemporaryFile(suffix=".sav") as fh:
        fh.write(z.read(next(n for n in z.namelist() if n.endswith(SAV))))
        fh.flush()
        _, meta = pyreadstat.read_sav(fh.name, metadataonly=True)
    stems = meta.column_names_to_labels
    vlabs = meta.variable_value_labels
    specs = [
        ("zhang_2024_smoking_rationalisation",
         [f"{p}{i}" for p, n in {"SFB": 5, "RGB": 3, "SAB": 6, "SSB": 4,
                                 "SEB": 5, "QHB": 3}.items()
          for i in range(1, n + 1)],
         "Chinese Male Smoking Rationalisation Scale (Huang et al., 2020)"),
        ("zhang_2024_ftcd", [f"ND{i}" for i in range(1, 7)],
         "Fagerstrom Test for Cigarette Dependence (FTCD / FTND)"),
    ]
    for table, items, instrument in specs:
        rows = []
        for it in items:
            for code, text in sorted(vlabs[it].items()):
                rows.append(row(table, it, instrument, "Chinese",
                                stems[it].strip(), int(code), text.strip()))
        write(table, rows)


if __name__ == "__main__":
    sison()
    zhang()
