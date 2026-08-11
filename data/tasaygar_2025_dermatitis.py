#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331030
# DOI: 10.1371/journal.pone.0331030
# Supporting Information: https://doi.org/10.1371/journal.pone.0331030.s001
#
# Cross-sectional study of seborrheic dermatitis patients. The raw file's
# "ad soyad" (name/surname, Turkish) column is PII and is dropped entirely;
# it is also non-unique (common names repeat for different patients, verified
# by mismatched age/gender across "duplicate" names), so it cannot be used
# as id either -- row index is used instead. Two scales are extracted:
#   - Beck Anxiety Inventory (BAI): 21 items ("soru 1".."soru21"), 0-3 scale.
#   - SDASI severity components (Seborrheic Dermatitis Area and Severity
#     Index): 4 raw clinician-scored components (erythema, scaling,
#     infiltration, extent), 0-4ish scale each. A single isolated
#     out-of-range value (1.2 on the otherwise-integer "extent" item, 1 of
#     210 observations) is dropped as a data-entry error.
# The partial "Bortner" columns (only 7 of the standard ~14 bipolar items
# present in the shared file, ambiguous which half) are not shipped.
# One isolated out-of-range value (a single "4" on BAI item soru5, which is
# scored 0-3 on every other item and every other observation of soru5
# itself: 1 occurrence out of 210) is dropped as a data-entry error.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0331030.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

BAI_COLS = ["soru 1", "soru2", "soru3", "soru4", "soru5", "soru6", "soru7",
            "soru8", "soru9", "soru10", "soru11", "soru12", "soru13",
            "soru14", "soru15", "soru16", "soru17", "soru18", "soru19",
            "soru20", "soru21"]
SDASI_COLS = ["eritem", "skuam", "infültrasyon", "yaygınlık"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.drop(columns=["ad soyad"])  # PII
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def _write(df, item_cols, out_name):
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # isolated data-entry errors (single occurrence, out of line with the
    # rest of the item's / scale's distribution) -- see datastandard.md's
    # "Data entry errors at known values"
    long.loc[(long["item"] == "yaygınlık") & (long["resp"] % 1 != 0), "resp"] = float("nan")
    long.loc[(long["item"] == "soru5") & (long["resp"] == 4), "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    _write(df, BAI_COLS, "tasaygar_2025_bai")
    _write(df, SDASI_COLS, "tasaygar_2025_sdasi")


if __name__ == "__main__":
    convert()
