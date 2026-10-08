#!/usr/bin/env python3
"""Item text for useche_2022_cbq and useche_2022_rprs (data/useche_2022_cbq.py).

Wording transcribed from the deposit's own "Appendix I - Root_Questionnaire_CBQ.pdf"
(Dataverse 10.7910/DVN/EP6QLN, file 7559246, the English researcher form), in bullet
order; anchors from the same PDF and "Appendix II - Codebook (CBQ-19).pdf" (7559247).
Item k of each section = the k-th bullet; the deposit's subscale-mean columns pin the
section boundaries (asserted in data/useche_2022_cbq.py). Source spelling kept as
printed, including F3 bullet 6, which the PDF prints without its leading "I".
"""
import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "itemtext_output"
LANG = ("English; Spanish; Portuguese; Finnish; Russian; Slovak; Dutch; Malay; "
        "Chinese; Danish; German; Polish; French")

F1 = ["Cycling under the influence of alcohol and/or other drugs or hallucinogens",
      "Riding against the traffic flow (wrong way)",
      "Zigzagging between (weaving in and out of) vehicles when using a mixed lane",
      "Handling potentially obstructive objects while riding a bicycle (food, packs, cigarettes ...)",
      "Feeling that I'm going at a higher speed than I should be going at",
      "Crossing what appears to be a clear crossing, even if the traffic light is red",
      "Carrying a passenger on my bicycle, without it being adapted for such a purpose",
      "Having a dispute in speed or 'race' with another cyclist or driver"]
F2 = ["Unintentionally crossing the street without looking properly, thus making another vehicle brake to avoid a crash",
      "Colliding (or being close to it) with a pedestrian or another cyclist while cycling distractedly",
      "Braking suddenly and being close to causing an accident",
      "Failing to notice the presence of pedestrians crossing when turning",
      "Not braking on a ‘Stop' sign and being close to colliding with another vehicle or pedestrian",
      "Braking very abruptly on a slippery surface",
      "While I am distracted, not realizing that a pedestrian intended to cross the street",
      "Not realising that a parked vehicle intends to leave and consequently having to brake abruptly to avoid a collision",
      "When riding on the left side, not realising that a passenger is getting out of a vehicle or bus, and thus being close to hitting them",
      "Trying to overtake a vehicle that had previously used its indicators to signal that it was going to turn, consequently having to brake",
      "Misjudging a turn and hitting something on the road, or being close to losing balance (or falling)",
      "Unintentionally hitting a parked vehicle",
      "Failing to be aware of the road conditions and falling over a bump, hole or obstacle",
      "Confusing one traffic signal with another, manoeuvring according to the latter",
      "Trying to brake but not being able to use the brakes properly due to a poor hand positioning"]
F3 = ["I stop and look at both sides before crossing a corner or intersection",
      "I try to move at a prudent speed to avoid sudden mishaps or braking",
      "I usually keep a safe distance from other cyclists or vehicles",
      "When I use the bike path (or bike-lane), I always use the indicated lane",
      "I avoid going out on my bike in adverse weather conditions",
      "avoid going out on my bike if I feel very tired or sick"]
RPRS = ["I readily recognise traffic signals",
        "I know the basic rules governing other types of vehicles",
        "I believe that pedestrians should always have priority, even over cyclists",
        "I easily identify areas prohibited to traffic or bicycle parking",
        "Overall, I know the bicycle safety regulations of my city/town",
        "I am aware of the potential consequences of being involved in a traffic accident, for example, with another vehicle",
        "I perceive potentially higher risks for my safety when I ride a bicycle, than when I am on a motorised vehicle",
        "I am always aware of the other vehicles that surround me on the road",
        "I realise that there are signalling and infrastructure problems that can affect my safety",
        "I believe that cycling under the influence of certain substances (alcohol, illegal and/or prescribed drugs) affects my ability to ride well",
        "I am aware of the risks involved in using headphones and mobile phones while I ride bicycle",
        "Riding in urban areas is especially risky, considering the number of vehicles and the complexity of the roads"]
FREQ = ["Never (at all)", "Almost never", "Sometimes", "Frequently", "Very Frequently"]
AGREE = ["Strongly disagree", "Disagree", "Neither agree nor disagree", "Agree",
         "Strongly agree"]
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp"]


def write(table, instrument, instructions, sections, options):
    rows, k = [], 0
    for sid, prompt, stems in sections:
        for stem in stems:
            k += 1
            item = f"{'CBQ' if table.endswith('cbq') else 'RPRS'}{k}"
            for r, opt in enumerate(options):
                rows.append([table, sid, item, instrument, LANG, instructions, prompt,
                             stem, "", opt, r])
    with open(OUT / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    print(table, len(rows), "rows,", k, "items")


write("useche_2022_cbq", "Cycling Behaviour Questionnaire (CBQ)", "", [
    ("useche_2022_cbq_f1", "Please estimate how often you do the following conventional risky behaviors:", F1),
    ("useche_2022_cbq_f2", "Please estimate how often you do the following risky behaviors, produced by errors:", F2),
    ("useche_2022_cbq_f3", "Please estimate how often you do the following protective behaviors:", F3),
], FREQ)
write("useche_2022_rprs", "Risk perception and rule knowledge (RPRS)",
      "Please indicate your level of agreement with the following statements, regarding your cycling experience.",
      [("useche_2022_rprs_1", "", RPRS)], AGREE)
