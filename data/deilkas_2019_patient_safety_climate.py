from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214914
# DOI: 10.1371/journal.pone.0214914
# Deilkas et al. (2019), "Variation in staff perceptions of patient
# safety climate across work sites in Norwegian general practitioner
# practices and out-of-hour clinics". S1 File. CC BY 4.0. N=112.
# 62-item safety-climate scale (Q4-Q65), text-coded 5-point agreement
# scale ("Disagree strongly".."Agree strongly") recoded 1-5; "Not
# relevant" responses and stray 0.0 sentinel values treated as missing.
# The file's other columns (Q2/Q3/Q3a-g: a different "Very good"-"Very
# bad" quality-rating scale; Q66-Q74: demographics) are not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0214914.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {
    "disagree strongly": 1, "disagree slightly": 2, "neutral": 3,
    "agree slightly": 4, "agree strongly": 5,
}
ITEM_COLS = [f"Q{i}" for i in range(4, 66)]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(str).str.lower().map(LIKERT_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "deilkas_2019_patient_safety_climate.csv"
    long.to_csv(out_path, index=False)
    print(f"deilkas_2019_patient_safety_climate: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
