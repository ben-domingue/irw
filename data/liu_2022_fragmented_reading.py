#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9415515
# DOI: 10.7717/peerj.13861
#
# "The effects of university students' fragmented reading on cognitive
# development in the new media age: evidence from Chinese higher education".
# Europe PMC supplementary file s001 (XLS) is the raw per-student item
# responses (N=916) to two 5-point-Likert instruments: the Fragmented
# Reading Questionnaire (FRQ, 22 items: N8_1-N8_22) and the Cognitive
# Development Questionnaire (CDQ, 11 items: N9_1-N9_11). N1-N7 are
# demographic covariates (gender, grade, age, major, etc.); no PII.
# CC BY 4.0 (PeerJ).

import io
import os
import zipfile

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9415515/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "N1": "cov_gender",
    "N2": "cov_grade",
    "N3": "cov_age",
    "N4": "cov_degree_level",
    "N5": "cov_major",
    "N6": "cov_c6",
    "N7": "cov_c7",
}

SCALES = {
    "liu_2022_fragreading_frq": [f"N8_{i}" for i in range(1, 23)],
    "liu_2022_fragreading_cdq": [f"N9_{i}" for i in range(1, 12)],
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    xls_name = [n for n in zf.namelist() if n.endswith("s001.xls")][0]
    df = pd.read_excel(io.BytesIO(zf.read(xls_name)))

    df = df.rename(columns={"Serial No.": "id"})
    df = df.rename(columns=COV_COLS)
    cov_cols = list(COV_COLS.values())

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # 5-point Likert scale
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
