#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33390886
# DOI: 10.6084/m9.figshare.33390886 (data)
#   Suryanegara E, Indradewa R, Anindita R, Alif MG (2026). Survey Response Data: Omnichannel Retailing, Service
#   Quality, Brand Trust, Customer Brand Engagement, and Brand Advocacy in Indonesian Healthcare Services [Data set].
#   figshare. Underlying data for an article submitted to F1000Research.
# License: CC0 (figshare record metadata)
# Data: Survey_Response_Data_324_EN.csv, 324 patients surveyed on site after a visit at three facilities in Jakarta and
#   Tangerang (Klinik Sehatku 101, Ukrida Hospital 108, Kalideres Regional General Hospital 115). 49 five-point
#   Likert items (record description); every item observed on 1-5.
# Tables (item = the deposit's column code): _omnichannel (OCR1-OCR10); _servqual (22 items, the five SERVQUAL
#   dimensions: tangibles T1-T4, reliability R1-R5, responsiveness Res1-Res4, assurance A1-A4, empathy E1-E5);
#   _brand_trust (BT1-BT4); _brand_engagement (cognitive Cog1-3, affective AFF1-4, behavioural BEH1-3);
#   _brand_advocacy (BA1-BA3). Same id (RespondentID) in all five.
# Covariates: cov_site, cov_age_group, cov_sex, cov_education, cov_monthly_expenditure. The three eligibility
#   questions are "Yes" for every row and are not carried; online channels used is not carried.
# Item text: not shipped -- the record mentions a codebook but none is in the figshare deposit (one CSV only).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://ndownloader.figshare.com/files/69749466'
N_ROWS = 324
ID_COL = 'RespondentID'
COVS = {'Site': 'cov_site', 'AgeGroup': 'cov_age_group', 'Sex': 'cov_sex', 'Education': 'cov_education', 'MonthlyExpenditure': 'cov_monthly_expenditure'}
COV_MAPS = {'cov_sex': {'Female': 'female', 'Male': 'male'}}
RENAME = {}
BLOCKS = {'suryanegara_2026_omnichannel': ['OCR1', 'OCR2', 'OCR3', 'OCR4', 'OCR5', 'OCR6', 'OCR7', 'OCR8', 'OCR9', 'OCR10'], 'suryanegara_2026_servqual': ['T1', 'T2', 'T3', 'T4', 'R1', 'R2', 'R3', 'R4', 'R5', 'Res1', 'Res2', 'Res3', 'Res4', 'A1', 'A2', 'A3', 'A4', 'E1', 'E2', 'E3', 'E4', 'E5'], 'suryanegara_2026_brand_trust': ['BT1', 'BT2', 'BT3', 'BT4'], 'suryanegara_2026_brand_engagement': ['Cog1', 'Cog2', 'Cog3', 'AFF1', 'AFF2', 'AFF3', 'AFF4', 'BEH1', 'BEH2', 'BEH3'], 'suryanegara_2026_brand_advocacy': ['BA1', 'BA2', 'BA3']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_csv(io.BytesIO(content))


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
