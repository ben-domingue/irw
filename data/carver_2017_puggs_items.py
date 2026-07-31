from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0169808
# DOI: 10.1371/journal.pone.0169808
# PUGGS (Public Understanding of Genetics and Genomics Survey), two pilot
# studies with raw data (S5/S6 Tables) and matching Code Books (S4/S2 Text).
#
# The two pilots use genuinely different response formats for the
# "core ideas" items, confirmed from their own Code Books -- not merged,
# per datastandard.md's "same instrument administered to multiple
# sub-studies" rule (identical administration must be confirmed, not
# assumed from similar item wording):
#   - Pilot 1: 4-point Likert agreement (1=strongly disagree ... 4=strongly
#     agree, 5=don't know) with each item individually true/false-keyed.
#     The paper's own codebook recodes this into a directional
#     "determinism"/"understanding" score -- not applied here; raw
#     agreement is shipped as-is (direction is allowed to vary by item
#     per datastandard.md's reverse-scoring rule).
#   - Pilot 2: a direct True(1)/False(2)/Don't know(3) choice per item.
#     Unlike pilot 1, this has no inherent ordinal direction as raw codes,
#     so (matching datastandard.md's own worked example for a
#     true/false/don't-know financial-literacy quiz) it is recoded to
#     correct(1)/incorrect(0) using the paper's own answer key; don't-know
#     and missing(99) are filtered as non-response, not coded as
#     incorrect.
#
# Both pilots' "Table of Traits" (TT) items (rate genetic vs. environmental
# influence on each of several traits, 1-5, higher = more genetic) are
# shipped as their own raw ordinal scale -- pilot 1's codebook additionally
# gives a scientifically "Expected answer" per trait, kept as an
# itemcov_expected_answer (an item-level attribute, not a derived score).
#
# Sentinel/missing codes confirmed against the actual data (not just the
# codebook): pilot 1 uses `99` as an additional true-missing code beyond
# the "don't know" option baked into each item's own scale (6 for TT, 5 for
# the Likert Q-items); pilot 2 uses `99` throughout. All filtered as
# missing, not coded as 0.
FILE_URLS = {
    1: ("https://journals.plos.org/plosone/article/file"
        "?type=supplementary&id=10.1371/journal.pone.0169808.s005"),
    2: ("https://journals.plos.org/plosone/article/file"
        "?type=supplementary&id=10.1371/journal.pone.0169808.s006"),
}
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Age": "cov_age_group",
    "Gender": "cov_gender",
    "Study": "cov_field_of_study",
    "Religion": "cov_religion_influence",
    "Experience": "cov_genetics_experience",
}

# Pilot 1: TT1-TT20, each with a scientifically "expected" response (1-5).
PILOT1_TT_EXPECTED = {
    "TT1": 3, "TT2": 4, "TT3": 4, "TT4": 2, "TT5": 5, "TT6": 4, "TT7": 3,
    "TT8": 2, "TT9": 1, "TT10": 5, "TT11": 2, "TT12": 1, "TT13": 4,
    "TT14": 3, "TT15": 4, "TT16": 4, "TT17": 4, "TT18": 2, "TT19": 1, "TT20": 5,
}
PILOT1_CORE_DET_ITEMS = [f"Q{i}" for i in range(1, 14)]
PILOT1_GENOM_ITEMS = [f"Q{i}" for i in range(14, 32)]
PILOT1_ATTITUDE_ITEMS = [f"Q{i}" for i in range(32, 52)]

# Pilot 2: TT1_Height ... TT17_Blood group (17 traits, no answer key given
# in this pilot's Code Book). Answer key for the true/false items, from
# the S2 Text Code Book (1 = correct answer is "True", 2 = correct answer
# is "False").
PILOT2_TT_COLS = ["TT1_Height", "TT2_Bipolar", "TT3_Diabetes", "TT4_Colour blindness",
                  "TT5_Schizophrenia", "TT6_Alcoholism", "TT7_Breast cancer",
                  "TT8_Interest in fashion", "TT9_Gambling", "TT10_Political beliefs",
                  "TT11_Intelligence", "TT12_Depression", "TT13_ADHD", "TT14_Asthma",
                  "TT15_Violent behav.", "TT16_Religious beliefs", "TT17_Blood group"]
