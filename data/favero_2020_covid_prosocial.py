#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/1LIIDV
# DOI: 10.30636/jbpa.32.167
#   Favero, N., & Pedersen, M. J. (2020). How to encourage "Togetherness by Keeping Apart"
#   amid COVID-19? The ineffectiveness of prosocial and empathy appeals. Journal of
#   Behavioral Public Administration, 3(2).
# Data: Harvard Dataverse 10.7910/DVN/1LIIDV (Favero, Nathan; Pedersen, Mogens Jin).
#       covid19perceptions.dta (file 3829239, format=original) -- 1,503 US online
#       respondents (March 2020), randomised to a control or one of four information-cue
#       arms. Study_of_Coronavirus_COVID-19_Perceptions.qsf (file 3829236) is the Qualtrics
#       survey export: full item wording, response anchors and block intros.
#       analysis.do (file 3829238) is the authors' cleaning and analysis code.
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped for all three tables, from the deposit's own Qualtrics export (.qsf):
#   question/choice text and the Likert answer labels (motiv) or slider end labels
#   (socdist, attitude), plus each block's intro as instructions. Built by
#   automated_finding/itemtext_verification/make_itemtext_favero_2020.py. Label levels
#   checked: the .dta variable labels carry the stems too but are cut at 80 characters
#   (motiv1 "... - I am an empathetic"), and its value labels carry the motiv 1-5 anchors;
#   the sliders have no value labels in the .dta -- hence the .qsf.
#
# Tables (as administered; no reverse-scoring applied):
#   favero_2020_prosocial_motivation  motiv1-motiv5, 1-5 (strongly disagree .. strongly
#                                     agree). motiv1 is the empathy item ("I am an empathetic
#                                     person"); the authors' prosocial index is motiv2-5.
#   favero_2020_social_distancing     socdist1_1-socdist5_1, 0-10 slider (strongly disagree
#                                     .. strongly agree), "During the next few weeks..."; items
#                                     1 and 3 are the reverse-worded ones (authors' index
#                                     uses 10 - x for them).
#   favero_2020_covid_attitudes       attitude1_1-attitude4_1, 0-10 slider.
# Skipped: attention1, attention2_1, attention3_1 (attention checks); maxweeks0-4 (open
#   numeric answers, one per arm); sourcenews_1-6 and race_1-9 (select-all checkboxes);
#   party_3_TEXT (free text); Qualtrics metadata (dates, Status, Progress, Duration,
#   Finished, ResponseId, DistributionChannel, UserLanguage); duplicate (flags the repeat
#   respondent).
# Dropped: ResponseId R_1FJTuRyeH7msWDG, the same respondent's second submission (the
#   authors' do-file drops it).
# treat is not used: there are five arms. cov_arm = control / treatment1-4 as stored.
# Covariates (codes as stored; the .dta value labels via the covariate-label harvest):
#   cov_gender (-9 prefer not to answer, 1 male, 2 female, ...), cov_age (band 1-8),
#   cov_education (1-8), cov_party (1 Republican, 2 Democratic, 3 other), cov_follow_news
#   (1-4), cov_state, cov_employment (1-8), cov_employment_change, cov_essential_worker
#   (-9 unsure, 0, 1), cov_income (-9 prefer not to answer, 1-6), cov_arm.
# id: row index (ResponseId is a Qualtrics response key; not shipped).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "1liidv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/3829239?format=original"
P = "favero_2020_"
TABLES = {"prosocial_motivation": ([f"motiv{i}" for i in range(1, 6)], range(1, 6)),
          "social_distancing": ([f"socdist{i}_1" for i in range(1, 6)], range(0, 11)),
          "covid_attitudes": ([f"attitude{i}_1" for i in range(1, 5)], range(0, 11))}
COVS = {"gender": "cov_gender", "age": "cov_age", "edu": "cov_education", "party": "cov_party",
        "follownews": "cov_follow_news", "state": "cov_state", "employ": "cov_employment",
        "employchange": "cov_employment_change", "essentialworker": "cov_essential_worker",
        "income": "cov_income", "arm": "cov_arm"}
SKIP = (["attention1", "attention2_1", "attention3_1", "party_3_TEXT", "duplicate",
         "StartDate", "EndDate", "Status", "Progress", "Duration__in_seconds_", "Finished",
         "RecordedDate", "ResponseId", "DistributionChannel", "UserLanguage"]
        + [f"maxweeks{i}" for i in range(5)] + [f"sourcenews_{i}" for i in range(1, 7)]
        + [f"race_{i}" for i in range(1, 9)] + ["race__9"])
DROP_RESPONSE = "R_1FJTuRyeH7msWDG"


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
    assert d.shape == (1503, 60) and d["ResponseId"].is_unique
    items = [c for v in TABLES.values() for c in v[0]]
    accounted = set(items) | set(COVS) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    print(f"  [skip] {len(SKIP)} columns: attention checks, checkboxes, free text, metadata")
    assert (d["ResponseId"] == DROP_RESPONSE).sum() == 1
    d = d[d["ResponseId"] != DROP_RESPONSE].reset_index(drop=True)
    print(f"  dropped {DROP_RESPONSE} (repeat respondent's second submission)")
    for c in items + [c for c in COVS if c != "arm"]:
        d[c] = pd.to_numeric(d[c].replace("", pd.NA), errors="raise")
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_arm":
            d[c] = d[c].astype("Int64")
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, (its, rng) in TABLES.items():
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
