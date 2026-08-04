#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273328
# DOI: 10.1371/journal.pone.0273328
#
# McCarlie VW Jr, Phillips ME, Price BD, Taylor PB, Eckert GJ, Stewart KT
# (2022) Orthodontic and oral health literacy in adults. PLoS ONE 17(8):
# e0273328.
#
# S1 Dataset (XLSX, "172 individuals participated" per the abstract; 176
# rows in the raw file) contains an 11-item binary (0=incorrect,
# 1=correct) orthodontic-literacy knowledge quiz (Q2_straighten_teeth ...
# Q12_when_don_t_have_to_wear_any_). Aggregate/derived columns
# (__correct_ortho, OrthoLiteracy, REALMD20, OHLItotal, OHLIknowledge,
# OHLIcomprehension, OHLInumeracy) are excluded -- they are composite scores,
# not raw item responses. No person-ID column exists, so the row index is
# used as `id`.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0273328.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [
    "Q2_straighten_teeth", "Q3_ab_2_yrs", "Q4__every_4_6_wks", "Q5_may_ache_a_bit",
    "Q6_fixed_metal", "Q7_am_pm__if_possible_after_ever", "Q8_decay__gum_disease",
    "Q9_foods_drinks__brushing_diffic", "Q10_ASAP", "Q11_Yes",
    "Q12_when_don_t_have_to_wear_any_",
]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    print("Fetching S1 Dataset (XLSX)...")
    raw = fetch_raw()
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)

    long = raw.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "mccarlie_2022_ortho_literacy.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
