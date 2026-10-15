#!/usr/bin/env python3
"""Item text for chen_2026_technostress, chen_2026_pos and chen_2026_dt_intention (figshare
10.6084/m9.figshare.31968699). Chinese administration.

Cheap case: data/chen_2026_technostress_burnout.py stems() reads the .sav variable labels (Chinese
stems, block-title prefix stripped from item 1) and the value labels (seven anchors); the item code is
the deposit's own column name. The UWES-9 and BAT-12 blocks ship no item text (rights register).
English in *_translated is an IRW translation.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("chen_2026_technostress_burnout")
INSTR = {"chen_2026_technostress": "技术压力", "chen_2026_pos": "组织支持感", "chen_2026_dt_intention": "数字教材使用意愿"}
INSTR_EN = {"chen_2026_technostress": "Technostress", "chen_2026_pos": "Perceived organisational support",
            "chen_2026_dt_intention": "Digital textbook use intention"}
OPT_EN = {"非常不同意": "Strongly disagree", "不同意": "Disagree", "略微不同意": "Slightly disagree", "一般": "Neutral",
          "略微同意": "Slightly agree", "同意": "Agree", "非常同意": "Strongly agree"}
EN = {
    "Q8_Row1": "Digital textbooks force me to work faster.",
    "Q8_Row2": "Digital textbooks make me take on a workload beyond my capacity.",
    "Q8_Row3": "Digital textbooks force me to finish work within very tight time frames.",
    "Q8_Row4": "Because of digital textbooks, I spend less time with my family.",
    "Q8_Row5": "Even during holidays, I have to deal with work matters at any time.",
    "Q8_Row6": "To keep up with technological developments, I have to sacrifice holidays and weekends.",
    "Q8_Row7": "I find it hard to make time to learn and improve my technical skills.",
    "Q8_Row8": "I find that newly hired staff are more proficient in computer technology than I am.",
    "Q8_Row9": "I often feel that new technology is too complex to understand and apply.",
    "Q8_Row10": "New technology makes me constantly worry about my job security.",
    "Q8_Row11": "Compared with colleagues who have newer technical skills, I feel threatened.",
    "Q8_Row12": "To avoid being replaced, knowledge sharing among colleagues has clearly decreased.",
    "Q8_Row13": "The technology we use keeps seeing new developments.",
    "Q8_Row14": "The computer software in my organisation changes frequently.",
    "Q8_Row15": "The computer network in my organisation is constantly upgraded.",
    "Q9_Row1": "My organisation values my opinions.",
    "Q9_Row2": "My organisation really cares about my well-being.",
    "Q9_Row3": "My organisation strongly values my goals and values.",
    "Q9_Row4": "When I have a problem, my organisation provides help.",
    "Q9_Row5": "If I make an honest mistake, my organisation understands and forgives me.",
    "Q9_Row6": "My organisation does not take advantage of me.",
    "Q9_Row7": "My organisation pays attention to my needs.",
    "Q9_Row8": "If I need special help, my organisation is willing to assist me.",
    "Q12_Row1": "I intend to keep using digital textbooks in my future teaching.",
    "Q12_Row2": "Whenever conditions allow, I will try to use digital textbooks in my teaching.",
    "Q12_Row3": "I plan to use digital textbooks continuously and frequently in my teaching.",
}


def main():
    stems = mod.stems()
    for table in INSTR:
        rows = []
        for code, stem, vl in stems[table]:
            for r in sorted(vl):
                rows.append(row(table, f"{table}_1", code, INSTR[table], "Chinese", r, stem, option_text=vl[r],
                                item_text_tr=EN[code], option_text_tr=OPT_EN[vl[r]]))
        write(table, rows)


if __name__ == "__main__":
    main()
