#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EDEVGY
# DOI: 10.7910/DVN/EDEVGY
# Social support (SS), emotional intelligence (EI), loneliness (LN), and beliefs (BL)
# in students using AI for homework help. Spanish. N≈300.
# Subscale aggregate columns (SS_FAMIL, EI_TT, etc.) are excluded.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "galindo_2023_social_support":        [f"SS0{i}{'MIFA' if i==1 else 'RECI' if i==2 else 'MISA' if i==3 else 'PUED' if i in [4,5,8] else 'TENG' if i==6 else 'MIFA' if i==7 else ''}" for i in range(1, 9)],
    "galindo_2023_emotional_intelligence": [f"EI{i:02d}" for i in range(1, 17)],
    "galindo_2023_loneliness":            [f"LN{i:02d}" for i in range(1, 4)],
    "galindo_2023_beliefs":               [f"BL{i:02d}" for i in range(1, 6)],
}

COV_COLS = ["EDADSOLO", "GÉNERO", "COUNTRY"]


def convert():
    r = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/",
                     params={"persistentId": "doi:10.7910/DVN/EDEVGY"},
                     headers=UA, timeout=20)
    files = r.json().get("data", {}).get("latestVersion", {}).get("files", [])
    df = None
    for f in files:
        dm = f.get("dataFile", {})
        if "Categories_Main" in dm.get("filename", ""):
            fid = dm.get("id")
            r2 = requests.get(f"https://dataverse.harvard.edu/api/access/datafile/{fid}",
                              headers=UA, timeout=60)
            df = pd.read_csv(io.StringIO(r2.content.decode("utf-8", errors="replace")),
                             sep="\t")
            break

    # Use row index as id (no unique person ID column)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    cov_present = [c for c in COV_COLS if c in df.columns]
    cov_rename = {c: f"cov_{c.lower().replace('é','e')}" for c in cov_present}
    df = df.rename(columns=cov_rename)
    cov_out = list(cov_rename.values())

    # Build scale column lists from actual column names (handles encoding)
    def find_cols(prefix, n):
        return [c for c in df.columns if str(c).startswith(prefix) and
                not any(x in str(c) for x in ["_FAMIL","_FRIEN","_TT","_SEA","_OEA","_UOE","_ROE","_RECOD","_RECO"])]

    scale_map = {
        "galindo_2023_social_support":         find_cols("SS", 8),
        "galindo_2023_emotional_intelligence": find_cols("EI", 16),
        "galindo_2023_loneliness":             find_cols("LN", 3),
        "galindo_2023_beliefs":                find_cols("BL", 5),
    }

    for out_name, item_cols in scale_map.items():
        if not item_cols:
            print(f"SKIP {out_name}: no columns found")
            continue
        long = df.melt(id_vars=["id"] + cov_out, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # Keep only the clean 4-char alphanumeric prefix (e.g. SS01, EI01, LN01, BL01)
        long["item"] = long["item"].str.slice(0, 4)
        long = long[["id", "item", "resp"] + cov_out]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
