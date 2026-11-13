#!/usr/bin/env python3
# Source: original deposit https://doi.org/10.14284/625 (VLIZ Marine Data Archive / IMIS dataset 8385)
#   Hooyberg A, Roose H, Lonneville B, et al. (2023). Survey data linking coastal visit behaviours to
#   socio-demographic and health profiles [Data set]. Flanders Marine Institute (VLIZ).
#   Paper: Hooyberg A et al. (2023), Psychologica Belgica, doi 10.5334/pb.1050 (a companion study).
# DOI: 10.14284/625 (data, original). Files read from the verbatim re-deposit
#   https://zenodo.org/records/13844677 (AISDL "BMF CP 85"; the same processed file is in 22654002).
# License: CC BY 4.0 -- the ORIGINATOR's licence (marineinfo.org dataset 8385, "This dataset is
#   licensed under a Creative Commons Attribution 4.0 International License"); the re-deposit is
#   CC BY 4.0 too. Credit is to Hooyberg et al.
# Data: Hooyberg_SurveyCoastalVisits_Processed.csv + _Codebook.csv (cp1252), 1,939 adults from the
#   Flemish population (2022, Dutch-language Qualtrics), weighted sample described in the codebook.
#
# Tables (5-point items 1 Never .. 5 Always unless noted; item = the codebook's New_name):
#   hooyberg_2023_coastal_experiences -- 27 experiences at the coast ("Being fascinated",
#     "Having peace of mind", "Feeling anxious", ...), stored as answered.
#   hooyberg_2023_coastal_activities  -- 32 activities (walking at the beach, cycling, ...);
#     the data column WatchBotes is the codebook's WatchBoats, renamed to it.
#   hooyberg_2023_coastal_barriers    -- 18 reasons for not visiting more often.
#   hooyberg_2023_coastal_company     -- 7 "with whom" frequencies (alone, partner, ...); item =
#     Coast<New_name> (CoastAlone, CoastWithPartner, ...; a bare WithPartner or Family reads as a
#     household covariate).
#   hooyberg_2023_sf36_mental_health  -- the 9 SF-36 vitality/mental-health items, 1-6 as stored:
#     the codebook marks the positive items "(6-1)" and the negative ones "(1-6)", i.e. all are
#     coded so that higher = better (every item correlates positively with the rest).
#   Respondents who did not visit the coast in the previous year answered the visit blocks about
#   their last visit (the codebook's *_ever questions, merged into the same columns in this file);
#   cov_visit_time carries which (Visited_Last.year 1,304 / Visited_Not.last.year 627 / never 8).
# Not shipped: NatureConnectedness (one item); visit counts and towns (counts / yes-no lists);
#   codebook "Duration" timing columns; composites (MentalHealth, SF36MH.*.mean -- flagged
#   "Wrongly calculated" in the codebook). DROPPED for privacy, in no form: all PostalCode* columns
#   and the distances computed from them (geographic codes); Chronic_*_spec free-text diagnoses and
#   the categories derived from them; BirthYear (age in years is kept).
# id: row number (the file's ID is a Qualtrics response id). Covariates: cov_age, cov_gender
#   (Female/Male), cov_education (as worded), cov_visit_time.
# Item text: not shipped -- the English questionnaire (Hooyberg_SurveyCoastalVisits_ENG.docx) and the
#   codebook descriptions carry the wording; the survey was administered in Dutch (codebook
#   Description_NL), so a translated-substitute pass is needed.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
BASE = "https://zenodo.org/api/records/13844677/files/{}/content"


def get(name, **kw):
    r = requests.get(BASE.format(name), timeout=180)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), **kw)


def main():
    d = get("Hooyberg_SurveyCoastalVisits_Processed.csv")
    cb = get("Hooyberg_SurveyCoastalVisits_Codebook.csv", encoding="cp1252")
    assert len(d) == 1939 and d["ID"].is_unique
    d = d.rename(columns={"WatchBotes": "WatchBoats"}).copy()
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Age"]
    d["cov_gender"] = d["Sex"]
    d["cov_education"] = d["Education"].str.replace("&#39;", "'", regex=False)
    d["cov_visit_time"] = d["Visit_Time"]
    covs = ["cov_age", "cov_gender", "cov_education", "cov_visit_time"]
    sel = cb["Population"].isin(["Visited_1y", "All"])
    blocks = {f"hooyberg_2023_coastal_{k.lower()}": (list(cb.loc[sel & (cb["Category"] == k), "New_name"]), 5)
              for k in ["Experiences", "Activities", "Barriers", "Company"]}
    blocks["hooyberg_2023_sf36_mental_health"] = (
        ["SF36MH_Liveliness", "SF36MH_Nervosity", "SF36MH_DepressionTrouble", "SF36MH_Relaxation",
         "SF36MH_Vitality", "SF36MH_DepressionDown", "SF36MH_Exhaustion", "SF36MH_Happinness",
         "SF36MH_Tiredness"], 6)
    want = {"hooyberg_2023_coastal_experiences": 27, "hooyberg_2023_coastal_activities": 32,
            "hooyberg_2023_coastal_barriers": 18, "hooyberg_2023_coastal_company": 7,
            "hooyberg_2023_sf36_mental_health": 9}
    for name, (items, top) in blocks.items():
        assert len(items) == want[name] and all(c in d for c in items), name
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        if name.endswith("_company"):
            t["item"] = "Coast" + t["item"]
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, top).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
