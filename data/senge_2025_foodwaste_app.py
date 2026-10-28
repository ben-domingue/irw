#!/usr/bin/env python3
# Source: https://zenodo.org/records/13772955
# DOI: 10.5281/zenodo.13772955
# Paper/deposit: Senge, J. M., Mielinger, E., Wendt, M.-C., Krupitzer, C., &
#   Weinrich, R. (2025). Dataset, Questionnaire and Interview-Guidelines:
#   Understanding Consumers' Attitudes towards a Smartphone Application to
#   Reduce Food Waste. Zenodo.
# Data: Clean_dataset.csv (semicolon-delimited, 520 German consumers)
# License: CC BY 4.0 (stated on the Zenodo deposit page)
#
# Eleven output tables, one per questionnaire battery. The deposit's own
# Survey-xFoWa.pdf numbers them, and the dataset's column prefixes follow it
# exactly (v_8 -> 2.1, v_9 -> 2.2, v_10 -> 3.1, v_11 -> 3.2, v_12 -> 4.1,
# v_13 -> 5.1, v_14 -> 6.1, v_15 -> 6.2, v_18 -> 7.3 + 7.4, v_19 -> 7.5).
# v_18 is split because the PDF shows it is two batteries: a..c is perceived
# usefulness of the app (7.3) and d..f is whether the respondent has what it
# takes to use it (7.4).
#
# Item text: shipped for the five study-authored food-waste batteries
# (shopping planning, talking about food waste, best-before-date beliefs,
# disposal frequency, storage). NOT shipped for the environmental-awareness,
# app-review, technology-affinity and app-acceptance batteries: those read as
# adaptations of published instruments (the 6.2 block is the TA-EG technology
# affinity scale, Karrer et al. 2009; the 7.3/7.4/7.5 blocks are UTAUT-shaped)
# and no rights basis was established for them in this batch. The wording of
# every battery is in Survey-xFoWa.pdf in this same deposit -- note it is the
# study's own ENGLISH TRANSLATION, the deposit says so explicitly; the
# administration was German and the German original is not deposited.
#
# PII: screened. screen_for_pii() returned clean over the 4 string columns
# (count asserted non-zero). Those four are the free-text answers to 7.1, 7.2,
# 7.3-technical-problems and a closing comments box -- columns whose job is to
# collect comments, not identifiers -- and none holds an email address. They
# are not shipped in any case.
#
# Dropped: v_15_k_Triffteherzu (constant 4, no counterpart in the
# questionnaire) and v_16_QuizfrageMHD (constant 1, the comprehension-test
# question text rather than a response). Both are single-valued, so neither
# carries any response information.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("SENGE_RAW", "Clean_dataset.csv")

# Survey-xFoWa.pdf, part 1
GENERATION = {1: "Gen Z (13-26)", 2: "Gen Y (27-41)", 3: "Gen X (42-57)",
              4: "Gen Boomer (58-76)", 5: "Gen Silent (77+)",
              6: "Gen till 45 (source label, as published)"}
GENDER = {1: "male", 2: "female"}
INCOME = {1: "under 1300 EUR", 2: "1301-1700 EUR", 3: "1701-2600 EUR",
          4: "2601-3600 EUR", 5: "3601-5000 EUR", 6: "5000 EUR or higher"}
EDUCATION = {1: "no school-leaving qualification",
             2: "still in school-based training",
             3: "secondary education", 4: "advanced secondary education",
             5: "A-level"}
LOCATION = {1: "metropolis (>500,000)", 2: "large city (100,001-500,000)",
            3: "medium-sized city (20,001-100,000)",
            4: "small town (5,001-20,000)", 5: "village (up to 5,000)"}
HOUSEHOLD = {1: "1 person", 2: "2 persons", 3: "3 persons", 4: "4 persons",
             5: "5 persons or more"}
CHILDREN = {1: "0", 2: "1", 3: "2", 4: "3", 5: "4 or more"}

