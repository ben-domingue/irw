#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Mobile_Banking_Adoption_and_Usage_among_Malaysians_of_Generation_Y/14882307
# DOI: 10.6084/m9.figshare.14882307 (data)
#   Al Tarawneh MA, Yong GF, Nguyen L (2021). Mobile Banking Adoption and Usage among Malaysians of Generation Y
#   [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: "Dataset_Mobile Banking Adoption ... Generation Y.xlsx", sheet "Raw data": 504 Malaysian Gen Y respondents
#   (Case is the original survey number, unique). The "- revised" workbook in the record holds the same values under
#   descriptive headers. Survey_Questionnaire _ Moemen.pdf (in the record) gives every section in order -- UTAUT2's
#   performance expectancy, effort expectancy, social influence, facilitating conditions, hedonic motivation, price
#   value, habit; then financial, time, performance, privacy, security and psychological risk; interface design
#   quality; intention to use; mobile banking use -- each on Strongly Disagree .. Strongly Agree (1-5), except
#   MBU2, the frequency of use (Very rare .. Daily use, 5 points).
# Tables (item = column code): one per UTAUT2 construct (_performance_expectancy PE1-4, _effort_expectancy EE1-4,
#   _social_influence SI1-3, _facilitating_conditions FC1-4, _hedonic_motivation HM1-3, _price_value PV1-4, _habit
#   HA1-4); _perceived_risk (the six risk facets, FR1-3 TR1-4 PR1-5 PvR1-3 SR1-3 PsR1-3; TR is time risk);
#   _interface_design (IDQ1-4); _intention_to_use (IU1-3); _use (MBU1 dependence, MBU2 frequency).
# Covariates: none. Gender, Age, Race, Education, Employment, Income, M.Use and M.Exp are stored as numeric codes; the
#   questionnaire lists the options in order but the file carries no value labels, so the codes are not carried.
# Item text: not shipped -- the questionnaire PDF has the English stems (by section, matching the codes) and the
#   anchors; the UTAUT2 items are Venkatesh et al. (2012) adaptations and need a register row first.
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
URL = 'https://ndownloader.figshare.com/files/28653108'
N_ROWS = 504
ID_COL = 'Case'
COVS = {}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'altarawneh_2021_performance_expectancy': ['PE1', 'PE2', 'PE3', 'PE4'], 'altarawneh_2021_effort_expectancy': ['EE1', 'EE2', 'EE3', 'EE4'], 'altarawneh_2021_social_influence': ['SI1', 'SI2', 'SI3'], 'altarawneh_2021_facilitating_conditions': ['FC1', 'FC2', 'FC3', 'FC4'], 'altarawneh_2021_hedonic_motivation': ['HM1', 'HM2', 'HM3'], 'altarawneh_2021_price_value': ['PV1', 'PV2', 'PV3', 'PV4'], 'altarawneh_2021_habit': ['HA1', 'HA2', 'HA3', 'HA4'], 'altarawneh_2021_perceived_risk': ['FR1', 'FR2', 'FR3', 'TR1', 'TR2', 'TR3', 'TR4', 'PR1', 'PR2', 'PR3', 'PR4', 'PR5', 'PvR1', 'PvR2', 'PvR3', 'SR1', 'SR2', 'SR3', 'PsR1', 'PsR2', 'PsR3'], 'altarawneh_2021_interface_design': ['IDQ1', 'IDQ2', 'IDQ3', 'IDQ4'], 'altarawneh_2021_intention_to_use': ['IU1', 'IU2', 'IU3'], 'altarawneh_2021_use': ['MBU1', 'MBU2']}
LO, HI = 1, 5
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name='Raw data')


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
