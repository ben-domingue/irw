#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295904
# S1 File: https://doi.org/10.1371/journal.pone.0295904.s001
# DOI: 10.1371/journal.pone.0295904
#
# Naja et al. (2024) "Intention to quit and its correlates among dieticians
# residing in the United Arab Emirates during the COVID-19 pandemic".
# The SI file's other columns are single derived/grouped covariates (e.g.
# R_Age_categorized, Resilient_GRP_2) rather than raw item-level responses —
# the 25-item CD-RISC resilience scale is only present as a binary derived
# group, not raw items, so it is not shippable. The one genuine multi-item
# battery in the file is the "which of the below do you perceive as a
# challenge during COVID-19?" multi-select checklist (respondents could pick
# more than one): work-life balance, seeing enough patients, face-to-face
# counseling, job security, job satisfaction. Each option is coded 0/1
# (not selected / selected) -> treated as 5 binary items.

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0295904.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = {
    "R_Work_life_balance_challenge": "work_life_balance",
    "R_Seeing_enough_patients_challenge": "seeing_enough_patients",
    "R_Face_to_face_counseling_challenge": "face_to_face_counseling",
    "R_Job_security_challenge": "job_security",
    "R_Job_satisfaction_challenge": "job_satisfaction",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df)

    df = df.rename(columns=ITEM_COLS)
    item_cols = list(ITEM_COLS.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    long = long[["id", "item", "resp"]]

    out_name = "naja_2024_challenges"
    out_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
