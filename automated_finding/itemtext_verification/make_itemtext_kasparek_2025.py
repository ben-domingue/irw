#!/usr/bin/env python3
"""Item text for kasparek_2025_{phq8,gad7,bhs,bpaq,jvq} (data/kasparek_2025_violence_psychopathology.py).

Source: KasparekEtAl_2025_SEESAW_DataDescriptions.xlsx (Harvard Dataverse 10.7910/DVN/CCMJTJ,
file 12014415). Its "Question" column gives, per data column, the survey's question text as
"<shared stem> - <item>" (Qualtrics matrix export); "Levels" gives the response labels on the
first item of each block. Item codes are the data columns themselves, so the codebook ties
code to text directly (no positional inference).

kasparek_2025_audit is NOT built: AUDIT is ship_with_note in the rights register and an
earlier batch (herreromontes_2022_audit) held its text pending a ruling.
"""
import csv
import io
import re
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parent.parent / "itemtext_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/12014415?format=original"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]
INSTR = {
    "kasparek_2025_phq8": ("Patient Health Questionnaire (PHQ-9), items 1-8", r"phq_[1-8]"),
    "kasparek_2025_gad7": ("Generalized Anxiety Disorder scale (GAD-7)", r"gad_[1-7]"),
    "kasparek_2025_bhs": ("Brief Hypervigilance Scale (BHS)", r"bhs_[1-5]"),
    "kasparek_2025_bpaq": ("Buss-Perry Aggression Questionnaire", r"bp_\d+"),
}


def levels(s):
    out = {}
    for part in re.split(r";\s*", str(s)):
        m = re.match(r"\s*(\d+)\s*=\s*(.+?)\s*$", part, re.S)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def main():
    x = pd.read_excel(io.BytesIO(requests.get(URL, headers=UA, timeout=120).content))
    x = x.set_index("Variable Name")
    for table, (instrument, pat) in INSTR.items():
        codes = [v for v in x.index if re.fullmatch(pat, str(v))]
        opts = levels(x.loc[codes[0], "Levels"])
        stems = [str(x.loc[c, "Question"]).split(" - ", 1) for c in codes]
        assert all(len(s) == 2 for s in stems)
        assert len({s[0] for s in stems}) == 1, table  # one shared stem per block
        instructions = stems[0][0].strip()
        rows = []
        for c, (_, text) in zip(codes, stems):
            for r, o in sorted(opts.items()):
                rows.append([table, f"{table}_1", c, instrument, instructions, "",
                             text.strip(), "", o, r])
        write(table, rows)
    # JVQ screener: the checklist question is the instruction; each scenario is an item.
    jq = x.loc["jvq_cl"]
    # one scenario per line; scenario 9 itself contains semicolons, so split on lines
    scen = {int(m.group(1)): m.group(2).strip() for m in
            re.finditer(r"^\s*(\d+)\s*=\s*(.+?)\s*$", str(jq["Levels"]), re.M)}
    di = levels(x.loc["jvq_4_di", "Levels"])  # 0 = not endorsed; 1 = endorsed
    rows = []
    for k in (4, 5, 9, 10, 14, 19, 27, 28, 29, 30):
        for r, o in sorted(di.items()):
            rows.append(["kasparek_2025_jvq", "kasparek_2025_jvq_1", f"jvq_{k}_di",
                         "Juvenile Victimization Questionnaire (JVQ) screener items",
                         " ".join(str(jq["Question"]).split()), "", scen[k], "", o, r])
    write("kasparek_2025_jvq", rows)


def write(table, rows):
    with open(OUT / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    print(table, len(rows), "rows")


if __name__ == "__main__":
    main()
