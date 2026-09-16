#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/7wfgz62xgs/1
# DOI: 10.1038/s41598-023-34006-0
# Data: 10.17632/7wfgz62xgs.1 (BITS_sample1_N965.sav, "BITS sample II_N803.sav")
# License: CC BY 4.0 (confirmed on the Mendeley Data record, 2026-09-16)
# Item text: not shipped. The .sav files carry value labels (Polish response
#   anchors) but no item wording, and the instruments involved — the Bern
#   Illegitimate Tasks Scale (Semmer et al.), the Burnout Assessment Tool
#   (Schaufeli et al.) and the work-overload scale — are published instruments
#   whose wording rights are separate from this deposit's CC BY. Only the
#   response-option anchors are known here, which is not item text.
#
# Basinska & Daderman (2023), Scientific Reports: a psychometric validation of
# the Polish BITS in two independently recruited employee samples. The deposit
# holds three files: BITS_sample1_N965.sav (sample 1, 2019, 965 employees after
# one multivariate outlier was dropped), "BITS sample II_N803.sav" (sample 2,
# 2020, 803 employees after 18 outliers were dropped) and BITS_PLv.pdf (the
# Polish BITS form, not data).
#
# Sample 1's file is 13 columns: BITS1-BITS9 plus four scored composites
# (Unnecessary_tasks_5item, Unreasonable_tasks, Illegitimate_tasks_9item,
# Unnecessary_tasks_4item), which are subscale aggregates and are excluded.
#
# Sample 2's file is 63 columns and holds four instruments plus demographics
# and derived scores. Methods/Table 1 name them: BITS (9 items), work overload
# (4 items, FII_D_WO1-4), the Burnout Assessment Tool BAT-23 (23 items, split
# across the four documented subscales Exhaustion 8 / Mental distance 5 /
# Cognitive impairment 5 / Emotional impairment 5, i.e. FII_Ex_*, FII_MD_*,
# FII_CI_*, FII_EI_*), a single-item job-satisfaction question (FII_W_JS1) and
# a single-item work-performance rating (FII_O_CWP1). The two single-item
# measures are not scales and are not shipped. FII_O_IP1-3 (a three-item 1-5
# agreement block, aggregated in the file as InRt2) is not described anywhere
# in the paper or Table 1, so its construct cannot be confidently assigned and
# it is excluded. The trailing derived columns — WEt2, WOt2, BITSat2, BITSbt2,
# BAT23t2, InRt2 and the two Mahalanobis distances MAH_1/MAH_2 — are composites
# and outlier statistics, all excluded. FII_DATA is an SPSS date of survey
# completion (study metadata, dropped); FII_AGREE is the consent flag, constant
# 1, and is dropped too.
#
# The BITS is the same nine-item Polish instrument in both samples ("We took
# the original ... BITS instrument including nine items", Measures; the same
# 1-5 never/very-often anchors appear in both .sav files), but the samples were
# recruited independently a year apart from different sectors, sample 1 carries
# no covariates at all, and the deposit keeps them apart. They are therefore
# shipped as two files rather than merged, so no id offsetting is needed and no
# false id collision is possible.
#
# Responses: every item is 1-5 from the .sav value labels — BITS 1 "Nigdy" to
# 5 "Bardzo czesto"; work overload and all BAT-23 items 1 "Nigdy" to 5
# "Zawsze". There are no extra labelled categories, no "don't know"/"not
# applicable" option, and no sentinel codes: both files are complete, with
# every column at full N and nothing outside 1-5 (the paper reports only
# "fully completed protocols", with multivariate outliers excluded rather than
# filled in). The paper contains no imputation language — no "imput", "missing
# data", "MICE" or "LOCF" anywhere in its text. Nothing is reverse-scored here;
# the paper notes all nine BITS items are positively worded, and the BAT-23
# items are left exactly as recorded. In BAT-23 four of the five emotional-
# impairment items (FII_EI_1/2/4/5) top out at an observed 4 rather than 5 —
# category non-use in a low-burnout sample, not a different response format:
# Table 1 gives one 5-point (1 = never, 5 = always) format for all 23 BAT
# items, and the validator's nested-range warning on that table is expected.
#
# No PII: neither file holds a name, email, IP/GPS, birthdate or national ID.
# Sample 2's only non-numeric column is the survey date. Neither file has a
# person identifier, so `id` is the row index per datastandard.md.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadstat
import requests
from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
API = "https://data.mendeley.com/public-api/datasets/7wfgz62xgs"

