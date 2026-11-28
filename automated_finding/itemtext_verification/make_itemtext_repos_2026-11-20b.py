#!/usr/bin/env python3
"""Item text for the repos leads 2026-11-20 lane 2 batch (automated_finding Step 3.5, built after the
response tables were final).

    python3 make_itemtext_repos_2026-11-20b.py <src_root> <held_dir>

<src_root> holds one sub-directory per lead number with that deposit's files as downloaded from the
record (file names with non-word characters replaced by '_'). Every builder ties text to the IRW item
code BY NAME: the code is the source column name, or a rename this file re-derives exactly as the
data/<script>.py did (positional codes inside a block are rebuilt from the same column slices).
write() asserts the item set and the resp set equal the staged response table in
automated_finding/irw_output/ exactly.

Tables whose wording may ship (study-authored wording under the deposit licence, or a register `ship`
instrument) go to automated_finding/itemtext_output/. Tables whose wording is a named third-party
instrument or an adapted battery with no located grant (rights register: silence on a named instrument
-> HOLD; domain-swapped batteries are still the instrument) are written to <held_dir> instead, gated the
same way, and kept outside the repo (Dropbox data/itemtext/) so a later clearance is an upload, not a redo.
"""
import csv
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve().parent.parent          # automated_finding/
RESP_DIR = HERE / "irw_output"
OUT_DIR = HERE / "itemtext_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
EN_COLS = [c for c in COLS if c != "language" and not c.endswith("_translated")]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else None
HELD = Path(sys.argv[2]) if len(sys.argv) > 2 else None
BUILT = []


