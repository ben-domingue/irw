#!/usr/bin/env python3
"""Item text for the #3077 zenodo re-mine batch (2026-10-18).

One builder for the whole batch. Every table here is `mapping_basis=data_labels`:
the code -> text tie comes from the source file's own SPSS labels or the deposit's
own codebook/questionnaire, never from position. The per-table `EVIDENCE` string
below is what goes into `itemtext/mapping_verification.csv`, and it names the file
AND the label level that did the tying.

Blocked by `itemtext/instrument_rights_register.csv` and therefore NOT built, even
though the wording was in hand:
  hung_2026_swls        SWLS         block (Ben, 2026-09-09)
  hung_2026_uwes_s      UWES         block (irw#1955)
  hung_2026_grit        GRIT family  block (ratified Ben 2026-09-30)
  nguyen_2024_swemwbs   WEMWBS       block (irw#1945 reserve-a-right test)
  premkumar_2020_olife  O-LIFE       block (ratified Ben 2026-09-30; the register row
                                     is the 42-item Short O-LIFE and this is the
                                     104-item full form, same originator -- blocked
                                     under Ben's standing "be conservative where the
                                     holder's own terms are unclear")
  hu_2026_psqi          PSQI         block
  granwald_2025_shps    SHAPS        block
Not built for lack of text: the granwald_2025_* tables (positional codes, no codebook),
hu_2026_digital_nomad_wellbeing, the rumangkit tables, purizaca (no labels at all).

Run from the repo root. Writes automated_finding/itemtext_output/<table>__items.csv.
"""
from __future__ import annotations

import os
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
RESP_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR",
                               REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COLS = ["table", "section_id", "item", "instrument", "language", "instructions",
        "section_prompt", "item_text", "correct_response", "option_text", "resp",
        "instructions_translated", "section_prompt_translated",
        "item_text_translated", "option_text_translated"]


def zenodo_fetch(record: int, fname: str, sub: str) -> Path:
    d = RAW_ROOT / sub
    p = d / fname
    if not p.exists():
        d.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{record}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def sav(record: int, fname: str, sub: str):
    return pyreadstat.read_sav(zenodo_fetch(record, fname, sub),
                               apply_value_formats=False)


