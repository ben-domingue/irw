#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0333390
# DOI: 10.1371/journal.pone.0333390
# Supporting Information: https://doi.org/10.1371/journal.pone.0333390.s001
#
# Four sleep/mood instruments bundled in one file, each written separately:
# the Korean Pre-Sleep Arousal Scale (PSAS, somatic + cognitive subscales),
# the Insomnia Severity Index (ISI, 7 raw components), 14 ordinal items
# from the Pittsburgh Sleep Quality Index (PSQI item 5's 10 disturbance
# sub-items plus items 6-9; PSQI items 1-4 are clock-time/duration fields,
# not Likert responses, and are excluded), and the Hospital Anxiety and
# Depression Scale (HADS, 14 items). All are stored as text-coded
# responses ("1=not at all", etc.) -- the leading integer is extracted.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0333390.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Age": "cov_age", "Gender": "cov_gender"}

PSAS_ITEMS = [f"PSAS_S{i}" for i in range(1, 9)] + [f"PSAS_C{i}" for i in range(1, 9)]
ISI_ITEMS = ["ISI_1_1", "ISI_1_2", "ISI_1_3", "ISI_2", "ISI_3", "ISI_4", "ISI_5"]
PSQI_ITEMS = [f"PSQI_5_{c}" for c in "abcdefghij"] + ["PSQI_6", "PSQI_7", "PSQI_8", "PSQI_9"]
HADS_ITEMS = [f"HADS_{i}" for i in range(1, 15)]


def extract_leading_int(series):
    return series.astype(str).str.extract(r"^(\d+)")[0].astype(float)


def write_scale(df, item_cols, cov_cols, out_name, valid_max):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = extract_leading_int(long["resp"])
    long = long[(long["resp"] >= 1) & (long["resp"] <= valid_max)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"No": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    if df["id"].nunique() != len(df):
        df = df.drop(columns=["id"]).reset_index(drop=True)
        df.insert(0, "id", df.index + 1)

    cov_cols = list(COV_RENAME.values())
    write_scale(df, PSAS_ITEMS, cov_cols, "kim_2025_psas", valid_max=5)
    write_scale(df, ISI_ITEMS, cov_cols, "kim_2025_isi", valid_max=5)
    write_scale(df, PSQI_ITEMS, cov_cols, "kim_2025_psqi", valid_max=4)
    write_scale(df, HADS_ITEMS, cov_cols, "kim_2025_hads", valid_max=4)


if __name__ == "__main__":
    convert()
