#!/usr/bin/env python3
# Source: https://osf.io/qn9a2/ ("Data and results" folder)
# DOI: 10.17605/OSF.IO/QN9A2 (data); paper Petrova D, Mas G, Navarrete G, Tello Rodriguez T,
#   Ortiz PJ, Garcia-Retamero R (2019). Cancer screening risk literacy of physicians in training:
#   An experimental study. PLoS ONE 14(7): e0218821.
# License: CC BY 4.0 (OSF node licence)
# Data: "Cancer screening risk literacy R1.sav", 172 Peruvian medical students (externos/internos)
#   and residents, Spanish-language questionnaire in four versions (A-D: 2 x 2 of whether the
#   screening test was effective and whether patient demand was mentioned). Scoring is the authors'
#   own, in "Variables R1.sps" in the same folder; the scored 0/1 variables are in the .sav and are
#   used as stored (the authors score every -66 "no response" as incorrect).
#
# Tables (item = the .sav variable name):
#   petrova_2019_screening_beliefs -- Screen1-5, 1-7 agreement with statements favouring screening
#     (the authors sum them, no reversal); 2 blank cells are not rows.
#   petrova_2019_numeracy -- num1.1-num3.1 (Schwartz numeracy) and num4.1-num7.1 (Berlin Numeracy
#     Test), 0/1; resp_raw = the answer given (num1num, num2..num7).
#   petrova_2019_screening_statistics -- cancerstat1-3 (knowledge of screening statistics) and
#     comp1.1-comp6.1 (comprehension of the screening evidence presented), 0/1; the key for comp1.1
#     and comp3.1 depends on the version (effective or not), as in the authors' syntax.
#   petrova_2019_science_literacy -- sci1-sci3, 0/1 (scored from sci8, sci9.1, sci9.2).
# Not shipped: perceived benefits/harms/recommendation and shared-decision items (single items /
#   pairs); free-text and institution columns. Place of origin (LugarProcedencia) dropped (geographic).
# id: IDparticipante. Covariates: cov_age, cov_gender, cov_training (externo/interno/residente),
#   cov_stats_training (si/no), cov_version (A-D), cov_test_effective, cov_patient_demand.
# Item text: not shipped -- Spanish stems are the .sav variable labels for the raw items, but the
#   scored items' correct answers depend on the version, and the numeracy items are third-party
#   (Schwartz 1997; Cokely et al. 2012).
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
URL = "https://osf.io/download/2zndg/"
RAW = {"num1.1": "num1num", "num2.1": "num2", "num3.1": "num3", "num4.1": "num4",
       "num5.1": "num5", "num6.1": "num6", "num7.1": "num7"}


def melt(d, items, covs):
    t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    return t.dropna(subset=["resp"])


def save(t, name, lo, hi, covs, extra=()):
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(lo, hi).all(), name
    t = t[["id", "item", "resp", *extra] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 172 and d["IDparticipante"].is_unique
    vl = meta.variable_value_labels
    d["id"] = d["IDparticipante"].astype(int)
    d["cov_age"] = d["Edad"]
    d["cov_gender"] = d["gender"].map(vl["gender"])
    d["cov_training"] = d["AnoAcademico"].map(vl["AnoAcademico"])
    d["cov_stats_training"] = d["CapacitacionEstadistica"]
    d["cov_version"] = d["Version"]
    d["cov_test_effective"] = d["effective"].map(vl["effective"])
    d["cov_patient_demand"] = d["demand"].map(vl["demand"])
    covs = ["cov_age", "cov_gender", "cov_training", "cov_stats_training", "cov_version",
            "cov_test_effective", "cov_patient_demand"]
    # authors' totals reproduce from the scored items
    assert (d[list(RAW)].sum(axis=1) == d["numeracy"]).all()
    assert (d[["sci1", "sci2", "sci3"]].sum(axis=1) == d["sciliteracy"]).all()
    assert (d[["comp1.1", "comp3.1", "comp4.1", "comp5.1", "comp6.1"]].sum(axis=1) == d["compR1"]).all()
    save(melt(d, [f"Screen{i}" for i in range(1, 6)], covs), "petrova_2019_screening_beliefs", 1, 7, covs)
    t = melt(d, list(RAW), covs)
    raw = d.set_index("id")
    t["resp_raw"] = [raw.at[i, RAW[it]] for i, it in zip(t["id"], t["item"])]
    save(t, "petrova_2019_numeracy", 0, 1, covs, extra=("resp_raw",))
    save(melt(d, ["cancerstat1", "cancerstat2", "cancerstat3"] + [f"comp{i}.1" for i in range(1, 7)], covs),
         "petrova_2019_screening_statistics", 0, 1, covs)
    save(melt(d, ["sci1", "sci2", "sci3"], covs), "petrova_2019_science_literacy", 0, 1, covs)


if __name__ == "__main__":
    main()
