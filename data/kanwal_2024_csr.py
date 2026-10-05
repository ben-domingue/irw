#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11490784
# DOI: 10.1016/j.heliyon.2024.e38987
#   "Corporate social responsibility: A Driver for green organizational climate
#   and workplace pro-environmental behavior" (Kanwal, Al Mamun, Wu, Bhatti &
#   Ali, 2024), Heliyon 10(19):e38987.
# Data: Heliyon supplementary files from the Europe PMC supplementaryFiles zip:
#       mmc1.csv (349 x 52 raw responses, one row per respondent) and mmc2.docx
#       (Table S1 "Survey Instrument": code -> item wording for every item;
#       Table S2: demographic profile, used to label the demographic codes).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary files.
#
# Item text: shipped (itemtext_output/<table>__items.csv, built by
#   automated_finding/itemtext_verification/make_itemtext_kanwal_2024.py).
#   Levels checked: the CSV has no variable/value labels (plain headers such as
#   CSRE1); mmc2.docx Table S1 keys every one of the 45 item headers to its English
#   wording by the same code (administered in English, per Methods 4.3). One
#   discrepancy, disclosed: Table S1 spells the green-shared-vision codes GRSV1-4,
#   the data GSRV1-4; item keeps the data's GSRVk, matched to S1's GRSVk by
#   number (the four are the only codes of that block either way). Table S1's
#   CSRN3 cell is cut off in the source ("... eco-design, "), shipped as cut.
#   Anchors: Methods gives only "1" = strong disagreement, "5" = strong agreement.
#
# Sample: 349 senior- and middle-level managers of medium and large
# manufacturing firms in Lahore, Pakistan (online Google Forms survey via the
# Lahore Chamber of Commerce and Industry).
#
# Tables (all items 1-5):
#   kanwal_2024_csr   perceived CSR, 26 items "based on the work of [23]": CSR
#                     towards employees (CSRE1-7), community (CSRC1-7),
#                     environment (CSRN1-8), customers (CSRU1-4); one table,
#                     as the paper takes the 26 items from one source scale
#                     (the validator's multi_scale warning is these four
#                     dimension prefixes)
#   kanwal_2024_goc   green organizational climate, GOCL1-9
#   kanwal_2024_gsv   green shared vision, GSRV1-4
#   kanwal_2024_wpeb  workplace pro-environmental behaviour, WPEB1-6
#
# Duplicates: two pairs of adjacent rows (file rows 262/263 and 339/340,
# 1-based after the header) carry identical answers on all 45 items while their
# demographics differ; no other pair of respondents agrees on more than 41 of
# 45. Two independent people matching on 45 five-point items is not chance, and
# which row of each pair is the real one cannot be told, so all four rows are
# dropped (345 respondents ship). No imputation (every cell an integer 1-5, no
# missing), no straight-liners, no PII. The demographic codes are labelled from
# Table S2, whose category counts match the code counts exactly (asserted).

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
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "kanwal_2024_csr"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11490784/supplementaryFiles"


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        for n in ("mmc1.csv", "mmc2.docx"):
            (RAW_DIR / n).write_bytes(z.read(n))
    return p


TABLES = {
    "kanwal_2024_csr": [f"CSRE{i}" for i in range(1, 8)] + [f"CSRC{i}" for i in range(1, 8)]
                       + [f"CSRN{i}" for i in range(1, 9)] + [f"CSRU{i}" for i in range(1, 5)],
    "kanwal_2024_goc": [f"GOCL{i}" for i in range(1, 10)],
    "kanwal_2024_gsv": [f"GSRV{i}" for i in range(1, 5)],
    "kanwal_2024_wpeb": [f"WPEB{i}" for i in range(1, 7)],
}

# Table S2 labels; the expected counts are S2's own N column.
DEMO = {
    "Gender": ("cov_gender", {1: "male", 2: "female"}, {1: 284, 2: 65}),
    "Age_Group": ("cov_age_group", {1: "18-25", 2: "26-35", 3: "36-45", 4: "46-55", 5: "56-65"},
                  {1: 26, 2: 163, 3: 99, 4: 49, 5: 12}),
    "Education": ("cov_education", {2: "bachelor", 3: "master", 4: "doctoral"},
                  {2: 173, 3: 111, 4: 65}),
    "Position": ("cov_position", {1: "senior management", 2: "middle management"},
                 {1: 81, 2: 268}),
    "Tenure": ("cov_tenure_years", {1: "<1", 2: "1-5", 3: "6-10", 4: "11-15", 5: "16-20"},
               {1: 12, 2: 160, 3: 152, 4: 12, 5: 13}),
    "Firm_Age": ("cov_firm_age_years", {2: "1-5", 3: "6-10", 4: "11-15", 5: "16-20", 6: ">20"},
                 {2: 5, 3: 46, 4: 176, 5: 88, 6: 34}),
    "Firm_Size": ("cov_firm_size", {1: "medium", 2: "large"}, {1: 227, 2: 122}),
}


def main() -> None:
    fetch("mmc2.docx")
    d = pd.read_csv(fetch("mmc1.csv"))
    assert d.shape == (349, 52), d.shape
    items = [c for v in TABLES.values() for c in v]
    assert len(items) == len(set(items)) == 45
    assert set(d.columns) == set(items) | set(DEMO), set(d.columns) ^ (set(items) | set(DEMO))

    for c, (_, labels, counts) in DEMO.items():
        assert d[c].value_counts().to_dict() == counts, c
        assert set(d[c]) <= set(labels), c

    # exact duplicate item vectors -> drop every member
    X = d[items].to_numpy()
    dup = d[items].duplicated(keep=False)
    assert sorted(d.index[dup]) == [261, 262, 338, 339], list(d.index[dup])
    n = len(X)
    agree = max(int((X[i] == X[j]).sum()) for i in range(n) for j in range(i + 1, n)
                if not (dup[i] and dup[j]))
    assert agree <= 41, agree
    print(f"  [drop] rows 261/262 and 338/339 (0-based): identical on all 45 items, "
          f"demographics differ; max agreement among other pairs = {agree}/45")

    d.insert(0, "id", np.arange(1, n + 1))
    d = d[~dup].reset_index(drop=True)
    cov_cols = []
    for c, (newc, labels, _) in DEMO.items():
        d[newc] = d[c].map(labels)
        cov_cols.append(newc)

    assert len(TABLES) == len(set(TABLES))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
        assert (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"])
        assert set(t["item"]) == set(its)
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in its}
        for i, s in pv.items():
            assert set(t.loc[t["item"] == i, "resp"]) <= s, (name, i)
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
