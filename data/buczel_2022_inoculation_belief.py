#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267463
# "Vaccination against misinformation: The inoculation technique reduces the
# continued influence effect"
# DOI: 10.1371/journal.pone.0267463
# S1 Data (raw data, xlsx):
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0267463.s001&type=supplementary
#
# Note: this file also contains 5 columns (Credible, Expert, Trustworthy,
# noRetr, noMisinf) that are counts of correct answers out of 5 open-ended
# inference questions per scenario (noMisinf even takes half-point values,
# e.g. 0.5, 1.5) -- these are aggregate/composite accuracy scores, not raw
# per-item responses, and are excluded per datastandard.md's
# "Subscale aggregate columns" / composite-exclusion rule.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW_URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0267463.s001&type=supplementary"

BELIEF_ITEMS = [
    "credible_misinf_Belief",
    "credible_retr_Belief",
    "expert_misinf_Belief",
    "expert_retr_Belief",
    "trust_misinf_Belief",
    "trust_retr_Belief",
]


def fetch_data() -> pd.DataFrame:
    import requests
    r = requests.get(RAW_URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}, timeout=120)
    r.raise_for_status()
    import io
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"Subject": "id"})

    assert df["id"].nunique() == len(df), "id column not unique"

    # Inoculation: 1 = inoculation present (treatment), 2 = control (no
    # inoculation). Direction inferred from data: group coded 1 has
    # substantially lower average misinformation-belief ratings
    # (5.67 vs 7.08 on the raw 1-11 scale) and lower continued-influence
    # accuracy scores, consistent with successful inoculation against the
    # continued influence effect described in the paper's hypothesis.
    df["treat"] = (df["Inoculation"] == 1).astype(int)

    cov_map = {"Age": "cov_age", "Gender": "cov_gender", "Education": "cov_education"}
    df = df.rename(columns=cov_map)
    cov_cols = list(cov_map.values())

    long = df.melt(
        id_vars=["id", "treat"] + cov_cols,
        value_vars=BELIEF_ITEMS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "treat"] + cov_cols
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "buczel_2022_inoculation_belief.csv")
    long.to_csv(out_path, index=False)

    print(f"buczel_2022_inoculation_belief.csv: rows={len(long)} "
          f"ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
