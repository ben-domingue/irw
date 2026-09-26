#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.28207451
# DOI: 10.1038/s41598-025-09988-8
#   "Development of a human analogue ADHD diagnostic system for family dogs"
#   (Csibra, Bunford & Gacsi, 2025), Scientific Reports 15:25671. PMC12263975.
# Data: figshare 28207451 (contributor Barbara Csibra), one file "Dataset for
#       Csibra et al 2025 Development of a human analogue ADHD diagnostic
#       system for family dogs.xlsx": 1872 dogs x 60 columns.
# License: CC BY 4.0 on the figshare deposit (api.figshare.com/v2/articles/
#          28207451); the article is also CC BY 4.0.
#
# Item text: available, not shipped here -- the article's Supplementary
#   Appendix A (41598_2025_9988_MOESM1_ESM.docx) prints the full English
#   wording of the DAFRS owner form: the 17 symptom items by original
#   questionnaire number (1, 3, 4, 7, 12 ... 42) with the anchors (0) Never -
#   (1) Rarely - (2) Often - (3) Very often, and the 7 functionality problems
#   asked three times (attributable to inattention / impulsivity / excessive
#   activity) with a 0-3 attribution scale (both "no such problem" and "a
#   problem, but not a result of X" score 0). The column names carry the item
#   numbers and short labels. Administered online to (mostly Hungarian) dog
#   owners; the form's source language is not stated beyond the English
#   appendix.
#
# The focal unit (id) is the DOG; each dog is rated once by its owner.
# The owner form collected owner name, email and the dog's name and birth date
# -- none of these is in the deposit (only ID, age in months, sex, neuter
# status), so there is no PII.
#
# Tables:
#   csibra_2025_dafrs_symptoms   17 symptom items (IA/H/I), 0-3
#   csibra_2025_dafrs_function   21 functional-impairment items (7 problems x
#                                attribution to IA / I / H), 0-3
# (The aggression and vocalisation functionality items on the form are not
# in the deposit.) Every other column is a score, weighted score or derived
# cut-off flag and is skipped. No missing cells, all integers.
#
# Duplicates: two adjacent-ID pairs (1165/1166, 1538/1539) are exact copies on
# all 59 non-ID columns, most likely double submissions. There is no wider
# near-duplicate network (median nearest-neighbour distance 6). The later ID of
# each pair is dropped (ben-domingue, 2026-09-26), leaving 1870 dogs.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/51681248"

COVS = {"Age_in_month": "cov_age_months",
        "Sex (1:male; 2:female)": "cov_sex",
        "Neutered (0:intact; 1: neutered)": "cov_neutered"}
DERIVED = [
    "Inattention (IA)", "Hyperactivity (H)", "Impulsivity (I)", "ADHD_Total",
    "Weighted_IA_score", "Weighted_H_score", "Weighted_I_score",
    "Weighted_ADHD_score", "Functionality_IA_7Q_per_4_true",
    "Functionality_I_7Q_per_4_true", "Functionality_H_7Q_per_4_true",
    "IA_H_impairment_combination", "IA_IMP_impairment_combination",
    "IMP_H_impairment_combination", "Impairment_in_IA_HY_I_combination",
    "Functionality_at_least_one_area_impaired_7Q_per4_true",
    "ADHD_score_cutoff_true", "High_risk_ADHD_true"]


def convert() -> None:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (1872, 60), d.shape
    assert d["ID"].is_unique

    # drop exact copies on every non-ID column, keeping the first ID
    dup = d.drop(columns="ID").duplicated(keep="first")
    assert sorted(d.loc[dup, "ID"]) == [1166, 1539], sorted(d.loc[dup, "ID"])
    print(f"  drop {dup.sum()} exact-duplicate rows: IDs {sorted(d.loc[dup, 'ID'])}")
    d = d[~dup].reset_index(drop=True)

    sym = [c for c in d.columns if c.startswith("Item_")]
    fun = [c for c in d.columns if c.startswith("Functionality_")
           and "_item_" in c]
    assert len(sym) == 17 and len(fun) == 21, (len(sym), len(fun))

    # ---- books ---------------------------------------------------------
    skipped = {"ID": "becomes id"}
    skipped.update({c: "sum / weighted score or derived cut-off flag"
                    for c in DERIVED})
    acc = set(sym) | set(fun) | set(COVS) | set(skipped)
    assert set(d.columns) == acc and len(d.columns) == len(acc), \
        set(d.columns) ^ acc
    for c, why in skipped.items():
        print(f"  skip {c}: {why}")

    # sanity: the deposited subscale sums reproduce from the items
    for suf, col in [("_IA", "Inattention (IA)"), ("_H", "Hyperactivity (H)"),
                     ("_I", "Impulsivity (I)")]:
        its = [c for c in sym if c.endswith(suf)]
        assert (d[its].sum(axis=1) == d[col]).all(), col

    d = d.rename(columns={"ID": "id", **COVS})
    cov_cols = list(COVS.values())
    names = []
    for table, items in [("csibra_2025_dafrs_symptoms", sym),
                         ("csibra_2025_dafrs_function", fun)]:
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert table not in names
        names.append(table)
        pv = {i: {0, 1, 2, 3} for i in items}
        assert not set(long["resp"]) - {0, 1, 2, 3}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            (table, [(f.check, f.message) for f in rep.errors])
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
