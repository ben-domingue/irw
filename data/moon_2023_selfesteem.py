#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10629385 (PeerJ)
# DOI: 10.7717/peerj.16295
# License: CC BY 4.0
#
# "Multiple mediation effect of coping styles and self-esteem in the
# relationship between spousal support and pregnancy stress of married
# immigrant pregnant women" (2023, PeerJ). Raw .sav has an unambiguous
# `id` column (206 unique for 206 rows) -- the original triage's
# "low-confidence id column" flag was a false positive.
#
# Four scales are shipped, each as its own file: self-esteem (11 items,
# 1-4), stress coping (18 items, problem- + emotion-focused subscales
# combined per the source column naming, 1-5), spousal/social support
# (11 items, 1-6), pregnancy stress (11 items, 1-4). Each scale used `9`
# (support additionally had one non-integer `1.6` value) as a sentinel/
# missing code for a small number of cells -- filtered by the scale's
# actual observed valid range, not a blanket `dropna()`. The 5 composite-
# total columns at the end of the file (StressT, spospoT, esteemT,
# emotCoT, problCoT) are excluded.

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10629385/supplementaryFiles"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "selfesteem": (["selfesteem1"] + [f"se{i}" for i in range(2, 11)] + ["selfesteem11"], 1, 4),
    "coping": (["stresscopingproblem1"] + [f"stresscopingp{i}" for i in range(2, 9)]
               + [f"stresscopinge{i}" for i in range(9, 19)], 1, 5),
    "support": ([f"socialsupportp{i}" for i in range(1, 12)], 1, 6),
    "pregstress": ([f"pregnancystress{i}" for i in range(1, 12)], 1, 4),
}
COV_COLS = ["cov_mothage", "cov_edu", "cov_income", "cov_nation"]
COV_MAP = {"mothage": "cov_mothage", "edu": "cov_edu", "income": "cov_income", "nation": "cov_nation"}


def _fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPP_URL, headers=UA, timeout=60)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    sav_name = [n for n in zf.namelist() if n.endswith("s001.sav")][0]
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(zf.read(sav_name))
        tmp.flush()
        return pd.read_spss(tmp.name)


def convert():
    df = _fetch_raw()
    df = df.rename(columns=COV_MAP)
    assert df["id"].nunique() == len(df), "id not unique"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scale, (items, lo, hi) in SCALES.items():
        long = df.melt(id_vars=["id"] + COV_COLS, value_vars=items,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long[long["resp"] == long["resp"].round()]  # drop stray non-integer sentinel
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + COV_COLS]

        out_name = f"moon_2023_{scale}"
        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
