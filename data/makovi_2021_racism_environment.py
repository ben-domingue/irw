#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8589981
# DOI: 10.1038/s41598-021-00329-z
#   "The effects of ideological value framing and symbolic racism on
#   pro-environmental behavior" (Makovi & Kasak-Gliboff, 2021), Scientific
#   Reports 11:22189.
# Data: the article's own supplementary dataset, 41598_2021_329_MOESM2_ESM.csv
#       (1,582 x 66, one row per first-wave respondent), fetched from the
#       Europe PMC supplementaryFiles zip. The zip also holds MOESM1 (SI PDF,
#       incl. the full Qualtrics survey text of both data collections) and
#       MOESM3 (the authors' R script). The paper's Data Availability also
#       points at osf.io/7cxe9 (pilot data); not needed here.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: shipped (itemtext_output/<table>__items.csv, built by
#   automated_finding/itemtext_verification/make_itemtext_makovi_2021.py).
#   Label levels checked: the CSV has no variable labels (column names are
#   positional, rscale_1..11 / escale_1..7), but the cells hold the response
#   option labels verbatim. The stems are in MOESM1 "Survey First Data
#   Collection" (Symbolic Racism Scale, Environmental Concern Scale, Risk - ...
#   blocks), whose option lists match the data's labels item for item,
#   including two survey typos ("Neither agree not disagree" on item 10 only,
#   "Pushing way to slowly").
#
# Sample: US MTurk workers (CloudResearch-approved, pre-classified by
# TurkPrime as liberal or conservative), first data collection, N = 1,582.
# The CSV's first (unnamed) column is a row number 1..1582 and is used as id.
# No MTurk IDs, zip codes or free text in the file.
#
# Tables (resp coded low -> high on the printed dimension; option order is
# reversed relative to the survey where the survey printed "Strongly agree"
# first):
#   makovi_2021_symbolic_racism       11 items rscale_1..11 (Symbolic Racism
#       Scale, as printed). Agree items 1-5 (Strongly disagree .. Strongly
#       agree); rscale_4 1-4 (Not at all .. Very responsible); rscale_6 1-5
#       (Pushing way to slowly .. Pushing way too fast); rscale_7 1-5 (None ..
#       All of the racial tension); rscale_11 1-5 (A lot of negative change ..
#       A lot of positive change). Shipped as administered, not reverse-keyed.
#       The authors' rscore is a rescaled composite and is skipped. Note its
#       weights reverse items 3 and 9 but not the reverse-worded item 8 ("Black
#       people generally do not complain as much as they should"), whose own
#       correlation with conservatism is -0.50; the shipped responses are raw,
#       so this affects only the authors' composite.
#   makovi_2021_environmental_concern 8 items: escale_1..7 + air_polluted, all
#       4-point. escale_1-5 coded 1-4 in printed order (Not concerned at all ..
#       Very concerned; Not at all .. Very willing; Not at all .. Very
#       dangerous); escale_6, escale_7, air_polluted Strongly disagree=1 ..
#       Strongly agree=4. air_polluted ("Air pollution is an issue in the area
#       where you live") is the 8th question printed in the survey's
#       Environmental Concern Scale block; the authors' escore uses
#       escale_1..7 only (escale_6 reversed; verified by regression below), so
#       it is kept as administered and flagged here.
#   makovi_2021_environmental_risk    4 items white.risk, black.risk,
#       poor.risk, self.risk ("<group>'s lives are negatively impacted by
#       environmental issues"), Strongly disagree=1 .. Strongly agree=4.
#
# Everything from the second data collection (treatment, donation, passage
# ratings t.*, risk.fam etc.) is post-treatment and only exists for 1,153
# returners; skipped with reasons below. No imputation possible (all cells are
# text labels, every label mapped exactly); no exact-duplicate rows.

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8589981/supplementaryFiles"
FNAME = "41598_2021_329_MOESM2_ESM.csv"

AGREE5 = {"Strongly disagree": 1, "Disagree": 2, "Neither agree nor disagree": 3,
          "Agree": 4, "Strongly agree": 5}
AGREE5_TYPO = {**{k: v for k, v in AGREE5.items() if v != 3},
               "Neither agree not disagree": 3}
AGREE4 = {"Strongly disagree": 1, "Disagree": 2, "Agree": 3, "Strongly agree": 4}

SR = {
    "rscale_1": AGREE5, "rscale_2": AGREE5, "rscale_3": AGREE5,
    "rscale_4": {"Not at all responsible": 1, "A little responsible": 2,
                 "Somewhat responsible": 3, "Very responsible": 4},
    "rscale_5": AGREE5,
    "rscale_6": {"Pushing way to slowly": 1, "Pushing a bit slow": 2,
                 "Pushing at the right pace": 3, "Pushing a bit fast": 4,
                 "Pushing way too fast": 5},
    "rscale_7": {"None of the racial tension": 1, "A little of the racial tension": 2,
                 "About half of the racial tension": 3,
                 "Most of the racial tension": 4, "All of the racial tension": 5},
    "rscale_8": AGREE5, "rscale_9": AGREE5, "rscale_10": AGREE5_TYPO,
    "rscale_11": {"A lot of negative change": 1, "A little negative change": 2,
                  "No change": 3, "A little positive change": 4,
                  "A lot of positive change": 5},
}
CONCERN = {"Not concerned at all": 1, "Somewhat unconcerned": 2,
           "Somewhat concerned": 3, "Very concerned": 4}
