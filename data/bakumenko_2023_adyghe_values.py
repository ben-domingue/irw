#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NIRWKZ
# DOI: 10.7910/DVN/NIRWKZ
# Attitudes of Adyghe people to traditional ethnic cultural values. Russian. N≈151.
# Items are Likert-style importance ratings (1-5). First 5 cols are covariates.
# item column uses generic IDs; item_text (Russian) and item_text_translated (English) added.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/",
                     params={"persistentId": "doi:10.7910/DVN/NIRWKZ"},
                     headers=UA, timeout=20)
    files = r.json().get("data", {}).get("latestVersion", {}).get("files", [])
    for f in files:
        dm = f.get("dataFile", {})
        if dm.get("filename", "").endswith(".xlsx"):
            fid = dm.get("id")
            r2 = requests.get(f"https://dataverse.harvard.edu/api/access/datafile/{fid}",
                              headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    all_cols = df.columns.tolist()
    # Cols 1-5: timestamp + 4 demographics
    cov_cols = all_cols[2:6]   # region, age_group, sex, education (skip timestamp)
    cov_rename = {c: f"cov_{i}" for i, c in enumerate(cov_cols, 1)}
    df = df.rename(columns=cov_rename)
    cov_out = list(cov_rename.values())

    # Only the 7 numeric importance-rating items ("Оцените важность…", original cols 6-12)
    # all_cols[7:14] after id inserted at position 0
    item_cols = all_cols[7:14]

    ITEM_TEXT = {
        "item_1": ("Оцените важность традиционной этики, морали и этикета (Адыгэ Хабзэ или Шариат)",
                   "Rate the importance of traditional ethics, morality and etiquette (Adyghe Khabze or Sharia)"),
        "item_2": ("Оцените важность знания родного языка",
                   "Rate the importance of knowing the native language"),
        "item_3": ("Оцените важность знания Нартского эпоса и народных песен",
                   "Rate the importance of knowing the Nart epics and folk songs"),
        "item_4": ("Оцените важность традиционных обрядов и национальных танцев",
                   "Rate the importance of traditional rituals and national dances"),
        "item_5": ("Оцените важность национального костюма",
                   "Rate the importance of national dress"),
        "item_6": ("Оцените важность национальной кухни",
                   "Rate the importance of national cuisine"),
        "item_7": ("Оцените важность национальных видов спорта",
                   "Rate the importance of national sports"),
    }
    item_id_map = {orig: f"item_{i}" for i, orig in enumerate(item_cols, 1)}

    long = df.melt(id_vars=["id"] + cov_out, value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["item"] = long["item"].map(item_id_map)
    long["item_text"] = long["item"].map(lambda x: ITEM_TEXT[x][0])
    long["item_text_translated"] = long["item"].map(lambda x: ITEM_TEXT[x][1])
    long = long[["id", "item", "resp", "item_text", "item_text_translated"] + cov_out]

    path = os.path.join(OUT_DIR, "bakumenko_2023_adyghe_values.csv")
    long.to_csv(path, index=False)
    print(f"bakumenko_2023_adyghe_values: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
