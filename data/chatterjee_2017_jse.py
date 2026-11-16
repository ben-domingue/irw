#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/LOGUCL
# DOI: 10.3352/jeehp.2017.14.33
# Paper: Chatterjee A, Ravikumar R, Singh S, Chauhan PS, Goel M (2017).
#   Clinical empathy in medical students in India measured using the Jefferson
#   Scale of Empathy-Student Version. Journal of Educational Evaluation for
#   Health Professions 14:33.
# Data: Harvard Dataverse 10.7910/DVN/LOGUCL, "Jeehp_14_33_raw data.xlsx"
#   (file 3093248; the paper's Supplement 1): 418 medical undergraduates at
#   University College of Medical Sciences, Delhi, July 2017 x 45 columns.
# License: CC0 1.0 (Dataverse record).
# Codebook: none; codes from the paper (Methods and Tables 1-2).
#
# Worked in overnight lane C 2026-11-10 (JEEHP collection); held that night,
# ruled ship by Ben 2026-11-11.
#
# ONE table: chatterjee_2017_jse, Jefferson Scale of Empathy - Student version
#   (English), Item_1..Item_20 as answered, 1-7 (1 = strongly disagree ..
#   7 = strongly agree). The deposit's reversed copies Item_k_RS (= 8 - x, on
#   the 10 negatively worded items 1, 3, 6, 7, 8, 11, 12, 14, 18, 19) are not
#   shipped; summing the reversed set reproduces Total_Score on every row.
# Checks against the paper: N = 418, 331 male / 87 female, total mean 96.01
#   (SD 14.56), hostel 266 / home 147 -- all reproduce.
# DATA NOTE -- POSSIBLE ROUNDED IMPUTATIONS: the paper's scoring allowed up to
#   4 blank items per form, each replaced by the respondent's mean item score.
#   The file holds integers only and no blanks, so any such replacement was
#   rounded and cannot be told apart from a real answer. Shipped as deposited.
# Not shipped: Total_Score and the three factor scores (composites); who
#   decided the student would join MBBS and its free-text "other" field,
#   intended specialty and sub-specialty codes (undocumented codes).
# Covariates: age, gender (1 male, 2 female, from the paper's counts),
#   semester (1/3/5/7), residence (1 hostel, 2 home, from Table 2's counts).
# `id` = Sl.no.
#
# Item text: NOT SHIPPED. The deposit has item numbers only; the JSE is a
#   copyrighted instrument (Thomas Jefferson University).

import os
import sys
from io import BytesIO

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.harvard.edu/api/access/datafile/3093248"
RAW = os.environ.get("CHATTERJEE2017_RAW")
NAME = "chatterjee_2017_jse"
REVERSED = [1, 3, 6, 7, 8, 11, 12, 14, 18, 19]


def load():
    if RAW:
        return pd.read_excel(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content))


def main():
    d = load()
    assert d.shape == (418, 45), d.shape
    items = [f"Item_{i}" for i in range(1, 21)]
    assert d[items].isin(range(1, 8)).all().all()
    for i in REVERSED:
        assert (d[f"Item_{i}_RS"] == 8 - d[f"Item_{i}"]).all()
    scored = [f"Item_{i}_RS" if i in REVERSED else f"Item_{i}" for i in range(1, 21)]
    assert (d[scored].sum(axis=1) == d["Total_Score"]).all()
    assert round(d["Total_Score"].mean(), 2) == 96.01
    assert d["Gender"].value_counts().to_dict() == {1: 331, 2: 87}
    assert d["Res_stat"].value_counts().to_dict() == {1: 266, 2: 147}
    d["id"] = d["Sl.no"]
    assert d["id"].is_unique
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_gender"] = d["Gender"].map({1: "male", 2: "female"})
    d["cov_semester"] = d["Sem"].astype(int)
    d["cov_residence"] = d["Res_stat"].map({1: "hostel", 2: "home"})
    covs = ["cov_age", "cov_gender", "cov_semester", "cov_residence"]
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    long["cov_age"] = long["cov_age"].astype("Int64")
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    pv = {i: set(range(1, 8)) for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(long, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:200]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    main()
