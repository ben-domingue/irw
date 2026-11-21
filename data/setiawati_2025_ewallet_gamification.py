#!/usr/bin/env python3
# Source: https://zenodo.org/records/15233515
# DOI: 10.5281/zenodo.15233515 (data)
#   Setiawati R (2025). Enhancing Gen Z Customer Decision Through Gamification Marketing, Peer Influence and User
#   Experience in E-Wallet [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: data kuesioner E-wallet.xlsx, 370 Gen Z e-wallet users in Jabodetabek; every item observed within 1-5.
#   questionnaire.docx (in the deposit) lists the four variables and one statement per indicator in order:
#   gamification marketing (3 indicators), peer influence (5), user experience (4), customer decision (4) --
#   matching X1.1-X1.3, X2.1-X2.5, X3.1-X3.4, Y1-Y4.
# Tables (item = column code): _gamification, _peer_influence, _user_experience, _customer_decision. No demographics
#   in the data file.
# Item text: not shipped -- the docx has the Indonesian statements but no response anchors.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://zenodo.org/api/records/15233515/files/data%20kuesioner%20E-wallet.xlsx/content'
N_ROWS = 370
ID_COL = 'No Responden'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'setiawati_2025_gamification': ['X1.1', 'X1.2', 'X1.3'], 'setiawati_2025_peer_influence': ['X2.1', 'X2.2', 'X2.3', 'X2.4', 'X2.5'], 'setiawati_2025_user_experience': ['X3.1', 'X3.2', 'X3.3', 'X3.4'], 'setiawati_2025_customer_decision': ['Y1', 'Y2', 'Y3', 'Y4']}
LO, HI = 1, 5
DROP_COLS = []


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
