#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283997
# DOI: 10.1371/journal.pone.0283997
#
# Jo, Baek (2023). Impacts of social isolation and risk perception on social
# networking intensity among university students during covid-19. PLOS ONE.
#
# S1 File (CSV) contains raw item-level responses (7-point Likert,
# 1=strongly disagree to 7=strongly agree, confirmed in S1 Appendix) to six
# instruments used in a COVID-19 social-networking survey of Korean and
# Vietnamese university students (N=345):
#   SNI1-3  Social Networking Intensity
#   SNO1-3  Subjective Norms
#   PBC1-3  Perceived Behavioral Control
#   ARP1-3  Affective Risk Perception
#   CRP3-4  Cognitive Risk Perception (source column numbering starts at 3;
#           kept as-is per original item labels)
#   CFS1,3,4 Cabin Fever Syndrome (source column numbering skips CFS2; kept
#           as-is per original item labels)
# Excluded: "Total" (constant=89 for every row, not a real response),
# "Software" / "Time" / "Natinality" metadata columns (kept relevant ones
# as covariates), "Gender(Male_1)" -> cov_gender.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SRC_URL = "https://doi.org/10.1371/journal.pone.0283997.s003"

SCALES = {
    "sni": ["SNI1", "SNI2", "SNI3"],
    "sno": ["SNO1", "SNO2", "SNO3"],
    "pbc": ["PBC1", "PBC2", "PBC3"],
    "arp": ["ARP1", "ARP2", "ARP3"],
    "crp": ["CRP3", "CRP4"],
    "cfs": ["CFS1", "CFS3", "CFS4"],
}

COV_MAP = {
    "Natinality": "cov_nationality",
    "Gender(Male_1)": "cov_gender_male",
    "Age": "cov_age",
}


def convert():
    import io
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), encoding="latin1")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"jo_2023_{name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
