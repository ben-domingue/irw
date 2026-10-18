#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/PAQ3NG (Harvard Dataverse)
# Hollibaugh, G., Miles, M., & Hassell, H. (2024). Replication Data for: Seeking the Public Good: Public Service
#   Motivation and Political Ambition [Data set]. Harvard Dataverse.
# Data: PB-NationalSample.tab (Stata file as deposited, 1,815 rows x 42 columns; US national survey).
# Table: hollibaugh_2024_ambition_reasons  12 items, 1-3 (1 less likely to run, 2 neither/neutral, 3 more likely to run
#   for elected office; value labels in the Stata file). Six "what is appealing about running" items (Q34_7_1-6) and six
#   "why many people are not interested in running" items (Q34_8_1-5, 7), each rated for whether it makes the respondent
#   more or less likely to run. Respondents are kept if they answered at least one item (item cells with missing values
#   are dropped).
# Item names are the Qualtrics codes (lower-cased). The deposit's Stata do-file and R script label them (Q34_7_1 talking
#   about solutions, 7_2 meeting new people, 7_3 fundraising, 7_4 publicity, 7_5 persuading people, 7_6 the competition,
#   8_1 privacy, 8_2 making important decisions, 8_4 the schedule/travel, 8_5 difficulty on family and friends) but the
#   two files DISAGREE on Q34_8_3 and Q34_8_7 (do-file: 8_3 "the conflict", 8_7 "public scrutiny"; R script: 8_3
#   "scrutiny", 8_7 "conflict"), so codes are kept rather than guessing a label.
# Direction: every item shares one 3-point label set, and all 66 inter-item correlations are positive (0.02-0.63), so
#   nothing is flipped (labels and data agree). Block 8 items read as deterrents but are rated on the same
#   more/less-likely-to-run labels; they are kept as administered.
# Not shipped: PB-BureaucratSample.tab (PSM/personality composites and 4 ambition items only; derived), and
#   PB-LawStudentSample.tab (reasons_1-14 have no value labels and no codebook, and the R script names only 12 of the 14
#   columns; codes would be inferred; law students, so mixed adult/young adult sample).
# Covariate: cov_gender (1 male, 2 female). The age column is stored as text and is not used.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none (no names, locations or free text); id is the 1..N row index (the deposit has no respondent id).
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_K_2026-10-16"
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


ITEMS = ["Q34_7_1", "Q34_7_2", "Q34_7_3", "Q34_7_4", "Q34_7_5", "Q34_7_6",
         "Q34_8_1", "Q34_8_2", "Q34_8_3", "Q34_8_4", "Q34_8_5", "Q34_8_7"]


def main() -> None:
    import pyreadstat
    p = dv_fetch("10.7910/DVN/PAQ3NG", "PB-NationalSample.tab", RAW_ROOT / "paq3ng")
    d, meta = pyreadstat.read_dta(str(p))
    d = d.reset_index(drop=True)
    assert d.shape == (1815, 42)
    for c in ITEMS:
        assert meta.variable_value_labels[c] == {1: "Less likely to run", 2: "Neither/Neutral", 3: "More likely to run"}, c
        assert d[c].dropna().isin([1, 2, 3]).all(), c
    assert (d[ITEMS].corr().values[np.triu_indices(12, 1)] > 0).all()
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["gender"].where(d["gender"].isin([1, 2])).astype("Int64")
    t = d.melt(id_vars=["id", "cov_gender"], value_vars=ITEMS, var_name="item", value_name="resp")
    t = t[t["resp"].notna()].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=ITEMS, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str).str.lower()
    t = t[["id", "item", "resp", "cov_gender"]]
    emit({"hollibaugh_2024_ambition_reasons": (t, {c.lower(): {1, 2, 3} for c in ITEMS})})


if __name__ == "__main__":
    main()
