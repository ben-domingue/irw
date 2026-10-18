#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/QGEBUB (Harvard Dataverse), Eugene-Springfield Community Sample (ESCS) dataset 18
# Goldberg, L. R. (2018). (18) Multidimensional Personality Questionnaire (MPQ). Eugene-Springfield Community Sample
#   [Data set]. Harvard Dataverse, V3 (the file MPQ_items_scales.tab was added in V3, 2026, replacing the earlier
#   separate item and scale files, which the depositor says did not reproduce each other).
# Data: MPQ_items_scales.tab, original format MPQ_items_scales.sav (733 ESCS adults x id, m1-m276, 15 derived scale columns).
# Table: goldberg_2018_mpq  276 two-option items (true/false or two phrases), in the order administered by the Oregon
#   Research Institute.
# Coding, from the deposit's "Scoring Procedures for the MPQ.PDF": option (a) is recorded as 1, option (b) as 2, and a
#   missing response as 1.5. 1.5 is a missing-data code, so those cells are dropped (374 of 203,308). resp keeps the
#   source codes 1/2 (a/b); it is not recoded to 0/1 because the (a)/(b) mapping to true/false is per item.
# Item names m1-m276 follow the scoring PDF's key (ORI administration order). Item text is not shipped (the MPQ is
#   a copyrighted instrument). SMISS, VRIN, TRIN, UV, WB, SP, AC, SC, SR, AG, AL, CO, HA, TR, AB are derived scale and
#   validity scores and are not shipped.
# Why it was not built before: data/goldberg_2018_escs.py excluded dataset 18 because it "ships no raw .tab at all". The
#   V3 file now has the item responses, so that reason no longer holds. (A 2026-10-05 lead row said "ESCS already built";
#   no MPQ table exists in the dictionary or data/.)
# Covariates: cov_sex, cov_age, cov_educ, cov_ethnic, cov_employ, cov_marital from the collection's demographics file
#   (DVN/VGMXJX), exactly as in data/goldberg_2018_neo_pir.py. id is the ESCS id, kept so the table joins the other ESCS tables.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. ESCS ids are study-assigned numbers; the demographics file carries no names or dates.
import os
import sys
import time
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_L_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}
COVS = {"SEX": "cov_sex", "AGE": "cov_age", "EDUC": "cov_educ", "ETHNIC": "cov_ethnic",
        "EMPLOY": "cov_employ", "MARITAL": "cov_marital"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset by its label or original name, in original format."""
    p = raw_dir / saveas
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if fname in (f["label"], f["dataFile"].get("originalFileName"))][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"}, headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert len(name) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and 8 <= t["item"].nunique() <= 700, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False, float_format="%.10g")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/QGEBUB", "MPQ_items_scales.sav", RAW_ROOT / "qgebub", "MPQ_items_scales.sav")
    d, _ = pyreadstat.read_sav(str(p))
    assert d.shape == (733, 292) and d["id"].is_unique
    items = [f"m{k}" for k in range(1, 277)]
    assert all(c in d.columns for c in items)
    # 1.5 is declared a user-missing value in the .sav, so pyreadstat reads it as NaN (the .tab conversion shows 1.5)
    assert d[items].stack().dropna().isin([1.0, 2.0]).all()
    n_missing = int(d[items].isna().sum().sum())
    assert n_missing == 374, n_missing
    dp = dv_fetch("10.7910/DVN/VGMXJX", "demographics-1.sav", RAW_ROOT / "vgmxjx", "demographics-1.sav")
    dem, _ = pyreadstat.read_sav(str(dp))
    dem.columns = [c.upper() for c in dem.columns]
    dem = dem.rename(columns={"ID": "id"})[["id"] + [c for c in COVS if c in dem]].rename(columns=COVS)
    d = d.merge(dem, on="id", how="left")
    assert len(d) == 733
    covs = [c for c in COVS.values() if c in d.columns]
    print(f"demographics matched for {int(d[covs[0]].notna().sum())} of {len(d)} respondents")
    d["id"] = d["id"].astype(int)
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t = t[t["resp"].notna()].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=items, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"goldberg_2018_mpq": (t[["id", "item", "resp"] + covs], {c: {1, 2} for c in items})})


if __name__ == "__main__":
    main()
