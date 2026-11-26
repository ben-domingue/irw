#!/usr/bin/env python3
# Source: https://zenodo.org/records/24071577
# DOI: 10.5281/zenodo.24071577 (data)
#   inanna (2026). University Students' Learning and Literacy Survey Dataset (N=497) [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: All participants data.xlsx, 497 students at Universitas Negeri Makassar, Indonesia. The record
#   describes 17 indicators of four constructs on a five-point Likert scale, 1-5.
# Tables, one per construct (item = the deposit's column code): _transformative_learning (TL1-TL4),
#   _digital_literacy (DL1-DL4), _economic_literacy (ELE1-ELE4), _critical_thinking (CTC1-CTC5).
#   Same id (Responden, R001..) in all four.
# Covariates: cov_gender, cov_age_group, cov_semester (bands as recorded). University is one value
#   for every row and is not carried.
# Item text: not shipped -- the deposit holds codes only; no questionnaire or codebook in the record.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/24071577/files/All%20participants%20data.xlsx/content'
N_ROWS = 497
ID_COL = 'Responden'
COVS = {'Gender': 'cov_gender', 'Age': 'cov_age_group', 'Semester': 'cov_semester'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki-laki': 'male'}, 'cov_age_group': {'18–20 tahun': '18-20', '18-20 tahun': '18-20', '21–23 tahun': '21-23', '21-23 tahun': '21-23', '> 23 tahun': '>23'}, 'cov_semester': {'Semester 1–2': '1-2', 'Semester 3–4': '3-4', 'Semester 5–6': '5-6', 'Semester ≥ 7': '>=7'}}
RENAME = {}
BLOCKS = {'inanna_2026_transformative_learning': ['TL1', 'TL2', 'TL3', 'TL4'], 'inanna_2026_digital_literacy': ['DL1', 'DL2', 'DL3', 'DL4'], 'inanna_2026_economic_literacy': ['ELE1', 'ELE2', 'ELE3', 'ELE4'], 'inanna_2026_critical_thinking': ['CTC1', 'CTC2', 'CTC3', 'CTC4', 'CTC5']}
LO, HI = 1, 5


def load(content):
    return pd.read_excel(io.BytesIO(content))


def main():
    r = requests.get(URL, timeout=180)
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
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
