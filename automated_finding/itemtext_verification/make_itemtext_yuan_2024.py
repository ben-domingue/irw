#!/usr/bin/env python3
"""Item text for yuan_2024_ucla, yuan_2024_contact, yuan_2024_trust
(10.1038/s41598-024-66646-1, PMC11237108, CC BY 4.0).

Stems: the deposit's own SPSS variable labels (41598_2024_66646_MOESM1_ESM.sav),
read off the T1 column whose name IS the item code plus "T1"
(UCLA01T1 -> item UCLA01), so code-to-text needs no positional inference.
The leading item number in each label ("2.How often ...") is the questionnaire
numbering, not wording, and is stripped; nothing else is changed (source
punctuation, e.g. no final period on some labels, kept).

Anchors: the .sav has no value labels on any item. The paper's Supplementary
Information 1 appendix (in the article full text) gives endpoint anchors only:
UCLA "1 never-4 always"; contact items 1-4 "1 never-7 frequently", item 5
"1 almost none-7 A large proportion", items 6-9 their own bipolar endpoints;
trust "1 never feel this way-7 always feel this way", printed once for the
four-item scale. Unlabelled midpoints get blank option_text (required).

Language: administered in Mandarin Chinese (paper: "the study was conducted
using Mandarin Chinese versions of the questionnaires"). Neither the .sav
(zero CJK characters in any variable or value label) nor the paper holds the
Chinese wording, so the authors' English ships in the base fields with
language = Chinese and empty *_translated fields (translated_substitute).
"""
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
CACHE = HERE / "runs" / "raw" / "yuan_2024"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11237108/supplementaryFiles"
FNAME = "41598_2024_66646_MOESM1_ESM.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

CONTACT_ENDS = {1: ("never", "frequently"), 2: ("never", "frequently"),
                3: ("never", "frequently"), 4: ("never", "frequently"),
                5: ("almost none", "A large proportion"),
                6: ("distant", "close"), 7: ("competitive", "cooperative"),
                8: ("unequal", "equal"), 9: ("unpleasant", "pleasant")}
TABLES = {
    "yuan_2024_ucla": ("UCLA", 20, 4, "UCLA Loneliness Scale",
                       lambda i: ("never", "always")),
    "yuan_2024_contact": ("QJJC", 9, 7,
                          "Intergroup Contact Experience Scale (Yang et al. revision)",
                          lambda i: CONTACT_ENDS[i]),
    "yuan_2024_trust": ("XR", 4, 7, "Intergroup Trust Scale",
                        lambda i: ("never feel this way", "always feel this way")),
}


def labels():
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / FNAME
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(zipfile.ZipFile(io.BytesIO(r.content)).read(FNAME))
    _, meta = pyreadstat.read_sav(str(p), metadataonly=True)
    labs = meta.column_names_to_labels
    assert not any(re.search(r"[一-鿿]", v or "") for v in labs.values())
    return labs


def main():
    labs = labels()
    for table, (prefix, n, top, instrument, ends) in TABLES.items():
        rows = []
        for i in range(1, n + 1):
            code = f"{prefix}{i:02d}"
            raw = labs[f"{code}T1"]
            m = re.match(rf"^{i}\.\s*(.+)$", raw)
            assert m, (code, raw)
            stem = m.group(1).strip()
            lo, hi = ends(i)
            for resp in range(1, top + 1):
                opt = lo if resp == 1 else hi if resp == top else ""
                rows.append({
                    "table": table, "section_id": f"{table}_1", "item": code,
                    "instrument": instrument, "language": "Chinese",
                    "instructions": "", "section_prompt": "",
                    "item_text": stem, "correct_response": "",
                    "option_text": opt, "resp": resp,
                    "instructions_translated": "", "section_prompt_translated": "",
                    "item_text_translated": "", "option_text_translated": "",
                })
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert {r["item"] for r in rows} == set(resp["item"].astype(str)), table
        assert {r["resp"] for r in rows} == set(resp["resp"].astype(int)), table
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUT_DIR / f"{table}__items.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{path.name}: {len(rows)} rows, {n} items")
        for r in rows[::top]:
            print(f"   {r['item']}: {r['item_text']}")


if __name__ == "__main__":
    main()
