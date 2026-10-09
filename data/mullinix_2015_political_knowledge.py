#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/JC2QJ0
# DOI: 10.1007/s11109-015-9318-4
#   Mullinix, K. J. (2016). Partisanship and preference formation: competing motivations,
#   elite polarization, and issue importance. Political Behavior, 38(2), 383-411
#   (online 2015).
# Data: Harvard Dataverse 10.7910/DVN/JC2QJ0 (Mullinix, Kevin; 2018). Mullinix_PolBeh_Data.dta
#       (file 2711363, format=original) -- 3,098 US adults in two survey experiments
#       (sales-tax and Social Security issues, 10 conditions). Besides the experimental
#       outcomes it carries a four-item political knowledge battery: Veto (raw choice 1-6),
#       MajHouse (1-4), Constitu (1-4), SecState (open-ended name), each with a scored copy
#       CVeto / CMajHouse / CConstitu / CSecState (1 correct, 0 incorrect, blank = not
#       answered), and Pknow = their sum (asserted).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .dta has no variable or value labels at either level; the
#   question wording (the standard ANES-style veto-override / House-majority /
#   constitutionality / Secretary-of-State items) is not deposited.
#
# Table:
#   mullinix_2015_political_knowledge  Veto, MajHouse, Constitu, SecState; resp = the
#     deposit's scoring (1 correct, 0 incorrect). resp_raw = the option chosen for the three
#     closed items (each scored option is the single code the deposit marks correct: Veto 4,
#     MajHouse 2, Constitu 3 -- asserted); SecState is open-ended and gets no resp_raw.
# Skipped: the experimental outcomes (Sales*/SSA* support, importance, argument ratings,
#   contact and involvement checkboxes, recall), PartyKnow (an unscored party-knowledge
#   item whose key is not documented), Pknow and the derived indicators (involve, party2,
#   party3, ideo3, tandemgroup, competegroup).
# Covariates (codes as stored; no labels in the file): cov_pid7 (PIDrep), cov_ideology,
#   cov_education, cov_income, cov_race, cov_age (band), cov_gender, cov_condition (group,
#   1-10), cov_party_activities (PolActivites), cov_talk_politics (TalkPoli), cov_trust_gov,
#   cov_interest (InterestPol).
# id: row index (no identifier).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "jc2qj0"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/2711363?format=original"
NAME = "mullinix_2015_political_knowledge"
ITEMS = {"Veto": 4, "MajHouse": 2, "Constitu": 3, "SecState": None}
COVS = {"PIDrep": "cov_pid7", "Ideology": "cov_ideology", "Education": "cov_education",
        "Income": "cov_income", "Race": "cov_race", "Age": "cov_age", "Gender": "cov_gender",
        "group": "cov_condition", "PolActivites": "cov_party_activities",
        "TalkPoli": "cov_talk_politics", "TrustGov": "cov_trust_gov",
        "InterestPol": "cov_interest"}


def fetch() -> Path:
    p = RAW_DIR / "data.dta"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_dta(str(fetch()))
    assert d.shape == (3098, 56)
    score = {k: pd.to_numeric(d["C" + k].replace("", pd.NA)) for k in ITEMS}
    s = pd.DataFrame(score)
    assert (s.fillna(0).sum(axis=1) == d["Pknow"]).all()
    for k, key in ITEMS.items():
        if key:
            raw = pd.to_numeric(d[k].replace("", pd.NA))
            ok = raw.notna()
            assert ((raw[ok] == key) == (s.loc[ok, k] == 1)).all(), k
            assert (s[k].notna() == ok).all(), k
    skipped = sorted(set(d.columns) - set(ITEMS) - {"C" + k for k in ITEMS} - set(COVS))
    print(f"  [skip] {len(skipped)} columns: experimental outcomes, PartyKnow, Pknow, derived")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov = d[["id"] + list(COVS)].rename(columns=COVS)
    for c in COVS.values():
        cov[c] = pd.to_numeric(cov[c].replace("", pd.NA)).astype("Int64")
    covs = list(COVS.values())
    rows = []
    for k, key in ITEMS.items():
        x = pd.DataFrame({"id": d["id"], "item": k, "resp": s[k],
                          "resp_raw": pd.to_numeric(d[k].replace("", pd.NA)).astype("Int64")
                          if key else pd.NA})
        rows.append(x.dropna(subset=["resp"]))
    t = pd.concat(rows, ignore_index=True).merge(cov, on="id", validate="many_to_one")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert len(t) == int(s.notna().sum().sum()) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and set(t["item"]) == set(ITEMS)
    pv = {i: {0, 1} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
