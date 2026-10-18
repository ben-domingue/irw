#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/G2UUFV (Harvard Dataverse)
# DOI: 10.7910/DVN/G2UUFV (dataset, 2025; Ksiazkiewicz, Aleksander; University of Illinois Urbana-Champaign),
#   "Replication Data for: Development and psychometric evaluation of a new genomic security and privacy
#   questionnaire in two national samples of United States residents".
# Data: df2023.csv (1,808 rows, one per respondent of the second national survey). GSPQ_1..GSPQ_73 are the
#   questionnaire items, 1-5 Likert, ~0.7% blank (dropped). Item wording is not in the deposit (only two .Rmd files).
# Table: ksiazkiewicz_2025_gspq  73 items, 1-5.
# Not shipped: the 2022 sample (df2022.csv / df22.csv): its items are bare Qualtrics ids (Q36..Q54, Q76..) and the
#   deposit does not document any mapping onto GSPQ_n, so no position-based cross-sample mapping is made.
#   df22.csv / df23.csv are the same respondents plus derived scales (risk, trust, ...), also not shipped.
#   Other 2023 Q-columns (policy items, exposure, willingness) and derived indices are not shipped.
# Reversal check: correlations are mixed in sign (27-33 negative pairs for the most affected items) because GSPQ
#   spans several subscales (utility / inaccuracy / privacy) with opposite keying; there is no codebook saying which
#   items, so none is flipped (datastandard: direction may vary across items); raw codes are shipped.
# Covariates: cov_age (years; the 1 value < 18 and the values > 100 are data-entry errors in an adult panel and are
#   set missing), cov_gender (man / woman / nonbinary from the deposit's indicator columns), cov_education (1-6) and
#   cov_income (1-12), codes as deposited.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. The deposit's "Unnamed: 0" is a row index; id is the 1..N row index of the source file.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_I_2026-10-16"
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


ITEMS = [f"GSPQ_{i}" for i in range(1, 74)]


def main() -> None:
    p = dv_fetch("10.7910/DVN/G2UUFV", "df2023.csv", RAW_ROOT / "g2uufv")
    d = pd.read_csv(p)
    assert d.shape[0] == 1808
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["age"].where(d["age"].between(18, 100)).astype("Int64")
    g = pd.Series(pd.NA, index=d.index, dtype="object")
    for col in ("man", "woman", "nonbinary"):
        g[d[col] == 1] = col
    d["cov_gender"] = g
    d["cov_education"] = d["edu"].astype("Int64")
    d["cov_income"] = d["income"].astype("Int64")
    covs = ["cov_age", "cov_gender", "cov_education", "cov_income"]
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    assert (t["resp"] % 1 == 0).all() and t["resp"].between(1, 5).all()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"].str.lower(), categories=[c.lower() for c in ITEMS], ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp"] + covs]
    emit({"ksiazkiewicz_2025_gspq": (t, {c.lower(): {1, 2, 3, 4, 5} for c in ITEMS})})


if __name__ == "__main__":
    main()
