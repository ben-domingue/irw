#!/usr/bin/env python3
# Source: https://zenodo.org/records/22135733
# DOI: 10.5281/zenodo.22135733
# Deposit: Nurmalita, D., & Seillah, F. B. (2026). Dataset, Questionnaire, dan
#   Codebook: The Impact of Financial Literacy, Self-Control, and Paylater
#   Usage Intensity on the Financial Stability of Income-Earning Generation Z
#   in the Greater Jakarta Area [Data set]. Zenodo.
# Data: Dataset.xlsx (one sheet, "1"; 177 rows x 17 columns: Id + 16 items)
#   sha256 65bb5499f47113a74c7669b26bcadfaa566098018225836a9cb42f438bac5c36
# Codebook: Codebook.pdf in the same deposit (variable codes, the 1-5 scale);
#   Kuesioner.pdf prints each code beside its Indonesian statement.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (the batch's one `good` row).
#
# FOUR output tables, one per construct, because the deposit is four separate
# 4-item scales administered side by side and analysed as four latent
# variables in the depositors' PLS-SEM:
#   LK1-LK4  Literasi Keuangan (financial literacy)       -> _financial_literacy
#   SC1-SC4  Self-Control                                  -> _self_control
#   IP1-IP4  Intensitas Penggunaan Paylater (paylater use) -> _paylater_use
#   SK1-SK4  Stabilitas Keuangan (financial stability)     -> _financial_stability
# The same respondent carries the same id in all four tables (the source Id,
# 1-177), so they can be rejoined.
#
# resp: all 16 items on the codebook's one 5-point agreement scale,
# 1 Sangat Tidak Setuju (strongly disagree) .. 5 Sangat Setuju (strongly
# agree), 3 = Ragu-ragu (undecided). Shipped as recorded; no item is
# reverse-worded in the questionnaire. Every cell is filled (177 x 16, no NA).
#
# Covariates: none. The file holds Id and the 16 items and nothing else; the
# questionnaire PDF's demographics were not deposited.
#
# Item text: SHIPPED for all four tables 2026-11-02 (staged, not yet
# uploaded) by automated_finding/itemtext_verification/
# make_itemtext_repos_2026-11-02.py. Indonesian statements from Kuesioner.pdf,
# which prints each code beside its statement (explicit, not positional);
# anchors from Codebook.pdf; English in *_translated is IRW's machine
# translation, which owes an itemtext_issues.qmd entry. Study-authored, CC BY
# 4.0; register row NURMALITA-PAYLATER (ship). Label levels: not applicable,
# the .xlsx carries no variable or value labels.
#
# PII: none possible -- every column is an integer (Id and 16 items in 1-5),
# asserted below, so there is no text column to screen.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NURMALITA_RAW", "Dataset.xlsx")

TABLES = {
    "nurmalita_2026_financial_literacy": ["LK1", "LK2", "LK3", "LK4"],
    "nurmalita_2026_self_control": ["SC1", "SC2", "SC3", "SC4"],
    "nurmalita_2026_paylater_use": ["IP1", "IP2", "IP3", "IP4"],
    "nurmalita_2026_financial_stability": ["SK1", "SK2", "SK3", "SK4"],
}


def convert():
    df = pd.read_excel(RAW, sheet_name="1")
    expected = ["Id"] + [c for items in TABLES.values() for c in items]
    assert list(df.columns) == expected, list(df.columns)
    assert len(df) == 177, len(df)
    assert all(pd.api.types.is_integer_dtype(df[c]) for c in df.columns), \
        "a non-integer column appeared -- screen it for PII before shipping"
    assert df["Id"].is_unique
    assert df.notna().all().all()

    df = df.rename(columns={"Id": "id"})
    os.makedirs(OUT_DIR, exist_ok=True)
    for table, items in TABLES.items():
        long = df.melt(id_vars=["id"], value_vars=items,
                       var_name="item", value_name="resp")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert long["resp"].between(1, 5).all()
        assert long["id"].nunique() >= 100

        checks = run_qc(long, permitted_values={i: [1, 2, 3, 4, 5]
                                                for i in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long[["id", "item", "resp"]].to_csv(
            os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
