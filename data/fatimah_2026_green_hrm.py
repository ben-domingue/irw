#!/usr/bin/env python3
# Source: https://zenodo.org/records/20763110
# DOI: 10.5281/zenodo.20763110 (dataset; the article is under review at F1000Research --
#   a peer-review report 10.5256/f1000research.204641.r519298 exists, no article DOI yet)
#   Fatimah, D., Ibrahim, M. H., Kumala Sari, F., Dwi Septianto, F., Abrorul Sofyan, A.,
#   Al Hanif, A., et al. (2026). Green Ability, Motivation, and Opportunity as Drivers of
#   Environmental Performance: The Roles of Green Workplace Behavior and Worker
#   Productivity [Data set]. Zenodo.
# Data: "Green Human Resources Management.xlsx" -- sheet Raw_Data: 304 employees of
#       Indonesian coffee shops x five background columns and 30 items GA1-EP5 (1-5);
#       sheet Questionnaire_Items: item code (GA-1 ..), the English item wording, and
#       "Likert 1-5" for every item.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. The Questionnaire_Items sheet gives English wording for all 30
#   items (no value labels; anchors not given beyond "Likert 1-5"), but the survey was run
#   with Indonesian coffee-shop staff and the deposit does not say which language was
#   administered, so whether this is the administered wording or a translation is unknown.
#   Recoverable from that sheet (GA-1 = column GA1, etc.) once the language is confirmed.
#
# Tables (1-5, one per construct named in the record and the item sheet):
#   fatimah_2026_green_ability       GA1-GA5
#   fatimah_2026_green_motivation    GM1-GM5
#   fatimah_2026_green_opportunity   GO1-GO5
#   fatimah_2026_green_workplace     GWP1-GWP5 (green workplace behaviour)
#   fatimah_2026_worker_productivity WB1-WB5
#   fatimah_2026_env_performance     EP1-EP5
# Covariates (text as stored): cov_gender, cov_education, cov_work_experience,
#   cov_employment_type, cov_income.
# id: row index (no identifier).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z20763110"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/20763110/files/"
       "Green%20Human%20Resources%20Management.xlsx/content")
P = "fatimah_2026_"
RANGE = range(1, 6)
TABLES = {"green_ability": "GA", "green_motivation": "GM", "green_opportunity": "GO",
          "green_workplace": "GWP", "worker_productivity": "WB", "env_performance": "EP"}
TABLES = {k: [f"{p}{i}" for i in range(1, 6)] for k, p in TABLES.items()}
COVS = {"Gender": "cov_gender", "Education": "cov_education",
        "Work Experience": "cov_work_experience", "Employment Type": "cov_employment_type",
        "Income": "cov_income"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    x = pd.ExcelFile(fetch())
    d = pd.read_excel(x, "Raw_Data")
    q = pd.read_excel(x, "Questionnaire_Items")
    items = [c for v in TABLES.values() for c in v]
    assert d.shape == (304, 35) and set(d.columns) == set(items) | set(COVS)
    assert sorted(q["Item"].str.replace("-", "")) == sorted(items)   # every item documented
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(RANGE).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(RANGE) for i in its}
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
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
