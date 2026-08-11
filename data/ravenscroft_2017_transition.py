#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179904
# DOI: 10.1371/journal.pone.0179904
#
# "Factors associated with successful transition among children with
# disabilities in eight European countries" (PLOS ONE, 2017). S2 File (CSV)
# contains raw responses from 306 parents to a 41-question online survey
# about their child's school transition experience. The full survey mixes
# response formats (binary "who did you meet" checkboxes, free-text /
# categorical fields, and ordinal 1-5 rating items). This script keeps only
# the ordinal 1-5 rating items -- the subset the paper itself analyzed via
# PCA as a single instrument battery -- and drops the checkbox/categorical
# columns, which are not on a comparable response scale.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "automated_finding", "raw_downloads",
                    "ravenscroft_2017_pone0179904_s2data.csv")

ITEM_COLS = [
    "Transition Involvement",
    "Frequency school visit",
    "Parent involved in transfer decision",
    "Child involved in transfer decision",
    "Support plan developed by professionals",
    "Parental involvement in child educational plan",
    "Frequency of review of educational plan",
    "Extent plan developed ahead of transition",
    "Satisfaction with info",
    "Info child friendly",
    "Satisfaction with resources",
    "Extent child adjusted",
    "Staff works as team",
    "Contact with school and agencies",
    "Extent organisations work together",
    "Parental involvement in defining transition goals",
    "Child involvement in defining transition goals",
    "Parental involvement in school decision making",
    "Child involvement in decision making",
    "Accessibility of school",
    "School inclusiveness",
    "Curriculum flexibility",
    "Child included in recreational activities",
    "Child involved in peer support",
    "Satisfied with transition",
]

COV_RENAME = {
    "Language": "cov_language",
    "Respondant gender": "cov_respondent_gender",
    "Country": "cov_country",
    "Child age": "cov_child_age",
    "Child gender": "cov_child_gender",
    "School": "cov_school_type",
}


def convert():
    df = pd.read_csv(SRC)
    df = df.rename(columns={"RespondentID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "ravenscroft_2017_transition"
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
