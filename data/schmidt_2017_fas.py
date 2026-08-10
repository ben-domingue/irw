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
# CC BY 4.0. Family Affluence Scale II (FAS II, 4 items: "ses_1_1".."ses_4_1"
# -- family car ownership, own bedroom, family holidays, computers).
# Response format genuinely varies by item (documented in the paper's
# Methods, e.g. car ownership 0-2, holidays 0-3) -- not a data error. No
# person ID column in the source file -- row index used as id, same as
# schmidt_2017_pds.py (the other small raw-item scale in this file). One
# isolated fractional value (ses_3_1=1.5, 1/228 non-null cells) dropped as
# a data entry error.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0182845.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["ses_1_1", "ses_2_1", "ses_3_1", "ses_4_1"]


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
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]
    long = long[long["resp"] == long["resp"].round()]  # drop isolated fractional (e.g. 1.5)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "schmidt_2017_fas.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
