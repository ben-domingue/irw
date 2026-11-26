#!/usr/bin/env python3
# Source: https://zenodo.org/records/23313645
# DOI: 10.5281/zenodo.23313645 (data)
#   Sucipto R, Susanto A, Utama A (2026). Dataset for Factors Affecting The Acceptance of Generative AI in
#   Improving the Financial Literacy of Retail Investors [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: the Google Forms export (one sheet), 151 retail investors in Jakarta/Tangerang; id = row order.
#   Each item header opens with its code (PEOU1 .. AU4) followed by the Indonesian stem. The record has no
#   description or anchors; every item is observed within 1-4, so 1-4 (four-point) is IRW's reading of the range.
# Tables, one per code prefix (TAM-style model): perceived ease of use, usefulness (PU1-3 and a second "PU3",
#   kept as PU3_b), attitude toward use, ethics, trust, social norm, actual use.
# Covariates: cov_age_band (Usia), cov_invest_experience (months investing).
# Dropped: Timestamp, the empty "Column 28", Domisili (city of residence; geographic rule).
# PII: none.
# Item text: shipped 2026-11-25c -- Indonesian stems from the Google Forms headers, IRW English, no anchors;
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
URL = 'https://zenodo.org/api/records/23313645/files/FAKTOR%20-%20FAKTOR%20YANG%20MEMPENGARUHI%20PENERIMAAN%20GENERATIVE%20AI%20DALAM%20MENINGKATKAN%20LITERASI%20KEUANGAN%20INVESTOR%20RITEL%20(Responses)%20(2).xlsx/content'
N_ROWS = 151
ID_COL = None
COVS = {'cov_age_band': 'cov_age_band', 'cov_invest_experience': 'cov_invest_experience'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'sucipto_2026_genai_peou': ['PEOU1', 'PEOU2', 'PEOU3'],
 'sucipto_2026_genai_usefulness': ['PU1', 'PU2', 'PU3', 'PU3_b'],
 'sucipto_2026_genai_attitude': ['ATU1', 'ATU2'],
 'sucipto_2026_genai_ethics': ['E1', 'E2', 'E3'],
 'sucipto_2026_genai_trust': ['T1', 'T2', 'T3', 'T4'],
 'sucipto_2026_genai_social_norm': ['SN1', 'SN2', 'SN3'],
 'sucipto_2026_genai_actual_use': ['AU1', 'AU2', 'AU3', 'AU4']}
# (lo, hi) response range per table
RANGES = {'sucipto_2026_genai_peou': (1, 4),
 'sucipto_2026_genai_usefulness': (1, 4),
 'sucipto_2026_genai_attitude': (1, 4),
 'sucipto_2026_genai_ethics': (1, 4),
 'sucipto_2026_genai_trust': (1, 4),
 'sucipto_2026_genai_social_norm': (1, 4),
 'sucipto_2026_genai_actual_use': (1, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Timestamp': 'form timestamp',
 'Column 28': 'empty',
 'Domisili': 'city of residence (geographic)',
 'Usia': 'carried as cov_age_band',
 'Pengalaman Berinvestasi di Pasar Modal Indonesia': 'carried as cov_invest_experience'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """item code = the code that opens each Google-Forms header; the deposit uses PU3 twice, the second becomes PU3_b"""
    new, seen = [], set()
    for c in d.columns:
        tok = c.split()[0]
        if re.fullmatch(r"[A-Z]+[0-9]", tok):
            tok = tok + "_b" if tok in seen else tok
            seen.add(tok)
            new.append(tok)
        else:
            new.append(c)
    d.columns = new
    d["cov_age_band"] = d["Usia"].str.replace(" Tahun", "").str.replace(" ", "")
    d["cov_invest_experience"] = d["Pengalaman Berinvestasi di Pasar Modal Indonesia"].map(slug)
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
        assert d[ID_COL].is_unique, "duplicate ids"
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
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
