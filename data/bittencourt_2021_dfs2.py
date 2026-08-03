#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0253044
# DOI: 10.1371/journal.pone.0253044
# Bittencourt et al. (2021), "Validation and psychometric properties of the
# Brazilian-Portuguese dispositional flow scale 2 (DFS-BR)", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0253044.s003

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0253044.s003"

ITEM_COLS = [f"Q{i}" for i in range(1, 37)]
COV_RENAME = {
    "gender": "cov_gender",
    "civil status": "cov_civil_status",
    "ethnic": "cov_ethnicity",
    "socioeconomic status": "cov_socioeconomic_status",
    "sexual orientation": "cov_sexual_orientation",
}
COV_COLS = list(COV_RENAME.values())


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    # "activity" is free text (what the respondent was doing during flow
    # assessment) -- not a usable covariate.

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    path = os.path.join(OUT_DIR, "bittencourt_2021_dfs2.csv")
    long.to_csv(path, index=False)
    print(f"bittencourt_2021_dfs2: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
