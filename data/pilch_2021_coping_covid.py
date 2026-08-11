#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258606
# DOI: 10.1371/journal.pone.0258606
# "The predictors of adaptive and maladaptive coping behavior during the
# COVID-19 pandemic: The Protection Motivation Theory and the Big Five
# personality traits" (Pilch, 2021), N=397 Polish general-population adults.
#
# SI file used: S1 Database (SAV), https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0258606.s002&type=supplementary
# License: CC BY 4.0 (confirmed on article page).
#
# Four instruments in one file -> four output tables:
#   - Coping Behavior Scale (CBS): BEH1-10 (adaptive/preventive) + Avoidance1-3
#     + Wishful1-3 (maladaptive), all on a 1-7 scale ("1=definitely not" .. "7=definitely yes")
#   - Protection Motivation Questionnaire (PMQ): Vulnerab1-2, Severity1-2,
#     Selfeffic1-2, Responseeffic1-2, Costs1-2 (10 items, 1-7 scale)
#   - Fear of COVID-19 Scale (FCV-19S): Fear1-7 (5-point scale, 1=strongly
#     disagree .. 5=strongly agree); has some missingness (pairwise deletion
#     used per the paper -> genuine NaNs, dropped, not imputed)
#   - IPIP-BFM-20 personality: IPIP1-20 (5-point scale)

import os
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "id=10.1371/journal.pone.0258606.s002&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Edu": "cov_education",
    "Empl": "cov_employment",
    "Marital": "cov_marital",
    "Risk1": "cov_risk_group",
    "Risk2": "cov_risk_contact",
}

SCALES = {
    "pilch_2021_coping_behavior": [
        "BEH1", "BEH2", "BEH3", "BEH4", "BEH5", "BEH6", "BEH7", "BEH8", "BEH9", "BEH10",
        "Avoidance1", "Avoidance2", "Avoidance3", "Wishful1", "Wishful2", "Wishful3",
    ],
    "pilch_2021_protection_motivation": [
        "Vulnerab1", "Vulnerab2", "Severity1", "Severity2",
        "Selfeffic1", "Selfeffic2", "Responseeffic1", "Responseeffic2",
        "Costs1", "Costs2",
    ],
    "pilch_2021_fear_covid19": [f"Fear{i}" for i in range(1, 8)],
    "pilch_2021_personality_ipip20": [f"IPIP{i}" for i in range(1, 21)],
}


def load_raw() -> pd.DataFrame:
    import requests
    import io
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = load_raw()

    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
