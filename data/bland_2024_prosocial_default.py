#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MHVAJZ
# DOI: 10.7910/DVN/MHVAJZ (dataset; the record cites no paper and none was found)
#   Bland, James (2024). "Replication Data for A Characteristic Adaptation of the
#   Prosocial Default: Unpacking the Role of Causality Orientations and Moral
#   Foundations in Public Service Motivation". Harvard Dataverse, V1.
# Data: "GCO_MFT_PSM.csv" (file 10162134, format=original; the .tab conversion is
#       GCO_MFT_PSM.tab) -- 544 respondents (public and nonprofit employees) x 110
#       columns: ID, 22 MFT items, 51 GCOS responses (17 vignettes x 3 orientations),
#       16 PSM items, Qualtrics leftovers and demographics. Record description:
#       "survey data general causality orientation, moral foundations (short version),
#       and public service motivation". No codebook, questionnaire or paper deposited.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain CSV, so there are no variable labels and no value
#   labels at either level; headers are positional codes (MFT1, GC3_A, APS2). The
#   wording is the published instruments': MFQ-20 (Graham et al. 2011,
#   moralfoundations.org), the 17-vignette GCOS (Deci & Ryan 1985; the CSDT library,
#   which is a `block` row in itemtext/instrument_rights_register.csv), and the 16-item
#   international PSM scale (Kim et al. 2013).
#
# Tables:
#   bland_2024_mfq20            MFT1-22 minus MFT6, MFT17; 1-6 as stored (the MFQ's
#                               0-5 relevance/agreement scales shifted up by one).
#                               MFT1-11 are the relevance part, MFT12-22 the judgments.
#   bland_2024_gcos_autonomy    GC1_A..GC17_A  1-7
#   bland_2024_gcos_control     GC1_C..GC17_C  1-7
#   bland_2024_gcos_impersonal  GC1_I..GC17_I  1-7  (GCOS scores each orientation as its
#                               own subscale; the three responses to one vignette are
#                               split across the three tables)
#   bland_2024_psm              APS1-4 (attraction to public service), CPV1-4
#                               (commitment to public values), COM1-4 (compassion),
#                               SS1-4 (self-sacrifice); 1-7 (Kim et al. 2013 dimensions).
#                               One table: the four are dimensions of one PSM construct,
#                               so the run_qc multi_scale warning on the prefixes is
#                               expected and accepted.
# Skipped: MFT6 and MFT17, the MFQ-20's two catch items ("good at math", "better to do
#   good than to do bad"). Their positions are the MFQ-20's, and their responses have the
#   catch-item profile (MFT6 mean 2.38, the lowest of 22; MFT17 mean 5.39 with 361 of 544
#   at the top, the highest). Q26 (constant 1: consent). Q21_10 (an unlabelled checkbox
#   between COM1 and COM2: ' ' or '1', 49 ticks; meaning unknown). Q30-Q36 (raw
#   demographic codes without labels: Q30, Q31, Q35 and Q34 are the sources of Sex,
#   Race_Binary, Ed_Ascending and the job-level dummies, checked by crosstab; Q32, Q33,
#   Q36 are undocumented). The seven role/sector dummies are folded into two covariates.
# Covariates (all as the deposit codes them; labels undocumented unless stated):
#   cov_sex (0/1), cov_race_binary (0/1), cov_job_type (1-3), cov_education
#   (Ed_Ascending, 1-5 ascending), cov_job_level (frontline / middle / upper, from the
#   Frontlines/Middle/Upper dummies, exactly one set per row), cov_sector (federal /
#   state / local / nonprofit, likewise). One respondent left every demographic blank.
# id = the deposit's ID (unique, 1-544).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "bland_2024"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/10162134?format=original"

MFQ_CATCH = ["MFT6", "MFT17"]
MFQ = [f"MFT{i}" for i in range(1, 23) if f"MFT{i}" not in MFQ_CATCH]
GCOS = {o: [f"GC{v}_{o}" for v in range(1, 18)] for o in "ACI"}
PSM = [f"{p}{i}" for p in ("APS", "CPV", "COM", "SS") for i in range(1, 5)]
TABLES = {"bland_2024_mfq20": (MFQ, range(1, 7)),
          "bland_2024_gcos_autonomy": (GCOS["A"], range(1, 8)),
          "bland_2024_gcos_control": (GCOS["C"], range(1, 8)),
          "bland_2024_gcos_impersonal": (GCOS["I"], range(1, 8)),
          "bland_2024_psm": (PSM, range(1, 8))}
COVS = {"Sex": "cov_sex", "Race_Binary": "cov_race_binary", "Job_Type": "cov_job_type",
        "Ed_Ascending": "cov_education"}
LEVEL = {"Frontlines": "frontline", "Middle": "middle", "Upper": "upper"}
SECTOR = {"Federal": "federal", "State": "state", "Local": "local", "Nonprofit": "nonprofit"}
SKIP = {"Q26": "constant 1 (consent)",
        "Q21_10": "unlabelled checkbox, meaning unknown",
        **{f"Q{i}": "raw demographic code, no labels" for i in range(30, 37)},
        "MFT6": "MFQ-20 catch item", "MFT17": "MFQ-20 catch item"}


def fetch() -> Path:
    p = RAW_DIR / "GCO_MFT_PSM.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def collapse(d: pd.DataFrame, dummies: dict) -> pd.Series:
    x = d[list(dummies)].apply(pd.to_numeric, errors="coerce")
    blank = x.isna().all(axis=1)
    assert ((x.sum(axis=1) == 1) | blank).all()
    return x.fillna(0).idxmax(axis=1).map(dummies).where(~blank)


def main() -> None:
    d = pd.read_csv(fetch(), encoding="utf-8-sig", na_values=[" "]).copy()
    assert d.shape == (544, 110) and d["ID"].is_unique, d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    accounted = {"ID"} | set(items) | set(COVS) | set(LEVEL) | set(SECTOR) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    # catch items: lowest and highest mean of the 22 MFT columns
    mft = d[[f"MFT{i}" for i in range(1, 23)]].mean()
    assert mft.idxmin() == "MFT6" and mft.idxmax() == "MFT17"
    d = d.assign(cov_job_level=collapse(d, LEVEL), cov_sector=collapse(d, SECTOR))
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values()) + ["cov_job_level", "cov_sector"]
    for c in COVS.values():
        d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        checks = run_qc(t)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload")
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
