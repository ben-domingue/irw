#!/usr/bin/env python3
"""Item text for rothlin_2022_scs_sf (Dryad 10.5061/dryad.2547d7wsv, Zenodo mirror 6633659;
paper 10.1080/1612197X.2021.2025134). Swiss athletes, administered in German; the deposit's
.sav carries ENGLISH SCS-SF stems as variable labels and English anchors as value labels,
so this is the fallback: language=German, English in the base fields, _translated empty,
text_source=translated_substitute.

Cheap case: data/rothlin_2022_self_compassion.py keeps the .sav variable names (scs1 ..
scs12) as item, so each variable label (stem) and its value labels (options) tie text to
code by name. The builder asserts every observed resp is a labelled option.
"""
import csv
import os
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "10.5061_dryad.2547d7wsv"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
T = "rothlin_2022_scs_sf"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated", "item_text",
        "item_text_translated", "correct_response", "option_text", "option_text_translated", "resp"]
INSTRUCTIONS = "Please read each statement carefully before answering. Indicate how often you behave in the stated manner."


def main() -> None:
    _, meta = pyreadstat.read_sav(str(RAW / "datafile_snf_diary.sav"), metadataonly=True)
    lab, vl = meta.column_names_to_labels, meta.variable_value_labels
    resp = pd.read_csv(RESP_DIR / f"{T}.csv")
    rows = []
    for it in sorted(resp["item"].unique(), key=lambda s: int(s[3:])):
        stem = " ".join(lab[it].split()).replace("fl aws", "flaws").replace("fi xate", "fixate")
        if it == "scs2":
            stem = "I " + stem   # the label dropped the leading pronoun
        opts = {int(k): " ".join(v.split()) for k, v in vl[it].items()}
        observed = set(resp.loc[resp["item"] == it, "resp"])
        assert observed <= set(opts), (it, observed)
        for k, o in sorted(opts.items()):
            rows.append({"table": T, "section_id": f"{T}_1", "item": it,
                         "instrument": "Self-Compassion Scale Short Form (SCS-SF)",
                         "language": "German", "instructions": INSTRUCTIONS,
                         "instructions_translated": "", "section_prompt": "",
                         "section_prompt_translated": "", "item_text": stem,
                         "item_text_translated": "", "correct_response": "",
                         "option_text": o, "option_text_translated": "", "resp": k})
    assert {r["item"] for r in rows} == set(resp["item"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{T}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {resp['item'].nunique()} items")
    for it in sorted({r['item'] for r in rows}, key=lambda s: int(s[3:])):
        print(" ", it, "|", next(r["item_text"] for r in rows if r["item"] == it))


if __name__ == "__main__":
    main()
