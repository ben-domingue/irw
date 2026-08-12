#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0347933
# DOI: 10.1371/journal.pone.0347933

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SI_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0347933.s001"

ITEM_COLS = {
    "10. Please rate the performance of the large language model in the following aspects (1-5 points, 1 is the lowest and 5 is the highest): Expertise accuracy": "expertise_accuracy",
    "10. Please rate the performance of the large language model in the following aspects (1-5 points, 1 is the lowest and 5 is the highest): Problem solving efficiency": "problem_solving_efficiency",
    "10. Please rate the performance of the large language model in the following aspects (1-5 points, 1 is the lowest and 5 is the highest): Practicality of the answer": "practicality_of_answer",
    "10. Please rate the performance of the large language model in the following aspects (1-5 points, 1 is the lowest and 5 is the highest): Inspiration for innovative thinking": "innovative_thinking",
    "10. Please rate the performance of the large language model in the following aspects (1-5 points, 1 is the lowest and 5 is the highest): Ease of use": "ease_of_use",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/zhu_2026.csv"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df = pd.read_csv(tmp)

    df["id"] = df["serial number"]
    df = df.rename(columns=ITEM_COLS)
    item_cols = list(ITEM_COLS.values())

    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    long = long[["id", "item", "resp"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "zhu_2026_llm_meteorology_performance.csv")
    long.to_csv(out_path, index=False)
    print(f"zhu_2026_llm_meteorology_performance: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
