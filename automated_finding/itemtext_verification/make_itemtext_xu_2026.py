#!/usr/bin/env python3
"""Item text for the three xu_2026_* tables (figshare 32238702).

Cleaned_Dataset.xlsx's column headers are the administered Chinese stems, in the
record's construct order. data/xu_2026_heritage_game.py assigns codes by column
position (INTER1-3, AE1-4, PRES1-3, EMO1-3, VAL1-3, AUTH1-5, SUB1-4, COMP1-3,
VISIT1-3, PROT1-3, DISS1-3); this script re-reads the same workbook with the same
block sizes, so code->stem is the script's own map. The sheet stores answers as
numbers only and the record publishes no anchors, so option_text is blank (audit
WARN expected). English translations are IRW's (translation_source = irw_generated).
"""
import csv
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
RAW = HERE / "runs" / "raw" / "10_6084_m9_figshare_32238702_v1" / "Cleaned_Dataset.xlsx"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
BLOCKS = [("INTER", 3), ("AE", 4), ("PRES", 3), ("EMO", 3), ("VAL", 3), ("AUTH", 5), ("SUB", 4),
          ("COMP", 3), ("VISIT", 3), ("PROT", 3), ("DISS", 3)]
TABLES = {"xu_2026_game_experience": "Cultural heritage simulation game experience questionnaire -- experience constructs (interactivity, aesthetics, presence, emotional engagement, value, authenticity)",
          "xu_2026_substitutability": "Cultural heritage simulation game experience questionnaire -- perceived substitutability",
          "xu_2026_participation": "Cultural heritage simulation game experience questionnaire -- complementarity, visit intention, protection and dissemination willingness"}
EN = ["I feel that this simulation game lets me interact with it in both directions.",
      "The simulation game gives timely feedback based on my actions.",
      "During the game, I can easily control the interaction process, and it holds my attention.",
      "The overall layout of the simulation game is clear and easy to grasp.",
      "The game's visual design is creative and full of variety.",
      "The game's colour combinations are very attractive and make me feel pleased.",
      "The game's visual appearance shows a professional, high-level standard of design.",
      "During the experience, I felt surrounded by the virtual environment.",
      "I felt as if I were really in the physical space shown by the virtual world.",
      "I felt completely immersed in the virtual environment, to the point of ignoring the existence of the real world.",
      "While experiencing the simulation game, I felt I invested a great deal of emotional energy.",
      "The content of the simulation game (such as ancient-architecture culture) evokes an emotional resonance in me.",
      "The experience of the simulation game deeply attracted me emotionally.",
      "I think this simulation game experience was \"worth the money\".",
      "Compared with the time and effort I put in, experiencing the game offered very good value.",
      "I think this simulation game is very worth recommending.",
      "I think the cultural heritage content presented in the game is real and credible.",
      "The ancient-architecture elements in the game show the true character cultural heritage should have.",
      "I think the cultural presentation in the game faithfully restores the features of the real heritage.",
      "I feel the game stayed honest and objective in presenting the cultural heritage.",
      "I believe the cultural heritage information conveyed by the game is authoritative.",
      "After experiencing this simulation game, I feel the need to visit the site in person has decreased.",
      "I think the game experience can to a large extent replace a real on-site visit.",
      "For me, the experience the game provides is already enough to satisfy my need to visit this heritage site.",
      "The game gave me an experience very close to an on-site visit.",
      "The background knowledge the simulation game provides helps me understand the real cultural heritage more deeply.",
      "I think experiencing the simulation game will markedly raise the perceived quality of my future offline visits.",
      "The simulation game and an on-site visit complement each other well.",
      "I intend to visit in person the real cultural heritage site related to the game in the coming period.",
      "I will try to find opportunities to visit in person the cultural heritage sites shown in the game.",
      "If conditions allow, I am very willing to experience offline, in person, the real scenes the game involves.",
      "I am willing to support the protection of this cultural heritage in various forms.",
      "I think protecting the cultural heritage presented in the game is very important.",
      "I have a strong wish to take part in protection actions related to this cultural heritage.",
      "I intend to share my experience of this cultural heritage through various channels.",
      "I am willing to recommend this cultural heritage to people around me.",
      "I will do my best to spread more information about this cultural heritage to others."]


def main() -> None:
    d = pd.read_excel(RAW)
    heads = [c for c in d.columns if c not in ("性别", "年龄", "学位")]
    assert len(heads) == len(EN) == 37
    codes, i = {}, 0
    for pre, n in BLOCKS:
        for k in range(1, n + 1):
            codes[f"{pre}{k}"] = (heads[i], EN[i])
            i += 1
    for table, instr in TABLES.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        items = [c for c in codes if c in set(resp["item"])]
        assert set(items) == set(resp["item"]), table
        rows = []
        for it in items:
            zh, en = codes[it]
            for r in sorted(resp.loc[resp["item"] == it, "resp"].unique()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": it, "instrument": instr,
                             "language": "Chinese", "instructions": "", "section_prompt": "", "item_text": zh,
                             "correct_response": "", "option_text": "", "resp": int(r),
                             "instructions_translated": "", "section_prompt_translated": "",
                             "item_text_translated": en, "option_text_translated": ""})
        with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(table, len(rows), "rows")


if __name__ == "__main__":
    main()
