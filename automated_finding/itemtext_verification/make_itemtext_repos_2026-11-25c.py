#!/usr/bin/env python3
"""Item text for the repos leads batch 2026-11-25c (automated_finding Step 3.5, built after the
response tables were final).

    python3 make_itemtext_repos_2026-11-25c.py <src_root> [deposit ...]

<src_root> holds one sub-directory per deposit with that deposit's files exactly as downloaded
from the record (names as the record gives them). Each builder below reads the deposit's own
text-bearing file, ties text to the IRW item code BY NAME (the code is the source column name, or
a rename the builder re-derives from data/<script>.py), and writes
automated_finding/itemtext_output/<table>__items.csv. write() asserts the item set and the resp set
equal the staged response table in automated_finding/irw_output/ exactly, so a builder that ties a
stem to the wrong code, drops an item or invents a resp level stops here.

Per-deposit notes (sources, language, rights basis) are in each builder's docstring and in the
table's itemtext_provenance.csv row.
"""
import csv
import os
import re
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent.parent          # automated_finding/
RESP_DIR = HERE / "irw_output"
OUT_DIR = HERE / "itemtext_output"
COLS = ["table", "section_id", "item", "instrument", "language", "instructions", "section_prompt",
        "item_text", "correct_response", "option_text", "resp", "instructions_translated",
        "section_prompt_translated", "item_text_translated", "option_text_translated"]
EN_COLS = [c for c in COLS if c != "language" and not c.endswith("_translated")]


LIVE_DIR = Path(os.environ.get("IRW_LIVE_SETS", "/nonexistent"))   # cached irw_table_sets() for live tables


def resp_levels(table):
    p = RESP_DIR / f"{table}.csv"
    if not p.exists():                        # a live table: its item x resp sets cached from irw_table_sets()
        p = LIVE_DIR / f"{table}.csv"
    r = pd.read_csv(p, usecols=["item", "resp"])
    return r, sorted(r["resp"].dropna().unique().tolist())


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def build(table, instrument, items, anchors, language=None, instructions="", instructions_tr="",
          correct=None):
    """items: {code: text} or {code: (text, text_en)}; anchors: {resp: label} or {resp: (label, en)},
    or a callable code -> such a dict for item-specific anchors. Rows are emitted for every resp
    level observed in the staged table (the gate compares against observed levels)."""
    resp, levels = resp_levels(table)
    rows = []
    for code, txt in items.items():
        t, t_en = (txt if isinstance(txt, tuple) else (txt, ""))
        a = anchors(code) if callable(anchors) else anchors
        for k in levels:
            lab = a.get(k, "") if a else ""
            o, o_en = (lab if isinstance(lab, tuple) else (lab, ""))
            rows.append({"table": table, "section_id": f"{table}_1", "item": code,
                         "instrument": instrument, "language": language or "",
                         "instructions": instructions, "section_prompt": "",
                         "item_text": norm(t) if t else "",
                         "correct_response": (correct or {}).get(code, ""),
                         "option_text": norm(o) if o else "", "resp": k,
                         "instructions_translated": instructions_tr, "section_prompt_translated": "",
                         "item_text_translated": norm(t_en) if t_en else "",
                         "option_text_translated": norm(o_en) if o_en else ""})
    write(table, rows, resp, translated=language is not None)


def write(table, rows, resp, translated):
    got_items = {r["item"] for r in rows}
    want_items = set(resp["item"].astype(str))
    assert got_items == want_items, (table, sorted(got_items ^ want_items))
    assert {r["resp"] for r in rows} == set(resp["resp"].dropna().unique()), table
    cols = COLS if translated else EN_COLS
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{table}__items.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{p.name}: {len(rows)} rows, {len(got_items)} items")


def blocks(script):
    """BLOCKS (table -> source columns) from a data/ script, without running it."""
    src = (HERE.parent / "data" / f"{script}.py").read_text(encoding="utf-8")
    m = re.search(r"^BLOCKS = (\{.*?\n\})", src, re.S | re.M) or \
        re.search(r"^BLOCKS = (\{.*?\})\n", src, re.S | re.M)
    return eval(m.group(1))  # a literal dict in our own repo script


