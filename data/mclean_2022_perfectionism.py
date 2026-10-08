#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/UTBOEQ
# DOI: 10.7910/DVN/UTBOEQ (dataset; the record cites no paper)
#   McLean, Michelle (2022). "Personality, academic behaviour, and mental health variables
#   from college student sample" [data set], Harvard Dataverse.
# Data: 472TotalData.sav (file 5014345): 123 undergraduates (a large university in Western
#       Canada, 2015-16) x 178 columns. Variable labels name each scale on its first item;
#       value labels give every item's anchors.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Levels checked: .sav variable labels (scale name on the first
#   item of each block only, e.g. "Rosenburg Self Esteem Scale"; no stems) and value labels
#   (anchors on every item). Option text alone is not shipped (#1770); the stems are in the
#   published instruments.
#
# Tables (item codes = the .sav names; values as stored, anchors per the value labels):
#   mclean_2022_mps        SOP/OOP/SPP 1-15  1-7  Multidimensional Perfectionism Scale, short
#                          form. OOP2/5/6/14/15 carry REVERSED value labels (1 = strongly
#                          agree .. 7 = strongly disagree), i.e. are stored reverse-scored.
#   mclean_2022_psps       PSP1-3, NDPI4-6, NDCI7-9  1-7  Perfectionistic Self-Presentation
#                          Scale, short form; PSP3, NDPI6, NDCI9 have reversed value labels.
#   mclean_2022_avpd       AVPD1-7  0/1 (not true / true)  PDQ-4 avoidant personality disorder
#   mclean_2022_rses       HSE1/3/4/7/10, LSE2/5/6/8/9  1-4  Rosenberg Self-Esteem Scale; the
#                          LSE items have reversed value labels (1 = strongly agree).
#   mclean_2022_dass21     stress/anxiety/depress 1-21  0-3  DASS-21
#   mclean_2022_pals       apprch1-5, avd6-11, nvty12-16, cheat17-19, lwach20-25, SH33-39
#                          1-5  Patterns of Adaptive Learning Scales subscales
#   mclean_2022_help_seeking  peerHS26-27, profHS28-30, avdHS31-32  1-5  threat of peer /
#                          professor help seeking and avoidance of help seeking (Ryan &
#                          Pintrich)
#   "Reversed value labels" means the stored code runs against the wording; nothing is
#   recoded here, so resp follows the stored code and its label.
# Skipped: all *tot scores; time-2 DASS totals; the 13 stressful-academic-event items
#   (sae1-13: codes derived by the authors from free-text counts in sae*text) and their
#   free text; major (free text); start/end timestamps and completion times; string
#   duplicates of coded covariates (ageSTR, genderSTR, eslSTR).
# Covariates: cov_age_band (age: 1 = 22 or younger .. 5 = 38 or older), cov_gender (0/1;
#   genderSTR shows 0 = male, 1 = female), cov_esl (0/1), cov_year, cov_grade (last
#   assignment %), cov_term (1 Fall 2015, 2 Winter 2016), cov_complete (both time points).
# id = the file's id.

import re
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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "mclean_2022"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/5014345?format=original"

TABLES = {
    "mclean_2022_mps": (r"(SOP|OOP|SPP)\d+", range(1, 8)),
    "mclean_2022_psps": (r"(PSP|NDPI|NDCI)\d+", range(1, 8)),
    "mclean_2022_avpd": (r"AVPD\d+", range(0, 2)),
    "mclean_2022_rses": (r"(HSE|LSE)\d+", range(1, 5)),
    "mclean_2022_dass21": (r"(stress|anxiety|depress)\d+", range(0, 4)),
    "mclean_2022_pals": (r"(apprch|avd|nvty|cheat|lwach|SH)\d+", range(1, 6)),
    "mclean_2022_help_seeking": (r"(peerHS|profHS|avdHS)\d+", range(1, 6)),
}
COVS = {"age": "cov_age_band", "gender": "cov_gender", "esl": "cov_esl", "year": "cov_year",
        "grade": "cov_grade", "termT1": "cov_term", "complete": "cov_complete"}
SKIP = re.compile(r"^(.*tot(T2)?|sae\d+(text)?|major|(start|end|time)T[12]|termT2|grade2|"
                  r"(age|gender|esl)STR)$")


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(fetch())
    assert d.shape == (123, 178), d.shape
    cols = {name: [c for c in d.columns if re.fullmatch(pat, c)] for name, (pat, _) in TABLES.items()}
    assert [len(v) for v in cols.values()] == [15, 9, 7, 10, 21, 32, 7], [len(v) for v in cols.values()]
    used = {"id"} | set(COVS) | {c for v in cols.values() for c in v}
    rest = [c for c in d.columns if c not in used]
    assert all(SKIP.match(c) for c in rest), [c for c in rest if not SKIP.match(c)]
    print(f"  skip {len(rest)} columns: totals, stressful-academic-event codes and free text, "
          "major, timestamps, string duplicates")
    g = d["gender"].notna()
    assert d.loc[g, "genderSTR"].eq(d.loc[g, "gender"].map({0: "male", 1: "female"})).all()
    assert d["id"].is_unique
    d["id"] = d["id"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if c != "cov_grade":
            d[c] = d[c].astype("Int64")
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (_, rng) in TABLES.items():
        its = cols[name]
        for c in its:  # value labels cover the permitted set
            assert set(meta.variable_value_labels[c]) == set(map(float, rng)), c
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
