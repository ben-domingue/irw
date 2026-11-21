#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/30315556
# DOI: 10.6084/m9.figshare.30315556 (data)
#   Sebayang TE, Alhamdi MR (2025). The Influence Of Perceived Usefulness, Perceived Ease-Of-Use, Privacy Risk, And
#   Social Influence On Mobile Banking Adoption Among Generation Z In Greater Jakarta Area [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: MasterData.xlsx, 200 Gen Z respondents in Greater Jakarta; 20 items, every one observed within 1-5. The "Name"
#   column holds only the placeholders "Respondent 1".."Respondent 200" (checked) and is dropped.
# Tables, one per construct (item = column code): _perceived_usefulness (PU1-4), _perceived_ease_of_use (PEOU1-4),
#   _privacy_risk (PR1-3), _social_influence (SI1-4), _adoption (MBA1-5). id = the file's "No." (1..200).
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
URL = 'https://ndownloader.figshare.com/files/58587418'
N_ROWS = 200
ID_COL = 'No.'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'sebayang_2025_perceived_usefulness': ['PU1', 'PU2', 'PU3', 'PU4'], 'sebayang_2025_perceived_ease_of_use': ['PEOU1', 'PEOU2', 'PEOU3', 'PEOU4'], 'sebayang_2025_privacy_risk': ['PR1', 'PR2', 'PR3'], 'sebayang_2025_social_influence': ['SI1', 'SI2', 'SI3', 'SI4'], 'sebayang_2025_adoption': ['MBA1', 'MBA2', 'MBA3', 'MBA4', 'MBA5']}
LO, HI = 1, 5
DROP_COLS = ['Name']


def load(content):
    return pd.read_excel(io.BytesIO(content))


def keep_rows(d):
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
