#!/usr/bin/env python3
# Source: https://osf.io/3649s/
# DOI: 10.17605/OSF.IO/3649S (data; no paper yet)
#   Delem M (2026). Working memory representational strategies in aphantasia (WM-FTT). OSF.
# License: CC BY 4.0 (OSF node licence)
# Data: "v3 Data/Processed data/all_data_surveys.csv" (one row per participant, 118 rows, 117 ids,
#   across three versions of the task; mostly French-speaking online volunteers) and codebook.pdf
#   in the same folder.
#
# Tables:
#   delem_2026_vviq -- Vividness of Visual Imagery Questionnaire (Marks 1973), 16 items vviq_q01..q16,
#     1 perfectly clear and vivid - 5 no image at all (codebook). Higher = weaker imagery.
#   delem_2026_osivq -- Object-Spatial Imagery and Verbal Questionnaire (Blazhenkova & Kozhevnikov
#     2009), the 34 items administered (14 object, 11 spatial, 9 verbal; the item code's last letter),
#     1 totally disagree - 5 totally agree. Stored AS ANSWERED: per the codebook, v1/v2 store the
#     reverse-keyed items q02v, q09v, q41v, q42s unreversed and v3 stores them already reversed, so
#     the v3 values of those four are put back (6 - x). Check: reversing those four for everyone
#     then reproduces the file's object_score, spatial_score and verbal_score for all 116
#     participants with OSIVQ data.
#   Not shipped: NIEQ (only percentages per characteristic), the WM-FTT task (per-stimulus recall
#   scores in all_data_full.csv), strategy items.
# id: the deposit's participant id (a random string). One person took part in v1 and v3; only the
#   v1 row is kept. Two participants have no questionnaire data; other blank cells are not rows.
# Covariates: cov_version (task version v1/v2/v3), cov_language (UI language en/fr), cov_age,
#   cov_gender (the free-text gender: "f" -> female, "m" -> male, the five self-descriptions, all
#   naming non-binary or agender, -> non-binary). country, job, education, field, where_from and
#   language columns are not carried.
# Item text: not shipped -- the codebook withholds the wording ("copyrighted by the original scale
#   authors"); VVIQ and OSIVQ are third-party.
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
URL = "https://osf.io/download/g62t4/"
REV = ["osivq_q02v", "osivq_q09v", "osivq_q41v", "osivq_q42s"]


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 118
    vviq = [f"vviq_q{i:02d}" for i in range(1, 17)]
    osivq = [c for c in d.columns if c.startswith("osivq_q")]
    assert len(osivq) == 34
    v3 = d["version"] == "v3"
    d.loc[v3, REV] = 6 - d.loc[v3, REV]  # back to as-answered, like v1/v2
    scored = d[osivq].copy()
    scored[REV] = 6 - scored[REV]
    for suf, col in (("o", "object_score"), ("s", "spatial_score"), ("v", "verbal_score")):
        items = [c for c in osivq if c.endswith(suf)]
        ok = d[col].isna() | (scored[items].sum(axis=1) == d[col])
        assert ok.all(), col
    d = d.drop_duplicates("id", keep="first")
    d["cov_version"] = d["version"]
    d["cov_language"] = d["language"]
    d["cov_age"] = d["age"]
    g = d["gender"].str.strip().str.lower()
    d["cov_gender"] = g.map({"f": "female", "m": "male"}).fillna("non-binary")
    covs = ["cov_version", "cov_language", "cov_age", "cov_gender"]
    for name, items in (("delem_2026_vviq", vviq), ("delem_2026_osivq", osivq)):
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all() and not t.duplicated(["id", "item"]).any()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        gate(t)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