# ---------------------------------------------------------------------------------------------
def herrera(src):
    """Zenodo 10.5281/zenodo.23455377, CC BY 4.0. Spanish administration (Peru). Stems are the
    `enunciado` column of the deposit's diccionario_de_datos.csv, keyed by `codigo`, which is the data
    file's own column name and the IRW item code (data/herrera_2026_market_traders.py keeps it).
    Anchors from the same file's `escala` column. English in *_translated is IRW's own
    (machine_translation)."""
    d = pd.read_csv(Path(src) / "diccionario_de_datos.csv", dtype=str)
    d = d.set_index("codigo")
    esc = {norm(v) for v in d["escala"]}
    assert esc == {"1 = nunca; 2 = casi nunca; 3 = a veces; 4 = casi siempre; 5 = siempre"}, esc
    anchors = {1: ("nunca", "never"), 2: ("casi nunca", "almost never"), 3: ("a veces", "sometimes"),
               4: ("casi siempre", "almost always"), 5: ("siempre", "always")}
    en = {
        "GFN1": "Keeps track of the income of their business.",
        "GFN2": "Properly records the expenses of their business.",
        "GFN3": "Does financial planning for the activities of their business.",
        "GFN4": "Organises the money of their business to cover their economic needs.",
        "CFD1": "Uses digital banking applications to carry out financial transactions.",
        "CFD2": "Uses digital means to make payments or transfers.",
        "CFD3": "Makes use of electronic wallets in their commercial activities.",
        "CFD4": "Uses digital platforms to keep track of their financial movements.",
        "TDF1": "Evaluates different alternatives before making financial decisions.",
        "TDF2": "Analyses the economic consequences before making major expenditures.",
        "TDF3": "Sets aside part of their income for savings.",
        "TDF4": "Manages the money of their business responsibly.",
        "CTD1": "Files their tax returns through online platforms.",
        "CTD2": "Pays their taxes on time.",
        "CTD3": "Uses electronic receipts in their commercial activities.",
        "CTD4": "Carries out tax procedures through digital means.",
        "OCT1": "Properly records the accounting transactions of their business.",
        "OCT2": "Keeps their tax documents in order.",
        "OCT3": "Keeps the payment receipts for their commercial transactions.",
        "OCT4": "Keeps track of the financial information of their business",
        "PTE1": "Plans how they will meet their tax obligations.",
        "PTE2": "Organises their economic activities taking their tax obligations into account.",
        "PTE3": "Assesses possible tax risks in their business.",
        "PTE4": "Seeks to avoid tax contingencies in their commercial activities.",
        "DC1": "Uses some software or digital system to record the transactions of their business.",
        "DC2": "Records their income and expenses electronically.",
        "DC3": "Issues or stores payment receipts by digital means.",
        "DC4": "Uses digital tools to organise the accounting information of their business.",
        "FE1": "Their business is formally registered with SUNAT.",
        "FE2": "Issues payment receipts for the sales they make.",
        "FE3": "Meets the tax obligations required for their commercial activity.",
        "FE4": "Keeps the legal and tax documentation of their business up to date.",
        "TRD1": "Uses digital applications to manage the finances of their business.",
        "TRD2": "Makes or receives payments by electronic means.",
        "TRD3": "Uses digital tools to monitor the financial movements of their business.",
        "TRD4": "Considers that digital technologies have improved the financial administration of their business.",
    }
    names = {
        "herrera_2026_financial_literacy": "Educación financiera (financial literacy): gestión financiera del negocio, comportamiento financiero digital, toma de decisiones financieras",
        "herrera_2026_tax_management": "Gestión tributaria (tax management): cumplimiento tributario digital, organización contable tributaria, planeación tributaria estratégica",
        "herrera_2026_accounting_digitalization": "Digitalización contable (accounting digitalisation), moderator",
        "herrera_2026_business_formalization": "Formalización empresarial (business formalisation), moderator",
        "herrera_2026_digital_finance_transform": "Transformación digital financiera (digital financial transformation), moderator",
    }
    for table, cols in blocks("herrera_2026_market_traders").items():
        items = {c: (d.loc[c, "enunciado"], en[c]) for c in cols}
        build(table, names[table] + "; study-authored questionnaire, Herrera López, Mires Jara & "
              "Puicán Rodríguez 2026", items, anchors, language="Spanish")


def croitoru(src):
    """Zenodo 10.5281/zenodo.23503832, CC BY 4.0. Administered in Romanian; the deposit publishes only
    the English wording (README_codebook.txt, 'items translated from English by back-translation'), so
    the English ships in the base fields as the fallback (text_source=translated_substitute,
    language=Romanian, the English being the depositors' own). Codes CM_1..PERF_4 are the CSV column
    names and the IRW item codes; the README lists each code beside its statement."""
    txt = (Path(src) / "README_codebook.txt").read_text(encoding="utf-8")
    stems = dict(re.findall(r"^((?:CM|CA|AT|SAT|PERF)_\d)\s{2,}(.+?)\s*$", txt, re.M))
    assert len(stems) == 20, len(stems)
    assert "1 = strongly disagree, 2 = disagree, 3 = neither agree nor disagree, 4 = agree, 5 = strongly agree" in txt
    anchors = {1: "strongly disagree", 2: "disagree", 3: "neither agree nor disagree", 4: "agree",
               5: "strongly agree"}
    names = {"croitoru_2026_supervisor_comm": "Manager-employee communication (CM)",
             "croitoru_2026_coworker_comm": "Communication between employees (CA)",
             "croitoru_2026_work_atmosphere": "Atmosphere at work (AT)",
             "croitoru_2026_job_satisfaction": "Job satisfaction (SAT)",
             "croitoru_2026_task_performance": "Task performance (PERF)"}
    for table, cols in blocks("croitoru_2026_workplace_comm").items():
        build(table, names[table] + "; study-authored items, Croitoru, Florea, Diaconeasa & Stanescu 2026",
              {c: stems[c] for c in cols}, anchors, language="Romanian")


def ahmad(src):
    """figshare 10.6084/m9.figshare.35106577, CC BY 4.0. Instrument_EN sheet: one row per item, 'Item
    ID' = the Data_Entry column name = the IRW item code, 'Item text (exactly as shown to
    respondents)', 'Response format', and 'Source or note' = 'Author-written' for every item.
    Administered in English (270) or French (72; cov_language); the French wording is in the
    Bilingual_Instrument_A1 sheet but the schema holds one administered text, so the English ships.
    K1-K6 are scored 0/1 in IRW against the codebook's key (B,C,B,B,B,A): item_text carries the
    question with its four printed options, correct_response the keyed letter, and the 0/1 option
    rows are blank (the source labels no scored level)."""
    f = next(p for p in Path(src).iterdir() if p.suffix == ".xlsx")
    d = pd.read_excel(f, "Instrument_EN", header=3, dtype=str)
    d = d[d["Item ID"].fillna("").str.match(r"^(UR|TR|VP|SE|K)\d+$")].set_index("Item ID")
    assert (d["Source or note"].str.startswith("Author-written")).all()
    text = "Item text (exactly as shown to respondents)"
    agree = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly agree"}
    freq = {1: "Never", 2: "Rarely", 3: "Sometimes", 4: "Often", 5: "Always"}
    fmt = {norm(v) for v in d.loc[d.index.str.match(r"^(UR|TR|SE)"), "Response format"]}
    assert fmt == {"1 Strongly disagree, 2 Disagree, 3 Neutral, 4 Agree, 5 Strongly agree"}, fmt
    assert {norm(v) for v in d.loc[d.index.str.startswith("VP"), "Response format"]} == \
        {"1 Never, 2 Rarely, 3 Sometimes, 4 Often, 5 Always"}
    key = {c: re.search(r"Correct: ([A-D])", d.loc[c, "Response format"]).group(1)
           for c in d.index if c.startswith("K")}
    assert "".join(key[f"K{i}"] for i in range(1, 7)) == "BCBBBA"
    names = {"ahmad_2026_ai_reliance": "AI use and reliance (UR)",
             "ahmad_2026_trust_ai_code": "Trust in AI-generated code (TR)",
             "ahmad_2026_verification_practices": "Verification practices (VP)",
             "ahmad_2026_secure_coding_self_efficacy": "Secure-coding self-efficacy (SE)",
             "ahmad_2026_secure_coding_knowledge": "Secure-coding knowledge check (K)"}
    for table, cols in blocks("ahmad_2026_ai_code_trust").items():
        a = freq if table.endswith("verification_practices") else \
            ({} if table.endswith("knowledge") else agree)
        build(table, names[table] + "; author-written questionnaire, Ahmad 2026",
              {c: d.loc[c, text] for c in cols}, a,
              language="English; French", correct=key if table.endswith("knowledge") else None)



