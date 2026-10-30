#!/usr/bin/env python3
# Source: https://zenodo.org/records/5553923
# DOI: 10.5281/zenodo.5553923
# Deposit: Mayweg-Paus, E., Zimmermann, M., & Ruwe, T. (2021). DIALLS Dataset of
#   evaluations of Open Educational Resources -- The Cultural Literacy Learning
#   Programme resources. Zenodo. (DIALLS, Dialogue and Argumentation for
#   cultural Literacy Learning in Schools, H2020 WP4 deliverable 4.1.)
# Data: DIALLS_evaluations_of_OER.sav (SPSS, 141 rows, 161 columns)
# Codebook: DIALLS_learning_material_evaluation_Description.pdf in the same
#   deposit, plus the .sav's own variable and value labels, which the PDF
#   points at as the codebook ("Values and variables are defined in the
#   available codebook").
# License: CC BY 4.0, stated on the Zenodo record and again in the
#   description PDF ("These data and their description are licensed under
#   CC BY 4.0").
#
# Why this was a lead and not a shipped table: the 2026-10-29b sweep flagged it
# `pii_suspected` on the column RGPC_1_Name, whose variable label begins
# "Respondent-Generated-Personal-Code 1: First letter of your first name". That
# is a FALSE POSITIVE and the deposit says so outright: the four RGPC_* columns
# are a respondent-generated linkage code (first letter of first name, day of
# the month of one's birthday, first letter of the city of birth, last digit of
# one's mobile number), and the description PDF's "Anonymisation of the data"
# section reads: "At no point of the survey was it possible to draw conclusions
# about the individual from the data. The use of a respondent generated
# personal code (see above) enabled a completely anonymous participation in the
# four different surveys." None of the four is a name, an email address, a date
# of birth or a phone number -- each is one character or one digit of one, and
# their whole purpose was to avoid collecting an identifier. They are dropped
# here in any case: `id` is the deposit's own participant number.
#
# One output table. The four surveys (professional-development materials for
# cultural literacy, for dialogue and argumentation and for wordless films;
# lesson plans; the Scale of Progression for Cultural Literacy Learning; the
# discussion forum) all apply the SAME evaluation instrument -- three items
# each on a resource's application, content, design and value, after
# Kirkpatrick & Kirkpatrick (2006) -- on the SAME five-point agreement scale,
# to the same teachers, who are linked across surveys by the RGPC code. So this
# is one crossed item battery, not four scales, and it ships as one sparse
# table of 79 items, following the merge Ben asked for on the
# lee_whiting_2025_trust_actors tables (2026-10-29f). Splitting it by survey
# would also put three of the four pieces under the N>=100 floor (lesson plans
# n=71, SPCLL n=65, discussion forum n=62) and throw them away.
#
# The missingness is by design, as the PDF states: "not all teachers answered
# all four surveys".
#
# `id` is the ROW INDEX, not the deposit's VP_NR ("Continuous participant
# numbers as specific identifier"): two rows share one VP_NR value, so it does
# not identify a respondent. The row index has no preimage and links only
# within this deposit.
#
# resp = 0 IS DROPPED. The value labels define 1-5 only ("Strongly disagree" ..
# "Strongly agree") and the PDF documents no sixth category, yet 67 cells over
# all 79 items hold 0, at most 3 per item. The same undocumented 0 appears in
# covariate columns whose labels run 1-2 or 1-3, which is what settles it: 0 is
# this export's no-answer code, not a response. 67 of 7,821 observed cells
# (0.9%).
#
# Item text: SHIPPED, from the .sav's own variable labels (the stem) and value
# labels (the five anchors) -- both levels present for all 79 items. The items
# are study-authored: the PDF states "UBER, as responsible partner, developed
# the items and analysed the data", and three stems were searched verbatim and
# match no published instrument. Kirkpatrick & Kirkpatrick (2006) is the
# evaluation MODEL the four facets come from, not an instrument whose wording
# was copied. Rights: study-authored under the deposit's own CC BY 4.0.
# The one caveat, which earns a public note: the labels are the study's ENGLISH
# master, while the surveys were fielded in four partner languages (German, UK
# English, Portuguese, Hebrew) and the PDF says the per-language datasets were
# merged into this one file. For the non-English partners the shipped wording
# is therefore a stand-in for what was administered -- the same shape as
# lee_whiting_2025_* in the 2026-10-29 batch.
#
# Dropped, each for a reason (the script balances its books and asserts that no
# source column is unaccounted for):
#   RGPC_1..4            the anonymisation code above
#   re_*                 reverse-coded copies of 15 items the depositors
#                        derived; the raw item is already shipped
#   *_mean_*             subscale and total composites, not responses
#   *_Feedback           free-text answers, not responses (screened for PII)
#   filter_$             an SPSS filter variable
#   DF_exp_1..4          four discussion-forum EXPERIENCE items on their own
#                        five-point experience scale (No experience ..
#                        Extensive experience) rather than the agreement scale,
#                        so a separate table -- and n=62, under the floor
#   AG_*, AG_num*, number_students, number_lessons, realistic_use
#                        survey-specific counts and multi-selects, several
#                        carrying stray undocumented codes (AG_1 holds a 6
#                        against labels 0-1; realistic_use a 10 against 1-2)
#
# PII: screened. The screen selects with is_string_dtype, not dtype == object
# (which finds nothing on a pyreadstat frame), prints its denominator and
# asserts it is non-zero. Clean over the five string columns -- the four
# open-feedback boxes and RGPC_1_Name/RGPC_3_City, which hold single capital
# letters.

