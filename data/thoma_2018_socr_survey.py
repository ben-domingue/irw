#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209550
# DOI: 10.1371/journal.pone.0209550
# Paper: Thoma, M. V., Mc Gee, S. L., Fegert, J. M., Glaesmer, H., Brähler, E.,
#   & Maercker, A. (2018). Evaluation of the revised sense of coherence scale
#   in a representative German sample. PLOS ONE 13(12): e0209550.
# Data: journal.pone.0209550.s001 (S1 Supporting information, "Raw data
#   file", .sav). 2,510 residents of Germany aged 14+, a nationwide household
#   survey with random-route sampling and Kish-grid selection within household
#   (USUMA, 2016). The deposit carries a survey weight.
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# THREE output tables, one per instrument:
#   thoma_2018_socr   SOCR_1..13, 1-5 (Not at all .. Extremely). The raw
#                     SOCR_6 ships, not the deposit's SOCR_6_R recode.
#   thoma_2018_phq4   PHQ4_1..4, 0-3. The deposit holds the PHQ-4 twice: a
#                     1-4 "_v1" copy and a 0-3 copy with the instrument's
#                     own anchors (Not at all .. Nearly every day); the 0-3
#                     copy ships. Note the stems say "during the last week"
#                     where the PHQ-4 asks about two weeks; shipped as
#                     administered.
#   thoma_2018_ctq    CTQ_1..28, 1-5 (Never true .. Very often true).
# Every item has its stem in the variable label and its anchors in the value
# labels; the three blocks are the instruments the paper names, item for item.
#
# -1 ("No information") and -2 ("Filter") are the deposit's missing codes on
# every column and become NaN; nothing else is recoded.
#
# Not shipped: the LEC-5 (17 events x 7 one-hot "happened to me / witnessed /
# ..." indicators -- a multi-select checklist, not an ordinal item battery),
# its follow-up questions (worst event, year, times), and the deposit's
# derived groupings.
#
# `id` is the deposit's own lD column (unique panel ids in 1056..4362).
#
# Covariates: gender, age in years, marital status, education, employment
# status, nationality (German / not), religion, household size, children under
# 18, East/West region, federal state, urbanicity (GKBIK three-way), and the
# survey weight as cov_survey_weight. Income is kept as the deposit's own
# income band codes (cov_income_band).
#
# Item text: SHIPPED for the PHQ-4 (register: PHQ/GAD screener family, ship).
# NOT SHIPPED for the SOC-R and the CTQ. The words are in hand for all three
# (both label levels read: stems in the variable labels, anchors in the value
# labels), so these are rights holds: the SOC-R is Bachem & Maercker's 2016
# instrument, with no open reuse terms located (register row added, hold);
# the CTQ is Bernstein & Fink's instrument published by Pearson under licence
# (register row added, hold).

import os
import re
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("THOMA_RAW", "S1_Supporting_information.sav")
N_ROWS = 2510
ITEMTEXT_COLS = ["table", "section_id", "item", "instrument", "instructions",
                 "section_prompt", "item_text", "correct_response",
                 "option_text", "resp"]
MISSING = [-1, -2]

BLOCKS = {
    "thoma_2018_socr": ([f"SOCR_{i}" for i in range(1, 14)], 1, 5, None),
    "thoma_2018_phq4": ([f"PHQ4_{i}" for i in range(1, 5)], 0, 3,
                        "Patient Health Questionnaire-4 (PHQ-4), as administered (one-week frame)"),
    "thoma_2018_ctq": ([f"CTQ_{i}" for i in range(1, 29)], 1, 5, None),
}


def clean(s):
    return s.where(~s.isin(MISSING))


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels, vl = meta.column_names_to_labels, meta.variable_value_labels
    assert len(df) == N_ROWS, len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    for c in txt:   # the two LEC multi-select strings, e.g. '01,02,'
        assert df[c].astype(str).str.fullmatch(r"[0-9,]*").all(), c
    assert df["lD"].is_unique   # a panel id, 1056..4362, not 1..N

    cov = pd.DataFrame({
        "id": df["lD"].astype(int),
        "cov_gender": clean(df["Gender"]).map({1: "male", 2: "female"}),
        "cov_age": clean(df["Age"]),
        "cov_marital_status": clean(df["Marital_status"]),
        "cov_education": clean(df["Education"]),
        "cov_employment": clean(df["Employment"]),
        "cov_german_national": clean(df["Nationality"]).map({1: 1, 2: 0}),
        "cov_religion": clean(df["Religion"]),
        "cov_household_size": clean(df["Household"]),
        "cov_children_under_18": clean(df["Kids"]),
        "cov_region": df["Region"].map({1: "west", 2: "east"}),
        "cov_federal_state": df["Federal_state"],
        "cov_urbanicity": df["Town_GKBIK"].map({1: "countryside", 2: "small_town", 3: "big_town"}),
        "cov_income_band": clean(df["Income"]),
        "cov_survey_weight": df["Weight"],
    })
    assert vl["Region"] == {1.0: "West", 2.0: "East"} or set(df["Region"]) == {1, 2}
    assert cov["cov_age"].between(14, 100).all(), cov["cov_age"].describe()
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    total = 0
    for name, (cols, lo, hi, instrument) in BLOCKS.items():
        wide = df[["lD"] + cols].rename(columns={"lD": "id"}).copy()
        wide["id"] = wide["id"].astype(int)
        for c in cols:
            wide[c] = clean(wide[c])
            opts = {int(k): v for k, v in vl[c].items() if int(k) >= 0}
            assert sorted(opts) == list(range(lo, hi + 1)), (c, vl[c])
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), (name, sorted(long["resp"].unique()))
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["item"].nunique() == len(cols) and not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} resp={lo}-{hi}")

        if instrument:
            rows = []
            for c in cols:
                # 'PHQ4 1 - Feeling nervous, anxious, oe on edge' -> stem after the dash
                stem = re.sub(r"^PHQ4 \d+ - ", "", labels[c]).strip()
                for k in range(lo, hi + 1):
                    rows.append({"table": name, "section_id": f"{name}_1", "item": c,
                                 "instrument": instrument,
                                 "instructions": "Complaints during the last week",
                                 "section_prompt": "NA", "item_text": stem,
                                 "correct_response": "NA", "option_text": vl[c][float(k)],
                                 "resp": k})
            it = pd.DataFrame(rows, columns=ITEMTEXT_COLS)
            assert set(it["item"]) == set(long["item"]) and set(it["resp"]) == set(long["resp"])
            it.to_csv(os.path.join(ITEMTEXT_DIR, name + "__items.csv"), index=False)
            print(f"  item text: {len(it)} rows; stems: {it['item_text'].unique().tolist()}")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
