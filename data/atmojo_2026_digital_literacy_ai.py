#!/usr/bin/env python3
# Source: https://zenodo.org/records/24468012
# DOI: 10.5281/zenodo.24468012 (data)
#   Atmojo RNP, Livia V, Jesslyn N, Siswanto EG, Justin, Jonathan W (2026). Survey Dataset 2026: Digital Literacy, AI
#   Usage Experience, AI Knowledge, and AI Ethics Awareness among Young Adults in Indonesia [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: DatasetRev_Nov26.csv, 350 Indonesian young adults, the deposit's own No column. The deposit's other file
#   (Dataset_DigitalLiteracy_AI Awareness Young Adults 2026.csv, a two-row header in cp1252) holds identical values,
#   checked cell by cell. Items are observed on 1-6; the record gives no anchors, so 1-6 (six-point) is the range.
# Tables, one per construct named on the record and in the first file's group header, item = the deposit's code:
#   _digital_literacy (DL1-5), _ai_usage (AIUE1-5, AI usage experience), _ai_knowledge (AIK1-5), _ai_ethics
#   (AIEA1-5, AI ethics awareness), _attitude_ai (AT1-5, attitude toward AI).
# Covariates: none in the deposit.
# PII: none (all columns numeric).
# Item text: not shipped -- codes only in the deposit.
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
URL = 'https://zenodo.org/api/records/24468012/files/DatasetRev_Nov26.csv/content'
N_ROWS = 350
ID_COL = 'No'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'atmojo_2026_digital_literacy': ['DL1', 'DL2', 'DL3', 'DL4', 'DL5'],
 'atmojo_2026_ai_usage': ['AIUE1', 'AIUE2', 'AIUE3', 'AIUE4', 'AIUE5'],
 'atmojo_2026_ai_knowledge': ['AIK1', 'AIK2', 'AIK3', 'AIK4', 'AIK5'],
 'atmojo_2026_ai_ethics': ['AIEA1', 'AIEA2', 'AIEA3', 'AIEA4', 'AIEA5'],
 'atmojo_2026_attitude_ai': ['AT1', 'AT2', 'AT3', 'AT4', 'AT5']}
# (lo, hi) response range per table
RANGES = {'atmojo_2026_digital_literacy': (1, 6),
 'atmojo_2026_ai_usage': (1, 6),
 'atmojo_2026_ai_knowledge': (1, 6),
 'atmojo_2026_ai_ethics': (1, 6),
 'atmojo_2026_attitude_ai': (1, 6)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {}


def load(content):
    return pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")


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
