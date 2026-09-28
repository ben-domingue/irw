#!/usr/bin/env python3
"""Build the __items.csv files for batch_ingest_0927 (tables ingested in irw#2484).

Run from itemtext/: python3 itemtables/batch_ingest_0927/build_items.py
Sources are cached under itemtext/.cache/ (gitignored); URLs are in provenance.csv.
Every item_text/option_text below is read from the deposit's own files -- nothing
is typed in by hand except the instrument names.
"""
import html
import json
import re
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent.parent / ".cache"
COLS = ["table", "section_id", "item", "instrument", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp"]


def write(rows, table):
    df = pd.DataFrame(rows, columns=COLS)
    df.to_csv(HERE / f"{table}__items.csv", index=False, na_rep="NA",
              quoting=1)  # QUOTE_ALL; normalize_nulls.R settles NA afterwards
    print(table, len(df), "rows", df["item"].nunique(), "items")


def strip_html(s):
    s = re.sub(r"</p>\s*<p>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return "\n".join(x.strip() for x in s.split("\n")).strip()


# ---------------------------------------------------------------- DVMSQ
def dvmsq():
    T = "williams_2022_dvmsq"
    k = pd.read_csv(CACHE / "williams_2022_dvmsq" / "dict.csv",
                    encoding="utf-8-sig").set_index("Variable / Field Name")
    form = k[k["Form Name"] == "dukevanderbilt_misophonia_screening_questionnaire"]
    inst = "Duke-Vanderbilt Misophonia Screening Questionnaire (DVMSQ), item pool as administered"
    rows, sec, prompt = [], 0, None
    for var, r in form.iterrows():
        if r["Field Type"] not in ("yesno", "radio"):
            continue
        hdr = r["Section Header"]
        if var == "misophonia_screen":
            sec, prompt = 1, None
        elif isinstance(hdr, str) and hdr.strip():
            sec, prompt = sec + 1, hdr.strip()
        elif var == "misophonia_overreact":      # standalone questions, no shared stem
            sec, prompt = sec + 1, None
        text = strip_html(r["Field Label"])
        if r["Field Type"] == "yesno":            # REDCap yesno: 1 = Yes, 0 = No
            opts = {0: "No", 1: "Yes"}
        else:
            opts = {int(a): b.strip() for a, b in
                    (p.split(",", 1) for p in r["Choices, Calculations, OR Slider Labels"].split("|"))}
        for v, lab in opts.items():
            rows.append([T, f"{T}_{sec}", var, inst, None, prompt, text, None, lab, v])
    write(rows, T)


# ---------------------------------------------------------------- estrella key file
def key():
    raw = (CACHE / "estrella_2023" / "key.csv").read_bytes().decode("cp1252")
    from io import StringIO
    return pd.read_csv(StringIO(raw)).set_index("Name")


def codes(values):
    parts = re.split(r",\s*(?=\d+=)", values.strip())
    return {int(a): b.strip() for a, b in (p.split("=", 1) for p in parts)}


def psq18():
    T = "estrella_2023_psq18"
    k = key()
    inst = "Short-Form Patient Satisfaction Questionnaire (PSQ-18)"
    # Full Survey.pdf (OSF yxju6), section 4a, read from its pdftotext -layout output
    # (.cache/estrella_2023/full.txt). The study's own wording: RAND's form speaks of
    # medical care in general, this study asks about care for joint hypermobility.
    full = re.sub(r"\s+", " ", (CACHE / "estrella_2023" / "full.txt").read_text())
    a = full.index("On the following pages are some things people say about medical care.")
    instr = full[a:full.index(" i. How strongly", a)]
    assert instr.endswith("received for joint hypermobility."), instr
    rows = []
    for b in (1, 2, 3):
        for j in range(1, 7):
            src = f"psq18_{b}_{j}"
            q, stmt = k.loc[src, "Label"].split(" - ", 1)
            assert q == "How strongly do you agree or disagree with each of the following statements?"
            for v, lab in codes(k.loc[src, "Values"]).items():
                rows.append([T, f"{T}_1", f"psq18_{(b - 1) * 6 + j}", inst,
                             instr + "\n" + q, None, stmt.strip(), None, lab, v])
    write(rows, T)


def hakim5():
    T = "estrella_2023_hakim5"
    k = key()
    inst = "Five-part questionnaire for joint hypermobility (Hakim & Grahame 5PQ)"
    rows = []
    for i in range(1, 6):
        src = f"inclusion_hakim5_{i}"
        instr, q = k.loc[src, "Label"].split(" - ", 1)
        assert instr == "Please respond to the five questions below to the best of your ability."
        for v, lab in codes(k.loc[src, "Values"]).items():
            rows.append([T, f"{T}_1", f"hakim5_{i}", inst, instr, None, q.strip(), None, lab, v])
    write(rows, T)


# ---------------------------------------------------------------- CAB
def cab():
    T = "robie_2022_cab"
    _, m = pyreadstat.read_sav(str(CACHE / "robie_2022_cab" / "merge.sav"), metadataonly=True)
    inst = ("Counterproductive Academic Behavior (CAB) items (Holtrop et al. 2014, "
            "from Hakstian et al. 2002)")
    # The descriptive text (tag Q0) that opens the qsf block "Counter-productive
    # academic behaviour items", ahead of Q126..Q150. Several blocks reuse the tag
    # Q0, so select by block; identical in all five condition .qsf files.
    qsf = json.load(open(CACHE / "robie_2022_cab" / "cond1.qsf", encoding="utf-8"))
    qs = {e["Payload"]["QuestionID"]: e["Payload"] for e in qsf["SurveyElements"]
          if isinstance(e.get("Payload"), dict) and "QuestionText" in e["Payload"]}
    bl = [e for e in qsf["SurveyElements"] if e["Element"] == "BL"][0]["Payload"]
    bl = bl.values() if isinstance(bl, dict) else bl
    blk = [b for b in bl if b.get("Description") == "Counter-productive academic behaviour items"][0]
    ids = [x["QuestionID"] for x in blk["BlockElements"] if x.get("Type") == "Question"]
    assert qs[ids[0]]["DataExportTag"] == "Q0" and qs[ids[1]]["DataExportTag"] == "Q126"
    instr = qs[ids[0]]["QuestionText"].strip()
    rows = []
    for k_, i in enumerate(range(126, 151), 1):          # data/robie_2022_response_order.py
        src = f"Q{i}"
        for v, lab in m.variable_value_labels[src].items():
            rows.append([T, f"{T}_1", f"cab_{k_}", inst, instr, None,
                         m.column_names_to_labels[src], None, lab, int(v)])
    write(rows, T)


if __name__ == "__main__":
    dvmsq(); psq18(); hakim5(); cab()
