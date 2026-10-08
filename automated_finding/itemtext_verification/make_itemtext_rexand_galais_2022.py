#!/usr/bin/env python3
"""Item text for rexand_galais_2022_ipofr (Mendeley 10.17632/tv6w6yyfy8.4).

The cheap case in Step 3.5: the deposit's own "IPO Codebook V2.pdf" prints the
40-item IPO-fr twice -- in French (as administered) and in the authors' English
translation -- and follows every item with its data-file code in parentheses,
e.g. "(IPO PD/ID7)". data/rexand_galais_2022_ipo.py turns those headers into
`item` reversibly ("IPO PD/ID7" -> "PDID7"), so each stem is tied to its code by
name, not by position. Text is taken from `pdftotext -layout` output: the
trailing "1 2 3 4 5" answer grid is stripped from each line and wrapped lines are
re-joined with single spaces; nothing else is changed.

Deviations, disclosed: none to the wording. Source oddities kept verbatim: the
English for RT7 and RT10 is the same sentence ("I believe that things will happen
simply by thinking about them.") although the French differs (RT7 "... mes
souhaits ou mes pensees vont se realiser comme par magie"); the English of
PDID10 reads "at other times 1 think", PDID30 "I'am", PDID12 "People tell me have
difficulty". The codebook's scoring key lists 9 RT item positions (3, 6, ..., 30)
while its item list and the data carry 10 RT codes; codes, not the key, decide.
"""
import csv
import re
import subprocess
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP = HERE / "irw_output" / "rexand_galais_2022_ipofr.csv"
PDF = HERE / "runs" / "raw" / "rexand_galais_2022" / "IPO Codebook V2.pdf"
TABLE = "rexand_galais_2022_ipofr"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text",
        "item_text_translated", "correct_response", "option_text",
        "option_text_translated", "resp"]
INSTR_FR = ("Ce questionnaire contient des affirmations portant sur une grande variété "
            "d'attitudes, de sentiments et de comportements que les personnes adoptent et "
            "éprouvent au cours de leur vie. Veuillez lire attentivement toutes les "
            "instructions ci-dessous et remplir ce questionnaire tel qu'il s'applique à vous. "
            "Pour chacune des questions ci-dessous, cochez la réponse qui caractérise le mieux "
            "ce que vous pensez de l'affirmation proposée : 1 = Jamais vrai, 2 = Rarement vrai, "
            "3 = Parfois vrai, 4 = Souvent vrai et 5 = Toujours vrai.")
INSTR_EN = ("This questionnaire contains statements about a variety of attitudes, feelings, "
            "and behaviors that people have during their lives. Please read carefully all of "
            "the directions below and complete this questionnaire as it applies to you. For "
            "each of the questions below, tick the answer that best characterizes how you feel "
            "about the proposed statement: 1 = Never true, 2 = Rarely true, 3 = Sometimes true, "
            "4 = Often true and 5 = Always true.")
OPT_FR = {1: "Jamais vrai", 2: "Rarement vrai", 3: "Parfois vrai", 4: "Souvent vrai",
          5: "Toujours vrai"}
OPT_EN = {1: "Never true", 2: "Rarely true", 3: "Sometimes true", 4: "Often true",
          5: "Always true"}


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def items(block):
    lines = [re.sub(r"\s+1\s+2\s+3\s+4\s+5\s*$", "", ln).strip() for ln in block.splitlines()]
    txt = " ".join(l for l in lines if l)
    out = {}
    for m in re.finditer(r"(?<![\w(])(\d{1,2})\.?\s+(.*?)\((IPO [^)]+)\)", txt):
        n, body, code = m.groups()
        code = norm(code).replace("IPO ", "").replace("/", "")
        assert code not in out, code
        out[code] = (int(n), norm(body))
    return out


def main():
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True,
                         text=True, check=True).stdout
    fr, en = txt.split("[English translation]")
    assert norm(INSTR_FR.split(" Pour")[0])[:60] in norm(fr)
    F, E = items(fr.split("Correction:")[0]), items(en)
    assert len(F) == 40 and set(F) == set(E), (len(F), set(F) ^ set(E))
    assert all(F[k][0] == E[k][0] for k in F)       # same position in both versions
    resp = pd.read_csv(RESP)
    assert set(resp["item"]) == set(F) and set(resp["resp"]) == {1, 2, 3, 4, 5}
    rows = []
    for code in sorted(F, key=lambda k: F[k][0]):
        for r in range(1, 6):
            rows.append({"table": TABLE, "section_id": f"{TABLE}_1", "item": code,
                         "instrument": "Inventaire de l'Organisation de la Personnalité – version française (IPO-fr)",
                         "language": "French", "instructions": INSTR_FR,
                         "instructions_translated": INSTR_EN, "section_prompt": "",
                         "item_text": F[code][1], "item_text_translated": E[code][1],
                         "correct_response": "", "option_text": OPT_FR[r],
                         "option_text_translated": OPT_EN[r], "resp": r})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{TABLE}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len(F)} items")


if __name__ == "__main__":
    main()