def xlsx_in(src):
    return next(p for p in Path(src).iterdir() if p.suffix == ".xlsx")


def sengarie(src):
    """Zenodo 10.5281/zenodo.23879195, CC BY 4.0. Sheet 'Codebook': Variable (= the 'Anonymized Data'
    column name = the IRW code) beside 'Description / Item' (English). No anchors in the deposit, so
    option_text is blank on every point. Administration language not stated (Indonesian consumers,
    Google Forms): English as deposited, language unset."""
    cb = pd.read_excel(xlsx_in(src), "Codebook", dtype=str).set_index("Variable")
    names = {"sengarie_2026_env_awareness": "Environmental Awareness",
             "sengarie_2026_product_quality": "Perceived Product Quality",
             "sengarie_2026_green_brand_image": "Green Brand Image",
             "sengarie_2026_purchase_intention": "Purchase Intention"}
    for table, cols in blocks("sengarie_2026_sustainable_fashion").items():
        assert set(cb.loc[cols, "Construct"]) == {names[table]}, table
        build(table, names[table] + "; study-authored items, Sengarie & Ratnaputri 2026",
              {c: cb.loc[c, "Description / Item"] for c in cols}, {})


def efawati(src):
    """Harvard Dataverse 10.7910/DVN/DHFHMV, CC0 1.0. Sheet 'codebook': 'Variable code' (= the 'data
    penelitian' column name = the IRW code) beside 'Full item wording'; anchors and section prompts from
    the deposit's 'Supplementary Data 2 - Questionnaire.pdf' (English; administration language not
    stated, Indonesian employees -> language unset)."""
    cb = pd.read_excel(xlsx_in(src), "codebook", header=2, dtype=str)
    cb = cb[cb["Variable code"].fillna("").str.match(r"^(EL|IC|WP)\d+$")].set_index("Variable code")
    anchors = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly agree"}
    names = {"efawati_2026_entrepreneurial_leadership": "Entrepreneurial Leadership",
             "efawati_2026_individual_creativity": "Individual Creativity",
             "efawati_2026_work_performance": "Work Performance"}
    ins = "Please mark (X) for each answer in one of the 1-5 scoring columns."
    for table, cols in blocks("efawati_2026_entrepreneurial_leadership").items():
        build(table, names[table] + "; study-authored items, Efawati, Chaniago, Andriani & Veranita 2026",
              {c: cb.loc[c, "Full item wording"] for c in cols}, anchors, instructions=ins)


def lee(src):
    """Harvard Dataverse 10.7910/DVN/O4E9YN, CC0 1.0. Data.xlsx sheet 'Codebook': Variable (= the Data
    sheet column name = the IRW code), 'English label or item', 'Values and coding' (1 = Strongly
    disagree .. 5 = Strongly agree, asserted for every item). Administration language not stated
    (the record names no paper) -> language unset."""
    cb = pd.read_excel(Path(src) / "Data.xlsx", "Codebook", dtype=str).set_index("Variable")
    names = {"lee_2026_meaning_making": "Meaning-making", "lee_2026_mastery": "Mastery",
             "lee_2026_self_esteem": "Self-esteem", "lee_2026_perceived_control": "Perceived control",
             "lee_2026_trust_in_ai": "Trust in AI", "lee_2026_creepiness": "Creepiness",
             "lee_2026_task_oriented_reliance": "Task-oriented reliance",
             "lee_2026_overreliance": "Overreliance", "lee_2026_ai_avoidance": "AI avoidance"}
    anchors = {1: "Strongly disagree", 2: "Disagree", 3: "Neutral", 4: "Agree", 5: "Strongly agree"}
    for table, cols in blocks("lee_2026_ai_reliance").items():
        assert set(cb.loc[cols, "Construct"]) == {names[table]}, table
        assert {norm(v) for v in cb.loc[cols, "Values and coding"]} == \
            {"1 = Strongly disagree; 2 = Disagree; 3 = Neutral; 4 = Agree; 5 = Strongly agree"}
        build(table, names[table] + " items, Lee 2026 (Adaptive Paradox of AI Reliance)",
              {c: cb.loc[c, "English label or item"] for c in cols}, anchors)


