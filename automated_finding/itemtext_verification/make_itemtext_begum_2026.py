#!/usr/bin/env python3
"""Item text for begum_2026_hama (Mendeley 10.17632/sg2whyws4h). English administration.

Cheap case: the deposit's "Codebook and Complete Survey Questionnaire.pdf" reproduces the 14
HAM-A items (Part-C) with the 0-4 anchors; the item codes HAM1..HAM14 are the deposit's own
column names, so the tie is the questionnaire's own numbering. ISI (begum_2026_isi) is not
built: the Insomnia Severity Index is a rights-register `block` row.
"""
import csv
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
TABLE = "begum_2026_hama"
INSTRUCTIONS = "Select one of the five responses for each of the fourteen questions."
OPTIONS = {0: "Not present", 1: "Mild", 2: "Moderate", 3: "Severe", 4: "Very severe"}
# transcribed from the deposit's codebook PDF, Part-C (line breaks joined)
ITEMS = {
    1: "Anxious mood (Worries, anticipation of the worst, fearful anticipation, irritability.)",
    2: "Tension (Feelings of tension, fatigability, startle response, moved to tears easily, trembling, feelings of restlessness, inability to relax.)",
    3: "Fears (Of dark, of strangers, of being left alone, of animals, of traffic, of crowds.)",
    4: "Insomnia (Difficulty in falling asleep, broken sleep, unsatisfying sleep and fatigue on waking, dreams, nightmares, night terrors)",
    5: "Intellectual (Difficulty in concentration, poor memory.)",
    6: "Depressed mood (Loss of interest, lack of pleasure in hobbies, depression, early waking, diurnal swing.)",
    7: "Somatic (muscular) (Pains and aches, twitching, stiffness, myoclonic jerks, grinding of teeth, unsteady voice, increased muscular tone.)",
    8: "Somatic (sensory) (Tinnitus, blurring of vision, hot and cold flushes, feelings of weakness, pricking sensation.)",
    9: "Cardiovascular symptoms (Tachycardia, palpitations, pain in chest, throbbing of vessels, fainting feelings, missing beat.)",
    10: "Respiratory symptoms (Pressure or constriction in chest, choking feelings, sighing, dyspnea.)",
    11: "Gastrointestinal symptoms (Difficulty in swallowing, wind abdominal pain, burning sensations, abdominal fullness, nausea, vomiting, borborygmi, looseness of bowels, loss of weight, constipation.)",
    12: "Genitourinary symptoms (Frequency of micturition, urgency of micturition, amenorrhea, menorrhagia, development of frigidity, premature ejaculation, loss of libido, impotence.)",
    13: "Autonomic symptoms (Dry mouth, flushing, pallor, tendency to sweat, giddiness, tension headache, raising of hair.)",
    14: "Behavior at interview (Fidgeting, restlessness or pacing, tremor of hands, furrowed brow, strained face, sighing or rapid respiration, facial pallor, swallowing, etc.)",
}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    resp = pd.read_csv(RESP_DIR / f"{TABLE}.csv")
    codes = {f"HAM{k}" for k in ITEMS}
    assert codes == set(resp["item"]), TABLE
    assert set(resp["resp"].unique()) <= set(OPTIONS), TABLE
    rows = []
    for k, text in ITEMS.items():
        for r, o in OPTIONS.items():
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": f"HAM{k}",
                         "instrument": "Hamilton Anxiety Rating Scale (HAM-A), self-rated",
                         "instructions": INSTRUCTIONS, "section_prompt": "", "item_text": text,
                         "correct_response": "", "option_text": o, "resp": r})
    p = OUT_DIR / f"{TABLE}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len(ITEMS)} items")


if __name__ == "__main__":
    main()
