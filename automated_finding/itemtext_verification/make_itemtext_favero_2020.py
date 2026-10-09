#!/usr/bin/env python3
"""Item text for the three favero_2020_* tables (Harvard Dataverse 10.7910/DVN/1LIIDV;
article 10.30636/jbpa.32.167). English administration (US Qualtrics panel).

Source: the deposit's own Qualtrics survey export,
Study_of_Coronavirus_COVID-19_Perceptions.qsf (file 3829236). Each response column of
covid19perceptions.dta is a Qualtrics DataExportTag, so the mapping is by name, not by
position:
  motiv1..motiv5  = the `motiv` matrix's ChoiceDataExportTags (choices 1-5; choice 6,
                    tag attention1, is the attention check and is not a table item);
                    resp 1-5 = its Answers (RecodeValues 1..5 are identity).
  socdistK_1      = slider question tagged socdistK (Qualtrics appends _1 for the single
                    slider choice); 0-10, end labels "Strongly disagree"/"Strongly agree".
  attitudeK_1     = slider question tagged attitudeK; same scale.
The block intro (a descriptive-text question in the same block) is `instructions`.
Slider interior points 1-9 have no labels and stay blank.
"""
import csv
import json
import os
import re
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("IRW_RAW_DIR", HERE / "runs" / "raw")) / "1liidv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
QSF_URL = "https://dataverse.harvard.edu/api/access/datafile/3829236"
INSTRUMENT = {
    "favero_2020_prosocial_motivation": "Prosocial motivation and empathy items (Favero & Pedersen 2020)",
    "favero_2020_social_distancing": "Intended social distancing (Favero & Pedersen 2020)",
    "favero_2020_covid_attitudes": "COVID-19 policy attitudes (Favero & Pedersen 2020)"}
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "").replace("&nbsp;", " ")
    return " ".join(s.split())


def main():
    p = RAW / "survey.qsf"
    if not p.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        r = requests.get(QSF_URL, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    q = json.load(open(p, encoding="utf-8"))
    sq = {el["PrimaryAttribute"]: el["Payload"] for el in q["SurveyElements"] if el.get("Element") == "SQ"}
    by_tag = {v.get("DataExportTag"): v for v in sq.values()}
    intro = {}
    for el in q["SurveyElements"]:
        if el.get("Element") != "BL":
            continue
        blocks = el["Payload"].values() if isinstance(el["Payload"], dict) else el["Payload"]
        for b in blocks:
            ids = [x["QuestionID"] for x in b.get("BlockElements", []) if x.get("Type") == "Question"]
            tags = [sq[i].get("DataExportTag") for i in ids if i in sq]
            db = [clean(sq[i]["QuestionText"]) for i in ids if sq.get(i, {}).get("QuestionType") == "DB"]
            for t in tags:
                intro[t] = db[0] if db else ""
    rows = {k: [] for k in INSTRUMENT}
    # motiv matrix
    m = by_tag["motiv"]
    tags = m["ChoiceDataExportTags"]
    assert m["RecodeValues"] == {str(i): str(i) for i in range(1, 6)}
    answers = {int(k): clean(v["Display"]) for k, v in m["Answers"].items()}
    t = "favero_2020_prosocial_motivation"
    for ch, tag in tags.items():
        if not tag.startswith("motiv"):
            assert tag == "attention1"
            continue
        for r in range(1, 6):
            rows[t].append({"table": t, "section_id": f"{t}_1", "item": tag,
                            "instrument": INSTRUMENT[t], "instructions": clean(m["QuestionText"]),
                            "section_prompt": "", "item_text": clean(m["Choices"][ch]["Display"]),
                            "correct_response": "", "option_text": answers[r], "resp": r})
    # sliders
    for t, stem, k in (("favero_2020_social_distancing", "socdist", 5),
                       ("favero_2020_covid_attitudes", "attitude", 4)):
        for i in range(1, k + 1):
            s = by_tag[f"{stem}{i}"]
            cfg = s["Configuration"]
            assert (cfg["CSSliderMin"], cfg["CSSliderMax"], cfg["GridLines"]) == (0, 10, 10)
            lab = {1: clean(s["Labels"]["1"]["Display"]), 2: clean(s["Labels"]["2"]["Display"])}
            for r in range(0, 11):
                rows[t].append({"table": t, "section_id": f"{t}_1", "item": f"{stem}{i}_1",
                                "instrument": INSTRUMENT[t], "instructions": intro[f"{stem}{i}"],
                                "section_prompt": "", "item_text": clean(s["QuestionText"]),
                                "correct_response": "",
                                "option_text": lab[1] if r == 0 else lab[2] if r == 10 else "",
                                "resp": r})
    out = HERE / "itemtext_output"
    for t, rr in rows.items():
        resp = pd.read_csv(HERE / "irw_output" / f"{t}.csv")
        assert {x["item"] for x in rr} == set(resp["item"]), t
        assert set(resp["resp"]) <= {x["resp"] for x in rr}, t
        with open(out / f"{t}__items.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(rr)
        print(f"{t}__items.csv: {len(rr)} rows")


if __name__ == "__main__":
    main()
