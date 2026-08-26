"""Peng (2024), Mendeley Data -- grit, emotions and English learning achievement in Chinese EFL students.

Source: https://data.mendeley.com/datasets/ddy7jc4mvb
DOI: 10.17632/ddy7jc4mvb
Data: Data_Grit, Emotions, and English learning Achievement.sav
License: CC BY 4.0

310 Chinese students of English as a foreign language completing three
instruments. Surfaced by the 2026-08-25 OpenAIRE/Mendeley pass.

How the blocks were identified
------------------------------
Two of the seven item-block prefixes (`CB`, `TB`) decode to nothing on their
own, and the file carries no variable labels. The deposit's own composite
scores settle it -- each is the exact sum of a specific set of blocks on every
complete case, which the script asserts before writing:

    Grit == sum(COI 4 + POE 4)                     8 items
    FLE  == sum(FLEP 5 + FLET 3 + FLEA 3)         11 items   (enjoyment)
    FLB  == sum(CB 8 + TB 5)                      13 items   (boredom)

So `COI`/`POE` are grit's consistency-of-interest and perseverance-of-effort
facets, `FLEP`/`FLET`/`FLEA` the three Foreign Language Enjoyment facets, and
`CB`/`TB` the two Foreign Language Boredom facets. Each instrument ships as
one table, since that is the level at which the deposit's own scores are
defined and the facet-to-item mapping is therefore verified.

Tables written
--------------
peng_2024_grit                          8 items, 1-5
peng_2024_language_enjoyment           11 items, 1-5
peng_2024_language_boredom             13 items, 1-5

Coding notes
------------
* `序号` is unique across all 310 rows and is used as `id`.
* All 32 item columns share a 1-5 response scale, with no constant items and
  no out-of-range or fractional values.
* The composite scores, their categorical bandings (`grit分类`, `FLB分类`,
  `FLE分类`, `grit新等级`, `flb新`, `fle新`) and the achievement outcome
  `Y成绩` are excluded -- the last is a test score, not an item response.
* Source column names are kept as `item` values so item text can join back.
"""

import io
import os
import re

import pandas as pd
import requests

API = "https://data.mendeley.com/public-api/datasets/ddy7jc4mvb"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

# table suffix -> (block prefixes, composite column that must equal their sum)
SCALES = {
    "grit":                (("COI", "POE"),            "Grit",  8),
    "language_enjoyment":  (("FLEP", "FLET", "FLEA"),  "FLE",  11),
    "language_boredom":    (("CB", "TB"),              "FLB",  13),
}

COVS = {"性别：": "cov_gender", "年龄": "cov_age"}


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
    assert d["序号"].is_unique
    d = d.rename(columns={"序号": "id"}).rename(columns=COVS)
    cov_cols = [c for c in COVS.values() if c in d.columns]

    os.makedirs(OUTDIR, exist_ok=True)
    for suffix, (prefixes, composite, n_expected) in SCALES.items():
        items = [c for p in prefixes for c in d.columns
                 if re.match(rf"^{p}\d+$", str(c))]
        assert len(items) == n_expected, (suffix, len(items))

        # Identification key: these blocks, summed, must be the deposit's own
        # composite. Without it the CB/TB prefixes would be a guess.
        s = d[items].sum(axis=1)
        ok = s.notna() & d[composite].notna()
        assert ok.sum() > 10 and (s[ok] - d[composite][ok]).abs().max() < 1e-6, (
            f"{composite} != sum({'+'.join(prefixes)})")

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["id"] = long["id"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(1, 5).all()
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"peng_2024_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
