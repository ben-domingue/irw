#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216266
# DOI: 10.1371/journal.pone.0216266
# Paper: Mee S, Bunney BG, Fujimoto K, Penner J, Seward G, Crowfoot K, Bunney WE,
#   Reist C (2019). A study of psychological pain in substance use disorder and
#   its relationship to treatment outcome. PLoS ONE 14(11): e0216266.
# Data: PLOS SI S1 File (journal.pone.0216266.s001, .xlsx, one sheet): 289
#   adult outpatients of a community substance-use treatment programme (the
#   Gary Center SACS, La Habra, California), intake assessments 2011-2013, from
#   a retrospective chart review; one row per patient x 104 columns.
# License: CC0 1.0 (PLOS SI, as recorded in the leads file).
# Codebook: none; scales from the paper's Assessment section, codes from
#   Table 1's counts.
#
# Worked from the cleaned leads list (leads/plos_leads_2026-10-30.csv); held
# 2026-11-10 by overnight lane A (not built), ruled ship by Ben 2026-11-11 with
# every non-integer cell dropped.
#
# FOUR tables, intake (w1) item columns as named in the deposit:
#   mee_2019_mbp  Mee-Bunney Psychological Pain Assessment Scale, 10 items
#     (the deposit numbers them 1-5, 10, 11, 13-15), 1-5.
#   mee_2019_bai  Beck Anxiety Inventory, 21 items, 0-3.
#   mee_2019_bdi  Beck Depression Inventory, 21 items, 0-3.
#   mee_2019_bhs  Beck Hopelessness Scale, 20 items, 0/1 (as deposited; the
#     deposit's own score bhsscore is the plain item sum, so these are keyed).
#
# DATA NOTE -- NON-INTEGER CELLS DROPPED: 1,374 of 20,808 item cells carry
#   undocumented non-integer values: half points (1.5, 2.5, 0.5), which may be
#   a mark between two boxes or an average, and mean-substitution fractions
#   (e.g. MBP 2.4747, BHS 0.5339 -- the same value down a column, i.e. a
#   column mean), which on BHS fill whole scales for some patients. Every
#   non-integer cell is dropped; integer cells ship as deposited. Per scale:
#   MBP 63 cells / 39 patients, BAI 271 / 39, BDI 318 / 54, BHS 722 / 46.
#
# Checks against the paper: N = 289; age by sex 32.8 (10.9) / 34.7 (10.1),
#   ethnicity counts 100/159/12/7/2/9, completion 68 / dropout 221, MBP mean
#   23.57 (8.87) (= the deposit's mbpscorews), BAI 11.73 vs 11.98, BHS 4.78 vs
#   4.8, and Cronbach's alpha MBP .90 / BDI .939 / BHS .876 / BAI .958 (paper
#   .902 / .941 / .876 / .958) all reproduce. Two do not: the paper's Table 1
#   gives 212 males / 77 females, the deposit 188 / 101 (sex code 1 / 2, whose
#   age means match the paper's males / females exactly); and Table 2 gives a
#   BDI mean of 8.54 (6.60) where the deposit's items and its own bdiscore give
#   17.20 (12.95). Read as slips in the paper, since everything computed from
#   the items reproduces, but recorded here.
#
# Not shipped: the scale totals (mbpscore, mbpscorews, baiscore, bdiscore,
#   bhsscore, mbpscorehilow), drug-screen flags, relapse counts and test
#   counts, suicide ideation/attempt codes (undocumented codes), treatment
#   process codes, and filter_$ (constant 1).
# Covariates: age, sex (1 male / 2 female, by the age means above), ethnicity
#   (codes matched to Table 1 counts: 1 Caucasian 100, 2 Hispanic 159, 3 Black
#   12, 4 Pacific Islander 2, 5 Asian 7, 6 other 9), completed treatment
#   (pp_complete_dich 1 = completed 68, 2 = dropped out 221).
# `id` = participant_id, the chart code the study assigned (e.g. 015-0057).
#
# Item text: NOT SHIPPED. Item numbers only in the deposit; BDI/BAI/BHS are
#   Pearson-copyrighted and the MBP is not reproduced in the paper.

import os
import sys
from io import BytesIO

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0216266.s001"
RAW = os.environ.get("MEE2019_RAW")

SCALES = [  # prefix, table, n items, permitted values
    ("mbp", "mee_2019_mbp", 10, range(1, 6)),
    ("bai", "mee_2019_bai", 21, range(0, 4)),
    ("bdi", "mee_2019_bdi", 21, range(0, 4)),
    ("bhs", "mee_2019_bhs", 20, range(0, 2)),
]
ETH = {1: "Caucasian", 2: "Hispanic", 3: "Black", 4: "Pacific Islander", 5: "Asian", 6: "other"}


def load():
    if RAW:
        return pd.read_excel(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content))


def main():
    d = load()
    assert d.shape == (289, 104), d.shape
    assert d["participant_id"].is_unique
    assert d["ethnicity"].value_counts().to_dict() == {2: 159, 1: 100, 3: 12, 6: 9, 5: 7, 4: 2}
    assert d["pp_complete_dich"].value_counts().to_dict() == {2: 221, 1: 68}
    d["id"] = d["participant_id"]
    d["cov_age"] = d["age"].astype(int)
    d["cov_sex"] = d["sex"].map({1: "male", 2: "female"})
    d["cov_ethnicity"] = d["ethnicity"].map(ETH)
    d["cov_completed_treatment"] = d["pp_complete_dich"].map({1: 1, 2: 0})
    covs = ["cov_age", "cov_sex", "cov_ethnicity", "cov_completed_treatment"]
    assert d[covs].notna().all().all()
    for prefix, name, n, values in SCALES:
        items = [c for c in d.columns if c.startswith(prefix + "_w1_")]
        assert len(items) == n, (prefix, len(items))
        x = d[items]
        assert x.notna().all().all()
        nonint = x != x.round()
        print(f"{name}: dropping {int(nonint.sum().sum())} non-integer cells "
              f"({int(nonint.any(axis=1).sum())} patients)")
        long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"] == long["resp"].round()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(values), (name, sorted(set(long["resp"])))
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        pv = {i: set(values) for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        report = irw_validate.validate_frame(long, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    main()
