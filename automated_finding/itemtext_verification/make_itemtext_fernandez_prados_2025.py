#!/usr/bin/env python3
"""Item text for the six fernandez_prados_2025 tables (Mendeley 10.17632/2gwnjx729x.3).

Cheap case (data_labels): every item column of DATOS_DEPURADOS_COMPLETOSC.sav carries
its administered Spanish statement in [brackets] at the start of its SPSS variable
label, and value labels carry the options. data/fernandez_prados_2025_ai_attitudes.py
keeps the column names as `item`, so each stem is tied to its code by the column's
own label. The text after the bracket is the block's question, truncated by SPSS at
256 characters, so instructions are taken from the deposit's Cuestionario.docx
paragraph for that block (verbatim, whitespace-normalised); for ai_uses the block
question in the label is complete and is used. Options = value labels verbatim.

English *_translated is IRW's own translation (translation_source =
machine_translation in the provenance note; owes an itemtext_issues.qmd entry).
"""
import csv
import importlib.util
import re
from pathlib import Path

import docx
import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
SCRIPT = HERE.parent / "data" / "fernandez_prados_2025_ai_attitudes.py"
RAW = HERE / "runs" / "raw" / "fernandez_prados_2025"
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "instructions_translated", "section_prompt", "item_text", "item_text_translated",
        "correct_response", "option_text", "option_text_translated", "resp"]
P = "fernandez_prados_2025_"
INSTRUMENT = {P + "attari": "Attitudes towards Artificial Intelligence (Stein et al., 2024)",
              P + "gaais": "General Attitudes towards Artificial Intelligence Scale (GAAIS; Schepman and Rodway, 2022)",
              P + "aias": "Artificial Intelligence Anxiety Scale (AIAS; Wang y Wang, 2019)",
              P + "digcomp_comm": "Competencias Digitales (DigComp; Vuorikari, Kluzer y Punie, 2022): habilidades de comunicación",
              P + "digcomp_info": "Competencias Digitales (DigComp; Vuorikari, Kluzer y Punie, 2022): información y alfabetización",
              P + "ai_uses": "Uso de la IA"}
INSTR_KEY = {P + "attari": "Ahora te presentaremos", P + "gaais": "Ahora te presentaremos",
             P + "aias": "La siguiente sección del cuestionario",
             P + "digcomp_comm": "¿Por favor, dígame si en los últimos 3 meses",
             P + "digcomp_info": "¿Por favor, dígame si en los últimos 3 meses"}
INSTR_EN = {
    "Ahora te presentaremos": "We will now present a series of statements about artificial intelligence (AI). Please indicate how far you agree with each of them, based on your personal feelings, knowledge and experiences of AI. (1= Strongly DISAGREE... 7= Strongly AGREE)",
    "La siguiente sección del cuestionario": "The following section of the questionnaire focuses on your emotional reactions to learning about and using Artificial Intelligence. Read each statement carefully and specify how you feel about each situation described in relation to AI. (1= Strongly DISAGREE... 7= Strongly AGREE)",
    "¿Por favor, dígame si en los últimos 3 meses": "Please tell me whether, in the last 3 months, and how often you have used the Internet through any device (including apps) to carry out any of the following activities for personal reasons?",
    "ai_uses": "What do you use AI for, and how often?",
}
OPT_EN = {"1: Totalmente en DESACUERDO": "1: Strongly DISAGREE", "2: En desacuerdo": "2: Disagree",
          "3: Algo en desacuerdo": "3: Somewhat disagree",
          "4: Ni de acuerdo ni en desacuerdo": "4: Neither agree nor disagree",
          "5: Algo de acuerdo": "5: Somewhat agree", "6: De acuerdo": "6: Agree",
          "7: Totalmente DE ACUERDO": "7: Strongly AGREE", "Nunca": "Never",
          "Menos de una vez a la semana": "Less than once a week",
          "Al menos una vez a la semana, pero no diariamente": "At least once a week, but not daily",
          "A diario, pero no varias veces al día": "Daily, but not several times a day",
          "Varias veces al día": "Several times a day"}
