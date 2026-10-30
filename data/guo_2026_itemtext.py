#!/usr/bin/env python3
# Item text for the guo_2026_adv_* tables (see
# guo_2026_adventure_sports_tourism.py for the response tables).
#
# Source wording, both CC BY 4.0 Supporting Information of
# 10.1371/journal.pone.0339943:
#   S1 File "Adventure Motivation Scale" -- all 24 motivation items, printed
#     under their subscale headings in the deposit's column order.
#   S3 File "Item-by-item rationale for the adapted empowerment scale" -- a
#     three-column table giving Boley & McGehee's (2014) ORIGINAL RETS wording,
#     this study's ADAPTED wording, and the rationale.
#
# ONLY THE ADAPTED COLUMN OF S3 IS TRANSCRIBED. The original RETS wording in
# the left-hand column is third-party text reproduced for comparison; it is
# not what these 566 women answered and it is not ours to redistribute. The
# adapted wording is the authors' own, published under their own CC BY licence
# and administered in this study, so it ships.
#
# NINE OF THE ELEVEN TABLES GET ITEM TEXT. Risk perception (6 items) and
# participation intention (3) have no published wording in the article or any
# of its eight supporting files, so those two tables are not covered here.
# That is an availability gap, not a rights one -- nothing is invented.
#
# THE MIDDLE OF THE RESPONSE SCALE IS DELIBERATELY BLANK. The paper labels the
# anchors only -- "1 (strongly disagree) to 5 (strongly agree)" -- and never
# prints wording for 2, 3 or 4. All five response values still get a row,
# because the validator requires the item-text resp set to match the response
# table's exactly, but option_text is empty for the three unlabelled points
# rather than filled with a guessed "Disagree / Neutral / Agree".
#
# The items were administered in Chinese to a Chinese sample; the supporting
# files publish them in English only, so the English is what ships.

import csv
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "automated_finding", "itemtext_output")

MOTIV_INSTR = (
    "Why do you participate in adventure sports tourism? Please indicate how "
    "much each of the following reasons corresponds to one of the reasons for "
    "which you participate.")
EMPOW_INSTR = (
    "Please indicate how strongly you agree or disagree with each of the "
    "following statements about adventure sports tourism.")

MOTIV = "Adventure Motivation Scale (adapted from the Sport Motivation Scale)"
EMPOW = ("Resident Empowerment through Tourism Scale (Boley & McGehee, 2014), "
         "adapted for female adventure sports tourists")

