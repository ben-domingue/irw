#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260559
# DOI: 10.1371/journal.pone.0260559
# SI: S1 Data ("Dataset file"), SAV
#
# "Public service motivation and organizational performance:
# Catalyzing effects of altruism, perceived social impact and
# political support." N=405 public officials, all items on a 5-point
# Likert scale. No person-id column exists in the source (first column
# is `Gender`) -- row index is used as `id`. Five separate raw-item
# scales are shipped:
#   - Public Service Motivation (PSM1-5)
#   - Political Support (PS1-3)
#   - Altruism (ALT1-4)
#   - Perceived Social Impact (PSI1-4)
#   - Organizational Performance (OP1-8)
# Although the paper reports dropping PSM1 for low factor loading
# during measurement-model validation, the raw item is kept here (raw
# item data, not the analysis-model-selected subset).

import os
import pandas as pd
import pyreadstat

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0260559_S1_Data.sav")
SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0260559.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

SCALES = {
    "zubair_2021_psm": [f"PSM{i}" for i in range(1, 6)],
    "zubair_2021_political_support": [f"PS{i}" for i in range(1, 4)],
    "zubair_2021_altruism": [f"ALT{i}" for i in range(1, 5)],
    "zubair_2021_social_impact": [f"PSI{i}" for i in range(1, 5)],
    "zubair_2021_org_performance": [f"OP{i}" for i in range(1, 9)],
}


def convert():
    if not os.path.exists(RAW):
        import requests
        r = requests.get(SI_URL, headers=UA, timeout=60)
        r.raise_for_status()
        with open(RAW, "wb") as f:
            f.write(r.content)

    df, meta = pyreadstat.read_sav(RAW)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
        long = long[["id", "item", "resp"]]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
