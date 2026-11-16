#!/usr/bin/env python3
# Source: https://zenodo.org/records/4655400
# DOI: 10.5281/zenodo.4655400 (data); documented by 10.5281/zenodo.4288282
#   Kuhlmann J, Raje F, Richard I, Ohlenforst B (2021). Evaluations of previous interventions in
#   improving quality of life (ANIMA project, ST3.1.2). Zenodo.
# License: CC BY 4.0 (Zenodo record)
# Data: "Schiphol Airport_dataset.xlsx" (1,212 residents aged 18+ around Schiphol Airport,
#   survey Nov 2018 - Oct 2019, ~14% response). Questionnaire and column map in the deposit's
#   "ANIMA_ST312_Schiphol Airport_survey.pdf" (Table 1). The deposit's Heathrow and Marseille
#   files are interview/focus-group notes, not response data.
#
# Tables (one per question block, each a different response format):
#   kuhlmann_2021_schiphol_noise_annoyance -- Q5, ISO/TS 15666 noise annoyance at home over the
#     past 12 months, 0 (not at all) - 10 (extremely), 7 sources V5_01..V5_07 in the questionnaire
#     order: road traffic, neighbours, trains, air traffic, companies/industry,
#     construction/demolition, loitering youth.
#   kuhlmann_2021_schiphol_sleep_disturbance -- Q6, same 0-10 scale and the same 7 sources,
#     noise interfering with sleep, V6_01..V6_07.
#   kuhlmann_2021_schiphol_worries -- Q14, 9 topics V14_01..V14_09 (security, climate change, CO2
#     emissions, fine dust, air pollution, noise disturbance, busy feeder roads, parking, public
#     transport connections). The file holds the Dutch labels; recoded per the deposit's own
#     description "1 = a lot of worries to 3 = no worries": Veel zorgen 1, Enige zorgen 2,
#     Geen zorgen 3.
# No cell of V5/V6/V14 is blank. Q1 and Q7-Q13 are single questions on separate formats; not shipped.
# id: row index (the file has no id column).
# Covariates: cov_sex (P9), cov_age (P2; 6 blank), cov_tenure (P1, owner/renter), cov_noise_zone
#   (Gebied: the study's 3 aircraft-noise strata -- inner area, outer area, outside contour), and
#   cov_month (Maand, survey month). The Percentage_* columns are area-level aggregates and weeg9
#   a survey weight; neither is a person-level response. Not shipped.
# Item text: not shipped -- the stems and the source/topic lists are in the deposit PDF, in an
#   English rendering of the Dutch questionnaire; the codes are tied to them only by list order.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails


OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/records/4655400/files/Schiphol%20Airport_dataset.xlsx?download=1"
WORRY = {"Veel zorgen": 1, "Enige zorgen": 2, "Geen zorgen": 3}
ZONE = {"Binnengebied": "inner area", "Buitengebied": "outer area", "Buiten contour": "outside contour"}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 1212
    d["id"] = range(1, len(d) + 1)
    d["cov_sex"] = d["P9"].map({"Vrouw": "female", "Man": "male"})
    d["cov_age"] = d["P2"]
    d["cov_tenure"] = d["P1"].map({"Koopwoning": "owner", "Huurwoning": "renter"})
    d["cov_noise_zone"] = d["Gebied"].map(ZONE)
    d["cov_month"] = d["Maand"]
    assert d[["cov_sex", "cov_noise_zone"]].notna().all().all()
    covs = ["cov_sex", "cov_age", "cov_tenure", "cov_noise_zone", "cov_month"]
    w = [f"V14_0{i}" for i in range(1, 10)]
    for c in w:
        assert d[c].isin(WORRY).all(), c
        d[c] = d[c].map(WORRY)
    blocks = {
        "kuhlmann_2021_schiphol_noise_annoyance": ([f"V5_0{i}" for i in range(1, 8)], 0, 10),
        "kuhlmann_2021_schiphol_sleep_disturbance": ([f"V6_0{i}" for i in range(1, 8)], 0, 10),
        "kuhlmann_2021_schiphol_worries": (w, 1, 3),
    }
    for name, (items, lo, hi) in blocks.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all() and len(t) == 1212 * len(items)
        assert not t.duplicated(["id", "item"]).any()
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        gate(t)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