def umoru(src):
    """figshare 10.6084/m9.figshare.35100916, CC BY 4.0. AR_Codebook.xlsx sheet 'Variables': Variable (=
    the public CSV column name = the IRW code), 'Label in SPSS file' (the item wording, identical to
    AR_Studies_Questionnaire.docx), and the value labels. Interviewer-administered; language not stated
    -> unset. Anchor wording from the questionnaire's own section headers (LS: '3 = Undecided';
    SC: '3 = Neither agree nor disagree'), which the codebook abbreviates."""
    cb = pd.read_excel(Path(src) / "AR_Codebook.xlsx", "Variables", dtype=str).set_index("Variable")
    lab = "Label in SPSS file"
    agree_ls = {1: "Strongly disagree", 2: "Disagree", 3: "Undecided", 4: "Agree", 5: "Strongly agree"}
    agree_sc = {1: "Strongly disagree", 2: "Disagree", 3: "Neither agree nor disagree", 4: "Agree", 5: "Strongly agree"}
    diff = {1: "None", 2: "Mild", 3: "Moderate", 4: "Severe", 5: "Extreme"}
    freq = {1: "Never", 2: "Rarely", 3: "Sometimes", 4: "Often", 5: "Always"}
    vals = "Values and value labels (full file)"
    for c in [f"HS{i}" for i in range(1, 7)]:
        assert norm(cb.loc[c, vals]) == "1 = None; 2 = Mild; 3 = Moderate; 4 = Severe; 5 = Extreme", c
    for c in [f"HS{i}" for i in range(7, 17)]:
        assert norm(cb.loc[c, vals]) == "1 = Never; 2 = Rarely; 3 = Sometimes; 4 = Often; 5 = Always", c
    names = {"umoru_2026_life_satisfaction": ("Life satisfaction (Section B)", agree_ls),
             "umoru_2026_social_capital": ("Social relationships / social capital (Section C)", agree_sc),
             "umoru_2026_health_stressors": ("Health stressors (Section D)",
                                             lambda c: diff if int(c[2:]) <= 6 else freq)}
    for table, cols in blocks("umoru_2026_older_farmers").items():
        n, a = names[table]
        build(table, n + ", Umoru, Babalola, Omolayo, Atoyebi, Owoyemi & Okiri 2026",
              {c: cb.loc[c, lab] for c in cols}, a)


def charzynska(src):
    """Zenodo 10.5281/zenodo.24139252, CC BY 4.0. Codebook.csv (';'-separated): Variable (= the Data.csv
    column name = the IRW code), Label (the item wording, prefixed by the scale tag and, for IWAS and
    MWMS, the shared stem), Values. Administered in the languages of 85 cultures; the deposit publishes
    the English master only -> language unset (the cultures are not mapped to languages anywhere in the
    deposit) and the provenance note says so."""
    cb = pd.read_csv(Path(src) / "Codebook.csv", sep=";", dtype=str).set_index("Variable")

    def opts(c):
        out = {}
        for part in re.split(r",\s*(?=\d+ = )", cb.loc[c, "Values (response categories)"].strip()):
            k, v = part.split(" = ", 1)
            out[int(k)] = v.strip()
        return out

    def split(c, prefix_re):
        lab = norm(cb.loc[c, "Label"])
        m = re.match(prefix_re, lab)
        assert m, (c, lab)
        return m.group("stem").strip(), m.group("item").strip()

    t = "charzynska_2026_iwas5"
    stems, items = set(), {}
    for c in blocks("charzynska_2026_work_addiction")[t]:
        st, it = split(c, r"^IWAS\d\. (?P<stem>How often during THE LAST YEAR have you\.\.\.) (?P<item>.+)$")
        stems.add(st); items[c] = it
    assert len(stems) == 1
    build(t, "International Work Addiction Scale, 5-item form (IWAS-5), Atroszko, Charzynska et al.",
          items, lambda c: opts(c), instructions=stems.pop())
    t = "charzynska_2026_uwes3"
    build(t, "Utrecht Work Engagement Scale, 3-item form (UWES-3), Schaufeli et al.",
          {c: split(c, r"^UWES\d\. (?P<stem>)(?P<item>.+)$")[1] for c in blocks("charzynska_2026_work_addiction")[t]},
          lambda c: opts(c))
    t = "charzynska_2026_mwms6"
    stems, items = set(), {}
    for c in blocks("charzynska_2026_work_addiction")[t]:
        st, it = split(c, r"^MWMS-6\. [^:]+: (?P<stem>Why do you or would you put efforts into your current job\?) (?P<item>.+)$")
        stems.add(st); items[c] = it
    assert len(stems) == 1
    build(t, "Multidimensional Work Motivation Scale, 6-item form (MWMS-6; one item per regulation type)",
          items, lambda c: opts(c), instructions=stems.pop())


def sav_labels(path):
    import pyreadstat
    _, m = pyreadstat.read_sav(str(path), metadataonly=True)
    return m


def hung(src):
    """Zenodo 10.5281/zenodo.23951310, CC BY 4.0. SPSS.sav variable labels (English) keyed by the
    column name = the IRW code; no value labels on the items (option_text blank). Administered in
    Chinese; the deposit holds only the English labels -> language=Chinese, fallback shape."""
    m = sav_labels(Path(src) / "SPSS.sav")
    names = {"hung_2026_social_avoidance": "Social avoidance items (SA1-SA5)",
             "hung_2026_psmu": "Problematic social media use items (PSMU1-PSMU6)",
             "hung_2026_upward_comparison": "Upward social comparison items (USC1-USC6)",
             "hung_2026_downward_comparison": "Downward social comparison items (DSC7-DSC12)",
             "hung_2026_shyness": "Shyness items (SHY1-SHY6)",
             "hung_2026_social_desirability": "Social desirability / impression management items (EX1-EX5)"}
    for table, cols in blocks("hung_2026_social_comparison_avoidance").items():
        build(table, names[table] + ", as administered by Hung 2026",
              {c: m.column_names_to_labels[c] for c in cols}, {}, language="Chinese")


