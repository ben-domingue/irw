#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_for_Technology_Readiness_and_Smart_Hotel_Technology_Usage_Intention_Parallel_Mediation_through_Attitude_and_Personal_Cognition/34704774
# DOI: 10.6084/m9.figshare.34704774.v1 (data; no paper DOI on the record)
#   Pimchangthong D (2026). Dataset for Technology Readiness and Smart Hotel
#   Technology Usage Intention: Parallel Mediation through Attitude and
#   Personal Cognition. figshare.
# Data: Survey-Sample-Data.sav (487 Chinese hotel customers with smart-hotel
#   experience x 50 columns; the record lists the file twice, same size).
# License: CC BY 4.0 (figshare record).
# Codebook: none; SPSS value labels (bilingual English/Chinese demographics;
#   items labelled 1-7) and the record's description.
#
# Counts: 487 rows = the description's "487 Chinese customers".
# Tables (1-7, codes as deposited; *mean columns and age dummies dropped):
#   pimchangthong_2026_tech_readiness     13 items: optimism OPT7-10,
#       innovativeness INN11-13, discomfort DIS14-16, insecurity INS17-19
#   pimchangthong_2026_attitude           ATT20-23
#   pimchangthong_2026_subjective_norms   SN24-27
#   pimchangthong_2026_perceived_control  PBC28-30
#   pimchangthong_2026_usage_intention    UI31-34
# id = the file's index column (unique, 3-557). Stayed (all "yes") and
#   totalseconds (completion time) dropped.
# Covariates: gender, age band, education, position, income (value-labelled).
# Item text: not shipped -- none in the deposit.

import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70360050"
SPEC = {
    "pimchangthong_2026_tech_readiness":
        ["OPT7", "OPT8", "OPT9", "OPT10", "INN11", "INN12", "INN13", "DIS14",
         "DIS15", "DIS16", "INS17", "INS18", "INS19"],
    "pimchangthong_2026_attitude": ["ATT20", "ATT21", "ATT22", "ATT23"],
    "pimchangthong_2026_subjective_norms": ["SN24", "SN25", "SN26", "SN27"],
    "pimchangthong_2026_perceived_control": ["PBC28", "PBC29", "PBC30"],
    "pimchangthong_2026_usage_intention": ["UI31", "UI32", "UI33", "UI34"],
}
COVS = {"Gen": "cov_gender", "Age": "cov_age_band", "Edu": "cov_education",
        "Position": "cov_position", "Income": "cov_income"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    assert d.shape == (487, 50), d.shape
    assert d["index"].is_unique and (d["Stayed"] == 1).all()
    d = d.rename(columns={"index": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    allowed = set(range(1, 8))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, cols in SPEC.items():
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
