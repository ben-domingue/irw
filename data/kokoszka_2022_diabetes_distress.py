from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263766
# DOI: 10.1371/journal.pone.0263766
# Kokoszka et al. (2022), "Body self-esteem is related to subjective
# well-being, severity of depressive symptoms, BMI, glycated hemoglobin
# levels, and diabetes-related distress in type 2 diabetes". S1 Data
# (semicolon-delimited). CC BY 4.0. N=100 type-2-diabetes patients. No
# usable id column in the file -- row index used. Five named validated
# instruments: Sense of Coherence (SOC, 35i), Hamilton Depression Rating
# Scale (ham, 17i), WHO-5 Well-Being Index (who, 5i), Problem Areas In
# Diabetes (paid, 20i). ZJN_1-4 (4i, unlabeled) also shipped. DSM_*
# columns (diagnostic checklist, mixed structure) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0263766.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"wiek": "cov_age", "grupa": "cov_group"}

SCALES = {
    "kokoszka_2022_soc": [f"SOC_{i}" for i in range(1, 36)],
    "kokoszka_2022_hamd": [f"ham{i}" for i in range(1, 16)] + ["ham16a", "ham16b", "ham17"],
    "kokoszka_2022_zjn": [f"ZJN_{i}" for i in range(1, 5)],
    "kokoszka_2022_who5": [f"who{i}" for i in range(1, 6)],
    "kokoszka_2022_paid": [f"paid{i}" for i in range(1, 21)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content), sep=";")
    df = df.rename(columns=COV_MAP)
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        if out_name == "kokoszka_2022_soc":
            long = long[long["resp"] != 99]  # sentinel/missing code
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
