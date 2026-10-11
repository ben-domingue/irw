#!/usr/bin/env python3
"""Item text for fang_2026_anime_museum (Harvard Dataverse DVN/LWQ2PF).

"raw versions.xlsx" carries the 38 administered Chinese stems as headers
("5、7.\\t在藏馆里 ..."), numbered 1-38; "processed versions.xlsx" (sheet "Topics
(Classified)") carries the same 38 items as construct codes with the same number
in brackets ("INTER3 (7)"). data/fang_2026_anime_museum.py ships the processed
codes; this script ties each code to its stem by that shared item number, so the
mapping is by the deposit's own numbering rather than by position alone. Answers
are numbers (1-7) with no anchors in the deposit, so option_text is blank (audit
WARN expected). English translations are IRW's (translation_source = irw_generated).
"""
import csv
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
RAW_DIR = HERE / "runs" / "raw" / "10_7910_dvn_lwq2pf"
TABLE = "fang_2026_anime_museum"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
INSTR = "Virtual anime-themed heritage museum (SCAA qualia experience) user questionnaire, 38 items"
EN = ["The museum's space is very realistic; I feel as if I am actually there.",
      "I can move freely around the museum as in the real world.",
      "The situation of talking with the virtual guide in the museum is the same as in the real world.",
      "The design of the cultural stories on different themes in the museum immerses me.",
      "The museum's interactive interface has clear instructions and is easy to pick up.",
      "The museum's interactive interface is convenient and smooth to use.",
      "In the museum, I can enjoy the visit through interaction with the surroundings (such as the virtual guide, music, lighting effects).",
      "In the museum, I can enjoy the visit through interaction with virtual characters on different themes.",
      "The intelligent voice reading of the exhibits helps me understand them.",
      "The intelligent virtual-human function in the museum incorporates the latest science and technology.",
      "For me, the application of intelligent technology in the museum is an innovative experience.",
      "The stimulation of the senses (such as kinaesthetic, visual, tactile, auditory) by the intelligent technology in the museum enhanced my experience.",
      "The exhibits' transformation of culture shows a distinctive beauty.",
      "The overall design of the museum has visual beauty.",
      "The museum and its exhibits show the unique charm of Eastern aesthetics.",
      "This experience gave me aesthetic enjoyment.",
      "The styling design of the exhibits is interesting.",
      "Exploring the hidden functions of the exhibits is fun for me.",
      "The overall process of viewing the digital exhibits in the museum is enjoyable.",
      "The whole digital museum is playable.",
      "By visiting the museum I can deeply feel the cultural meaning of the exhibits.",
      "By visiting the museum I can learn about traditional culture.",
      "The digital exhibits inspire me to reflect on culture, and I am moved by its charm.",
      "The digital exhibits in the museum serve to carry cultural knowledge.",
      "I like entering this digital museum to visit.",
      "I long to experience the digital museum often.",
      "I look forward to owning similar digital exhibits.",
      "The whole visit experience fascinated me.",
      "The whole visit experience gave me a desire to explore.",
      "I will collect the exhibits in the digital museum.",
      "I plan to keep experiencing this museum through more advanced devices in the future.",
      "I will experience new functions of the museum and its exhibits later on.",
      "I will let others know that I have experienced this digital museum.",
      "I will recommend that others experience this digital museum.",
      "Being able to use the device to experience the museum makes me feel confident.",
      "Being able to experience the exhibits freely in the virtual space makes me feel proud.",
      "Being able to operate the device skilfully for the experience gives me a sense of achievement.",
      "Visiting the museum helps me relieve anxiety and release stress."]


def main() -> None:
    raw = pd.read_excel(RAW_DIR / "raw versions.xlsx")
    proc = pd.read_excel(RAW_DIR / "processed versions.xlsx", sheet_name="Topics (Classified)")
    stems = {}
    for c in raw.columns:
        m = re.match(r"5、(\d+)\.\s*(.+)$", str(c))
        if m:
            stems[int(m.group(1))] = m.group(2).strip()
    codes = {}
    for c in proc.columns:
        m = re.match(r"(\w+?)\s*\((\d+)\)\s*$", str(c))
        if m:
            codes[m.group(1)] = int(m.group(2))
    assert sorted(stems) == sorted(codes.values()) == list(range(1, 39))
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert set(codes) == set(resp["item"]), set(codes) ^ set(resp["item"])
    rows = []
    for code, num in codes.items():
        for r in sorted(resp.loc[resp["item"] == code, "resp"].unique()):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code, "instrument": INSTR,
                         "language": "Chinese", "instructions": "", "section_prompt": "", "item_text": stems[num],
                         "correct_response": "", "option_text": "", "resp": int(r),
                         "instructions_translated": "", "section_prompt_translated": "",
                         "item_text_translated": EN[num - 1], "option_text_translated": ""})
    with open(OUT_DIR / f"{TABLE}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(TABLE, len(rows), "rows")


if __name__ == "__main__":
    main()
