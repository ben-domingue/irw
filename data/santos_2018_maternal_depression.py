#!/usr/bin/env python3
# Source: https://osf.io/e9r5s/ (raw data file "Santos_PlosOne.txt")
# Paper: Santos HP Jr, Kossakowski JJ, Schwartz TA, Beeber L, Fried EI (2018).
#   Longitudinal network structure of depression symptoms and self-efficacy
#   in low-income mothers. PLOS ONE, 13(1), e0191675.
#   https://doi.org/10.1371/journal.pone.0191675
# GitHub issue: https://github.com/ben-domingue/irw/issues/1557 ("permission
#   from author" -- processed on direct author permission, not an open
#   license posted on the OSF page.)
#
# N=306 low-income mothers (two combined RCTs, 2003-2010), up to 4 waves
# (baseline, 14wk, 22wk, 26wk post-baseline; not all participants retained
# at every wave). Two instruments in the same raw file, each written to its
# own output file per the one-scale-per-file rule:
#   - GSE: 10-item Generalized Self-Efficacy scale, 1-4 response range.
#     Column names (gse2, gse4, gse5, gse8, gse9, gse10, gse12, gse13,
#     gse17, gse18) are kept as-is -- they are the item numbers from the
#     source instrument's larger item bank, not arbitrary positions.
#     "GSEcomponent" is a PCA composite of these 10 items computed for the
#     paper's network analysis (not a raw response) -- excluded.
#   - CESD: 20-item CES-D depression scale, 0-3 response range.
#     "CESDtot" is the aggregate sum -- excluded.
# "RX" is the RCT intervention/control assignment (2=intervention,
# 1=control per the paper's Methods), constant within id across waves --
# mapped to the standard treat encoding (1=intervention, 0=control).
# "time" (1-4) is the longitudinal wave, larger=later, already in the
# correct direction -- kept as-is as `wave`.
# The value 9 appears sparsely (1-2 times) on every single item in both
# scales, consistent with a missing-data sentinel outside each scale's
# documented range (1-4 / 0-3) -- filtered out. A small number of isolated
# `4`s on two CES-D items (cesd12, cesd13; otherwise 0-3) are data-entry
# errors by the cross-item-consistency check and are dropped too. The
# paper's own missing-data text ("we estimated GGMs ... using pairwise
# complete observations") confirms no imputation was applied to this raw
# file.

import os

import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = "https://osf.io/download/w9fbc/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

GSE_COLS = ["gse2", "gse4", "gse5", "gse8", "gse9", "gse10", "gse12", "gse13", "gse17", "gse18"]
CESD_COLS = [f"cesd{i}" for i in range(1, 21)]


def load_raw():
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text), sep=" ")


def base_frame(d):
    out = d[["ID", "time", "RX"]].copy()
    out = out.rename(columns={"ID": "id", "time": "wave"})
    out["treat"] = (out["RX"] == 2).astype(int)
    out = out.drop(columns=["RX"])
    return out


def make_scale(d, item_cols, valid_min, valid_max, out_name):
    base = base_frame(d)
    item_frame = pd.concat([base, d[item_cols]], axis=1)

    long = item_frame.melt(
        id_vars=["id", "wave", "treat"],
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )

    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)].reset_index(drop=True)

    long = long[["id", "item", "resp", "wave", "treat"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    d = load_raw()
    assert d["ID"].nunique() == 306

    make_scale(d, GSE_COLS, 1, 4, "santos_2018_gse.csv")
    make_scale(d, CESD_COLS, 0, 3, "santos_2018_cesd.csv")


if __name__ == "__main__":
    convert()