EN = {
    "Astein_SQ001": "AI will make this world a better place.",
    "Astein_SQ002": "I have strong negative emotions about AI.",
    "Astein_SQ003": "I want to use technologies that rely on AI.",
    "Astein_SQ004": "AI has more disadvantages than advantages.",
    "Astein_SQ005": "I look forward to future AI developments.",
    "Astein_SQ006": "AI offers solutions to many world problems.",
    "Astein_SQ007": "I prefer technologies that do not feature AI.",
    "Astein_SQ008": "I am afraid of AI.",
    "Astein_SQ009": "I would rather choose a technology with AI than one without it.",
    "Astein_SQ010": "AI creates problems rather than solving them.",
    "Astein_SQ011": "When I think about AI, I have mostly positive feelings.",
    "Astein_SQ012": "I would rather avoid technologies that are based on AI.",
    "Aschepam_SQ002": "Artificial intelligence can provide new economic opportunities for this country.",
    "Aschepam_SQ003": "There are many beneficial applications of artificial intelligence.",
    "Aschepam_SQ004": "Much of society will benefit from a future full of artificial intelligence.",
    "Aschepam_SQ005": "Artificial intelligence can have positive impacts on people's wellbeing.",
    "Aschepam_SQ006": "I find artificial intelligence sinister.",
    "Aschepam_SQ007": "I shiver with discomfort when I think about future uses of artificial intelligence.",
    "Aschepam_SQ008": "Artificial intelligence might take control of people.",
    "Aschepam_SQ009": "I think artificial intelligence is dangerous.",
    "ANwang_SQ001": "I fear that an AI technique/product may replace humans.",
    "ANwang_SQ002": "Learning to use specific functions of an AI technique/product makes me anxious.",
    "ANwang_SQ003": "Reading the manual of an AI technique/product makes me anxious.",
    "ANwang_SQ004": "Learning how an AI technique/product works makes me anxious.",
    "ANwang_SQ005": "I fear that AI techniques/products will replace someone's job.",
    "ANwang_SQ006": "Being unable to keep up with the advances associated with AI techniques/products makes me anxious.",
    "ANwang_SQ007": "I fear that the widespread use of humanoid robots will take jobs away from people.",
    "ANwang_SQ008": "Learning to understand all of the special functions associated with an AI technique/product makes me anxious.",
    "ANwang_SQ009": "Learning to use AI techniques/products makes me anxious.",
    "ANwang_SQ010": "I fear that if I begin to use AI techniques/products I will become dependent upon them and lose some of my reasoning skills.",
    "ANwang_SQ011": "Learning to interact with an AI technique/product makes me anxious.",
    "ANwang_SQ012": "I fear that an AI technique/product will make us even lazier.",
    "ANwang_SQ013": "Taking a class about the development of AI techniques/products makes me anxious.",
    "ANwang_SQ014": "I fear that an AI technique/product will make us dependent.",
    "DigComp_HabilidadesComunicación_1": "Receiving or sending emails",
    "DigComp_HabilidadesComunicación_2": "Making or receiving calls or video calls over the Internet (using apps such as WhatsApp, Skype, Messenger, Facetime, ...)",
    "DigComp_HabilidadesComunicación_3": "Taking part in social networks (creating a user profile, posting messages or other contributions to Facebook, X, Instagram ...).",
    "DigComp_HabilidadesComunicación_4": "Using instant messaging (via WhatsApp, Skype, Messenger...)",
    "DigComp_HabilidadesComunicación_5": "Posting opinions on social or political issues on websites or social networks (e.g. Facebook, X, Instagram ...)",
    "DigComp_HabilidadesComunicación_6": "Taking part in online consultations or voting on civic or political issues",
    "DigComp_InformacionAlfabetizacion_1": "Reading news, newspapers, magazines online.",
    "DigComp_InformacionAlfabetizacion_2": "Looking for information on health topics (e.g. injuries, diseases, nutrition, ...)",
    "DigComp_InformacionAlfabetizacion_3": "Looking for information about goods or services",
    "DigComp_InformacionAlfabetizacion_4": "Checking the truthfulness of information or content found on the Internet by verifying the sources or looking for other information on the Internet",
    "DigComp_InformacionAlfabetizacion_5": "Checking the truthfulness of information or content found on the Internet by following or taking part in online discussions about the information",
    "DigComp_InformacionAlfabetizacion_6": "Checking the truthfulness of information or content found on the Internet by discussing it or using other information outside the Internet",
    "DigComp_InformacionAlfabetizacion_7": "Not checking the truthfulness of information or content found on the Internet because I knew the information or source was not reliable",
    "Uia_SQ002": "Consulting or searching for information",
    "Uia_SQ003": "Summarising texts or files",
    "Uia_SQ004": "Writing assignments, texts or emails",
    "Uia_SQ005": "Creating images, sounds or video",
    "Uia_SQ006": "Analysing data or calculations",
    "Uia_SQ007": "Writing code or programming",
}


def norm(s):
    return " ".join(str(s).replace("\xa0", " ").split())


def main():
    spec = importlib.util.spec_from_file_location("fp", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d, meta = pyreadstat.read_sav(str(RAW / "DATOS DEPURADOS_COMPLETOSC.sav"))
    tabs = mod.table_items(d.columns)
    paras = [norm(p.text) for p in docx.Document(str(RAW / "Cuestionario.docx")).paragraphs]
    for table, items in tabs.items():
        if table in INSTR_KEY:
            (instr,) = {p for p in paras if p.startswith(INSTR_KEY[table])}
            instr_en = INSTR_EN[INSTR_KEY[table]]
        else:
            lab = meta.column_names_to_labels[items[0]]
            instr = norm(re.match(r"\s*\[.*?\]\s*(.*)", lab, re.S).group(1))
            assert instr == "¿Para qué y con qué frecuencia utiliza las IA?", instr
            instr_en = INSTR_EN["ai_uses"]
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        rows = []
        for it in items:
            stem = norm(re.match(r"\s*\[(.*?)\]", meta.column_names_to_labels[it], re.S).group(1))
            for k, lab in sorted(meta.variable_value_labels[it].items()):
                lab = norm(lab)
                rows.append({"table": table, "section_id": f"{table}_1", "item": it,
                             "instrument": INSTRUMENT[table], "language": "Spanish",
                             "instructions": instr, "instructions_translated": instr_en,
                             "section_prompt": "", "item_text": stem,
                             "item_text_translated": EN[it], "correct_response": "",
                             "option_text": lab, "option_text_translated": OPT_EN[lab],
                             "resp": int(k)})
        assert {r["item"] for r in rows} == set(resp["item"])
        assert set(resp["resp"]) <= {r["resp"] for r in rows}
        p = OUT_DIR / f"{table}__items.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(f"{p.name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
