#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263220
# DOI: 10.1371/journal.pone.0263220
# SI: S4 File ("The study dataset"), XLSX (sheet "absenteeism dataset";
#     sheet "codebook" maps each column code to its question text)
#
# "Integrating quantitative and qualitative approaches to assess
# wintertime illness-related absenteeism and its direct and indirect
# costs among the private sector in Ulaanbaatar." Single cross-sectional
# survey of N=1329 workers (S1-S3 files are the questionnaire/interview
# instruments themselves, not data). Three separate binary (0/1)
# checklist scales are shipped, each asked of essentially the full
# sample (no skip-logic sentinel contamination):
#   - symptoms experienced during high air-pollution periods (Q1.1-Q1.8)
#   - diseases believed to be caused by air pollution (Q2.1-Q2.5)
#   - type of leave used when absent (Q7.1-Q7.5)
# The K3.1-K3.8 "reasons for absence" block is NOT shipped: it is
# answered only by the subset who reported being absent (Q3), so ~66-68%
# of its cells are the 8888 not-applicable/skip code rather than a
# clean universally-asked item -- flagged as too skip-logic-heavy to
# ship cleanly alongside the other two blocks here.
# Paper text: "Missing data comprised less than 5% for each variable,
# and list wise deletion was applied ... during the analyses" -- no
# imputation. One duplicate `ID` row (1330 rows / 1329 unique ids) is
# dropped as a data-entry duplicate.

import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0263220_S4_File.xlsx")
SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0263220.s004&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

SCALES = {
    "ganbat_2022_pollution_symptoms": [f"Q1.{i}" for i in range(1, 9)],
    "ganbat_2022_pollution_disease_risk": [f"Q2.{i}" for i in range(1, 6)],
    "ganbat_2022_pollution_leave_type": [f"Q7.{i}" for i in range(1, 6)],
}


def convert():
    if not os.path.exists(RAW):
        import requests
        r = requests.get(SI_URL, headers=UA, timeout=60)
        r.raise_for_status()
        with open(RAW, "wb") as f:
            f.write(r.content)

    df = pd.read_excel(RAW, sheet_name="absenteeism dataset")
    df = df.rename(columns={"ID": "id"})
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        # drop the 8888 not-applicable/skip sentinel where it appears
        long = long[long["resp"].isin([0, 1])].reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
