#!/usr/bin/env python3
"""Item text for mendes_lobao_2018_hpv_{knowledge,attitudes}
(10.1371/journal.pone.0206726, PLOS SI, CC BY 4.0).

Sources, both the study's own:
- S2 Questionnaire (journal.pone.0206726.s002): the Portuguese telephone
  questionnaire that was administered ("Avaliação da Aceitação Parental da
  Vacina Contra HPV"). Base fields.
- S3 Questionnaire (journal.pone.0206726.s003): the authors' "ENGLIGH
  TRANSLATION". The *_translated fields (translation_source =
  study_supplied). The English is a looser rendering in places: C12/C13/C15-C17
  add "I think that", C23-C29 are recast in the second person ("You think
  ..."), C27 reads "You trust the national immunisation program" where the
  Portuguese says "Eu confio nas vacinas que são dadas nas campanhas de
  vacinação" (I trust the vaccines given in vaccination campaigns), and B4
  "airborne" for "por via respiratória / pelo ar". Shipped as the study wrote it.

Item codes: the .sav variable names (b2..b11, c11..c40) are the
questionnaire's own item numbers, printed beside each statement in both
versions (the Portuguese repeats C2-C5 for the son block that the English
numbers C7-C10, but C11-C40 agree). Explicit code-label match.

Transcription: the Portuguese .docx drops the space at many run boundaries
("camisinhaprotege", "filhanão", "Vocêconcorda"); those spaces are restored
here, and the script asserts that each restored string equals the .docx text
once all whitespace is removed, so nothing else was changed.

Response coding (data/mendes_lobao_2018_hpv.py): attitudes 1 = yes, I agree,
0 = no ("I don't know", code 2, dropped). Knowledge is SCORED, 1 = the answer
matches the paper's Table 2 key, 0 = it does not; option_text is blank for
both levels, and correct_response carries the keyed answer as the
questionnaire labels it (Verdadeiro/Falso for the true/false blocks; the two
knowledge statements asked in the agree/disagree block, C22 and C31, carry
"Você concorda?"/"Você não concorda?").

Run: RESP_DIR=<dir> [RAW_PT=<s002.docx>] [RAW_EN=<s003.docx>] python3 make_itemtext_mendes_lobao_2018.py
"""
import csv
import io
import os
import re
from pathlib import Path

import docx
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = Path(os.environ.get("RESP_DIR", HERE / "irw_output"))
SI = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0206726.s00"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
INSTRUMENT = "Avaliação da Aceitação Parental da Vacina Contra HPV (Mendes Lobão et al. 2018, telephone KAP questionnaire, Brazil)"

PT = {
    "b2": "O HPV é transmitido pelo uso de banheiro público / piscina / banheira.",
    "b3": "O HPV é transmitido por contato sexual.",
    "b4": "O HPV é transmitido por via respiratória / pelo ar.",
    "b5": "Uma pessoa com HPV geralmente apresenta sintomas.",
    "b6": "O HPV é um vírus muito comum.",
    "b7": "Homens não podem contrair / pegar HPV.",
    "b8": "Mesmo não tendo sintomas, uma pessoa pode transmitir HPV.",
    "b9": "O uso de camisinha protege completamente contra HPV.",
    "b10": "O HPV pode ser curado com antibióticos.",
    "b11": "Já existe vacina contra HPV.",
    "c11": "A vacina contra HPV é eficaz / funciona.",
    "c12": "Minha filha não precisa tomar a vacina contra HPV.",
    "c13": "Meu filho não precisa tomar a vacina contra HPV.",
    "c14": "Eu acredito em vacinas de um modo geral.",
    "c15": "Minha filha tem risco/chance de pegar HPV.",
    "c16": "Meu filho tem risco/chance de pegar HPV.",
    "c17": "A vacina contra HPV é muito cara.",
    "c18": "Eu não daria a vacina contra HPV a minha filha se tivesse que pagar.",
    "c19": "Eu não daria a vacina contra HPV a meu filho se tivesse que pagar.",
    "c20": "A vacina contra o HPV não é segura e pode dar reações graves.",
    "c21": "Meninas de 9 á 13 anos são muito novas para tomar a vacina contra HPV.",
    "c22": "As reações mais comuns à vacina contra HPV são leves, tipo dor e incômodo no local da injeção.",
    "c23": "Tomar a vacina contra HPV pode fazer as meninas iniciarem a vida sexual mais cedo.",
    "c24": "Tomar a vacina contra HPV pode fazer os meninos iniciarem a vida sexual mais cedo.",
    "c25": "Eu só daria a vacina contra HPV para minha filha se o médico dela recomendasse.",
    "c26": "Minha religião não permite vacinar contra HPV.",
    "c27": "Eu confio nas vacinas que são dadas nas campanhas de vacinação",
    "c28": "Eu só daria a vacina contra HPV a minha filha se minhas amigas também dessem para as filhas delas.",
    "c29": "Eu não daria uma vacina contra uma doença sexualmente transmissível.",
    "c30": "Os pais têm obrigação de vacinar seus filhos.",
    "c31": "A vacina contra HPV não serve para meninos.",
    "c32": "Existe vacina contra o câncer do colo do útero.",
    "c33": "Não existe vacina contra condiloma e verruga genital.",
    "c34": "O HPV pode causar câncer do colo do útero.",
    "c35": "O câncer de colo do útero não é uma causa comum de morte por câncer entre as mulheres",
    "c36": "O HPV não causa câncer em homens.",
    "c37": "O HPV pode causar verrugas genitais / condiloma / “crista de galo.”",
    "c38": "Se o exame preventivo / Papanicolau é normal, então a mulher não tem HPV.",
    "c39": "Meninas que tomaram a vacina contra o HPV não precisam mais fazer o exame preventivo / Papanicolau.",
    "c40": "A vacina contra o HPV funciona melhor quando dada antes do início da vida sexual.",
}
PROMPT_B = "Mesmo assim, gostaria de saber sua opinião sobre HPV. Eu vou ler algumas afirmações. Por favor, responda se você acha que é ‘Verdadeiro’ ou ‘Falso’."
PROMPT_B_EN = "Either way, I would like to hear your opinion about HPV. I will read some statements. Please, respond “YES” or “NO.”"
AGREE, DISAGREE = "Você concorda?", "Você não concorda?"
KEY = {"b2": 0, "b3": 1, "b4": 0, "b5": 0, "b6": 1, "b7": 0, "b8": 1, "b9": 0, "b10": 0, "b11": 1,
       "c22": 1, "c31": 0, "c32": 1, "c33": 0, "c34": 1, "c35": 0, "c36": 0, "c37": 1, "c38": 0,
       "c39": 0, "c40": 1}


