#!/usr/bin/env python3
"""Item text for the four gwen_2025 tables (Zenodo 10.5281/zenodo.17982683).

Cheap case: the deposit is a Google Forms export whose column headers are the
administered Indonesian statements. data/gwen_2025_social_support.py assigns the
codes (ic1-13, se1-2, ss1-3, mh1-4) to those headers in column order and exposes
the (code, header) pairs through its stems() function, which this script imports
-- so each stem is the very header its responses sit under. Stems are shipped
verbatim (trailing whitespace stripped only).

item_text_translated is IRW's own English translation (translation_source =
machine_translation in the provenance note; owes an itemtext_issues.qmd entry).
The deposit gives no option labels and no instructions, so option_text and
instructions are blank; resp 1-5 rows are emitted so the resp set matches.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "gwen_2025_social_support.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]
INSTR = {"gwen_2025_interpersonal_comm": "Interpersonal communication",
         "gwen_2025_self_esteem": "Self-esteem",
         "gwen_2025_social_support": "Social support",
         "gwen_2025_mental_health": "Mental health symptoms"}
EN = {
    "ic1": "I feel comfortable being open when talking with other people",
    "ic2": "I am able to understand other people's feelings when they talk to me",
    "ic3": "I give support to other people when they need me",
    "ic4": "I try to keep a positive attitude when communicating with other people",
    "ic5": "I treat the person I am talking with as an equal, without feeling superior or inferior",
    "ic6": "I am willing to share personal information with people I trust",
    "ic7": "I can feel relaxed when talking with new people",
    "ic8": "I am able to express my opinion firmly without offending others",
    "ic9": "I pay attention to other people's needs and perspectives when communicating",
    "ic10": "I can manage the flow of a conversation so that communication goes well",
    "ic11": "I can express my thoughts and feelings clearly",
    "ic12": "I respond quickly to the other person when they invite me to interact",
    "ic13": "I am able to adapt the way I communicate to a particular situation or environment",
    "se1": "I feel that I am a person of worth",
    "se2": "I value myself and believe in my personal abilities.",
    "ss1": "I feel I have someone who gives me emotional comfort when I am having problems",
    "ss2": "I get advice or information that helps me deal with problems from the people around me",
    "ss3": "I have someone who can help me directly when I need practical help.",
    "mh1": "I feel I experience symptoms of depression such as loss of motivation or low mood",
    "mh2": "I feel I experience anxiety such as excessive worry or difficulty feeling calm",
    "mh3": "I experience signs of trauma such as flashbacks, nightmares, or avoiding things that remind me of bad experiences",
    "mh4": "I experience sleep disturbances such as difficulty sleeping, waking up often, or restless sleep",
}


def main():
    spec = importlib.util.spec_from_file_location("gwen", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pairs = mod.stems()
    assert {c for v in pairs.values() for c, _ in v} == set(EN)
    for table, cs in pairs.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        for code, head in cs:
            for r in sorted(resp["resp"].unique()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": code,
                             "instrument": INSTR[table], "language": "Indonesian",
                             "instructions": "", "instructions_translated": "",
                             "section_prompt": "", "item_text": head.strip(),
                             "item_text_translated": EN[code], "correct_response": "",
                             "option_text": "", "option_text_translated": "", "resp": int(r)})
        assert {r["item"] for r in rows} == set(resp["item"])
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
