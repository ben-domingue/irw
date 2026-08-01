#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179185
# DOI: 10.1371/journal.pone.0179185
# Lopes de Jesus et al. (2017), "Comparison between intra-articular ozone and
# placebo in the treatment of knee osteoarthritis: A randomized, double-blinded,
# placebo-controlled study". S4 File. CC BY 4.0.
#
# One RCT dataset, four separate instruments -> four output files:
#   Lequesne Algofunctional Index (8 items), SF-36 (22 items),
#   WOMAC (24 items), Geriatric Pain Measure / GPM (24 items).
# id = Number (patient), wave = Week (1/4/8/16), treat = Group (1=ozone, 0=placebo).
# TUG (seconds) and the standalone VAS pain item are single-item measures and
# are intentionally not shipped (no single-item scales).

import io
import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0179185.s004")

COV_RENAME = {
    "Schooling": "cov_schooling",
    "Age (years)": "cov_age",
    "Marital status": "cov_marital_status",
    "Sex": "cov_sex",
    "Race": "cov_race",
    "Knee": "cov_knee",
}


def convert():
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    r = requests.get(SI_URL, headers=headers, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])

    df = df.rename(columns={"Number": "id", "Week": "wave"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["wave"] = pd.to_numeric(df["wave"], errors="coerce")

    df["treat"] = (df["Group"] == "Treatment").astype(int)

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    # Covariates are collected at baseline only but repeated across visit
    # rows in the source file; a couple of patients have a stray second
    # value (e.g. Schooling/Age updated between visits) -- use each
    # patient's first non-null value throughout.
    for c in cov_cols:
        df[c] = df.groupby("id")[c].transform("first")

    leq_cols = ["Leq. Night", "Leq. Morning", "Leq. Standing", "Leq. Walking",
                "Leq. Going up", "Leq. Dist.", "Leq. Life dificulty 1",
                "Leq. Life dificulty 2", "Leq. Life dificulty 3",
                "Leq. Life dificulty 4"]
    sf36_cols = [c for c in df.columns if c.startswith("SF-36")]
    womac_cols = [c for c in df.columns if c.startswith("WOM ")]
    gpm_cols = [c for c in df.columns if c.startswith("GPM")]

    scales = {
        "dejesus_2017_lequesne": leq_cols,
        "dejesus_2017_sf36": sf36_cols,
        "dejesus_2017_womac": womac_cols,
        "dejesus_2017_gpm": gpm_cols,
    }

    id_vars = ["id", "wave", "treat"] + cov_cols

    for out_name, item_cols in scales.items():
        long = df.melt(id_vars=id_vars, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp", "wave", "treat"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.1f}-{long['resp'].max():.1f}")


if __name__ == "__main__":
    convert()
