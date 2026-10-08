#!/usr/bin/env python3
"""Item text for prihandoko_2025_ews (Zenodo 10.5281/zenodo.18056003).

Cheap case: a Google Forms export whose column headers are the administered
Indonesian statements. data/prihandoko_2025_ews.py assigns ews1-ews13 to those
headers in column order and exposes the exact (code, header) pairs via stems(),
imported here, so each stem is the header its responses sit under. Stems are
verbatim (outer whitespace stripped). Instrument name from the deposit file name.

item_text_translated is IRW's own English translation (translation_source =
machine_translation in the provenance note; owes an itemtext_issues.qmd entry).
No option labels in the deposit, so option_text is blank for resp 1-5.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "prihandoko_2025_ews.py"
OUT = HERE / "itemtext_output" / "prihandoko_2025_ews__items.csv"
RESP = HERE / "irw_output" / "prihandoko_2025_ews.csv"
TABLE = "prihandoko_2025_ews"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]
EN = {
    "ews1": "I do not often experience mental exhaustion (burnout) or excessive stress due to my current workload.",
    "ews2": "My job allows me to maintain good physical health (enough rest, no disruption to my sleep hours).",
    "ews3": "I feel that the compensation and benefits provided by the company give me a sense of financial security.",
    "ews4": "I feel able to balance the demands of work with my personal life (\"Thriving\").",
    "ews5": "I feel the company truly cares about my well-being, not merely providing programs as a formality.",
    "ews6": "I feel safe to express opinions, take risks, or innovate without fear of being judged (Psychological Safety).",
    "ews7": "Management communication is transparent and the workload given to me is still within reasonable limits.",
    "ews8": "I feel comfortable using the health services or well-being programs provided by the office (if any).",
    "ews9": "I feel highly involved (engaged) and enthusiastic when doing my work.",
    "ews10": "The current work environment supports me to work with high productivity.",
    "ews11": "I would recommend this company to others as a good place to work (acting as a Brand Ambassador).",
    "ews12": "I plan to keep working at this company for a long time.",
    "ews13": "I rarely take sick leave for reasons of stress or work pressure",
}


def main():
    spec = importlib.util.spec_from_file_location("ews", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pairs = mod.stems()
    resp = pd.read_csv(RESP)
    assert {c for c, _ in pairs} == set(EN) == set(resp["item"])
    rows = []
    for code, head in pairs:
        for r in range(1, 6):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": "Employee Well-Being Score (EWS)", "language": "Indonesian",
                         "instructions": "", "instructions_translated": "", "section_prompt": "",
                         "item_text": " ".join(head.split()), "item_text_translated": EN[code],
                         "correct_response": "", "option_text": "",
                         "option_text_translated": "", "resp": r})
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{OUT.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
