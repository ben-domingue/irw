#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0330637
# DOI: 10.1371/journal.pone.0330637
# "How electronic health literacy influences physical activity behaviour among
#  university students: A moderated mediation model" (Zhou et al. 2025, PLOS ONE)
#
# S1 Data (journal.pone.0330637_S1_Data.xlsx) contains raw survey responses for
# 14,892 university students recruited from 4 schools in 3 regions ("Questionnaire"
# groups: Eastern China / Shangqiu / Central China). The "Number" column resets
# within each region group, so it is NOT unique on its own -- a composite of
# Number + Questionnaire (region group) is unique across all rows and is used as id.
#
# Two genuine item-level Likert batteries are present:
#   - eHealth Literacy Scale: 8 items (@32 ...), 1-5 scale
#   - Peer Relationship scale: 16 items (@35 ...), 1-4 scale
# "Exercise Behaviour", "Sleep Quality", "Ehealth Literacy", "Peer Relationship"
# columns are pre-computed aggregate/composite scores -- excluded from item lists.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0330637.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

EH_COLS = [
    "@32、2-1 I know how to go online to find useful health resource information",
    "@32、2-2 I know how to use the internet to answer my health questions",
    "@32、2-3 I know what health resource information is available from the internet",
    "@32、2-4 I know where to get useful information on health resources from the web",
    "@32、2-5 I know how to use the information obtained on web-based health resources",
    "@32、2-6 I have the skills to evaluate good and bad information about online health resources",
    "@32、2-7 I am able to differentiate between high and low quality health resource information on the web",
    "@32、2-8 I am confident in applying online information to make health-related decisions",
]

PR_COLS = [
    "@35、1, I make new friends easily at school",
    "@35、2, I can't find anyone to talk to",
    "@35、3, I am good at studying with other students",
    "@35、4, I don't make friends easily",
    "@35、5, I have a lot of friends",
    "@35、6, I feel lonely",
    "@35、7, When I need a friend I can find",
    "@35、8, I have a hard time getting other students to like me",
    "@35、9, there's no one to play with",
    "@35、10, I get along well with other students",
    "@35、11, I feel that people don't want to play with me",
    "@35、12，Nobody helps me when I need help.",
    "@35、13，I don't get along with other students.",
    "@35、14，I'm always alone.",
    "@35、15，Everyone in my class loves me.",
    "@35、16，I don't have any friends.",
]

COV_RENAME = {
    "@1、Your School：": "cov_school",
    "@4、Your gender": "cov_gender",
    "@5、Your age？": "cov_age",
    "@7、What grade are you currently in？": "cov_grade",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Data")


def build_long(df: pd.DataFrame, item_cols: list[str], item_prefix: str) -> pd.DataFrame:
    cov_cols = list(COV_RENAME.values())
    keep = ["id"] + cov_cols + item_cols
    sub = df[keep].copy()
    sub = sub.rename(columns={c: f"{item_prefix}{i+1}" for i, c in enumerate(item_cols)})
    item_names = [f"{item_prefix}{i+1}" for i in range(len(item_cols))]

    long = sub.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    return long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(
        f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


def convert() -> None:
    print("Downloading journal.pone.0330637_S1_Data.xlsx …")
    raw = fetch_data()
    raw = raw.dropna(how="all").reset_index(drop=True)

    raw = raw.rename(columns=COV_RENAME)
    # composite id: per-region "Number" resets, so combine with region group
    raw["id"] = raw["Questionnaire"].astype(str) + "_" + raw["Number"].astype(str)
    assert raw["id"].nunique() == len(raw), "id is not unique after compositing"

    eh = build_long(raw, EH_COLS, "eh")
    pr = build_long(raw, PR_COLS, "pr")

    write_scale(eh, "zhou_2025_ehealth_literacy.csv")
    write_scale(pr, "zhou_2025_peer_relationship.csv")


if __name__ == "__main__":
    convert()
