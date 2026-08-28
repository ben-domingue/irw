"""Leadership Virtues Questionnaire (LVQ).

Source: Livacic-Rojas, Pablo, Harvard Dataverse 10.7910/DVN/AEX8PP, CC0 1.0 --
"Replication Data for: Data base of Validation and Analysis of the metric
Properties of the Leadership Virtues Questionnaire". Single .xlsx, 759
respondents x 19 columns, every column an LVQ item on a 1-5 scale.

The source uses the full item text as the column name (e.g. "Item 1= Does as
he/she ougth to do in a given situation"). Those are renamed to `Item1`..
`Item19` by their leading number: an IRW item code is a stable short
identifier, and a 90-character English sentence -- carrying the source's own
typos and a trailing `R*` reverse-scoring marker -- is item *text*, which
belongs in an item text table rather than in the `item` column.

The item numbers come from the labels themselves, not from column order, so a
reordering of the source file cannot silently renumber the items.
"""
import os
import re

import pandas as pd
import requests

DOI = "10.7910/DVN/AEX8PP"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "livacicrojas_2021_lvq"

# Harvard Dataverse answers 403 to requests without a User-Agent.
UA = {"User-Agent": "irw-batch/1.0 (research; contact itemresponsewarehouse@stanford.edu)"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    base = "https://dataverse.harvard.edu"
    meta = requests.get(f"{base}/api/datasets/:persistentId/",
                        params={"persistentId": f"doi:{DOI}"},
                        headers=UA, timeout=120).json()
    files = meta["data"]["latestVersion"]["files"]
    f = next(x for x in files
             if x["dataFile"]["filename"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f"{base}/api/access/datafile/{f['dataFile']['id']}",
                     headers=UA, timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["dataFile"]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df = pd.read_excel(fetch_raw(path))

    rename = {}
    for c in df.columns:
        m = re.match(r"^\s*Item\s*(\d+)", str(c))
        assert m, f"column is not a numbered LVQ item: {c!r}"
        rename[c] = f"Item{int(m.group(1))}"
    assert len(set(rename.values())) == 19, \
        f"expected 19 distinct item numbers, got {len(set(rename.values()))}"

    df = df.rename(columns=rename).reset_index(drop=True)
    items = sorted(set(rename.values()), key=lambda s: int(s[4:]))
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"], value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 19
    assert long["resp"].between(1, 5).all(), "LVQ is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
