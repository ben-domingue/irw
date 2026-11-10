#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/wybf5zgdmj
# DOI: 10.17632/wybf5zgdmj (Mendeley Data, published 2026-07-30)
#   Fazi M. "Early maladaptive schemas and misophonia: incremental contributions beyond
#   personality traits and general psychopathology" [dataset].
# License: CC BY 4.0 (Mendeley Data record)
# Data: Dataset.xlsx, sheet Foglio1: 144 Italian adults (72 with misophonia, 72 matched
#   controls -- matches the record), collected online; anonymized participant code P001...
#
# Tables (items keep the source column names):
#   fazi_2026_dmss    Duke Misophonia Questionnaire symptom scale: dmss_affect1-8,
#                     dmss_physio1-5, dmss_cog1-10, 0-4
#   fazi_2026_dmq_imp DMQ impairment items dmq_imp1-12, 0-4
#   fazi_2026_pid5bf  Personality Inventory for DSM-5 Brief Form, PID-1..PID-25, 0-3
#   fazi_2026_ysqs3   Young Schema Questionnaire Short Form 3, YSQ-1..YSQ-90, 1-6
#   fazi_2026_bdi2    Beck Depression Inventory-II, BDI-1..BDI-21, 0-3
# Not shipped: the STAI-Y columns (8 state + 8 trait). Several carry an "(r)" suffix and the
#   deposit does not say whether those values were already reverse-scored; per the
#   pre-scored-reversals rule a table whose reversal state cannot be verified is dropped.
#   Also not shipped: all subscale/total columns.
# Covariates: cov_group (Misofonia/Controllo), cov_age, cov_sex, cov_gender_identity,
#   cov_education, cov_occupation (Italian labels as deposited). Sexual orientation, marital
#   status and the screening yes/no columns are not carried.
# Item text: not shipped -- the deposit has column codes only; instruments are published
#   elsewhere (Italian YSQ-S3, PID-5-BF, BDI-II are copyrighted).
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/wybf5zgdmj/files/"
       "8ab54c45-6e02-424d-854e-90968d1474fc/file_downloaded")


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Foglio1")
    assert len(d) == 144 and d["Codice"].is_unique
    assert d["Gruppo"].value_counts().to_dict() == {"Misofonia": 72, "Controllo": 72}
    d = d.rename(columns={"Codice": "id", "Gruppo": "cov_group", "Età": "cov_age",
                          "Sesso": "cov_sex", "Identità di genere:": "cov_gender_identity",
                          "Titolo di studio:": "cov_education",
                          "Occupazione attuale:": "cov_occupation"})
    covs = ["cov_group", "cov_age", "cov_sex", "cov_gender_identity", "cov_education",
            "cov_occupation"]
    scales = {
        "dmss": ([f"dmss_affect{i}" for i in range(1, 9)] + [f"dmss_physio{i}" for i in range(1, 6)]
                 + [f"dmss_cog{i}" for i in range(1, 11)], 0, 4),
        "dmq_imp": ([f"dmq_imp{i}" for i in range(1, 13)], 0, 4),
        "pid5bf": ([f"PID-{i}" for i in range(1, 26)], 0, 3),
        "ysqs3": ([f"YSQ-{i}" for i in range(1, 91)], 1, 6),
        "bdi2": ([f"BDI-{i}" for i in range(1, 22)], 0, 3),
    }
    for name, (cols, lo, hi) in scales.items():
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t.to_csv(OUT / f"fazi_2026_{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
