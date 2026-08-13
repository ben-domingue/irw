#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0194569
# DOI: 10.1371/journal.pone.0194569
#
# "The effects of exposure to images of others' suffering and vulnerability
# on altruistic, trust-based, and reciprocated economic decision-making"
# (Powell, 2018)
#
# Two experiments (Experiment 1 n=317, Experiment 2 n=202) that the paper's
# Methods confirm used identical measures: "the same measures as described
# in Experiment 1 were used" in Experiment 2 for the QCAE empathy
# questionnaire and Trust measure; the 5-item affective-state mood check and
# 5-item incidental memory check are likewise administered the same way in
# both. Per datastandard.md's same-instrument/multiple-samples rule, the two
# experiments are merged into single files, offsetting Experiment 2's id by
# +100000 (source ID numbering restarts at 1 within each experiment) so ids
# stay unique across the merged sample.
#
# Four separate scales/tasks, each its own output file:
#   - QCAE (Questionnaire of Cognitive and Affective Empathy), 31 items, 4-pt
#     Likert (1=strongly disagree .. 4=strongly agree). The rQCAE* columns
#     are the source file's own reverse-recoded duplicates of some QCAE
#     items and are dropped to avoid double-counting the same item.
#   - Trust measure (adapted SOEP-Trust), 3 items, 4-pt Likert. rTrust3 is
#     likewise a recoded duplicate of Trust3 and is dropped.
#   - Affective state, 5 items (happy/sad/disgust/proud/compassion), 4-pt
#     Likert (1=not at all .. 4=very), "How do you feel right now?"
#   - Memory, 5 binary (0/1) incidental-memory-check items.
# Composite/derived columns (CE, AE, TrustScore, MemoryScore, and the
# economic-game decision variables) are excluded as aggregates, not raw
# item responses.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://doi.org/10.1371/journal.pone.0194569.s005"

QCAE_ITEMS = [f"QCAE{i}" for i in range(1, 32)]
TRUST_ITEMS = ["Trust1", "Trust2", "Trust3"]
AFFECT_ITEMS = ["Happy", "Sad", "Disgust", "Proud", "Compassion"]
MEMORY_ITEMS = ["Memory1", "Memory2", "Memory3", "Memory4", "Memory5"]

COV_MAP = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Origin": "cov_origin",
    "Econ": "cov_econ_background",
    "Affiliation": "cov_affiliation",
    "Condition": "cov_condition",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=60)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_csv(BytesIO(r.content))


def prep_id(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    assert df.groupby("Experiment")["ID"].apply(lambda s: s.nunique() == len(s)).all(), \
        "ID not unique within an experiment"
    df["id"] = df["ID"].astype(int) + 100000 * df["Experiment"].astype(int)
    return df


def build_long(df: pd.DataFrame, items: list[str], out_name: str, item_prefix_strip: str = ""):
    cov_cols = list(COV_MAP.values())
    item_cols = [c for c in items if c in df.columns]

    long = df[["id"] + cov_cols + item_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Downloading S1 Dataset …")
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    df = prep_id(raw)

    build_long(df, QCAE_ITEMS, "powell_2018_qcae.csv")
    build_long(df, TRUST_ITEMS, "powell_2018_trust.csv")
    build_long(df, AFFECT_ITEMS, "powell_2018_affect.csv")
    build_long(df, MEMORY_ITEMS, "powell_2018_memory.csv")


if __name__ == "__main__":
    convert()
