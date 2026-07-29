#!/usr/bin/env python3
# Source: https://osf.io/37ycj/overview
# Paper: https://journals.sagepub.com/doi/10.1177/09567976261458325
# DOI (paper): 10.1177/09567976261458325
# Authors: Knight EL, Nave G, Shaw SD, Apicella C, Bonin PL, Dreber A, Geniole SN,
#          Johannesson M, Manfredi D, Mehta P, Proietti V, Stanton SJ, Luberti FR,
#          Ortiz T, Carre JM (2026). Psychological Science, 37(7), 463-476.
# License: CC0 (OSF data), confirmed on the OSF node page (osf.io/37ycj)
#
# 1,000-participant double-blind, placebo-controlled RCT of intranasal
# testosterone vs. placebo, testing effects on the 7-item Cognitive Reflection
# Test (CRT). Item-level long data pulled from TED_CRT_longdata.csv
# (Data and Code/code/data/ on the OSF node), cross-checked against
# "TED CRT Data Dictionary.docx" on the same node.
#   TP        -> treat (Testosterone=1, Placebo=0)
#   CRTn      -> item (CRT1..CRT7)
#   CRTc_dum  -> resp (Correct=1, Incorrect=0)
#   logRT     -> rt, back-transformed from natural log to seconds via exp()

import os
import io
import numpy as np
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

LONGDATA_URL = "https://osf.io/download/6952a2e6900cc63c0411d38f/"  # TED_CRT_longdata.csv


def convert():
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    r = requests.get(LONGDATA_URL, headers=headers, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), index_col=0)

    df = df.rename(columns={"Subject.Number": "id", "CRTn": "item"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    # resp: item-level correctness (Correct=1, Incorrect=0)
    df["resp"] = df["CRTc_dum"].map({"Correct": 1, "Incorrect": 0})

    # treat: experimental assignment (Testosterone=1, Placebo=0)
    df["treat"] = (df["TP"] == "Testosterone").astype(int)

    # rt: logRT is natural-log response time in seconds; back-transform
    df["rt"] = np.exp(df["logRT"])

    df = df.dropna(subset=["resp", "rt"]).reset_index(drop=True)
    df["resp"] = df["resp"].astype(int)

    out = df[["id", "item", "resp", "treat", "rt"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_name = "knight_2026_crt"
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    out.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(out)} ids={out['id'].nunique()} "
          f"items={out['item'].nunique()} resp={out['resp'].min():.0f}-{out['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
