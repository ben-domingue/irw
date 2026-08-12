#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0180102
# DOI: 10.1371/journal.pone.0180102

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0180102.s003"

# Zhang et al.'s 14 usability heuristics + TAM's 3 constructs, each its own scale
SCALES = {
    "tam_pu": (["PU1", "PU2", "PU3", "PU4", "PU5"], "perceived usefulness"),
    "tam_peou": (["PEOU1", "PEOU2", "PEOU3", "PEOU4", "PEOU5", "PEOU6"], "perceived ease of use"),
    "tam_bi": (["BI1", "BI2", "BI3", "BI4"], "behavioral intention"),
    "h1_consistency": (["H1-1", "H1-2", "H1-3", "H1-4", "H1-5", "H1-6"], "consistency"),
    "h2_visibility": (["H2-1", "H2-2", "H2-3", "H2-4"], "visibility"),
    "h3_match": (["H3-1", "H3-2", "H3-3"], "match"),
    "h4_minimalist": (["H4-1", "H4-2", "H4-3", "H4-4"], "minimalist design"),
    "h5_memory": (["H5-1", "H5-2", "H5-3", "H5-4", "H5-5", "H5-6", "H5-7"], "memory load"),
    "h6_feedback": (["H6-1", "H6-2", "H6-3", "H6-4"], "feedback"),
    "h7_flexibility": (["H7-1", "H7-2", "H7-3"], "flexibility"),
    "h8_message": (["H8-1", "H8-2", "H8-3"], "message clarity"),
    "h9_error": (["H9-1", "H9-2", "H9-3", "H9-4"], "error prevention"),
    "h10_closure": (["H10-1", "H10-2", "H10-3"], "closure"),
    "h11_undo": (["H11-1", "H11-2", "H11-3", "H11-4"], "undo"),
    "h12_language": (["H12-1", "H12-2", "H12-3"], "language"),
    "h13_control": (["H13-1", "H13-2"], "control"),
    "h14_document": (["H14-1", "H14-2", "H14-3"], "documentation"),
}


def load_raw():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/tsai_2017.xlsx"
    with open(tmp, "wb") as f:
        f.write(r.content)

    raw = pd.read_excel(tmp, header=None)
    colnames = raw.iloc[1].tolist()
    df = raw.iloc[2:].copy()
    df.columns = colnames
    df = df.reset_index(drop=True)

    df["id"] = pd.to_numeric(df["Participants"], errors="coerce")
    df["cov_gender"] = df["Gender"].astype(str)
    df["cov_age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["cov_education"] = df["Educatoin"].astype(str)
    df["cov_sns_experience"] = df["SNS Experience"].astype(str)
    return df


def convert():
    df = load_raw()
    os.makedirs(OUT_DIR, exist_ok=True)

    cov_cols = ["cov_gender", "cov_age", "cov_education", "cov_sns_experience"]

    for out_name, (item_cols, _label) in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")

        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        fname = f"tsai_2017_treeit_{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