def wren(src):
    """figshare 10.6084/m9.figshare.33623410, CC BY 4.0. Qualtrics .sav: variable labels (English) keyed
    by the column name = the IRW code; value labels for the options. ACE and CAGE-AID are recoded by
    data/wren_2026_trauma_help_seeking.py from 1 = Yes / 2 = No to 1/0, so resp 1 = the source's 'Yes'
    and resp 0 = its 'No' (asserted from the value labels). The CTQ-SF and GHSQ labels carry the
    matrix stem before ' - '; it goes to instructions/section_prompt and the row label to item_text."""
    m = sav_labels(next(p for p in Path(src).iterdir() if p.suffix == ".sav"))

    def vl(c):
        return {int(k): v for k, v in m.value_labels[m.variable_to_label[c]].items()}

    B = blocks("wren_2026_trauma_help_seeking")
    for table, cols in B.items():
        if table in ("wren_2026_ace", "wren_2026_cage_aid"):
            for c in cols:
                assert {k: norm(v) for k, v in vl(c).items()} == {1: "Yes", 2: "No"}, (c, vl(c))
            name = ("Adverse Childhood Experiences questionnaire (ACE, 10 items)" if table.endswith("ace")
                    else "CAGE-AID (CAGE Adapted to Include Drugs), Brown & Rounds 1995")
            build(table, name, {c: m.column_names_to_labels[c] for c in cols}, {1: "Yes", 0: "No"})
            continue
        stems, items = set(), {}
        for c in cols:
            st, it = m.column_names_to_labels[c].split(" - ", 1)
            stems.add(norm(st)); items[c] = it
        assert len(stems) == 1, (table, stems)
        a = {}
        for c in cols:
            a.setdefault("x", vl(c))
            assert vl(c) == a["x"], c
        name = ("Childhood Trauma Questionnaire - Short Form (CTQ-SF), Bernstein et al. 2003"
                if "ctq" in table else "General Help-Seeking Questionnaire (GHSQ), Wilson et al. 2005")
        build(table, name, items, a["x"], instructions=stems.pop())


def anonpni(src):
    """Zenodo 10.5281/zenodo.23982003 (CC BY 4.0). EFAData.sav and CFAData.sav: each item's variable
    label is its statement and the column name is the IRW code (data/anon_2026_perceived_narcissism.py
    stacks the two files under cov_sample; the CFA file carries 24 of the EFA's 34 PNI items, and the
    impressions items only). Labels and value labels are asserted identical wherever the two files share
    a column. Codes ending in R are the depositors' reverse-keyed items, stored as answered."""
    e = sav_labels(Path(src) / "EFAData.sav")
    c_ = sav_labels(Path(src) / "CFAData.sav")
    lab, vls = {}, {}
    for m in (e, c_):
        for col in m.column_names:
            if col in m.column_names_to_labels and m.column_names_to_labels[col]:
                v = m.value_labels.get(m.variable_to_label.get(col), {})
                if col in lab:
                    assert norm(lab[col]) == norm(m.column_names_to_labels[col]), col
                    assert v == vls[col], col
                lab[col] = m.column_names_to_labels[col]
                vls[col] = v
    names = {"anon_2026_pni": "Perceived Narcissism Inventory items (study-developed), Towson University study",
             "anon_2026_pni_impressions": "Impressions of the target person (study-authored items)"}
    for table, cols in blocks("anon_2026_perceived_narcissism").items():
        build(table, names[table], {c: lab[c] for c in cols},
              lambda c: {int(k): v for k, v in vls[c].items()})


def ye(src):
    """figshare 10.6084/m9.figshare.33425338, CC BY 4.0. 'Raw Data.xlsx': row 3 of the sheet holds the
    codes (MC1..CC4 = the IRW codes), row 1 the English and row 2 the Chinese wording of each item,
    column by column. Administered in Chinese; English is the depositor's own (study_supplied). No
    anchors in the deposit."""
    d = pd.read_excel(Path(src) / "Raw Data.xlsx", header=None, nrows=3, dtype=str)
    assert d.iat[0, 5] == "Questionnaire item" and d.iat[1, 5] == "Questionnaire item in Chinese"
    by = {d.iat[2, j]: (d.iat[1, j], d.iat[0, j]) for j in range(8, d.shape[1])}
    names = {"ye_2026_music_cognition": "Music cognition (MC)", "ye_2026_immersion": "Immersion (IM)",
             "ye_2026_emotional_arousal": "Emotional arousal (EA)", "ye_2026_purchase_intention": "Purchase intention (PI)",
             "ye_2026_game_engagement": "Game engagement (GE)", "ye_2026_cultural_cognition": "Cultural cognition (CC)"}
    for table, cols in blocks("ye_2026_game_music").items():
        build(table, names[table] + "; Ye 2026 game-music questionnaire (Black Myth: Wukong players)",
              {c: by[c] for c in cols}, {}, language="Chinese")


SUCIPTO_EN = {
    "PEOU1": "In my opinion, Generative Artificial Intelligence (Generative AI) technology is very easy to use",
    "PEOU2": "In my opinion, no advanced skills are needed to be able to use Generative Artificial Intelligence (Generative AI).",
    "PEOU3": "In my opinion, it is very easy to learn how to use Generative Artificial Intelligence (Generative AI) technology.",
    "PU1": "At present, I learn financial theory by asking Generative Artificial Intelligence (Generative AI).",
    "PU2": "The existence of Generative Artificial Intelligence (Generative AI) technology helps me learn the basics of financial theory",
    "PU3": "The existence of Generative Artificial Intelligence (Generative AI) technology helps me study financial theory in more depth",
    "PU3_b": "I will recommend Generative Artificial Intelligence (Generative AI) technology to my friends who want to learn about the world of finance.",
    "ATU1": "When I want to learn the basics of financial theory, I will use Generative Artificial Intelligence (Generative AI).",
    "ATU2": "The existence of Generative Artificial Intelligence (Generative AI) is very important for improving my financial literacy.",
    "E1": "I believe that using Generative Artificial Intelligence (Generative AI) to understand finance does not violate the ethics of technology use.",
    "E2": "I feel it is important to use Generative Artificial Intelligence (Generative AI) responsibly and not to rely entirely on its output when making financial decisions.",
    "E3": "I use Generative Artificial Intelligence (Generative AI) wisely so as not to misunderstand or spread incorrect financial information.",
    "T1": "I trust the information and analysis results provided by Generative Artificial Intelligence (Generative AI) regarding financial literacy.",
    "T2": "I feel I can rely on Generative Artificial Intelligence (Generative AI) to help me understand and manage financial information.",
    "T3": "The explanations given by Generative Artificial Intelligence (Generative AI) help me understand financial concepts more accurately and on the basis of relevant data.",
    "T4": "Generative Artificial Intelligence (Generative AI) can help me overcome various difficulties in understanding financial topics.",
    "SN1": "I feel that using Generative AI to help me understand financial literacy is a normal thing to do.",
    "SN2": "I use Generative AI to improve my financial literacy because many people around me also consider this technology useful",
    "SN3": "I feel that my decision to use Generative AI to improve my financial literacy has the support of the people around me.",
    "AU1": "I have used Generative Artificial Intelligence (Generative AI) intensively since learning of its benefits",
    "AU2": "Using Generative Artificial Intelligence (Generative AI) has succeeded in increasing my knowledge of financial literacy.",
    "AU3": "I recommend Generative Artificial Intelligence (Generative AI) technology to others for learning financial literacy.",
    "AU4": "Learning financial literacy without the help of Generative Artificial Intelligence (Generative AI) feels less than optimal.",
}


