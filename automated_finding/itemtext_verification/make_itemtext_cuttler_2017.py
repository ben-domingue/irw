#!/usr/bin/env python3
"""Item text for cuttler_2017_dfaqcu_freq (PLOS ONE 10.1371/journal.pone.0178194; data
S2 File.sav, inventory S1 File.docx, figshare 10.6084/m9.figshare.5045962). English
administration (US undergraduates and community users; the inventory is in English).

Cheap case. data/cuttler_2017_cannabis.py keeps the .sav variable names (DFAQCU2, ...) as
`item`, so each SPSS variable label (the stem) and its value labels (the options) tie text
to code by name. The S1 File inventory is the authors' own CC BY material and gives the
same stems and options; the builder asserts every option label it ships is in the .sav's
value labels for that item.

Two items have no value labels because they are free counts: DFAQCU7 ("Approximately how
many days of the past month did you use cannabis?", 0-31) gets one row per observed count
with option_text blank (an unlabelled numeric answer is left blank, never padded with its
own number). DFAQCU6's labels are "0 days" .. "7 days" and ship as written.
Instructions: the S1 File's inventory instructions, verbatim.
"""
import csv
import os
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "plos_0178194"
OUT_DIR = Path(os.environ.get("ITEMTEXT_OUT_DIR", HERE / "itemtext_output"))
RESP_DIR = Path(os.environ.get("IRW_RESP_DIR", HERE / "irw_output"))
T = "cuttler_2017_dfaqcu_freq"
INSTRUMENT = ("Daily Sessions, Frequency, Age of Onset, and Quantity of Cannabis Use Inventory "
              "(DFAQ-CU), frequency items")
INSTRUCTIONS = ("Please read each of the following questions and mark the response alternative "
                "that best describes your use of cannabis. Note that the term cannabis is being "
                "used to refer to marijuana, cannabis concentrates, and cannabis-infused edibles.")
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def main() -> None:
    _, meta = pyreadstat.read_sav(str(RAW / "S2 File.sav"), metadataonly=True)
    lab, vl = meta.column_names_to_labels, meta.variable_value_labels
    resp = pd.read_csv(RESP_DIR / f"{T}.csv")
    rows = []
    for it in sorted(resp["item"].unique(), key=lambda s: int(s[6:])):
        stem = " ".join(lab[it].split())
        observed = sorted(resp.loc[resp["item"] == it, "resp"].unique())
        if it in vl:
            opts = {int(k): " ".join(v.split()) for k, v in vl[it].items()}
            assert set(observed) <= set(opts), (it, observed)
        else:
            assert it == "DFAQCU7", it
            opts = {int(k): "" for k in observed}
        for k, o in sorted(opts.items()):
            rows.append({"table": T, "section_id": f"{T}_1", "item": it,
                         "instrument": INSTRUMENT, "instructions": INSTRUCTIONS,
                         "section_prompt": "", "item_text": stem, "correct_response": "",
                         "option_text": o, "resp": k})
    assert {r["item"] for r in rows} == set(resp["item"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{T}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {resp['item'].nunique()} items")
    for it in sorted({r['item'] for r in rows}):
        print(" ", it, "|", next(r["item_text"] for r in rows if r["item"] == it))


if __name__ == "__main__":
    main()
