#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0291647 (S8 Data)
# DOI: 10.1371/journal.pone.0291647 (paper); data 10.1371/journal.pone.0291647.s008
#   Meng P, Meng X, Hu R, Zhang L (2023). Predicting the aesthetics of dynamic generative art.
#   PLoS ONE 18(9): e0291647.
# License: CC BY 4.0 (PLOS article and its figshare SI record)
# Data: pone.0291647.s008.xlsx, "Individual aesthetic ratings for each image in the ISs":
#   participant_id, image_sequence (1-8) and time_12..time_144, one column per image.
#   Methods: eight generative artworks, each converted to an image sequence (IS) of twelve
#   images shown at 12-s steps of its 144-s generation, rated by 1,701 Chinese adults (54.1%
#   female, age M 30.43) in an online survey on a 7-point scale. Each participant rated ONE
#   sequence (211-216 per sequence); the file has 1,701 ids, 8 sequences, values 1-7, no blanks.
#
# Table: meng_2023_generative_art -- item "is<k>_t<sec>" = image at second <sec> of sequence k
#   (96 items; each person answers the 12 of their sequence). resp = rating 1-7.
#   cov_sequence carries the sequence the person rated. The paper's GIF ratings are not in S8.
# id: participant_id as deposited.
# Item text: not shipped -- the items are images (the stimuli are figures in the paper), not text.
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
URL = "https://ndownloader.figshare.com/files/42419544"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    times = [c for c in d.columns if str(c).startswith("time_")]
    assert len(times) == 12
    d = d.dropna(subset=["participant_id"])
    assert len(d) == 1701 and d["participant_id"].is_unique
    d["id"] = d["participant_id"].astype(int)
    d["cov_sequence"] = d["image_sequence"].astype(int)
    t = d[["id", "cov_sequence"] + times].melt(id_vars=["id", "cov_sequence"], var_name="time", value_name="resp")
    assert t["resp"].notna().all()
    t["item"] = "is" + t["cov_sequence"].astype(str) + "_t" + t["time"].str.replace("time_", "", regex=False)
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 7).all() and len(t) == 1701 * 12 and t["item"].nunique() == 96
    assert not t.duplicated(["id", "item"]).any()
    t = t[["id", "item", "resp", "cov_sequence"]].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "meng_2023_generative_art.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
