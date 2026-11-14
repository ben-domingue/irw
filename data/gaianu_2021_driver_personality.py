#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/r2bdvzkzbj/3
# DOI: 10.17632/r2bdvzkzbj.3 (data)
#   Gaianu P-A (2021). Theory Of Planned Behavior: A Path From Personality Traits To Traffic Violations
#   [Data set]. Mendeley Data, V3.
# License: CC BY 4.0 (Mendeley Data)
# Data: "BD_TPB a path fom PT to VIO_2021.sav", 236 Romanian drivers aged 18-67, recruited through
#   online survey campaigns on social media. One row = one respondent; id = row order. No names,
#   emails or IP addresses in the file.
#
# IPIP-NEO-300 (Romanian, Iliescu et al. 2015), resp 1-5. THE DEPOSIT STORES IT KEYED, AND THIS SCRIPT
#   UN-REVERSES IT TO THE ANSWERS AS GIVEN. Columns are <facet>_<j>, the j-th item of a facet. Each
#   variable label is the Romanian item with its IPIP-NEO-300 administration number (n1_1 = "1. Imi fac
#   griji...", n1_6 = "151. ..."). All 300 numbers and wordings line up, in order, with the IPIP
#   facet key (ipip.ori.org/newNEOFacetsKey.htm): in every facet the + keyed items come first, then the
#   - keyed ones. The stored values are the keyed ones: every deposited facet score (n1..c6) is the
#   plain sum of its 10 stored items, every domain score (N..C) is the plain sum of its 6 facets, and
#   item-rest correlations are positive except where noted below. The script therefore stores
#   6 - x for the 148 - keyed items (MINUS_COUNT below) and asserts the facet sums first.
#   a2_5 is the one item whose Romanian wording reverses the English one: IPIP "Know how to get around
#   the rules" (- keyed) became "Stiu sa ma supun regulilor" ("I know how to obey the rules"). The
#   depositors keyed it as the English item, so its keyed item-rest r is -0.39. As shipped (the answer
#   as given), it is simply a positively worded Morality item. Analysts building facet scores from
#   these data should treat a2_5 as + keyed.
#   n4_9 is blank for 2 respondents.
# DBQ (Romanian version, Sarbescu 2013), 27 items, resp 1-6. No reversals (every subscale total is
#   the plain sum). Names give the subscale: dbq_n lapses, dbq_g errors, dbq_ao ordinary violations,
#   dbq_ag aggressive violations.
# TPB questionnaire (Gaianu et al. 2020), resp 1-7, asked about each of seven driving situations
#   S1-S7 (the record lists them: speeding to impress, rushing, illegal overtaking, showing
#   indignation, competing, drink-driving, handheld phone). Item = s<k>q<q>_<construct>. One table per
#   construct; each deposited situation total is the plain sum of its items:
#     gaianu_2021_tpb_intention           -- q1-q3 (21 items)
#     gaianu_2021_tpb_attitude            -- q41-q413, 13 semantic differentials (91 items)
#     gaianu_2021_tpb_subjective_norm     -- q5-q7 (21 items)
#     gaianu_2021_tpb_descriptive_norm    -- q8-q10 (21 items)
#     gaianu_2021_tpb_perceived_control   -- q12-q15 (28 items; 214 of the 236 answered some, many skipped it)
#   One s2q15_ccp cell is 21 (outside 1-7) and is dropped as a data-entry error.
#   Not shipped: q11 ("trecere", "I completely rule out this behaviour"), which is in no deposited score.
# Covariates: cov_age (years), cov_gender, cov_education, cov_driving_purpose (CI_1, Romanian value
#   labels translated), cov_driving_experience (CI_2, years). Not carried: CI_3 self-reported distance
#   (units not documented).
# Item text: not shipped -- the variable labels carry the Romanian wording, but the file lost the
#   letters a-breve, s-comma and t-comma (each stored as "?"), so the administered text cannot be
#   recovered exactly.
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/r2bdvzkzbj/files/"
       "c9ac777f-bf20-4268-8f27-110b0cc3e307/file_downloaded")
