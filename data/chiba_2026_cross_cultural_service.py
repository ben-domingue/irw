#!/usr/bin/env python3
# Source: https://jstagedata.jst.go.jp/articles/dataset/Perceived_level_of_cross-cultural_service_perceived_absolute_decrease_in_the_level_of_routine_service_perceived_relative_decrease_in_the_level_of_routine_service_tourist_satisfaction_warmth_of_the_service_provider_and_competence_of_the_serv/32359635
# DOI: 10.50998/data.marketing.32359635.v1 (data)
#   Chiba T (2026). Perceived level of cross-cultural service, perceived absolute decrease in the
#   level of routine service, ... warmth ... and competence of the service provider [Data set].
#   J-STAGE Data. Paper: Japan Marketing Journal, 10.7222/marketing.2026.034.
# License: CC BY 4.0 (J-STAGE Data record)
# Data: QJM46-3_Chiba_data.csv, 403 Japanese domestic tourists (online panel, 9-10 Feb 2026), a
#   four-scenario between-subjects experiment. The record documents every column: Q1 level of
#   cross-cultural service (items 1-6), Q2 absolute decrease in routine service (1-5), Q3 relative
#   decrease (1-5), Q4 tourist satisfaction (6 items, 7-point semantic differential), Q5 warmth
#   (items 1-3) and competence (items 4-6) of the provider; all other items 7-point Likert,
#   1 strongly disagree .. 7 strongly agree.
# Tables (item = q<question>_<item>, from the "Q1項目1" headers):
#   chiba_2026_cross_cultural_service q1_1-6, chiba_2026_absolute_service_decrease q2_1-5,
#   chiba_2026_relative_service_decrease q3_1-5, chiba_2026_tourist_satisfaction q4_1-6,
#   chiba_2026_provider_warmth q5_1-3, chiba_2026_provider_competence q5_4-6.
# id: SAMPLENUM (the survey's serial number). The panel's 回答者ID (respondent account id) is not carried.
# Covariates (labels from the record): cov_scenario (S2: the image viewed -- high/low cross-cultural
#   service x corporate/employee level), cov_gender, cov_age_group, cov_occupation.
# Not carried: response date and time, S3 (display control).
# Item text: not shipped -- the Japanese statements are in the headers (with the service placeholder
#   "その●●●"), but the scales are adapted from the hospitality literature and not identified here.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/65387991"
SCENARIO = {1: "high cross-cultural service, corporate level", 2: "high cross-cultural service, employee level",
            3: "low cross-cultural service, corporate level", 4: "low cross-cultural service, employee level"}
GENDER = {1: "male", 2: "female", 3: "no response"}
AGE = {1: "under 20", 2: "20s", 3: "30s", 4: "40s", 5: "50s", 6: "60s", 7: "70s", 8: "80 and above"}
OCC = {1: "company employee (full-time)", 2: "company employee (contract/dispatched)",
       3: "civil servant/nonprofit staff", 4: "teacher", 5: "school staff", 6: "doctor",
       7: "medical professional", 8: "welfare professional", 9: "lawyer/CPA/tax accountant",
       10: "self-employed", 11: "part-time/temporary/freelance", 12: "full-time homemaker", 13: "student",
       14: "unemployed", 15: "other"}
TABLES = {"chiba_2026_cross_cultural_service": ["q1_%d" % i for i in range(1, 7)],
          "chiba_2026_absolute_service_decrease": ["q2_%d" % i for i in range(1, 6)],
          "chiba_2026_relative_service_decrease": ["q3_%d" % i for i in range(1, 6)],
          "chiba_2026_tourist_satisfaction": ["q4_%d" % i for i in range(1, 7)],
          "chiba_2026_provider_warmth": ["q5_1", "q5_2", "q5_3"],
          "chiba_2026_provider_competence": ["q5_4", "q5_5", "q5_6"]}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 403 and d["SAMPLENUM"].is_unique
    rename = {}
    for c in d.columns:
        m = re.match(r"^Q(\d)項目(\d)．", c)
        if m:
            rename[c] = f"q{m.group(1)}_{m.group(2)}"
    assert len(rename) == 28
    d = d.rename(columns=rename)
    col = {k: [c for c in d.columns if c.startswith(k)][0] for k in ("F1", "F2", "F3", "S2")}
    d["id"] = d["SAMPLENUM"]
    d["cov_scenario"] = d[col["S2"]].map(SCENARIO)
    d["cov_gender"] = d[col["F1"]].map(GENDER)
    d["cov_age_group"] = d[col["F2"]].map(AGE)
    d["cov_occupation"] = d[col["F3"]].map(OCC)
    covs = ["cov_scenario", "cov_gender", "cov_age_group", "cov_occupation"]
    assert d[covs].notna().all().all()
    for name, items in TABLES.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(1, 7).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 8)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
