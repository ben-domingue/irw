#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12103844
# DOI: 10.7717/peerj.19428
#
# "Human-elephant conflicts and attitude of the local communities toward
# African elephant (Loxodonta africana) conservation in Kafta Sheraro
# National Park, Tigray region, Ethiopia". Europe PMC supplementary file
# s001 (CSV) embeds several tables from the paper; this script extracts the
# two 7-item, 5-point Likert attitude batteries (Table 2: attitude toward
# park conservation; Table 3: attitude toward African elephant conservation),
# each surveyed on the same N=395 households (1=strongly agree ... 5=strongly
# disagree). The file's own footnote states "0=missing value" for these
# tables, so 0s are filtered as sentinel/non-response, not a real scale
# point. Only anonymous sequential household numbers are used as `id` --
# no names/GPS/other PII in this file. CC BY 4.0 (PeerJ).

import io
import os
import zipfile

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12103844/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

TABLES = {
    "temesgen_2025_elephant_park_attitude": (408, 802),
    "temesgen_2025_elephant_conserv_attitude": (808, 1202),
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    csv_name = [n for n in zf.namelist() if n.endswith("s001.csv")][0]
    raw = pd.read_csv(io.BytesIO(zf.read(csv_name)), encoding="latin1",
                       header=None)

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (start, end) in TABLES.items():
        block = raw.iloc[start:end + 1, 1:9]
        block.columns = ["id", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
        block = block.copy()
        block["id"] = pd.to_numeric(block["id"], errors="coerce")
        block = block.dropna(subset=["id"]).reset_index(drop=True)
        block["id"] = block["id"].astype(int)
        assert block["id"].nunique() == len(block), "id column is not unique per row"

        item_cols = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
        long = block.melt(id_vars=["id"], value_vars=item_cols,
                           var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # 0 = missing value per the source table's own footnote; scale is 1-5
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

        long = long[["id", "item", "resp"]]
        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