FACETS = [f"{t}{k}" for t in "neoac" for k in range(1, 7)]
# number of - keyed items per facet (IPIP facet key); they are items 11-m..10 of the facet
MINUS_COUNT = {"n1": 5, "n2": 5, "n3": 3, "n4": 4, "n5": 5, "n6": 5, "e1": 5, "e2": 5, "e3": 5, "e4": 5,
               "e5": 2, "e6": 2, "o1": 4, "o2": 5, "o3": 5, "o4": 6, "o5": 5, "o6": 7, "a1": 4, "a2": 8,
               "a3": 5, "a4": 7, "a5": 6, "a6": 6, "c1": 4, "c2": 5, "c3": 5, "c4": 3, "c5": 5, "c6": 7}
GENDER = {1: "male", 2: "female"}
EDU = {1: "lower secondary or less", 2: "vocational school", 3: "high school", 4: "post-secondary",
       5: "university", 6: "master's or above"}
PURPOSE = {1: "professional driver", 2: "regularly for work", 3: "occasionally for work", 4: "outside work only"}
TPB = {"gaianu_2021_tpb_intention": ("i", ["1", "2", "3"]),
       "gaianu_2021_tpb_attitude": ("a", [f"4{j}" for j in range(1, 14)]),
       "gaianu_2021_tpb_subjective_norm": ("ns", ["5", "6", "7"]),
       "gaianu_2021_tpb_descriptive_norm": ("nd", ["8", "9", "10"]),
       "gaianu_2021_tpb_perceived_control": ("ccp", ["12", "13", "14", "15"])}


def write(d, name, items, covs, lo, hi):
    t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    assert t["resp"].isin(range(lo, hi + 1)).all(), name
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':
        c = requests.get(json.loads(c)["url"], timeout=120).content
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(c)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 236
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Age"]
    d["cov_gender"] = d["Gen"].map(GENDER)
    d["cov_education"] = d["Edu"].map(EDU)
    d["cov_driving_purpose"] = d["CI_1"].map(PURPOSE)
    d["cov_driving_experience"] = d["CI_2"]
    covs = ["cov_age", "cov_gender", "cov_education", "cov_driving_purpose", "cov_driving_experience"]
    assert d[covs[1:4]].notna().all().all()

    # IPIP-NEO-300: check the stored values are keyed, then un-reverse the - keyed items
    lab = meta.column_names_to_labels
    ipip = []
    for f in FACETS:
        cols = [f"{f}_{j}" for j in range(1, 11)]
        assert np.allclose(d[cols].sum(axis=1), d[f], equal_nan=True), f
        assert int(lab[cols[0]].split(".")[0]) < int(lab[cols[-1]].split(".")[0]), f
        ipip += cols
    for dom in "NEOAC":
        assert np.allclose(d[[f"{dom.lower()}{k}" for k in range(1, 7)]].sum(axis=1), d[dom]), dom
    assert d[ipip].isna().sum().sum() == 2 == d["n4_9"].isna().sum()
    for f, m in MINUS_COUNT.items():
        for j in range(11 - m, 11):
            d[f"{f}_{j}"] = 6 - d[f"{f}_{j}"]
    write(d, "gaianu_2021_ipip_neo300", ipip, covs, 1, 5)

    dbq = [c for c in d.columns if c.startswith("dbq_") and c[-1].isdigit()]
    assert len(dbq) == 27
    for sc in ["n", "g", "ao", "ag"]:
        cs = [c for c in dbq if c.split("_")[1].rstrip("0123456789") == sc]
        assert np.allclose(d[cs].sum(axis=1), d[f"dbq_{sc}"]), sc
    write(d, "gaianu_2021_dbq", dbq, covs, 1, 6)

    bad = d["s2q15_ccp"] == 21
    assert bad.sum() == 1
    d.loc[bad, "s2q15_ccp"] = np.nan
    for name, (con, qs) in TPB.items():
        items = []
        for k in range(1, 8):
            cs = [f"s{k}q{q}_{con}" for q in qs]
            full = d[cs].notna().all(axis=1) & ~bad
            assert np.allclose(d.loc[full, cs].sum(axis=1), d.loc[full, f"S{k}_{con}"]), (name, k)
            items += cs
        write(d, name, items, covs, 1, 7)


if __name__ == "__main__":
    main()
