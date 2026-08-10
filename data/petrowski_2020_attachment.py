#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0230864
# DOI: 10.1371/journal.pone.0230864
#
# Petrowski, Brahler, Suslow, Zenger (2020). Revised short screening version
# of the attachment questionnaire for couples from the German general
# population. PLOS ONE.
#
# S1 Data (SAV) contains the raw 12-item ECR-based attachment questionnaire
# (qr101-qr112), each on a 1-7 scale ("Stimmt ueberhaupt nicht" [does not
# apply at all] to "Stimmt voll und ganz" [fully applies]). No person ID or
# covariate columns are present in the SI file itself. Per the paper's
# methods, missing item data were handled by listwise exclusion (no
# imputation mentioned).

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = "https://doi.org/10.1371/journal.pone.0230864.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"qr1{str(i).zfill(2)}" for i in range(1, 13)]


def load_raw():
    import io
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df


def clean_resp(series):
    # Values come as mixed numeric strings and text-labelled endpoints,
    # e.g. "7 = Stimmt voll und ganz" / "1 = Stimmt ueberhaupt nicht".
    s = series.astype(str).str.extract(r"(\d+)")[0]
    return pd.to_numeric(s, errors="coerce")


def convert():
    df = load_raw()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    for c in ITEM_COLS:
        df[c] = clean_resp(df[c])

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]

    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "petrowski_2020_attachment.csv")
    long.to_csv(out_path, index=False)
    print(f"petrowski_2020_attachment.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
