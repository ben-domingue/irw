#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/EP6QLN
# DOI: 10.1016/j.trf.2022.10.025
#   Useche, S.A., Alonso, F., Boyko, A., ... Montoro, L. (2022). "Cross-culturally
#   approaching the cycling behaviour questionnaire (CBQ): Evidence from 19
#   countries", Transportation Research Part F 91, 386-400.
# Data: Harvard Dataverse 10.7910/DVN/EP6QLN (Sergio A. Useche, 2023): "Raw data
#       (CBQ-19).csv" (file 7557056; semicolon-delimited, decimal comma) -- 7001
#       urban cyclists from 19 countries x 55 columns. The deposit also holds
#       "Appendix I - Root_Questionnaire_CBQ.pdf" (7559246: every item stem, in
#       order, under its section header) and "Appendix II - Codebook (CBQ-19).pdf"
#       (7559247: country/region/gender codes and the 0-4 anchors).
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped (Appendix I questionnaire stems + Appendix II anchors, both in
#   the deposit). The CSV has no labels; item codes CBQ1-29 / RPRS1-12 are tied to
#   the questionnaire's bullet order. The deposit's own composite columns pin the
#   subscale boundaries: CBQ_Violations = mean(CBQ1-8) (F1, 8 bullets),
#   CBQ_Errors = mean(CBQ9-23) (F2, 15), CBQ_Positive_Behaviors = mean(CBQ24-29)
#   (F3, 6), RPRS_Rule_Knowledge = mean(RPRS1-5), RPRS_Risk_Perception =
#   mean(RPRS6-12) -- asserted below on every complete row.
#
# Tables:
#   useche_2022_cbq    CBQ1-29   0-4  0 = Never (at all) .. 4 = Very frequently
#                                     (F1 violations 1-8, F2 errors 9-23, F3
#                                     positive behaviours 24-29; not reversed)
#   useche_2022_rprs   RPRS1-12  0-4  0 = Strongly disagree .. 4 = Strongly agree
#                                     (rule knowledge 1-5, risk perception 6-12)
# Skipped: the five subscale means and three z-scores (composites).
# Covariates: country and region as the codebook's names, age, gender
#   (0 female / 1 male / 2 other, as labels), crash in past 5 years (0/1) and the
#   number of crashes. Blank (' ') cells are missing.
# No id column: id = row index + 1. 229 rows are exact duplicates of another row on
#   all 55 columns (189 groups, mostly adjacent pairs; the larger groups are
#   "ideal-answer" straight-liners). The authors analyse N = 7001 and nothing in
#   the deposit marks a row as a resubmission, so all rows are kept.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "useche_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/7557056?format=original"

CBQ = [f"CBQ{i}" for i in range(1, 30)]
RPRS = [f"RPRS{i}" for i in range(1, 13)]
TABLES = {"useche_2022_cbq": CBQ, "useche_2022_rprs": RPRS}
COMPOSITES = {
    "CBQ_Violations": CBQ[0:8], "CBQ_Errors": CBQ[8:23],
    "CBQ_Positive_Behaviors": CBQ[23:29],
    "RPRS_Rule_Knowledge": RPRS[0:5], "RPRS_Risk_Perception": RPRS[5:12],
}
ZSCORES = ["ZCBQ_Violations", "ZCBQ_Errors", "ZCBQ_Positive_Behaviors"]
COUNTRY = {1: "United Kingdom", 2: "Chile", 3: "Colombia", 4: "Mexico",
           5: "Dominican Republic", 6: "Spain", 7: "Finland", 8: "Russia",
           9: "Slovakia", 10: "Brazil", 11: "Belgium", 12: "Malaysia", 13: "China",
           14: "Denmark", 15: "Germany", 16: "Austria", 17: "Australia",
           18: "Poland", 19: "Cameroon"}
REGION = {1: "Europe", 2: "Latin America", 3: "Asia", 4: "Oceania", 5: "Africa"}
GENDER = {0: "female", 1: "male", 2: "other"}
COVS = ["cov_country", "cov_region", "cov_age", "cov_gender", "cov_crash_5yr",
        "cov_n_crashes_5yr"]


def fetch() -> Path:
    p = RAW_DIR / "raw_data_cbq19.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), sep=";", decimal=",", encoding="utf-8-sig",
                    na_values=[" "], keep_default_na=True)
    assert d.shape == (7001, 55), d.shape
    covsrc = ["Country_residence", "Region", "Age", "Gender", "Acc_DIC",
              "Incidents_as_cyclist"]
    expected = set(covsrc) | set(CBQ) | set(RPRS) | set(COMPOSITES) | set(ZSCORES)
    assert set(d.columns) == expected, set(d.columns) ^ expected
    # books: every column either shipped or skipped with a reason
    for c in list(COMPOSITES) + ZSCORES:
        print(f"  skip {c}: subscale composite")
    # composites confirm subscale boundaries (item order = questionnaire order)
    for comp, its in COMPOSITES.items():
        ok = d[its].notna().all(axis=1) & d[comp].notna()
        diff = (d.loc[ok, its].mean(axis=1) - d.loc[ok, comp]).abs().max()
        assert diff < 1e-6, (comp, diff)
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["cov_country"] = d["Country_residence"].map(COUNTRY)
    d["cov_region"] = d["Region"].map(REGION)
    d["cov_age"] = d["Age"].astype("Int64")
    d["cov_gender"] = d["Gender"].map(GENDER)
    d["cov_crash_5yr"] = d["Acc_DIC"].astype("Int64")
    d["cov_n_crashes_5yr"] = d["Incidents_as_cyclist"].astype("Int64")
    assert d["cov_country"].notna().all() and d["cov_region"].notna().all()
    assert d["cov_gender"].notna().all()
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + COVS, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].isin(range(5)).all(), name
        for it in its:  # every item uses the full 0-4 range
            assert set(t.loc[t["item"] == it, "resp"]) == set(range(5)), (name, it)
        t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(range(5)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