def sucipto(src):
    """Zenodo 10.5281/zenodo.23313645, CC BY 4.0. Google Forms export: each item header is '<code>
    <Indonesian stem>'; data/sucipto_2026_genai_finlit.py takes the code from the header's first token
    (the second 'PU3' becomes 'PU3_b'), and this builder re-derives the same tie from the same headers.
    No anchors in the deposit (option_text blank). English in *_translated is IRW's own."""
    cols = list(pd.read_excel(xlsx_in(src), nrows=0).columns)
    stems, seen = {}, set()
    for c in cols:
        tok = c.split()[0]
        if re.fullmatch(r"[A-Z]+[0-9]", tok):
            code = tok + "_b" if tok in seen else tok
            seen.add(tok)
            stems[code] = c[len(tok):].strip()
    names = {"sucipto_2026_genai_peou": "Perceived ease of use (PEOU)", "sucipto_2026_genai_usefulness": "Perceived usefulness (PU)",
             "sucipto_2026_genai_attitude": "Attitude toward use (ATU)", "sucipto_2026_genai_ethics": "Ethics (E)",
             "sucipto_2026_genai_trust": "Trust (T)", "sucipto_2026_genai_social_norm": "Social norm (SN)",
             "sucipto_2026_genai_actual_use": "Actual use (AU)"}
    for table, cs in blocks("sucipto_2026_genai_finlit").items():
        build(table, names[table] + " of Generative AI for financial literacy; study-authored items, Sucipto, Susanto & Utama 2026",
              {c: (stems[c], SUCIPTO_EN[c]) for c in cs}, {}, language="Indonesian")


AINI_EN = [
    "Social media content about high-protein food products catches my attention.",
    "Information about high-protein food products that I see on social media is relevant to my needs or interests.",
    "Social media content provides information that helps me understand high-protein food products.",
    "Social media content helps me learn about the benefits or advantages of high-protein food products.",
    "Marketing activities for high-protein food products on social media make me more interested in those products.",
    "Content about high-protein food products on social media prompts me to look for more information about those products.",
    "I pay attention to other consumers' reviews of high-protein food products on the internet.",
    "I use online reviews as one source of information before considering buying high-protein food products.",
    "Other consumers' reviews help me judge the quality of high-protein food products.",
    "I take other consumers' experiences into account when choosing high-protein food products online.",
    "Positive recommendations from other users increase my interest in high-protein food products.",
    "I tend to trust information about high-protein food products that comes from other consumers' experiences on the internet.",
    "Information from other consumers on the internet can influence my decision when considering buying high-protein food products.",
    "I believe that high-protein food products can benefit my health.",
    "I believe that consuming high-protein food products can help meet my nutritional needs.",
    "I believe that high-protein food products can support my physical condition.",
    "I believe that high-protein food products can help support a healthy lifestyle.",
    "Health benefits are one of the important reasons for me to consider high-protein food products.",
    "I feel that the health benefits offered by high-protein food products match my needs.",
    "I see high-protein food products as a food choice that provides health benefits.",
    "The quality of the protein content and the nutritional benefits offered are worth the cost I pay.",
    "Overall, buying high-protein food products is a beneficial choice for me.",
    "The benefits I get from high-protein food products outweigh the money I have to spend.",
    "I intend to buy high-protein food products online.",
    "The likelihood that I will buy high-protein food products online is quite high.",
    "I will consider high-protein food products when shopping online.",
    "I am willing to choose high-protein food products via digital platforms in the future.",
]


def aini(src):
    """Zenodo 10.5281/zenodo.23295180, CC BY 4.0. Google Forms export with no codes: each of the 27 item
    headers IS the Indonesian stem. data/aini_2026_high_protein_food.py assigns codes POSITIONALLY
    (header 1 = the frequency covariate; headers 2-7 = smm1-6, 8-14 = reviews1-7, 15-21 = hb1-7, 22-24 =
    value1-3, 25-28 = purchase_intention1-4). This builder applies the identical slicing to the same
    header row, asserting 28 headers, so the code<-header tie is the script's own, re-derived. English in
    *_translated is IRW's own."""
    cols = list(pd.read_excel(xlsx_in(src), nrows=0).columns)
    assert len(cols) == 28
    code_of = {}
    for n, a, b in [("smm", 1, 7), ("reviews", 7, 14), ("hb", 14, 21), ("value", 21, 24), ("purchase_intention", 24, 28)]:
        for i in range(a, b):
            code_of[f"{n}{i - a + 1}"] = (cols[i].strip(), AINI_EN[i - 1])
    names = {"aini_2026_smm": "Social media marketing content", "aini_2026_reviews": "Online consumer reviews",
             "aini_2026_health_benefit": "Perceived health benefit", "aini_2026_value": "Perceived value",
             "aini_2026_purchase_intention": "Online purchase intention"}
    for table, cs in blocks("aini_2026_high_protein_food").items():
        build(table, names[table] + " (block named by IRW from the stems); study-authored items, Aini 2026",
              {c: code_of[c] for c in cs}, {}, language="Indonesian")


