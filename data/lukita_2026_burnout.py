#!/usr/bin/env python3
# Source: https://zenodo.org/records/23877402
# DOI: 10.5281/zenodo.23877402 (dataset; the record names no published paper)
# Deposit: Lukita, M. Y., & Syahputra, W. (2026). Predicting School Burnout
#   among Secondary School Students: The Mediating Role of Academic Resilience
#   in Self-Regulated Learning, Social Support, and Bedtime Procrastination
#   [Data set]. Zenodo.
# Data: dataeg.xlsx (one sheet; 453 rows x 66 columns: gender, school, grade +
#   63 items)
#   sha256 23544c1ec6bf750b2b70558f1b93d04db68222eae0646e6e9d4ccc89a74c61f0
#   Dataega.xlsx (453 rows x 13 columns: the same respondents in the same row
#   order -- its nine burnout columns EXH1-4/CYN1-3/INAD1-2 equal sbi1/4/7/9,
#   sbi2/5/6, sbi3/8 cell for cell on every row -- plus one yes/no question
#   that dataeg.xlsx lacks). Used only for that question.
#   sha256 2ca6b99769412e8216d03b4f151576fdc85590400047e3574041303920f4639c
# Codebook: none. The deposit is the two workbooks only, with no description,
#   questionnaire or value labels; the Zenodo record's description is empty.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (recoverable_format: the
# triage's 60-column 1-4 block was right in spirit, but one block is 1-5).
#
# No person id was deposited: the row index (1-453, file order) is the id, and
# is the same in all five tables, so they can be rejoined.
#
# FIVE output tables, one per instrument, block prefixes as in the source:
#   lukita_2026_burnout             sbi1-sbi9   9 items, observed 1-4
#       School Burnout Inventory-shaped (9 items; Dataega.xlsx assigns them to
#       exhaustion EXH, cynicism CYN and inadequacy INAD subscales).
#   lukita_2026_self_regulated      srl1-srl9   9 items, observed 1-4
#   lukita_2026_bedtime_procrast    bp1-bp9     9 items, observed 1-5
#       Nine items on 1-5 matches the Bedtime Procrastination Scale (Kroese et
#       al. 2014). Items bp2, bp3, bp7, bp9 load negatively on the first
#       component -- exactly the BPS's four reverse-worded items -- so they are
#       NOT reversed in the file; shipped as recorded.
#       CAUTION, unresolved: the 5s are confined to two items (bp5: 18 of
#       453, bp7: 6 of 453); the other seven never use 5, and every other
#       block in the file is 1-4. So the block is either the BPS's 1-5 scale
#       with the top category barely used, or a 1-4 scale with 24 mis-keyed
#       cells. The deposit cannot settle it; shipped as recorded on 1-5.
#   lukita_2026_social_support      sup1-sup12  12 items, observed 1-4
#       Source codes are pss1-pss12 (perceived social support). RENAMED to
#       sup1-sup12 because `^pss[_ ]?[0-9]` is the rights register's matcher
#       for the Perceived Stress Scale, which this is not. 12 items with a
#       three-factor-looking spectrum is the MSPSS's shape, but no stems are
#       in the deposit to confirm it.
#   lukita_2026_academic_resilience ars1-ars24  24 items, observed 1-4
#       ars19-ars23 correlate negatively with the rest (reverse-worded items,
#       not reversed in the file); shipped as recorded.
# Response anchors and directions are NOT documented anywhere in the deposit:
#   the ranges above are as observed (every value of each range occurs).
# Every item cell is filled (no NA).
#
# Plausibility check (2026-11-02, after a chunk-1 deposit looked generated):
#   within-block inter-item r is clearly positive for sbi (mean .32, min .17),
#   srl (.33, .14) and sup (.35, .11); bp and ars have negative pairs only
#   where the reverse-worded items fall. No duplicate response vectors. Read as
#   real survey data.
#
# Covariates: cov_gender (Jenis Kelamin: Laki-laki -> male, Perempuan ->
#   female), cov_school_type (Asal Sekolah: MTs = madrasah tsanawiyah, SMP =
#   general junior secondary), cov_grade (Kelas 7-9; one blank),
#   cov_study_schedule (Dataega.xlsx "Apakah kamu memiliki jadwal belajar rutin
#   di rumah?" -- do you have a regular study schedule at home -- Ya -> yes,
#   Tidak -> no).
#
# Item text: NOT shipped -- not in hand. The deposit carries item codes only;
#   no questionnaire, and the stems are not in the workbooks.
#
# PII: none. The only text columns are gender, school type (two values each)
#   and the yes/no schedule question, asserted below; no names, emails or
#   school names.

