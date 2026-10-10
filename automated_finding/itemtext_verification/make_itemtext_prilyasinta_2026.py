#!/usr/bin/env python3
"""Item text for the six prilyasinta_2026_* tables (Zenodo 10.5281/zenodo.18365911;
article 10.1080/14664208.2026.2646706). Administered in Indonesian.

Source: the deposit's "Full questionnaire items for pilot and main Study.pdf", whose pilot
list numbers the 39 items 1-39, each as the Indonesian stem followed by the authors'
English. data/prilyasinta_2026_balinese_motivation.py codes item k as bali_<k> by matching
each CSV header (the full Indonesian stem) to exactly one numbered PDF item, so this
builder uses the same match: item_text = the CSV header (administered wording),
item_text_translated = the rest of PDF item k after its Indonesian stem.
Options: the 1-6 points are not labelled anywhere in the deposit; option_text and
option_text_translated stay blank (no number padding).
"""
import csv
import os
import re
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "z18365911"
P = "prilyasinta_2026_"
TABLES = ["identity", "responsibility", "connectedness", "multilingualism", "intensity",
          "pilot_items"]
INSTRUMENT = ("Balinese language motivation questionnaire (Prilyasinta & Purnawan 2026; "
              "tripartite motivation framework)")
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]
norm = lambda s: " ".join(str(s).split())  # noqa: E731


def main():
    txt = subprocess.run(["pdftotext", str(RAW / "questionnaire.pdf"), "-"], capture_output=True,
                         text=True, check=True).stdout
    pil = txt[txt.index("For Pilot Study"):txt.index("For Main Study")]
    b = re.split(r"\n(\d+)\.\s", pil)
    pdf = {int(b[i]): norm(b[i + 1]) for i in range(1, len(b), 2)}
    e = pd.read_csv(RAW / "efa.csv")
    stem = {}
    for c in e.columns[8:]:
        k = [k for k, v in pdf.items() if v.startswith(norm(c))]
        assert len(k) == 1, c
        stem[f"bali_{k[0]}"] = (norm(c), pdf[k[0]][len(norm(c)):].strip())
    assert len(stem) == 39 and all(en for _, en in stem.values())
    for t in TABLES:
        table = P + t
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        rows = []
        for it in sorted(resp["item"].unique(), key=lambda s: int(s[5:])):
            for r in range(1, 7):
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": INSTRUMENT, "language": "Indonesian",
                             "instructions": "", "instructions_translated": "",
                             "section_prompt": "", "item_text": stem[it][0],
                             "item_text_translated": stem[it][1], "correct_response": "",
                             "option_text": "", "option_text_translated": "", "resp": r})
        with open(HERE / "itemtext_output" / f"{table}__items.csv", "w", newline="",
                  encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{table}__items.csv: {len(rows)} rows")


if __name__ == "__main__":
    main()
