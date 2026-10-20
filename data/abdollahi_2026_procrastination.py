#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_Psychometric_comparison_of_the_Complete_and_Short_form_of_the_Persian_Academic_Procrastination_Scale_among_Iranian_students_b_/31724872
# DOI: 10.6084/m9.figshare.31724872.v1
#   Abdollahi, Abbas (2026). Psychometric comparison of the Complete and Short
#   form of the Persian Academic Procrastination Scale among Iranian students.
#   figshare dataset (published 2026-03-14).
# Data: Data23Azar_485.sav -- 485 Iranian students x 53 columns:
#       Proc1-Proc25 (Academic Procrastination Scale, complete form, 1-5),
#       Tukman1-Tukman16 (Tuckman Procrastination Scale, 1-4), nine
#       demographic columns and three total-score columns.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. The .sav has no variable labels and no value labels
#   on any item column (checked: column_labels is None for all Proc*/Tukman*
#   columns; the only label in the file is "age" on `Age`), and the deposit
#   holds no codebook -- the two files in it are the same .sav twice. The
#   wording would have to come from the published APS/Tuckman instruments.
#
# Two tables, one per instrument:
#   abdollahi_2026_aps        Proc1-Proc25, 1-5
#   abdollahi_2026_tuckman    Tukman1-Tukman16, 1-4 as administered here
# NOT shipped: APS (= the exact sum of Proc1-25, verified), Tuk (= the exact
#   sum of Tukman1-16, verified) and ShAPS (the short-form total, 5-25) are
#   composites; BirthYear is unusable (it mixes Persian calendar years such as
#   1380 with ages such as 20/22) and `Age` already carries age.
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR", REPO_ROOT / "automated_finding" / "irw_output"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://ndownloader.figshare.com/files/62784847"

COVS = {"Gender": "cov_gender", "maritalStatus": "cov_marital_status",
        "Age": "cov_age", "employmentStatus": "cov_employment_status",
        "Grade": "cov_grade", "major": "cov_major",
        "university": "cov_university"}
DROP = {"APS": "total of Proc1-25 (exact sum, verified) -- a composite",
        "Tuk": "total of Tukman1-16 (exact sum, verified) -- a composite",
        "ShAPS": "short-form total score (5-25) -- a composite",
        "BirthYear": "mixes Persian-calendar years with ages; Age is kept"}
SCALES = {"abdollahi_2026_aps": ([f"Proc{i}" for i in range(1, 26)], (1, 5)),
          "abdollahi_2026_tuckman": ([f"Tukman{i}" for i in range(1, 17)],
                                     (1, 4))}


def main() -> None:
    raw = Path(os.environ.get("IRW_RAW_DIR", "/tmp")) / "abdollahi_2026.sav"
    if not raw.exists():
        r = requests.get(DATA_URL, headers=UA, timeout=300)
        r.raise_for_status()
        raw.write_bytes(r.content)
    d, _meta = pyreadstat.read_sav(raw, apply_value_formats=False)

    items = [c for cols, _ in SCALES.values() for c in cols]
    accounted = {"Radif"} | set(COVS) | set(items) | set(DROP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in DROP.items():
        print(f"  skipped {c}: {why}")

    assert d["Radif"].nunique() == len(d)
    d = d.rename(columns={"Radif": "id", **COVS})
    covs = sorted(COVS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assert len(set(SCALES)) == len(SCALES)
    for name, (cols, (lo, hi)) in SCALES.items():
        assert len(name) <= 40, name
        t = d.melt(id_vars=["id"] + covs, value_vars=cols, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), "fractional resp -> imputation?"
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all(), sorted(t["resp"].unique())
        t["id"] = t["id"].astype(int)
        t = t[["id", "item", "resp"] + covs].reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
        pv = {i: list(range(lo, hi + 1)) for i in cols}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:180]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
