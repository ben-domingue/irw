#!/usr/bin/env python3
# Source: https://zenodo.org/records/7499867
# DOI: 10.5281/zenodo.7499867 (data)
#   Garcia Bacete, F. J., Marande Perrin, G., Munoz Tinoco, M. V., & GREI
#   Group (2023). "Friendship Features Interview for Young Children //
#   FRIENDSHIP-Q_Data_CC_T4-Post." Zenodo.
# Data: FRIENDSHIP-Q_Data_CC_T4-Post.sav (latin-1 strings), 4th-grade pupils
#   of the GREI Castellon comparison cohort, spring 2013: the Friendship
#   Features Interview for Young Children (Ladd, Kochenderfer & Coleman 1996,
#   Spanish translation), 24 items about a named best friend, 1 = no,
#   2 = sometimes, 3 = yes. The Met-D PDF gives every item's wording.
# License: CC BY 4.0 (Zenodo record).
# Codebook: FRIENDSHIP-Q_Met-D_CC_T4-Post_Eng.pdf in the deposit.
#
# GREI is a near-identical T1-T4 series; this is the one representative
#   wave for this instrument (see garciabacete_2023_teacher_relationship.py).
# Item text: not shipped -- wording in the Met-D PDF; no rights-register row.
#
# Table: garciabacete_2023_friendship_features, FriendshipQ1..Q24 (wave
#   suffix stripped), 1-3, items as deposited (the deposit's factor scores
#   are not shipped). Of 290 roster rows, 118 children answered.
# Covariates: cov_sex (0 = boy, 1 = girl), cov_friend_sex, cov_classroom.
#   The friend's study ID is not carried. id = the deposit's 6-digit child ID.

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
URL = ("https://zenodo.org/api/records/7499867/files/"
       "FRIENDSHIP-Q_Data_CC_T4-Post.sav/content")
TABLE = "garciabacete_2023_friendship_features"
SUF = "_T4post"
ITEMS = [f"FriendshipQ{i}" for i in range(1, 25)]
ALLOWED = {1, 2, 3}
SEX = {0: "boy", 1: "girl"}


def main():
    r = requests.get(URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        d, _ = pyreadstat.read_sav(tmp.name, encoding="latin1")
    assert d.shape == (290, 38), d.shape
    d = d.rename(columns={i + SUF: i for i in ITEMS})
    assert d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d["cov_sex"] = d["Sex"].map(SEX)
    d["cov_friend_sex"] = d["SexFriend" + SUF].map(SEX)
    d["cov_classroom"] = d["Classroom" + SUF].astype("Int64")
    covs = ["cov_sex", "cov_friend_sex", "cov_classroom"]
    long = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
                  value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert not set(long["resp"]) - ALLOWED
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: ALLOWED for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
