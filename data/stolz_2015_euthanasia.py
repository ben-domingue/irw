#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0124320
# DOI: 10.1371/journal.pone.0124320
#
# Stolz E, Burkert N, Grossschaedl F, Rasky E, Stronegger WJ, Freidl W (2015)
# Determinants of Public Attitudes towards Euthanasia in Adults and
# Physician-Assisted Death in Neonates in Austria: A National Survey.
# PLoS ONE 10(4): e0124320.
#
# S1 Dataset (SAV) is a national survey (N=1971) with many sociodemographic
# columns plus two genuine multi-item Likert scales:
#   - c14x1..c14x6: 6-item attitudes-toward-death/euthanasia-legalization scale
#     (4-pt agreement scale: 1=stimme voellig zu ... 4=stimme ueberhaupt nicht
#     zu; value 5="weiss nicht" was a "don't know" sentinel with no observed
#     rows in the data, so no filtering needed there)
#   - c15x1..c15x8: 8-item Authoritarianism scale (matches S2 Table caption:
#     "Authoritarianism: Descriptive statistics and factor loadings.
#     Cronbach's alpha = 0.79 ... one factor extracted"), same 4-pt scale.
# Other columns (st*, c1-c13 singles) are sociodemographics or single vignette
# items and are excluded per the no-single-item-scale rule.

import io
import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0124320.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

DEATH_ITEMS = ["c14x1", "c14x2", "c14x3", "c14x4", "c14x5", "c14x6"]
AUTH_ITEMS = ["c15x1", "c15x2", "c15x3", "c15x4", "c15x5", "c15x6", "c15x7", "c15x8"]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_stolz_2015_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp_path, apply_value_formats=False)
    os.remove(tmp_path)
    return df


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[["nummer"] + item_cols].copy()
    d = d.rename(columns={"nummer": "id"})
    d["id"] = pd.to_numeric(d["id"], errors="coerce")
    d = d.dropna(subset=["id"])
    assert d["id"].is_unique, "id column not unique"

    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # values are integer-coded 1-4; value 5 ("don't know") never appears in data
    long = long[(long["resp"] >= 1) & (long["resp"] <= 4)]
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 Dataset (SAV)...")
    raw = fetch_raw()

    death = build_long(raw, DEATH_ITEMS)
    auth = build_long(raw, AUTH_ITEMS)

    write_scale(death, "stolz_2015_death_attitudes.csv")
    write_scale(auth, "stolz_2015_authoritarianism.csv")


if __name__ == "__main__":
    convert()
