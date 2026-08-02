#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264722
# DOI: 10.1371/journal.pone.0264722
# Pavic & Suljok (2022), "Vaccination conspiracy beliefs among social science
# & humanities and STEM educated people -- An analysis of the mediation
# paths", PLOS ONE. CC BY 4.0. N=577.
#   Vac_con1-7: Vaccination conspiracy beliefs scale (Shapiro et al.), 5-pt
#   Imm1-3:     Natural-immunity subscale of the VAX scale (Martin & Petrie)
#   HCS_trust1-8: Trust in Healthcare System scale (Shea et al., Croatian-
#                 adapted, 1 item dropped) -- raw items only, the "_rec"
#                 columns are reverse-coded duplicates of the same items
#   Lit1-15:    Science literacy scale (Oxford/Eurobarometer-derived), binary
#                correct/not-correct
# Subscale total columns (HCS_trust_total, Lit_total, Imm_total,
# Vac_con_total) are excluded as derived composites.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0264722.s001

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0264722.s001"

LIKERT5 = {
    "Completely disagree": 1, "Disagree": 2, "Neither disagree nor agree": 3,
    "Agree": 4, "Completely agree": 5,
}
CORRECT2 = {"Not correct or don't know": 0, "Correct": 1}

SCALES = {
    "pavic_2022_vaccine_conspiracy": ([f"Vac_con{i}" for i in range(1, 8)], LIKERT5),
    "pavic_2022_natural_immunity": ([f"Imm{i}" for i in range(1, 4)], LIKERT5),
    "pavic_2022_healthcare_trust": ([f"HCS_trust{i}" for i in range(1, 9)], LIKERT5),
    "pavic_2022_science_literacy": ([f"Lit{i}" for i in range(1, 16)], CORRECT2),
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", "Age": "cov_age", "Gender": "cov_gender"})


def convert():
    df = fetch()
    for out_name, (item_cols, mapping) in SCALES.items():
        long = df.melt(id_vars=["id", "cov_age", "cov_gender"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).map(mapping)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_age", "cov_gender"]]
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