import hashlib
import os
import sys
import urllib.request

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
FILES = {
    "dataeg.xlsx": "23544c1ec6bf750b2b70558f1b93d04db68222eae0646e6e9d4ccc89a74c61f0",
    "Dataega.xlsx": "2ca6b99769412e8216d03b4f151576fdc85590400047e3574041303920f4639c",
}


def _raw(name):
    """LUKITA_RAW_DIR, else fetch into raw_cache with a sha256 check."""
    d = os.environ.get("LUKITA_RAW_DIR")
    if not d:
        d = os.path.join(REPO_ROOT, "automated_finding", "runs", "raw_cache",
                         "lukita_2026")
    os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, name)
    if not os.path.exists(dest):
        url = f"https://zenodo.org/api/records/23877402/files/{name}/content"
        req = urllib.request.Request(
            url, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r:
            blob = r.read()
        with open(dest, "wb") as fh:
            fh.write(blob)
    with open(dest, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == FILES[name], \
            f"{name} changed"
    return dest


SRC_BLOCKS = {
    "lukita_2026_burnout": ("sbi", 9, "sbi", [1, 2, 3, 4]),
    "lukita_2026_self_regulated": ("srl", 9, "srl", [1, 2, 3, 4]),
    "lukita_2026_bedtime_procrast": ("bp", 9, "bp", [1, 2, 3, 4, 5]),
    "lukita_2026_social_support": ("pss", 12, "sup", [1, 2, 3, 4]),
    "lukita_2026_academic_resilience": ("ars", 24, "ars", [1, 2, 3, 4]),
}
SBI_SUBSCALE_COLS = {"EXH1": "sbi1", "EXH2": "sbi4", "EXH3": "sbi7",
                     "EXH4": "sbi9", "CYN1": "sbi2", "CYN2": "sbi5",
                     "CYN3": "sbi6", "INAD1": "sbi3", "INAD2": "sbi8"}
SCHEDULE_Q = "Apakah kamu memiliki jadwal belajar rutin di rumah?"


def convert():
    df = pd.read_excel(_raw("dataeg.xlsx"))
    d2 = pd.read_excel(_raw("Dataega.xlsx"))
    assert df.shape == (453, 66) and d2.shape == (453, 13), (df.shape, d2.shape)
    items_src = [f"{p}{i}" for p, n, _, _ in SRC_BLOCKS.values()
                 for i in range(1, n + 1)]
    covs_src = ["Jenis Kelamin", "Asal Sekolah", "Kelas"]
    assert list(df.columns) == covs_src + items_src, list(df.columns)
    assert all(pd.api.types.is_integer_dtype(df[c]) for c in items_src)
    assert df[items_src].notna().all().all()
    # row alignment of the second workbook, cell for cell
    for a, b in SBI_SUBSCALE_COLS.items():
        assert (d2[a] == df[b]).all(), a
    assert set(df["Jenis Kelamin"]) == {"Laki-laki", "Perempuan"}
    assert set(df["Asal Sekolah"]) == {"MTs", "SMP"}
    assert set(d2[SCHEDULE_Q]) == {"Ya", "Tidak"}

    df.insert(0, "id", range(1, len(df) + 1))
    df["cov_gender"] = df["Jenis Kelamin"].map(
        {"Laki-laki": "male", "Perempuan": "female"})
    df["cov_school_type"] = df["Asal Sekolah"]
    df["cov_grade"] = df["Kelas"].astype("Int64")
    df["cov_study_schedule"] = d2[SCHEDULE_Q].map({"Ya": "yes", "Tidak": "no"})
    covs = ["cov_gender", "cov_school_type", "cov_grade", "cov_study_schedule"]

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (src, n, out, scale) in SRC_BLOCKS.items():
        ren = {f"{src}{i}": f"{out}{i}" for i in range(1, n + 1)}
        cols = list(ren.values())
        long = df.rename(columns=ren).melt(
            id_vars=["id"] + covs, value_vars=cols,
            var_name="item", value_name="resp")
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert long["resp"].isin(scale).all()
        assert set(long["resp"]) == set(scale)
        assert long["id"].nunique() >= 100

        checks = run_qc(long, permitted_values={i: scale for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
