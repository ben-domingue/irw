#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206899
# DOI: 10.1371/journal.pone.0206899
# SI: S1 File (10.1371/journal.pone.0206899.s002), SPSS .sav

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0206899.s002&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Motivation to attend/during-session activity assessed by staff on a
# 5-point Likert scale (paper Methods): 0=no motivation, 1=low,
# 2=moderate, 3=high, 4=very high.
MOT_MAP = {
    "no": 0,
    "low": 1,
    "moderate": 2,
    "high": 3,
    "very high": 4,
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))

    df = df.rename(columns={"cod_nr": "id", "act_nr": "wave", "typ_act": "item"})
    df["resp"] = df["mot_act"].astype(str).str.strip().str.lower().map(MOT_MAP)
    df = df.dropna(subset=["resp", "id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    df["wave"] = pd.to_numeric(df["wave"], errors="coerce").astype(int)
    df["item"] = df["item"].str.strip().str.lower().str.replace(" ", "_")
    df["resp"] = df["resp"].astype(int)

    out = df[["id", "item", "resp", "wave"]].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "sondell_2018_dementia_motivation.csv"
    out.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(out)} ids={out['id'].nunique()} "
          f"items={out['item'].nunique()} resp={out['resp'].min()}-{out['resp'].max()}")


if __name__ == "__main__":
    convert()
