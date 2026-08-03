#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243890
# DOI: 10.1371/journal.pone.0243890
# Shen et al. (2020), "Investigation of anxiety levels of 1637 healthcare
# workers during the epidemic of COVID-19", PLOS ONE. CC BY 4.0.
# Raw data is split across 5 supplementary files, one per participating
# hospital, each with the identical 20-item Zung Self-Rating Anxiety Scale
# (SAS) in its standard item order (columns numbered 11-30, following 10
# demographic questions in the original survey). Merged here with a
# per-hospital `id` offset since each file's "Subjects" column restarts at 1.
# Download raw files:
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.s001
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.s002
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.s003
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.s004
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.s005

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
HOSPITALS = {
    1: ("s001", "Chunan Hospital of Traditional Chinese Medicine"),
    2: ("s002", "Hangzhou Hospital of Traditional Chinese Medicine"),
    3: ("s003", "Children's Hospital, Zhejiang University School of Medicine"),
    4: ("s004", "First Affiliated Hospital, Zhejiang University School of Medicine"),
    5: ("s005", "Xiaoshan First People's Hospital"),
}
ITEM_NUMBERS = range(11, 31)  # the 20 SAS items, in standard SAS order


def fetch_one(suffix: str) -> pd.DataFrame:
    url = f"https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243890.{suffix}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    frames = []
    for hosp_num, (suffix, hosp_name) in HOSPITALS.items():
        df = fetch_one(suffix)
        item_cols = [c for c in df.columns if c.split(":", 1)[0].isdigit()
                     and int(c.split(":", 1)[0]) in ITEM_NUMBERS]
        assert len(item_cols) == 20, f"hospital {hosp_num}: found {len(item_cols)} SAS items"

        out = df[["Subjects"] + item_cols].copy()
        out["id"] = out["Subjects"] + hosp_num * 10000
        out["cov_hospital"] = hosp_name
        for i, c in enumerate(item_cols, start=1):
            out[c] = out[c].astype(str).str.extract(r"\((\d+(?:\.\d+)?)\)")[0].astype(float)
        out = out.rename(columns={c: f"sas_{i}" for i, c in enumerate(item_cols, start=1)})
        frames.append(out[["id", "cov_hospital"] + [f"sas_{i}" for i in range(1, 21)]])

    df = pd.concat(frames, ignore_index=True)
    item_cols = [f"sas_{i}" for i in range(1, 21)]

    long = df.melt(id_vars=["id", "cov_hospital"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_hospital"]]

    path = os.path.join(OUT_DIR, "shen_2020_sas20.csv")
    long.to_csv(path, index=False)
    print(f"shen_2020_sas20: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