PILOT2_DET_ANSWER_KEY = {"Q1": 2, "Q2": 2, "Q3": 1, "Q4": 2, "Q5": 1,
                          "Q6": 2, "Q7": 2, "Q8": 1, "Q9": 1}
PILOT2_GENOM_ANSWER_KEY = {"Q10": 2, "Q11": 1, "Q12": 1, "Q13": 2, "Q14": 1,
                           "Q15": 1, "Q16": 1, "Q17": 1, "Q18": 2, "Q19": 2,
                           "Q20": 2, "Q21": 1, "Q22": 2, "Q23": 1, "Q24": 2, "Q25": 1}
PILOT2_ATTITUDE_ITEMS = [f"Q{i}" for i in range(26, 46)]


def fetch(pilot: int) -> pd.DataFrame:
    r = requests.get(FILE_URLS[pilot], headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")
    df = df.rename(columns={"Questionnaire number": "id", **COV_MAP})
    # A stray Age=5 (outside the codebook's 1-4 categories) in pilot 1 --
    # a data-entry slip, not a valid category.
    df.loc[~df["cov_age_group"].isin([1, 2, 3, 4]), "cov_age_group"] = pd.NA
    for cov in COV_MAP.values():
        df.loc[df[cov] == 99, cov] = pd.NA
    return df


def _write(long: pd.DataFrame, cov_cols: list[str], out_name: str, itemcov_cols=None):
    cols = ["id", "item", "resp"] + (itemcov_cols or []) + cov_cols
    long = long[cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def _melt_likert(df, item_cols, valid_max, dk_code, cov_cols):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != dk_code]
    long = long[long["resp"] != 99]
    long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
    return long.reset_index(drop=True)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cov_cols = list(COV_MAP.values())

    # ---------------- Pilot 1 ----------------
    df1 = fetch(1)
    assert df1["id"].nunique() == len(df1)

    long = _melt_likert(df1, list(PILOT1_TT_EXPECTED.keys()), valid_max=5, dk_code=6, cov_cols=cov_cols)
    long["itemcov_expected_answer"] = long["item"].map(PILOT1_TT_EXPECTED)
    _write(long, cov_cols, "carver_2017_puggs_pilot1_traits", ["itemcov_expected_answer"])

    long = _melt_likert(df1, PILOT1_CORE_DET_ITEMS, valid_max=4, dk_code=5, cov_cols=cov_cols)
    _write(long, cov_cols, "carver_2017_puggs_pilot1_det_core")

    long = _melt_likert(df1, PILOT1_GENOM_ITEMS, valid_max=4, dk_code=5, cov_cols=cov_cols)
    _write(long, cov_cols, "carver_2017_puggs_pilot1_genom_know")

    long = _melt_likert(df1, PILOT1_ATTITUDE_ITEMS, valid_max=4, dk_code=5, cov_cols=cov_cols)
    _write(long, cov_cols, "carver_2017_puggs_pilot1_attitudes")

    # ---------------- Pilot 2 ----------------
    df2 = fetch(2)
    assert df2["id"].nunique() == len(df2)

    long = _melt_likert(df2, PILOT2_TT_COLS, valid_max=5, dk_code=-1, cov_cols=cov_cols)
    _write(long, cov_cols, "carver_2017_puggs_pilot2_traits")

    for answer_key, out_name in [(PILOT2_DET_ANSWER_KEY, "carver_2017_puggs_pilot2_det_core"),
                                  (PILOT2_GENOM_ANSWER_KEY, "carver_2017_puggs_pilot2_genom_know")]:
        item_cols = list(answer_key.keys())
        long = df2.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="raw")
        long["raw"] = pd.to_numeric(long["raw"], errors="coerce")
        # 3 = don't know, 99 = missing -- both true non-response, dropped
        # rather than scored as incorrect.
        long = long[long["raw"].isin([1, 2])].copy()
        long["correct_code"] = long["item"].map(answer_key)
        long["resp"] = (long["raw"] == long["correct_code"]).astype(int)
        long = long.drop(columns=["raw", "correct_code"])
        _write(long, cov_cols, out_name)

    long = _melt_likert(df2, PILOT2_ATTITUDE_ITEMS, valid_max=4, dk_code=-1, cov_cols=cov_cols)
    _write(long, cov_cols, "carver_2017_puggs_pilot2_attitudes")


if __name__ == "__main__":
    convert()
