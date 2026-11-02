#!/usr/bin/env python3
"""Item text for the clemente_2024 attitude tables (formerly four) (10.1016/j.heliyon.2024.e36260).

Source: the article's own SI, mmc1.pdf (Europe PMC supplementaryFiles zip for
PMC11378926), which prints (a) the authors' English translation of the
attitude block and (b) the full Spanish questionnaire as administered in Spain
and Peru, including the SD4 and PMD blocks (the English part omits those two:
"The standardized questionnaires SD-4, PMD ... can be consulted in Spanish").

Administered language: Spanish. Base fields hold the Spanish wording verbatim
(typos kept: SD4 item 6 "Hacer halagos en una buena manera"). _translated:
  * attitude_father / attitude_mother: the authors' own English translation
    from the same PDF, verbatim (including "He Psychologically abuses",
    "She doesn't know how to educate his children").
  * sd4 / pmd: the SI has no English. The _translated fields are IRW's own
    rendering of the Spanish (not the published English SD4/PMD wording),
    disclosed in provenance and public_note.

Code-to-text tie (data/clemente_2024_divorced_parents.py keeps the .sav column
names as `item`):
  * FATHERk / MOTHERk = item k of the "Preguntas sobre el padre/la madre"
    block. The .sav variable labels agree with the printed item at the same
    position for k != 9; FATHER9/MOTHER9 are labelled "Does not see child",
    which matches no printed item, and are tied to printed item 9 by position.
  * SD4_k = item k of the SD4 block (positional; verify_clemente_2024_sd4.R).
  * PMD columns are named by mechanism (Moral_justification ...
    Attribution_of_blame), in the order of Moore et al.'s (2012) 8-item PMD,
    which is the printed order of items 1-8 here; item 9 is the attention check.
Every Spanish string below is asserted to occur, in block order, in the PDF.

2026-11-02: the SD4 and PMD blocks were removed from this script and their two
item-text tables withdrawn (tools/withdrawals/withdraw_weak_hits_2026-11-02.py):
the Short Dark Tetrad is blocked and Moore et al.'s PMD is held in
itemtext/instrument_rights_register.csv. Only the two attitude tables are built.
"""
import csv
import io
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11378926/supplementaryFiles"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]

PARENT_ES = [
    "Sus hijos no le quieren", "No sabe educarles", "Es posible que les agreda físicamente",
    "Les maltrata psicológicamente", "No les cuida adecuadamente",
    "No aporta dinero para su cuidado, si es su obligación", "Es raro que les haga regalos",
    "Es raro que les llame telefónicamente cuando no está con ellos",
    "Creo que no quiere a sus hijos",
    "Creo que utiliza a sus hijos para ir contra el otro progenitor"]
FATHER_EN = [
    "The children do not love this parent", "He doesn't know how to educate his children",
    "He may physically attack his children", "He Psychologically abuses his children",
    "He does not take proper care of his children",
    "He does not contribute money for the care of his children, if it is his obligation",
    "It is rare that he gives gifts to his children",
    "It is rare that he calls his children when he is not with them.",
    "I believe that he/she does not love his/her children.",
    "I think he uses his children to go against the other parent"]
MOTHER_EN = [
    "The children do not love this parent", "She doesn't know how to educate his children",
    "She may physically attack his children", "She Psychologically abuses his children",
    "She does not take proper care of his children",
    "She does not contribute money for the care of his children, if it is his obligation",
    "It is rare that She gives gifts to his children",
    "It is rare that She calls his children when She is not with them.",
    "I believe that he/she does not love his/her children.",
    "I think She uses his children to go against the other parent"]
PARENT_INSTR_ES = ("A continuación le vamos a efectuar unas preguntas referentes a los padres "
                   "de los niños, a las madres, a los niños y a usted. Responda según la escala "
                   "desde “muy de acuerdo” a “muy en desacuerdo”.")
PARENT_INSTR_EN = ("Next we are going to ask you some questions regarding the children's fathers, "
                   "the mothers, the children and you. Respond according to the scale from "
                   "“strongly agree” to “strongly disagree.”")
OPT5_ES = ["Completamente en desacuerdo", "En desacuerdo", "Ni de acuerdo ni en desacuerdo",
           "De acuerdo", "Completamente de acuerdo"]
OPT5_PARENT_EN = ["Completely disagree", "Disagreement", "Neither agree nor disagree",
                  "Agree", "Completely agree"]



def norm(s: str) -> str:
    s = re.sub(r"(?<!\S)[1-7](?!\S)", " ", s)      # strip the printed 1..7 answer grid
    return re.sub(r"\s+", " ", s).strip()


def pdf_text() -> str:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    blob = zipfile.ZipFile(io.BytesIO(r.content)).read("mmc1.pdf")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(blob)
        f.flush()
        return norm(subprocess.run(["pdftotext", f.name, "-"], check=True,
                                   capture_output=True, text=True).stdout)


def in_order(txt: str, start: int, strings: list) -> int:
    pos = start
    for s in strings:
        i = txt.find(norm(s), pos)
        assert i >= 0, ("not found in order", s, pos)
        pos = i + len(norm(s))
    return pos


def main() -> None:
    txt = pdf_text()
    es = txt.index("Preguntas sobre el padre de los niños:")
    assert norm(PARENT_INSTR_ES) in txt[:es]
    in_order(txt, es, PARENT_ES)
    ma = txt.index("Preguntas sobre la madre de los niños:")
    in_order(txt, ma, PARENT_ES)
    en = txt.index("Questions about the children's father:")
    assert norm(PARENT_INSTR_EN) in txt[:en]
    p = in_order(txt, en, FATHER_EN)
    in_order(txt, p, MOTHER_EN)

    specs = {
        "clemente_2024_attitude_father": dict(
            instrument="Attitudes toward the children's father after divorce (Clemente et al., 10 items)",
            items=[f"FATHER{i}" for i in range(1, 11)], es=PARENT_ES, en=FATHER_EN,
            instr=(PARENT_INSTR_ES, PARENT_INSTR_EN),
            prompt=("Preguntas sobre el padre de los niños:", "Questions about the children's father:"),
            opts=(OPT5_ES, OPT5_PARENT_EN)),
        "clemente_2024_attitude_mother": dict(
            instrument="Attitudes toward the children's mother after divorce (Clemente et al., 10 items)",
            items=[f"MOTHER{i}" for i in range(1, 11)], es=PARENT_ES, en=MOTHER_EN,
            instr=(PARENT_INSTR_ES, PARENT_INSTR_EN),
            prompt=("Preguntas sobre la madre de los niños:", "Questions about the children’s mother:"),
            opts=(OPT5_ES, OPT5_PARENT_EN)),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, s in specs.items():
        resp = pd.read_csv(HERE / "irw_output" / f"{table}.csv")
        assert set(resp["item"]) == set(s["items"]), table
        ok_es, ok_en = s["opts"]
        assert set(resp["resp"]) <= set(range(1, len(ok_es) + 1)), table
        rows = []
        for k, item in enumerate(s["items"]):
            for v, (o_es, o_en) in enumerate(zip(ok_es, ok_en), start=1):
                rows.append([table, f"{table}_1", item, s["instrument"], "Spanish",
                             s["instr"][0], s["prompt"][0], s["es"][k], None, o_es, v,
                             s["instr"][1], s["prompt"][1], s["en"][k], o_en])
        out = pd.DataFrame(rows, columns=COLS)
        out.to_csv(OUT_DIR / f"{table}__items.csv", index=False,
                   quoting=csv.QUOTE_NONNUMERIC, na_rep="NA")
        print(f"{table}__items.csv: {len(out)} rows, {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
