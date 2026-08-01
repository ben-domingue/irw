#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DEJQM4
# DOI: 10.7910/DVN/DEJQM4
# License: CC0 1.0
#
# Source file is a 190-item Google Forms export with two stacked header
# rows (English item text, then a Russian translation) before the numeric
# data starts. Only the embedded MEQ-30 mystical-experience subscale (the
# first 15 items of the full MEQ-30, labeled as such in the source) is
# extracted here -- the other ~175 columns are opaque federation-specific
# survey items (column headers are bare spreadsheet-style codes with no
# recoverable meaning) or free text, and are out of scope for this file.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://dataverse.harvard.edu/api/access/datafile/3892094"  # FFR_190items_surveyRus_raw_scored.tab
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (column position in the raw file, MEQ-30 original item number)
MEQ_COLS = [(82, 35), (83, 41), (84, 54), (85, 77), (86, 83), (87, 12),
            (88, 14), (89, 47), (90, 74), (91, 9), (92, 22), (93, 69),
            (94, 36), (95, 55), (96, 73)]


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    r = requests.get(URL, headers=HEADERS)
    r.raise_for_status()
    raw_path = os.path.join(OUT_DIR, "_tutrin_2020_raw.tab")
    with open(raw_path, "wb") as f:
        f.write(r.content)

    df = pd.read_csv(raw_path, sep="\t")
    os.remove(raw_path)

    # Row 0 is English item text, row 1 is a Russian translation; real
    # responses start at row 2.
    data = df.iloc[2:].reset_index(drop=True)

    rename = {data.columns[c]: f"MEQ_{num}" for c, num in MEQ_COLS}
    data = data.rename(columns=rename)
    item_cols = list(rename.values())

    data.insert(0, "id", data.index + 1)

    long = data.melt(id_vars=["id"], value_vars=item_cols,
                      var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # MEQ-30 is scored 0 (none) - 5 (extreme); anything outside that range
    # is a stray non-numeric/text artifact that survived to_numeric coercion
    # (shouldn't happen, but guard anyway).
    long = long[(long["resp"] >= 0) & (long["resp"] <= 5)].reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_name = "tutrin_2020_meq30"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
