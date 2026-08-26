"""Choi et al. (2026), Harvard Dataverse -- Clinical Medical Science
Comprehensive Examination (CMSCE), Korea.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/TQZQ6L
DOI: 10.7910/DVN/TQZQ6L
License: CC0 1.0

Item-level scored responses from six administrations of Korea's Clinical
Medical Science Comprehensive Examination, deposited for a study of whether
the exam could move to computerized adaptive testing. 30,383 examinee
sittings across 1,739 distinct items, all scored right/wrong.

Found by the 2026-08-26 triage of the educational-measurement term sweep --
`computerized adaptive testing` was one of the terms added on 2026-08-25 after
the audit found the standing term list had no ability or achievement coverage
at all.

Tables written
--------------
One per administration, `choi_2026_cmsce_<year>_<part>`:

    choi_2026_cmsce_2019_1   4,190 examinees x 302 items
    choi_2026_cmsce_2019_2   5,586 x 301
    choi_2026_cmsce_2020_1   5,388 x 304
    choi_2026_cmsce_2020_2   3,972 x 304
    choi_2026_cmsce_2021_1   4,662 x 263
    choi_2026_cmsce_2021_2   6,585 x 265

**Six tables, not one.** The forms share *no items whatsoever* -- checked
pairwise across all fifteen pairs, the intersection is empty every time, and
the 1,739 distinct items are exactly the sum of the six item counts. Stacking
them would produce a block-diagonal matrix that is 83% missing by
construction and would imply a linking design the deposit does not support.

Coding notes
------------
* Every value is 0 or 1 -- the exam is scored dichotomously and the deposit
  ships the scored responses, not the raw option choices.
* **The files carry no identifier column**: all 302-ish columns are items
  (`A67564`, `A68350`, ...). One row is one examinee sitting, so `id` is the
  row position within each form. Ids are therefore *not* comparable across
  forms, which is correct -- these are separate administrations and the
  deposit provides nothing to link a candidate across them.
* Item ids are the source column names, which are the exam's own item
  identifiers, so an item bank could be joined on them.
* Density is 1.000 in every form: no examinee skipped an item.
"""

import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/TQZQ6L"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"

# source filename -> table suffix
FORMS = {"19_1.tab": "2019_1", "19_2.tab": "2019_2",
         "20_1.tab": "2020_1", "20_2.tab": "2020_2",
         "21_1.tab": "2021_1", "21_2.tab": "2021_2"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    by_name = {f["dataFile"]["filename"]: f["dataFile"]["id"]
               for f in meta["files"]}
    missing = [n for n in FORMS if n not in by_name]
    assert not missing, (missing, sorted(by_name))

    os.makedirs(OUTDIR, exist_ok=True)
    seen_items, total = {}, 0
    for filename, suffix in FORMS.items():
        raw = s.get(f"{BASE}/api/access/datafile/{by_name[filename]}", timeout=900)
        raw.raise_for_status()
        d = pd.read_csv(io.BytesIO(raw.content), sep="\t", low_memory=False)

        items = [c for c in d.columns if re.match(r"^A\d+$", str(c))]
        assert len(items) == len(d.columns), (
            suffix, [c for c in d.columns if c not in items])
        seen_items[suffix] = set(items)

        d = d.reset_index(drop=True).copy()
        d["id"] = range(1, len(d) + 1)
        long = d.melt(id_vars=["id"], value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        assert long["resp"].isin([0, 1]).all()
        assert long.groupby("item")["resp"].nunique().min() > 1, f"{suffix}: constant item"
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"choi_2026_cmsce_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp 0-1, density {len(long)/(n_id*n_it):.3f}", flush=True)

    # The whole reason these ship separately: no item appears in two forms.
    names = list(seen_items)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            shared = seen_items[names[i]] & seen_items[names[j]]
            assert not shared, (names[i], names[j], sorted(shared)[:5])
    print(f"\n{len(FORMS)} tables, {total:,} responses; "
          f"{len(set().union(*seen_items.values()))} distinct items, no overlap "
          f"between any pair of forms")


if __name__ == "__main__":
    main()
