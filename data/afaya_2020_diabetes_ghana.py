from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0237710
# DOI: 10.1371/journal.pone.0237710
# Afaya et al. (2020), "Medication adherence and self-care behaviours
# among patients with type 2 diabetes mellitus in Ghana". S1 Data. CC BY
# 4.0. N=326. Seven diabetes-knowledge subscales (1-3 scale, likely
# correct/incorrect/don't-know), each shipped separately: general (gk,
# 11i), diet (kd, 13i), monitoring (km, 7i), exercise (ke, 4i),
# medication (kom, 10i), foot care (kf, 14i), complications (kc, 7i).
# The file's many single-purpose behavior items after these blocks (not
# part of a numbered item set) are not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0237710.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"sex": "cov_sex", "age": "cov_age", "education": "cov_education"}

SCALES = {
    "afaya_2020_general_knowledge": [f"gk{i}_{s}" for i, s in enumerate(
        ["sweets","insulin","obesity","exer","sugar","child","cure","urine","cuts","shake","thirst"], 1)],
    "afaya_2020_diet_knowledge": [f"kd{i}_{s}" for i, s in enumerate(
        ["juice","diet","free","lowfat","salt","protein","fibre","prepare","beverage","medicine","meals","food","dietician"], 1)],
    "afaya_2020_monitoring_knowledge": [f"km{i}_{s}" for i, s in enumerate(
        ["glucose","test","ideal","morning","exercise","signs","deal"], 1)],
    "afaya_2020_exercise_knowledge": [f"ke{i}_{s}" for i, s in enumerate(
        ["exercise","maintenace","need","medicine"], 1)],
    "afaya_2020_medication_knowledge": [f"kom{i}_{s}" for i, s in enumerate(
        ["name","effect","drugs","cure","complicate","double","site","change","time","medicine"], 1)],
    "afaya_2020_footcare_knowledge": [f"kf{i}_{s}" for i, s in enumerate(
        ["feet","inspect","protect","care","cleanse","bath","barefoot","outside","warmness","drytoes","advice","cream","socks","followup"], 1)],
    "afaya_2020_complications_knowledge": [f"kc{i}_{s}" for i, s in enumerate(
        ["kidney","feeling","vision","heartdx","ulcer","hyposexual","circulation"], 1)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns=COV_MAP)
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        item_cols = [c for c in item_cols if c in df.columns]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