def tothe(src):
    """Mendeley Data 10.17632/7cjz65mg6g, CC BY 4.0. educational-factors.xlsx sheet 'details': variable
    names (= the data sheet's column names = the IRW codes) beside their English wording, in two column
    pairs; the scale line '5-point Likert scale questions (1=Bad, 5=Good)' heads both. Vietnamese
    students; administration language not stated -> unset. Gated against the live tables (they shipped
    2026-11-23) via cached irw_table_sets()."""
    d = pd.read_excel(Path(src) / "educational-factors.xlsx", "details", header=None, dtype=str)
    txt = {}
    for a, b in [(0, 1), (3, 4)]:
        for _, r in d.iterrows():
            k = str(r[a]).strip()
            if re.fullmatch(r"[ab]\d+_\d+", k):
                assert k not in txt, k
                txt[k] = r[b].strip()
    assert sum(str(v).startswith("5-point Likert scale questions (1=Bad, 5=Good)") for v in d.values.ravel()) == 2
    anchors = {1: "Bad", 5: "Good"}
    # b4_8 'I am satisfied with my life' matches the register's SWLS row (verdict block) word for word.
    # Ships: one common sentence inside an author-developed list is not the SWLS (ben-domingue, 2026-11-25).
    assert txt["b4_8"] == "I am satisfied with my life"
    for table, cs in blocks("tothe_2021_student_satisfaction").items():
        build(table, "Questionnaire on factors in Vietnamese students' motivation and satisfaction under COVID-19, "
              "To-The, Khuc-Van, Hoang-Duc et al. 2021", {c: txt[c] for c in cs}, anchors)


def minozzo(src):
    """Zenodo 10.5281/zenodo.22284893, CC BY 4.0. The Google Forms headers of amostra_calibracao.xlsx are
    '<block prompt> [<Portuguese item>]'; data/minozzo_2026_seafood_consumers.py renames each FULL header
    to its code by an explicit dict (no position), which this builder re-reads from the script. item_text
    = the bracketed Portuguese, section_prompt = the block prompt (one section per distinct prompt in a
    table). English: Supplementary_Material_EN Table_S1 'English translation' for the 48 listed items
    (depositor's own; Table_S1's Portuguese is asserted equal to the header's); the 7 barrier items and
    the block prompts are IRW's own translation. Anchors from Table_S1's note: 1 = discordo totalmente,
    7 = concordo totalmente; 2-6 unlabelled."""
    srcpy = (HERE.parent / "data" / "minozzo_2026_seafood_consumers.py").read_text(encoding="utf-8")
    m = re.search(r"\.rename\(columns=(\{.*?\})\)", srcpy, re.S)
    ren = eval(m.group(1))
    s1 = pd.read_excel(Path(src) / "Supplementary_Material_EN (1).xlsx", "Table_S1", header=3, dtype=str)
    s1 = s1[s1["Item code"].notna()].set_index("Item code")
    en_s1 = {k: (norm(r["Original wording (Portuguese)"]), norm(r["English translation"])) for k, r in s1.iterrows()}
    PROMPT_EN = {
        "Avalie seu nível de concordância com as afirmações abaixo sobre qualidade, confiança e segurança do pescado.":
            "Rate your level of agreement with the statements below about the quality, trustworthiness and safety of seafood.",
        "Avalie seu nível de concordância com as afirmações abaixo sobre barreiras ao consumo de pescado.":
            "Rate your level of agreement with the statements below about barriers to seafood consumption.",
        "Indique seu nível de concordância sobre a possibilidade de comprar os seguintes produtos à base de pescado.":
            "Indicate your level of agreement about the possibility of buying the following seafood-based products.",
        "Indique seu nível de concordância com as afirmações abaixo sobre tecnologia, processamento e industrialização do pescado.":
            "Indicate your level of agreement with the statements below about technology, processing and industrialisation of seafood.",
        "Com relação a intenção  de compra e disponibilidade em pagar analise cada opção e classifique conforme a escala":
            "With regard to purchase intention and willingness to pay, consider each option and rate it on the scale",
        "Quais barreiras de consumo": "Which consumption barriers",
    }
    BARRIER_EN = {
        "barreira_1": "The high price reduces how often I eat seafood.",
        "barreira_2": "The presence of bones reduces my interest in eating seafood.",
        "barreira_3": "The characteristic smell of seafood makes it harder for me to eat it.",
        "barreira_4": "I find it difficult to prepare seafood at home.",
        "barreira_5": "I find it difficult to find good-quality seafood where I live.",
        "barreira_6": "Seafood is not part of my family's eating routine.",
        "barreira_7": "Distrust about its origin reduces my intention to buy seafood.",
    }
    hdr = [str(c).strip() for c in pd.read_excel(Path(src) / "amostra_calibracao.xlsx", nrows=0).columns]
    by_code = {}
    for h, code in ren.items():
        assert h in hdr, code
        mm = re.fullmatch(r"(.+?)\s*\[(.+)\]", h, re.S)
        prompt, pt = norm(mm.group(1)), norm(mm.group(2))
        key = next(k for k in PROMPT_EN if norm(k) == prompt)
        if code in en_s1:
            assert en_s1[code][0] == pt, (code, en_s1[code][0], pt)
            en = en_s1[code][1]
        else:
            en = BARRIER_EN[code]
        by_code[code] = (pt, en, prompt, PROMPT_EN[key])
    anchors = {1: ("discordo totalmente", "strongly disagree"), 7: ("concordo totalmente", "strongly agree")}
    names = {t: t.replace("minozzo_2026_", "").replace("_", " ") for t in blocks("minozzo_2026_seafood_consumers")}
    for table, cs in blocks("minozzo_2026_seafood_consumers").items():
        resp, levels = resp_levels(table)
        prompts = list(dict.fromkeys(by_code[c][2] for c in cs))
        rows = []
        for c in cs:
            pt, en, pr, pr_en = by_code[c]
            sec = f"{table}_{prompts.index(pr) + 1}"
            for k in levels:
                o, o_en = anchors.get(k, ("", ""))
                rows.append({"table": table, "section_id": sec, "item": c,
                             "instrument": f"Seafood consumer survey: {names[table]} (study-authored items, Minozzo Giordani 2026)",
                             "language": "Portuguese", "instructions": "", "section_prompt": pr,
                             "item_text": pt, "correct_response": "", "option_text": o, "resp": k,
                             "instructions_translated": "", "section_prompt_translated": pr_en,
                             "item_text_translated": en, "option_text_translated": o_en})
        write(table, rows, resp, translated=True)


