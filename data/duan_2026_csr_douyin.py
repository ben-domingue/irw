#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_for_Managing_CSR_Communication_on_Short-Video_Platforms_Trust_Favorability_and_Brand_Loyalty_/29062934
# DOI: 10.6084/m9.figshare.29062934 (data)
#   Duan Y (2026). Dataset for "Managing CSR Communication on Short-Video Platforms: Trust, Favorability and Brand
#   Loyalty" [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: SurveyData_cleaned.xlsx, 402 Chinese Douyin users (online survey, purposive/snowball sampling). The record names
#   the constructs: CSR communication transparency, consistency and relevance, trust, favorability, brand loyalty,
#   cognitive level and participation intention. Every item is observed on 1-5 (five-point agreement; the record calls
#   them scales), so 1-5 is taken as the range.
# Tables, one per construct, item = the deposit's own column code: _transparency (Tran1-3), _consistency (Cons1-3),
#   _relevance (REL1-3), _trust (Trust1-4), _favorability (FAV1-3), _brand_loyalty (BL1-4), _cognitive_level (CL1-5),
#   _participation (PI1-3). id = the deposit's "No." column.
# Covariates: none. Gender, Age, Education, Occupation and the two Douyin-use questions are numeric codes with no key
#   in the deposit, so they are not carried.
# PII: none (no free-text columns).
# Item text: not shipped -- the deposit has codes only; the stems are in the manuscript, not in the deposit.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://ndownloader.figshare.com/files/54564782'
N_ROWS = 402
ID_COL = 'No.'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'duan_2026_csr_transparency': ['Tran1', 'Tran2', 'Tran3'],
 'duan_2026_csr_consistency': ['Cons1', 'Cons2', 'Cons3'],
 'duan_2026_csr_relevance': ['REL1', 'REL2', 'REL3'],
 'duan_2026_csr_trust': ['Trust1', 'Trust2', 'Trust3', 'Trust4'],
 'duan_2026_csr_favorability': ['FAV1', 'FAV2', 'FAV3'],
 'duan_2026_csr_brand_loyalty': ['BL1', 'BL2', 'BL3', 'BL4'],
 'duan_2026_csr_cognitive_level': ['CL1', 'CL2', 'CL3', 'CL4', 'CL5'],
 'duan_2026_csr_participation': ['PI1', 'PI2', 'PI3']}
# (lo, hi) response range per table
RANGES = {'duan_2026_csr_transparency': (1, 5),
 'duan_2026_csr_consistency': (1, 5),
 'duan_2026_csr_relevance': (1, 5),
 'duan_2026_csr_trust': (1, 5),
 'duan_2026_csr_favorability': (1, 5),
 'duan_2026_csr_brand_loyalty': (1, 5),
 'duan_2026_csr_cognitive_level': (1, 5),
 'duan_2026_csr_participation': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Gender': 'unkeyed code',
 'Age': 'unkeyed code',
 'Education': 'unkeyed code',
 'Occupation': 'unkeyed code',
 'CSR_Douyin\n_freq': 'unkeyed code',
 'Douyin_\ndaily_time': 'unkeyed code'}


def load(content):
    d = pd.read_excel(io.BytesIO(content))
    return d.dropna(how="all")


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
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
    covs = list(COVS.values())
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
