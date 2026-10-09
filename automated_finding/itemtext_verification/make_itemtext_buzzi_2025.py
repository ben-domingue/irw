#!/usr/bin/env python3
"""Item text for buzzi_2025_autonomy (Zenodo 10.5281/zenodo.15305238).

Cheap case: a LimeSurvey export whose column headers are
"G01Q04[SQ00k]. <question> <option legend> [<subquestion>]". data/buzzi_2025_students_covid.py
assigns item codes from those headers (brackets -> underscore) and exposes the exact
(code, question, subquestion) triples via stems(), imported here, so each item's text is
the header its responses sit under. instructions = the question text with its trailing
"1: per niente; ...; 5: completamente" legend removed; item_text = the bracketed
subquestion, verbatim. Options from the deposit's Foglio1 codebook sheet via options(),
cross-checked against the legend in the header.

The *_translated columns are IRW's own English translation (translation_source =
machine_translation in the provenance note; owes an itemtext_issues.qmd entry).
Run with IRW_RAW_DIR set as for the data script.
"""
import csv
import importlib.util
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "buzzi_2025_students_covid.py"
TABLE = "buzzi_2025_autonomy"
OUT = HERE / "itemtext_output" / f"{TABLE}__items.csv"
RESP = HERE / "irw_output" / f"{TABLE}.csv"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]
INSTR_EN = "Indicate how independent you are in carrying out the following activities"
ITEM_EN = {
    "G01Q04_SQ001": "School and study activities",
    "G01Q04_SQ002": "Sports activities",
    "G01Q04_SQ003": "Leisure activities (going out with friends, playing an instrument, "
                    "going on trips/excursions, ...)",
    "G01Q04_SQ004": "Getting around (the school-home journey, or to do sports or leisure "
                    "activities, etc.)",
}
OPT_EN = {1: "not at all", 2: "a little", 3: "fairly", 4: "very", 5: "completely"}


def main():
    spec = importlib.util.spec_from_file_location("buzzi", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    triples = mod.stems(TABLE)
    opts = mod.options("G01Q04")
    resp = pd.read_csv(RESP)
    assert {c for c, _, _ in triples} == set(ITEM_EN) == set(resp["item"])
    assert sorted(opts) == sorted(resp["resp"].unique()) == [1, 2, 3, 4, 5]
    rows = []
    for code, question, sub in triples:
        instr, legend = re.match(r"^(.*?attività)\s+(1: .*)$", question).groups()
        assert legend == "; ".join(f"{k}: {v}" for k, v in sorted(opts.items()))
        for r in range(1, 6):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": "Autonomy in everyday activities (study-specific)",
                         "language": "Italian",
                         "instructions": instr, "instructions_translated": INSTR_EN,
                         "section_prompt": "", "item_text": sub,
                         "item_text_translated": ITEM_EN[code], "correct_response": "",
                         "option_text": opts[r], "option_text_translated": OPT_EN[r],
                         "resp": r})
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{OUT.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
