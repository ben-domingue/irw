#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257552
# DOI: 10.1371/journal.pone.0257552
#
# Fukuda Y, Ando S, Fukuda K (2021) Knowledge and preventive actions
# toward COVID-19, vaccination intent, and health literacy among educators
# in Japan: An online survey. PLoS ONE.
#
# S1 Data (XLSX, N=1000) has three raw multi-item batteries, no person-id
# column in the source so row index is used:
#   - "Health literacy item 1".."item 47" (46 present, item 39 missing from
#     the source file -- HLS-EU-Q47-style self-rated task difficulty scale):
#     text-labeled very easy < fairly easy < fairly difficult < very
#     difficult, mapped to 1-4; "don't know"/"neither"/its untranslated
#     Japanese equivalent (どちらとも言えない) treated as missing and
#     dropped, matching the English "neither"/"don't know" sentinels.
#   - "Information reliability: <source>" (8 items, trust in different
#     information sources): untrusted < somewhat unreliable < neither <
#     somewhat reliable < reliable, mapped to 1-5.
#   - "Withholding <activity>" (6 items, binary self-reported behavior
#     restriction during COVID-19): Yes/No mapped to 1/0.
# Single-select demographic/checkbox columns (gender, education, "Key
# sources of information" multi-select flags, single COVID-knowledge
# items) excluded per the no-single-item / not-a-validated-scale rules.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0257552.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

HL_MAP = {
    "very easy": 1,
    "fairly easy": 2,
    "fairly difficult": 3,
    "very difficult": 4,
}
INFO_MAP = {
    "untrusted": 1,
    "somewhat unreliable": 2,
    "neither": 3,
    "somewhat reliable": 4,
    "reliable": 5,
}
YESNO_MAP = {"No": 0, "Yes": 1}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str], value_map: dict, rename) -> pd.DataFrame:
    d = df[item_cols].copy()
    d["id"] = d.index
    for c in item_cols:
        d[c] = d[c].astype(str).str.strip().map(value_map)
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["item"] = long["item"].map(rename)
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    print("Fetching S1 Data (XLSX)...")
    raw = fetch_raw()

    hl_cols = [c for c in raw.columns if c.startswith("Health literacy")]
    hl_rename = {c: f"hl_item{i+1}" for i, c in enumerate(sorted(
        hl_cols, key=lambda s: int("".join(ch for ch in s if ch.isdigit()) or 0)))}
    info_cols = [c for c in raw.columns if "Information reliability" in c]
    info_rename = {c: f"info_source{i+1}" for i, c in enumerate(info_cols)}
    withh_cols = [c for c in raw.columns if c.startswith("Withholding")]
    withh_rename = {c: f"withholding_item{i+1}" for i, c in enumerate(withh_cols)}

    write_scale(build_long(raw, hl_cols, HL_MAP, hl_rename), "fukuda_2021_health_literacy.csv")
    write_scale(build_long(raw, info_cols, INFO_MAP, info_rename), "fukuda_2021_info_reliability.csv")
    write_scale(build_long(raw, withh_cols, YESNO_MAP, withh_rename), "fukuda_2021_withholding_behavior.csv")


if __name__ == "__main__":
    convert()
