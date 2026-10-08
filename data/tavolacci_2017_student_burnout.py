#!/usr/bin/env python3
# Source: https://zenodo.org/records/1015002
# DOI: 10.5281/zenodo.1015002 (dataset; the deposit cites no paper)
#   Tavolacci, Marie Pierre (2017). "Database Burnout Rouen and Paris Nanterre
#   (France) n=1134" [data set], Zenodo.
# Data: "Database Burn out Rouen Paris.xlsx", sheet "N=1134": 1133 university
#       students (Rouen and Paris Nanterre) x 74 columns (59 used, 15 empty). The
#       second sheet "Desc_HID" is an unlabelled numeric scratch table (row index,
#       a decreasing series, 0/1) and is not documentation. No codebook.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: xlsx headers only (no variable or value
#   labels, no codebook); headers are positional ("AUDIT1", "Malasch3", "Cohen7").
#   The instruments are the published AUDIT, SCOFF, MBI emotional-exhaustion
#   subscale and PSS-10 (French versions); MBI and PSS are blocked in the itemtext
#   rights register.
#
# Tables (instrument identified from the column prefix, item count and range):
#   tavolacci_2017_audit    AUDIT1-10   0-4  Alcohol Use Disorders Identification Test
#   tavolacci_2017_scoff    SCOFF1-5    0/1  SCOFF eating-disorder screen (0 no, 1 yes)
#   tavolacci_2017_mbi_ee   Malasch1-9  0-6  Maslach Burnout Inventory, emotional
#                                            exhaustion (9 items, 0-6 frequency)
#   tavolacci_2017_pss10    Cohen1-10   0-4  Cohen Perceived Stress Scale (10 items)
#   Item codes are the deposit's headers (the SCOFF headers carry a "0:no 1:yes"
#   suffix, stripped to SCOFF1..SCOFF5).
# Dropped cells (data-entry errors / missing codes): text codes ("MANQ", "manquant",
#   "DM"), fractional values (AUDIT2 "2.5" and "1,5", AUDIT3 2.5, Malasch1 "3,5"),
#   values outside the instrument's range (Malasch1 11, Malasch6 30, SCOFF1 3, and
#   PSS values 5 and 6 -- 13 cells over 6 items against ~1100 per item). AUDIT2-10
#   are blank for ~225 students (skip pattern after AUDIT1); blank = not asked.
#   AUDIT4 and AUDIT5 are observed as {0,1,2,4} (no 3); shipped as recorded.
# Skipped: totals and classifications (Total AUDIT, AUDIT, Total SCOFF, SCOFF, Total
#   Malasch, MALASH EPUISEMENT, Total COHEN), "Financial difficulties Y/N" (a
#   recode of the 0-5 rating), "Estimation level" (undocumented), 15 empty columns.
# Covariates: as recorded. cov_gender is the deposit's 0/1 with no codebook.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "tavolacci_2017"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/1015002/files/"
       "Database%20Burn%20out%20Rouen%20Paris.xlsx/content")

SCOFF_SRC = ["SCOFF10:no 1:yes", "SCOFF20:no 1:yes", "SCOFF3 0:no 1:yes",
             "SCOFF4 0:no 1:yes", "SCOFF5 0:no 1:yes"]
TABLES = {
    "tavolacci_2017_audit": ({f"AUDIT{i}": f"AUDIT{i}" for i in range(1, 11)}, range(0, 5)),
    "tavolacci_2017_scoff": ({s: f"SCOFF{i}" for i, s in enumerate(SCOFF_SRC, 1)}, range(0, 2)),
    "tavolacci_2017_mbi_ee": ({f"Malasch{i}": f"Malasch{i}" for i in range(1, 10)}, range(0, 7)),
    "tavolacci_2017_pss10": ({f"Cohen{i}": f"Cohen{i}" for i in range(1, 11)}, range(0, 5)),
}
COVS = {"City": "cov_city", "Age": "cov_age", "Gender ": "cov_gender",
        "Marital status": "cov_marital_status", "Curriculum": "cov_curriculum",
        "Years": "cov_study_years", "Job": "cov_job", "Grant holder": "cov_grant_holder",
        "Accomodation": "cov_accommodation",
        "Financial difficulties 0 to 5": "cov_financial_difficulties",
        "Smoking": "cov_smoking",
        " Cannabis experimentaiton 0:no 1:yes": "cov_cannabis_ever",
        "Cannabis12 month 0:no 1:yes": "cov_cannabis_12m",
        "Cannabis user 0:no 1:yes": "cov_cannabis_user",
        "BINGE DRINKING": "cov_binge_drinking", "Sport": "cov_sport"}
SKIP = {"Total AUDIT": "total", "AUDIT": "classification of the total",
        "Total SCOFF": "total", "SCOFF": "classification of the total",
        "Total Malasch": "total", "MALASH EPUISEMENT": "classification of the total",
        "Total COHEN": "total",
        "Financial difficulties Y/N": "recode of the 0-5 rating",
        "Estimation level": "undocumented"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="N=1134")
    assert d.shape == (1133, 74), d.shape
    empty = [c for c in d.columns if d[c].isna().all()]
    assert len(empty) == 15
    used = set(COVS) | set(SKIP) | set(empty) | {c for m, _ in TABLES.values() for c in m}
    assert used == set(d.columns), set(d.columns) ^ used
    for c, why in SKIP.items():
        print(f"  skip {c!r}: {why}")
    print(f"  skip {len(empty)} empty columns")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d["cov_study_years"] = d["cov_study_years"].astype(str).str.strip().replace("nan", pd.NA)
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cmap, rng) in TABLES.items():
        sub = d[["id"] + covs + list(cmap)].rename(columns=cmap)
        its = list(cmap.values())
        t = sub.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="raw")
        t = t[t["raw"].notna()]
        t["resp"] = pd.to_numeric(t["raw"], errors="coerce")  # text codes -> NaN
        bad = t["resp"].isna() | (t["resp"] % 1 != 0) | ~t["resp"].isin(list(rng))
        for (it, v), n in t[bad].groupby(["item", "raw"]).size().items():
            print(f"    {name}: drop {it}={v!r} x{n}")
        t = t[~bad].copy()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
