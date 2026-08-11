#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0296908
# S1 Dataset: https://doi.org/10.1371/journal.pone.0296908.s002
# DOI: 10.1371/journal.pone.0296908
#
# Zhang & Liu (2024) "Gift-giving intentions in pan-entertainment live
# streaming: Based on social exchange theory". Two-wave survey of TikTok
# live-streaming viewers, N=325. Six constructs, all 5-point Likert
# (1=Strongly Disagree ... 5=Strongly Agree), one file per construct:
#   ATR   Streamer Attractiveness (4 items)
#   EXP   Expertise (3 items)
#   PSI   Parasocial Interaction (3 items)
#   VDSP  Viewer's Deceptive Self-Presentation (6 items)
#   SDSP  Streamer's Deceptive Self-Presentation (4 items)
#   INT   Gift-Giving Intention (3 items)

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0296908.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "zhang_2024_attractiveness": ["ATR1", "ATR2", "ATR3", "ATR4"],
    "zhang_2024_expertise": ["EXP1", "EXP2", "EXP3"],
    "zhang_2024_parasocial": ["PSI1", "PSI2", "PSI3"],
    "zhang_2024_viewer_dsp": ["VDSP1", "VDSP2", "VDSP3", "VDSP4", "VDSP5", "VDSP6"],
    "zhang_2024_streamer_dsp": ["SDSP1", "SDSP2", "SDSP3", "SDSP4"],
    "zhang_2024_gift_intention": ["INT1", "INT2", "INT3"],
}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Income": "cov_income",
    "TotalSpend": "cov_total_spend",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Number": "id"})
    assert df["id"].nunique() == len(df)
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, out_name + ".csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
