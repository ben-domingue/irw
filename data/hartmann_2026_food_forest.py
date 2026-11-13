#!/usr/bin/env python3
# Source: https://zenodo.org/records/22035305
# DOI: 10.5281/zenodo.22035305 (data)
#   Hartmann P (2026). Survey data on willingness to pay for food forest produce: monoculture health
#   risk, nature connectedness and need for uniqueness [Data set]. Zenodo. TRANSCLIMA project,
#   University of the Basque Country UPV/EHU.
# License: CC BY 4.0 (Zenodo)
# Data: "26 food forest acceptance.sav", 845 US consumers (Census-region quota), anonymised by the
#   depositor. Every item carries its full stem as the SPSS variable label ("<section prompt>: <stem>")
#   and value labels for the two anchors (2-4 labelled by number).
#
# Tables, 1-5 as stored, item = the .sav variable name:
#   hartmann_2026_food_forest_wtp               -- WillingnessToPay1-4 (disagree..agree)
#   hartmann_2026_monoculture_health_risk       -- MonocultureHealthRisk1-6
#   hartmann_2026_climate_concern               -- ClimateConcern1-4 (not concerned/serious .. very)
#   hartmann_2026_nature_connectedness          -- NatureConnectedness1-6 (the NR-6 stems)
#   hartmann_2026_need_for_uniqueness           -- NeedForUniqueness1-8
#   No item runs against its scale's direction in the stems, nothing reversed.
# Not shipped: PriorAwareness (one item).
# id: row number (the file's ID is a 6-character random code). Covariates (value labels applied):
#   cov_gender, cov_age, cov_region (US Census region), cov_income, cov_education.
# Item text: not shipped in this batch -- full stems are the .sav variable labels (cheap); the NR-6
#   and the consumer need-for-uniqueness short form are third-party instruments with no rights-register
#   row, and the other three blocks' sources need identifying first.
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/22035305/files/26%20food%20forest%20acceptance.sav/content"
BLOCKS = {
    "hartmann_2026_food_forest_wtp": ("WillingnessToPay", 4),
    "hartmann_2026_monoculture_health_risk": ("MonocultureHealthRisk", 6),
    "hartmann_2026_climate_concern": ("ClimateConcern", 4),
    "hartmann_2026_nature_connectedness": ("NatureConnectedness", 6),
    "hartmann_2026_need_for_uniqueness": ("NeedForUniqueness", 8),
}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 845 and d["ID"].is_unique
    vl = meta.variable_value_labels
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].map(vl["Gender"])
    d["cov_age"] = d["Age"]
    d["cov_region"] = d["Region"].map(vl["Region"])
    d["cov_income"] = d["Income"].map(vl["Income"])
    d["cov_education"] = d["Education"].map(vl["Education"])
    covs = ["cov_gender", "cov_age", "cov_region", "cov_income", "cov_education"]
    used = {"ID", "Gender", "Age", "Region", "Income", "Education", "PriorAwareness"}
    for name, (pre, k) in BLOCKS.items():
        items = [f"{pre}{i}" for i in range(1, k + 1)]
        used |= set(items)
        for c in items:
            assert sorted(vl[c]) == [1, 2, 3, 4, 5], c
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    left = [c for c in meta.column_names if c not in used]
    assert not left, left


if __name__ == "__main__":
    main()
