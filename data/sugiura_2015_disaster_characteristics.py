#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0130349
# DOI: 10.1371/journal.pone.0130349
# S1 File (XLSX, sheet "data P") -- 40-item personal-characteristics scale
# ("power to live with disasters") administered to survivors of the 2011
# Great East Japan Earthquake. Response scale 0 ("not at all") - 5
# ("very much"). Covariates (age/sex) live in the "data D" sheet, keyed by
# the same ID.

import os
import io

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0130349.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return io.BytesIO(r.content)


def convert():
    buf = fetch()
    xls = pd.ExcelFile(buf)

    # Item data: sheet "data P", first row is header (item numbers 1-40)
    p = xls.parse("data P", header=0)
    p = p.rename(columns={p.columns[0]: "id"})
    p = p[pd.to_numeric(p["id"], errors="coerce").notna()].reset_index(drop=True)
    p["id"] = p["id"].astype(int)

    item_cols = [c for c in p.columns if c != "id"]
    item_map = {c: f"item_{int(c):02d}" for c in item_cols}
    p = p.rename(columns=item_map)
    item_names = list(item_map.values())

    # Covariates: sheet "data D" -> columns 1 (age category), 2 (sex)
    d = xls.parse("data D", header=0)
    d = d.rename(columns={d.columns[0]: "id", d.columns[1]: "cov_age_cat",
                           d.columns[2]: "cov_sex"})
    d = d[pd.to_numeric(d["id"], errors="coerce").notna()].reset_index(drop=True)
    d["id"] = d["id"].astype(int)

    merged = p.merge(d[["id", "cov_age_cat", "cov_sex"]], on="id", how="left")

    assert merged["id"].nunique() == len(merged), "id not unique"

    long = merged.melt(
        id_vars=["id", "cov_age_cat", "cov_sex"],
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "cov_age_cat", "cov_sex"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR_abs = os.path.abspath(OUT_DIR)
    os.makedirs(OUT_DIR_abs, exist_ok=True)
    out_path = os.path.join(OUT_DIR_abs, "sugiura_2015_disaster_characteristics.csv")
    long.to_csv(out_path, index=False)
    print(f"sugiura_2015_disaster_characteristics.csv: rows={len(long)} "
          f"ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
