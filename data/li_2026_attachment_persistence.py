#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_Beyond_Attachment_Stability_Individual_Differences_in_Attachment_Persistence_Across_Time_and_Relational_Transitions_b_/34399539
# DOI: 10.6084/m9.figshare.34399539.v1 (data; no paper DOI on the record)
#   Li H (2026). Beyond Attachment Stability: Individual Differences in
#   Attachment Persistence Across Time and Relational Transitions. figshare.
# Data: Study1_data.xlsx (1,205 Chinese university students, one wave) and
#   Study2_data.xlsx (1,112 students, three waves). Study3_data.xlsx (164
#   students; separation-context and repeated post-separation attachment
#   ratings) is not shipped: its repeated blocks are undocumented.
# License: CC BY 4.0 (figshare record).
# Codebook: none; the record's description gives the design.
#
# Instrument: an 18-item Adult Attachment Scale, 1-5 (AAS_1-18 in Study 1; in
#   Study 2 the same item numbers split into avoidance, AVD_AAS{1,2,5,6,7,8,
#   12,13,14,16,17,18}, and anxiety, ANX_AAS{3,4,9,10,11,15}). Item codes are
#   AAS1-AAS18 in both studies. One table, cov_study = 1/2 (same instrument,
#   independently recruited samples; Study 2 ids offset by 100000).
# Waves: Study 1 is wave 1; Study 2 columns W1_, W2_2_ and W3_ are waves 1-3
#   (the record: "rank-order continuity in both attachment dimensions across
#   three waves"). No calendar dates in the file.
# Counts: 1,205 and 1,112 rows; no N on the record to compare.
# Not shipped: the genotype columns (DRD2, MAOA, DBH, COMT, DAT polymorphisms).
#   They are genetic data, not demographics, and are left in the deposit.
# id = row index within study. Covariate: sex.
# Item text: not shipped -- none in the deposit.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
S1 = "https://ndownloader.figshare.com/files/70858983"
S2 = "https://ndownloader.figshare.com/files/70858998"
TABLE = "li_2026_aas"
WAVE = {"W1": 1, "W2_2": 2, "W3": 3}


def get(url):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def main():
    d1 = get(S1)
    assert d1.shape == (1205, 23), d1.shape
    d1 = d1.reset_index(drop=True)
    d1["id"] = d1.index + 1
    a1 = [f"AAS_{i}" for i in range(1, 19)]
    l1 = d1[["id", "Sex"] + a1].melt(id_vars=["id", "Sex"], var_name="src",
                                     value_name="resp")
    l1["item"] = l1["src"].str.replace("AAS_", "AAS", regex=False)
    l1["wave"] = 1
    l1["cov_study"] = 1

    d2 = get(S2)
    assert d2.shape == (1112, 60), d2.shape
    d2 = d2.reset_index(drop=True)
    d2["id"] = d2.index + 1 + 100000
    pat = re.compile(r"^(W1|W2_2|W3)_(AVD|ANX)_AAS(\d+)$")
    a2 = [c for c in d2.columns if pat.match(c)]
    assert len(a2) == 54
    l2 = d2[["id", "Sex"] + a2].melt(id_vars=["id", "Sex"], var_name="src",
                                     value_name="resp")
    m = l2["src"].str.extract(pat)
    l2["wave"] = m[0].map(WAVE)
    l2["item"] = "AAS" + m[2]
    l2["cov_study"] = 2
    sub = {"AVD": {1, 2, 5, 6, 7, 8, 12, 13, 14, 16, 17, 18}, "ANX": {3, 4, 9, 10, 11, 15}}
    for k, v in sub.items():
        assert set(m.loc[m[1] == k, 2].astype(int)) == v, k
    long = pd.concat([l1, l2], ignore_index=True).dropna(subset=["resp"])
    assert set(long["item"]) == {f"AAS{i}" for i in range(1, 19)}
    long = long.rename(columns={"Sex": "cov_sex"})
    allowed = set(range(1, 6))
    assert not set(long["resp"]) - allowed
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave", "cov_study", "cov_sex"]]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: allowed for c in set(long["item"])})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {TABLE} {c.name}: {c.detail[:120]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
