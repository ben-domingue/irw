#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/QQGCLX
# DOI: 10.7910/DVN/QQGCLX (data); paper 10.1017/psrm.2024.42
#   Elkjaer MA, Wlezien C (2024). Estimating public opinion from surveys: the impact of including
#   a "don't know" response option in policy preference questions. Political Science Research and
#   Methods. (Paper CC BY 4.0.)
# License: CC0 1.0 (Harvard Dataverse)
# Data: Data.dta -- long file, one row per respondent x topic: 4,810 US adults from a pre-registered
#   online survey experiment run in three rounds, 8 policy questions each (38,480 rows, one per
#   respondent x topic, none duplicated).
#
# Table: elkjaer_2024_policy_support -- support (1) / oppose (0) for 8 policy proposals. Topic
#   names are the titles Main_analysis.do gives topics 1-8: infrastructure (infrastructure bill),
#   min_wage (raise the minimum wage), estate_tax (repeal the estate tax), cap_gains_tax (tax
#   capital gains as income), border_security (tighten border security), transgender_military
#   (allow transgender people in the military), roe, vaccine_mandates.
#   `roe` is kept as stored: Main_analysis.do reverses topic 7 before analysis so that 1 means
#   "keep Roe v. Wade", which means the stored 1 is support for the question as worded, the
#   reverse of keeping Roe.
#   treat = 1 when the respondent was randomly offered an explicit "don't know" option (the
#   experiment). A "don't know" or a skip has no support value and is not a row (2,878 cells).
# id: respondent_id. Covariates: cov_round (survey round 1-3), cov_gender (female 1 -> female, 0 -> male),
#   cov_age, cov_party_id (pid labels), cov_race (race labels), cov_political_knowledge (the
#   deposit's 0-5 knowledge index; its items are not in the file). Education and liberal-
#   conservative self-placement are stored as unlabelled codes; not shipped. `sure` (certainty
#   about the answer, 1-4) is a follow-up to each item, not shipped.
# Item text: not shipped -- the deposit has only the short topic titles in the do-file; the
#   question wording is in the paper's appendix.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/10278041?format=original"
TOPIC = {1: "infrastructure", 2: "min_wage", 3: "estate_tax", 4: "cap_gains_tax", 5: "border_security",
         6: "transgender_military", 7: "roe", 8: "vaccine_mandates"}
PID = {2: "Democrat", 3: "Independent", 4: "Other", 5: "Republican"}
RACE = {2: "Asian or Asian-American", 3: "Black or African-American", 4: "Hispanic or Latino",
        5: "Middle Eastern", 6: "Native American", 7: "Other", 8: "Two or more races", 9: "White"}


def main():
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    # the .dta has non-UTF-8 strings in columns we do not use; read the numeric ones only
    d = pd.read_stata(io.BytesIO(r.content), convert_categoricals=False,
                      columns=["respondent_id", "topic", "round", "treatment", "support", "female", "age",
                               "pid", "race", "pol_know"])
    assert len(d) == 38480 and d["respondent_id"].nunique() == 4810
    assert not d.duplicated(["respondent_id", "topic"]).any()
    d["id"] = d["respondent_id"].astype(int)
    d["item"] = d["topic"].map(TOPIC)
    d["treat"] = d["treatment"].astype(int)
    d["cov_round"] = d["round"].astype(int)
    d["cov_gender"] = d["female"].map({1: "female", 0: "male"})
    d["cov_age"] = d["age"]
    d["cov_party_id"] = d["pid"].map(PID)
    d["cov_race"] = d["race"].map(RACE)
    d["cov_political_knowledge"] = d["pol_know"]
    assert d["item"].notna().all()
    print("DK/skip cells dropped:", d["support"].isna().sum())
    t = d.dropna(subset=["support"]).copy()
    t["resp"] = t["support"].astype(int)
    assert t["resp"].isin([0, 1]).all()
    covs = ["cov_round", "cov_gender", "cov_age", "cov_party_id", "cov_race", "cov_political_knowledge"]
    t = t[["id", "item", "resp", "treat"] + covs].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "elkjaer_2024_policy_support.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
