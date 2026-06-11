#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/11283215
# DOI (data): 10.3389/fpsyg.2019.02550.s001
# DOI (paper): 10.3389/fpsyg.2019.02550
# Factor structure & measurement invariance of Youth Psychopathic Traits Inventory-Child
# Version (YPIC) in Chinese children. N=299. Also includes CPTI, SDQ, SCPV.
# Missing value codes: YPIC/SCPV -> 99/999, CPTI/SDQ -> 9. Filtered before output.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (scale_prefix, output_name, max_valid_resp)
SCALES = [
    ("YPIC", "ren2019_ypic",  4),
    ("CPTI", "ren2019_cpti",  4),
    ("SDQ",  "ren2019_sdq",   3),
    ("SCPV", "ren2019_scpv",  5),
]

COV_MAP = {
    "gender":    "cov_gender",
    "age":       "cov_age",
    "EDUCATION": "cov_education",
    "INCOME":    "cov_income",
}


def convert():
    r = requests.get("https://ndownloader.figshare.com/files/19972844",
                     headers=UA, timeout=60)
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.rename(columns=COV_MAP)
    df["id"] = pd.to_numeric(df["ID"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    cov_cols = list(COV_MAP.values())

    for prefix, out_name, max_resp in SCALES:
        item_cols = [c for c in df.columns if c.startswith(prefix)]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[long["resp"] <= max_resp].dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
