from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264089
# DOI: 10.1371/journal.pone.0264089
# Fadhliah et al. (2022), "Comparison of disaster information from
# various media in strengthening ecological communication during & after
# natural disasters". S1 Data. CC BY 4.0. N=75.
# Ratings of 8 named information channels (TV/Internet/WA-SMS/Radio/
# Mosque-Church/Surau/Community leader/Word to Mouth), item = channel
# name, likely a trust-or-usefulness rating (exact question wording not
# in the file). S2 Data (a separate table with no real column headers,
# just index numbers) is not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0264089.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["TV", "Internet", "WA/SMS", "Radio", "Mosque/Church", "Surau",
             "Community leader", "Word to Mouth"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), header=2)
    return df


def convert():
    df = fetch()
    df = df.rename(columns={df.columns[1]: "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "fadhliah_2022_disaster_media_trust.csv"
    long.to_csv(out_path, index=False)
    print(f"fadhliah_2022_disaster_media_trust: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
