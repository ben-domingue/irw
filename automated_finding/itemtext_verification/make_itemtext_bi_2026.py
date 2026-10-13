#!/usr/bin/env python3
"""Item text for the four bi_2026_* tables (Zenodo 10.5281/zenodo.22040756). Chinese
administration (preservice teachers, single Chinese institution).

Cheap case: the deposit's Data_Dictionary sheet gives each Q-code's Chinese wording;
data/bi_2026_preservice_teachers_ai.py exposes stems() -> {Q-code: stem} and BLOCKS, so the
item code is the deposit's own variable name. The sheet gives no option labels beyond "1-5
Likert response", so option_text is blank on every scale point. English in item_text_translated is an IRW
translation.
"""
import csv
import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "bi_2026_preservice_teachers_ai.py"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
EN = {
    "Q7": "I can clearly distinguish which educational software genuinely uses AI technology.",
    "Q8": "I broadly understand the core concepts behind common AI teaching tools (such as machine learning or prompts).",
    "Q9": "I know the limits of what AI can do in education, and what it is and is not good at.",
    "Q10": "I understand that AI-generated content is based on data computation rather than genuine human-like understanding of knowledge.",
    "Q11": "I can skilfully use AI tools to help with lesson-preparation tasks such as writing lesson plans and making courseware.",
    "Q12": "Using AI tools appropriately can significantly improve the efficiency of my lesson preparation and instructional design.",
    "Q13": "When AI output is unsatisfactory, I can flexibly adjust the prompt to obtain accurate content.",
    "Q14": "I can select and combine the content best suited to my teaching objectives from the variety of lesson-preparation material AI provides.",
    "Q15": "I can accurately evaluate the strengths and weaknesses of a given AI teaching tool for a specific subject.",
    "Q16": "I can choose suitable AI tools to support teaching according to the teaching task.",
    "Q17": "Before using AI-generated content, I carefully verify its accuracy to guard against factual errors.",
    "Q18": "When using AI to support teaching, I always strictly observe academic integrity and educational ethics.",
    "Q19": "When letting AI process student data (such as grades or assignments), I am highly alert to the risk of privacy leaks.",
    "Q20": "I am always alert to the misuse of AI in education (such as relying entirely on AI to write lesson plans).",
    "Q21": "I check whether AI-generated teaching material carries bias or stereotypes, so as not to mislead students.",
    "Q22": "Even when AI has been deeply involved in lesson preparation, I am clear that the final responsibility for teaching lies with the teacher.",
    "Q23": "I believe AI-generated instructional designs are reliable in their logic and knowledge structure.",
    "Q24": "For routine lesson-preparation tasks, I feel AI is an assistant I can rely on.",
    "Q25": "When AI output seems somewhat perfunctory or inaccurate, I become wary of it.",
    "Q26": "I always doubt whether AI-generated examples might contain hidden bias or misleading guidance.",
    "Q27": "Even if a lesson plan makes heavy use of AI-generated material, I still feel I am the true author of the instructional design.",
    "Q28": "Throughout the process of preparing lessons with AI, I feel I remain fully in control of the direction of the teaching ideas.",
    "Q29": "When using AI to generate teaching plans, I feel the final educational decision-making power remains firmly in my own hands.",
    "Q30": "I can actively guide AI to produce content that fits my personal teaching style, rather than passively accepting its defaults.",
    "Q31": "When AI's suggestions conflict with my educational beliefs, I can decisively discard them without being swayed by its technical authority.",
    "Q32": "I use AI to tailor different learning materials for students of different levels (for example, generating accessible stories for struggling students and extension problems for advanced students).",
    "Q33": "I often draw on AI's creativity to design novel classroom activities (such as role play or situational puzzles), breaking the traditional pattern of the teacher talking and students listening.",
    "Q34": "In the teaching plans I design, I boldly let students interact directly with AI (for example, asking AI questions or simulating dialogue) to help them understand complex knowledge.",
    "Q35": "I not only use AI to innovate assignment formats, but also use it to help analyse students' response data and provide immediate, targeted evaluative feedback.",
    "Q36": "When an AI-assisted system or tool reports that students have knowledge gaps, I can flexibly and immediately adjust my subsequent instructional design or teaching focus based on that information.",
}


def main():
    spec = importlib.util.spec_from_file_location("bi", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zh = mod.stems()
    for suffix, (nums, instrument) in mod.BLOCKS.items():
        table = f"bi_2026_{suffix}"
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        codes = [f"Q{k}" for k in nums]
        assert set(codes) == set(resp["item"]), table
        rows = []
        assert set(resp["resp"].unique()) <= set(range(1, 6)), table
        for code in codes:
            for r in range(1, 6):  # one row per scale point; anchors not in the sheet, option_text blank
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                             "language": "Chinese", "instructions": "", "section_prompt": "", "item_text": zh[code],
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