VALID_MIN, VALID_MAX = 1, 5

BITS_ITEMS = [f"BITS{i}" for i in range(1, 10)]
WO_ITEMS = [f"FII_D_WO{i}" for i in range(1, 5)]
BAT_ITEMS = (
    [f"FII_Ex_{i}" for i in range(1, 9)]
    + [f"FII_MD_{i}" for i in range(1, 6)]
    + [f"FII_CI_{i}" for i in range(1, 6)]
    + [f"FII_EI_{i}" for i in range(1, 6)]
)

# Person-level covariates in sample 2's file, kept as the source's numeric
# codes (their value labels are Polish; see the .sav for the mapping).
COV_RENAME = {
    "FII_Occupation": "cov_occupation",
    "FII_Gender": "cov_gender",
    "FII_Age": "cov_age",
    "FII_Edu": "cov_education",
    "FII_City": "cov_city_size",
    "FII_Marriage": "cov_partnered",
    "FII_Kids": "cov_children",
    "FII_Province": "cov_province",
    "FII_Tenure": "cov_tenure",
    "FII_Manger": "cov_manager",
    "FII_tenureOrg": "cov_tenure_org",
    "FII_sizeOrg": "cov_org_size",
}


def _fetch(filename: str) -> pd.DataFrame:
    """Read one .sav file from the Mendeley Data record."""
    meta = requests.get(API, headers=UA, timeout=60).json()
    url = next(f["content_details"]["download_url"] for f in meta["files"]
               if f["filename"] == filename)
    content = requests.get(url, headers=UA, timeout=120).content
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_DIR / f".{filename.replace(' ', '_')}"  # pyreadstat needs a path
    tmp.write_bytes(content)
    try:
        df, _ = pyreadstat.read_sav(str(tmp))
    finally:
        tmp.unlink(missing_ok=True)
    return df


def _write(df: pd.DataFrame, items: list[str], covs: list[str],
           out_name: str) -> None:
    missing = [c for c in items if c not in df.columns]
    assert not missing, f"{out_name}: missing item columns {missing}"

    long = df.melt(id_vars=["id"] + covs, value_vars=items,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= VALID_MIN) & (long["resp"] <= VALID_MAX)]
    long = long[["id", "item", "resp"] + covs].reset_index(drop=True)

    assert long["resp"].between(VALID_MIN, VALID_MAX).all()
    assert not long.duplicated(["id", "item"]).any()
    assert not long.isna().any().any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert() -> None:
    # Sample 1 (2019, n=965): BITS only, no covariates distributed.
    s1 = _fetch("BITS_sample1_N965.sav").reset_index(drop=True)
    assert len(s1) == 965, f"expected 965 rows in sample 1, got {len(s1)}"
    s1.insert(0, "id", s1.index + 1)
    _write(s1, BITS_ITEMS, [], "basinska_2023_bits_s1.csv")

    # Sample 2 (2020, n=803): BITS, work overload and BAT-23, with covariates.
    s2 = _fetch("BITS sample II_N803.sav").reset_index(drop=True)
    assert len(s2) == 803, f"expected 803 rows in sample 2, got {len(s2)}"
    s2 = s2.rename(columns=COV_RENAME)
    s2.insert(0, "id", s2.index + 1)
    covs = sorted(COV_RENAME.values())

    _write(s2, BITS_ITEMS, covs, "basinska_2023_bits_s2.csv")
    _write(s2, WO_ITEMS, covs, "basinska_2023_work_overload.csv")
    _write(s2, BAT_ITEMS, covs, "basinska_2023_bat23.csv")


if __name__ == "__main__":
    convert()
