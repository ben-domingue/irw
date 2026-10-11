#!/usr/bin/env python3
"""Item text for the three perez_hernandez_2021_* tables (ENCOVID-19, Zenodo 4602374 / 4776828).

Stems are the Stata variable labels of the two .dta files, anchors their value labels,
both Spanish as administered. data/perez_hernandez_2021_encovid.py maps the ship codes
(gad1-7, elcsa1-8, cesd1-7) to variable names by an explicit table; this script uses the
same table, so code->label is by variable name. Stata truncates labels at 80 characters:
gad1 and gad2 are completed from the October file's untruncated GAD-2 labels; gad5 and
cesd1 are completed by IRW with the standard Spanish wording ("... tranquilo(a)?",
"... la tristeza?") and disclosed. The labels abbreviate the ELCSA stem as
"ELU3M, PFDDOR:" (= "En los ultimos 3 meses, por falta de dinero u otros recursos"),
expanded into section_prompt. English is IRW's (translation_source = irw_generated).
"""
import csv
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent
OUT_DIR = HERE / "itemtext_output"
RESP_DIR = HERE / "irw_output"
RAW = {"july": HERE / "runs" / "raw" / "10_5281_zenodo_4602374" / "base_covid_julio2020.dta",
       "october": HERE / "runs" / "raw" / "10_5281_zenodo_4776828" / "base_covid_octubre2020.dta"}
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
P = "perez_hernandez_2021_"
GAD = {f"gad{k}": f"p{67 + k}_ansiedad" for k in range(1, 8)}
CESD = {f"cesd{k}": f"p{77 + k}_salud" for k in range(1, 8)}
ELCSA = {f"elcsa{k}": f"p66{c}_segalim" for k, c in enumerate("abcdefgh", 1)}
FIX = {  # truncated Stata labels, completed (see docstring)
    "gad1": "¿Con que frecuencia se ha sentido nervioso(a), intranquilo(a) o con los nervios de punta?",
    "gad2": "¿Con que frecuencia sintio que no podia dejar de preocuparse o que no podia controlar la preocupación?",
    "gad5": "¿Con que frecuencia estuvo tan inquieto que le era dificil permanecer sentado tranquilo(a)?",
    "cesd1": "Durante la semana pasada, ¿sintió como si no pudiera quitarse de encima la tristeza?",
}
EN_GAD = ["How often have you felt nervous, anxious or on edge?",
          "How often did you feel that you could not stop worrying or could not control your worrying?",
          "How often did you feel that you worried too much about different things?",
          "How often did you feel it was difficult to relax?",
          "How often were you so restless that it was hard to sit still?",
          "How often did you feel that you became annoyed or irritable easily?",
          "How often did you feel afraid, or as if something terrible might happen?"]
EN_CESD = ["During the past week, did you feel as if you could not shake off the sadness?",
           "During the past week, did you have trouble concentrating on what you were doing?",
           "During the past week, did you feel depressed?",
           "During the past week, did you feel that everything you did was an effort?",
           "During the past week, were you unable to sleep well?",
           "During the past week, did you enjoy life?",
           "During the past week, did you feel sad?"]
EN_ELCSA = ["Did you worry that food would run out in your household?",
            "Did your household run out of food?",
            "Did your household stop having a healthy diet?",
            "Did your household have a diet based on little variety of foods?",
            "Did your household skip breakfast, lunch or dinner?",
            "Did you eat less than you should?",
            "Did you feel hungry but not eat?",
            "Did you eat only once a day or go a whole day without eating?"]
OPT_GAD = {0: "Never", 1: "Several days", 2: "More than half the days", 3: "Nearly every day or every day"}
OPT_CESD = {0: "Rarely or never", 1: "A few times or once (1 or 2 days)", 2: "More than half the days (3 or 4 days)",
            3: "Nearly every day or every day (5 or more days)"}
OPT_YN = {0: "No", 1: "Yes"}
ELCSA_PROMPT = "En los últimos 3 meses, por falta de dinero u otros recursos, ..."
ELCSA_PROMPT_EN = "In the last 3 months, for lack of money or other resources, ..."


def labels(month):
    _, m = pyreadstat.read_dta(str(RAW[month]), metadataonly=True)
    return m.column_names_to_labels, m.variable_value_labels


def main() -> None:
    jl, jv = labels("july")
    ol, ov = labels("october")
    # the October GAD-2 labels are untruncated and complete gad1/gad2
    assert ol["p76_ansiedad"].endswith("nervios de punta?") and ol["p77_ansiedad"].endswith("preocupación?")
    specs = {  # table -> (instrument, code->var, label source, value-label source, prompt, EN stems, EN options)
        P + "gad7": ("GAD-7 (Escala del trastorno de ansiedad generalizada), ENCOVID-19 July 2020; October 2020 asked the GAD-2",
                     GAD, jl, jv, "", EN_GAD, OPT_GAD),
        P + "elcsa": ("ELCSA (Escala Latinoamericana y Caribeña de Seguridad Alimentaria), adult items, ENCOVID-19 July and October 2020",
                      ELCSA, jl, jv, ELCSA_PROMPT, EN_ELCSA, OPT_YN),
        P + "cesd7": ("CES-D-7 (Escala de Depresión del Centro de Estudios Epidemiológicos, 7 items), ENCOVID-19 October 2020",
                      CESD, ol, ov, "", EN_CESD, OPT_CESD),
    }
    for table, (instr, cmap, lab, vlab, prompt, en, opts) in specs.items():
        resp = pd.read_csv(RESP_DIR / f"{table}.csv")
        assert set(cmap) == set(resp["item"]), (table, set(cmap) ^ set(resp["item"]))
        rows = []
        for k, (code, var) in enumerate(cmap.items()):
            stem = lab[var]
            if code in FIX:
                assert FIX[code].startswith(stem[:60]), (code, stem)
                stem = FIX[code]
            if stem.startswith("ELU3M, PFDDOR:"):
                stem = stem[len("ELU3M, PFDDOR:"):].strip()
            vl = vlab[var]
            for r in sorted(resp.loc[resp["item"] == code, "resp"].unique()):
                rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instr,
                             "language": "Spanish", "instructions": "", "section_prompt": prompt, "item_text": stem,
                             "correct_response": "", "option_text": vl[int(r)], "resp": int(r),
                             "instructions_translated": "", "section_prompt_translated": ELCSA_PROMPT_EN if prompt else "",
                             "item_text_translated": en[k], "option_text_translated": opts[int(r)]})
        with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rows)
        print(table, len(rows), "rows")


if __name__ == "__main__":
    main()
