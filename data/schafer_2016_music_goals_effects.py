#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0151634
# DOI: 10.1371/journal.pone.0151634
# Schafer, T. et al (2016). "The Goals and Effects of Music Listening and Their
# Relationship to the Strength of Music Preference." PLOS ONE.
#
# S1 Table (Level 1, episode-level diary data, N=1502 listening episodes,
# 121 participants) contains 6 single-item ratings on a 1(not at all)-10(very
# much) scale answered after each music-listening episode:
#   - 3 "goals" items: how important was self-awareness / social relatedness /
#     arousal-and-mood-regulation as a *reason* to listen, in that situation
#   - 3 "effects" items: how strongly did each of those functions *actually
#     occur* through listening, in that situation
# Two additional single-item ratings (music preference, past functional
# experience) exist in the same file but are NOT shipped here since a lone
# item cannot form a >=2-item scale table (see IRW no-single-item-scale rule).
#
# Each participant contributes multiple diary episodes -> duplicate id+item
# is valid because we attach a `wave` column giving the chronological episode
# order for that participant (sorted by day, then situation-within-day).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1371/journal.pone.0151634"
TITLE = "The Goals and Effects of Music Listening and Their Relationship to the Strength of Music Preference"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

S1_URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0151634.s001&type=supplementary"

GOALS_ITEMS = {
    "goals self-awareness": "goals_self_awareness",
    "goals social relatedness": "goals_social_relatedness",
    "goals arousal and mood": "goals_arousal_mood",
}

EFFECTS_ITEMS = {
    "effects self-awareness": "effects_self_awareness",
    "effects social relatedness": "effects_social_relatedness",
    "effects emotion and mood": "effects_emotion_mood",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(S1_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    return df


def add_wave(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["participant", "day", "situation"]).reset_index(drop=True)
    df["wave"] = df.groupby("participant").cumcount() + 1
    return df


def build_long(df: pd.DataFrame, item_map: dict) -> pd.DataFrame:
    cols = ["participant", "wave"] + list(item_map.keys())
    sub = df[cols].copy()
    sub = sub.rename(columns={"participant": "id"})
    sub = sub.rename(columns=item_map)
    item_names = list(item_map.values())

    long = sub.melt(
        id_vars=["id", "wave"],
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp", "wave"]
    return long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Downloading S1 Table (episode-level diary data) ...")
    raw = fetch_data()
    raw = add_wave(raw)

    goals = build_long(raw, GOALS_ITEMS)
    effects = build_long(raw, EFFECTS_ITEMS)

    write_scale(goals, "schafer_2016_music_goals.csv")
    write_scale(effects, "schafer_2016_music_effects.csv")


if __name__ == "__main__":
    convert()