def load_docx(env, n):
    src = os.environ.get(env)
    if not src:
        r = requests.get(SI + str(n), headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    d = docx.Document(src)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            parts += [c.text for c in row.cells]
    return "\n".join(parts)


def english(text):
    """Item number at line start, tab, statement (s003 layout)."""
    out = {}
    for ln in text.splitlines():
        m = re.match(r"^\s*([BC]\d+)\t(.+)$", ln)
        if m and m.group(1).lower() in PT:
            out[m.group(1).lower()] = m.group(2).strip()
    return out


def main():
    pt_doc = re.sub(r"\s+", "", load_docx("RAW_PT", 2))
    en = english(load_docx("RAW_EN", 3))
    assert set(en) == set(PT), set(PT) ^ set(en)
    for code, s in PT.items():
        assert re.sub(r"\s+", "", s) in pt_doc, code
    for s in (PROMPT_B, AGREE, DISAGREE):
        assert re.sub(r"\s+", "", s) in pt_doc, s

    # knowledge
    t = "mendes_lobao_2018_hpv_knowledge"
    resp = pd.read_csv(RESP_DIR / f"{t}.csv")
    rows = []
    for code in KEY:
        if code.startswith("b"):
            sec, sp, sp_en, key = 1, PROMPT_B, PROMPT_B_EN, ("Verdadeiro" if KEY[code] else "Falso")
        elif code in ("c22", "c31"):
            sec, sp, sp_en, key = 2, "", "", (AGREE if KEY[code] else DISAGREE)
        else:
            sec, sp, sp_en, key = 3, "", "", ("Verdadeiro" if KEY[code] else "Falso")
        for v in (0, 1):
            rows.append({"table": t, "section_id": f"{t}_{sec}", "item": code, "instrument": INSTRUMENT,
                         "language": "Portuguese", "instructions": "", "section_prompt": sp,
                         "item_text": PT[code], "correct_response": key, "option_text": "", "resp": v,
                         "instructions_translated": "", "section_prompt_translated": sp_en,
                         "item_text_translated": en[code], "option_text_translated": ""})
    write(t, rows, resp)

    # attitudes
    t = "mendes_lobao_2018_hpv_attitudes"
    resp = pd.read_csv(RESP_DIR / f"{t}.csv")
    rows = []
    for code in [c for c in PT if c.startswith("c") and c not in KEY]:
        for v, lab, lab_en in ((0, DISAGREE, "NO, I DISAGREE"), (1, AGREE, "YES, I AGREE")):
            rows.append({"table": t, "section_id": f"{t}_1", "item": code, "instrument": INSTRUMENT,
                         "language": "Portuguese", "instructions": "", "section_prompt": "",
                         "item_text": PT[code], "correct_response": "", "option_text": lab, "resp": v,
                         "instructions_translated": "", "section_prompt_translated": "",
                         "item_text_translated": en[code], "option_text_translated": lab_en})
    write(t, rows, resp)


def write(t, rows, resp):
    assert {r["item"] for r in rows} == set(resp["item"]), t
    assert {r["resp"] for r in rows} == set(resp["resp"]), t
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{t}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{t}__items.csv: {len(rows)} rows, {len({r['item'] for r in rows})} items")


if __name__ == "__main__":
    main()
