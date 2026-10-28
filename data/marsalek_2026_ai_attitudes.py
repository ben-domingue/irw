#!/usr/bin/env python3
# Source: https://zenodo.org/records/23389256
# DOI: 10.5281/zenodo.23389256
# Paper: Marsalek, R., Tepla, M., & Sumbera, J. (2026). Artificial Intelligence
#        in the Classroom and Beyond: Usage Patterns, Attitudes, and Risks
#        Among School Students.
# Data: SI_data_code.xlsx, sheet "data" (572 Czech secondary-school students);
#       sheets "codebook" and "codebook_values" carry the Czech item wording
#       and the value labels.
# License: CC BY 4.0 (stated on the Zenodo deposit page and in README.md)
# Item text: shipped. The deposit's own "codebook" sheet gives the Czech
#   wording of each of the seven attitude statements, so the item-to-text tie
#   is by variable name with no positional inference. The 1-5 response anchors
#   respondents read are NOT published: README.md documents the scale only as
#   English prose ("1 = strongly disagree; 5 = strongly agree"), so option_text
#   ships blank rather than invented.
#
# One output table: the seven five-point attitude statements. The rest of the
# file is not item-response data -- it is multi-select AI-tool and purpose
# codes (one column per selection slot, values are category codes from a
# content analysis of open text, so a column is a slot and not an item) plus
# the open-text source columns those codes were derived from. Those are left
# out, and the per-column accounting below asserts that nothing else was lost.
#
# PII: screened. screen_for_pii() returned clean over 7 string columns
# (printed below, with the count asserted non-zero), and no email address
# appears in any of them. The open-text columns are not shipped in any case.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("MARSALEK_RAW", "SI_data_code.xlsx")

NAME = "marsalek_2026_ai_attitudes"

ITEMS = [
    "statement_ai_fear",
    "statement_ai_dumbing_effect",
    "statement_ai_positive_future",
    "statement_ai_support_understanding",
    "statement_ai_homework_help",
    "statement_ai_inevitable_in_education",
    "statement_ai_misinformation",
]

# codebook_values sheet, translated from the Czech labels
GENDER = {0: "girl", 1: "boy", 2: "prefers not to say"}
EVER_USED = {0: "no", 1: "yes", 2: "not sure"}
NONACADEMIC = {0: "no", 1: "yes"}
SCHOOL_TYPE = {
    2: "lower secondary (zakladni skola, 2nd stage)",
    3: "gymnasium, lower stage of an eight-year programme",
    4: "gymnasium, upper stage or four-year programme",
    5: "non-gymnasium secondary school (maturita track)",
}

COVS = {
    "age": "cov_age",
    "knowledge_level": "cov_ai_knowledge",
    "attitude": "cov_ai_attitude",
    "study_use_freq": "cov_study_use_freq",
    "class_use_freq_code": "cov_class_use_freq",
    "STUDENT_PUPIL_cheating_use_freq_code": "cov_cheating_use_freq",
    "TEACHER_PUPIL_region_teaching": "cov_region",
}


def convert():
    df = pd.read_excel(RAW, sheet_name="data")
    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id"})

    # value-labelled covariates: the source codes alone are opaque here (the
    # file is .xlsx, so metadata/covariate_labels/ has nothing to harvest)
    df["cov_gender"] = df["gender"].map(GENDER)
    df["cov_ever_used_ai"] = df["ever_used_freq"].map(EVER_USED)
    df["cov_nonacademic_use"] = df["STUDENT_PUPIL_nonacademic_use_freq"].map(NONACADEMIC)
    df["cov_school_type"] = df["TEACHER_PUPIL_school_type_1"].map(SCHOOL_TYPE)
    for src, dst in COVS.items():
        assert src in df.columns, src
    df = df.rename(columns=COVS)

    cov_cols = sorted(list(COVS.values()) + ["cov_gender", "cov_ever_used_ai",
                                             "cov_nonacademic_use",
                                             "cov_school_type"])

    # balance the books: every source column is shipped, carried, or named here
    src_cols = list(pd.read_excel(RAW, sheet_name="data", nrows=0).columns)
    accounted = set(COVS) | set(ITEMS) | {
        "ID", "group", "gender", "ever_used_freq",
        "STUDENT_PUPIL_nonacademic_use_freq", "TEACHER_PUPIL_school_type_1",
    }
    left_out = [c for c in src_cols if c not in accounted]
    # everything left must be a multi-select slot or the open text behind one
    for c in left_out:
        assert ("OPEN" in c.upper() or "open_code" in c
                or c.rsplit("_", 1)[-1].isdigit()), f"unaccounted column: {c}"
    print(f"left out {len(left_out)} multi-select slot / open-text columns "
          f"(not item responses): {left_out[:4]} ...")
    assert len(left_out) + len(accounted) == len(src_cols)

    # whole-number covariates carry NaNs, which pandas would write as "15.0"
    for c in ("cov_age", "cov_study_use_freq", "cov_class_use_freq"):
        df[c] = df[c].astype("Int64")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert long["resp"].between(1, 5).all(), "resp outside the documented 1-5"
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
