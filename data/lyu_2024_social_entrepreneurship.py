#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10978997
# DOI: 10.1038/s41598-024-58060-4
#   "Social entrepreneurial intention among university students in China"
#   (Lyu, Al Mamun, Yang & Aziz, 2024), Scientific Reports 14:7362.
# Data: the article's supplementary files from the Europe PMC supplementaryFiles
#       zip: 41598_2024_58060_MOESM2_ESM.csv (684 x 58 raw responses, one row per
#       respondent: 6 demographic codes, 42 items, a `Random` column and 9
#       construct means) and MOESM1_ESM.docx (Table S1 "Survey Instrument": code ->
#       English item wording for every item).
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Item text: shipped (itemtext_output/<table>__items.csv, built by
#   automated_finding/itemtext_verification/make_itemtext_lyu_2024.py).
#   Levels checked: the CSV has no variable/value labels (plain headers such as
#   RTP1); MOESM1 Table S1 keys every one of the 42 item headers to its wording
#   by the same code. Anchors: Methods gives "strongly disagree" (1) and
#   "strongly agree" (5) only. The administration language is not stated in the
#   paper; Table S1 is in English.
#
# Sample: 684 students and graduates of five universities in Southern China,
# online survey June-July 2022.
#
# Tables (all items 1-5 agreement; one table per construct, as in the paper's
# measurement model):
#   lyu_2024_rtp  risk-taking propensity, RTP1-4
#   lyu_2024_sef  self-efficacy, SEF1-5
#   lyu_2024_nfa  need for achievement, NFA1-5
#   lyu_2024_pvs  perceived values on sustainability, PVS1-5
#   lyu_2024_org  opportunity recognition competency, ORG1-4
#   lyu_2024_ate  attitude towards entrepreneurship, ATE1-5
#   lyu_2024_sun  subjective norms, SUN1-4
#   lyu_2024_pbc  perceived behavioural control, PBC1-5
#   lyu_2024_sei  social entrepreneurial intention, SEI1-5
#
# Skipped columns: the nine construct means (RTP ... SEI; each equals the mean of
# its items exactly, asserted) and `Random` (a continuous 41-58 variable that is
# not a questionnaire item; it appears to be a generated marker variable for the
# full-collinearity VIF test, paper Table 1).
#
# Duplicates: three pairs of adjacent rows (0-based 29/30, 193/194, 274/275) are
# identical on all 42 items AND all six demographics, differing only in
# `Random`; no other pair of respondents agrees on more than 36 of 42 items. They
# are treated as double submissions: the first row of each pair is kept, so 681
# respondents ship (paper N = 684). No missing cells, no fractional values, no
# straight-liners, no PII. Demographic codes are labelled from the paper's
# Table 2, whose counts match the code counts exactly (asserted).

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "lyu_2024_social_entrepreneurship"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10978997/supplementaryFiles"
FILES = ("41598_2024_58060_MOESM2_ESM.csv", "41598_2024_58060_MOESM1_ESM.docx")


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for n in FILES:
            (RAW_DIR / n).write_bytes(z.read(n))
    return p


CONSTRUCTS = {"RTP": 4, "SEF": 5, "NFA": 5, "PVS": 5, "ORG": 4,
              "ATE": 5, "SUN": 4, "PBC": 5, "SEI": 5}
TABLES = {f"lyu_2024_{k.lower()}": [f"{k}{i}" for i in range(1, n + 1)]
          for k, n in CONSTRUCTS.items()}

# Table 2 labels; the expected counts are Table 2's own n column.
DEMO = {
    "Gender": ("cov_gender", {1: "male", 2: "female"}, {1: 308, 2: 376}),
    "Education": ("cov_education", {1: "undergraduate student", 2: "graduate student",
                                    3: "doctoral student"}, {1: 576, 2: 87, 3: 21}),
    "HH_Income": ("cov_household_income_cny",
                  {1: "<2500", 2: "2501-5000", 3: "5001-7500", 4: "7501-10000",
                   5: "10001-12500", 6: ">12500"},
                  {1: 17, 2: 54, 3: 94, 4: 283, 5: 167, 6: 69}),
    "Age_Group": ("cov_age_group", {2: "18-22", 3: "23-26", 4: "27-30", 5: ">30"},
                  {2: 159, 3: 224, 4: 217, 5: 84}),
    "University": ("cov_university",
                   {1: "Fuzhou Institute of Technology", 2: "Guangxi Medical University",
                    3: "Hunan University", 4: "South China Normal University",
                    5: "South China Agricultural University"},
                   {1: 154, 2: 90, 3: 154, 4: 144, 5: 142}),
    "Subject": ("cov_subject", {1: "social science", 2: "natural science"},
                {1: 482, 2: 202}),
}
DUP_ROWS = [29, 30, 193, 194, 274, 275]


def main() -> None:
    fetch(FILES[1])
    d = pd.read_csv(fetch(FILES[0]), encoding="utf-8-sig")
    assert d.shape == (684, 58), d.shape
    items = [c for v in TABLES.values() for c in v]
    assert len(items) == len(set(items)) == 42
    means = list(CONSTRUCTS)
    # balance the books
    assert set(d.columns) == set(items) | set(DEMO) | set(means) | {"Random"}, \
        set(d.columns) ^ (set(items) | set(DEMO) | set(means) | {"Random"})
    for k in means:
        its = [c for c in items if c.startswith(k) and c[len(k):].isdigit()]
        assert np.allclose(d[its].mean(axis=1), d[k]), k
    print(f"  [skip] {len(means)} construct means {means}: each = mean of its items")
    print("  [skip] Random: generated dependent variable for the full-collinearity test")

    for c, (_, labels, counts) in DEMO.items():
        assert d[c].value_counts().to_dict() == counts, c
    assert d.notna().all().all()
    assert (d[items] % 1 == 0).all().all() and d[items].isin(range(1, 6)).all().all()
    assert (d[items].nunique(axis=1) > 1).all()

    # double submissions: identical items and demographics, adjacent rows
    dup = d[items + list(DEMO)].duplicated(keep=False)
    assert list(d.index[dup]) == DUP_ROWS, list(d.index[dup])
    assert list(d.index[d[items].duplicated(keep=False)]) == DUP_ROWS
    X = d[items].to_numpy()
    A = (X[:, None, :] == X[None, :, :]).sum(2)
    np.fill_diagonal(A, 0)
    m = dup.to_numpy()
    agree = int(A[~(m[:, None] & m[None, :])].max())
    assert agree <= 36, agree
    print(f"  [drop] second row of pairs 29/30, 193/194, 274/275 (0-based): identical on "
          f"all 42 items and 6 demographics; max agreement among other pairs = {agree}/42")

    d.insert(0, "id", np.arange(1, len(d) + 1))
    d = d[~d[items + list(DEMO)].duplicated(keep="first")].reset_index(drop=True)
    assert len(d) == 681
    cov_cols = []
    for c, (newc, labels, _) in DEMO.items():
        d[newc] = d[c].map(labels)
        assert d[newc].notna().all()
        cov_cols.append(newc)

    assert len(TABLES) == len(set(TABLES))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                   var_name="item", value_name="resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
