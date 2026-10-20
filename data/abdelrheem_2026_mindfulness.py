#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IVKVFT
# DOI: 10.7910/DVN/IVKVFT
#   Mohamed Abdelrheem, Tarik N. (2026). "Mindfulness: Enhancing emotional
#   creativity and academic achievement in college students". Harvard
#   Dataverse, V1 (released 2026-10-16). The companion paper was under review
#   at Cogent Education when the data were deposited.
# Data: "PURE_Data _EC&Mindfulness_Final Final" (format=original -> SPSS .sav),
#       640 college students x 85 columns: EC1-EC30 (Emotional Creativity
#       Inventory, 1-5), M1-M39 (Five Facet Mindfulness Questionnaire, 1-5),
#       GPA/Sex/Major columns and eight subscale/total aggregate columns.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .sav carries NO variable labels for any item
#   column (checked: column_labels is None for every EC*/M* column; the only
#   label in the file is on `Sex`, "1= female; 0= male") and there is no
#   codebook file in the deposit. The wording would have to come from the
#   published ECI (Averill 1999) and FFMQ (Baer et al. 2006) instruments,
#   which is a rights question, not a cheap extraction.
#
# Two tables, one per instrument:
#   abdelrheem_2026_eci    EC1-EC30, 1-5
#   abdelrheem_2026_ffmq   M1-M39,   1-5
# NOT shipped (aggregates, printed by the script): EC_Preparedness,
#   EC_Novelty, EC_Effectivness, EC (= the exact sum of EC1-EC30, verified),
#   M_Observing, M_Descripition, M_ActionAware, M_NonJudgmental,
#   M_Non_reactivity, Mindfulness. These are subscale/total composites, not
#   per-item responses.
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR", REPO_ROOT / "automated_finding" / "irw_output"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://dataverse.harvard.edu/api/access/datafile/10273924"
            "?format=original")

COVS = {"GPA": "cov_gpa", "Sex": "cov_sex", "Major": "cov_major",
        "Major_Class": "cov_major_class", "Major_Group": "cov_major_group"}
AGGREGATES = ["EC_Preparedness", "EC_Novelty", "EC_Effectivness", "EC",
              "M_Observing", "M_Descripition", "M_ActionAware",
              "M_NonJudgmental", "M_Non_reactivity", "Mindfulness"]
SCALES = {"abdelrheem_2026_eci": [f"EC{i}" for i in range(1, 31)],
          "abdelrheem_2026_ffmq": [f"M{i}" for i in range(1, 40)]}


def main() -> None:
    raw = Path(os.environ.get("IRW_RAW_DIR", "/tmp")) / "abdelrheem_2026.sav"
    if not raw.exists():
        r = requests.get(DATA_URL, headers=UA, timeout=300)
        r.raise_for_status()
        raw.write_bytes(r.content)
    d, _meta = pyreadstat.read_sav(raw, apply_value_formats=False)

    # Books balance: id + covariates + items + named aggregates == all columns.
    items = [c for s in SCALES.values() for c in s]
    accounted = {"NO"} | set(COVS) | set(items) | set(AGGREGATES)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c in AGGREGATES:
        print(f"  skipped {c}: subscale/total aggregate, not a response")

    assert d["NO"].nunique() == len(d)
    d = d.rename(columns={"NO": "id", **COVS})
    covs = sorted(COVS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert len(set(SCALES)) == len(SCALES)
    for name, cols in SCALES.items():
        assert len(name) <= 40, name
        t = d.melt(id_vars=["id"] + covs, value_vars=cols, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), "fractional resp -> imputation?"
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, 5).all(), sorted(t["resp"].unique())
        t["id"] = t["id"].astype(int)
        t = t[["id", "item", "resp"] + covs].reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
        checks = run_qc(t, permitted_values={i: [1, 2, 3, 4, 5] for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:180]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
