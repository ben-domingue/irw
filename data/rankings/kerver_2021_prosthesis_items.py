#!/usr/bin/env python3
##Top-10 ranking of prosthesis-use items by people with upper limb absence -> one IRW rankings table.
##Source: Kerver, N., van der Sluis, C. K., van Twillert, S. and Krabbe, P. F. M. "Towards assessing
##the preferred usage features of upper limb prostheses: most important items regarding prosthesis
##use in people with major unilateral upper limb absence - a Dutch national survey", Disability and
##Rehabilitation (doi 10.1080/09638288.2021.1988734). Data: DataverseNL doi:10.34894/OCZJAL,
##CC0 1.0. Files read: Dataset_HealthFan_survey.csv (358 rows, the top-10 selections) and
##Codebook_dataset_HealthFan_survey.pdf (the item labels, transcribed into ITEMS below).
##
##Each participant picked their 10 most important items out of the 79 in the HealthFan diagram and
##then ranked those ten from most to least important. The CSV holds one row per participant with
##First_factor .. Tenth_factor giving the ITEM NUMBER at each position, so the position is the
##column and the value is the item -- the mirror of the usual layout. Sentinel values are not rows:
##-999 missing factor (44 cells), -888 unclear factor (10), -666 more than ten factors selected and
##not ranked, or the survey not filled in as intended (80).
##
##The deposit's own `Fulfill_ranking` flag is 0 for six participants who selected ten items but did
##NOT rank them; the deposit then shows their factors "in random order", so those six are dropped
##rather than shipped as rankings (the count is in the design record). Eight more rows carry no
##usable cell at all. Two participants name the same item at two positions; those are kept as
##recorded (duplicate marks, README).
##
##Layout: id = the participant re-keyed 1..n in file order (the deposit's own Participant number is
##dropped), task = 1, item = the English label as the codebook prints it (the options are items of
##prosthesis use, not people, so the text is kept; the source's spellings "Life-like appaerance" and
##"Prussure of others" are left as printed), resp = the position, 1 = most important. The deposit
##carries no covariates: the depositors removed every personal detail because the Dutch population
##with upper limb absence is small, so there is nothing to put in cov_*.
##
##Usage: python3 kerver_2021_prosthesis_items.py build <raw dir> <out dir>
##Table: kerver_2021_prosthesis_items.
from __future__ import annotations

import csv
import sys
from pathlib import Path

from rank_common import design_counts, fetch, upsert_design, write_table

TABLE = "kerver_2021_prosthesis_items"
COLLECTION = "10.34894/OCZJAL"
DATA_URL = "https://dataverse.nl/api/access/datafile/195107"
POSITIONS = ["First_factor", "Second_factor", "Third_factor", "Fourth_factor", "Fifth_factor",
             "Sixth_factor", "Seventh_factor", "Eighth_factor", "Ninth_factor", "Tenth_factor"]
SENTINELS = {-999: "missing factor", -888: "unclear factor", -666: "not ranked or survey misused"}

##The 79 HealthFan items, English labels, from Codebook_dataset_HealthFan_survey.pdf.
ITEMS = {1: "Self-confidence", 2: "Independence", 3: "Self-image", 4: "Work/job", 5: "Water/dirt proof",
    6: "Prejudices of others", 7: "Information services", 8: "Modeling", 9: "Self-care",
    10: "Transporting the prosthesis", 11: "Transport", 12: "Catching",
    13: "Appearance in combination with clothing", 14: "Access to service", 15: "Time investment",
    16: "Household", 17: "Supporting body", 18: "Support from family/friends", 19: "Peer support",
    20: "Giving support to family/friends", 21: "Stabilize/support objects", 22: "Leisure activities",
    23: "Performing social role", 24: "Social interaction", 25: "Speed of movements", 26: "Body embarrassment",
    27: "Performing family role", 28: "Vulnerability/robustness", 29: "Religion", 30: "Reactions from public",
    31: "Prosthesis training", 32: "Advertisement", 33: "Professional prosthesis maintenance",
    34: "Procedure insurances", 35: "Prosthesis fit", 36: "Overuse complaints", 37: "Need for prosthesis",
    38: "Multi-tasking", 39: "Natural movements", 40: "Life-like appaerance", 41: "Durability", 42: "Cold",
    43: "Cost of prosthesis", 44: "Cost of maintenance", 45: "Putting clothes on", 46: "Feeling disabled",
    47: "Skin irritation", 48: "Heat/sweating", 49: "Size", 50: "Grabbing, picking up and holding", 51: "Weight",
    52: "Ease in cleaning", 53: "Ease of control", 54: "Noise", 55: "Usability", 56: "Functionality",
    57: "Dexterity", 58: "Phantom limb pain", 59: "Phantom limb sensation", 60: "Fitting in",
    61: "Self-maintenance", 62: "Own costs", 63: "Pushing/pulling", 64: "Prussure of others",
    65: "Wearing comfort", 66: "Expertise of guidance", 67: "Feeling comfortable", 68: "Embodiment",
    69: "Wrist control", 70: "Moving multiple joints", 71: "Elbow control", 72: "Reliability",
    73: "Physical effort needed to control", 74: "Mental effort needed to control",
    75: "Controlling electronic devices", 76: "Body balance", 77: "Autonomy", 78: "Anonymity",
    79: "Donning/doffing"}