WILLING = {"Not at all willing": 1, "Somewhat willing": 2, "Mostly willing": 3,
           "Very willing": 4}
DANGER = {"Not at all dangerous": 1, "Slightly dangerous": 2,
          "Somewhat dangerous": 3, "Very dangerous": 4}
EC = {"escale_1": CONCERN, "escale_2": WILLING, "escale_3": WILLING,
      "escale_4": DANGER, "escale_5": DANGER, "escale_6": AGREE4,
      "escale_7": AGREE4, "air_polluted": AGREE4}
RISK = {c: AGREE4 for c in ["white.risk", "black.risk", "poor.risk", "self.risk"]}

TABLES = {
    "makovi_2021_symbolic_racism": SR,
    "makovi_2021_environmental_concern": EC,
    "makovi_2021_environmental_risk": RISK,
}

COV = {
    "age": "cov_age",
    "gender": "cov_gender",            # Female / Non-Female (as deposited)
    "race": "cov_race",                # White / Non-White (as deposited)
    "hisp.lat": "cov_hispanic",
    "education": "cov_education",
    "income": "cov_income",            # 2019 household income quintile label
    "politics": "cov_ideology_turkprime",
    "self.ideo": "cov_ideology_self",
}

SKIP = {
    "Unnamed: 0": "row number, becomes id",
    "con.enviro": "perceived concern of most conservatives about the environment (judgement about others, single item)",
    "lib.enviro": "perceived concern of most liberals about the environment (judgement about others, single item)",
    "con.race": "perceived concern of most conservatives about racial discrimination (single item)",
    "lib.race": "perceived concern of most liberals about racial discrimination (single item)",
    "if.moderate": "follow-up liberal/conservative choice asked only of 61 self-described moderates",
    "time.x": "first-survey duration in minutes (whole survey, not per item)",
    "escore": "authors' rescaled Environmental Concern composite",
    "rscore": "authors' rescaled Symbolic Racism composite",
    "agegroup": "binned copy of age",
    "p.consistent": "derived: TurkPrime vs self-reported ideology agreement",
    "norm.enviro": "second data collection (post-treatment), returners only",
    "norm.race": "second data collection (post-treatment), returners only",
    "returned": "second-collection participation flag",
    "donation": "second-collection outcome (tokens donated)",
    "EJ.effect": "second-collection rating of Earthjustice, returners only",
    "EJ.ideo": "second-collection rating of Earthjustice, returners only",
    "t.race": "experimental treatment arm (second collection)",
    "t.bias": "second-collection passage rating, single item",
    "t.credible": "second-collection passage rating, single item",
    "t.politics": "second-collection passage rating, single item",
    "t.tone": "second-collection passage rating, single item",
    "t.hope": "second-collection passage rating, single item",
    "risk.fam": "second-collection passage rating, single item",
    "risk.com": "second-collection passage rating, single item",
    "fam.relate": "second-collection passage rating, single item",
    "fam.dinner": "second-collection passage rating, single item",
    "num_failures": "second-collection comprehension-check failures",
    "treatment": "experimental treatment arm (second collection)",
    "time.y": "second-survey duration in minutes",
    "rtreat": "experimental treatment arm (second collection)",
    "rcorrect": "second-collection manipulation check",
    "ptreat": "experimental treatment arm (second collection)",
    "donated": "second-collection outcome (donated anything)",
    "t.align": "experimental treatment arm (second collection)",
}


def fetch() -> pd.DataFrame:
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_csv(io.BytesIO(z.read(FNAME)))


def main() -> None:
    d = fetch()
    assert d.shape == (1582, 66), d.shape
    assert (d["Unnamed: 0"] == np.arange(1, 1583)).all()
    assert len(TABLES) == len(set(TABLES))

    # books
    item_cols = [c for t in TABLES.values() for c in t]
    assert len(item_cols) == len(set(item_cols))
    accounted = set(item_cols) | set(COV) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert not d.drop(columns=["Unnamed: 0"]).duplicated().any()

    # every label maps exactly; no missing item cells
    num = {}
    for c in item_cols:
        m = {**SR, **EC, **RISK}[c]
        assert d[c].notna().all(), c
        bad = set(d[c]) - set(m)
        assert not bad, (c, bad)
        num[c] = d[c].map(m)
    num = pd.DataFrame(num)

    # escore = rescaled mean of escale_1..7 with escale_6 reversed (air_polluted not in it)
    X = num[[f"escale_{i}" for i in range(1, 8)]].copy()
    X["escale_6"] = 5 - X["escale_6"]
    pred = (X.mean(axis=1) - 1) / 3
    assert (pred - d["escore"]).abs().max() < 0.01

    out = pd.DataFrame({"id": d["Unnamed: 0"].astype(int)})
    for src, dst in COV.items():
        out[dst] = d[src]
    cov_cols = list(COV.values())
    out = pd.concat([out, num], axis=1)

    for name, items in TABLES.items():
        t = out.melt(id_vars=["id"] + cov_cols, value_vars=list(items),
                     var_name="item", value_name="resp").dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert set(t["item"]) == set(items)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100

        pv = {i: set(m.values()) for i, m in items.items()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
