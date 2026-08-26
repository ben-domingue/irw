"""Manolika (2021), Harvard Dataverse -- personality and media preferences.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/23NDKX
DOI: 10.7910/DVN/23NDKX
License: CC0 1.0
Paper: Manolika, M. (2022). The Big Five and beyond: which personality traits
do predict movie and reading preferences? Psychology of Popular Media.

386 respondents completing four instruments: liking ratings for 21 film
genres and 27 book genres, the 20-item Mini-IPIP, and the 12-item Dirty
Dozen.

Tables written
--------------
manolika_2021_movie_preferences     386 x 21 items, 1-5
manolika_2021_reading_preferences   386 x 27 items, 1-5
manolika_2021_mini_ipip             386 x 20 items, 1-5
manolika_2021_dirty_dozen           386 x 12 items, 1-5

Coding notes
------------
* Four tables, not one: the genre-liking ratings ("Dislike Strongly".."Like
  Strongly"), the Mini-IPIP and the Dirty Dozen are separate instruments, and
  the film and book genre lists are separate item sets that reuse names
  (`Romance`, `Horror`, `Thriller`, ...) and restart their numbering.
* **The `.sav` original is read rather than Dataverse's `.tab` conversion.**
  In the `.tab` the SPSS user-missing cells arrive as `0`, which looks like a
  sixth response category on a 1-5 scale; in the original they are missing,
  and there are no zeros anywhere. This is why `format=original` is requested.
* The SPSS variable labels are the full item stems for the Mini-IPIP and the
  Dirty Dozen ("Am the life of the party"), so item text joins directly on
  the source column names kept as item ids.
* The deposit carries no identifier column, so `id` is row position.
"""

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/23NDKX"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = {"Gender": "cov_gender", "Age": "cov_age"}
# (suffix, SPSS variable label that identifies the block, expected n items)
BLOCKS = [("movie_preferences",   "Genres of movies", 21),
          ("reading_preferences", "Genres of books",  27),
          ("mini_ipip",           None,               20),
          ("dirty_dozen",         None,               12)]
PREFIX = {"mini_ipip": "IPIP_", "dirty_dozen": "DD_"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"].endswith(".tab")]
    assert len(hit) == 1
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    open("/tmp/manolika.sav", "wb").write(raw.content)
    d, m = pyreadstat.read_sav("/tmp/manolika.sav")
    labels = m.column_names_to_labels

    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].map({0.0: "man", 1.0: "woman"})
    d["cov_age"] = d["Age"]

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for suffix, label, n_expected in BLOCKS:
        if label is not None:
            items = [c for c in d.columns if labels.get(c) == label]
        else:
            items = [c for c in d.columns
                     if str(c).startswith(PREFIX[suffix])]
        assert len(items) == n_expected, (suffix, len(items))
        assert not shipped & set(items)
        shipped.update(items)

        long = d.melt(id_vars=["id", "cov_gender", "cov_age"],
                      value_vars=items, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "cov_gender", "cov_age"]]

        assert long["resp"].between(1, 5).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"manolika_2021_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"density {len(long) / (n_id * n_it):.3f}")

    for c in d.columns:
        if c in shipped or c in COVS or c in ("id", "cov_gender", "cov_age"):
            continue
        raise AssertionError(f"unaccounted source column: {c}")
    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
