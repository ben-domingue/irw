#!/usr/bin/env python3
"""Item text for the four makkiyah_2023_* tables (Zenodo 10.5281/zenodo.8406719).
Indonesian medical students, administered in Indonesian: the deposit's column headers are
the Indonesian statements, so they go in item_text verbatim (leading item number removed);
the *_translated columns are IRW's own English rendering (translation_source =
machine_translation in the provenance note; owes an itemtext_issues.qmd entry). The
anchors are not in the file, so option_text is blank for every scale point.

Cheap case: data/makkiyah_2023_medical_students.py assigns item codes <block>_<k> in
header order and exposes the exact (code, header) pairs via stems(), imported here.
"""
import csv
import importlib.util
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "makkiyah_2023_medical_students.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "section_prompt_translated", "item_text",
        "item_text_translated", "correct_response", "option_text", "option_text_translated", "resp"]
META = {"srl": ("makkiyah_2023_srl", "Self-regulated learning scale (MSLQ learning-strategies items, 50 items)", range(1, 6)),
        "mot": ("makkiyah_2023_motivation", "Learning motivation scale (MSLQ motivation items, 18 items)", range(1, 6)),
        "gse": ("makkiyah_2023_gse", "General Self-Efficacy Scale (10 items)", range(1, 5)),
        "eq": ("makkiyah_2023_eq", "Emotional intelligence scale (WLEIS, 16 items)", range(1, 6))}
