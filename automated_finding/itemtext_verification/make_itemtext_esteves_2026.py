#!/usr/bin/env python3
"""Item text for esteves_2026_sdi and esteves_2026_dddt (Mendeley 10.17632/thmf63pbzr).
Portuguese (Brazil) administration.

Cheap case: the .sav variable labels are the Portuguese stems ("1- Sexo com animais.");
data/esteves_2026_sexual_disgust_dark_triad.py exposes stems(block) -> (code, stem) pairs read
from those labels, so the item code is the deposit's own column name. The file has no value
labels, so option_text is blank on every scale point (one row per item x point). English in item_text_translated is an IRW
translation.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "esteves_2026_sexual_disgust_dark_triad.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
META = {"sdi": ("esteves_2026_sdi", "Sexual Disgust Inventory (SDI), Brazilian Portuguese", range(1, 8)),
        "dddt": ("esteves_2026_dddt", "Dirty Dozen Dark Triad (DDDT), Brazilian Portuguese", range(1, 6))}
EN = {
    "SDI_01": "Sex with animals.", "SDI_02": "Whipping someone during sex.",
    "SDI_03": "Giving and receiving oral sex at the same time (\"69\").",
    "SDI_04": "Sex between two women.", "SDI_05": "Sex involving three people.",
    "SDI_06": "Sex with someone who has unpleasant body odour.",
    "SDI_07": "Sex with someone under 18 years of age.", "SDI_08": "Causing someone pain during sex.",
    "SDI_09": "A man performing oral sex on a woman.", "SDI_10": "Male homosexuality.",
    "SDI_11": "Watching pornography.", "SDI_12": "Sex with someone who has bad breath.",
    "SDI_13": "Sexual pleasure from the use of human faeces.",
    "SDI_14": "Tying up and/or restraining (bondage) a man for sexual purposes.",
    "SDI_15": "A woman performing oral sex on a man.", "SDI_16": "Female homosexuality.",
    "SDI_17": "An agreement between couples to have sex with other couples outside the relationship.",
    "SDI_18": "Rape.", "SDI_19": "Tying up and/or restraining (bondage) a woman for sexual purposes.",
    "SDI_20": "Licking someone during sex.", "SDI_21": "Group sex or orgies.",
    "SDI_22": "Sex between siblings.", "SDI_23": "Domination and/or submission during sex.",
    "SDI_24": "Sex between two men.", "SDI_25": "Sex with one's father and/or mother.",
    "SDI_26": "Sex with a dead person.", "SDI_27": "Spanking someone's buttocks during sex.",
    "SDI_28": "Vomiting during sex.", "SDI_29": "Sex with one's own child.",
    "SDI_30": "Choking someone during sex.", "SDI_31": "Pornography involving children.",
    "DD_01": "Manipulates others to get what they want.", "DD_02": "Deceives or lies to get what they want.",
    "DD_03": "Flatters people to get what they want.", "DD_04": "Exploits others for their own benefit.",
    "DD_05": "Lacks remorse.", "DD_06": "Is unconcerned with the morality of their actions.",
    "DD_07": "Is callous or insensitive.", "DD_08": "Is cynical.", "DD_09": "Wants others to admire them.",
    "DD_10": "Wants attention from others.", "DD_11": "Seeks prestige or status.",
    "DD_12": "Expects special favours from others.",
}


def main():
    spec = importlib.util.spec_from_file_location("esteves", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for block, (table, instrument, scale) in META.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        codes = mod.stems(block)
        assert {c for c, _ in codes} == set(resp["item"]) == {c for c in EN if c in dict(codes)}, table
        rows = []
        assert set(resp["resp"].unique()) <= set(scale), table
        for code, pt in codes:
            for r in scale:  # one row per scale point; anchors not in the file, option_text blank
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                             "language": "Portuguese", "instructions": "", "section_prompt": "", "item_text": pt,
                             "correct_response": "", "option_text": "", "resp": r,
                             "instructions_translated": "", "section_prompt_translated": "",
                             "item_text_translated": EN[code], "option_text_translated": ""})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(codes)} items")


if __name__ == "__main__":
    main()
