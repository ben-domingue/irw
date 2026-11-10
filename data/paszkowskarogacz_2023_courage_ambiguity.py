#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/gbh5mt36hk
# DOI: 10.17632/gbh5mt36hk (Mendeley Data, v1, 2023-12-12)
#   Paszkowska-Rogacz A. "Courage versus Tolerance of Ambiguity among Young Adults Making
#   Career Decisions. The Moderating Effect of Life Orientation."
# License: CC BY 4.0 (Mendeley Data record)
# Data: "Paszkowska-Rogacz_Courage versus Tolerance of Ambiguity .sav" (229 Polish young
#   adults aged 19-26, 145 women / 84 men -- matches the record's abstract), plus "The
#   key.docx" (item -> subscale key) and "Tools description.docx" (codebook).
#
# Tables (items keep the SPSS variable names; English stems are in the variable labels):
#   paszkowskarogacz_2023_cdat  Career Decision Ambiguity Tolerance Scale-R (Xu & Tracey),
#                               Polish pilot version, 20 items CDAT1..CDAT20, 1-7.
#                               Subscales per the key: preference 1-5, tolerance 6-10,
#                               confidence 11-15, aversion 16-20 (aversion items raw).
#   paszkowskarogacz_2023_cmr   Courage Measure - Revised, 6 items CM_R1..CM_R6, 1-7.
#   paszkowskarogacz_2023_spq   KPS-S2 Social Participation Questionnaire (life orientation),
#                               20 items SPQ_1..SPQ_20, 1-5; moratory items 2,4,7,8,13,14,15,
#                               16,18,19, transitive items the rest (per the key).
# Not shipped: subscale/total score columns; Q1/Q2 (employment yes/no) and Holland type are
#   carried as covariates.
# id: row index (no id column). Covariates: cov_gender (woman/man), cov_age, cov_domicile,
#   cov_holland_type, cov_employed (Q1), cov_worked_before (Q2) -- value labels applied.
# Item text: not shipped -- SPSS variable labels carry English stems for all 46 items;
#   cheap later, needs register rows for CDAT/CM-R/KPS-S2.
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/gbh5mt36hk/files/"
       "f1362f05-cda3-4521-ab9e-fe1bc36adb00/file_downloaded")


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 229
    vl = meta.variable_value_labels
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].map(vl["Gender"])
    d["cov_age"] = d["Age"]
    d["cov_domicile"] = d["Domicile"].map(vl["Domicile"])
    d["cov_holland_type"] = d["Holland"].map(vl["Holland"])
    d["cov_employed"] = d["Q1"].map(vl["Q1"])
    d["cov_worked_before"] = d["Q2"].map(vl["Q2"])
    covs = ["cov_gender", "cov_age", "cov_domicile", "cov_holland_type", "cov_employed",
            "cov_worked_before"]
    assert (d["cov_gender"].value_counts().to_dict() == {"woman": 145, "man": 84})
    scales = {"cdat": ([f"CDAT{i}" for i in range(1, 21)], 7),
              "cmr": ([f"CM_R{i}" for i in range(1, 7)], 7),
              "spq": ([f"SPQ_{i}" for i in range(1, 21)], 5)}
    for name, (cols, top) in scales.items():
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(1, top).all()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t.to_csv(OUT / f"paszkowskarogacz_2023_{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