DEMOG = {
    "v_1_Geburtsjahr": ("cov_generation", GENERATION),
    "v_2_Geschlecht": ("cov_gender", GENDER),
    "v_4_Einkommen": ("cov_income", INCOME),
    "v_5_Schulabschluss": ("cov_education", EDUCATION),
    "v_6_Einwohner": ("cov_location", LOCATION),
    "v_7A_Haushalt": ("cov_household_size", HOUSEHOLD),
    "v_7B_Kinder": ("cov_children_under_18", CHILDREN),
}
# 16 German federal states, labelled by their own numbering in the PDF; kept
# as the source code because a state is a bare category, not a scale
STATE_COL = "v_3_Bundesland"

TABLES = {
    "senge_2025_shopping_planning": "v_8_",
    "senge_2025_food_waste_talk": "v_9_",
    "senge_2025_bbd_attitudes": "v_10_",
    "senge_2025_disposal_frequency": "v_11_",
    "senge_2025_storage": "v_12_",
    "senge_2025_env_awareness": "v_13_",
    "senge_2025_app_review_use": "v_14_",
    "senge_2025_tech_affinity": "v_15_",
    "senge_2025_app_intention": "v_19_",
}
# v_18 is two batteries in one prefix
SPLIT = {
    "senge_2025_app_usefulness": ["v_18_a_AppSinnvoll", "v_18_b_AppNützlich",
                                  "v_18_c_AppAustausch"],
    "senge_2025_app_facil_conditions": ["v_18_d_RessourcenHandy",
                                        "v_18_e_technWissen",
                                        "v_18_f_AppNutzenEinfach"],
}
DROP = ["v_15_k_Triffteherzu", "v_16_QuizfrageMHD"]


def convert():
    df = pd.read_csv(RAW, sep=";")
    assert df["lfdn"].nunique() == len(df), "lfdn is not unique"
    df = df.rename(columns={"lfdn": "id"})

    for src, (dst, mapping) in DEMOG.items():
        assert src in df.columns, src
        bad = set(df[src].dropna().unique()) - set(mapping)
        assert not bad, f"{src}: unmapped codes {bad}"
        df[dst] = df[src].map(mapping)
    df["cov_state"] = df[STATE_COL]
    cov_cols = sorted([d for d, _ in DEMOG.values()] + ["cov_state"])

    groups = {name: [c for c in df.columns if c.startswith(pre)
                     and c not in DROP]
              for name, pre in TABLES.items()}
    groups.update(SPLIT)
    expected = {"senge_2025_shopping_planning": 5,
                "senge_2025_food_waste_talk": 3,
                "senge_2025_bbd_attitudes": 5,
                "senge_2025_disposal_frequency": 10,
                "senge_2025_storage": 5,
                "senge_2025_env_awareness": 6,
                "senge_2025_app_review_use": 5,
                "senge_2025_tech_affinity": 9,
                "senge_2025_app_intention": 6,
                "senge_2025_app_usefulness": 3,
                "senge_2025_app_facil_conditions": 3}
    for name, cols in groups.items():
        assert len(cols) == expected[name], (name, len(cols), cols)

    # balance the books: every source column is shipped, a covariate, an
    # explicitly dropped constant, or a free-text column that is not a response
    item_cols = {c for cols in groups.values() for c in cols}
    accounted = item_cols | set(DEMOG) | {"lfdn", STATE_COL} | set(DROP)
    left_out = [c for c in pd.read_csv(RAW, sep=";", nrows=0).columns
                if c not in accounted]
    assert all(c.endswith("_OFFEN") for c in left_out), left_out
    print(f"left out {len(left_out)} free-text columns (not responses): {left_out}")

    os.makedirs(OUT_DIR, exist_ok=True)
    written = set()
    for name, cols in sorted(groups.items()):
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        # two coding schemes in one file: the agreement batteries are the
        # questionnaire's own -2..2, the disposal-frequency battery is 1..5
        lo, hi = (1, 5) if name.endswith("disposal_frequency") else (-2, 2)
        assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())
        assert name not in written, f"duplicate output name {name}"
        assert len(name) <= 40, f"{name} is over the 40-character cap"
        written.add(name)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