# table -> (instrument, instructions, section_prompt, [(item_code, text), ...])
BLOCKS = {
    "guo_2026_adv_motiv_to_know": (MOTIV, MOTIV_INSTR,
     "Intrinsic motivation - to know", [
        ("IM_to_know_1", "For the pleasure of knowing more about this adventure sports tourism activity."),
        ("IM_to_know_2", "For the pleasure of discovering new training techniques for this activity."),
        ("IM_to_know_3", "For the pleasure of learning training techniques I have never tried before."),
        ("IM_to_know_4", "For the pleasure of discovering new strategies and tactics in this activity."),
     ]),
    "guo_2026_adv_motiv_accomplishment": (MOTIV, MOTIV_INSTR,
     "Intrinsic motivation - accomplishment", [
        ("IM_accomplishment_1", "For the satisfaction I experience while mastering difficult training techniques."),
        ("IM_accomplishment_2", "For the pleasure I feel while improving my weak points in this activity."),
        ("IM_accomplishment_3", "For the satisfaction I get from improving my abilities."),
        ("IM_accomplishment_4", "For the pleasure I feel when executing high-difficulty movements."),
     ]),
    "guo_2026_adv_motiv_stimulation": (MOTIV, MOTIV_INSTR,
     "Intrinsic motivation - experience stimulation", [
        ("IM_stimulation_1", "For the excitement and stimulation I feel while participating."),
        ("IM_stimulation_2", "For the excitement I feel when I am deeply involved in the activity."),
        ("IM_stimulation_3", "For the intense emotional experiences I have while doing this activity."),
        ("IM_stimulation_4", "For the feeling of being totally immersed in the activity."),
     ]),
    "guo_2026_adv_motiv_identified_reg": (MOTIV, MOTIV_INSTR,
     "Extrinsic motivation - identified regulation", [
        ("EM_identified_regulation_1", "For the things I learn in this activity that are useful in other areas of my life."),
        ("EM_identified_regulation_2", "To maintain a healthy body through participation."),
        ("EM_identified_regulation_3", "For the benefits this activity contributes to my personal development."),
        ("EM_identified_regulation_4", "To gain the health benefits that are valued by those around me."),
     ]),
    "guo_2026_adv_motiv_introjected_reg": (MOTIV, MOTIV_INSTR,
     "Extrinsic motivation - introjected regulation", [
        ("EM_introjected_regulation_1", "To feel good about myself when I engage in this activity."),
        ("EM_introjected_regulation_2", "I would feel bad if I did not spend time doing this activity."),
        ("EM_introjected_regulation_3", "I would feel uncomfortable if I could not participate regularly."),
        ("EM_introjected_regulation_4", "To show others that I am excellent at this activity."),
     ]),
    "guo_2026_adv_motiv_external_reg": (MOTIV, MOTIV_INSTR,
     "Extrinsic motivation - external regulation", [
        ("EM_external_regulation_1", "To maintain good relationships with friends through this activity."),
        ("EM_external_regulation_2", "To gain recognition from people I know."),
        ("EM_external_regulation_3", "To use this activity as a way to interact with others."),
        ("EM_external_regulation_4", "To gain glory or other rewards I desire."),
     ]),
    "guo_2026_adv_psych_empowerment": (EMPOW, EMPOW_INSTR,
     "Psychological empowerment", [
        ("Psychological_empowerment_1", "Adventure sports tourism makes me proud to be a female adventure sports participant."),
        ("Psychological_empowerment_2", "Adventure sports tourism makes me feel special because I can accomplish things many think women cannot do."),
        ("Psychological_empowerment_3", "Adventure sports tourism makes me want to recommend this destination to others."),
        ("Psychological_empowerment_4", "Adventure sports tourism reminds me that I have a unique story to share with others."),
        ("Psychological_empowerment_5", "Adventure sports tourism makes me want to work to keep my identity in this sport strong."),
     ]),
    "guo_2026_adv_social_empowerment": (EMPOW, EMPOW_INSTR,
     "Social empowerment", [
        ("Social_empowerment_1", "Adventure sports tourism makes me feel more connected to my community of female adventurers."),
        ("Social_empowerment_2", "Adventure sports tourism fosters a sense of 'community spirit' among female participants within me."),
        ("Social_empowerment_3", "Adventure sports tourism provides ways for me to get involved in the female adventure community."),
     ]),
    "guo_2026_adv_political_empowerment": (EMPOW, EMPOW_INSTR,
     "Political empowerment", [
        ("Political_empowerment_1", "I feel like I have a voice in the adventure sports tourism community."),
        ("Political_empowerment_2", "I feel like I have access to the decision making process when it comes to women's participation in adventure."),
        ("Political_empowerment_3", "I feel like my actions make a difference in how female adventure tourism is viewed in society."),
        ("Political_empowerment_4", "I feel like I have an outlet to share my concerns about women's true needs in adventure sports tourism."),
     ]),
}

# the paper labels the two anchors and nothing in between -- see the header
OPTIONS = [(1, "Strongly disagree"), (2, ""), (3, ""), (4, ""),
           (5, "Strongly agree")]

COLS = ["table", "section_id", "item", "instrument", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text",
        "resp"]


def build():
    os.makedirs(OUT, exist_ok=True)
    n_items = 0
    for table, (instrument, instructions, prompt, items) in BLOCKS.items():
        section = table + "_1"
        rows = []
        for code, text in items:
            for resp, label in OPTIONS:
                rows.append({"table": table, "section_id": section,
                             "item": code, "instrument": instrument,
                             "instructions": instructions,
                             "section_prompt": prompt, "item_text": text,
                             "correct_response": "", "option_text": label,
                             "resp": resp})
        assert len(rows) == len(items) * len(OPTIONS)
        path = os.path.join(OUT, table + "__items.csv")
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        n_items += len(items)
        print(f"{table}__items.csv: {len(items)} items, {len(rows)} rows")
    assert n_items == 36, n_items
    print(f"{len(BLOCKS)} item-text tables, {n_items} items "
          f"(risk perception and participation intention have no published "
          f"wording and are not covered)")


if __name__ == "__main__":
    build()
