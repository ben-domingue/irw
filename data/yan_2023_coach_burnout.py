#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/DATA_coach_burnout_study/21195868
# DOI: 10.1177/17479541231181971
#   Yan, Jang, Kwon & Jin (2023). "An integrated perspective of the demand-control
#   and effort-reward imbalance models on burnout among sport coaches: The
#   moderating role of over-commitment and coaching efficacy", International
#   Journal of Sports Science & Coaching. (Paper paywalled; abstract read.)
# Data: figshare 10.6084/m9.figshare.21195868 (Dojin Jang, 2022), data.xlsx (file
#       37576135): 398 Chinese school sport coaches x 66 columns (ID, six coded
#       demographics, ERI1-10, OS1-4, OC1-6, CE1-24, CB1-15). N=398 matches the
#       paper's abstract. No codebook in the deposit.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Levels checked: xlsx, headers only (no variable or value
#   labels, no codebook); wording is in the instruments cited by the paywalled
#   paper.
#
# Tables (prefixes are the deposit's; constructs from the paper's abstract and the
# item counts/response ranges, which match the standard instruments):
#   yan_2023_eri                  ERI1-10  1-4  effort-reward imbalance, short form
#                                               (3 effort + 7 reward items, 4-point)
#   yan_2023_overcommitment       OC1-6    1-4  ERI over-commitment (6 items, 4-point)
#   yan_2023_job_stress           OS1-4    1-5  the paper's job-stress mediator; "OS" is
#                                               not expanded anywhere in the deposit
#   yan_2023_coaching_efficacy    CE1-24   1-5  coaching efficacy (24 items, as in the
#                                               original Coaching Efficacy Scale)
#   yan_2023_coach_burnout        CB1-15   1-5  burnout (15 items, ABQ structure)
# Covariates ship as the deposit's codes (no codebook): Sex, Age, SchoolGrade,
#   CoachLevel, "CoahinCreear" (coaching career), Income -- all 1-4 or 1-3 codes.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "jang_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/37576135"

TABLES = {
    "yan_2023_eri": ([f"ERI{i}" for i in range(1, 11)], range(1, 5)),
    "yan_2023_overcommitment": ([f"OC{i}" for i in range(1, 7)], range(1, 5)),
    "yan_2023_job_stress": ([f"OS{i}" for i in range(1, 5)], range(1, 6)),
    "yan_2023_coaching_efficacy": ([f"CE{i}" for i in range(1, 25)], range(1, 6)),
    "yan_2023_coach_burnout": ([f"CB{i}" for i in range(1, 16)], range(1, 6)),
}
COVS = {"Sex": "cov_sex", "Age": "cov_age_band", "SchoolGrade": "cov_school_level",
        "CoachLevel": "cov_coach_level", "CoahinCreear": "cov_coaching_career",
        "Income": "cov_income_band"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch())
    assert d.shape == (398, 66), d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    assert set(d.columns) == {"ID"} | set(items) | set(COVS), set(d.columns) ^ ({"ID"} | set(items) | set(COVS))
    assert d["ID"].is_unique
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        assert t["resp"].isin(list(rng)).all(), name
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
