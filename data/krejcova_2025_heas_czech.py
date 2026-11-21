#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/4fn25r4xfz (version 1)
# DOI: 10.17632/4fn25r4xfz (data)
#   Krejcova K (2025). Hogg Eco Anxiety Scale (HEAS) Czech validation [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: ecoanxiety_data.xlsx, 694 Czech respondents (2024-2025), all administered in Czech. The 13 item columns carry
#   the English stems of the Hogg Eco-Anxiety Scale (Hogg et al. 2021), in the published order: affective symptoms
#   (1-4), rumination (5-7), behavioural symptoms (8-10), anxiety about one's negative personal impact (11-13). The
#   HEAS asks how often over the past two weeks, 0 = Not at all .. 3 = Nearly every day; every item observed within 0-3.
# Item codes: the headers are the English stems, so item = HEAS1..HEAS13 by position (= the published numbering,
#   checked stem by stem). RENAME lists the pairs.
# Tables: _heas (13 items). id = the file's ID.
# Covariates: cov_gender; cov_age (typed free: three word answers converted, one implausible age of 6 set missing).
#   The language column is "Cestina" for every row and is not carried.
# Item text: not shipped -- English HEAS stems are the headers, but the Czech wording that was administered is not in
#   the deposit; HEAS needs a register row.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://data.mendeley.com/public-files/datasets/4fn25r4xfz/files/c334f5c4-bc7c-44dc-855e-4a900a42f3e7/file_downloaded'
N_ROWS = 694
ID_COL = 'ID'
COVS = {'gender': 'cov_gender', 'age_clean': 'cov_age'}
COV_MAPS = {'cov_gender': {'Žena': 'female', 'Muž': 'male', 'Raději nesdělovat': 'prefer_not_to_say'}}
RENAME = {'Feeling nervous, anxious or on edge': 'HEAS1', 'Not being able to stop or control worrying': 'HEAS2', 'Worrying too much': 'HEAS3', 'Feeling afraid': 'HEAS4', 'Unable to stop thinking about future climate change and other global environmental problems': 'HEAS5', 'Unable to stop thinking about past events related to climate change': 'HEAS6', 'Unable to stop thinking about losses to the environment': 'HEAS7', 'Difficulty sleeping': 'HEAS8', 'Difficulty enjoying social situations with family and friends': 'HEAS9', 'Difficulty working and/or studying': 'HEAS10', 'Feeling anxious about the impact of your personal behaviours on the earth': 'HEAS11', 'Feeling anxious about your personal responsibility to help address environmental problems': 'HEAS12', 'Feeling anxious that your personal behaviours will do little to help fix the problem': 'HEAS13', 'Gender (žena=female; muž=male)': 'gender'}
BLOCKS = {'krejcova_2025_heas': ['HEAS1', 'HEAS2', 'HEAS3', 'HEAS4', 'HEAS5', 'HEAS6', 'HEAS7', 'HEAS8', 'HEAS9', 'HEAS10', 'HEAS11', 'HEAS12', 'HEAS13']}
LO, HI = 0, 3
DROP_COLS = []


def load(content):
    return pd.read_excel(io.BytesIO(content))


def keep_rows(d):
    # Age was typed free; three answers are words ("dvacet jedna" = 21, "20 let", "26 let"). One recorded age of 6 in a
    # young-adult sample is a typo and is set missing.
    words = {"dvacet jedna": 21, "20 let": 20, "26 let": 26}
    age = d["Age"].map(lambda v: words.get(v.strip(), v) if isinstance(v, str) else v)
    age = pd.to_numeric(age, errors="raise")
    assert (age < 15).sum() == 1
    d["age_clean"] = age.where(age >= 15)
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
