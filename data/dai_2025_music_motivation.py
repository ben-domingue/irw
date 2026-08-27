"""MUSIC(R) Academic Motivation Inventory, Chinese Legal English / Legal
Translation students.

DOI: 10.17632/hwvsd5zd4d
Source: https://data.mendeley.com/datasets/hwvsd5zd4d
License: CC BY 4.0
Contributor (deposit record): DAI, Xiao

356 respondents, 19 MUSIC inventory items on a 1-6 scale.

The workbook uses TWO header rows: row 0 carries the covariate names plus a
single merged 'MUSIC Inventory Items' banner over the item block, and row 1
carries each item's full Chinese wording. Read naively this yields
'Unnamed: N' columns, which is why the connector could not identify the item
block. Here the file is read with header=None and skiprows=2, covariate names
are taken from row 0 and item wording from row 1.

Items are shipped under stable codes item01-item19 rather than their Chinese
sentences, because `item` is the join key against a future itemtext table and
must be a short stable identifier. The Chinese wording is printed at build
time and is available in the source file for that later itemtext pass.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

DOI = "10.17632/hwvsd5zd4d"
KEY = "hwvsd5zd4d"
FILENAME = "Dataset.xlsx"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

N_COV = 5                      # Number, Time, Major, Grade, Gender
COV_NAMES = {"Time": "cov_time_code", "Major": "cov_major",
             "Grade": "cov_grade", "Gender": "cov_gender"}
SCALE = (1, 6)


def fetch() -> bytes:
    r = requests.get(f"https://data.mendeley.com/public-api/datasets/{KEY}",
                     headers=UA, timeout=60)
    r.raise_for_status()
    match = [f for f in r.json()["files"] if f["filename"] == FILENAME]
    assert len(match) == 1
    rr = requests.get(match[0]["content_details"]["download_url"],
                      headers=UA, timeout=180)
    rr.raise_for_status()
    return rr.content


def build() -> None:
    raw = fetch()
    head = pd.read_excel(io.BytesIO(raw), header=None, nrows=2)
    body = pd.read_excel(io.BytesIO(raw), header=None, skiprows=2)

    cov_labels = [str(x).strip() for x in head.iloc[0, :N_COV]]
    item_text = [str(x).strip() for x in head.iloc[1, N_COV:]]
    assert cov_labels[0] == "Number", cov_labels
    assert all(t and t != "nan" for t in item_text), item_text
    assert len(cov_labels) + len(item_text) == body.shape[1], \
        (len(cov_labels), len(item_text), body.shape)

    codes = [f"item{i:02d}" for i in range(1, len(item_text) + 1)]
    body.columns = cov_labels + codes
    body["id"] = range(1, len(body) + 1)

    print(f"  {len(codes)} items, Chinese wording kept for a future itemtext pass:")
    for code, text in list(zip(codes, item_text))[:3]:
        print(f"    {code}: {text}")
    print(f"    ... and {len(codes) - 3} more")

    cov = body[["id"] + list(COV_NAMES)].rename(columns=COV_NAMES)
    long = (body[["id"] + codes]
            .melt(id_vars="id", var_name="item", value_name="resp")
            .dropna(subset=["resp"])
            .merge(cov, on="id"))
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(*SCALE).all(), sorted(long["resp"].unique())
    long = long[["id", "item", "resp"] + list(COV_NAMES.values())]

    checks = run_qc(long)
    fails = [c for c in checks if c.status == "fail"]
    assert not fails, [(c.name, c.detail) for c in fails]
    for c in checks:
        if c.status == "warn":
            print(f"    NOTE {c.name}: {c.detail}")

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() > 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "dai_2025_music_motivation.csv", index=False)
    print(f"  dai_2025_music_motivation: {long['id'].nunique()} ids x "
          f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    build()
