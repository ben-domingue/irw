from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288563
# DOI: 10.1371/journal.pone.0288563
# Gillman et al. (2023), "The role of social support and social
# identification on challenge and threat cognitive appraisals, perceived
# stress, and life satisfaction in workplace employees". S1 File. CC BY
# 4.0. N=412. Two scales: cognitive-appraisal items (ALE, 16 items, 1-7,
# suffix codes T/C/L = threat/challenge/loss appraisal dimensions per the
# paper's framing) and Perceived Stress Scale (PS, 10 items, 0-4; `_R`
# suffix marks reverse-worded items in the source, shipped raw/
# unreversed). Both blocks had a scattered handful of unique-looking
# fractional values (e.g. 2.227143, 2.671287) on otherwise strictly
# integer items -- a mean/interpolation-imputation pattern for missing
# responses, not genuine raw data -- filtered to integers only.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0288563.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age": "cov_age", "Sex": "cov_sex"}
ALE_ITEMS = ["ALE_1_T","ALE_2_T","ALE_3_C","ALE_4_T","ALE_5_T","ALE_6_C","ALE_7_C","ALE_8_C",
             "ALE_9_L","ALE_10_L","ALE_11_L","ALE_12_C","ALE_13_C","ALE_14_T","ALE_15_T","ALE_16_L"]
PS_ITEMS = ["PS_1","PS_2","PS_3","PS_4_R","PS_5_R","PS_6","PS_7_R","PS_8_R","PS_9","PS_10"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "Part_No": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in [("gillman_2023_appraisals", ALE_ITEMS), ("gillman_2023_pss", PS_ITEMS)]:
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[long["resp"] % 1 == 0]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