import os
import re

import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "automated_finding", "itemtext_output")

RAW = os.environ.get("DIALLS_RAW", "DIALLS_evaluations_of_OER.sav")

TABLE = "maywegpaus_2021_dialls_oer"

# the agreement-scale evaluation items, by the source's own column names
ITEM_RE = re.compile(
    r"^(?:(?:CL|DA|WF|LP|SPCLLboth|DF)_(?:app|con|des|val|mot|par|top)_[0-9]"
    r"|SPCLL_con_[0-9]_[DC])$")

# the five anchors, as the value labels give them (61 items capitalise the
# first word and 12 do not -- same scale, so the shipped option text is
# normalised to the capitalised form and the difference noted here)
ANCHORS = {1: "Strongly disagree", 2: "Disagree",
           3: "Neither disagree nor agree", 4: "Agree", 5: "Strongly agree"}

INSTRUMENT = ("DIALLS evaluation of open educational resources "
              "(study-authored, after Kirkpatrick & Kirkpatrick 2006): three "
              "items each on a resource's application, content, design and "
              "value")

COUNTRY = {1: "UCAM, United Kingdom", 2: "NOVA, Portugal",
           3: "HUJI, Israel", 4: "UBER, Germany"}
DEMOG = {
    "country": "cov_partner_country",
    "Demographics_T_Exp": "cov_teaching_experience",
    "Demographics_CL_Exp": "cov_cultural_literacy_expertise",
    "Demographics_DA_Exp": "cov_dialogue_argumentation_expertise",
    "Demographics_WF_Exp": "cov_wordless_films_expertise",
    "Demographics_Col_Exp": "cov_colleagues_used_dialls",
}
# which battery each item prefix belongs to -- the item text table's sections
SECTIONS = {
    "CL": ("PD material: cultural literacy",
           "Professional development material on cultural literacy"),
    "DA": ("PD material: dialogue and argumentation",
           "Professional development material on dialogue and argumentation"),
    "WF": ("PD material: wordless films",
           "Professional development material on mediating wordless films"),
    "LP": ("Lesson plans", "The DIALLS lesson plans and lesson prompts"),
    "SPCLLboth": ("SPCLL", "The Scale of Progression for Cultural Literacy "
                           "Learning, both tools"),
    "SPCLL_con": ("SPCLL tools", "The SPCLL Dialogue Progression Tool and "
                                 "Cultural Learning Progression Tool"),
    "DF": ("Discussion forum", "The DIALLS discussion forum as a community "
                               "of practice"),
}

DROPPED_EXACT = ["RGPC_1_Name", "RGPC_2_Birthday", "RGPC_3_City",
                 "RGPC_4_Number", "filter_$", "AG_number_1", "AG_number_2",
                 "AG_number_3", "AG_num1", "AG_num2", "AG_num3",
                 "number_students", "number_lessons", "realistic_use",
                 "AG_1", "AG_2", "AG_3", "AG_1new", "AG_2new", "AG_3new",
                 "DF_exp_1", "DF_exp_2", "DF_exp_3", "DF_exp_4"]
DROPPED_RE = re.compile(r"_mean_|^re_|Feedback$")


