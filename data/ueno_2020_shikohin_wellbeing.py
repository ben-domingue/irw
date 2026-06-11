#!/usr/bin/env python3
# Source: https://osf.io/sydzb/
# Preprint DOI: 10.31234/osf.io/dwyvs
# Effects of Shikohin (coffee/tea/alcohol/tobacco) consumption contexts on
# resilience and psychological wellbeing in Japanese adults. N=2820.
# Scales identified from Legend sheet in the OSF xlsx:
#   q1 = SPEQ (Shikohin Products Experience Questionnaire, 32i, 1-7)
#   q2 = SRBQ (Shikohin-Related Behavior Questionnaire, 10i, 1-7)
#   q3 = Resilience: understanding of personal resources (20i, 1-5)
#   q4 = Resilience: utilization of personal resources (29i, 1-5)
#   q5 = Resilience: understanding of environmental resources (20i, 1-5)
#   q6 = Resilience: utilization of environmental resources (30i, 1-5; q6_25,q6_29 inverted)
#   q7 = Brief PWBS psychological wellbeing scale (16i, 1-6; q7_1-4 inverted)

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output", "cleaned")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"no": "id", "group": "cov_group"}


def convert():
    r = requests.get("https://api.osf.io/v2/nodes/sydzb/files/osfstorage/",
                     headers=UA, timeout=30)
    for f in r.json().get("data", []):
        if f["attributes"]["name"].endswith(".xlsx"):
            r2 = requests.get(f["links"]["download"], headers=UA, timeout=60)
            df = pd.read_excel(io.BytesIO(r2.content))
            break

    df = df.rename(columns={k: v for k, v in COV_MAP.items() if k in df.columns})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)

    cov_cols = [v for v in COV_MAP.values() if v != "id" and v in df.columns]

    SCALE_NAMES = {
        1: "ueno_2020_speq",
        2: "ueno_2020_srbq",
        3: "ueno_2020_resilience_personal_understanding",
        4: "ueno_2020_resilience_personal_utilization",
        5: "ueno_2020_resilience_environmental_understanding",
        6: "ueno_2020_resilience_environmental_utilization",
        7: "ueno_2020_pwbs",
    }

    for q in range(1, 8):
        prefix = f"q{q}_"
        item_cols = [c for c in df.columns if str(c).startswith(prefix)]
        if not item_cols:
            continue
        out_name = SCALE_NAMES[q]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
