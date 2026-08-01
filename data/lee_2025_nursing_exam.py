#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PWV6H2
# DOI: 10.7910/DVN/PWV6H2
# License: CC0 1.0

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://dataverse.harvard.edu/api/access/datafile/13126442"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    raw_path = os.path.join(OUT_DIR, "_lee_2025_raw.tab")
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_csv(raw_path, sep="\t")
    os.remove(raw_path)

    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    item_cols = [c for c in df.columns if c != "id"]
    item_rename = {c: f"item_{int(c):02d}" for c in item_cols}
    df = df.rename(columns=item_rename)
    item_cols = list(item_rename.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_name = "lee_2025_nursing_exam"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
