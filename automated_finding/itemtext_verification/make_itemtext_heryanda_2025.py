#!/usr/bin/env python3
"""Item text for heryanda_2025_gamification_features / _psychological_needs / _usage_outcomes
(Mendeley 10.17632/mkd998xj9j). Indonesian stems from the Google-Forms column headers ("REW1. ..."),
keyed by the printed code = the table's item. Anchors are not in the file (1-5) -> option_text blank.
Indonesian administration; English in _translated is IRW's.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("heryanda_2025_digital_banking_gamification")
EN = {
    "REW1": "In the digital banking app I use, rewards are only given to users who actively make transactions.",
    "REW2": "I would use digital banking more often if the app gave rewards.",
    "REW3": "The reward feature in the digital banking app is easy to use because its design is simple and clear.",
    "REW4": "The reward feature in the digital banking app motivates me to increase my transaction activity.",
    "LEV1": "I feel happy when the digital banking app has a level feature.",
    "LEV2": "The level feature motivates me to use the digital banking app more often.",
    "LEV3": "The level feature in the digital banking app is easy to use because its design is simple and clear.",
    "LEV4": "The level feature in the digital banking app motivates me to increase my transaction activity.",
    "PNT1": "The points feature in the digital banking app is easy to use because its design is simple and clear.",
    "PNT2": "Earning points for every digital banking activity encourages me to use the app's features more often.",
    "PNT3": "The points feature in the digital banking app helps me reach my financial goals more effectively.",
    "PNT4": "The points feature in the digital banking app encourages me to increase my transaction activity.",
    "AUT1": "The digital banking app I use provides various options for managing my finances.",
    "AUT2": "I am confident the digital banking app can adjust financial goals to my needs.",
    "AUT3": "With the digital banking app, I can set financial goals that suit my needs.",
    "AUT4": "The digital banking app gives me the freedom to use it according to my needs.",
    "COMP1": "Points from the digital banking app make me feel more competent in managing my finances.",
    "COMP2": "Rewards from the digital banking app make me feel more competent in managing my finances.",
    "COMP3": "Moving up a level in the app makes me feel more competent in managing my finances.",
    "COMP4": "After using the digital banking app for some time, I feel more competent in managing my finances.",
    "REL1": "The gamification elements in the digital banking app make me feel closer to the service provided.",
    "REL2": "I feel connected to the digital banking app because it helps meet my financial needs.",
    "REL3": "When I use digital banking features that suit my needs, I feel more comfortable and connected to the service.",
    "REL4": "After learning how others use the digital banking app's features (through reviews or testimonials), I feel more confident using the service.",
    "MOT1": "I find the digital banking app I use interesting.",
    "MOT2": "I like using the digital banking app I use.",
    "MOT3": "The digital banking app I use helps me with financial management.",
    "MOT4": "I feel motivated to use the digital banking app when it provides services the way I want.",
    "SAT1": "I am satisfied with my experience of using the digital banking app.",
    "SAT2": "I am satisfied with the features available in the digital banking app.",
    "SAT3": "When I am satisfied using the digital banking app, I will recommend it to others.",
    "SAT4": "Overall, I am satisfied with the digital banking app I use.",
    "CON1": "The experience of using the digital banking app is better than I expected.",
    "CON2": "The features provided by the digital banking app I use are better than I expected.",
    "CON3": "I use the digital banking app to manage my finances better than I expected.",
    "CON4": "Managing finances in the digital banking app is more interesting than I expected.",
    "USE1": "Using the digital bank app I use improves the effectiveness of my financial management.",
    "USE2": "The digital banking app helps save time on transactions and improves the efficiency of my financial management.",
    "USE3": "I find the digital banking app useful in everyday life.",
    "USE4": "Overall, the digital bank app I use is beneficial.",
    "CI1": "I intend to keep using the digital banking app I use.",
    "CI2": "I intend to increase how often I use the digital banking app I currently use.",
    "CI3": "I intend to keep using the digital banking app in the future.",
    "CI4": "I will always try to use the digital banking app in everyday life."}
INSTR = {"gamification_features": "Gamification features in digital banking apps (rewards, levels, points), 12 items",
         "psychological_needs": "Basic psychological needs in digital banking use (autonomy, competence, relatedness), 12 items",
         "usage_outcomes": "Motivation, satisfaction, confirmation, usefulness and continuance intention, 20 items"}


def main():
    stems = mod.headers()
    assert set(stems) == set(EN)
    import re
    for g, prefixes in mod.GROUPS.items():
        table = f"heryanda_2025_{g}"
        codes = [c for c in stems if re.match(r"([A-Z]+)\d", c).group(1) in prefixes]
        rows = [row(table, f"{table}_1", c, INSTR[g], "Indonesian", r, stems[c], option_text="", item_text_tr=EN[c])
                for c in codes for r in range(1, 6)]
        write(table, rows)


if __name__ == "__main__":
    main()
