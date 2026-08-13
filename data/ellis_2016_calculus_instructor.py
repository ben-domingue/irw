#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0157447
# DOI: 10.1371/journal.pone.0157447
#
# "Women 1.5 Times More Likely to Leave STEM Pipeline after Calculus Compared
# to Men: Lack of Mathematical Confidence a Potential Culprit". S2 File (.s003)
# is the raw end-of-semester survey data across many US Calculus I sections;
# S2 File Data README (.s004) is the codebook. Two clean 6-point Likert item
# batteries about the instructor are used here (composite/derived and
# non-Likert columns -- SAT/ACT scores, final grades, single yes/no items,
# checklist reason items -- are excluded):
#   - Q18Post_* (8 items): perceptions of instructor quality
#   - Q19Post_* (8 items): frequency of instructor classroom practices
# `Institution` is a random, anonymous per-institution identifier per the
# codebook (not PII) and is kept as a covariate. CC BY 4.0.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0157447.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "ellis_2016_calc_instrqual": [
        "Q18Post_AskedQs", "Q18Post_Listened", "Q18Post_Applications",
        "Q18Post_Time", "Q18Post_ProblemSolver", "Q18Post_Explanations",
        "Q18Post_Appointments", "Q18Post_Discouraged",
    ],
    "ellis_2016_calc_instrprac": [
        "Q19Post_SpecificProblems", "Q19Post_WorkTogether",
        "Q19Post_Discussion", "Q19Post_Presentations",
        "Q19Post_Individually", "Q19Post_Lecture",
        "Q19Post_AskQuestions", "Q19Post_ExplainThinking",
    ],
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.content.decode("latin1")))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns={"Institution": "cov_institution"})

    cov_cols = ["cov_institution"]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # valid range is 1-6 per codebook (strongly disagree..strongly agree
        # / not at all..very often)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 6)]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