def galindo(src):
    """HELD (see provenance). Harvard Dataverse 10.7910/DVN/FDVOTW, CC0. The IRW item code is the .sav
    column name itself (e.g. 'PLN1.Arazobatkonpontzeko...'); its variable label is '[TAG] NN. <Basque
    stem>', and the stem after the tag and number goes to item_text. Built in Basque only (no English)
    because the table is held."""
    m = sav_labels(Path(src) / "Main DataBase.sav")
    lab = {}
    for col, l in m.column_names_to_labels.items():
        mm = re.match(r"^\[(OVR|PLN|SMT|EVA|RFL|EFT)\]\s*\d+\.\s*(.+)$", l or "")
        if mm:
            lab[col] = mm.group(2)
    for table, cs in blocks("galindodominguez_2026_srl_ai").items():
        build(table, table + " (held)", {c: lab[c] for c in cs}, {}, language="Basque")


def gomezmari(src):
    """HELD (see provenance). Zenodo 10.5281/zenodo.24271649. database.xlsx headers 'k. <Spanish stem>';
    item_k = the item numbered k (data/gomezmari_2026_asd_self_efficacy.py). The two sheets word every
    item with the label the group read (TEA / sindrome de Asperger); item_text quotes the TEA sheet."""
    cols = list(pd.read_excel(xlsx_in(src), sheet_name=0, nrows=0).columns)[11:41]
    lab = {"item_" + re.match(r"(\d+)\.", c).group(1): re.sub(r"^\d+\.\s*", "", c) for c in cols}
    for table, cs in blocks("gomezmari_2026_asd_self_efficacy").items():
        build(table, table + " (held)", {c: lab[c] for c in cs}, {}, language="Spanish")


def torun(src):
    """HELD (see provenance). Zenodo 10.5281/zenodo.24116589. Google Forms headers '<code>. <Turkish
    stem>'; the code before the dot is the IRW code."""
    cols = list(pd.read_excel(xlsx_in(src), nrows=0).columns)
    lab = {}
    for c in cols:
        mm = re.match(r"^([A-ZÇĞİÖŞÜ]+\d+)\.\s*(.+)$", str(c).strip())
        if mm:
            lab[mm.group(1)] = mm.group(2).strip()
    for table, cs in blocks("torun_2026_short_video_procrastination").items():
        missing = [c for c in cs if c not in lab]
        if missing:
            print("torun: codes not parsed, skipping", table, missing[:3])
            continue
        build(table, table + " (held)", {c: lab[c] for c in cs}, {}, language="Turkish")


def upoma(src):
    """Mendeley Data 10.17632/f26fhdpw23, CC BY 4.0. ONLY the two study-specific blocks: AI Literacy &
    Ethics (Q18-Q21) and the AI stressors (Q132-Q133), which the deposit's own README and
    AI_Learning_Stress_Master_Codebook.xlsx Variable_Codebook 'Notes' mark 'study-specific' (the
    TAM/AAIUS/GADS/GAIES/SDLRS/PSS-derived blocks are held). Variable (= the IRW code) beside 'Source
    Question' ('<section> [<item>]', the bracketed part is the item) and 'Value Labels'. English
    administration (survey_instrument_english.docx). Gated against the live tables (shipped 2026-11-23)."""
    cb = pd.read_excel(Path(src) / "AI_Learning_Stress_Master_Codebook.xlsx", "Variable_Codebook", dtype=str).set_index("Variable")

    def opts(c):
        return {int(k): v.strip() for k, v in (x.split("=", 1) for x in cb.loc[c, "Value Labels"].split("|"))}

    for table, cs in [("upoma_2026_ai_literacy_ethics", ["Q18", "Q19", "Q20", "Q21"]),
                      ("upoma_2026_ai_stressors", ["Q132", "Q133"])]:
        assert cs == blocks("upoma_2026_ai_learning_stress")[table]
        for c in cs:
            assert "study-specific" in cb.loc[c, "Notes"], c
        items = {c: re.fullmatch(r".*?\[(.+)\]\s*", cb.loc[c, "Source Question"], re.S).group(1) for c in cs}
        name = ("AI Literacy & Ethics items (study-specific), Upoma et al. 2026" if "literacy" in table
                else "AI-specific stressor items (study-specific, not part of the PSS-10), Upoma et al. 2026")
        build(table, name, items, lambda c: opts(c))


BUILDERS = {"herrera": herrera, "croitoru": croitoru, "ahmad": ahmad, "sengarie": sengarie,
            "efawati": efawati, "lee": lee, "umoru": umoru, "charzynska": charzynska, "hung": hung,
            "wren": wren, "anonpni": anonpni, "ye": ye, "sucipto": sucipto, "aini": aini,
            "tothe": tothe, "minozzo": minozzo, "galindo": galindo, "gomezmari": gomezmari, "torun": torun, "upoma": upoma}

if __name__ == "__main__":
    root = Path(sys.argv[1])
    for name in (sys.argv[2:] or BUILDERS):
        BUILDERS[name](root / name)
