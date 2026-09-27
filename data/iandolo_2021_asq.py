#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/EXPLORATION_OF_THE_SPANISH_VERSION_OF_THE_ATTACHMENT_STYLE_QUESTIONNAIRE_A_COMPARATIVE_STUDY_BETWEEN_SPANISH_ITALIAN_AND_JAPANESE_CULTURE/13601096
# DOI: 10.6084/m9.figshare.13601096.v1
# License: CC BY 4.0

import os
import re

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://ndownloader.figshare.com/files/26078555"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUT_DIR, "_iandolo_2021_raw.xlsx")
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_excel(raw_path, sheet_name="Data set")
    os.remove(raw_path)

    df = df.rename(columns={
        "ID_ATTACH": "id",
        "grupo": "cov_country",
        "Edad": "cov_age",
        "Género": "cov_gender",
        "Relacion romantica": "cov_romantic_relationship",
    })
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    cov_cols = ["cov_country", "cov_age", "cov_gender", "cov_romantic_relationship"]

    item_cols = [c for c in df.columns
                 if re.match(r"^ASQ-\d+", c)]
    assert len(item_cols) == 40, f"expected 40 ASQ items, found {len(item_cols)}"

    item_rename = {c: "ASQ_" + re.match(r"^ASQ-(\d+)", c).group(1) for c in item_cols}
    df = df.rename(columns=item_rename)
    item_cols = list(item_rename.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Scale is a 1-6 Likert; a handful of isolated 7s (3 occurrences across
    # 3 different items, out of ~13900 valid responses) are data-entry errors.
    long = long[long["resp"] <= 6].reset_index(drop=True)

    # #2099: the reverse-keyed items ASQ_20/21/33 (headers "ASQ-20-R- DC",
    # "ASQ-21-R DC", "ASQ-33-R C") are stored raw for Spain (cov_country 1) but
    # already reverse-scored for Italy (2) and Japan (3): their correlation with
    # the non-reversed items of their own subscale is negative in Spain and
    # positive in Italy/Japan. Un-reverse Italy/Japan (7 - x on the 1-6 scale)
    # so all three subsamples are raw.
    flip = long["item"].isin(["ASQ_20", "ASQ_21", "ASQ_33"]) & long["cov_country"].isin([2, 3])
    long.loc[flip, "resp"] = 7 - long.loc[flip, "resp"]

    long["resp"] = long["resp"].astype(int)
    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_name = "iandolo_2021_asq"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
