#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IDNB1Z
# DOI: 10.1111/padm.70091
#   Wang, X. (C.), Perry, J. L., Wang, Y., Chen, D., & Liu, B. (2026). Inspired to serve:
#   Exposure to moral models to enhance public service motivation. Public Administration.
# Data: Harvard Dataverse 10.7910/DVN/IDNB1Z (Wang, Perry, Wang, Chen, Liu; 2026-08-20).
#       "study 1_data.sav" (file 14152631, format=original) -- recall experiment, 131
#       Chinese public employees (condition 0 control / 1 moral-model recall).
#       "study 2_data.sav" (file 14152632) -- field survey, 217 trainees from two
#       universities' public-sector training programmes.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Both .sav files carry an English stem for every item at the
#   variable-label level (psm_1 "I'm interested in making public programs that are
#   beneficial for my country ...") and the anchors as value labels (1 strongly disagree
#   .. 6 strongly agree; 1 not at all .. 6 very much). Not shipped because the study was
#   administered in Chinese and the deposit has no Chinese wording, so it would be a
#   translated_substitute fallback; the English is recoverable from the labels.
#
# Tables (1-6 throughout, as the value labels define):
#   wang_2026_psm              psm_1-psm_18, both studies (348 = 131 + 217). Same 18
#                              items, same labels and value labels in both files (asserted).
#   wang_2026_moral_elevation  15 items, both studies. Study 2 orders the items differently;
#                              its columns are mapped onto Study 1's codes by exact variable-
#                              label match (asserted one-to-one, value labels equal), so
#                              item = the Study 1 header.
#   wang_2026_pse              pse_1-3 public service self-efficacy (Study 1)
#   wang_2026_social_desirability soc_des_1-5 (Study 1)
#   wang_2026_panas_pa         pa_1-5 (Study 1)
#   wang_2026_panas_na         na_1-5 (Study 1)
#   wang_2026_moral_exposure   mor_ex_1-3 (Study 2; exposure to moral models)
#   wang_2026_cognitive_load   cogload_1-3 (Study 2)
# Skipped: Study 1 mcheck_1-3 and ma_check (manipulation check items and their mean); all
#   composite means (pa, na, soc_des, psf, mor_ele, psm, psm_d1-4, psm_p1-4, mor_ex, cogload).
# id: "s<study>_<row>" (the files carry no identifier; ids are prefixed so the two samples
#   cannot collide). cov_study = 1/2.
# treat: Study 1 condition (1 = moral-model recall, 0 = control); missing for Study 2.
# Covariates: cov_age, cov_sex (0 female, 1 male), cov_education (the value-label text, since
#   the two files code education differently), cov_tenure (years), cov_university (Study 2's
#   "school", 1/2).

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "idnb1z"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILES = {"study1.sav": "https://dataverse.harvard.edu/api/access/datafile/14152631?format=original",
         "study2.sav": "https://dataverse.harvard.edu/api/access/datafile/14152632?format=original"}
P = "wang_2026_"
PSM = [f"psm_{i}" for i in range(1, 19)]
ME = [f"mor_ele_{i}" for i in range(1, 16)]
S1_ONLY = {"pse": [f"pse_{i}" for i in range(1, 4)],
           "social_desirability": [f"soc_des_{i}" for i in range(1, 6)],
           "panas_pa": [f"pa_{i}" for i in range(1, 6)],
           "panas_na": [f"na_{i}" for i in range(1, 6)]}
S2_ONLY = {"moral_exposure": [f"mor_ex_{i}" for i in range(1, 4)],
           "cognitive_load": [f"cogload_{i}" for i in range(1, 4)]}
COMPOSITES = {"pa", "na", "soc_des", "psf", "mor_ele", "psm", "psm_d1", "psm_d2", "psm_d3",
              "psm_d4", "psm_p1", "psm_p2", "psm_p3", "psm_p4", "mor_ex", "cogload", "ma_check"}


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
    a, ma = pyreadstat.read_sav(str(paths["study1.sav"]))
    b, mb = pyreadstat.read_sav(str(paths["study2.sav"]))
    assert a.shape == (131, 70) and b.shape == (217, 52)
    la, lb = ma.column_names_to_labels, mb.column_names_to_labels
    va, vb = ma.variable_value_labels, mb.variable_value_labels
    for c in PSM:
        assert la[c] == lb[c] and va[c] == vb[c], c
    inv = {la[c].strip(): c for c in ME}
    me_map = {c: inv[lb[c].strip()] for c in ME}           # study-2 code -> study-1 code
    assert sorted(me_map.values()) == sorted(ME)
    for c2, c1 in me_map.items():
        assert va[c1] == vb[c2], (c2, c1)
    mcheck = ["mcheck_1", "mcheck_2", "mcheck_3"]
    cov1 = ["age", "sex", "edu", "tenure", "condition"]
    cov2 = ["age", "sex", "edu", "tenure", "school"]
    acc1 = set(PSM) | set(ME) | {c for v in S1_ONLY.values() for c in v} | set(mcheck) \
        | set(cov1) | (COMPOSITES & set(a.columns))
    acc2 = set(PSM) | set(ME) | {c for v in S2_ONLY.values() for c in v} | set(cov2) \
        | (COMPOSITES & set(b.columns))
    assert acc1 == set(a.columns), set(a.columns) ^ acc1
    assert acc2 == set(b.columns), set(b.columns) ^ acc2
    print("  [skip] mcheck_1-3, ma_check: Study 1 manipulation check")
    print(f"  [skip] composites: {sorted(COMPOSITES - {'ma_check'})}")
    b = b.rename(columns=me_map)

    def prep(x, m, study):
        x = x.reset_index(drop=True).copy()
        x.insert(0, "id", [f"s{study}_{i + 1:03d}" for i in range(len(x))])
        x["cov_study"] = study
        x["cov_education"] = x["edu"].map(m.variable_value_labels["edu"])
        assert x["cov_education"].notna().all()
        x = x.rename(columns={"age": "cov_age", "sex": "cov_sex", "tenure": "cov_tenure"})
        return x
    a = prep(a, ma, 1).rename(columns={"condition": "treat"})
    b = prep(b, mb, 2).rename(columns={"school": "cov_university"})
    d = pd.concat([a, b], ignore_index=True)
    assert d["id"].is_unique
    d["treat"] = d["treat"].astype("Int64")
    d["cov_sex"] = d["cov_sex"].astype("Int64")
    d["cov_university"] = d["cov_university"].astype("Int64")
    covs = ["cov_study", "cov_age", "cov_sex", "cov_education", "cov_tenure", "cov_university"]
    tables = {"psm": PSM, "moral_elevation": ME, **S1_ONLY, **S2_ONLY}
    names = [P + k for k in tables]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in tables.items():
        name = P + k
        t = d.melt(id_vars=["id", "treat"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 7)).all(), name
        t["resp"] = t["resp"].astype(int)
        cols = ["id", "item", "resp"] + (["treat"] if t["treat"].notna().any() else []) + \
            [c for c in covs if t[c].notna().any()]
        t = t[cols].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 7)) for i in its}
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
    allits = [c for v in tables.values() for c in v]
    assert total == int(d[allits].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