def build(raw_dir: Path, out_dir: Path) -> None:
    src = fetch(DATA_URL, raw_dir / "Dataset_HealthFan_survey.csv")
    with open(src, newline="", encoding="utf-8-sig") as f:
        data = list(csv.DictReader(f))
    rows, unranked, no_marks, sentinel = [], 0, 0, {k: 0 for k in SENTINELS}
    for i, r in enumerate(data, start=1):
        if (r.get("Fulfill_ranking") or "").strip() == "0":
            unranked += 1
            continue
        marks = []
        for pos, col in enumerate(POSITIONS, start=1):
            v = (r.get(col) or "").strip()
            if not v:
                continue
            n = int(float(v))
            if n in sentinel:
                sentinel[n] += 1
                continue
            if n not in ITEMS:
                raise ValueError(f"unknown factor {n} in {col} of participant {r.get('Participant')}")
            marks.append({"id": i, "task": 1, "item": ITEMS[n], "resp": pos})
        if not marks:
            no_marks += 1
            continue
        rows.extend(marks)
    ##ids are re-keyed after the drops so they run 1..n with no gaps
    remap = {old: new for new, old in enumerate(dict.fromkeys(r["id"] for r in rows), start=1)}
    for r in rows:
        r["id"] = remap[r["id"]]
    write_table(out_dir / f"{TABLE}.csv", rows)
    counts = design_counts(rows)
    upsert_design({
        "table": TABLE, "source_file": "Dataset_HealthFan_survey.csv", "collection": COLLECTION,
        "jurisdiction": "Netherlands (national survey of people with major unilateral upper limb absence)",
        "date": "unknown",
        "office": ("the ten most important items regarding prosthesis use, chosen from the 79-item HealthFan "
                   "diagram and then ranked 1 (most important) to 10"),
        "method": "survey", "seats": "na", **counts,
        "n_ballots_cast": len(data), "n_ballots_eligible_est": len(data),
        "write_in_allowed": "no", "candidate_order": "unknown",
        "evidence": (f"DataverseNL {COLLECTION} file Dataset_HealthFan_survey.csv (id 195107), CC0 1.0; item "
                     f"labels from Codebook_dataset_HealthFan_survey.pdf (id 195108); paper Kerver et al., "
                     f"Disability and Rehabilitation, 10.1080/09638288.2021.1988734; date unknown (the deposit "
                     f"states no fielding date); seats na (a survey); {len(data)} participants in the file, "
                     f"{unranked} dropped for Fulfill_ranking = 0 (items selected but shown in random order, "
                     f"not ranked), {no_marks} with no usable cell; sentinel cells dropped: "
                     f"{ {SENTINELS[k]: v for k, v in sentinel.items()} }; "
                     f"{counts['n_duplicate_marks']} duplicate marks kept as recorded; n_candidates counts the "
                     f"distinct items that received a position, of 79 offered; candidate_order unknown (the "
                     f"diagram's layout is not recorded in the deposit); counts computed by "
                     f"kerver_2021_prosthesis_items.py"),
    })
    print(f"{TABLE}: {len(rows)} rows, {counts['n_ballots_with_marks']} participants, "
          f"{counts['n_candidates']} items used, {unranked} unranked dropped, {no_marks} empty, "
          f"sentinels {sentinel}, {counts['n_duplicate_marks']} duplicate marks")


def main(argv: list[str]) -> int:
    if len(argv) < 4 or argv[1] != "build":
        print("usage: kerver_2021_prosthesis_items.py build <raw dir> <out dir>")
        return 2
    build(Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
