#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/TVUXDL
# DOI: 10.7910/DVN/TVUXDL (dataset; the record cites no paper)
#   chen, cthomas (2024). The study on the relationship between learning motivation and
#   learning effectiveness: the mediating effect of learning engagement and the moderating
#   effect of personality traits [Data set]. Harvard Dataverse.
# Data: "Data-2-learningmotivation-personality.xlsx" (file 10591424) -- 328 students.
#       Sheet "Specific data": Gender, Grade, M2-M10, I1-I9, C1..C23 (17 retained),
#       G1-G11. Sheet "Variable data": the same Gender/Grade and 15 construct means.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain xlsx, positional codes, no labels at either level, no
#   questionnaire deposited.
#
# How the blocks were identified: regressing each of the 15 deposited construct means on
#   all 46 item columns reproduces it exactly (max residual 0) as an equal-weight mean of
#   one block -- External motivation = M2-M5, Internal motivation = M6-M10; Vitality I1-I3,
#   Dedication I4-I6, Concentration I7-I9 (the UWES-9S layout); Expertise G1-G5,
#   Integrated skills G6-G11; Neuroticism C1,C6,C11,C16,C21; Extraversion C7,C12,C22;
#   Openness C8,C14,C18,C23; Agreeableness C9,C14; Conscientiousness C5,C10,C15. The script
#   re-derives and asserts this. Note the deposit's own scoring puts C14 in BOTH Openness
#   and Agreeableness and C13 in neither.
# Tables (one per instrument, as stored):
#   chen_2024_learning_motivation   M2-M10, 1-5 (external M2-M5, internal M6-M10)
#   chen_2024_learning_engagement   I1-I9, 1-5
#   chen_2024_personality           the 17 C items, 1-5 (trait membership above)
#   chen_2024_learning_effectiveness G1-G11, 1-4
# Covariates (codes as stored, undocumented): cov_gender, cov_grade.
# id: row index (no identifier).

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "tvuxdl"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/10591424?format=original"
P = "chen_2024_"
C = lambda *k: [f"C{i}" for i in k]  # noqa: E731
KEY = {"External motivation": [f"M{i}" for i in range(2, 6)],
       "Internal motivation": [f"M{i}" for i in range(6, 11)],
       "Vitality": ["I1", "I2", "I3"], "Dedication": ["I4", "I5", "I6"],
       "Concentration": ["I7", "I8", "I9"],
       "Expertise": [f"G{i}" for i in range(1, 6)],
       "Integrated skills": [f"G{i}" for i in range(6, 12)],
       "Neuroticism": C(1, 6, 11, 16, 21), "Extraversion": C(7, 12, 22),
       "Openness": C(8, 14, 18, 23), "Agreeableness": C(9, 14),
       "Conscientiousness": C(5, 10, 15)}
TABLES = {"learning_motivation": ("M", range(1, 6)), "learning_engagement": ("I", range(1, 6)),
          "personality": ("C", range(1, 6)), "learning_effectiveness": ("G", range(1, 5))}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    x = pd.ExcelFile(fetch())
    d = pd.read_excel(x, "Specific data")
    v = pd.read_excel(x, "Variable data")
    assert d.shape == (328, 48) and v.shape == (328, 17)
    assert (d[["Gender", "Grade"]].values == v[["Gender", "Grade"]].values).all()
    items = [c for c in d.columns if c not in ("Gender", "Grade")]
    for comp, its in KEY.items():
        X = np.c_[np.ones(len(d)), d[items].values]
        b = np.linalg.lstsq(X, v[comp].values, rcond=None)[0]
        found = [items[i] for i in range(len(items)) if abs(b[i + 1]) > 0.01]
        assert sorted(found) == sorted(its), (comp, found)
        assert np.allclose(d[its].mean(axis=1), v[comp])
    print("  [skip] sheet 'Variable data': 15 construct means (block membership verified)")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={"Gender": "cov_gender", "Grade": "cov_grade"})
    covs = ["cov_gender", "cov_grade"]
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, (pre, rng) in TABLES.items():
        name = P + k
        its = [c for c in items if c[0] == pre]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
