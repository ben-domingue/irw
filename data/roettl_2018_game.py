#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0200724
# DOI: 10.1371/journal.pone.0200724
# SI: S1 Data ("Data set of the main study"), SAV
#
# "The same video game in 2D, 3D or virtual reality - How does
# technology impact game evaluation and brand placements?" N=234,
# between-subjects design (2D n=79 / stereoscopic 3D n=78 / VR-HMD
# n=77), condition mapped to cov_condition. The source `V1` id column
# is NOT unique (132 unique values across 234 rows -- ids were reused
# across condition blocks), so row index is used as `id` instead.
#
# Five separate raw-item scales are shipped from this one file
# (pre-computed composite/overall columns, e.g. F1_Attitude_game,
# F31_Scepticism_overall, are excluded):
#   - game attitude   (F1_1-6, 7-pt semantic differential)
#   - arousal         (F2_1-3, 7-pt)
#   - brand attitude  (F13/F16/F19/F22 x 1-6, 7-pt, one 6-item battery
#                        per in-game brand: Nachos/Chocolate/Smartphone/
#                        Energy Drink)
#   - brand recognition (F5-F12 coded columns, 0/1 forced-choice correct
#                        per brand category: Airline/Chocolate/Bank/
#                        Energy Drink/Coffee/Fitness Club/Nachos/
#                        Smartphone)
#   - scepticism      (F31_1-9, 7-pt)
# F25_Presence (single item) is excluded -- no single-item scales.

import os
import pandas as pd
import pyreadstat

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0200724_S1_Data.sav")
SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0200724.s004&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

GAME = [f"F1_{i}_Game_Attitude_{s}" for i, s in enumerate(
    ["appealing", "pleasant", "dynamic", "attractive", "enjoyable", "refreshing"], 1)]
AROUSAL = ["F2_1_Arousal_excited", "F2_2_Arousal_stimulated", "F2_3_Arousal_alert"]
SCEPT = [f"F31_{i}_Scepticism" for i in range(1, 10)]
BRAND_ATT = []
for brand, pref in [("Nachos", "F13"), ("Chocolate", "F16"), ("Smartphone", "F19"), ("Energy_Drink", "F22")]:
    for i in range(1, 7):
        BRAND_ATT.append(f"{pref}_{i}_{brand}_Attitude")
BRAND_REC = ["F5_coded_Airline", "F6_coded_Chocolate", "F7_coded_Bank",
             "F8_coded_Energy_Drink", "F9_coded_Coffee", "F10_coded_Fitness_Club",
             "F11_coded_Nachos", "F12_coded_Smartphone"]

SCALES = {
    "roettl_2018_game_attitude": (GAME, 1, 7),
    "roettl_2018_arousal": (AROUSAL, 1, 7),
    "roettl_2018_brand_attitude": (BRAND_ATT, 1, 7),
    "roettl_2018_brand_recognition": (BRAND_REC, 0, 1),
    "roettl_2018_scepticism": (SCEPT, 1, 7),
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

    cond_map = {1.0: "2D", 2.0: "3D", 3.0: "VR"}
    df["cov_condition"] = df["Condition"].map(cond_map)

    for out_name, (item_cols, lo, hi) in SCALES.items():
        long = df.melt(id_vars=["id", "cov_condition"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long = long[["id", "item", "resp", "cov_condition"]]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
