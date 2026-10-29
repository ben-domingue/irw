"""
Item text for kubilay_2023_scam_identification and kubilay_2023_scam_confidence.

Source: Kubilay, E., Raiber, E., Spantig, L., Cahlíková, J., & Kaaria, L.
        (2023). Can you spot a scam? Measuring and improving scam
        identification ability. Journal of Development Economics, 165, 103147.
        DOI 10.1016/j.jdeveco.2023.103147
Data:   https://doi.org/10.7910/DVN/HUYYQZ (CC0 1.0)

`item_text` is BLANK BY DESIGN. The twelve stimuli are phone screenshots --
"Vignettes kept the original wording of the screenshots and were visually
harmonized, i.e., all vignettes were displayed on the same phone with the same
signal strength, battery level, etc." (appendix Table A1 notes; Figure A1 is an
example image). The source publishes no wording for them, and the item codes
denote stable stimuli because the two blocks are fixed sets, so this is the
picture-stimulus case ruled on 2026-09-05: ship the table, leave `item_text`
blank, carry what the source does publish.

What the source does publish, and what this ships:
  * `option_text` -- from the deposit's own codebook
    (online_survey_labeled_codebook.xlsx): 1 = Scam, 2 = No scam for the
    classification, and the five confidence anchors.
  * `correct_response` -- from the article's appendix Table A1, "Overview of
    vignettes", whose `Intention` column marks each of the twelve as Genuine or
    Fraudulent: two genuine and four fraudulent per block. The correct answer to
    "is this a scam?" is therefore 1 (Scam) for a fraudulent message and 2 (No
    scam) for a genuine one. This is a fact about the stimuli, not expressive
    text copied from the article.

The one thing that had to be established rather than read off: Table A1 lists
six rows per block but does not name them M1..M6, so tying its rows to the
source columns is positional. verify_kubilay_2023_scam_identification.R is the
falsifiable check -- the two genuine messages in each block must be the two with
the lowest share of "Scam" answers, and they are, by a wide margin and in both
blocks independently. That pins exactly the Genuine/Fraudulent split, which is
exactly what `correct_response` claims; nothing finer is shipped, so nothing
finer needs pinning.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

OUT = Path(sys.argv[1])

FIELDS = ["table", "section_id", "item", "instrument", "instructions",
          "section_prompt", "item_text", "correct_response", "option_text",
          "resp"]

INSTRUMENT = ("Scam Identification Ability (SIA) measure, Kubilay, Raiber, "
              "Spantig, Cahlíková & Kaaria 2023 -- twelve phone-message "
              "vignettes in two fixed blocks of four scams and two genuine "
              "messages each")

# Appendix Table A1, in the order the table prints them, which
# verify_kubilay_2023_scam_identification.R ties to M1..M6 within each block.
INTENTION = {
    "sia_a_m1": "Genuine", "sia_a_m2": "Genuine",
    "sia_a_m3": "Fraudulent", "sia_a_m4": "Fraudulent",
    "sia_a_m5": "Fraudulent", "sia_a_m6": "Fraudulent",
    "sia_b_m1": "Genuine", "sia_b_m2": "Genuine",
    "sia_b_m3": "Fraudulent", "sia_b_m4": "Fraudulent",
    "sia_b_m5": "Fraudulent", "sia_b_m6": "Fraudulent",
}

ANSWER_OPTIONS = {1: "Scam", 2: "No scam"}
CONFIDENCE_OPTIONS = {1: "Not confident at all", 2: "A little confident",
                      3: "Moderately confident", 4: "Confident",
                      5: "Very confident"}


def rows(table: str, options: dict, with_key: bool) -> list:
    out = []
    for item, intention in INTENTION.items():
        key = ""
        if with_key:
            key = 1 if intention == "Fraudulent" else 2
        for resp, text in options.items():
            out.append({
                "table": table,
                "section_id": f"{table}_1",
                "item": item,
                "instrument": INSTRUMENT,
                "instructions": "",
                "section_prompt": "",
                "item_text": "",
                "correct_response": key,
                "option_text": text,
                "resp": resp,
            })
    return out


def write(table: str, data: list) -> None:
    path = OUT / f"{table}__items.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(data)
    print(f"{path}: {len(data)} rows")


def main() -> None:
    assert len(INTENTION) == 12
    assert sum(v == "Genuine" for v in INTENTION.values()) == 4
    write("kubilay_2023_scam_identification",
          rows("kubilay_2023_scam_identification", ANSWER_OPTIONS, True))
    write("kubilay_2023_scam_confidence",
          rows("kubilay_2023_scam_confidence", CONFIDENCE_OPTIONS, False))


if __name__ == "__main__":
    main()
