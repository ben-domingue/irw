#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0128638
# DOI: 10.1371/journal.pone.0128638
# Supporting Information: https://doi.org/10.1371/journal.pone.0128638.s001
#
# 2-wave (pre/post intervention) design, explicit in column suffixes.
# Three raw-item scales used as-is (no direction recoding needed per the
# IRW standard -- reverse items only need to be consistent within
# themselves): caug (10 items, Spanish General Self-Efficacy
# Questionnaire wording), IRI (13 items, Interpersonal Reactivity Index
# short form), TMMS24 (24 items, Trait Meta-Mood Scale). A 35-item CIS
# block was NOT used -- its response categories are item-specific full
# Spanish phrases (not a uniform scale), which would need careful
# per-item translation/ordinal judgment with real risk of getting the
# direction wrong; deferred rather than guessed. A handful of *REC
# columns (recoded twins of reverse-worded items) also exist but weren't
# needed. A few stray numeric values appear among the text categories in
# caug/TMMS24 (e.g. a lone "6.0"/"43.0" where every other value is a
# category label) -- these don't match any map key and are dropped
# automatically via dropna, consistent with the isolated-stray-value
# diagnostic. `nsujeto` is the person id (unique).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0128638.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_CAUG = {"incorrecto": 1, "apenas cierto": 2, "mas bien cierto": 3, "cierto": 4}
MAP_IRI = {"No me describe bien": 1, "Me describe un poco": 2, "Me describe bien": 3,
           "Me describe bastante bien": 4, "Me describe muy bien": 5}
MAP_TMMS = {"nada de acuerdo": 1, "algo de acuerdo": 2, "bastante de acuerdo": 3,
            "muy de acuerdo": 4, "totalmente de acuerdo": 5}

SCALES = {
    "zautra_2015_caug": ("caug", 10, MAP_CAUG),
    "zautra_2015_iri": ("IRI", 13, MAP_IRI),
    "zautra_2015_tmms24": ("TMMS24_", 24, MAP_TMMS),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"sexo": "cov_sex"})
    # nsujeto is unique only WITHIN BBDD (experimental/control) -- 247+103
    # unique ids within each group, confirmed -- composite id needed.
    df["id"] = df["BBDD"].astype(str) + "-" + df["nsujeto"].astype(int).astype(str)
    return df


def write_scale(long: pd.DataFrame, out_name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} waves={sorted(long['wave'].unique())}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)

    for out_name, (prefix, n_items, value_map) in SCALES.items():
        frames = []
        for wave, suffix in [(1, "pre"), (2, "post")]:
            item_names = [f"{prefix}{i}" for i in range(1, n_items + 1)]
            cols = [f"{prefix}{i}{suffix}" for i in range(1, n_items + 1)]
            sub = df[["id", "cov_sex"] + cols].copy()
            sub = sub.rename(columns=dict(zip(cols, item_names)))
            sub["wave"] = wave
            frames.append(sub)
        combined = pd.concat(frames, ignore_index=True)
        item_names = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        long = combined.melt(id_vars=["id", "wave", "cov_sex"], value_vars=item_names,
                              var_name="item", value_name="resp")
        long["resp"] = long["resp"].map(value_map)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        write_scale(long[["id", "item", "resp", "wave", "cov_sex"]], out_name)


if __name__ == "__main__":
    convert()
