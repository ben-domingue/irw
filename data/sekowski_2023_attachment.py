#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/S5MIUH (Harvard Dataverse)
# Sekowski, M. Attachment disorganization, anxiety and avoidance [Data set]. Harvard Dataverse, released 2023-10-13.
#   Data for Sekowski, M., & Gambin, M. (2023). Attachment disorganization, anxiety and avoidance: Factor structure and
#   latent profiles of the three dimensions of attachment and their associations with hypomentalization, depressive
#   symptoms and suicidality (deposit's own citation; no DOI or journal given, so 2023 is the cited year, not verified
#   against the journal). Polish adults (Maria Grzegorzewska University online sample; age 18-90).
# Data: The_Maria_Grzegorzewska_University_attachment_dimesions_and_profiles_database.sav (498 rows, 61 columns,
#   SPSS, fetched in original format). No codebook or value labels on the item columns.
# Tables (all one sample, N = 498 before cell cleaning; separate files per instrument):
#   ECR (16 items, ECR_01..16) is NOT shipped: the instrument rights register has a 'block' verdict on the ECR family
#   (irw#1955, permission-required clause).
#   sekowski_2023_rfq8    8 items RFQ_01..RFQ_08, 1-7, hypomentalizing, stored RAW (corpus convention for the RFQ-8, see
#                         itemtext/instrument_rights_register.csv). Item 7 is the reverse-keyed item: the deposit's own
#                         scoring uses RFQ_07r (8 - RFQ_07) and RFQ_hypomentalizing_mean equals the mean of items 1-6, 8
#                         and RFQ_07r (asserted), so higher = more hypomentalizing after reversing item 7 only.
#   sekowski_2023_phq9    9 items PHQ_01..PHQ_09, 0-3 (PHQ9_sum equals the item sum, asserted, range 0-27).
#                         Two respondents are dropped from this table only: one has the impossible value 4 on items 1-6
#                         (a single respondent, not a scale feature) and one has 0.5 on item 5.
#   sekowski_2023_ada     9 items ADA_01..ADA_09, 1-7, disorganized attachment (ADA_disorganized_mean equals the item
#                         mean, asserted). Direction: the deposit names the mean ADA_disorganized_mean, higher = more
#                         disorganized; no reversal is applied by the deposit.
# Not shipped: ECR (see above), SBQ (4 items on different response ranges, below the 8-item floor), the *_mean/_sum columns and
#   Latent_profiles_attachment (derived), Personal_status / Place_of_residence / Professional_situation.
# Cleaning: isolated off-grid cells (ADA_01 = 6.5; ECR_11 = 2.5 in the unshipped ECR block) are dropped as data-entry errors; one cov_education of 2.3
#   is set missing.
# id: the deposit's own sequential ID column (1..498), a study-assigned row number.
# Covariates: cov_age (18-90, adults only), cov_gender (0 = female, 1 = male, from the deposit's value labels),
#   cov_education (1 Elementary, 2 Basic vocational, 3 Secondary, 4 Bachelor's, 5 Graduate, from value labels).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none (age, gender, education only).
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_S_2026-10-17"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


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


def build(d: pd.DataFrame, src: list, names: list, valid: set) -> tuple:
    """Long table; cells outside `valid` (off-grid or out of range) are dropped, respondents with none left vanish."""
    covs = ["cov_age", "cov_gender", "cov_education"]
    sub = d[["id"] + covs].copy()
    sub[names] = d[src].values
    t = sub.melt(id_vars=["id"] + covs, value_vars=names, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    bad = ~t["resp"].isin(valid)
    print(f"    dropped {int(bad.sum())} off-grid cell(s) among {names[0].split('_')[0]} items")
    t = t[~bad].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    for c in covs:
        t[c] = t[c].astype("Int64")
    return t[["id", "item", "resp"] + covs], {n: valid for n in names}


def main() -> None:
    fn = "The_Maria_Grzegorzewska_University_attachment_dimesions_and_profiles_database.tab"
    p = dv_fetch("10.7910/DVN/S5MIUH", fn, RAW_ROOT / "s5miuh", "attachment.sav")
    d, _ = pyreadstat.read_sav(str(p), apply_value_formats=False)
    assert d.shape == (498, 61), d.shape
    assert d["ID"].is_unique and d["Age_in_years"].min() >= 18
    d = d.rename(columns={"ID": "id", "Age_in_years": "cov_age", "Gender": "cov_gender", "Education_level": "cov_education"})
    d["id"] = d["id"].astype(int)
    assert set(d["cov_gender"].dropna()) <= {0.0, 1.0}
    d.loc[~d["cov_education"].isin([1, 2, 3, 4, 5]), "cov_education"] = np.nan  # one off-grid value (2.3)

    def mean_matches(cols, target, rev=()):
        x = d[cols].copy()
        for c in rev:
            x[c] = 8 - x[c]
        ok = x.apply(lambda s: s == s.round()).all(axis=1)  # skip the rows with off-grid cells
        return np.allclose(x[ok].mean(axis=1), d.loc[ok, target])

    ecr = [f"ECR_{i:02d}" for i in range(1, 17)]
    assert mean_matches(ecr[:8], "Anx_ECR_SF_mean") and mean_matches(ecr[8:], "Avoid_ECR_SF_mean")
    rfq = [f"RFQ_{i:02d}" for i in range(1, 9)]
    assert (d["RFQ_07"] + d["RFQ_07r"] == 8).all()
    rfq_src = [c if c != "RFQ_07" else "RFQ_07r" for c in rfq]
    assert np.allclose(d[rfq_src].mean(axis=1), d["RFQ_hypomentalizing_mean"])
    phq = [f"PHQ_{i:02d}" for i in range(1, 10)]
    assert (d[phq].sum(axis=1) == d["PHQ9_sum"]).all()
    ada = [f"ADA_{i:02d}" for i in range(1, 10)]
    assert mean_matches(ada, "ADA_disorganized_mean")

    # drop, from the PHQ table only, respondents with any impossible PHQ cell (one respondent has 4 on items 1-6,
    # one has 0.5 on item 5); the other scales of those respondents are intact
    phq_ok = d[phq].isin([0, 1, 2, 3]).all(axis=1)
    print(f"    PHQ: dropping {int((~phq_ok).sum())} respondent(s) with impossible values")

    tabs = {}
    for name, src, items, valid, dd in [
        ("sekowski_2023_rfq8", rfq, [f"rfq_{i}" for i in range(1, 9)], set(range(1, 8)), d),
        ("sekowski_2023_phq9", phq, [f"phq9_{i}" for i in range(1, 10)], {0, 1, 2, 3}, d[phq_ok]),
        ("sekowski_2023_ada", ada, [f"ada_{i}" for i in range(1, 10)], set(range(1, 8)), d),
    ]:
        tabs[name] = build(dd, src, items, valid)
        t = tabs[name][0]
        wide = t.pivot(index="id", columns="item", values="resp")
        c = wide.corr().values
        print(f"    {name}: min inter-item r = {np.nanmin(c):.2f}")
    emit(tabs)


if __name__ == "__main__":
    main()
