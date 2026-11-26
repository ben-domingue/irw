#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35106577.v1
# DOI: 10.6084/m9.figshare.35106577.v1 (data)
#   Ahmad M (2026). Trust, Verification Practices and Security Knowledge When Using AI-Generated Code Among Computing Students and Early-Career Developers [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35106577.v1
# License: CC BY 4.0 (record metadata)
# Data: workbook sheet Data_Entry (header on row 4), 342 computing students / early-career developers in Nigeria, Ghana and Niger, the
#   file's RespID. Instrument_EN gives every item's exact wording and format; Variable_Codebook the scales and the knowledge key (B,C,B,B,B,A).
# K1-K6 scored 0/1 against the documented key.
# Covariates: status, country, institution type, profile codes B05-B08, AI-use frequency, paid tools, survey language.
# Dropped: date, institution/employer name (B04), multi-select lists, guidance single items, free text, derived scores.
# PII: none.
# Item text: shipped 2026-11-25c -- Instrument_EN sheet, every item 'Author-written'; the French version (72
#   respondents) is in Bilingual_Instrument_A1;
#   automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://ndownloader.figshare.com/files/71835334'
N_ROWS = 342
ID_COL = 'RespID'
COVS = {'B01': 'cov_status',
 'B02': 'cov_country',
 'B03': 'cov_institution_type',
 'B05': 'cov_b05',
 'B06': 'cov_b06_months',
 'B07': 'cov_b07',
 'B08': 'cov_b08',
 'B10': 'cov_ai_use_freq',
 'B11': 'cov_paid_tools',
 'B13': 'cov_language'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'ahmad_2026_ai_reliance': ['UR1', 'UR2', 'UR3', 'UR4', 'UR5'],
 'ahmad_2026_trust_ai_code': ['TR1', 'TR2', 'TR3', 'TR4', 'TR5'],
 'ahmad_2026_verification_practices': ['VP1', 'VP2', 'VP3', 'VP4', 'VP5', 'VP6', 'VP7', 'VP8', 'VP9', 'VP10'],
 'ahmad_2026_secure_coding_self_efficacy': ['SE1', 'SE2', 'SE3', 'SE4', 'SE5'],
 'ahmad_2026_secure_coding_knowledge': ['K1', 'K2', 'K3', 'K4', 'K5', 'K6']}
# (lo, hi) response range per table
RANGES = {'ahmad_2026_ai_reliance': (1, 5),
 'ahmad_2026_trust_ai_code': (1, 5),
 'ahmad_2026_verification_practices': (1, 5),
 'ahmad_2026_secure_coding_self_efficacy': (1, 5),
 'ahmad_2026_secure_coding_knowledge': (0, 1)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Date': 'response date',
 'B04': 'institution / employer name (codebook: protect)',
 'B09': 'multi-select tool list',
 'B12': 'multi-select language list',
 'GP1': 'single guidance question',
 'GP2': 'single guidance question',
 'GP3': 'single guidance item',
 'GP4': 'single guidance item',
 'CH1': 'multi-select challenges',
 'OE1': 'free-text incident',
 'TR5_rev': 'reverse-coded copy',
 'Trust_mean': 'composite / derived',
 'Reliance_mean': 'composite / derived',
 'Verif_mean': 'composite / derived',
 'SelfEff_mean': 'composite / derived',
 'Knowledge_0to6': 'composite / derived',
 'Joint_TR2ge4_Kle3': 'composite / derived',
 'Trust_3item': 'composite / derived'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Data_Entry', header=3)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    key = {'K1': 'B', 'K2': 'C', 'K3': 'B', 'K4': 'B', 'K5': 'B', 'K6': 'A'}
    for c, k in key.items():
        d[c] = d[c].map(lambda v: v if pd.isna(v) else int(str(v).strip() == k))
    for c in ["B01", "B02", "B03", "B10", "B11", "B13"]:
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