EN = {
 "srl_1": "When I study the readings for this course, I outline the material to help me organize my thoughts.",
 "srl_2": "During class time I often miss important points because I'm thinking of other things.",
 "srl_3": "When studying for this course, I often try to explain the material to a classmate or friend.",
 "srl_4": "I usually study in a place where I can concentrate on my course work.",
 "srl_5": "When reading for this course, I make up questions to help focus my reading.",
 "srl_6": "I often feel so lazy or bored when I study for this class that I quit before I finish what I planned to do.",
 "srl_7": "I often find myself questioning things I hear or read in this course to decide if I find them convincing.",
 "srl_8": "When I study for this class, I practice saying the material to myself over and over.",
 "srl_9": "Even if I have trouble learning the material in this class, I try to do the work on my own, without help from anyone.",
 "srl_10": "When I become confused about something I'm reading for this class, I go back and try to figure it out.",
 "srl_11": "When I study for this course, I go through the readings and my class notes and try to find the most important ideas.",
 "srl_12": "I make good use of my study time for this course.",
 "srl_13": "If course readings are difficult to understand, I change the way I read the material.",
 "srl_14": "I try to work with other students from this class to complete the course assignments.",
 "srl_15": "When studying for this class, I read my class notes and the course readings over and over again.",
 "srl_16": "When a theory, interpretation, or conclusion is presented in class or in the readings, I try to decide if there is good supporting evidence.",
 "srl_17": "I work hard to do well in this class even if I don't like what we are doing.",
 "srl_18": "I make simple charts, diagrams, or tables to help me organize course material.",
 "srl_19": "When studying for this course, I often set aside time to discuss course material with a group of students from the class.",
 "srl_20": "I treat the course material as a starting point and try to develop my own ideas about it.",
 "srl_21": "I find it hard to stick to a study schedule.",
 "srl_22": "When I study for this class, I pull together information from different sources, such as lectures, readings, and discussions.",
 "srl_23": "Before I study new course material thoroughly, I often skim it to see how it is organized.",
 "srl_24": "I ask myself questions to make sure I understand the material I have been studying in this class.",
 "srl_25": "I try to change the way I study in order to fit the course requirements and the instructor's teaching style.",
 "srl_26": "I often find that I have been reading for class but don't know what it was all about.",
 "srl_27": "I ask the instructor to clarify concepts I don't understand well.",
 "srl_28": "I memorize key words to remind me of important concepts in this class.",
 "srl_29": "When course work is difficult, I give up or only study the easy parts.",
 "srl_30": "I try to think through a topic and decide what I am supposed to learn from it rather than just reading it over when studying.",
 "srl_31": "I try to relate ideas in this subject to those in other courses whenever possible.",
 "srl_32": "When I study for this course, I go over my class notes and make an outline of important concepts.",
 "srl_33": "When reading for this class, I try to relate the material to what I already know.",
 "srl_34": "I have a regular place set aside for studying.",
 "srl_35": "I try to play around with ideas of my own related to what I am learning in this course.",
 "srl_36": "When I study for this course, I write brief summaries of the main ideas from the readings and the concepts from the lectures.",
 "srl_37": "When I can't understand the material in this course, I ask another student in this class for help.",
 "srl_38": "I try to understand the material in this class by making connections between the readings and the concepts from the lectures.",
 "srl_39": "I make sure I keep up with the weekly readings and assignments for this course.",
 "srl_40": "Whenever I read or hear an assertion or conclusion in this class, I think about possible alternatives.",
 "srl_41": "I make lists of important terms for this course and memorize the lists.",
 "srl_42": "I attend class regularly.",
 "srl_43": "Even when course materials are dull and uninteresting, I manage to keep working until I finish.",
 "srl_44": "I try to identify students in this class whom I can ask for help if necessary.",
 "srl_45": "When studying for this course I try to determine which concepts I don't understand well.",
 "srl_46": "I often find that I don't spend very much time on this course because of other activities.",
 "srl_47": "When I study for this class, I set goals for myself in order to direct my activities in each study period.",
 "srl_48": "If I get confused taking notes in class, I make sure I sort it out afterwards.",
 "srl_49": "I rarely find time to review my notes or readings before an exam.",
 "srl_50": "I try to apply ideas from course readings in other class activities such as lecture and discussion.",
 "mot_1": "In a class like this, I prefer course material that really challenges me so I can learn new things.",
 "mot_2": "If I study in appropriate ways, then I will be able to learn the material in the medical course.",
 "mot_3": "I think I will be able to use what I learn in this course in other courses.",
 "mot_4": "Getting a good grade in this class is the most satisfying thing for me right now.",
 "mot_5": "It is my own fault if I don't learn the material in the medical course.",
 "mot_6": "It is important for me to learn the course material in this class.",
 "mot_7": "The most important thing for me right now is improving my overall grade point average, so my main concern in this class is getting a good grade.",
 "mot_8": "If I can, I want to get better grades in this class than most of the other students.",
 "mot_9": "In a class like this, I prefer course material that arouses my curiosity, even if it is difficult to learn.",
 "mot_10": "I am very interested in the content area of the medical course.",
 "mot_11": "If I try hard enough, then I will understand the course material.",
 "mot_12": "The most satisfying thing for me in the medical course is trying to understand the content as thoroughly as possible.",
 "mot_13": "I think the course material in this class is useful for me to learn.",
 "mot_14": "When I have the opportunity in this class, I choose course assignments that I can learn from even if they don't guarantee a good grade.",
 "mot_15": "If I don't understand the course material, it is because I didn't try hard enough.",
 "mot_16": "I like the subject matter of the medical course.",
 "mot_17": "Understanding the subject matter of the medical course is very important to me.",
 "mot_18": "I want to do well in this class because it is important to show my ability to my family, friends, employer, or others.",
 "gse_1": "I can always manage to solve difficult problems if I try hard enough.",
 "gse_2": "If someone opposes me, I can understand that and find the means and ways to deal with it.",
 "gse_3": "It is easy for me to stick to my aims and accomplish my goals.",
 "gse_4": "I am confident that I could deal efficiently with unexpected events.",
 "gse_5": "Thanks to my resourcefulness, I can handle situations that have not yet occurred.",
 "gse_6": "I can solve most problems if I invest the necessary effort.",
 "gse_7": "I can remain calm when facing difficulties because I trust my abilities.",
 "gse_8": "When I am confronted with a problem, I can find several solutions.",
 "gse_9": "If I am in trouble, I can usually think of a solution.",
 "gse_10": "I can usually handle whatever comes my way.",
 "eq_1": "I have a good sense of why I have certain feelings most of the time.",
 "eq_2": "I have a good understanding of my own emotions.",
 "eq_3": "I really understand what I feel.",
 "eq_4": "I always know whether or not I am happy.",
 "eq_5": "I always know my friends' emotions from their behaviour.",
 "eq_6": "I am a good observer of others' emotions.",
 "eq_7": "I am sensitive to the feelings and emotions of others.",
 "eq_8": "I have a good understanding of the emotions of people around me.",
 "eq_9": "I always set goals for myself and then try my best to achieve them.",
 "eq_10": "I always tell myself I am a competent person.",
 "eq_11": "I am a self-motivated person.",
 "eq_12": "I would always encourage myself to try my best.",
 "eq_13": "I am able to control my temper so that I can handle difficulties rationally.",
 "eq_14": "I am quite capable of controlling my own emotions.",
 "eq_15": "I can always calm down quickly when I am very angry.",
 "eq_16": "I have good control of my own emotions.",
}


def main():
    spec = importlib.util.spec_from_file_location("makkiyah", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for block, (table, instrument, valid) in META.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        pairs = mod.stems(block)
        assert {c for c, _ in pairs} == set(resp["item"]) and set(resp["resp"]) <= set(valid), table
        rows = []
        for code, header in pairs:
            stem = re.sub(r"^\d+[.,]\s*", "", header).strip()
            for r in valid:
                rows.append({"table": table, "section_id": f"{table}_1", "item": code,
                             "instrument": instrument, "language": "Indonesian", "instructions": "",
                             "instructions_translated": "", "section_prompt": "",
                             "section_prompt_translated": "", "item_text": stem,
                             "item_text_translated": EN[code], "correct_response": "",
                             "option_text": "", "option_text_translated": "", "resp": r})
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows, {len(pairs)} items")


if __name__ == "__main__":
    main()
