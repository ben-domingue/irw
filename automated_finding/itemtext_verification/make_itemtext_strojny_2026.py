#!/usr/bin/env python3
"""Item text for strojny_2026_gmi (10.1038/s41598-026-49533-9, osf.io/ay296).

Source: the deposit's own SPSS file, "GMI-PL validation data.sav". Every item
column GMI1..GMI88 -- which data/strojny_2026_gaming_motivation.py keeps as the
IRW item code, unchanged -- carries a variable label of the form

    D_GMI_<n>_<subscale>_<shared prompt> - <item stem>

e.g. "D_GMI_1_Rozwój_Dlaczego grasz w gry wideo? Gram w gry wideo… - ponieważ
lubię uczucie ciągłego awansowania." The number in the label is asserted equal
to the column's own number, the shared prompt becomes section_prompt (two
sections: items 1-66 "Why do you play", 67-88 "What kinds of games do you
prefer"), and the stem after " - " becomes item_text. The subscale name is
the authors' scoring key, not something respondents read, and is not shipped.

Anchors come from the value labels, identical on all 88 items:
"1 zdecydowanie się nie odnosi", "2".."6", "7 zdecydowanie się odnosi",
99 = "uzasadniony brak danych" (justified missing; never observed). The
leading numeral of the two endpoint labels is the resp code and is dropped;
the bare-number midpoint labels are left blank, not padded.

Administered language is Polish (the paper: "we translated the Polish version
from the English item set supplied by the original authors"). The English GMI
item set is not in the deposit or the SI, so the *_translated fields are IRW's
own translation of the Polish (stems and prompts); the two endpoint anchors use
the paper's own English ('Definitely not applicable' / 'Definitely
applicable').

Labels are transcribed verbatim, including two source slips: GMI23 has no
final full stop and GMI29 reads "rzeczywywistości" (the SI's Appendix has
"rzeczywistości"). The .sav gives masculine forms only ("miałem",
"powinienem", "sam", "kompetentny"); the SI Appendix prints both forms
("miałem/miałam"). The .sav wording is shipped, as the file's own label.

IGDS9-SF and GDT (strojny_2026_igds9sf, strojny_2026_gdt) are NOT built: both
are Dr. Halley Pontes's instruments, and itemtext/instrument_rights_register.csv
blocks IGDS9-SF (CC BY-NC-ND footer + permission-for-translations clause,
ruled 2026-09-09); the GDT page on the same site carries the same footer and
clause.
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
SAV = HERE / "runs" / "raw" / "strojny_2026" / "GMI-PL_validation_data.sav"
TABLE = "strojny_2026_gmi"

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

PROMPT_EN = {
    "Dlaczego grasz w gry wideo? Gram w gry wideo…":
        "Why do you play video games? I play video games…",
    "Jakie rodzaje gier preferujesz? Lubię gry wideo, które…":
        "What kinds of games do you prefer? I like video games that…",
}

EN = {
    1: "because I like the feeling of constant advancement.",
    2: "because I like levelling up in games.",
    3: "because I like it when I move on to the next level/stage in games.",
    4: "I used to have good reasons, but now I ask myself whether I should keep playing.",
    5: "honestly, I don't know; I feel that I am wasting my time.",
    6: "it has stopped being clear; sometimes I ask myself whether it is good for me.",
    7: "because I can decide for myself what I do in games.",
    8: "because I can play games according to my own preferences.",
    9: "because they give me interesting options and choices.",
    10: "because I experience a lot of freedom in games.",
    11: "because I am bored.",
    12: "to kill time.",
    13: "because I have nothing else to do.",
    14: "because when I am doing well in a game, I feel good about myself.",
    15: "because my successes raise my self-esteem.",
    16: "because I feel very competent and effective while playing.",
    17: "because I like competing with others.",
    18: "because I like winning.",
    19: "because I like being better than others.",
    20: "until I have finished 100% of the game, I collect everything I can.",
    21: "until I unlock all the achievements.",
    22: "until I master all the elements of the game.",
    23: "because they help me vent my anger",
    24: "because they help me de-stress.",
    25: "because they put me in a better mood.",
    26: "to avoid thinking about real problems and worries.",
    27: "because playing helps me forget everyday troubles.",
    28: "to forget unpleasant things or hurts.",
    29: "because playing helps me escape from reality.",
    30: "because I like discovering different elements or possibilities of the game.",
    31: "because I like experimenting with different ways of playing.",
    32: "because I like working out how particular elements of the game work.",
    33: "because I like exploring/learning the game mechanics in depth.",
    34: "because I can do things that are not possible in reality or that I am not allowed to do.",
    35: "because I can be in another world.",
    36: "because I can be someone else or somewhere else for a while.",
    37: "because I feel immersed in the virtual world.",
    38: "because I have the opportunity to earn money.",
    39: "because I have a chance of extra income.",
    40: "because I can earn some money.",
    41: "because I like reaching the peak of my abilities.",
    42: "because I like perfecting specific skills in games.",
    43: "because I like constantly improving my play.",
    44: "because I like practising and perfecting my play.",
    45: "because playing games is a meaningful activity.",
    46: "because games are an extension of me.",
    47: "because they are an integral part of my life.",
    48: "because they have personal meaning for me.",
    49: "because games are in harmony with the other activities in my life.",
    50: "because I have to play to feel good about myself.",
    51: "because otherwise I would feel bad about myself.",
    52: "because I feel that I have to play regularly.",
    53: "because games are fun.",
    54: "for fun.",
    55: "to relax.",
    56: "because playing sharpens my senses.",
    57: "because they improve my skills.",
    58: "because they improve my concentration.",
    59: "because they improve my coordination.",
    60: "because I can meet new people.",
    61: "because I like playing with others.",
    62: "because I feel connected to other players.",
    63: "because I consider relationships with other players important.",
    64: "for the prestige of being a good player.",
    65: "because I gain the recognition and respect of others.",
    66: "because others see me as a competent player.",
    67: "raise my adrenaline level.",
    68: "keep me in suspense.",
    69: "raise the level of excitement.",
    70: "are intense and dynamic.",
    71: "allow players to cooperate with others.",
    72: "promote working together as a group.",
    73: "require teamwork.",
    74: "allow players to customise in-game objects (e.g. avatar/vehicle/items…).",
    75: "give players many customisation options.",
    76: "allow players to customise their items/things/characters so as to give a sense of uniqueness.",
    77: "allow players to make explosions.",
    78: "involve destruction.",
    79: "allow players to break things.",
    80: "are visually breathtaking.",
    81: "have excellent graphics.",
    82: "have good graphics, are simply beautiful.",
    83: "have an interesting plot.",
    84: "have an elaborate plot that stirs my emotions.",
    85: "have an absorbing narrative.",
    86: "require strategic thinking.",
    87: "require planning ahead and making strategic decisions.",
    88: "require making tactical decisions.",
}

LABEL = re.compile(r"^D_GMI_(\d+)_[^_]+_(.+?) - (.+)$")


def main():
    if not SAV.exists():
        sys.exit(f"run data/strojny_2026_gaming_motivation.py first ({SAV})")
    _, meta = pyreadstat.read_sav(str(SAV), metadataonly=True)
    labels = meta.column_names_to_labels
    vlab = meta.variable_value_labels
    expected_vl = {1.0: "1 zdecydowanie się nie odnosi", 2.0: "2", 3.0: "3",
                   4.0: "4", 5.0: "5", 6.0: "6",
                   7.0: "7 zdecydowanie się odnosi",
                   99.0: "uzasadniony brak danych"}
    options = [(1, "zdecydowanie się nie odnosi", "Definitely not applicable"),
               (2, "", ""), (3, "", ""), (4, "", ""), (5, "", ""), (6, "", ""),
               (7, "zdecydowanie się odnosi", "Definitely applicable")]
    sections = {}
    rows = []
    for n in range(1, 89):
        code = f"GMI{n}"
        m = LABEL.match(labels[code])
        assert m, (code, labels[code])
        assert int(m.group(1)) == n, (code, m.group(1))
        prompt, stem = m.group(2).strip(), m.group(3).strip()
        assert prompt in PROMPT_EN, (code, prompt)
        sec = sections.setdefault(prompt, f"{TABLE}_{len(sections) + 1}")
        assert vlab[code] == expected_vl, (code, vlab[code])
        for resp, pl, en in options:
            rows.append({
                "table": TABLE, "section_id": sec, "item": code,
                "instrument": "Gaming Motivation Inventory (GMI), Polish version",
                "language": "Polish", "instructions": "",
                "section_prompt": prompt, "item_text": stem,
                "correct_response": "", "option_text": pl, "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": PROMPT_EN[prompt],
                "item_text_translated": EN[n], "option_text_translated": en,
            })
    assert list(sections.values()) == [f"{TABLE}_1", f"{TABLE}_2"]
    # sections are contiguous: 1-66 and 67-88
    first = {r["item"]: r["section_id"] for r in rows}
    assert all(first[f"GMI{n}"] == f"{TABLE}_{1 if n <= 66 else 2}" for n in range(1, 89))

    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    assert {r["item"] for r in rows} == set(resp["item"].astype(str))
    assert {float(r["resp"]) for r in rows} == set(resp["resp"].astype(float))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{TABLE}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{path.name}: {len(rows)} rows, 88 items, 7 options")


if __name__ == "__main__":
    main()
