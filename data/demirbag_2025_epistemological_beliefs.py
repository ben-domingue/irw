"""Demirbag & Savas (2025), Harvard Dataverse -- middle-school students'
epistemological beliefs, goal orientations and emotions.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/HYZ6QH
DOI: 10.7910/DVN/HYZ6QH
License: CC0 1.0

1,073 Turkish middle-school students completing three instruments. Found by
the 2026-08-26 triage of the educational-measurement term sweep.

Tables written
--------------
demirbag_2025_epistemological_beliefs   26 items, 1-5
demirbag_2025_emotions                  24 items, 1-5
demirbag_2025_goal_orientations         21 items, 1-5

Coding notes
------------
* The three blocks share a 1-5 scale but are distinct constructs, named by
  their source prefixes (`ep`, `emo`, `go`) and by the deposit's own title, so
  they ship as separate tables rather than one 71-item file.
* **The deposit has no identifier column**, so `id` is the row position --
  one row is one student.
* The file is described as a recoded dataset; every value is an integer in
  1-5 with no out-of-range codes.
* Source item names are kept so item text can join back.
"""

import io
import os
import re

import pandas as pd
import requests

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/HYZ6QH"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"

SCALES = [("ep",  "epistemological_beliefs", 26),
          ("emo", "emotions",                24),
          ("go",  "goal_orientations",       21)]


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
    for prefix, suffix, n_expected in SCALES:
        items = [c for c in d.columns if re.match(rf"^{prefix}\d+$", str(c))]
        assert len(items) == n_expected, (suffix, len(items))

        long = d.melt(id_vars=["id"], value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        assert long["resp"].between(1, 5).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"demirbag_2025_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")
    print(f"\n{len(SCALES)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
