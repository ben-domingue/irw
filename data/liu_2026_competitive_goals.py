#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Data_for_Competitive_Achievement_Goals_and_Social_Alienation_in_Chinese_Junior_High_School_Students_Evidence_from_PLS-SEM_and_fsQCA/32599122
# DOI: 10.6084/m9.figshare.32599122.v1 (dataset; the manuscript it accompanies has no DOI yet)
#   Liu, Jie; Guo, Hongxia; Gai, Yihe; Luo, Kangrong (2026). "Data for: Competitive
#   Achievement Goals and Social Alienation in Chinese Junior High School Students:
#   Evidence from PLS-SEM and fsQCA". figshare.
# Data: Original_data.csv (file 65349861) -- 1,883 junior high school students from 40
#       schools in Chengdu, paper-and-pencil survey; 21 composite/subscale means, ID,
#       four demographics and 86 item responses. Data_Dictionary_clean.xlsx (file
#       65349858) gives, per column, its construct, dimension, role and coding
#       (agreement items 1 = strongly disagree .. 5 = strongly agree; self-control
#       items 1 = not at all like me .. 5 = very much like me; higher = more of the
#       construct for every item).
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Plain CSV (no variable or value labels at either level); the
#   dictionary's labels are positional ("Social alienation item 3"). The wording is in
#   the manuscript's (Chinese) instruments, not deposited.
#
# Tables (one per instrument, as the dictionary's Construct column groups them):
#   liu_2026_competitive_goals   X1_1-3 performance-approach, X2_1-3 performance-avoidance
#   liu_2026_social_alienation   Y1-Y15
#   liu_2026_moral_disengagement M1_<dim>_<k>: 8 mechanisms, 26 items
#   liu_2026_empathy             M2_1_1-11 cognitive, M2_2_1-9 affective
#   liu_2026_self_control        M3_<dim>_<k>: 5 dimensions, 19 items
#   All five pass run_qc with no warnings.
# Composites: each of the 21 composite/subscale columns is checked to equal the mean of
#   the items its dictionary Derivation lists (so the item cells are the scored ones and
#   none is imputed), then skipped. Every item cell is an integer 1-5; no missing cells.
# Covariates (dictionary codes): cov_gender (0 female, 1 male), cov_school_location
#   (0 rural, 1 urban), cov_grade (1-3 = grades 7-9), cov_only_child (0 only child,
#   1 not).
# id: the deposit's ID.

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "f32599122"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"data.csv": "https://ndownloader.figshare.com/files/65349861",
         "dict.xlsx": "https://ndownloader.figshare.com/files/65349858"}
P = "liu_2026_"
TABLES = {"competitive_goals": "Competitive achievement goals",
          "social_alienation": "Social alienation",
          "moral_disengagement": "Moral disengagement",
          "empathy": "Empathy",
          "self_control": "Self-control"}
COVS = {"Gender": "cov_gender", "Schoollocation": "cov_school_location",
        "Grade": "cov_grade", "Onlychildstatus": "cov_only_child"}


def fetch() -> dict:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, url in FILES.items():
        p = RAW_DIR / name
        if not p.exists():
            r = requests.get(url, headers=UA, timeout=300)
            r.raise_for_status()
            p.write_bytes(r.content)
        out[name] = p
    return out


def main() -> None:
    paths = fetch()
    d = pd.read_csv(paths["data.csv"])
    dic = pd.read_excel(paths["dict.xlsx"])
    assert d.shape == (1883, 112) and d["ID"].is_unique
    assert set(dic["Variable Name"]) == set(d.columns) and dic["Variable Name"].is_unique
    role = dict(zip(dic["Variable Name"], dic["Variable Role"]))
    items = {k: list(dic.loc[(dic["Construct"] == c) & (dic["Variable Role"] == "Item response"),
                             "Variable Name"]) for k, c in TABLES.items()}
    comps = [c for c, r in role.items() if r in ("Composite score", "Subscale score")]
    allitems = [c for v in items.values() for c in v]
    accounted = {"ID"} | set(COVS) | set(allitems) | set(comps)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    # every composite = mean of the items its Derivation lists
    der = dict(zip(dic["Variable Name"], dic["Derivation / Source"]))
    for c in comps:
        cols, groups = [], []
        for a, b in re.findall(r"(\w+)-(\w+)", str(der[c])):
            pa, na = re.fullmatch(r"(.*?)(\d+)", a).groups()
            pb, nb = re.fullmatch(r"(.*?)(\d+)", b).groups()
            assert pa == pb, (c, a, b)
            g = [f"{pa}{i}" for i in range(int(na), int(nb) + 1)]
            assert set(g) <= set(allitems), (c, g)
            cols += g
            groups.append(g)
        assert cols, (c, der[c])
        diff = (d[cols].mean(axis=1) - d[c]).abs().max()
        if diff > 1e-6 and len(groups) > 1:   # overall score = mean of the subscale means
            diff = (pd.concat([d[g].mean(axis=1) for g in groups], axis=1).mean(axis=1)
                    - d[c]).abs().max()
        print(f"  [skip] {c}: composite (mean over {len(cols)} items; max |diff| {diff:.2g})")
        assert diff < 1e-6, (c, diff)
    vals = d[allitems]
    assert vals.isin(range(1, 6)).all().all(), "non-integer or out-of-range item cell"
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in items.items():
        name = P + k
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in its}
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
    assert total == int(vals.notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
