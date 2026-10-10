#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/JHZDLR
# DOI: 10.3352/jeehp.2018.15.2
#   Babenko, O., Mosewich, A., Abraham, J., & Lai, H. (2018). Contributions of
#   psychological needs, self-compassion, leisure-time exercise, and achievement goals to
#   academic engagement and exhaustion of Canadian medical students. Journal of
#   Educational Evaluation for Health Professions, 15, 2.
# Data: Harvard Dataverse 10.7910/DVN/JHZDLR (Babenko, Mosewich, Abraham, Lai; 2018).
#       "Jeehp_15_2_raw data.xlsx" (file 3097345), Sheet1 -- 200 undergraduate medical
#       students (University of Alberta) x gender, age band, year in program, 19
#       achievement-goal items (pap/map/mav/pav), 16 OLBI-S items (engage/exh), 12 SCS-SF
#       items (sc), 12 basic-needs items (auto/compet/relat) and three Godin exercise
#       frequencies. The record lists the instruments: OLBI-S, Basic Psychological Needs
#       Scale, SCS-SF, Godin Leisure-Time Exercise Questionnaire, Achievement Goals
#       Instrument.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain xlsx (no variable or value labels); headers are positional
#   codes (engage_1, sc_4_RC). The wording is the published instruments' (OLBI-S;
#   Raes et al. 2011 SCS-SF; the basic-needs scale; the achievement goal questionnaire),
#   none of it deposited.
#
# Tables (response ranges as observed and as the instruments define them):
#   babenko_2018_olbi_engagement  engage_1-8, 1-4
#   babenko_2018_olbi_exhaustion  exh_1-8, 1-4
#   babenko_2018_scs_sf           sc_1-12, 1-5
#   babenko_2018_basic_needs      auto_1-4, compet_1-4, relat_1-4, 1-6
#   babenko_2018_achievement_goals pap_1-4 (performance-approach), map_1-4 (mastery-
#                                 approach), mav_1-7 (mastery-avoidance), pav_1-4
#                                 (performance-avoidance), 1-7, in the deposit's column order
# Reverse keying: the *_RC items are stored ALREADY reverse-scored (every _RC item correlates
#   positively with its block), kept as stored and named as the deposit names them.
# Skipped: exercise_mild/_mod/_str (Godin bout-frequency categories, not a scale).
# Covariates: cov_gender (0/1 as stored; undocumented), cov_age (band string), cov_year
#   (year in program, 1-4).
# id: row index (the file has no identifier).

import os
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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "jhzdlr"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/3097345?format=original"
P = "babenko_2018_"
COVS = {"gender": "cov_gender", "age": "cov_age", "year in program": "cov_year"}
SKIP = {"exercise_mild": "Godin frequency", "exercise_mod": "Godin frequency",
        "exercise_str": "Godin frequency"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Sheet1")
    assert d.shape == (200, 65)
    cols = list(d.columns)
    blk = lambda *pre: [c for c in cols if c.split("_")[0] in pre]  # noqa: E731
    tables = {"olbi_engagement": (blk("engage"), range(1, 5)),
              "olbi_exhaustion": (blk("exh"), range(1, 5)),
              "scs_sf": (blk("sc"), range(1, 6)),
              "basic_needs": (blk("auto", "compet", "relat"), range(1, 7)),
              "achievement_goals": (blk("pap", "map", "mav", "pav"), range(1, 8))}
    n = {k: len(v[0]) for k, v in tables.items()}
    assert n == {"olbi_engagement": 8, "olbi_exhaustion": 8, "scs_sf": 12, "basic_needs": 12,
                 "achievement_goals": 19}, n
    items = [c for v in tables.values() for c in v[0]]
    accounted = set(items) | set(COVS) | set(SKIP)
    assert accounted == set(cols), set(cols) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    for k in ("olbi_engagement", "olbi_exhaustion", "scs_sf"):   # the blocks with _RC items:
        assert (d[tables[k][0]].corr() > 0).all().all(), k       # already reversed, no r < 0
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d["cov_gender"] = d["cov_gender"].astype("Int64")
    covs = list(COVS.values())
    names = [P + k for k in tables]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, (its, rng) in tables.items():
        name = P + k
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
