#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.33425338.v1
# DOI: 10.6084/m9.figshare.33425338.v1 (data)
#   Ye Q (2026). Music Cognition and Purchase Intention in Video Games: The Mediating Roles of Immersion and Emotional Arousal - Dataset [Data set]. figshare. https://doi.org/10.6084/m9.figshare.33425338.v1
# License: CC BY 4.0 (record metadata)
# Data: 'Raw Data.xlsx', 561 Chinese players of Black Myth: Wukong; rows 1-2 of the sheet give every item's English and Chinese
#   wording, row 3 the codes (MC, IM, EA, PI, GE, CC); the file's No. as id. All items 1-5. GE (engagement/motivation after
#   the music) and CC (cultural meaning) are IRW's reading of the stems.
# Covariates: recruitment source, completion time (s), age band, gender, education, hours played, game progress.
# PII: none.
# Item text: English + Chinese wording for all 26 items in the first two sheet rows (cheap later build).
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://ndownloader.figshare.com/files/68170747'
N_ROWS = 561
ID_COL = 'No.'
COVS = {'Source': 'cov_source',
 'Time (s)': 'cov_completion_time_s',
 'Age': 'cov_age_band',
 'Gender': 'cov_gender',
 'Education': 'cov_education',
 'Duration of Playing “Black Myth Wukong”': 'cov_hours_played',
 'Progress in playing “Black Myth Wukong”': 'cov_game_progress'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'ye_2026_music_cognition': ['MC1', 'MC2', 'MC3', 'MC4'],
 'ye_2026_immersion': ['IM1', 'IM2', 'IM3', 'IM4'],
 'ye_2026_emotional_arousal': ['EA1', 'EA2', 'EA3', 'EA4'],
 'ye_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5'],
 'ye_2026_game_engagement': ['GE1', 'GE2', 'GE3', 'GE4', 'GE5'],
 'ye_2026_cultural_cognition': ['CC1', 'CC2', 'CC3', 'CC4']}
# (lo, hi) response range per table
RANGES = {'ye_2026_music_cognition': (1, 5),
 'ye_2026_immersion': (1, 5),
 'ye_2026_emotional_arousal': (1, 5),
 'ye_2026_purchase_intention': (1, 5),
 'ye_2026_game_engagement': (1, 5),
 'ye_2026_cultural_cognition': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=2)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d = d[d["Gender"] != "Gender"].reset_index(drop=True)
    for c in ["Source", "Gender", "Education", "Age", "Duration of Playing “Black Myth Wukong”", "Progress in playing “Black Myth Wukong”"]:
        d[c] = d[c].map(slug)
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
