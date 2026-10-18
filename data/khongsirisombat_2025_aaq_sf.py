#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/YPYMQ5 (Harvard Dataverse)
# Khongsirisombat, N. (2025). Validation of the Thai Short Form of the Attitudes to Ageing Questionnaire [Data set].
#   Harvard Dataverse.
# Data: "DATA Thai AAQ-SF.tab", original format DATA Thai AAQ-SF.csv. 224 community-dwelling older Thai adults (age 60-96)
#   plus five legend rows under the data (value labels for the demographic columns), which are dropped.
# Table: khongsirisombat_2025_aaq_sf  12-item Thai AAQ-SF, Item1PG1-Item12PC4, 1-5. The item names carry the AAQ-SF
#   subscale (PG psychological growth, PL psychosocial loss, PC physical change), so the mapping is in the deposit.
# Scale: 1-5 is confirmed by the deposit's own ReversePL1-4 columns, which equal 6 - the four PL items (asserted).
# Direction: items are kept as administered. ReversePL1-4 are derived re-codings of the PL items and are not shipped.
#   PL items correlate negatively with the PG and PC items and positively with each other, as for a negatively worded
#   subscale, so nothing is flipped.
# Covariates: cov_sex (1 male, 2 female), cov_age (years), cov_marital_status (1 single, 2 married, 3 widowed,
#   4 divorced, 5 separated). Labels are from the legend rows. Not shipped: Age Group (derived from age), Currently living
#   (code 4 has 84 respondents but the legend defines only 1-3), Educational level (code 3 has 9 respondents but the
#   legend defines only 0-2).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. No identifier in the file; id is the row index.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_L_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (original format) and save it as `saveas`."""
    p = raw_dir / saveas
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False, float_format="%.10g")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/YPYMQ5", "DATA Thai AAQ-SF.tab", RAW_ROOT / "ypymq5", "thai.csv")
    d = pd.read_csv(p, encoding="utf-8-sig")
    d = d[pd.to_numeric(d["Age"], errors="coerce").notna()].reset_index(drop=True)  # drops the legend rows
    assert len(d) == 224
    items = [c for c in d.columns if c.startswith("Item")]
    assert len(items) == 12 and d[items].notna().all().all() and d[items].stack().isin([1, 2, 3, 4, 5]).all()
    for r, i in zip(["ReversePL1", "ReversePL2", "ReversePL3", "ReversePL4"],
                    ["Item3PL1", "Item5PL2", "Item7PL3", "Item10PL4"]):
        assert (6 - d[i] == d[r]).all(), r
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = pd.to_numeric(d["Sex"]).astype(int)
    d["cov_age"] = d["Age"].astype(int)
    d["cov_marital_status"] = pd.to_numeric(d["Marital status"]).astype(int)
    assert set(d["cov_sex"]) <= {1, 2} and set(d["cov_marital_status"]) <= {1, 2, 3, 4, 5}
    covs = ["cov_sex", "cov_age", "cov_marital_status"]
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=items, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"khongsirisombat_2025_aaq_sf": (t[["id", "item", "resp"] + covs], {c: {1, 2, 3, 4, 5} for c in items})})


if __name__ == "__main__":
    main()
