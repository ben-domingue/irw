from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0182845
# DOI: 10.1371/journal.pone.0182845
# Schmidt, Egger, Benzing, Jaeger, Conzelmann, Roebers et al. (2017),
# "Disentangling the relationship between children's motor ability,
# executive function and academic achievement". S1 Dataset (.s001, SAV).
# CC BY 4.0. German version of the Pubertal Development Scale (PDS,
# 3 items, "pub_1_1"/"pub_2_1"/"pub_3_1"), each scored 1-4. No person ID
# column in the source file -- row index used as id per datastandard.md's
# "missing person ID" rule. One isolated fractional value (pub_2_1=2.5,
# 1/232 non-null cells) dropped as a data entry error. See also
# schmidt_2017_fas.py for the second small raw-item scale in this file
# (Family Affluence Scale II).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0182845.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["pub_1_1", "pub_2_1", "pub_3_1"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content), convert_categoricals=False)
    df = df.rename(columns={"sex": "cov_sex"})
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    cov_names = ["cov_sex"]
    long = df.melt(id_vars=["id"] + cov_names, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 4)]
    long = long[long["resp"] == long["resp"].round()]  # drop isolated fractional (e.g. 2.5)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "schmidt_2017_pds.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
