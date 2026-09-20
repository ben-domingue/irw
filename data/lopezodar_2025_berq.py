#!/usr/bin/env python3
"""Behavioral-Emotional Regulation Questionnaire in Peruvian adults (BERQ-PA).

Source: https://www.mdpi.com/2076-328X/15/2/224
DOI: 10.3390/bs15020224
Data: https://osf.io/t4kna/ (file "Base de datos BERQ_OSF.csv", osf.io/yru42)
License: CC BY 4.0 (Crossref and Europe PMC core record both report cc-by;
         the OSF node itself carries no licence statement, so the article's
         terms govern -- the deposit is the article's own supplementary data
         by the same authors)

403 Peruvian adults answered three instruments in one form. Each ships as its
own table, per the one-file-per-scale rule.

Response coding. The paper documents BERQ as a 5-point scale "from 1 (seldom)
to 5 (almost always)" and GHQ-28 as 4-point "from 0 (not at all) to 3 (much
more than usual)". GHQ arrives exactly as documented, 0-3. BERQ arrives 0-4 --
five levels, smooth and unimodal, every item spanning the full width -- i.e.
the depositors stored the documented 1-5 scale zero-indexed. Shipped as
recorded rather than shifted to 1-5: the ordering and spacing are what a model
uses, and re-indexing would invent a value that is not in the source file.

ERQ IS DELIBERATELY NOT SHIPPED. The paper states the Peruvian ERQ
(Gargurevich & Matos, 2010) "consists of 10 items answered through a 7-point
Likert scale (1 = strongly disagree and 7 = strongly agree)". The deposited
ERQ1-ERQ10 columns hold five levels, 0-4, across all 403 respondents -- not a
7-point scale with two unused extremes, since a 403 x 10 block would not miss
both top categories entirely. Something between administration and deposit
changed the scale, and nothing in the paper or the deposit says what. Unlike
the BERQ case above this is not a re-indexing: the number of levels disagrees,
so the responses cannot be mapped back to the documented anchors at all.
Shipping it would mean publishing a scale we cannot describe. Held pending a
question to the authors -- see automated_finding/TODO.md.

Item text: not shipped. All three instruments are third-party published
measures (BERQ: Kraaij & Garnefski 2019, Spanish adaptation by Dominguez-Lara
et al. 2022; GHQ-28: Goldberg & Hillier 1979) and the deposit's column names
are positional (BERQ1..BERQ20, GHQ1..GHQ28) with no labels of any kind -- it
is a plain CSV, so there is no variable-label or value-label level to check.
The paper prints only one example item per subscale. The wording is in the
cited source instruments, not here, and the third-party originator question
is the same one that holds the R-UCLA items (see TODO.md, Tatala 2023).
"""
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
DATA_URL = "https://osf.io/download/yru42/"
UA = {"User-Agent": "irw-batch/1.0 (research)"}

# table -> (item column prefix, n items, documented permitted values)
SCALES = {
    "lopezodar_2025_berq":  ("BERQ", 20, (0, 4)),
    "lopezodar_2025_ghq28": ("GHQ", 28, (0, 3)),
}

# ESTADOCIVIL and TIENEHIJOS are blank (" ") for some respondents and carry no
# codebook; kept as the source's own numeric codes with blanks as missing.
# TIENEHIJOS is named "has children" but takes values 0-3, so it reads as a
# count rather than a yes/no -- named neutrally for that reason.
COV_COLS = {
    "EDAD": "cov_age",
    "SEXO": "cov_sex",
    "GRADODEINST": "cov_education",
    "ESTADOCIVIL": "cov_marital_status",
    "TIENEHIJOS": "cov_children",
}


def fetch() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=120)
    r.raise_for_status()
    from io import BytesIO
    df = pd.read_csv(BytesIO(r.content))
    df.columns = [c.strip().lstrip("﻿") for c in df.columns]
    return df


def convert() -> None:
    raw = fetch()

    assert raw["SUJETO"].nunique() == len(raw), "SUJETO is not one row per person"
    raw = raw.rename(columns={"SUJETO": "id"})

    cov = raw[["id"] + list(COV_COLS)].rename(columns=COV_COLS)
    for c in ("cov_marital_status", "cov_children"):
        cov[c] = pd.to_numeric(cov[c].astype(str).str.strip(), errors="coerce")
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (prefix, n_items, (lo, hi)) in SCALES.items():
        item_cols = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        missing = [c for c in item_cols if c not in raw.columns]
        assert not missing, f"{table}: missing item columns {missing}"

        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), f"{table}: resp outside {lo}-{hi}"
        assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
        assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
        assert long["item"].nunique() == n_items, f"{table}: item count changed"
        # The paper: "no lost data were reported, and it was unnecessary to
        # apply imputation procedures" -- and the file has no missing cells.
        assert len(long) == len(raw) * n_items, f"{table}: cells lost in melt"

        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, [(c.name, c.detail) for c in bad]

        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
