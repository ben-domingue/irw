#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/8DEYWD (Harvard Dataverse)
# DOI: 10.7910/DVN/8DEYWD (dataset, 2021; Austin, Erica), "Data supporting COVID-19 disinformation and political
#   engagement among communities of color: The role of media literacy" (HKS Misinformation Review, 2021).
# Data: WSU Murrow Center COVID-19 Survey Excerpt ... .tab (SPSS file as deposited, 1,264 adult respondents, Washington
#   State and US samples, 75 columns).
# Table: austin_2021_media_literacy  11 items, 1-5 (strongly disagree .. strongly agree; value labels in the SPSS file):
#   MLSN* (6 items, news source media literacy: who/how the news was created) and MLCN* (5 items, news content media
#   literacy). Item names kept. 95 missing cells dropped.
# Not shipped: the 7 MISPER* misinformation-belief items and the 7 SCIL* science true/false items (7 items each, below
#   the 8-item floor; the scored SCIKNOW* columns are derived), RiskJustice/RiskEcon (2 items), the deposit's index
#   columns (MLSNews, MLCNews, Totscilit, Disperceptions, derived), weights, dates and open-end text.
# Reversal check: all 11 items are positively worded; every pairwise correlation is positive (lowest r = 0.44).
#   Nothing flipped.
# Covariates: cov_gender (GenderBinary, 1 male 2 female), cov_age_group (AgeGrp, 1 = 18-29 .. 7 = 80+), cov_wa_us
#   (WAorUS, 0 = Washington State sample, 1 = US sample), cov_polor (1 very liberal .. 5 very conservative),
#   cov_completion_time_s (whole-survey duration, seconds).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none shipped. The deposit's ID is a platform respondent number; id is the 1..N row index instead.
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_J_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
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
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")



ITEMS = ["MLSNHow", "MLSNWho", "MLSNWhtThnk", "MLSNGoal", "MLSNCompare", "MLSNClear", "MLCNCompare", "MLCNMore",
         "MLCNTwice", "MLCNAccurate", "MLCNUp2Date"]


def main() -> None:
    import pyreadstat
    fn = "WSU Murrow Center COVID-19 Survey Excerpt for Harvard Misinformation Review Repository.tab"
    p = dv_fetch("10.7910/DVN/8DEYWD", fn, RAW_ROOT / "8deywd")
    d, _ = pyreadstat.read_sav(str(p))
    d = d.reset_index(drop=True)
    assert d.shape == (1264, 75)
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["GenderBinary"]
    d["cov_age_group"] = d["AgeGrp"]
    d["cov_wa_us"] = d["WAorUS"]
    d["cov_polor"] = d["PolOr"]
    d["cov_completion_time_s"] = d["Duration__in_seconds_"]
    covs = ["cov_gender", "cov_age_group", "cov_wa_us", "cov_polor", "cov_completion_time_s"]
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    assert (t["resp"] % 1 == 0).all() and t["resp"].between(1, 5).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=ITEMS, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    for c in covs[:4]:
        t[c] = t[c].astype("Int64")
    t = t[["id", "item", "resp"] + covs]
    emit({"austin_2021_media_literacy": (t, {c: set(range(1, 6)) for c in ITEMS})})


if __name__ == "__main__":
    main()
