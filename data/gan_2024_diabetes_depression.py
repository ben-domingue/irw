"""Gan et al. (2024), Frontiers in Endocrinology -- social support, depression
and alexithymia in type 2 diabetes.

Source: https://doi.org/10.3389/fendo.2024.1390564
DOI: 10.3389/fendo.2024.1390564
Data: Table 1 (frontiersin.figshare.com article 26786089)
License: CC BY 4.0

318 Chinese patients with type 2 diabetes mellitus, deposited for a structural
equation model of social support, depression, alexithymia and glycemic
control. Recovered 2026-08-25 from the candidate pool that had been
unintentionally blocklisted by `googlesheet_humaneye.csv`.

Tables written
--------------
gan_2024_depression       18 items, 0-4 (per-item maxima vary; see below)
gan_2024_alexithymia      19 items, 1-5

The social-support block is deliberately **not** exported -- see below.

How the blocks were identified
------------------------------
The file carries no variable labels, but the column prefixes are the construct
names in Chinese and line up with the paper: `社` (社会支持, social support),
`抑` (抑郁, depression), and the `@` block, whose derived companions in the same
file are `DIF`, `DDF` and `EOT` -- the three canonical subscales of the
Toronto Alexithymia Scale, matching the deposit's own `述情均分`
(alexithymia mean). The `@` block is 19 items on a 1-5 scale; `@1` is absent
from the file, so this is 19 of the TAS-20's 20 items.

Coding notes
------------
* **Only the numbered columns are items.** The file interleaves raw items with
  derived means whose names share the same prefixes (`社会均分`, `抑郁1均分`,
  `述情均分`, `DIF均分`, ...). Those carry fractional values; every numbered
  column is a pure integer in its documented range. The item blocks are
  matched on `^社\\d+$` / `^抑\\d+$` / `^@\\d+$` so no derived column can
  enter a table.
* **The derived means do not reconstruct** as a plain mean or sum of their
  whole block -- they are subscale means over subsets the file does not
  document. That costs nothing here, since each instrument ships as one table
  rather than being split by subscale, but it does mean the item-to-subscale
  mapping is not recoverable from the deposit.
* **The `社` social-support block is not shipped.** Its 32 columns are not one
  homogeneous instrument: 11 are 1-4 Likert items, 17 are 0/1 multi-select
  checkbox options belonging to two parent questions (`社6*`, `社7*`), and
  three of those (`社69`, `社79`, `社710`) are constant 0 -- options nobody
  selected. Mixing response formats in one table is the defect that got
  `reuter_2021_campuslife` pulled, and the checkbox options are alternatives
  within a question rather than independent items, so they are not items in
  their own right either. Splitting it correctly needs the instrument, which
  the deposit does not include.
* **The depression block's per-item maxima vary by design.** Four items run
  0-1, eight run 0-2, one 0-3 and five 0-4. That is the Hamilton Depression
  Rating Scale's own structure, corroborated by the deposit's derived factor
  columns -- `体重均分` (weight), `认知障碍均分` (cognitive impairment),
  `阻滞均分` (retardation), `睡眠障碍均分` (sleep disturbance),
  `躯体焦虑化均分` (somatic anxiety) are the HAMD factors -- and by `抑162`,
  the second part of its two-part item 16. Every item is ordinal within
  itself, which is what the standard requires; the precedent for mixed
  per-item category counts inside one instrument is `lee_2020_alcohol_use`.
* `序号` ("serial number") is not an identifier -- only 164 distinct values
  over 318 rows -- so `id` is the row position.
* Clinical and demographic columns (`性别` sex, `年龄段` age band, `病程`
  disease duration, `糖化` HbA1c, ...) are left in the source file rather than
  exported: they are patient clinical data rather than item responses, and
  none is needed to use the item tables.
"""

import io
import os
import re

import pandas as pd
import requests

FILES_API = "https://api.figshare.com/v2/articles/26786089/files"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

BLOCKS = [
    (re.compile(r"^抑\d+$"), "depression",  18, (0, 4)),
    (re.compile(r"^@\d+$"),  "alexithymia", 19, (1, 5)),
]


def _load() -> pd.DataFrame:
    files = requests.get(FILES_API, timeout=60, headers=UA).json()
    xl = [f for f in files if f["name"].lower().endswith((".xls", ".xlsx"))]
    assert len(xl) == 1, [f["name"] for f in files]
    raw = requests.get(xl[0]["download_url"], timeout=300, headers=UA)
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load()
    # 序号 repeats (164 distinct of 318), so it is a batch sequence, not an id.
    assert d["序号"].duplicated().any()
    d = d.reset_index(drop=True).copy()
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUTDIR, exist_ok=True)
    for pat, suffix, n_expected, (lo, hi) in BLOCKS:
        items = [c for c in d.columns if pat.match(str(c))]
        assert len(items) == n_expected, (suffix, len(items))
        # Guard the raw-vs-derived split explicitly: a derived mean would be
        # fractional, and none of these may be.
        for c in items:
            v = d[c].dropna()
            assert (v % 1 == 0).all(), f"{c} holds fractional values"

        long = d.melt(id_vars=["id"], value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"gan_2024_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
