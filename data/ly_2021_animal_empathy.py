#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247808
# DOI: 10.1371/journal.pone.0247808
# Supporting Information: https://doi.org/10.1371/journal.pone.0247808.s003
#
# Each of 30 participants rated 10 of 20 farm-animal videos (some depicting
# a painful procedure, some not) on 7 emotion dimensions (Pain, Anger,
# Fear, Disgust, Sadness, Happiness, Surprise; 0-10 continuous). Since
# participant x video is unique (verified: no participant saw the same
# video twice), item is defined as video_id + emotion so that ratings of
# the same video are comparable across participants. LAU/LEX (facial
# action-unit coding) and P_NP (pain/no-pain condition) are trial-level
# attributes, not response items, and are dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0247808.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

EMOTIONS = ["Pain", "Anger", "Fear", "Disgust", "Sadness", "Happiness", "Surprise"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    df = df.rename(columns={"PARTICIPANT": "id"})

    long = df.melt(id_vars=["id", "VIDEO_ID"], value_vars=EMOTIONS,
                    var_name="emotion", value_name="resp")
    long["item"] = long["VIDEO_ID"] + "_" + long["emotion"]
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "ly_2021_animal_empathy.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
