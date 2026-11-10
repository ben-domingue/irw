#!/usr/bin/env python3
# Source: https://zenodo.org/records/23790531
# DOI: 10.5281/zenodo.23790531
#   Vera Mendoza EM (2026). Base de datos del Burnout y rasgos de personalidad como
#   predictores de ideacion suicida [dataset]. Zenodo.
# License: CC BY 4.0 (Zenodo record)
# Data: "Analisis de datos.sav" (110 Peruvian health-sciences undergraduates; the .xlsx in
#   the record is the same data with a two-row header). SPSS variable labels carry the
#   Spanish stems, value labels the options.
#
# Tables (item = <table suffix>_nn from the SPSS name Items_0k_nn, e.g. Items_02_07 ->
#   mbiss_07; the block number k fixes the scale, nn the item):
#   veramendoza_2026_bfi15p  Big Five Inventory-15P (Peruvian BFI short form), 15 items
#                            Items_01_01..15, 1-5 (muy en desacuerdo .. muy de acuerdo)
#   veramendoza_2026_mbiss   Maslach Burnout Inventory-Student Survey as administered, 14
#                            items Items_02_01..14 (exhaustion 1-5, cynicism 6-9, academic
#                            efficacy 10-14), 1-5 (nunca .. siempre)
#   veramendoza_2026_pansi   Positive and Negative Suicide Ideation Inventory, 14 items
#                            Items_03_01..14 (negative ideation 1-8, positive/protective
#                            9-14), 0-4 (nunca .. siempre); raw, not reversed
# Not shipped: dimension scores, Dim_*/CALIF_* categories, Escala_Maslach_total.
# id: row index. Covariates: cov_age, cov_sex, cov_program (carrera), cov_semester
#   (value labels applied).
# Item text: not shipped -- Spanish stems in the SPSS variable labels; cheap later, needs
#   register rows for BFI-15P/MBI-SS/PANSI (MBI is proprietary).
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/23790531/files/Analisis%20de%20datos.sav/content"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 110
    vl = meta.variable_value_labels
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Edad"]
    d["cov_sex"] = d["Sexo"].map(vl["Sexo"])
    d["cov_program"] = d["Carrera"].map(vl["Carrera"])
    d["cov_semester"] = d["Semestre"].map(vl["Semestre"])
    covs = ["cov_age", "cov_sex", "cov_program", "cov_semester"]
    scales = {"bfi15p": ("Items_01_", 15, 1, 5), "mbiss": ("Items_02_", 14, 1, 5),
              "pansi": ("Items_03_", 14, 0, 4)}
    for name, (p, n, lo, hi) in scales.items():
        cols = sorted(c for c in d.columns if c.startswith(p))
        assert len(cols) == n, (name, len(cols))
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t["item"] = name + "_" + t["item"].str[len(p):]   # Items_02_07 -> mbiss_07
        assert t["resp"].between(lo, hi).all()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t.to_csv(OUT / f"veramendoza_2026_{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
