#!/usr/bin/env python3
# Source: https://zenodo.org/records/23977547
# DOI: 10.5281/zenodo.23977547 (data)
#   Saputra D, Viaura NF, Clara L (2026). Examining the Effect of Brand Experience on Brand Loyalty through Brand Trust
#   and Brand Love in High-End Luxury Brands [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: "yang baru.csv" (semicolon-separated), 268 rows of 20 items, every one observed within 1-5. Construct names
#   follow the title's order (brand experience X1, brand trust Z1, brand love Z2, brand loyalty Y1) -- the record has
#   no description, so the code-to-construct reading is IRW's. 9 rows are exact copies of another row (one group of
#   six all-same rows, two copied non-straight-line pairs); read as double submissions and dropped, leaving 259.
#   No respondent id, so id = row order after de-duplication.
# Tables (item = column code): _brand_experience (X1.1-X1.6), _brand_trust (Z1.1-Z1.4), _brand_love (Z2.1-Z2.4),
#   _brand_loyalty (Y1.1-Y1.6). No demographics in the file.
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
URL = 'https://zenodo.org/api/records/23977547/files/yang%20baru.csv/content'
N_ROWS = 268
ID_COL = None
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'saputra_2026_brand_experience': ['X1.1', 'X1.2', 'X1.3', 'X1.4', 'X1.5', 'X1.6'], 'saputra_2026_brand_trust': ['Z1.1', 'Z1.2', 'Z1.3', 'Z1.4'], 'saputra_2026_brand_love': ['Z2.1', 'Z2.2', 'Z2.3', 'Z2.4'], 'saputra_2026_brand_loyalty': ['Y1.1', 'Y1.2', 'Y1.3', 'Y1.4', 'Y1.5', 'Y1.6']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content), sep=';')


def keep_rows(d):
    n0 = len(d)
    d = d.drop_duplicates()
    print("exact duplicate rows dropped:", n0 - len(d))
    assert len(d) == 259
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
