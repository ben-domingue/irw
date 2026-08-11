#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0255689
# S1_Database: https://doi.org/10.1371/journal.pone.0255689.s001
# DOI: 10.1371/journal.pone.0255689
#
# Orovou, Theodoropoulou, Antoniou (2021) "Psychometric properties of the
# Post Traumatic Stress Disorder Checklist for DSM-5 in a sample of Greek
# women after cesarean section". N=469 postpartum women. Two instruments in
# the SAV file:
#   PCL1-20: PCL-5, 20 items, 5-point scale (0=Not at all ... 4=Extremely)
#            confirmed via SPSS value labels.
#   LEC1-17: Life Events Checklist-5 (LEC-5), 17 items, binary
#            (0=No, 1="It happened to me/I was a witness") — a trauma
#            exposure checklist, confirmed via SPSS value labels.
# Written as two separate scale files per datastandard.md.

import os
import tempfile
import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0255689.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df, meta = pyreadstat.read_sav(tmp.name)
    df = df.rename(columns={"ID1": "id"})
    assert df["id"].nunique() == len(df)

    cov_cols = ["cov_csection_type"]
    df = df.rename(columns={"TypeOfCsection": "cov_csection_type"})

    scales = {
        "orovou_2021_pcl5": [f"PCL{i}" for i in range(1, 21)],
        "orovou_2021_lec5": [f"LEC{i}" for i in range(1, 18)],
    }

    for out_name, item_cols in scales.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, out_name + ".csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
