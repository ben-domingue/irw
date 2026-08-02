from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209845
# DOI: 10.1371/journal.pone.0209845
# Lavallee et al. (2019), "Beliefs about the controllability of social
# characteristics and children's jealous responses to outsiders'
# interference in friendship". S1 File. CC BY 4.0. N=286 children.
# Six clean baseline scales shipped: self/other social-emotional-behavior
# beliefs (SSEB/OSEB, 3i each, 1-5), loneliness (LON, 3i, 1-5), jealousy
# (JEA, 10i -- non-sequential item numbers 2-27 preserved from source,
# 0-4), harmony/friendship-quality (HAR, 14i, 1-4), casual attribution
# scale (CAS, 24i, binary). NOT shipped: the file's scenario-condition
# blocks (VIG/INT/STB/GLO/INA/INB/UPS/MAD/B01-B11, each x4 experimental
# conditions) and the large tail of derived/reverse-coded/composite
# columns (HAR*R, *PRES, *AVE, etc.) -- needs the source paper to
# interpret the scenario design safely.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0209845.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"SEX": "cov_sex", "RACE": "cov_race", "GRADE": "cov_grade"}

SCALES = {
    "lavallee_2019_sseb": ["SSEB01", "SSEB02", "SSEB03"],
    "lavallee_2019_oseb": ["OSEB01", "OSEB02", "OSEB03"],
    "lavallee_2019_loneliness": ["LON01", "LON02", "LON03"],
    "lavallee_2019_jealousy": ["JEA02", "JEA04", "JEA08", "JEA10", "JEA12", "JEA14", "JEA20", "JEA22", "JEA26", "JEA27"],
    "lavallee_2019_harmony": [f"HAR{i:02d}" for i in range(1, 15)],
    "lavallee_2019_cas": [f"CAS{i:02d}" for i in range(1, 25)],
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "SUBNUM": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
