#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/wxskmjb6m5 (version 2)
# DOI: 10.17632/wxskmjb6m5 (data)
#   Setiawan E, Adi HC, Mahaputra R, Granita W (2026). Survey Data on Social Media Influencer Credibility, Brand Trust,
#   Impulsive Buying, and Repurchase Intention among Indonesian Social Media Users [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: 01_Raw_Data_208_Respondents_Anonymized.xlsx, sheet Raw_Data (Google Forms, 6 May - 1 June 2026). 185 of the 208
#   rows answered the 30 items; the other 23 were screened out first. 03_Data_Codebook.xlsx gives every item's
#   construct and wording and the scale, Likert 1-5.
# Tables (item = column code): _influencer_credibility (SMIC: attractiveness ATT1-5, trustworthiness TRU1-5,
#   expertise EXP1-5), _brand_trust (BT1-BT5), _impulsive_buying (IB1-IB5), _repurchase_intention (RI1-RI5).
# Covariates: cov_age_group, cov_gender, cov_zero_variance (1 = the 18 respondents who gave one answer to all 30
#   items, whom the authors' 167-row cleaned file drops). Domicile, platforms, product category, spend and usage
#   frequency are not carried.
# Item text: not shipped -- 03_Data_Codebook.xlsx (Questionnaire_Codebook sheet) has the Bahasa Indonesia wording of all
#   30 items, but no anchor labels beyond "Likert 1-5"; items adapted from published scales (Reference_Sources sheet).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.mendeley.com/public-files/datasets/wxskmjb6m5/files/064997df-e7e5-44c8-97c3-9c6a8af1e91f/file_downloaded'
N_ROWS = 208
ID_COL = 'Respondent ID'
COVS = {'Age Group': 'cov_age_group', 'Gender': 'cov_gender', 'zero_var': 'cov_zero_variance'}
COV_MAPS = {'cov_gender': {'Perempuan': 'female', 'Laki-laki': 'male'}}
RENAME = {}
BLOCKS = {'setiawan_2026_influencer_credibility': ['ATT1', 'ATT2', 'ATT3', 'ATT4', 'ATT5', 'TRU1', 'TRU2', 'TRU3', 'TRU4', 'TRU5', 'EXP1', 'EXP2', 'EXP3', 'EXP4', 'EXP5'], 'setiawan_2026_brand_trust': ['BT1', 'BT2', 'BT3', 'BT4', 'BT5'], 'setiawan_2026_impulsive_buying': ['IB1', 'IB2', 'IB3', 'IB4', 'IB5'], 'setiawan_2026_repurchase_intention': ['RI1', 'RI2', 'RI3', 'RI4', 'RI5']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Raw_Data')


def keep_rows(d):
    items = sum(BLOCKS.values(), [])
    # 23 rows never reached the items (11 failed the prior-purchase screen, 12 were over 45 and were stopped).
    d = d[d[items].notna().any(axis=1)].copy()
    assert len(d) == 185 and d[items].notna().all().all()
    # The authors dropped 18 respondents who gave one answer to all 30 items; kept here and flagged.
    d["zero_var"] = (d[items].nunique(axis=1) == 1).astype(int)
    assert d["zero_var"].sum() == 18
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
