#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Questionnaire_data_on_Cultural_Heritage_Tourism_of_the_Gansu_Section_of_the_Silk_Road/30264874
# DOI: 10.6084/m9.figshare.30264874.v1 (data)
#   Su L (2025). Questionnaire data on Cultural Heritage Tourism of the Gansu Section of the Silk Road
#   [Data set]. figshare. Paper: Wu K, Su L, Zhang S, Yang S (2025). PLOS ONE,
#   10.1371/journal.pone.0335476 (its S1 Data, figshare 30544643, is the same file -- checked equal).
# License: CC BY 4.0 (figshare record)
# Data: S1 Data.xlsx, 381 tourists at Silk Road heritage sites in Gansu; 35 item columns (headers are
#   English renderings of the statements), 1-5, followed by the depositors' dimension means.
# Item codes: the headers are statements, not codes, so each item is coded by its dimension and its
#   position within it. The tie is checked, not assumed: for every dimension the row mean of its
#   columns equals the deposited dimension mean (COD, CRD, CCD, QV, EV, PV, NV, TS, TL) in all 381 rows.
# Tables:
#   su_2025_cultural_distortion_risk -- cod_1-4, crd_1-4, ccd_1-4 (the paper's three risk dimensions)
#   su_2025_perceived_value          -- qv_1-4, ev_1-4, pv_1-4, nv_1-4 (quality, emotional, price,
#                                       novelty value)
#   su_2025_tourist_satisfaction     -- ts_1-4
#   su_2025_tourist_loyalty          -- tl_1-3
# id: the deposit's Number. Not carried: Gender, age, education, income, occupation, prior Silk Road
#   visit (numeric codes with no key in the deposit); Total score and dimension means.
# Item text: not shipped -- the English headers are renderings of a Chinese questionnaire whose
#   administered wording is not deposited.
import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/58452787"
DIMS = [("COD", 4), ("CRD", 4), ("CCD", 4), ("QV", 4), ("EV", 4), ("PV", 4), ("NV", 4), ("TS", 4), ("TL", 3)]
TABLES = {"su_2025_cultural_distortion_risk": ["COD", "CRD", "CCD"],
          "su_2025_perceived_value": ["QV", "EV", "PV", "NV"],
          "su_2025_tourist_satisfaction": ["TS"], "su_2025_tourist_loyalty": ["TL"]}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 381 and d["Number"].is_unique
    raw = list(d.columns[2:37])
    assert raw[0].startswith("Address the challenge") and raw[-1].startswith("Share travel updates")
    rename, k = {}, 0
    for dim, n in DIMS:
        cols = raw[k:k + n]
        k += n
        assert np.allclose(d[cols].mean(axis=1), d[dim]), dim
        for i, c in enumerate(cols, 1):
            rename[c] = f"{dim.lower()}_{i}"
    d = d.rename(columns=rename)
    d["id"] = d["Number"]
    for name, dims in TABLES.items():
        items = [v for v in rename.values() if v.split("_")[0].upper() in dims]
        t = d[["id"] + items].melt(id_vars=["id"], var_name="item", value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin([1, 2, 3, 4, 5]).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"]].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
