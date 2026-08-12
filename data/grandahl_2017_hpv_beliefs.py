#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0187193
# DOI: 10.1371/journal.pone.0187193

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0187193.s003"

ITEM_COLS = [
    "Q23a_Sideeffects", "Q23b_Protec_condyloma", "Q23c_Protect_Cxca",
    "Q23d_Difficult_appointment", "Q23e_Fear_of_needles", "Q23f_Serious_disease",
    "Q23g_Risk_wom_HPV", "Q23h_Risk_men_HPV", "Q23i_Cxca_lifethreatening",
    "Q23j_HPV_spread_sex", "Q23k_Always_aware_HPV", "Q23l_Other_cancer",
    "Q23m_Will_vaccinate", "Q23n_New_partner_condom", "Q23o_Attend_screening",
]

RESP_MAP = {
    "Totally disagree": 1,
    "Partly disagree": 2,
    "Neither agree or disagree": 3,
    "Partly agree": 4,
    "Totally agree": 5,
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/grandahl_2017.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df = pd.read_spss(tmp)

    df["id"] = df["Test1"]
    df["cov_group"] = df["Group"].astype(str)
    df["cov_sex"] = df["Q2_Sex"].astype(str)

    keep = ["id", "cov_group", "cov_sex"] + ITEM_COLS
    df = df[keep].copy()

    for c in ITEM_COLS:
        df[c] = df[c].astype(str).map(RESP_MAP)

    long = df.melt(id_vars=["id", "cov_group", "cov_sex"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "cov_group", "cov_sex"]
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "grandahl_2017_hpv_beliefs.csv")
    long.to_csv(out_path, index=False)
    print(f"grandahl_2017_hpv_beliefs: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
