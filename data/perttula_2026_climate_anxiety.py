#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/6bc2mbztmy (version 1)
# DOI: 10.17632/6bc2mbztmy (data)
#   Perttula K (2026). Climate Change Anxiety Survey Data [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: Kelsi Data cleaned.sav (Qualtrics, autumn 2024), 452 Colorado State University students. "Data dictionary.csv"
#   and the .sav labels give each item's wording and coding: CAS1-CAS22 on 1 = Never .. 5 = Almost Always. The 22
#   stems are Clayton & Karazsia's (2020) Climate Change Anxiety Scale and its companion scales, verbatim in order:
#   cognitive-emotional (CAS1-8) and functional (CAS9-13) impairment, experience of climate change (CAS14-16) and
#   behavioural engagement (CAS17-22).
# Tables: _climate_anxiety (CAS1-CAS13, the anxiety scale proper), _climate_experience (CAS14-16), _climate_behavior
#   (CAS17-22). id = the Qualtrics ResponseId (a per-response key, not an account id).
# Covariates (from the .sav value labels): cov_sex, cov_race, cov_age_group, cov_living, cov_employed,
#   cov_parent_degree, cov_residency. Not carried: sexual orientation; free-text and numeric income; the free-text
#   "other" boxes; the CAPT single questions (each on its own response format) and select-all items.
# Item text: not shipped -- the stems are in the .sav labels and the data dictionary, but the CAS is a published
#   third-party instrument with no register row yet.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://data.mendeley.com/public-files/datasets/6bc2mbztmy/files/092c9c3c-fe1d-49fb-9ed3-9c7b3fbaf181/file_downloaded'
N_ROWS = 452
ID_COL = 'ResponseId'
COVS = {'Sex': 'cov_sex', 'RACE': 'cov_race', 'Age': 'cov_age_group', 'Living': 'cov_living', 'Employ': 'cov_employed', 'ParentDegree': 'cov_parent_degree', 'CSUResidency': 'cov_residency'}
COV_MAPS = {'cov_sex': {1.0: 'female', 2.0: 'male', 3.0: 'intersex'}, 'cov_race': {1.0: 'asian', 2.0: 'black', 3.0: 'indigenous', 4.0: 'latina_o', 5.0: 'middle_eastern', 6.0: 'white', 7.0: 'multiracial', 8.0: 'prefer_not_to_say'}, 'cov_age_group': {1.0: '15-17', 2.0: '18-22', 3.0: '23+'}, 'cov_living': {1.0: 'alone', 2.0: 'roommates_partner', 3.0: 'parents_caregiver'}, 'cov_employed': {1.0: 'yes', 2.0: 'no'}, 'cov_parent_degree': {1.0: 'yes', 2.0: 'no'}, 'cov_residency': {1.0: 'in_state', 2.0: 'out_of_state'}}
RENAME = {}
BLOCKS = {'perttula_2026_climate_anxiety': ['CAS1', 'CAS2', 'CAS3', 'CAS4', 'CAS5', 'CAS6', 'CAS7', 'CAS8', 'CAS9', 'CAS10', 'CAS11', 'CAS12', 'CAS13'], 'perttula_2026_climate_experience': ['CAS14', 'CAS15', 'CAS16'], 'perttula_2026_climate_behavior': ['CAS17', 'CAS18', 'CAS19', 'CAS20', 'CAS21', 'CAS22']}
LO, HI = 1, 5
DROP_COLS = ['Income', 'Income_r', 'Orientation', 'CAPT5_6_TEXT', 'CAPT6_4_TEXT', 'CAPT7_6_TEXT']


def load(content):
    import os, tempfile
    import pyreadstat
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(content)
    try:
        d, meta = pyreadstat.read_sav(f.name)
    finally:
        os.unlink(f.name)
    # The value labels this script maps from (checked when written): CAS1-CAS22 1 = Never .. 5 = Almost Always.
    assert meta.variable_value_labels["CAS1"] == {1.0: "Never", 2.0: "Rarely", 3.0: "Sometimes", 4.0: "Often", 5.0: "Almost Always"}
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
