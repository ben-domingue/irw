#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/31575919
# DOI: 10.6084/m9.figshare.31575919 (data)
#   Balakova I (2026). Questionnaire survey: Consumer handling of household equipment in the context of
#   sustainability [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: DATA_FINAL_ALL.xlsx, 750 completed interviews from a Czech online panel (October 2025, per the file's start dates). Sheet VALUES holds
#   numeric codes and sheet VARIABLES the same rows as labelled answers; the first row of each gives the question
#   codes. The attitude blocks are 7-point, 1 = rozhodne nesouhlasim (strongly disagree) .. 7 = rozhodne souhlasim
#   (strongly agree), or 1 (rozhodne ne) .. 7 (rozhodne ano) for the motive / barrier blocks -- the endpoints are
#   labelled in VARIABLES, the middle points are numbers only.
# Tables, one per question block (item = the question code): _sustainable_purchasing (Q2_1-8), _reuse_behavior
#   (Q5A_1-8), _reuse_centre (Q5B_1-7), _secondhand_motives (Q6_1-6), _secondhand_barriers (Q7_1-5),
#   _upcycling_attitudes (Q11_1-12), _furniture_motives (Q12_1-6: motives for buying upcycled furniture), _furniture_barriers
#   (Q13_1-8: barriers to it),
#   _sustainable_cosmetics (Q15_1-7), _refill_attitudes (Q17_1-7), _cosmetics_barriers (Q18_1-4). Not shipped: the
#   two ranking tasks (Q1, Q14), single questions (Q3, Q4, Q8-Q10, Q16) and the 0/1 information-channel checklist
#   (Q19). id = the panel's respondent number.
# Covariates (labelled text from VARIABLES): cov_gender, cov_age (years), cov_age_group, cov_education,
#   cov_economic_activity, cov_household_income, cov_settlement_size, cov_region (14 Czech regions).
# Item text: not shipped -- VARIABLES has every Czech stem in its headers with the endpoint labels; a cheap build
#   later (author-developed items).
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
URL = 'https://ndownloader.figshare.com/files/62536399'
N_ROWS = 750
ID_COL = 'ID'
COVS = {'G': 'cov_gender', 'A': 'cov_age', 'AK': 'cov_age_group', 'E': 'cov_education', 'W': 'cov_economic_activity', 'I': 'cov_household_income', 'S': 'cov_settlement_size', 'R': 'cov_region'}
COV_MAPS = {'cov_gender': {'Žena': 'female', 'Muž': 'male'}}
RENAME = {}
BLOCKS = {'balakova_2026_sustainable_purchasing': ['Q2_1', 'Q2_2', 'Q2_3', 'Q2_4', 'Q2_5', 'Q2_6', 'Q2_7', 'Q2_8'], 'balakova_2026_reuse_behavior': ['Q5A_1', 'Q5A_2', 'Q5A_3', 'Q5A_4', 'Q5A_5', 'Q5A_6', 'Q5A_7', 'Q5A_8'], 'balakova_2026_reuse_centre': ['Q5B_1', 'Q5B_2', 'Q5B_3', 'Q5B_4', 'Q5B_5', 'Q5B_6', 'Q5B_7'], 'balakova_2026_secondhand_motives': ['Q6_1', 'Q6_2', 'Q6_3', 'Q6_4', 'Q6_5', 'Q6_6'], 'balakova_2026_secondhand_barriers': ['Q7_1', 'Q7_2', 'Q7_3', 'Q7_4', 'Q7_5'], 'balakova_2026_upcycling_attitudes': ['Q11_1', 'Q11_2', 'Q11_3', 'Q11_4', 'Q11_5', 'Q11_6', 'Q11_7', 'Q11_8', 'Q11_9', 'Q11_10', 'Q11_11', 'Q11_12'], 'balakova_2026_furniture_motives': ['Q12_1', 'Q12_2', 'Q12_3', 'Q12_4', 'Q12_5', 'Q12_6'], 'balakova_2026_furniture_barriers': ['Q13_1', 'Q13_2', 'Q13_3', 'Q13_4', 'Q13_5', 'Q13_6', 'Q13_7', 'Q13_8'], 'balakova_2026_sustainable_cosmetics': ['Q15_1', 'Q15_2', 'Q15_3', 'Q15_4', 'Q15_5', 'Q15_6', 'Q15_7'], 'balakova_2026_refill_attitudes': ['Q17_1', 'Q17_2', 'Q17_3', 'Q17_4', 'Q17_5', 'Q17_6', 'Q17_7'], 'balakova_2026_cosmetics_barriers': ['Q18_1', 'Q18_2', 'Q18_3', 'Q18_4']}
LO, HI = 1, 7
DROP_COLS = []


def load(content):
    # Two sheets, same rows: VALUES holds the numeric codes, VARIABLES the same answers as labelled text. In both,
    # the first data row holds the question codes (Q2_1 ...), which become the column names.
    x = pd.ExcelFile(io.BytesIO(content))
    v = x.parse("VALUES", header=0)
    t = x.parse("VARIABLES", header=0)
    codes = [str(c) for c in t.iloc[0]]
    assert codes == [str(c) for c in v.iloc[0]] and (v["ID respondenta"].values == t["ID respondenta"].values).all()
    v, t = v.iloc[1:].reset_index(drop=True), t.iloc[1:].reset_index(drop=True)
    v.columns = t.columns = codes
    d = v[["ID"] + [c for c in codes if c.startswith(("Q2_", "Q5A_", "Q5B_", "Q6_", "Q7_", "Q11_", "Q12_", "Q13_", "Q15_", "Q17_", "Q18_"))]].copy()
    for src, new in [("Q20", "G"), ("Q21_KAT", "AK"), ("Q22", "E"), ("Q23", "W"), ("Q26", "I"), ("Q27", "S"), ("Q28", "R")]:
        d[new] = t[src].values
    d["A"] = pd.to_numeric(v["Q21"]).values
    return d


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
