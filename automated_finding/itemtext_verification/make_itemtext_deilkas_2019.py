#!/usr/bin/env python3
"""Item text for deilkas_2019_saq and deilkas_2019_collaboration (PLOS ONE
10.1371/journal.pone.0218244, S3 File .sav). Norwegian nursing-home staff, administered in
Norwegian; the deposit's .sav carries ENGLISH stems as variable labels and English anchors
as value labels, so this is the fallback: language=Norwegian, English in the base fields,
_translated empty, text_source=translated_substitute.

Cheap case: data/deilkas_2019_saq_nursing_homes.py keeps the .sav variable names (SAQ1 ..
SAQ62, Physicians .. Hospital) as item, so each variable label and its value labels tie
text to code by name. The SAQ labels start with their item number ("1. High levels of
..."), which is stripped. 0 "Not applicable" was dropped from the response table and is
not emitted. The builder asserts every observed resp is a labelled option.
"""
import csv
import os
import re
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "10.1371_journal.pone.0218244"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated", "item_text",
        "item_text_translated", "correct_response", "option_text", "option_text_translated", "resp"]
META = {"deilkas_2019_saq": ("Safety Attitudes Questionnaire, nursing home version (62 items)",
                             "Please answer the following items with respect to your specific unit or clinical area."),
        "deilkas_2019_collaboration": ("Safety Attitudes Questionnaire, collaboration and communication ratings",
                                       "With respect to your experiences at this site, use the scale to describe the quality of collaboration and communication that you have experienced with:")}
COLLAB_STEM = re.compile(r"experienced with (.+?):?\s*$")


def main() -> None:
    _, meta = pyreadstat.read_sav(str(RAW / "pone.0218244.s003.sav"), metadataonly=True)
    lab, vl = meta.column_names_to_labels, meta.variable_value_labels
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (instrument, instructions) in META.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        key = (lambda s: int(s[3:])) if table.endswith("saq") else None
        for it in sorted(resp["item"].unique(), key=key):
            stem = " ".join(lab[it].split())
            if table.endswith("saq"):
                stem = re.sub(r"^\d+\.\s*", "", stem)
            else:
                stem = COLLAB_STEM.search(stem).group(1).strip().strip("\u200e")
                # kept verbatim, Norwegian words and spellings included ("ambulansepersonell", "sykehus")
            opts = {int(k): " ".join(v.split()) for k, v in vl[it].items() if int(k) != 0}
            observed = set(resp.loc[resp["item"] == it, "resp"])
            assert observed <= set(opts), (it, observed, opts)
            for k, o in sorted(opts.items()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": instrument, "language": "Norwegian",
                             "instructions": instructions, "instructions_translated": "",
                             "section_prompt": "", "section_prompt_translated": "",
                             "item_text": stem, "item_text_translated": "", "correct_response": "",
                             "option_text": o, "option_text_translated": "", "resp": k})
        assert {r["item"] for r in rows} == set(resp["item"])
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {resp['item'].nunique()} items")
        for r in rows[::5][:3]:
            print("  ", r["item"], "|", r["item_text"][:80], "|", r["option_text"])


if __name__ == "__main__":
    main()
