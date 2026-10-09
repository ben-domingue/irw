#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/kfk5j9g4xc/1
# DOI: 10.17632/kfk5j9g4xc.1 (dataset; the record names no article)
#   Azizi, A., Achak, D., Saad, E., Hilali, A., Nejjari, C., Youlyouz Marfak, I., &
#   Marfak, A. (2023). "EQ-5D-5L data for Moroccan COVID-19 survivors" [data set].
#   Mendeley Data, v1.
# Data: "EQ-5D-5L data for COVID-19 survivors.xlsx": sheet "Data" = 213 COVID-19
#       survivors (55 ICU, 158 non-ICU) x participant number + Q1-Q19; sheet
#       "Questionnaire" = the codebook (question wording and every response choice);
#       "Feuil3" is empty.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped. The Questionnaire sheet carries the EQ-5D-5L dimension
#   names and all five option statements per dimension (cheap), but the EQ-5D is
#   blocked in itemtext/instrument_rights_register.csv (EuroQol licence terms).
#   Label levels: xlsx, so no variable/value labels; the Questionnaire sheet is
#   the codebook.
#
# Table:
#   azizi_2023_eq5d5l  Q14 mobility, Q15 self-care, Q16 usual activities, Q17
#                      pain/discomfort, Q18 anxiety/depression; 1 = no problems ...
#                      5 = unable / extreme (the Questionnaire sheet's choices 1-5).
# Not shipped: Q19 (EQ-VAS, a single 0-100 rating).
# Covariates (Questionnaire sheet labels, kept as text): Q1 cov_sex, Q2 cov_age_group
#   (18-40 / 41-60 / over 60), Q3 cov_marital, Q4 cov_education, Q5 cov_employment,
#   Q6 cov_residence, Q7 cov_ses, Q8-Q12 cov_diabetes_t1, cov_diabetes_t2,
#   cov_hypertension, cov_kidney_disease, cov_cardiovascular (Yes/No), Q13 cov_icu
#   (ICU admission, Yes/No).
# id: "N° participant" (1..213, unique).

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw" / "azizi_2023"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/kfk5j9g4xc/files/"
       "f86ce460-4b85-4c5b-bb1e-a55f193ba277/file_downloaded")
NAME = "azizi_2023_eq5d5l"
ITEMS = ["Q14", "Q15", "Q16", "Q17", "Q18"]
COVS = {"Q1": "cov_sex", "Q2": "cov_age_group", "Q3": "cov_marital",
        "Q4": "cov_education", "Q5": "cov_employment", "Q6": "cov_residence",
        "Q7": "cov_ses", "Q8": "cov_diabetes_t1", "Q9": "cov_diabetes_t2",
        "Q10": "cov_hypertension", "Q11": "cov_kidney_disease",
        "Q12": "cov_cardiovascular", "Q13": "cov_icu"}
SKIP = {"Q19": "EQ-VAS, a single 0-100 rating"}


def fetch() -> Path:
    p = RAW_DIR / "eq5d5l_covid_survivors.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    src = fetch()
    d = pd.read_excel(src, "Data  ")
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (213, 20) and d["N° participant"].is_unique
    assert set(d.columns) == {"N° participant"} | set(ITEMS) | set(COVS) | set(SKIP)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    q = pd.read_excel(src, "Questionnaire", header=None)
    dims = dict(zip(q[0].astype(str).str.strip(), q[1].astype(str).str.strip()))
    assert [dims[i] for i in ITEMS] == ["Mobility", "Self-care", "Usual activities",
                                        "Pain /Discomfort", "Anxiety / Depression"]
    for c in COVS:
        d[c] = d[c].astype(str).str.strip()
    assert (d["Q13"].value_counts().to_dict() == {"No": 158, "Yes": 55})
    d = d.rename(columns={"N° participant": "id", **COVS})
    covs = list(COVS.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(ITEMS) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100
    names = [NAME]
    assert len(set(names)) == len(names)
    pv = {i: set(range(1, 6)) for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
