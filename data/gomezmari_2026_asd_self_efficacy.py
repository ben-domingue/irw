#!/usr/bin/env python3
# Source: https://zenodo.org/records/24271649
# DOI: 10.5281/zenodo.24271649 (data); paper 10.1111/1471-3802.12585
#   Gomez-Mari I, Pastor-Cerezuela G, Lacruz-Perez I, Tarraga-Minguez R (2026). Do labels matter? Analysis of teachers' self-efficacy towards the autism spectrum disorder depending on the diagnostic label [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24271649
# License: CC BY 4.0 (record metadata)
# Data: database.xlsx, two sheets: 117 pre-service teachers who read 'TEA' (ASD) and 114 who read 'Asperger' in the same 30
#   self-efficacy items (0-5); the header carries each item's Spanish wording. id = label + row.
# Covariates: label group, sex (1 man, 2 woman), age, programme (1 primary, 2 special-needs teaching), training/experience yes-no codes.
# Dropped: four free-text follow-ups and the sum.
# PII: none.
# Item text: Spanish wording of all 30 items in the column headers (cheap later build; the TEA/Asperger word differs by group).
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
URL = 'https://zenodo.org/api/records/24271649/files/database.xlsx/content'
N_ROWS = 231
ID_COL = 'pid'
COVS = {'label': 'cov_label',
 'sex': 'cov_sex',
 'age': 'cov_age',
 'programme': 'cov_programme',
 'other_training': 'cov_other_training',
 'asd_training': 'cov_asd_training',
 'asd_method_known': 'cov_asd_method_known',
 'asd_experience': 'cov_asd_experience'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'gomezmari_2026_asd_teacher_self_efficacy': ['item_1',
                                              'item_2',
                                              'item_3',
                                              'item_4',
                                              'item_5',
                                              'item_6',
                                              'item_7',
                                              'item_8',
                                              'item_9',
                                              'item_10',
                                              'item_11',
                                              'item_12',
                                              'item_13',
                                              'item_14',
                                              'item_15',
                                              'item_16',
                                              'item_17',
                                              'item_18',
                                              'item_19',
                                              'item_20',
                                              'item_21',
                                              'item_22',
                                              'item_23',
                                              'item_24',
                                              'item_25',
                                              'item_26',
                                              'item_27',
                                              'item_28',
                                              'item_29',
                                              'item_30']}
# (lo, hi) response range per table
RANGES = {'gomezmari_2026_asd_teacher_self_efficacy': (0, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'other_training_txt': 'free text',
 'asd_training_txt': 'free text',
 'asd_method_txt': 'free text',
 'asd_experience_txt': 'free text',
 'SUMATORIO TOTAL': 'sum score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """sheet 1 (ASD label) and sheet 2 (Asperger label) hold the same 30 items, worded with the label each group saw;
    item_k = the item numbered k in the header. Demographic columns are positional (identical across sheets)."""
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    sheets = pd.read_excel(io.BytesIO(r.content), sheet_name=None)
    parts = []
    for lab, s in zip(["asd", "asperger"], sheets.values()):
        s = s.dropna(subset=[s.columns[0]]).reset_index(drop=True)
        cols = list(s.columns)
        new = ["sex", "age", "programme", "other_training", "other_training_txt", "asd_training", "asd_training_txt", "asd_method_known",
               "asd_method_txt", "asd_experience", "asd_experience_txt"]
        for c in cols[11:41]:
            new.append("item_" + re.match(r"([0-9]+)[.]", c).group(1))
        new += [str(c) for c in cols[41:]]
        s.columns = new
        s["label"] = lab
        s["pid"] = [lab + "_" + str(i) for i in range(1, len(s) + 1)]
        parts.append(s)
    return pd.concat(parts, ignore_index=True)


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
