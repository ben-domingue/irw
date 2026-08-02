from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249397
# DOI: 10.1371/journal.pone.0249397
# Kowal et al. (2021), "Experiencing one's own body and body image in
# living kidney donors - A sociological and psychological study". S1
# Questionnaire. CC BY 4.0. N=31 living kidney donors (small sample).
# 35-item body-image questionnaire, mostly 1-5. Three items (13, 14, 33)
# contain a 9999 sentinel value (missing/not-applicable code, standing out
# far beyond the 1-5 range) -- treated as missing and dropped, per
# datastandard.md's sentinel-code handling.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0249397.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=1)


def convert():
    df = fetch()
    df = df.rename(columns={df.columns[0]: "id"})
    item_cols = [c for c in df.columns if str(c).lower().startswith("question")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[long["resp"] != 9999]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "kowal_2021_kidney_donor_body_image.csv"
    long.to_csv(out_path, index=False)
    print(f"kowal_2021_kidney_donor_body_image: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
