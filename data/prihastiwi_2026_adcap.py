"""Adaptive Capital Scale (AdCap), Indonesian sample.

Source: Prihastiwi, W. J. & Antawati, D. (2026), Zenodo 10.5281/zenodo.22104768,
CC BY 4.0 -- supporting dataset for the AdCap scale. Single file
`AdCap_Anonymized_Dataset.xlsx`, 1,010 respondents x 60 items on a 1-4 scale.

The sheet has a three-row hierarchical header, not a single header row:

    row 0  Aspek        Toughness | Innovativeness | Independence | Wisdom | Arif
    row 1  Indikator    the indicator under each aspect
    row 2  Nomer aitem  the questionnaire's own item number
    row 3+ subjek N     the responses

Read with `header=0` -- the natural call -- pandas takes row 0 as the header
and the item numbers become data, so the aspect names end up as column labels
and 59 of 60 columns come back named `Unnamed: N`. The item numbers in row 2
are the source's own identifiers and are used as the item codes, so `item` is
`AdCap_1`, `AdCap_8`, `AdCap_16` ... rather than a positional renumbering.

The aspect each item belongs to is carried as `itemcov_aspect`: it is a
property of the item, not of the respondent.
"""
import os

import pandas as pd
import requests

RECORD = 22104768
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "prihastiwi_2026_adcap"


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith((".xlsx", ".xls")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    raw = pd.read_excel(fetch_raw(path), header=None)
    assert str(raw.iloc[0, 0]).strip().lower() == "aspek", \
        "the three-row header is not where it was; re-inspect the sheet"
    assert str(raw.iloc[2, 0]).strip().lower().startswith("nomer"), \
        "row 2 is no longer the item-number row"

    aspects = raw.iloc[0, 1:].ffill()
    numbers = raw.iloc[2, 1:]
    body = raw.iloc[3:].reset_index(drop=True)

    items, aspect_of = [], {}
    for pos, (num, asp) in enumerate(zip(numbers, aspects), start=1):
        code = f"AdCap_{int(float(num))}"
        items.append((pos, code))
        aspect_of[code] = str(asp).strip()
    assert len(items) == 60, f"expected 60 items, found {len(items)}"
    assert len({c for _p, c in items}) == 60, "duplicate item numbers"

    records = []
    for row_i in range(len(body)):
        for pos, code in items:
            v = body.iloc[row_i, pos]
            if pd.isna(v):
                continue
            records.append((row_i + 1, code, int(float(v))))
    long = pd.DataFrame(records, columns=["id", "item", "resp"])
    long["itemcov_aspect"] = long["item"].map(aspect_of)

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 60
    assert long["resp"].between(1, 4).all(), \
        f"expected 1-4, saw {long['resp'].min()}-{long['resp'].max()}"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
