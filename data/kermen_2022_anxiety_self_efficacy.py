"""Kermen & Yuksel (2022), Mendeley Data -- anxiety, self-efficacy and
self-regulation in Turkish high school students.

Source: https://data.mendeley.com/datasets/3gx5f24fpv
DOI: 10.17632/3gx5f24fpv
Data: data.sav
License: CC BY 4.0

325 Turkish high school students completing four instruments. Surfaced by the
2026-08-25 OpenAIRE/Mendeley pass.

How the blocks were identified
------------------------------
The source names the item columns with bare letters (`b1`..`b17`, `c1`..`c16`,
`d1`..`d20`, `e1`..`e20`) and carries no variable labels, so the prefixes
decode to nothing on their own. The deposit does, however, also carry four
scored variables -- `effi`, `regu`, `att`, `anx` -- and each one reconstructs
*exactly* as the plain sum of one block on every complete case:

    effi == sum(b1..b17)     self-efficacy      17 items, 1-5
    regu == sum(c1..c16)     self-regulation    16 items, 1-5
    anx  == sum(d1..d20)     anxiety            20 items, 0-3
    att  == sum(e1..e20)     attention          20 items, 1-4

That is a positive identification rather than a guess about the prefixes, and
the script asserts each of the four sums before writing anything.

Tables written
--------------
kermen_2022_self_efficacy      17 items, 1-5
kermen_2022_self_regulation    16 items, 1-5
kermen_2022_anxiety            20 items, 0-3
kermen_2022_attention          20 items, 1-4

Coding notes
------------
* `sira` ("row") is the source's sequence number; it is used as `id` only
  after asserting it is unique.
* The four scored variables are excluded from the item tables, having served
  their purpose as the identification key.
* Source column names are kept as `item` values so item text can join back.
"""

import io
import os
import re

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/3gx5f24fpv"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

# prefix -> (table suffix, scored variable that must equal the block sum, range)
BLOCKS = [
    ("b", "self_efficacy",   "effi", (1, 5)),
    ("c", "self_regulation", "regu", (1, 5)),
    ("d", "anxiety",         "anx",  (0, 3)),
    ("e", "attention",       "att",  (1, 4)),
]

COVS = {"cinsiyet": "cov_gender", "sinif": "cov_grade", "yas": "cov_age"}


def _load() -> pd.DataFrame:
    meta = requests.get(API, timeout=60, headers=UA).json()
    sav = [f for f in meta["files"] if f["filename"].endswith(".sav")]
    assert len(sav) == 1, [f["filename"] for f in meta["files"]]
    raw = requests.get(sav[0]["content_details"]["download_url"], timeout=300,
                       headers=UA)
    raw.raise_for_status()
    return pd.read_spss(io.BytesIO(raw.content), convert_categoricals=False)


def main():
    d = _load()
    assert d["sira"].is_unique, "sira is not unique"
    d = d.rename(columns={"sira": "id"}).rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    os.makedirs(OUTDIR, exist_ok=True)
    for prefix, suffix, scored, (lo, hi) in BLOCKS:
        pat = re.compile(rf"^{prefix}\d+$")
        items = sorted((c for c in d.columns if pat.match(str(c))),
                       key=lambda c: int(str(c)[len(prefix):]))
        assert items, prefix

        # The identification key: this block, summed, must be the scored
        # variable. If it ever stops holding, the mapping is wrong and the
        # script must not write a mislabelled table.
        s = d[items].sum(axis=1)
        ok = s.notna() & d[scored].notna()
        assert ok.sum() > 10 and (s[ok] - d[scored][ok]).abs().max() < 1e-6, (
            f"{scored} != sum({prefix}1..{prefix}{len(items)})")

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["id"] = long["id"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"kermen_2022_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
