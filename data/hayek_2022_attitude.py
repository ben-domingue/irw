#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0265595
# DOI: 10.1371/journal.pone.0265595
# "Authoritative parenting stimulates academic achievement, also partly via
#  self-efficacy and intention towards getting good grades" (Hayek et al. 2022,
#  PLOS ONE)
#
# S1 Dataset (journal.pone.0265595_S1_Dataset.sav) is a Theory-of-Planned-
# Behaviour-style survey of 345 secondary-school students in Lebanon. Three
# genuine item-level Likert (-2..2, Strongly disagree..Strongly agree) batteries
# are present:
#   - Attitude toward getting good grades: Att_PRO1, Att_PRO2, Att_CON1, Att_CON2 (4 items)
#   - Subjective norm (father/mother/teacher): S_N_1-3 (3 items)
#   - Self-efficacy: S_eff_1-5 (5 items)
# "Intent" is a single item (excluded -- no single-item scales). Tot_Att and
# Tot_Seff are pre-computed aggregate totals (excluded).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0265595.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "attitude": ["Att_PRO1", "Att_PRO2", "Att_CON1", "Att_CON2"],
    "subj_norm": ["S_N_1", "S_N_2", "S_N_3"],
    "self_efficacy": ["S_eff_1", "S_eff_2", "S_eff_3", "S_eff_4", "S_eff_5"],
}

COV_RENAME = {
    "Gender": "cov_gender",
    "Type_sch": "cov_school_type",
    "Age.2": "cov_age",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _meta = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


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
    print("Downloading journal.pone.0265595_S1_Dataset.sav …")
    raw = fetch_data()

    raw = raw.rename(columns={"ID": "id", **COV_RENAME})
    assert raw["id"].nunique() == len(raw), "id is not unique"

    prefix_map = {"attitude": "att", "subj_norm": "sn", "self_efficacy": "se"}
    fname_map = {
        "attitude": "hayek_2022_attitude.csv",
        "subj_norm": "hayek_2022_subj_norm.csv",
        "self_efficacy": "hayek_2022_self_efficacy.csv",
    }
    for scale, cols in SCALES.items():
        long = build_long(raw, cols, prefix_map[scale])
        write_scale(long, fname_map[scale])


if __name__ == "__main__":
    convert()
