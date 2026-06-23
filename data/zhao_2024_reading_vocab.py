#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/reading_comprehension_and_vocabulary/26288533
# DOI: 10.6084/m9.figshare.26288533.v1
# License: CC BY 4.0
# Author: Aiping Zhao (2024)
# Dataset: reading comprehension and vocabulary
# 205 Chinese-as-foreign-language learners; 6 subtests covering receptive/productive
# vocabulary, reading comprehension, morphological awareness, lexical inferencing,
# and word consciousness. Each subtest is a separate scale (different items/scoring).

import os
import io
import requests
import pandas as pd

HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")

DATA_URL = "https://ndownloader.figshare.com/files/47654563"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)

    r = requests.get(DATA_URL, headers=HEADERS, allow_redirects=True)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    # Rename id and covariates
    df = df.rename(columns={"ID": "id"})
    cov_rename = {
        "gender": "cov_gender",
        "age": "cov_age",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = ["cov_gender", "cov_age"]

    # Item/subtest columns
    item_cols = [
        "Reading comprehension",
        "Lexical inferencing",
        "Morphological awareness",
        "Productive vocabulary",
        "Receptive Vocabulary",
        "Word consciousness",
    ]

    # Rename to IRW-style item names
    item_rename = {
        "Reading comprehension": "reading_comprehension",
        "Lexical inferencing": "lexical_inferencing",
        "Morphological awareness": "morphological_awareness",
        "Productive vocabulary": "productive_vocabulary",
        "Receptive Vocabulary": "receptive_vocabulary",
        "Word consciousness": "word_consciousness",
    }
    df = df.rename(columns=item_rename)
    clean_item_cols = list(item_rename.values())

    long = df[["id"] + cov_cols + clean_item_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=clean_item_cols,
        var_name="item",
        value_name="resp",
    )

    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Enforce column order
    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "zhao_2024_reading_vocab"
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(
        f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


if __name__ == "__main__":
    convert()
