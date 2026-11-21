#!/usr/bin/env python3
# Source: https://repository.lboro.ac.uk/articles/dataset/_/29314136
# DOI: 10.17028/rd.lboro.29314136 (data)
#   Ghulman S (2025). Dataset: Public Perceptions of Saudi Arabia's Nation Brand (Online Questionnaire) [Data set].
#   Loughborough University.
# License: CC BY-NC 4.0 (repository record metadata); derived license carries the NC term.
# Data: "... (SPSS).sav", 543 respondents to an online questionnaire (2021, Study 1 of a PhD project), Arabic/English.
#   Questions 5 and 7-16 are three-option factual questions about Saudi Arabia (continent, size, oil reserves,
#   largest animal, capital, flag colour, provinces, religion, seas, beaches, UNESCO sites); the .sav value labels
#   give the options, and the file's own score columns (Q5.Score, Q.7 .. Q.16) mark each answer right (1) or wrong (0).
#   Checked: every score equals (answer == the keyed option), and TotalScore is their sum for all 543 rows.
# Table: ghulman_2025_saudi_knowledge -- item = the .sav variable name of the question (Continent, Capital, ...),
#   resp = the deposit's own score. The deposit scores an unanswered question 0; here it is missing instead (5-25
#   per question). Open-ended questions 6 and 17-20 are not carried.
# Covariates: cov_gender (Female/Male/Other; the label "NA" -> missing), cov_generation, cov_nationality_group
#   (all from the .sav value labels). id = the file's ResponseID (S1P01..).
# Item text: not shipped -- the stems are the .sav variable labels and the options its value labels; the key is the
#   depositor's. A cheap build later.
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/55371329"
NAME = "ghulman_2025_saudi_knowledge"
SCORES = {"Continent": "Q5.Score", "GeographicalSizeComparison": "Q.7", "OilReserves": "Q.8", "LargestAnimal": "Q.9",
          "Capital": "Q.10", "FlagColour": "Q.11", "Provinces": "Q.12", "Religion": "Q.13", "SeasAndOceans": "Q.14",
          "TypeOfBeaches": "Q.15", "UnescoWorldHeritageSites": "Q.16"}
COVS = {"Gender": "cov_gender", "Generation": "cov_generation", "Nationality": "cov_nationality_group"}


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
    try:
        d, meta = pyreadstat.read_sav(f.name)
    finally:
        os.unlink(f.name)
    assert len(d) == 543 and d["ResponseID"].is_unique
    assert (d[list(SCORES.values())].sum(axis=1) == d["TotalScore"]).all()
    for ans, sc in SCORES.items():
        right = d.loc[d[sc] == 1, ans].dropna().unique()
        assert len(right) == 1, ans                                   # one keyed option per question
        assert ((d[ans] == right[0]) == (d[sc] == 1)).all(), ans     # score == (answer == key)
    labels = meta.variable_value_labels
    for src, cov in COVS.items():
        d[cov] = d[src].map(labels[src])
        assert d[cov].notna().sum() == d[src].notna().sum(), cov
    d["cov_gender"] = d["cov_gender"].replace({"NA": pd.NA}).str.lower()
    d = d.rename(columns={"ResponseID": "id"})
    covs = list(COVS.values())
    w = d[["id"] + covs].copy()
    for ans, sc in SCORES.items():
        w[ans] = d[sc].where(d[ans].notna())
    t = w.melt(id_vars=["id"] + covs, var_name="item", value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert set(t["resp"]) == {0, 1}
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t, permitted_values=[0, 1]) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / f"{NAME}.csv", index=False)
    print(NAME, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
