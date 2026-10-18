#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WITW8F (Harvard Dataverse)
# DOI: 10.7910/DVN/WITW8F (dataset, 2026; Chen, Juan), "Data for studying cognitive-utility and socio-affective
#   pathways to GenAI learning". Chinese-language survey of students on generative AI use for study.
# Data: data794.tab (SPSS file as deposited, 794 rows, 44 columns, no missing item cells).
# Table: chen_2026_genai_learning  39 items, 1-5 (very much disagree .. very much agree; value labels in the SPSS
#   file): TTF1-3, SI1-3, HM1-3, AN1-3, PE1-4, EE1-4, CA1-2, HA1-2, POE1-3, NE1-4, BI1-3, AUB1-2, GLP1-3. Column
#   names kept (the Chinese item wording sometimes numbers items 1,3,4 where the column says 1,2,3; names follow the
#   columns).
# Not shipped: totalvalue (a derived total that does not even equal the item sum), index (respondent number).
# Reversal check: NE1-4 (negative feelings) and HA1-2 (hindrance appraisal) are negatively worded and the data agree:
#   they correlate positively with each other (r 0.42-0.90) and ~0 or negative with the positive blocks (lowest r =
#   -0.19). Labels and data agree and direction varies across items, so nothing is flipped.
# Covariates: cov_gender (1 male, 2 female), cov_major (1 arts, 2 science), cov_completion_time_s (seconds).
# Sample: age and institution are neither recorded nor described; the question asks for "major type" (a university
#   major), so a student sample is assumed; Age Range is left blank in the tags.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. The deposit's index column is a respondent number; id is the 1..N row index instead.
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



ITEMS = ["TTF1", "TTF2", "TTF3", "SI1", "SI2", "SI3", "HM1", "HM2", "HM3", "AN1", "AN2", "AN3", "PE1", "PE2",
         "PE3", "PE4", "EE1", "EE2", "EE3", "EE4", "CA1", "CA2", "HA1", "HA2", "POE1", "POE2", "POE3", "NE1",
         "NE2", "NE3", "NE4", "BI1", "BI2", "BI3", "AUB1", "AUB2", "GLP1", "GLP2", "GLP3"]


def main() -> None:
    import pyreadstat
    p = dv_fetch("10.7910/DVN/WITW8F", "data794.tab", RAW_ROOT / "witw8f")
    d, _ = pyreadstat.read_sav(str(p))
    d = d.reset_index(drop=True)
    assert d.shape == (794, 44) and len(ITEMS) == 39
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["gender"].astype(int)
    d["cov_major"] = d["major"].astype(int)
    d["cov_completion_time_s"] = d["totalseconds"]
    covs = ["cov_gender", "cov_major", "cov_completion_time_s"]
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    assert t["resp"].notna().all() and (t["resp"] % 1 == 0).all() and t["resp"].between(1, 5).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=ITEMS, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp"] + covs]
    emit({"chen_2026_genai_learning": (t, {c: set(range(1, 6)) for c in ITEMS})})


if __name__ == "__main__":
    main()
