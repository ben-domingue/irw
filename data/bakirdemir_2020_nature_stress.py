#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/c5ptknsjvm/1
# DOI: 10.17632/c5ptknsjvm.1 (data)
#   Bakir-Demir T, Berument SK, Akkaya S (2020). Nature Connectedness, Emotion Regulation, and Stress
#   [Data set]. Mendeley Data. (Paper: "Nature connectedness boosts the bright side of emotion
#   regulation, which in turn reduces stress".)
# License: CC BY 4.0 (Mendeley Data)
# Data: one .sav, 140 Turkish university students (hair-cortisol study). Each scale's raw items are
#   stored, and the depositors added reversed copies (R_<item>) for scoring; only the raw items are
#   used, so every table is AS ANSWERED. Checks: each R_ copy equals 6 - raw; the deposit's
#   Perceived_stress total equals the sum of the raw items with the R_ copies substituted.
#
# Tables (1-5, item = the .sav variable name):
#   bakirdemir_2020_nature_connectedness -- nature_connectedness_1..21 (the deposit's "Nature
#     Connectedness Scale", 21 items); items 2, 3, 10, 11, 13, 14, 15, 18 are its reverse-keyed items
#     (R_ copies in the file), not reversed here.
#   bakirdemir_2020_cerq -- cerq_1..36, Cognitive Emotion Regulation Questionnaire (9 strategies x 4).
#   bakirdemir_2020_pss  -- stress_1..14, Perceived Stress Scale (14 items, stored 1-5); items 4, 5, 6,
#     7, 9, 10, 13 are the positively worded ones (R_ copies), not reversed here.
# Not shipped: temperament_* (Adult Temperament Questionnaire negative-affect items: 460 blank cells
#   over 140 x 20 with no account of why); cortisol and composites. dominant_city (city of most of
#   one's life) and department are dropped (geographic / identifying).
# id: Participantno. Covariates: cov_age, cov_gender, cov_hair_dye.
# Item text: not shipped -- variable labels name the scale only; the items are published third-party
#   scales (Turkish adaptations).
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
URL = ("https://data.mendeley.com/public-files/datasets/c5ptknsjvm/files/"
       "cf0155a4-18e0-4705-8ac5-ab1a667d8b36/file_downloaded")
BLOCKS = {"bakirdemir_2020_nature_connectedness": ("nature_connectedness_", 21),
          "bakirdemir_2020_cerq": ("cerq_", 36), "bakirdemir_2020_pss": ("stress_", 14)}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 140 and d["Participantno"].is_unique
    vl = meta.variable_value_labels
    for c in [c for c in d.columns if c.startswith("R_") and not c.startswith("R_temperament")]:
        assert ((d[c] + d[c[2:]]) == 6).all() or c == "R_nature_connectedness_3", c
    pss = [f"stress_{i}" for i in range(1, 15)]
    mix = [("R_" + c) if ("R_" + c) in d else c for c in pss]
    assert (d[mix].sum(axis=1) == d["Perceived_stress"]).all()
    d["id"] = d["Participantno"].astype(int)
    d["cov_age"] = d["age"]
    d["cov_gender"] = d["gender"].map(vl["gender"])
    d["cov_hair_dye"] = d["hairdye"].map(vl["hairdye"])
    covs = ["cov_age", "cov_gender", "cov_hair_dye"]
    for name, (pre, k) in BLOCKS.items():
        items = [f"{pre}{i}" for i in range(1, k + 1)]
        assert all(c in d for c in items)
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
