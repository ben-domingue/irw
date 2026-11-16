#!/usr/bin/env python3
# Source: https://figshare.northumbria.ac.uk/articles/dataset/Data_code_and_supplementary_material_for_i_The_Perfectionistic_Self-Presentation_i_i_Short_Form_Further_Psychometric_Validation_i_/34094325
# DOI: 10.25398/rd.northumbria.34094325.v1 (data; no paper DOI on the record)
#   Grugan M (2026). Data, code, and supplementary material for "The
#   Perfectionistic Self-Presentation-Short Form: Further Psychometric
#   Validation". Northumbria University figshare.
# Data: students_data.csv (537 UK university students) and
#   non_students_data.csv (353 UK community adults), same 69 columns, Qualtrics
#   2023-2026. The deposit's *_clean.csv files are the authors' analysis
#   samples (after their exclusions); the raw files ship here.
# License: CC BY 4.0 (figshare record).
# Codebook: none; the deposit's pre-registration PDF and Mplus outputs describe
#   the measures (the Mplus output labels Gender 1 = male, 2 = female).
#
# Counts: description says N = 539 students and 354 adults, minus two student
#   and one adult straight-lining case removed before deposit = 537 + 353,
#   exactly the two files.
# Tables (one merged file per instrument, cov_sample = student / community;
#   items as deposited, no reverse-scoring):
#   grugan_2026_psps            Perfectionistic Self-Presentation Scale (Hewitt
#                               et al. 2003), 27 items PSPS_1-27, 1-7
#   grugan_2026_psp_hes         Perfectionistic Self-Presentation Hiding Effort
#                               Scale, 4 items PSP.HE.S_1-4, 1-7
#   grugan_2026_social_anxiety  12 items Social.Anxiety._1-12, 1-5; the
#                               pre-registration names social interaction
#                               anxiety and social phobia (a 6+6 short-form
#                               pair), item order not documented
#   grugan_2026_mps15           trait perfectionism, 15 items
#                               Perfectionism_1-15, 1-7 (self-oriented, socially
#                               prescribed, other-oriented per the
#                               pre-registration)
# id: students 1-537, community adults 100001-100353 (row index; StartDate is
#   an obfuscated number, not an id, and is dropped).
# Covariates: sample, age, gender (1 male, 2 female, 3-5 undocumented), year of
#   study (students). Free-text gender, birth country, profession and course
#   are not carried; employment/profession codes are unlabelled.
# Item text: not shipped -- no wording in the deposit; PSPS and HF-MPS are
#   published instruments with no register row.

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
FILES = {"student": ("https://ndownloader.figshare.com/files/69852666", 537, 0),
         "community": ("https://ndownloader.figshare.com/files/69852660", 353, 100000)}
SPEC = {
    "grugan_2026_psps": ([f"PSPS_{i}" for i in range(1, 28)], range(1, 8)),
    "grugan_2026_psp_hes": ([f"PSP.HE.S_{i}" for i in range(1, 5)], range(1, 8)),
    "grugan_2026_social_anxiety": ([f"Social.Anxiety._{i}" for i in range(1, 13)], range(1, 6)),
    "grugan_2026_mps15": ([f"Perfectionism_{i}" for i in range(1, 16)], range(1, 8)),
}
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Year": "cov_study_year"}
DROPPED = {"StartDate", "Gender_Other", "Birth_Country", "Student_Status",
           "Employed", "Profession", "Profession_Other", "Course"}


def main():
    parts = []
    for sample, (url, n, off) in FILES.items():
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        d = pd.read_csv(io.BytesIO(r.content))
        assert d.shape == (n, 69), (sample, d.shape)
        used = set(COVS) | DROPPED
        for cols, _ in SPEC.values():
            used |= set(cols)
        assert used == set(d.columns), set(d.columns) ^ used
        d = d.reset_index(drop=True)
        d["id"] = d.index + 1 + off
        d["cov_sample"] = sample
        parts.append(d)
    d = pd.concat(parts, ignore_index=True).rename(columns=COVS)
    assert d["id"].is_unique
    covs = ["cov_sample"] + list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (cols, vals) in SPEC.items():
        allowed = set(vals)
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
