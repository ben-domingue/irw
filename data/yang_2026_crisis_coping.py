#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0350928
# DOI: 10.1371/journal.pone.0350928
# Yang, Lu & Wang (2026), "Promoting psychological crisis coping through
# physical activity: The mediating roles of rumination and emotion
# regulation among college students". S1 File. CC BY 4.0.
#
# One survey, four separate instruments -> four output files:
#   Rumination Response Scale / RRS (22 items, 1-4), Physical Activity
#   Rating Scale / PARS-3 (3 items, 1-5), College Students' Stress Response
#   Questionnaire / Duan coping scale (32 items, 1-5), Emotion Regulation
#   Questionnaire / ERQ (14 items, 1-7).
# Raw file has a 3-row merged header (subscale group / sub-code / item
# label) followed by data, plus 6 trailing blank/artifact rows at the end
# (stray leftover values from broken spreadsheet formulas, not real
# respondents -- dropped via id notna). RRS sub-codes (rumination1/2/3)
# were verified item-by-item against the paper's stated item lists
# (Symptomatic Rumination = items 1,2,3,4,6,8,9,14,17,18,19,22; Compulsive
# Meditation = 5,10,13,15,16; Reflective Pondering = 7,11,12,20,21) -- exact
# match, confirming the raw file's own sub-codes are reliable. The paper
# does not give per-item breakdowns for the 5-subscale coping questionnaire,
# so it ships as one 32-item block without a subscale label.

import io
import os
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0350928.s001")


def convert():
    headers = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
    r = requests.get(SI_URL, headers=headers, timeout=60)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), header=None)

    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = range(data.shape[1])

    data = data.rename(columns={0: "id", 1: "cov_sex", 2: "cov_age"})
    data["id"] = pd.to_numeric(data["id"], errors="coerce")
    data = data.dropna(subset=["id"]).reset_index(drop=True)

    scales = {
        "yang_2026_rrs": list(range(3, 25)),          # rumination, 22 items
        "yang_2026_pars3": list(range(25, 28)),        # PA, 3 items
        "yang_2026_stress_response": list(range(28, 60)),  # CC, 32 items
        "yang_2026_erq": list(range(60, 74)),          # ER, 14 items
    }

    id_vars = ["id", "cov_sex", "cov_age"]
    os.makedirs(OUT_DIR, exist_ok=True)

    for out_name, item_idx in scales.items():
        block = data[["id", "cov_sex", "cov_age"] + item_idx].copy()
        block.columns = id_vars + [f"item{i}" for i in range(1, len(item_idx) + 1)]
        long = block.melt(id_vars=id_vars, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + id_vars[1:]
        long = long[out_cols]

        out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.1f}-{long['resp'].max():.1f}")


if __name__ == "__main__":
    convert()