def emit(table: str, instrument: str, stems: dict, options: dict,
         language: str = "", stems_en: dict | None = None,
         options_en: dict | None = None, instructions: str = "") -> None:
    """stems: item -> text. options: item -> {resp: option_text} (text may be "").

    One row per item x response option. The resp set per item is taken from the
    staged response CSV, so the join keys cannot drift from the shipped table.
    """
    resp_csv = RESP_DIR / f"{table}.csv"
    assert resp_csv.exists(), resp_csv
    r = pd.read_csv(resp_csv, usecols=["item", "resp"])
    by_item = {i: sorted(g["resp"].unique()) for i, g in r.groupby("item")}
    assert set(by_item) == set(stems), (
        table, sorted(set(by_item) ^ set(stems)))

    rows = []
    for item in sorted(by_item):
        for resp in by_item[item]:
            rows.append({
                "table": table,
                "section_id": f"{table}_1",
                "item": item,
                "instrument": instrument,
                "language": language,
                "instructions": instructions,
                "section_prompt": "",
                "item_text": stems[item],
                "correct_response": "",
                "option_text": options.get(item, {}).get(resp, ""),
                "resp": resp,
                "instructions_translated": "",
                "section_prompt_translated": "",
                "item_text_translated": (stems_en or {}).get(item, ""),
                "option_text_translated": (
                    (options_en or {}).get(item, {}).get(resp, "")),
            })
    t = pd.DataFrame(rows, columns=COLS)
    if not language:                      # English administration: omit entirely
        t = t.drop(columns=[c for c in COLS if c.endswith("_translated")]
                   + ["language"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{table}__items.csv", index=False)
    print(f"{table}__items.csv: items={t['item'].nunique()} rows={len(t)} "
          f"blank_option_text={(t['option_text'] == '').sum()}")


# --------------------------------------------------------------------- 13859254
# CODEBOOK.docx is a two-column Word table: variable name | description | scoring.
def codebook_13859254() -> dict:
    p = zenodo_fetch(13859254, "CODEBOOK.docx", "10_5281_zenodo_13859254")
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    import re
    cells = []
    for tc in re.findall(r"<w:tc[ >].*?</w:tc>", xml, re.S):
        txt = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", tc))
        cells.append(" ".join(txt.split()))
    # Walk cells in triples (name, description, scoring).
    out = {}
    for i in range(0, len(cells) - 2, 3):
        name = cells[i].replace(" ", "")
        out[name] = {"desc": cells[i + 1], "scoring": cells[i + 2]}
    return out


NGUYEN_ANCHORS = {
    "freq": {1: "Never", 2: "Rarely", 3: "Sometimes", 4: "Usually", 5: "Always"},
    "agree": {1: "Strongly Disagree", 2: "Disagree", 3: "Undecided", 4: "Agree",
              5: "Strongly agree"},
    "time": {1: "None of the Time", 2: "Rarely", 3: "Some of the time",
             4: "Often", 5: "All of the time"},
}
NGUYEN_TABLES = {
    "nguyen_2024_helia": (
        "Health Literacy Instrument for Adults (HELIA)", "freq",
        [f"Re{i}" for i in (1, 2, 3, 4)] + [f"Atl{i}" for i in range(1, 7)]
        + [f"Und{i}" for i in range(1, 8)] + [f"App{i}" for i in range(1, 5)]
        + [f"DM{i}" for i in range(1, 13)]),
    "nguyen_2024_eheals": (
        "eHealth Literacy Scale (eHEALS)", "agree",
        [f"EHL{i}" for i in range(1, 9)]),
    "nguyen_2024_sleep_hygiene": (
        "Sleep hygiene behaviour items", "time", ["SHI1", "SHI2", "SH3"]),
}
# The codebook spells three variables differently from the data file.
NGUYEN_CODEBOOK_ALIAS = {"Re2": "Re2", "SHI1": "SH1", "SHI2": "SH2", "SH3": "SH3"}
NGUYEN_EVIDENCE = (
    "Stems and 1-5 anchor wording from the deposit's own CODEBOOK.docx, a Word table "
    "mapping each SPSS variable NAME to its description and its scoring labels; the "
    "item codes are the data file's own column names, matched to the codebook by name "
    "rather than by position. The codebook writes the three sleep-hygiene variables "
    "SH1/SH2/SH3 where the data file writes SHI1/SHI2/SH3; that rename is the only "
    "name-level adjustment and is applied explicitly in the builder."
)


def build_nguyen() -> None:
    cb = codebook_13859254()
    for table, (instrument, anchor, items) in NGUYEN_TABLES.items():
        stems_en = {}
        for it in items:
            key = NGUYEN_CODEBOOK_ALIAS.get(it, it)
            assert key in cb, (table, it, key)
            stems_en[it] = cb[key]["desc"]
        opts_en = {it: dict(NGUYEN_ANCHORS[anchor]) for it in items}
        emit(table, instrument, stems_en, opts_en,
             language="Persian", stems_en=None, options_en=None)
        # Persian administration, English-only codebook: the English goes in the base
        # fields and the _translated fields stay empty. See itemtext_standard.md,
        # "The fallback, and what `language` holds in it".


# --------------------------------------------------------------------- 18113188
def build_hung() -> None:
    d, m = sav(18113188, "522English.sav", "10_5281_zenodo_18113188")
    items = ["GM1R", "GM2R", "GM3R", "GM4F", "GM5F", "GM6F"]
    stems = {i: " ".join(m.column_names_to_labels[i].split()) for i in items}
    # The file's value labels are ONE generic frequency set ("The action or event never
    # happens" ... "every time") attached identically to all 40 variables, including the
    # agree/disagree instruments. That cannot be the wording a mindset item was answered
    # on, so option_text is left blank rather than publishing it.
    emit("hung_2026_growth_mindset",
         "Implicit theories of intelligence (growth mindset) items",
         stems, {}, language="Chinese")


# --------------------------------------------------------------------- 3956134
PREMKUMAR = {
    "premkumar_2020_lee": ("Level of Expressed Emotion (LEE)",
                           [f"LEE{i:02d}" for i in range(1, 39)]),
    "premkumar_2020_bpaq": ("Buss-Perry Aggression Questionnaire (BPAQ)",
                            [f"Buss{i:02d}" for i in range(1, 30)]),
    "premkumar_2020_dass21": ("Depression Anxiety Stress Scales-21 (DASS-21)",
                              [f"DASS{i:02d}" for i in range(1, 22)]),
}
PREMKUMAR_EVIDENCE = (
    "Stems from the SPSS variable labels of the deposit's own "
    "'Schizotypy, depression, aggression and perceived EE - data sharing.sav'; the item "
    "codes are that file's own column names, so code and text come from the same row of "
    "the same file and nothing is matched by position. Value-label level checked too and "
    "it differs per instrument: LEE carries 1-4 Untrue..True on all 38 items and DASS-21 "
    "carries its 0-3 anchors on all 21, so both ship their option_text; the 29 Buss "
    "items carry no value labels at all, so premkumar_2020_bpaq ships blank option_text "
    "rather than reconstructing the published 1-7 anchors."
)

# The deposit's SPSS label for DASS value 3 is a copy-paste error: it is the value-2
# label with the real value-3 anchor appended to it, unseparated. Stripping the
# value-2 label off the front recovers the canonical anchor exactly, so the repair is
# deterministic and reversible rather than an invention. Asserted, not assumed.
def _fix_dass(opts: dict) -> dict:
    two, three = opts[2], opts[3]
    assert three.startswith(two) and len(three) > len(two), (two, three)
    return {**opts, 3: three[len(two):]}


def build_premkumar() -> None:
    d, m = sav(3956134,
               "Schizotypy, depression, aggression and perceived EE - data sharing.sav",
               "10_5281_zenodo_3956134")
    vvl = m.variable_value_labels or {}
    assert not any(c in vvl for c in PREMKUMAR["premkumar_2020_bpaq"][1]), \
        "Buss value labels appeared; revisit the blank option_text decision"
    for table, (instrument, items) in PREMKUMAR.items():
        stems = {}
        for i in items:
            lab = " ".join((m.column_names_to_labels[i] or "").split())
            # LEE stems are deposited in brackets; Buss/DASS carry a leading number.
            lab = lab.strip("[]").strip()
            for pre in (f"{int(i[-2:])})", f"{int(i[-2:])}."):
                if lab.startswith(pre):
                    lab = lab[len(pre):].strip()
            stems[i] = lab
        opts = {}
        for i in items:
            if i in vvl:
                o = {int(k): v for k, v in vvl[i].items()}
                opts[i] = _fix_dass(o) if i.startswith("DASS") else o
        emit(table, instrument, stems, opts)


# --------------------------------------------------------------------- 7394999
KARAS_ITEMS = [f"P2.{i}" for i in range(1, 18)]
KARAS_PL_EN = {
    "P2.1": "Buying products made abroad is wrong.",
    "P2.2": "A real Pole should buy products made in this country.",
    "P2.3": ("We should buy products made in Poland instead of letting other "
             "countries get rich off us."),
    "P2.4": ("Poles should not buy products made abroad, because it hurts Polish "
             "business and causes unemployment."),
    "P2.5": ("Poles should always buy products made in Poland rather than imported "
             "products."),
    "P2.6": "Polish products above all else!",
    "P2.7": ("Poles who buy products made abroad are responsible for unemployment in "
             "Poland."),
    "P2.8": "Buying products made abroad is un-Polish.",
    "P2.9": "Only products that are not available in Poland should be imported.",
    "P2.10": ("From other countries we should buy only those products that we cannot "
              "produce in our own country."),
    "P2.11": "It is always better to buy Polish products.",
    "P2.12": ("Products made abroad should be taxed heavily to limit their import into "
              "Poland."),
    "P2.13": ("In the long run it may turn out to be more expensive, but I prefer to "
              "buy Polish products."),
    "P2.14": ("Trading in and buying products made abroad should be limited to cases "
              "of necessity."),
    "P2.15": "All imports should be subject to control.",
    "P2.16": ("Foreign countries should be forbidden from putting foreign products on "
              "our market."),
    "P2.17": ("One should buy Polish products, because they provide employment for "
              "Poles."),
}
KARAS_EVIDENCE = (
    "Stems and 1-7 anchor wording from the SPSS variable labels and value labels of the "
    "deposit's own Etnocentryzm_Baza_PL.sav / Ethnocentrism_Data_ENG.sav; both label "
    "levels present for all 17 items in both files, and the item codes are those files' "
    "own column names. Nothing is matched by position -- which matters here, because the "
    "two files put different CETSCALE statements at the same code (PL P2.1 is 'buying "
    "products made abroad is wrong' where EN P2.1 is 'British people should always buy "
    "British-made products'), so a positional mapping would have been wrong."
)


def build_karas() -> None:
    _, mpl = sav(7394999, "Etnocentryzm_Baza_PL.sav", "10_5281_zenodo_7394999")
    _, men = sav(7394999, "Ethnocentrism_Data_ENG.sav", "10_5281_zenodo_7394999")
    pl_opts = {int(k): v for k, v in mpl.variable_value_labels["P2.1"].items()}
    en_opts = {int(k): v for k, v in men.variable_value_labels["P2.1"].items()}
    emit("karas_2022_cetscale_pl", "Consumer Ethnocentric Tendencies Scale (CETSCALE)",
         {i: " ".join(mpl.column_names_to_labels[i].split()).rstrip(":")
          for i in KARAS_ITEMS},
         {i: dict(pl_opts) for i in KARAS_ITEMS},
         language="Polish",
         stems_en=KARAS_PL_EN,
         # The English anchors are the authors' own, taken from the companion English
         # file's value labels -- the same 7-point agree scale, not an IRW translation.
         options_en={i: dict(en_opts) for i in KARAS_ITEMS})
    emit("karas_2022_cetscale_en", "Consumer Ethnocentric Tendencies Scale (CETSCALE)",
         {i: " ".join(men.column_names_to_labels[i].split()).rstrip(":")
          for i in KARAS_ITEMS},
         {i: dict(en_opts) for i in KARAS_ITEMS})


# --------------------------------------------------------------------- 16745477
MARKOVA_EVIDENCE = (
    "Stems from the 'Variable Lables' sheet and anchor wording from the 'Value Lables' "
    "sheet of the deposit's own variable_codebook.xls, both keyed by variable NAME; the "
    "item codes are the csv's own column headers, matched to the codebook by name. The "
    "one adjustment: the deposit heads MAILS item 24 with the bare name 'MAILS', which "
    "is unusable as a code beside MAILSI2f_23 and MAILSI2f_25, so both the response "
    "table and this item text spell it MAILSI2f_24. The MAILS 0-10 scale labels only "
    "its endpoints, so option_text is blank at 1-9 rather than padded with the number."
)


def build_markova() -> None:
    p = zenodo_fetch(16745477, "variable_codebook.xls", "10_5281_zenodo_16745477")
    xl = pd.ExcelFile(p)
    vl = xl.parse("Variable Lables")
    stems_all = {str(r["variableName"]).strip(): " ".join(str(r["variableLabel"]).split())
                 for _, r in vl.iterrows()}
    vv = xl.parse("Value Lables")
    vv.columns = ["var", "value", "label"]
    vv["var"] = vv["var"].ffill()

    def anchors(var: str) -> dict:
        sub = vv[vv["var"] == var]
        out = {}
        for _, r in sub.iterrows():
            if pd.isna(r["value"]):
                continue
            lab = str(r["label"]).strip()
            # "0-never or not very often" / "10-very often"; bare numbers mean unlabeled.
            if lab.replace(".0", "").isdigit():
                lab = ""
            elif "-" in lab and lab.split("-", 1)[0].isdigit():
                lab = lab.split("-", 1)[1].strip()
            out[int(r["value"])] = lab
        return out

    gaais = ["P1a_1", "P1a_2", "N1a_3", "P1a_4", "P1a_5", "N1a_6", "P1a_7",
             "N1b_8", "N1b_9", "N1b_10", "P1b_11", "P1b_12", "P1b_13",
             "P1c_14", "N1c_15", "P1c_16", "P1c_17", "P1c_18", "N1c_19", "N1c_20"]
    g_opts = anchors("P1a_1")
    emit("markova_2025_gaais",
         "General Attitudes towards Artificial Intelligence Scale (GAAIS)",
         {i: stems_all[i].rstrip(".") + "." for i in gaais},
         {i: dict(g_opts) for i in gaais}, language="Bulgarian")

    mails_src = [c for c in stems_all
                 if c.startswith(("MAILS", "IMAILS")) and "_" in c
                 and c.rsplit("_", 1)[1].isdigit()] + ["MAILS"]
    m_opts = anchors("MAILS2a_1")
    stems = {("MAILSI2f_24" if c == "MAILS" else c):
             stems_all[c].replace("lan- guages", "languages")
                         .replace("deci- sions", "decisions")
                         .replace("intellige", "intelligence")
             for c in mails_src}
    emit("markova_2025_mails", "Meta AI Literacy Scale (MAILS)",
         stems, {i: dict(m_opts) for i in stems}, language="Bulgarian")


# --------------------------------------------------------------------- 10608935
PAQC_EN_STEMS = {
    "PAQ_2": "Active in physical education classes",
    "PAQ_3": "Most frequent activity during school breaks",
    "PAQ_4": "Activity you normally do at lunchtime (before and after eating)",
    "PAQ_5": "How many days did you play before your afternoon snack?",
    "PAQ_6": "How many days did you play after your afternoon snack?",
    "PAQ_7": ("How many times last weekend did you do sports, dance or play games in "
              "which you were very active?"),
    "PAQ_8": "Which of the following statements best describes your last week?",
}
PAQC_EN_OPTS = {
    "activity": {1: "Sitting (talking, reading, doing class work)",
                 2: "Standing or walking around",
                 3: "Running or playing a little",
                 4: "Running and playing quite a bit",
                 5: "Running and playing hard most of the time"},
    "effort": {1: "I did not do it", 2: "Hardly ever", 3: "Sometimes", 4: "Often",
               5: "Always"},
    "days": {1: "None", 2: "Once in the last week", 3: "2-3 times in the last week",
             4: "4 times in the last week", 5: "5 times or more in the last week"},
    "week": {1: ("All or most of my free time was spent doing things that involve "
                 "little physical effort"),
             2: "I sometimes (1 or 2 times) did physical things in my free time",
             3: "I often (3-4 times a week) did physical things in my free time",
             4: ("I quite often (5-6 times in the last week) did physical things in my "
                 "free time"),
             5: ("I very often (7 or more times in the last week) did physical things "
                 "in my free time")},
}
PAQC_OPT_KIND = {"PAQ_2": "effort", "PAQ_3": "activity", "PAQ_4": "activity",
                 "PAQ_5": "days", "PAQ_6": "days", "PAQ_7": "days", "PAQ_8": "week"}
PAQC_EVIDENCE = (
    "Spanish stems from the SPSS variable labels and Spanish 1-5 option wording from the "
    "value labels of the deposit's own Dataset_PAQ-C.sav; both levels present for all "
    "seven shipped items, and the item codes are that file's own column names, so the "
    "tie is name-to-name within one row of one file. The two PAQ-C items whose labels "
    "are present but whose values are the depositor's mean over undeposited sub-parts "
    "(PAQ_1, PAQ_9) are not in the response table and so are not here either."
)


def build_valenciano() -> None:
    d, m = sav(10608935, "Dataset_PAQ-C.sav", "10_5281_zenodo_10608935")
    items = [f"PAQ_{i}" for i in range(2, 9)]
    vvl = m.variable_value_labels
    emit("valenciano_2022_paqc",
         "Physical Activity Questionnaire for Children (PAQ-C)",
         {i: " ".join((m.column_names_to_labels[i] or "").split()) for i in items},
         {i: {int(k): v for k, v in vvl[i].items()} for i in items},
         language="Spanish",
         stems_en=PAQC_EN_STEMS,
         options_en={i: PAQC_EN_OPTS[PAQC_OPT_KIND[i]] for i in items})


# --------------------------------------------------------------------- 15628398
MAHARANI_EVIDENCE = (
    "Stems from Table 1 of the deposit's own "
    "'How UI_UX Design Influences - suppl material - Questionnaire .docx', which "
    "tabulates every question against its item code in its own final column, so the "
    "code -> stem tie is the authors' and nothing is matched by position. The same file "
    "gives the response scale as endpoints only (1 = Sangat Tidak Setuju, 6 = Sangat "
    "Setuju), so option_text carries those two Indonesian anchors and is blank at 2-5. "
    "One code is spelled differently on the two sides: the questionnaire's second "
    "average-order-value row is coded AOV2 where the response workbook heads the same "
    "column AVO2. The item text ships under AVO2, the response table's spelling, so the "
    "join holds; the pairing is unambiguous because AOV1/AOV3/AOV4 line up by name and "
    "AOV2 is the one row left over."
)
# questionnaire code -> response-table code, where the deposit's two files disagree.
MAHARANI_CODE_FIX = {"AOV2": "AVO2"}
MAHARANI_ITEMS = ["VD1", "VD2", "VD3", "VD4", "ND1", "ND2", "ND3", "ND4",
                  "EOU1", "EOU2", "EOU3", "EOU4", "US1", "US2", "US3", "US4",
                  "CR1", "CR2", "CR3", "AOV1", "AVO2", "AOV3", "AOV4",
                  "CLV1", "CLV2", "CLV3", "CLV4"]


def build_maharani() -> None:
    import re
    p = zenodo_fetch(15628398,
                     "How UI_UX Design Influences - suppl material - Questionnaire .docx",
                     "10_5281_zenodo_15628398")
    with zipfile.ZipFile(p) as z:
        xml = z.read("word/document.xml").decode("utf-8", "replace")
    cells = []
    for tc in re.findall(r"<w:tc[ >].*?</w:tc>", xml, re.S):
        txt = re.sub(r"<[^>]+>", "", re.sub(r"</w:p>", "\n", tc))
        cells.append(" ".join(txt.split()))
    # The code cell follows its question cell; pick the question that precedes each code.
    stems = {}
    for i, c in enumerate(cells):
        code = c.strip()
        code = MAHARANI_CODE_FIX.get(code, code)
        if code in MAHARANI_ITEMS and i > 0:
            q = cells[i - 1].strip()
            assert len(q) > 15 and q[0].isupper(), (code, q)
            stems[code] = q
    missing = [c for c in MAHARANI_ITEMS if c not in stems]
    assert not missing, missing
    opts = {i: {1: "Sangat Tidak Setuju", 6: "Sangat Setuju"} for i in MAHARANI_ITEMS}
    opts_en = {i: {1: "Strongly disagree", 6: "Strongly agree"}
               for i in MAHARANI_ITEMS}
    emit("maharani_2025_ecommerce_uiux",
         "UI/UX and e-commerce profitability questionnaire (TAM-based)",
         stems, opts, language="Indonesian", options_en=opts_en)


BUILDERS = [build_nguyen, build_hung, build_premkumar, build_karas,
            build_markova, build_valenciano, build_maharani]


def main() -> None:
    for b in BUILDERS:
        b()


if __name__ == "__main__":
    main()
