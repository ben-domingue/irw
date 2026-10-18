#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SQJFVA (Harvard Dataverse)
# DOI: 10.7910/DVN/SQJFVA (dataset, 2023; Pakpour, Amir; Qazvin University of Medical Sciences),
#   "health literacy and mental health". Iranian adults in six cities of Qazvin and Alborz provinces (Persian).
# Data: HL SH data.tab (9,775 rows x 66 columns, one row per respondent) and CODEBOOK.docx (item wording and
#   value labels). Blank cells are missing and are dropped.
# Tables (one instrument each):
#   pakpour_2023_helia            33 items, 1-5 never .. always: Health Literacy Instrument for Adults (HELIA):
#                                 Re1-4 reading, Atl1-6 access, Und1-7 understanding, App1-4 appraisal,
#                                 DM1-12 decision making / behavioural intention.
#   pakpour_2023_ehealth_literacy  8 items, 1-5 strongly disagree .. strongly agree: eHEALS (EHL1-EHL8);
#                                 the deposit's eHEALS total equals the item sum on every complete row.
# Not shipped: D1-D7 (short WEMWBS, 7 items, below the 8-item floor), SHI1/SHI2/SH3 (sleep hygiene, 3 items),
#   and the derived columns Re, AC, Un, Ap, DE, WEMWBS, TOTALHL, SHB, eHEALS (subscale/total scores).
# Reversal check: every pairwise inter-item correlation in both blocks is positive (min r = 0.27 HELIA, 0.55
#   eHEALS) and the codebook gives one value label set per block, so no item is flipped; raw codes are shipped.
# Covariates (codebook coding kept as numeric codes): cov_age (years), cov_gender (0 female, 1 male),
#   cov_education (1 primary .. 4 university), cov_residence (1 city, 2 rural), cov_marital (1 single,
#   2 married, 3 divorced), cov_city (1 Qazvin, 2 Buein Zahra, 3 Avaj, 4 Takestan, 5 Abyek, 6 Alborz).
# The multi_scale warning on HELIA is expected: the Re/Atl/Und/App/DM prefixes are the five subscales of one
#   instrument (codebook: TOTALHL = Health Literacy Instrument for Adults), kept as one table.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. No identifier column in the deposit; id is the 1..N row index of the source file.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_G_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (ingested tab)."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["dataFile"]["filename"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", headers=UA, timeout=600)
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


COVS = {"age": "cov_age", "gender": "cov_gender", "education": "cov_education",
        "accomodation": "cov_residence", "marital": "cov_marital", "city": "cov_city"}
HELIA = ([f"Re{i}" for i in range(1, 5)] + [f"Atl{i}" for i in range(1, 7)] + [f"Und{i}" for i in range(1, 8)]
         + [f"App{i}" for i in range(1, 5)] + [f"DM{i}" for i in range(1, 13)])
EHEALS = [f"EHL{i}" for i in range(1, 9)]


def long_table(d: pd.DataFrame, items: list) -> pd.DataFrame:
    t = d.melt(id_vars=["id"] + list(COVS.values()), value_vars=items, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    assert (t["resp"] % 1 == 0).all() and t["resp"].between(1, 5).all(), sorted(t["resp"].unique())
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"].str.lower(), categories=[c.lower() for c in items], ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    for c in COVS.values():
        assert (t[c].dropna() % 1 == 0).all(), c
        t[c] = t[c].astype("Int64")
    return t[["id", "item", "resp"] + list(COVS.values())]


def main() -> None:
    p = dv_fetch("10.7910/DVN/SQJFVA", "HL SH data.tab", RAW_ROOT / "sqjfva")
    d = pd.read_csv(p, sep="\t")
    assert d.shape == (9775, 66)
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns=COVS)
    assert d["cov_age"].dropna().min() >= 18
    assert set(d["cov_gender"].dropna()) <= {0, 1}
    tables = {
        "pakpour_2023_helia": (long_table(d, HELIA), {c.lower(): {1, 2, 3, 4, 5} for c in HELIA}),
        "pakpour_2023_ehealth_literacy": (long_table(d, EHEALS), {c.lower(): {1, 2, 3, 4, 5} for c in EHEALS}),
    }
    emit(tables)


if __name__ == "__main__":
    main()
