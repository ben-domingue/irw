#!/usr/bin/env python3
# Source: https://zenodo.org/records/18454147
# DOI: 10.5281/zenodo.18454147 (data)
#   Febriyanti RW, Rahmadini FI, Putra EP (2026). User Acceptance of a Ride-Hailing Application: An Extended Technology
#   Acceptance Model Integrating Trust and Service Quality [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: hasil data.csv (semicolon-separated; the SmartPLS input), TAM items on ride-hailing in Jabodetabek. The record
#   reports 150 active users. The file has 250 rows but only 149 distinct response patterns: 101 rows are exact
#   copies of other rows (pairs, not straight-liners), i.e. the file was padded. Exact duplicates are dropped,
#   leaving 149 rows, which matches the record's N. No respondent id, so id = row order after de-duplication.
#   Every item observed within 1-6, and no 7 occurs anywhere, so the range is taken as 1-6 (the record states none).
# Tables, one per construct (item = column code; the file's own "SQ" for the first service-quality item is kept):
#   _trust (T1-3), _service_quality (SQ, SQ2, SQ3), _perceived_usefulness (PU1-3), _perceived_ease_of_use (PEOU1-3),
#   _attitude (ATU1-3), _actual_use (AU1-3), _behavioral_intention (BI1-3). No demographics in the file.
# Item text: not shipped -- codes only.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/18454147/files/hasil%20data.csv/content'
N_ROWS = 250
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'febriyanti_2026_trust': ['T1', 'T2', 'T3'], 'febriyanti_2026_service_quality': ['SQ', 'SQ2', 'SQ3'], 'febriyanti_2026_perceived_usefulness': ['PU1', 'PU2', 'PU3'], 'febriyanti_2026_perceived_ease_of_use': ['PEOU1', 'PEOU2', 'PEOU3'], 'febriyanti_2026_attitude': ['ATU1', 'ATU2', 'ATU3'], 'febriyanti_2026_actual_use': ['AU1', 'AU2', 'AU3'], 'febriyanti_2026_behavioral_intention': ['BI1', 'BI2', 'BI3']}
LO, HI = 1, 6
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content), sep=';')


def keep_rows(d):
    n0 = len(d)
    d = d.drop_duplicates()
    print("exact duplicate rows dropped:", n0 - len(d))
    assert len(d) == 149
    return d


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    d = d.drop(columns=[c for c in DROP_COLS if c in d.columns])
    d = keep_rows(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        d[cov] = d[src].map(COV_MAPS[cov]) if cov in COV_MAPS else d[src]
        if cov in COV_MAPS:
            assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    shipped = set()
    for name, items in BLOCKS.items():
        assert all(c in d for c in items), [c for c in items if c not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(LO, HI).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert name not in shipped
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    used = set(sum(BLOCKS.values(), [])) | set(COVS) | {ID_COL}
    print("source columns not shipped:", [c for c in d.columns if c not in used and c != "id" and c not in covs])


if __name__ == "__main__":
    main()
