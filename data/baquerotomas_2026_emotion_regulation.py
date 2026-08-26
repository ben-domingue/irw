"""Baquero-Tomas (2026), Harvard Dataverse -- emotion-regulation difficulties,
anxiety and depression in Spanish university students.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MXYEMC
DOI: 10.7910/DVN/MXYEMC
License: CC0 1.0

566 Spanish university students completing seven instruments. Found by the
2026-08-26 triage of the educational-measurement term sweep.

Tables written
--------------
baquerotomas_2026_ders     28 items, 0-4  Difficulties in Emotion Regulation Scale
baquerotomas_2026_spsi     25 items, 0-4  Social Problem-Solving Inventory
baquerotomas_2026_pil      20 items, 1-7  Purpose in Life test
baquerotomas_2026_emas     12 items, 1-7  Endler Multidimensional Anxiety Scales
baquerotomas_2026_neoffi    9 items, 1-5  NEO Five-Factor Inventory items
baquerotomas_2026_phq9      9 items, 0-3  Patient Health Questionnaire-9
baquerotomas_2026_gad7      7 items, 0-3  Generalized Anxiety Disorder-7

Coding notes
------------
* Each instrument is its own table: the seven span four different response
  scales (0-4, 1-7, 1-5, 0-3), so one table per mailing would put
  incommensurable values in a single `resp` column.
* The source prefixes name the instruments directly (`DERS_`, `SPSI_`,
  `PIL_`, `EMAS_`, `NEOFFI_`, `PHQ9_`, `GAD7_`), and the item counts match
  the published short forms, so no inference was needed.
* **The deposit has no identifier column**, so `id` is the row position --
  one row is one student.
* Source item names are kept so item text can join back.
"""

import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/MXYEMC"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"

# source prefix -> table suffix, expected item count, (lo, hi)
SCALES = [
    ("DERS_",   "ders",   28, (0, 4)),
    ("SPSI_",   "spsi",   25, (0, 4)),
    ("PIL_",    "pil",    20, (1, 7)),
    ("EMAS_",   "emas",   12, (1, 7)),
    ("NEOFFI_", "neoffi",  9, (1, 5)),
    ("PHQ9_",   "phq9",    9, (0, 3)),
    ("GAD7_",   "gad7",    7, (0, 3)),
]


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    tab = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].endswith(".tab")]
    assert len(tab) == 1, [f["dataFile"]["filename"] for f in meta["files"]]
    raw = s.get(f"{BASE}/api/access/datafile/{tab[0]['id']}", timeout=600)
    raw.raise_for_status()
    d = pd.read_csv(io.BytesIO(raw.content), sep="\t", low_memory=False)

    d = d.reset_index(drop=True).copy()
    d["id"] = range(1, len(d) + 1)

    os.makedirs(OUTDIR, exist_ok=True)
    total = 0
    for prefix, suffix, n_expected, (lo, hi) in SCALES:
        items = [c for c in d.columns
                 if re.match(rf"^{re.escape(prefix)}\d+$", str(c))]
        assert len(items) == n_expected, (suffix, len(items))

        long = d.melt(id_vars=["id"], value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"baquerotomas_2026_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")
    print(f"\n{len(SCALES)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
