#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0146914
# DOI: 10.1371/journal.pone.0146914
# Sun et al. (2016), "Effect of Graph Scale on Risky Choice: Evidence from
# Preference and Process in Decision-Making". CC BY 4.0.
#
# This paper has THREE Supporting Information files (S1/S2/S3 "Dataset:
# experiment N", .sav), one per experiment. Only Experiment 1 (S1,
# id.s001) contains raw per-trial item-level data: 189 undergraduates each
# made 4 binary choices ("resulta".."resultd") between a "probability bet"
# (option A: higher win probability, lower prize) and a "money bet"
# (option B: lower win probability, higher prize) -- e.g. "80% chance of
# $50" vs "40% chance of $100". Coded resp = 1 if the probability bet (A)
# was chosen, 0 if the money bet (B) was chosen; consistent A/B meaning
# within each of the 4 trials satisfies the "consistent direction within
# item" rule. `condition` is the paper's between-subjects graph-scale
# manipulation (compressed-probability-distance vs compressed-money-
# distance display), kept as cov_graph_condition.
#
# Experiments 2 and 3 were EXCLUDED: Experiment 2's S2 file (n=43) holds
# only per-person aggregated measures (mean RT per option, proportion
# choosing each bet type across the 18 trials) rather than raw per-trial
# choices -- a composite, not a raw response. Experiment 3's S3 file
# (n=140) has only a single trial/item ("preference") per participant,
# which violates the no-single-item-scale rule. Neither is shipped.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0146914.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["resulta", "resultb", "resultc", "resultd"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    tmp = OUT_DIR / "_sun2016_tmp.sav"
    tmp.write_bytes(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    tmp.unlink()

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns={"condition": "cov_graph_condition"})

    # Recode A/B choice letters to 1/0 (1 = chose probability bet "A").
    for c in ITEM_COLS:
        df[c] = df[c].map({"A": 1, "B": 0})

    long = df.melt(id_vars=["id", "cov_graph_condition"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_graph_condition"]]

    out_name = "sun_2016_risky_choice_graph.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
