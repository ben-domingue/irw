#!/usr/bin/env python3
"""Item text for sakal_2026_ai_resistance (Zenodo 22644543). Turkish stems from the deposited
CODEBOOK_*.txt, keyed by variable name. The codebook gives the anchors in English only (1 = Strongly
Disagree .. 5 = Strongly Agree); the Turkish anchor wording is not in the deposit, so option_text is
left blank and the English goes in option_text_translated. Turkish administration; English stems are
IRW's translations.
"""
from _itemtext_writer_c import load_script, row, write

mod = load_script("sakal_2026_ai_resistance")
ANCH = {1: "Strongly Disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly Agree"}
EN = {"BDS_01": "I worry that artificial intelligence will take control of my working life.",
      "BDS_02": "The idea of working with AI tools causes me stress.",
      "BDS_03": "Being required to work with AI is emotionally demanding for me.",
      "BDS_04": "The development of AI increases my risk of losing my job.",
      "BDS_05": "I feel the need to defend myself against AI technologies.",
      "BDS_06": "My first reaction to AI technologies is usually negative.",
      "BDS_07": "I have difficulty understanding how AI systems work.",
      "BDS_09": "I do not have enough knowledge about AI technologies.",
      "BDS_10": "I do not believe AI technologies will benefit my work.",
      "KDS_13": "Our organizational structure slows the adoption of AI technologies.",
      "KDS_14": "Bureaucracy in decision-making processes makes integrating AI technologies difficult.",
      "KDS_15": "Our current work processes are not suited to AI technologies.",
      "KDS_17": "Our organization's current technological infrastructure does not accommodate AI systems.",
      "KDS_18": "Our outdated technological infrastructure prevents our transition to AI systems.",
      "KDS_19": "We do not have a sufficient budget to invest in AI technologies.",
      "KDS_20": "The lack of staff with AI expertise delays projects.",
      "KDS_21": "I feel I am not adequately informed about our AI projects and their effects.",
      "KDS_22": "Lack of communication in planning and implementing AI projects is a major problem.",
      "KDS_23": "Our leaders do not give enough support to AI projects.",
      "KDS_24": "AI investments seem inconsistent with our organization's overall strategy.",
      "KDS_25": "The current culture in our organization resists AI technologies.",
      "KDS_28": "Employees' ideas and concerns are not taken into account in AI projects.",
      "KBL_41": "Thanks to AI taking over my routine tasks, I will be able to focus on more strategic tasks.",
      "KBL_42": "I think using AI tools will contribute to my career development.",
      "KBL_43": "I trust that AI technologies will improve and simplify our work processes.",
      "KBL_44": "I am willing to continuously develop myself in AI technologies.",
      "KBL_45": "The development of AI will create new opportunities in my career."}


def main():
    stems = mod.stems()
    assert set(stems) == set(EN)
    table = "sakal_2026_ai_resistance"
    rows = [row(table, f"{table}_1", c, "AI Workplace Resistance Scale, 27 items (IRS / ORS / APB)", "Turkish", r, stems[c],
                option_text="", item_text_tr=EN[c], option_text_tr=ANCH[r]) for c in stems for r in ANCH]
    write(table, rows)


if __name__ == "__main__":
    main()