def screen_for_pii(df):
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(txt)} of {len(df.columns)} columns: {txt}")
    assert txt, "PII screen selected no columns -- the selector is wrong"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
                     r"|\+?\d{9,}"
                     r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str)
            if pat.search(v)]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("PII screen: clean")


def section_of(item):
    for pre in ("SPCLL_con", "SPCLLboth", "CL", "DA", "WF", "LP", "DF"):
        if item.startswith(pre + "_"):
            return pre
    raise AssertionError(f"no section for {item}")


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    raw_cols = list(df.columns)
    screen_for_pii(df)

    items = [c for c in raw_cols if ITEM_RE.match(c)]
    assert len(items) == 79, (len(items), items)

    # balance the books
    accounted = (set(items) | set(DEMOG) | {"VP_NR"} | set(DROPPED_EXACT)
                 | {c for c in raw_cols if DROPPED_RE.search(c)})
    left_out = [c for c in raw_cols if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    derived = [c for c in raw_cols if DROPPED_RE.search(c)]
    print(f"dropped {len(DROPPED_EXACT) + len(derived)} source columns: "
          f"4 RGPC code parts, {len(derived)} derived/free-text/filter, "
          f"4 DF_exp_* (own scale, n=62), 16 survey-specific counts and "
          f"multi-selects")

    # VP_NR repeats once in the file (two rows share one number), so it
    # cannot be the id; fall back to the row index, which the standard allows
    # and which nothing outside this deposit links to
    dup = df["VP_NR"].duplicated(keep=False).sum()
    if dup:
        print(f"VP_NR is not unique ({dup} rows share a value) -- using the "
              f"row index as id")
        df["id"] = df.index + 1
    else:
        df["id"] = df["VP_NR"].astype(int)

    df["cov_partner_country"] = df["country"].map(COUNTRY)
    for src, dst in DEMOG.items():
        if dst == "cov_partner_country":
            continue
        labels = meta.variable_value_labels.get(src)
        assert labels, f"{src} has no value labels"
        # 0 is this export's undocumented no-answer code; see header
        df[dst] = df[src].where(df[src] != 0).map(labels)
    cov_cols = sorted(DEMOG.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].notna() & (long["resp"] != 0)].copy()
    print(f"dropped {before - len(long)} cells coded 0 "
          f"(undocumented no-answer) of {before} observed")
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(1, 5).all(), long["resp"].unique()
    assert long["id"].nunique() >= 100, long["id"].nunique()
    assert long["item"].nunique() == 79, long["item"].nunique()

    os.makedirs(OUT_DIR, exist_ok=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")

    # ---- item text, one row per item x response option -------------------
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    rows = []
    for it in items:
        stem = meta.column_names_to_labels.get(it)
        assert stem, f"{it} has no variable label"
        # the labels prefix each stem with its own battery and facet, e.g.
        # "PD Material Cultural Literacy application 1: I need additional
        # support ...". Keep only what was asked of the teacher.
        text = stem.split(":", 1)[1].strip() if ":" in stem else stem.strip()
        assert text, f"{it} stem is empty after stripping the label prefix"
        labels = meta.variable_value_labels.get(it)
        assert labels and len(labels) == 5, (it, labels)
        pre = section_of(it)
        sec, prompt = SECTIONS[pre]
        for code, anchor in ANCHORS.items():
            rows.append({
                "table": TABLE,
                "section_id": f"{TABLE}_{pre.lower()}",
                "item": it,
                "instrument": INSTRUMENT,
                # fielded in four partner languages; the shipped wording is
                # the study's English master, so the _translated columns stay
                # out entirely (standard: "Administered language")
                "language": "English; German; Portuguese; Hebrew",
                "instructions": "Please indicate how far you agree with each "
                                "statement.",
                "section_prompt": prompt,
                "item_text": text,
                "correct_response": "",
                "option_text": anchor,
                "resp": code,
            })
    items_df = pd.DataFrame(rows)
    assert len(items_df) == 79 * 5, len(items_df)
    assert set(items_df["item"]) == set(long["item"]), "item sets differ"
    assert set(items_df["resp"]) == set(range(1, 6))
    assert set(long["resp"]) <= set(items_df["resp"]), "resp sets differ"
    items_df.to_csv(os.path.join(ITEMTEXT_DIR, TABLE + "__items.csv"),
                    index=False)
    print(f"{TABLE}__items: rows={len(items_df)} items={items_df['item'].nunique()}")


if __name__ == "__main__":
    convert()
