#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_of_Assessing_the_Role_of_Robotic_Process_Automation_in_Building_Resilience_in_Supply_Chains_and_Sustainable_Growth/34691808
# DOI: 10.6084/m9.figshare.34691808.v1 (data; no paper DOI on the record)
#   Saputra N (2026). Dataset of Assessing the Role of Robotic Process
#   Automation in Building Resilience in Supply Chains and Sustainable Growth.
#   figshare.
# Data: "Dataset RPA LB_145_RPA_SCR_SGR.csv" (semicolon-separated; 146
#   employees x 28 columns), purposive/snowball survey across industries.
# License: CC BY 4.0 (figshare record).
# Codebook: none (headers are item codes; no anchors in the deposit).
#
# Counts: 146 rows = the description's "146 respondents".
# Tables (codes as deposited; observed 1-5):
#   saputra_2026_rpa                 RPA01-RPA08  robotic process automation
#   saputra_2026_supply_chain_resilience  SCR01-SCR04
#   saputra_2026_sustainable_growth  SGR01-SGR08
# id = row index. Covariate: age. Birth year duplicates age; gender, industry,
#   coverage, company size, position and tenure are unlabelled codes, so not
#   carried.
# Item text: not shipped -- none in the deposit.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70303314"
SPEC = {
    "saputra_2026_rpa": ("RPA", 8),
    "saputra_2026_supply_chain_resilience": ("SCR", 4),
    "saputra_2026_sustainable_growth": ("SGR", 8),
}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), sep=";")
    assert d.shape == (146, 28), d.shape
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={"Age": "cov_age"})
    covs = ["cov_age"]
    allowed = set(range(1, 6))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pre, n) in SPEC.items():
        cols = [f"{pre}{i:02d}" for i in range(1, n + 1)]
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
