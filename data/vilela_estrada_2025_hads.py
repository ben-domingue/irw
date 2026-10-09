#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Psychometric_properties_of_Spanish_Version_of_Hospital_Anxiety_and_Depression_Scale_in_cancer_patients/13626773
# DOI: 10.3389/fpsyg.2024.1497946
#   Vilela-Estrada, A. L., Villarreal-Zegarra, D., Copez-Lonzoy, A., et al. (2025).
#   Psychometric properties of the Spanish version of the hospital anxiety and
#   depression scale in cancer patients. Frontiers in Psychology, 15:1497946.
# Data: figshare 10.6084/m9.figshare.13626773.v2 (Villarreal-Zegarra, David; 2024).
#       Database.csv (file 51295196) -- 467 adults with cancer treated at a public
#       specialised cancer institute in Peru x 24 columns: five demographics, BAI and BDI
#       totals, HADS1-HADS14, and the HADS anxiety / depression / total scores.
#       Cancer_HADS_v1_2020_05_17.html (file 51295208) is the authors' R analysis report.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Plain CSV with positional headers (HADS1-HADS14) and no labels
#   at either level. The HADS is a `block` row in itemtext/instrument_rights_register.csv
#   (GL Assessment), so the wording would not ship in any case.
#
# Table:
#   vilela_estrada_2025_hads   HADS1-HADS14, 0-3 as scored (higher = more symptom);
#                              anxiety (odd) and depression (even) items in one table, as
#                              the paper analyses the instrument's factor structure.
# Skipped: BAITOTAL, BECKTOTAL (only totals deposited), HADA/HADD/HADSTOTAL (checked to equal
#   the odd-item, even-item and all-item sums, then dropped; one row's HADSTOTAL
#   repeats its HADA, a totalling slip -- its items agree with HADA and HADD).
# Covariates (Spanish labels as stored): cov_age (EDAD), cov_sex (SEXO), cov_marital
#   (ESTADOCIVIL), cov_education (GRADODEINSTRUCCION), cov_employment
#   (SITUACIONLABORALACTUAL).
# id: row index (the file has no identifier).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "f13626773"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/51295196"
NAME = "vilela_estrada_2025_hads"
ITEMS = [f"HADS{i}" for i in range(1, 15)]
COVS = {"EDAD": "cov_age", "SEXO": "cov_sex", "ESTADOCIVIL": "cov_marital",
        "GRADODEINSTRUCCIÓN": "cov_education", "SITUACIÓNLABORALACTUAL": "cov_employment"}
SKIP = {"BAITOTAL": "BAI total only", "BECKTOTAL": "BDI total only",
        "HADA": "HADS anxiety sum", "HADD": "HADS depression sum", "HADSTOTAL": "HADS total"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (467, 24)
    accounted = set(ITEMS) | set(COVS) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert (d[ITEMS[0::2]].sum(axis=1) == d["HADA"]).all()
    assert (d[ITEMS[1::2]].sum(axis=1) == d["HADD"]).all()
    bad = d[ITEMS].sum(axis=1) != d["HADSTOTAL"]
    assert bad.sum() == 1   # one row's HADSTOTAL repeats its HADA (2) instead of HADA+HADD (7)
    assert (d.loc[bad, "HADSTOTAL"] == d.loc[bad, "HADA"]).all()
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(0, 4)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(ITEMS) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and len(t) == int(d[ITEMS].notna().sum().sum())
    pv = {i: set(range(0, 4)) for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