def norm(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def resp_levels(table):
    r = pd.read_csv(RESP_DIR / f"{table}.csv", usecols=["item", "resp"])
    return r, sorted(r["resp"].dropna().unique().tolist())


def build(table, instrument, items, anchors, held, language=None, instructions="", instructions_tr=""):
    """items: {code: text} or {code: (text, text_en)}; anchors {resp: label} or {resp: (label, en)}."""
    resp, levels = resp_levels(table)
    rows = []
    for code, txt in items.items():
        t, t_en = (txt if isinstance(txt, tuple) else (txt, ""))
        for k in levels:
            lab = (anchors or {}).get(k, "")
            o, o_en = (lab if isinstance(lab, tuple) else (lab, ""))
            rows.append({"table": table, "section_id": f"{table}_1", "item": code, "instrument": instrument,
                         "language": language or "", "instructions": norm(instructions) if instructions else "",
                         "section_prompt": "", "item_text": norm(t) if t else "", "correct_response": "",
                         "option_text": norm(o) if o else "", "resp": k,
                         "instructions_translated": norm(instructions_tr) if instructions_tr else "",
                         "section_prompt_translated": "", "item_text_translated": norm(t_en) if t_en else "",
                         "option_text_translated": norm(o_en) if o_en else ""})
    got = {r["item"] for r in rows}
    want = set(resp["item"].astype(str))
    assert got == want, (table, sorted(got ^ want))
    assert {r["resp"] for r in rows} == set(resp["resp"].dropna().unique()), table
    out = (HELD if held else OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{table}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS if language else EN_COLS, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    BUILT.append((table, "held" if held else "ship"))
    print(f"{'HELD ' if held else 'SHIP '}{p.name}: {len(rows)} rows, {len(got)} items")


def sav_labels(lead, pattern):
    f = sorted((SRC / str(lead)).glob(pattern))[0]
    _, m = pyreadstat.read_sav(f, metadataonly=True)
    return {k: norm(v) for k, v in m.column_names_to_labels.items() if v}, m.variable_value_labels


def headers(lead, fname, **kw):
    p = SRC / str(lead) / fname
    d = pd.read_csv(p, nrows=0, **kw) if fname.lower().endswith(".csv") else pd.read_excel(p, nrows=0, **kw)
    return [" ".join(str(c).split()) for c in d.columns]


AGREE5 = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly agree"}


# ------------------------------------------------------------------------------------- SHIP
def saleem():
    """Mendeley djd7xvw6d5 (CC BY 4.0). GAD-7 (register: PHQ/GAD family = ship, Pfizer grant, no permission
    required). Stems are the bracketed text of the seven Google-Form headers; gad1..gad7 in header order,
    exactly as data/saleem_2021_gad7_reopening.py assigns them. The framing is the deposit's own."""
    c = headers(60, "Copy_of_GAD.csv")[7:14]
    items = {f"gad{i}": re.search(r"\[(.*)\]", h).group(1) for i, h in enumerate(c, 1)}
    instr = re.sub(r"\s*\[.*$", "", c[0])
    build("saleem_2021_gad7", "Generalized Anxiety Disorder 7-item scale (GAD-7), Spitzer et al. 2006, framed on the "
          "re-opening of college", items, {0: "Not at all", 1: "Several Days", 2: "More than half the days",
                                           3: "Nearly Every Day"}, held=False, instructions=instr)


def elshanhaby():
    """Mendeley ks69yfk5by (CC BY 4.0). ai_influencer_disclosure_codebook.csv: 'Item wording' per Variable,
    which is the data file's column name and the IRW item code. MC1-3 are study-specific manipulation checks
    (Source: 'Study-specific; based on ...') -> ship. PIA/PSI/BT/PI are adapted from cited published scales
    (Moulard et al. 2015; Chung & Cho 2017; Chaudhuri & Holbrook 2001; Hwang & Zhang 2018) -> held."""
    cb = pd.read_csv(SRC / "87" / "ai_influencer_disclosure_codebook.csv").set_index("Variable")
    anch = {1: "Strongly disagree", 7: "Strongly agree"}
    for table, codes, held, inst in [
            ("elshanhaby_2026_manipulation_check", ["MC1", "MC2", "MC3"], False, "AI-identity manipulation check (study-specific)"),
            ("elshanhaby_2026_ai_authenticity", ["PIA1", "PIA2", "PIA3"], True, "Perceived AI influencer authenticity, adapted from Moulard et al. (2015)"),
            ("elshanhaby_2026_parasocial_interaction", [f"PSI{i}" for i in range(1, 6)], True, "Parasocial interaction, adapted from Chung & Cho (2017)"),
            ("elshanhaby_2026_brand_trust", [f"BT{i}" for i in range(1, 5)], True, "Brand trust, Chaudhuri & Holbrook (2001)"),
            ("elshanhaby_2026_purchase_intention", [f"PI{i}" for i in range(1, 5)], True, "Purchase intention, adapted from Hwang & Zhang (2018)")]:
        build(table, inst, {c: cb.loc[c, "Item wording"] for c in codes}, anch, held=held)


VALERA_EN_P = {
    1: "Do you take part, through the CONEI and APAFA, in drawing up the school's Educational Project?",
    2: "Do you know the vision, mission and pedagogical proposal of the Institutional Educational Project?",
    3: "Do you believe the Institutional Educational Project shows how your children are educated and how their learning is ensured?",
    4: "Have you perceived, through your children, that all the educational activities carried out at the school were planned?",
    5: "Do you take part, through the CONEI and APAFA, in drawing up the annual work plan?",
    6: "Do you believe the activities planned in the annual work plan are the most appropriate?",
    7: "Do you believe the activities scheduled in the annual work plan have been carried out successfully?",
    8: "Do you believe the annual work plan puts into practice the objectives planned in the PEI?",
    9: "Do you believe the distribution of tasks includes all staff according to their responsibilities?",
    10: "Do you believe the distribution of tasks among the administrative staff is in line with their abilities?",
    11: "Do you believe the distribution of tasks among the auxiliary staff is in line with their abilities?",
    12: "Do you believe the distribution of tasks among the cleaning staff is in line with their abilities?",
    13: "Do you believe the management uses the human, financial and material resources the school needs and administers them rationally?",
    14: "Do you believe the management takes action to keep the community united around the institution's objectives?",
    15: "Do you believe management and teaching staff often take part in events from which educational benefits may follow?",
    16: "Do you believe management and teaching staff meet the commitments made to students and parents in a timely way?",
    17: "Do you believe the management's administration is very good with respect to the interests of the school?",
    18: "Do you consider the work the management is doing, in terms of administration, to be efficient?",
    19: "Do you consider, in general terms, that the school's management is efficient?",
    20: "The school's physical facilities are adequate for carrying out educational activities.",
    21: "The material resources (classrooms, offices, computer room and workshops) are equipped with modern, working materials and equipment that allow meaningful learning.",
    22: "The school has properly equipped workshops for all the technical specialities taught.",
    23: "The school has computer equipment for the exclusive use of the school's staff.",
    24: "The school has sound and multimedia equipment and others that support students' learning.",
    25: "The school has sound and multimedia equipment and others that support students' learning.",
    26: "The scheduled content is diversified according to your children's needs.",
    27: "The teachers cover all the scheduled content.",
    28: "Do you believe the content included in the lesson plans is interesting and necessary for your children?",
    29: "The time devoted to covering the scheduled content is sufficient.",
    30: "The curricular content in the technical area meets parents' demands.",
    31: "Do you believe the teaching staff keep to their working hours?",
    32: "Do you believe the teaching staff identify with the work they do?",
    33: "Do you believe the teaching staff keep up to date on pedagogical topics?",
    34: "Do you believe the teacher applies the knowledge acquired with your children?",
    35: "Do you believe the teacher plans their teaching in line with the guidelines of the Institutional Educational Project?",
    36: "Do you believe the teacher prepares their teaching materials for working with your children?",
    37: "Do you believe the teacher prepares each class session to apply in the classroom?",
    38: "Do you believe the teacher follows up teaching activities as planned?",
    39: "Do you believe the teacher reviews their students' tests and other work and guides them to improve?",
    40: "Do you believe the teacher writes assessment reports pointing out achievements, difficulties and proposals for improvement?",
    41: "Do you believe the teacher talks with parents about the students' learning and gives them the corresponding guidance?",
    42: "Do you often talk with the school authorities about your children's learning problems?",
    43: "Do you often talk with the school's teachers about your children's learning problems?",
    44: "Do you feel the school considers you a strategic ally?",
    45: "Do you believe the school contributes to solving problems that affect your children, such as gangs or drug addiction?",
    46: "Do you attend the parents' school workshops on drug addiction?",
    47: "Do you attend the parents' school workshops on gangs?",
    48: "Do you attend the parents' school workshops on AIDS?",
    49: "Do you believe there is active participation among management, teachers, students and parents in events for the school and the community?",
    50: "Do you believe there is initiative to carry out activities for the development of the Mi Perú community?",
    51: "The school's students carry out work for the benefit of the community.",
}
VALERA_EN_S = {
    1: "Do you receive information from your classmates who represent you on the CONEI about the planning of the school's educational activities?",
    2: "Do you think students' opinions, through their representatives on the CONEI, are taken into account in planning the school's activities?",
    3: "Do you consider the educational activities carried out by the school to be the most appropriate?",
    4: "Do you identify with the activities scheduled by the school?",
    5: "Do you consider the activities planned in the annual work plan to be the most appropriate?",
    6: "Do you consider the activities scheduled in the annual work plan to have been carried out as planned?",
    7: "The school has up-to-date organisation charts posted where the whole school can see them.",
    8: "Do you consider the distribution of tasks to include all staff according to their responsibilities?",
    9: "Do you consider the distribution of tasks among the administrative staff to be in line with their abilities and responsibilities?",
    10: "Do you consider the distribution of tasks among the auxiliary staff to be in line with their abilities and responsibilities?",
    11: "Do you consider the distribution of tasks among the cleaning staff to be in line with their abilities and responsibilities?",
    12: "Do you consider the distribution of tasks among the teaching staff to be in line with their abilities and responsibilities?",
    13: "Do you consider that the management handles the human, financial and material resources the school needs and administers them rationally?",
    14: "Do you consider that the management implements strategies to keep the community united around the institution's objectives?",
    15: "Do you consider that management and teaching staff often take part in events from which educational benefits may follow?",
    16: "Do you consider that management and teaching staff meet the commitments made to students and parents in a timely way?",
    17: "Do you consider the management's administration to be efficient, effective and timely with respect to the school's interests?",
    18: "Do you consider the work the management is doing, in terms of administration, to be efficient and effective?",
    19: "Do you consider, in general terms, that the school's management is efficient?",
    20: "Do you consider the school's physical facilities adequate for carrying out educational activities?",
    21: "Do you consider that the material resources (classrooms, offices, computer room and workshops) are equipped with modern, working materials and equipment that allow meaningful learning?",
    22: "Do you consider that the school has properly equipped workshops for all the technical specialities taught?",
    23: "Do you consider that the school has computer equipment for the exclusive use of the school's staff?",
    24: "Do you consider that the school has sound and multimedia equipment and others that support students' learning?",
    25: "Do you consider that the school has innovative classrooms and an up-to-date library?",
    26: "Do you consider the scheduled content to be diversified according to students' needs and demands?",
    27: "Do you consider that all the scheduled content gets covered?",
    28: "Do you consider the complexity of the content covered to be the most appropriate for the students?",
    29: "Do you consider that the school community feels the content in the lesson plans is of interest and necessary to them?",
    30: "Do you consider the time devoted to covering the scheduled content to be adequate?",
    31: "Do you consider that the technical-area curricular content taught meets the requirements of students and parents?",
    32: "Do you consider that your teachers keep fully to their working hours?",
    33: "The teacher starts classes at the time set in the timetable.",
    34: "When they miss a class, they make it up on another day.",
    35: "They use teaching resources (transparencies, board, audiovisual and computer media, etc.) that help in understanding the content.",
    36: "Do you consider that your teachers identify with the work they do?",
    37: "Do you consider that your teachers plan the work areas and academic units in line with what is planned in the school's educational project?",
    38: "Do you consider that your teachers prepare enough educational resources and materials in advance for work with the students?",
    39: "Do you consider that your teachers prepare each work session or learning experience, including the design of tests and exercises?",
    40: "Do you consider that your teachers offer their students additional support in all kinds of learning activities?",
    41: "Do you consider that your teachers review their students' tests and other work and support them by guiding them on any shortcomings they find?",
    42: "Do you consider that your teachers write assessment reports pointing out achievements, difficulties and proposals for improvement?",
    43: "Do you consider that your teachers talk with their students to inform them about their academic performance and give them the corresponding guidance?",
    44: "They keep you informed about the various events the school holds.",
    45: "Do you consider that the school organises seminars or workshops that help prevent drug and gang problems among its students?",
    46: "Do you consider that the school organises talks on the prevention of sexually transmitted diseases among its students?",
    47: "Do you consider that the school builds strategic ties with other institutions to carry out prevention activities on sexual abuse and other issues?",
    48: "Do you consider that the school extends to the community the benefits of its relations with other institutions?",
    49: "Do you think there is active participation among management, teachers, students and parents in events for the school and the community?",
    50: "Do you consider that there is initiative to carry out activities for the development of the community?",
    51: "Have the school's technical areas carried out any social-outreach work for students and parents?",
}


def valera():
    """Zenodo 22677 (parents) and 22674 (students), CC0. Valera-Gálvez (2012) thesis questionnaires, Spanish,
    written for this school (CONEI/APAFA, Mi Perú): study-authored -> ship under CC0. Stems are the SPSS
    variable labels keyed by the SPSS name, which is the IRW item code (students' 'tem14' -> Item14, as in the
    data script). No value labels in either .sav: the 1-5 points are unlabelled (option_text blank). English
    in *_translated is IRW's own."""
    for lead, who, en in [(103, "parents", VALERA_EN_P), (147, "students", VALERA_EN_S)]:
        lab, _ = sav_labels(lead, "*.sav")
        lab = {("Item14" if k == "tem14" else k): v for k, v in lab.items()}
        for dim in ["institutional", "administrative", "pedagogical", "community"]:
            t = f"valera_2012_{who}_{dim}"
            codes = sorted(pd.read_csv(RESP_DIR / f"{t}.csv", usecols=["item"])["item"].unique(), key=lambda x: int(x[4:]))
            build(t, f"Perception of the educational service quality of a Ventanilla school, {who} form, {dim} dimension "
                     f"(Valera-Gálvez 2012)", {c: (lab[c], en[int(c[4:])]) for c in codes}, {}, held=False, language="Spanish")


OSTOS_EN = {
    1: "The principal inspires little trust in the school.", 2: "The principal takes on little responsibility in difficult situations.",
    3: "The principal communicates decisions through orders.", 4: "The principal shows little respect for the rules of coexistence.",
    5: "The principal acts with partiality in the school.", 6: "The principal asks for help to solve problems.",
    7: "The principal achieves little communication with parents.", 8: "The principal communicates through other people.",
    9: "The principal is tolerant and flexible when parents exercise their free right to expression or opinion.",
    10: "The principal takes on and shares responsibilities with the members of the APAFA.",
    11: "The principal delegates power within the school.", 12: "The principal shares ideas and actions, strengthening the parents' work.",
    13: "The principal develops cooperative relations with parents.",
    14: "The principal properly resolves the interpersonal conflicts that arise within the school.",
    15: "The principal takes on his or her responsibility and considers that every member of the institution should take on theirs.",
    16: "The principal makes assertive decisions in line with the school's reality.",
    17: "The principal takes into account the successful experiences of teachers and parents.",
    18: "The principal delegates tasks to outstanding parents, setting them new challenges.",
    19: "The principal gives recognition to parents for good actions, ideas, initiatives and improvements that benefit the school.",
    20: "The principal recognises and motivates the work of staff and parents more.",
}


def ostos():
    """Zenodo 20795, CC0. Ostos-De-la-Cruz (2010) thesis: leadership items Item1-20 written for the principals of
    network 04 (APAFA references) -> study-authored, ship; anchors from the SPSS value labels (1 = Totalmente de
    Acuerdo .. 5 = Totalmente en desacuerdo, as labelled). Service quality C1-C40 reproduces SERVQUAL's
    dimensions and several of its items in Spanish ('Cuando su Institución Educativa promete hacer algo en cierto
    tiempo lo hace') -> adapted named instrument, held. English is IRW's own."""
    lab, vl = sav_labels(104, "*.sav")
    a1 = {int(k): v for k, v in vl["Item1"].items()}
    en1 = {1: "Strongly agree", 2: "Agree", 3: "Indifferent", 4: "Disagree", 5: "Strongly disagree"}
    build("ostos_2010_principal_leadership", "Principal leadership style as perceived by parents (Ostos-De-la-Cruz 2010)",
          {f"Item{i}": (lab[f"Item{i}"], OSTOS_EN[i]) for i in range(1, 21)}, {k: (a1[k], en1[k]) for k in a1},
          held=False, language="Spanish")
    a2 = {int(k): v for k, v in vl["C1"].items()}
    en2 = {1: "Deficient", 2: "Bad", 3: "Fair", 4: "Good", 5: "Excellent"}
    build("ostos_2010_service_quality", "Educational service quality, SERVQUAL-based (Ostos-De-la-Cruz 2010)",
          {f"C{i}": lab[f"C{i}"] for i in range(1, 41)}, {k: (a2[k], en2[k]) for k in a2}, held=True, language="Spanish")


# ------------------------------------------------------------------------------------- HELD
def from_headers(table, inst, lead, fname, cols, codes, anchors, language=None, bracket=False, **kw):
    hs = headers(lead, fname, **kw)
    items = {}
    for col, code in zip(cols, codes):
        h = hs[col] if isinstance(col, int) else col
        items[code] = re.search(r"\[(.*)\]", h).group(1) if bracket else h
    build(table, inst, items, anchors, held=True, language=language)


def sreen():
    """Mendeley 7pwhtgfn9f. Headers are the English statements; codes rebuilt from the same column positions as
    data/sreen_2017_green_purchase.py. TPB blocks are adapted from Ajzen-style items, collectivism and long-term
    orientation are CVSCALE (Yoo, Donthu & Lenartowicz 2011; register: hold), the rest adapted -> all held."""
    pos = [("att", [4, 5, 6, 7]), ("sn", [8, 9, 10, 23]), ("pbc", [11, 12, 13, 14]), ("pi", [15, 16, 17]),
           ("col", [18, 19, 20, 21, 22]), ("lto", [24, 25, 26, 27, 28]), ("mno", [29, 30, 31, 32]), ("ek", [33, 34, 35, 36, 37])]
    tab = {"att": "attitude", "sn": "subjective_norm", "pbc": "perceived_behav_control", "pi": "purchase_intention",
           "col": "collectivism", "lto": "long_term_orientation", "mno": "man_nature_orientation", "ek": "environmental_knowledge"}
    for code, cols in pos:
        from_headers(f"sreen_2017_{tab[code]}", f"{tab[code].replace('_', ' ')} (Sreen et al. 2018)", 47,
                     "Indian_consumer_green_purchase_Responses_1_.xlsx", cols, [f"{code}{i}" for i in range(1, len(cols) + 1)],
                     {}, sheet_name="Form Responses 1")


def ilieva():
    """Mendeley yb262txrvn. Bracketed statements in the coded CSV headers; codes by position within each prefix
    block (data/ilieva_2023_ewallet_bulgaria.py). TAM/UTAUT battery adapted to e-wallets -> held."""
    hs = headers(66, "E-Wallets_Attitude_Online_Survey_Dataset_Coded_EN.csv", sep=";", encoding="cp1252")
    for code, p, t in [("pu", "Perceived Usefulness", "perceived_usefulness"), ("peou", "Perceived Easy of Use", "perceived_ease_of_use"),
                       ("si", "Social Influence", "social_influence"), ("fc", "Facilitating Conditions", "facilitating_conditions"),
                       ("lc", "Lifestyle Compatibility", "lifestyle_compatibility"), ("pt", "Perceived Trust", "perceived_trust"),
                       ("int", "Intention to Use e-Wallet", "intention_to_use"), ("ad", "Adoption of e-Wallet", "adoption")]:
        cols = [h for h in hs if h.startswith(p + " [")]
        build(f"ilieva_2023_{t}", f"{p} (TAM/UTAUT-based, adapted to e-wallets; Ilieva et al. 2023)",
              {f"{code}{i}": re.search(r"\[(.*)\]", h).group(1) for i, h in enumerate(cols, 1)}, AGREE5, held=True)


def lie():
    """Zenodo 24362742. Headers are the statements; blocks as data/lie_2026_ewallet_intention.py. TAM-based -> held."""
    hs = headers(71, "Study_of_Important_Factors_Affecting_Intentions_in_using_E-Wallet_for_Online_Transactions_Responses_.xlsx")
    for code, sl, t in [("pu", slice(5, 11), "perceived_usefulness"), ("peou", slice(11, 16), "perceived_ease_of_use"),
                        ("pr", slice(16, 21), "perceived_risk"), ("int", slice(21, 27), "intention_to_use")]:
        build(f"lie_2026_{t}", f"{t.replace('_', ' ')} (TAM-based, Lie & Utomo 2026)",
              {f"{code}{i}": h for i, h in enumerate(hs[sl], 1)}, {}, held=True)


def thai():
    """figshare 15167982. Bracketed statements; numbered within each construct; TAM-based -> held."""
    hs = headers(122, "database_for_ewallet_adoption_in_malaysia.xlsx")
    for code, p, t in [("peou", "1. Perceived Ease of Use", "perceived_ease_of_use"), ("pu", "2. Perceived Usefulness", "perceived_usefulness"),
                       ("pr", "3. Perceived Risk", "perceived_risk"), ("si", "4. Social Influence", "social_influence"),
                       ("gs", "5. Government Support", "government_support")]:
        cols = [h for h in hs if h.startswith(p + " [")]
        build(f"thai_2021_{t}", f"{p[3:]} (TAM-based e-wallet adoption, Thai 2021)",
              {f"{code}{i}": re.sub(r"^\d+\.\s*", "", re.search(r"\[(.*)\]", h).group(1)) for i, h in enumerate(cols, 1)}, {}, held=True)


def nguyen():
    """Mendeley pgxcjwcpsg. Codebook.xlsx 'Statements' keyed by Variable (= item code). Administered in
    Vietnamese (Questionnaire_VN.docx); the authors' English is shipped as the stand-in (fallback). Adapted
    green-marketing batteries with no located grant -> held."""
    cb = pd.read_excel(SRC / "110" / "Codebook.xlsx").set_index("Variable")
    for t, p in [("eco_label_info_quality", "ELIQ"), ("perceived_greenwashing", "PGW"), ("consumer_effectiveness", "PCE"),
                 ("price_consciousness", "PC"), ("green_trust", "GT"), ("green_purchase_intention", "GPI")]:
        codes = [c for c in cb.index if re.fullmatch(p + r"\d+", str(c))]
        build(f"nguyen_2026_{t}", cb.loc[codes[0], "Construct / definition"], {c: cb.loc[c, "Statements"] for c in codes},
              AGREE5, held=True, language="Vietnamese")


def kumar():
    """Mendeley b9hdy2swyy. Data.xlsx Sheet2: code -> statement (the sheet's header row is itself the first pair).
    TPB-based adapted battery -> held."""
    s2 = pd.read_excel(SRC / "112" / "Data.xlsx", sheet_name="Sheet2", header=None)
    lab = {norm(a): norm(b) for a, b in s2.values if str(a) != "nan"}
    for t, p in [("attitude", "AT"), ("subjective_norm", "SN"), ("perceived_behav_control", "PBC"), ("eo", "EO"),
                 ("environmental_concern", "EC"), ("green_purchase_intention", "GPI"), ("green_purchase_behavior", "GPB")]:
        table = f"kumar_2022_gp_{t}"
        codes = pd.read_csv(RESP_DIR / f"{table}.csv", usecols=["item"])["item"].unique()
        build(table, f"{t.replace('_', ' ')} (Kumar 2022, TPB-based)", {c: lab[c] for c in codes}, {}, held=True)


def ji():
    """Mendeley 687vv29wsk. SPSS variable labels 'HC1.<Chinese statement>'; code prefix stripped. Mindful
    consumption facets follow the published Mindful Consumption scale; others adapted -> held. No English yet."""
    lab, _ = sav_labels(114, "*.sav")
    for t in ["health_consciousness", "perceived_behav_control", "ethical_identity", "green_purchase_intention",
              "mc_caring_others", "mc_caring_environment", "mc_temperance"]:
        table = f"ji_2024_{t}"
        codes = pd.read_csv(RESP_DIR / f"{table}.csv", usecols=["item"])["item"].unique()
        build(table, f"{t} (Ji 2024)", {c: re.sub(r"^[A-Z]+\d+[.．]\s*—?", "", lab[c]) for c in codes},
              {}, held=True, language="Chinese")


def samaranayake():
    """Dataverse CXL7FF. SPSS labels 'Q1a Writing math quiz' -> situation after the code; value labels give the
    1-10 anchors. An adaptation of the sMARS (named instrument, no grant located) -> held."""
    lab, vl = sav_labels(168, "*.sav")
    anch = {int(k): v for k, v in vl["Q1a"].items()}
    for t, pre in [("math_test_anxiety", "Q1"), ("math_task_anxiety", "Q2")]:
        table = f"samaranayake_2026_{t}"
        codes = pd.read_csv(RESP_DIR / f"{table}.csv", usecols=["item"])["item"].unique()
        build(table, "Math anxiety situations adapted from the sMARS (Samaranayake 2026)",
              {c: re.sub(r"^Q\w+\s+", "", lab[c]) for c in codes}, anch, held=True)


def mccall():
    """figshare 31976897 (CC BY). SPSS variable labels are English renderings of a German administration (no
    German wording in the deposit) -> fallback: English in the base fields, language German. BFI-10 (register:
    block), Connectedness to Nature Scale (Mayer & Frantz 2004), Climate Anxiety Scale (Clayton & Karazsia 2020),
    the 10-item anxiety short scale -> all held."""
    lab, vl = sav_labels(160, "*.sav")
    for t, pre, n0, n1, a in [("anxiety", "AE", 1, 10, "AE1"), ("bfi10", "P", 1, 10, "P1"), ("connectedness_to_nature", "NV", 2, 15, "NV2"),
                              ("climate_anxiety", "KA", 1, 13, "KA1")]:
        anch = {int(k): v for k, v in vl.get(a, {}).items()}
        build(f"mccall_2026_{t}", t.replace("_", " "), {f"{pre}{i}": lab[f"{pre}{i}"] for i in range(n0, n1 + 1)}, anch,
              held=True, language="German")


def cetinkaya():
    """figshare 29476802. SPSS labels '[Simply for reasons of curiosity]' for Q13.1-12 (item q13_1..). Travel-motive
    list adapted from the destination-image literature; source not established -> held."""
    lab, _ = sav_labels(162, "*.sav")
    build("cetinkaya_2025_italy_travel_motives", "Motives for visiting Italy (Cetinkaya 2025)",
          {"q13_" + k.split(".")[1]: lab[k].strip("[]") for k in lab if k.startswith("Q13.")}, {}, held=True)


def rahmah():
    """figshare 33071000. Indonesian statement headers; blocks/positions as data/rahmah_2026_wardah_skincare.py.
    Brand experience (Brakus et al. 2009), trust, love and loyalty batteries adapted -> held. No English yet."""
    fn = [p.name for p in (SRC / "85").glob("*.xlsx")][0]
    hs = headers(85, fn)
    for code, sl, t in [("bx", slice(10, 21), "brand_experience"), ("bt", slice(21, 25), "brand_trust"),
                        ("bl", slice(25, 29), "brand_love"), ("loy", slice(29, 33), "brand_loyalty")]:
        build(f"rahmah_2026_{t}", f"{t.replace('_', ' ')} (Rahmah 2026)", {f"{code}{i}": h for i, h in enumerate(hs[sl], 1)},
              {}, held=True, language="Indonesian")


if __name__ == "__main__":
    for f in [saleem, elshanhaby, valera, ostos, sreen, ilieva, lie, thai, nguyen, kumar, ji, samaranayake, mccall,
              cetinkaya, rahmah]:
        f()
    print(len([b for b in BUILT if b[1] == "ship"]), "ship,", len([b for b in BUILT if b[1] == "held"]), "held")
