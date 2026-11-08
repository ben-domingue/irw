#!/usr/bin/env python3
"""Item text for pytlikzillig_2017_{institutional_trust,dispositional_trust,
government_trust} (10.1371/journal.pone.0175387, PLOS SI S1 File "Appendix
of Measures", journal.pone.0175387.s001, CC BY 4.0). Administered in English.

Mapping, by table:
- government_trust: the codes name their target (TrusFed, TrusStat, TrusLoc,
  TrusUNL, TrusUSSC, TrusMil, TrusPres) and each appendix item names one
  target. Self-describing; no inference.
- institutional_trust: codes are <target>_<construct><n>. The construct
  abbreviations resolve against the appendix headings one-for-one, with item
  counts matching exactly (USConf 4 = Unspecified Institutional Confidence,
  Leg 4 = Legitimacy, PfR 3 = Respect, PfV 3 = Voice, Dj 3 = Distributive
  Justice, Loy 4 = Loyalty, Svs 3 = Values Similarity, TwBM 3 = Benevolence,
  TwC 2 = Competence, TwHI 3 = Integrity, Obl 4 = Obligation to Obey, PfI 4 =
  Bias, Cyn 4 = Cynicism; 40 trustworthiness items, as the article says). The
  number <n> is taken as the item's position under its heading -- an ORDER
  inference within construct, checked by verify_pytlikzillig_2017.py (PfI4,
  the one positively-worded Bias item in the appendix, is the item the
  authors' SAS reverse-scores, and the 8 untrustworthiness items correlate
  negatively with the trustworthiness items).
  The appendix writes the target as "[institution]"; every item was rated for
  both the Nebraska Department of Natural Resources (codes NDNR_) and the
  Natural Resources Districts (codes NRD_), so the two targets are two
  sections and the placeholder is kept, as the study published it.
- dispositional_trust: Dt1-Dt9 = the nine appendix items in order (positional;
  the items share one polarity and one factor, so no statistical route can
  pin order -- recorded as such).
Responses: 1-7 agreement, stored 1 = strongly disagree ... 7 = strongly
  agree (data/pytlikzillig_2017_trust.py flips the deposit's reversed
  coding). The article labels the endpoints and calls 4 the neutral midpoint;
  only the two endpoint labels ship, levels 2-6 as rows with blank option_text.
One space restored: "The [institution]is not representative of Nebraskans"
  (Cyn2) is shipped as "The [institution] is not representative ...".
water_knowledge is NOT built: the appendix does not include the 18 quiz items.

Run: RESP_DIR=<dir> [RAW=<s001.docx>] python3 make_itemtext_pytlikzillig_2017.py
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
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0175387.s001"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt", "item_text",
        "correct_response", "option_text", "resp"]
OPTS = {1: "strongly disagree", 7: "strongly agree"}
HEAD = {"USConf": "Unspecified Institutional Confidence", "Leg": "Legitimacy", "PfR": "Respect",
        "PfV": "Voice", "Dj": "Distributive Justice", "Loy": "Loyalty", "Svs": "Values Similarity",
        "TwBM": "Benevolence", "TwC": "Competence", "TwHI": "Integrity", "Obl": "Obligation to Obey",
        "PfI": "Bias", "Cyn": "Cynicism"}
NONITEM = {"Trustworthiness", "Untrustworthiness", "Dispositional Trust", "Governmental Trust"} | set(HEAD.values())
GOV = {"TrusFed": "federal government", "TrusStat": "state government", "TrusLoc": "local government",
       "TrusUNL": "University of Nebraska", "TrusUSSC": "Supreme Court", "TrusMil": "military",
       "TrusPres": "President"}
TARGET = {"NDNR": "Nebraska Department of Natural Resources", "NRD": "Natural Resources Districts"}


def appendix():
    src = os.environ.get("RAW")
    if not src:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    lines = [p.text.strip() for p in docx.Document(src).paragraphs if p.text.strip()]
    assert lines[0] == "Appendix of Measures"
    groups, cur = {}, None
    for ln in lines[1:]:
        if ln in NONITEM:
            cur = ln
            groups.setdefault(cur, [])
        else:
            groups[cur].append(ln.replace("[institution]is", "[institution] is"))
    return groups


def rows_for(table, item, sec, instrument, text, levels):
    return [{"table": table, "section_id": sec, "item": item, "instrument": instrument, "instructions": "",
             "section_prompt": "", "item_text": text, "correct_response": "",
             "option_text": OPTS.get(int(v), ""), "resp": int(v)} for v in levels]


def write(table, rows):
    resp = pd.read_csv(RESP_DIR / f"{table}.csv")
    assert {r["item"] for r in rows} == set(resp["item"]), set(resp["item"]) ^ {r["item"] for r in rows}
    assert {r["resp"] for r in rows} == set(resp["resp"]), table
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / f"{table}__items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    print(f"{table}__items.csv: {len(rows)} rows, {len({r['item'] for r in rows})} items")


def main():
    g = appendix()
    lv = range(1, 8)
    counts = {"USConf": 4, "Leg": 4, "PfR": 3, "PfV": 3, "Dj": 3, "Loy": 4, "Svs": 3, "TwBM": 3,
              "TwC": 2, "TwHI": 3, "Obl": 4, "PfI": 4, "Cyn": 4}
    for ab, n in counts.items():
        assert len(g[HEAD[ab]]) == n, (ab, len(g[HEAD[ab]]))
    assert sum(counts.values()) - 4 == 40

    t = "pytlikzillig_2017_institutional_trust"
    inst = ("Institutional trust and trustworthiness items (PytlikZillig et al. 2017, S1 Appendix of Measures); "
            "[institution] = the Nebraska Department of Natural Resources (items NDNR_*) or the Natural Resources Districts (items NRD_*)")
    rows = []
    for k, (pre, name) in enumerate(TARGET.items(), start=1):
        for ab in counts:
            for i, text in enumerate(g[HEAD[ab]], start=1):
                rows += rows_for(t, f"{pre}_{ab}{i}", f"{t}_{k}", inst, text, lv)
    write(t, rows)

    t = "pytlikzillig_2017_dispositional_trust"
    dt = g["Dispositional Trust"]
    assert len(dt) == 9
    rows = []
    for i, text in enumerate(dt, start=1):
        rows += rows_for(t, f"Dt{i}", f"{t}_1", "Dispositional trust (PytlikZillig et al. 2017, S1 Appendix of Measures)", text, lv)
    write(t, rows)

    t = "pytlikzillig_2017_government_trust"
    gv = g["Governmental Trust"]
    assert len(gv) == 7
    rows = []
    for code, key in GOV.items():
        hit = [s for s in gv if key in s]
        assert len(hit) == 1, (code, hit)
        rows += rows_for(t, code, f"{t}_1", "Governmental trust (PytlikZillig et al. 2017, S1 Appendix of Measures)", hit[0], lv)
    write(t, rows)


if __name__ == "__main__":
    main()
