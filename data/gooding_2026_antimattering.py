#!/usr/bin/env python3
# Source: https://figshare.manchester.ac.uk/articles/dataset/antimattering_anxiety_helpseeking_folder/34167447
# DOI: 10.48420/34167447 (data; no paper DOI on the record)
#   Gooding P, Harris K, Ruigrok A, Peters S (2026). antimattering anxiety
#   helpseeking folder. University of Manchester figshare.
# Data: "antimattering anxiety helpseeking CSV.csv" (172 University of
#   Manchester students x 51 columns), collected Feb-Dec 2024 on Qualtrics.
# License: CC BY 4.0 (figshare record).
# Codebook: "ReadMe antimattering anxiety helpseeking.odt" in the deposit,
#   which names the three measures; it gives no response anchors.
#
# Counts: 172 rows = the deposit description's N = 172.
# id = the file's ID_Number (unique, 172 values).
# Tables (items as deposited, no reverse-scoring):
#   gooding_2026_ssosh           Self-Stigma of Seeking Help (Vogel, Wade &
#                                Haake 2006), 10 items, 1-5 (HelpSeeking1-10)
#   gooding_2026_anti_mattering  Anti-Mattering Scale (Flett et al. 2022),
#                                5 items, 1-4
#   gooding_2026_dass21          DASS-21, 21 items, stored 1-4 (the published
#                                0-3 scale +1); "#NULL!" cells are missing.
# Not shipped: SSoSHNeg/SSoSHNonNeg and DASS_* subscale totals; free-text
#   ethnicity, gender identity and discipline ("in their own words").
# Covariates: age, student type, year of study, full/part-time, UK/non-UK,
#   native English speaker (text categories as deposited).
# Item text: not shipped -- no wording in the deposit (headers are positional);
#   the instruments are published scales (DASS-21, SSOSH, AMS).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/69728154"

COVS = {"Age": "cov_age", "Type_Student": "cov_student_type",
        "Study_year": "cov_study_year", "Full_PT_status": "cov_full_part_time",
        "UK_nonUK": "cov_uk_status",
        "NativeEnglishSpeaker": "cov_native_english"}
DROPPED = {"Ethnicity", "GenderIdentity", "DisciplineStudied", "SSoSHNeg",
           "SSoSHNonNeg", "DASS_Depression", "DASS_Anxiety", "DASS_Stress"}
SPEC = {
    "gooding_2026_ssosh": ([f"HelpSeeking{i}" for i in range(1, 11)], range(1, 6)),
    "gooding_2026_anti_mattering": ([f"AntiMatter{i}" for i in range(1, 6)], range(1, 5)),
    "gooding_2026_dass21": ([f"DASS{i}" for i in range(1, 22)], range(1, 5)),
}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), na_values=["#NULL!"])
    assert d.shape == (172, 51), d.shape
    assert d["ID_Number"].is_unique
    used = {"ID_Number"} | set(COVS) | DROPPED
    for cols, _ in SPEC.values():
        used |= set(cols)
    assert used == set(d.columns), set(d.columns) ^ used
    d = d.rename(columns={"ID_Number": "id", **COVS})
    covs = list(COVS.values())
    for c in covs:
        if d[c].dtype == object:
            d[c] = d[c].str.strip()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (cols, vals) in SPEC.items():
        allowed = set(vals)
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        long = long.dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, (table, set(long["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
