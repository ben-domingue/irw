#!/usr/bin/env python3
# Source: https://zenodo.org/records/7547098
# DOI: 10.1016/j.ijdrr.2024.104448
#   Amerigo, M., Talayero, F., Garcia, J. A., Perez-Lopez, R., Poggio, L.,
#   Bodoque, J. M., & Diez-Herrero, A. (2024). Designing an instrument to
#   measure attitudes toward flood risk management in riverside populations.
#   International Journal of Disaster Risk Reduction, 106, 104448.
#   (Not linked from the deposit's metadata; found by Crossref title search.
#   The paper is CC BY-NC but sits behind a ScienceDirect bot wall, so it was
#   not read.)
#   Deposit: Talayero, F., Garcia, J. A., & Amerigo, M. (2023). Dataset to
#   analyze the psychometric and structural properties of a scale designed to
#   measure attitudes to integrated flood risk management. Zenodo.
# Data: Zenodo 7547098, DATASET_Zamora_Edited.sav (406 rows x 39 columns;
#       a survey of residents of Zamora, Spain, described by the deposit as a
#       representative sample).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: the .sav carries full
#   ENGLISH variable labels for every P1/P2/P4 item (P1_2..P1_6 are
#   elliptical continuations of P1_1's stem) and endpoint-only value labels
#   (1 = Not at all likely / Strongly disagree, 5 = Very likely / Strongly
#   agree). The survey was administered in Spain, so the English labels are a
#   translation of the administered Spanish wording, which is in the paper
#   (bot-walled) and not in the deposit.
#
# Tables (item codes are the source column names). Blocks follow the deposit
# description's column map.
#   talayero_2023_flood_risk_perception  P1_1-P1_6   perceived probability of
#       flooding (city / neighbourhood / home x next 5 years / lifetime),
#       1-5, endpoint value labels.
#   talayero_2023_flood_mitigation_attitudes  P2_1-P2_15  attitudes toward
#       traditional and integrated flood mitigation measures, 1-5 agreement,
#       endpoint value labels.
#   talayero_2023_flood_management_adequacy  P4_1-P4_2  adequacy of flood
#       protection in the city / neighbourhood, 1-5 agreement, endpoint value
#       labels.
#   The permitted set 1-5 is taken from the value labels (labelled endpoints 1
#   and 5), not from the observed values.
#
# Dropped:
#   - P3_1-P3_6 (perceived efficiency of six general measures): every row is a
#     permutation of 1-6 (asserted), i.e. a RANKING, which is ipsative and not
#     six independent ordinal responses.
#   - P5_1-P5_3 (safety / environment / economy preferences): a constant-sum
#     allocation of 100 points (every row sums to 100, asserted), ipsative.
#   - TFMM, IFMM: saved factor scores.
#   - P6 (postal code): not shipped as a covariate (a quasi-identifier with no
#     analytic use here). P7REC: a recode of P7 (age).
# id: row index (no respondent id in the file).
# Covariates: cov_flooding_area (1 flooding area, 2 non-flooding area),
#   cov_age (years), cov_sex (1 male, 2 female).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/7547098/files/"
       "DATASET_Zamora_Edited.sav/content")

TABLES = {
    "talayero_2023_flood_risk_perception": [f"P1_{i}" for i in range(1, 7)],
    "talayero_2023_flood_mitigation_attitudes": [f"P2_{i}"
                                                 for i in range(1, 16)],
    "talayero_2023_flood_management_adequacy": ["P4_1", "P4_2"],
}
RANKING = [f"P3_{i}" for i in range(1, 7)]
ALLOCATION = ["P5_1", "P5_2", "P5_3"]
OTHER_DROPPED = {"TFMM", "IFMM", "P6", "P7REC"}
COVS = {"FLOODING_AREA": "cov_flooding_area", "P7": "cov_age",
        "P8": "cov_sex"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (406, 39), d.shape

    # Balance the books.
    items = {c for its in TABLES.values() for c in its}
    known = (items | set(RANKING) | set(ALLOCATION) | OTHER_DROPPED
             | set(COVS))
    assert set(d.columns) == known, set(d.columns) ^ known

    # P3 is a ranking and P5 a 100-point allocation: both ipsative.
    assert d[RANKING].apply(lambda r: sorted(r) == [1, 2, 3, 4, 5, 6],
                            axis=1).all()
    assert (d[ALLOCATION].sum(axis=1) == 100).all()

    # Permitted set from the value labels: endpoints 1 and 5 labelled.
    for its in TABLES.values():
        for c in its:
            vl = meta.variable_value_labels[c]
            assert set(vl) == {1.0, 5.0}, (c, vl)
    assert not d.duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(range(1, 6))
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
