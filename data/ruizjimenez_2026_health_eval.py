#!/usr/bin/env python3
# Source: https://zenodo.org/records/23880944
# DOI: 10.5281/zenodo.23880944 (data; no paper yet)
#   Ruiz Jimenez AM, Ferri Fuentevilla E, Aquino Llinares N, Echavarren Fernandez JM (2026).
#   Encuesta FEDER UPO-1381076 (2020): Criterios de merecimiento en la asignacion de servicios
#   publicos: nacionalismo del bienestar. Zenodo.
# License: CC BY 4.0 (Zenodo record)
# Data: FEDER2020_encuesta_datos.sav (1,201 Spanish nationals aged 30-60 in Andalucia and
#   Cataluna, Netquest online panel, Jan-Feb 2023; quota sample). Codebook FEDER2020_codebook_EN.pdf
#   and FEDER2020_diccionario_variables.csv in the same deposit.
#
# Table: ruizjimenez_2026_health_eval -- P6, "how do you rate the following aspects of the
#   current public health system", 12 items P6N_1..P6N_12, 1 (muy negativamente) - 10 (muy
#   positivamente), asked of every respondent before the experimental video. No non-response
#   code occurs in P6 (all 1,201 x 12 cells are 1-10).
# Not shipped: P10-P12 are rankings (the value is the option placed in each position, README s.3),
#   P9 and the political items are single questions on different formats.
# id: ID_CASO, the deposit's own sequential id (platform ids and e-mail removed by the depositors).
# Covariates: cov_sex, cov_age, cov_region (Andalucia/Cataluna), cov_education (P17N, "No sabe"
#   -> NA), cov_card_version (COD_VERSION: the regional or national health-card video shown
#   AFTER P6, so it cannot affect these items; kept as a covariate, not as treat).
# Item text: shipped (SPSS variable labels = the P6 statements; value labels = the 1-10 anchors).
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/records/23880944/files/FEDER2020_encuesta_datos.sav?download=1"
ITEMS = [f"P6N_{i}" for i in range(1, 13)]


def main():
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 1201 and d["ID_CASO"].is_unique
    d["id"] = d["ID_CASO"].astype(int)
    d["cov_sex"] = d["SEXO"].map({1: "male", 2: "female"})
    d["cov_age"] = d["EDAD"].astype(int)
    d["cov_region"] = d["COD_CCAA"].map({1: "Andalucia", 9: "Cataluna"})
    d["cov_education"] = d["P17N"].map({1: "no formal schooling", 2: "primary", 3: "secondary", 4: "higher"})
    d["cov_card_version"] = d["COD_VERSION"].map({3: "regional", 4: "national", 5: "regional", 6: "national"})
    covs = ["cov_sex", "cov_age", "cov_region", "cov_education", "cov_card_version"]
    assert d[["cov_sex", "cov_region", "cov_card_version"]].notna().all().all()
    t = d[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 10).all() and not t.duplicated(["id", "item"]).any()
    assert len(t) == 1201 * 12
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "ruizjimenez_2026_health_eval.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
