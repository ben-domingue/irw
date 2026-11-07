#!/usr/bin/env python3
# Source: https://doi.org/10.17026/dans-za8-qpmw
# DOI: 10.1371/journal.pone.0249058
# Paper: Vicens P, Heredia L, Bustamante E, Perez Y, Domingo JL, Torrente M
#   (2021). Does living close to a petrochemical complex increase the adverse
#   psychological effects of the COVID-19 lockdown? PLoS ONE 16(3): e0249058.
# Data: DANS Data Station SSH doi:10.17026/dans-za8-qpmw, file "DATOS
#   PETROCOVID 1 LIMPIOS CON DISTANCIA_English.xls" (datafile 20884), sheet
#   Petrovid_15-05-2020, with "variables PETROCOVID survey.pdf" (the
#   codebook). 1,607 adults in Catalonia/Valencia answering the online
#   Petrocovid Survey during the spring 2020 lockdown.
# License: CC0 1.0 on the DEPOSIT (DANS dataset licence); the article is
#   CC BY 4.0.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 4.
#
# FOUR output tables, item codes the deposit's own:
#   vicens_2021_pss    Perceived Stress Scale, t1_1-14, 0 "never" to 4 "very
#     often" (the codebook's codes; the paper describes the same scale as
#     1-5).
#   vicens_2021_hads   Hospital Anxiety and Depression Scale, A1-A7 and
#     D1-D7, 0-3.
#   vicens_2021_bis11  Barratt Impulsiveness Scale, t3_1-30, 1 "never or
#     rarely" to 4 "always or almost always".
#   vicens_2021_erq    Emotion Regulation Questionnaire, t4_1-10, 1 "strongly
#     disagree" to 7 "strongly agree".
#   Items whose code ends in "i" (t1_4i, A1i, t3_1i, ...) are deposited
#   ALREADY REVERSED: the deposit's own totals (TOTAL PSS, A_TOTAL, D_TOTAL,
#   T3_TOTAL, T3_P) equal the plain sum of the stored columns on every row.
#   The codes keep the "i" so the direction is visible; t3-12i is renamed
#   t3_12i.
# Covariates: sex (0 male, 1 woman, the codebook), age (four negative ages,
#   -55 to -1, set to missing).
# Dropped: the town and postal code of residence during lockdown and usually
#   (population, cp, population1, cp1, "Canvi population") and the distance
#   to the nearest petrochemical focus (2026-10-20 geography ruling); the
#   near/far flag "cercaPeclosePetrotro", because its coding conflicts with
#   the paper (the codebook says 1 = near; 1,024 rows hold 1, and the paper's
#   far group is n = 1,024); the danger rating and the B-block lockdown
#   questions (single yes/no and 1-3 items on different scales); every total
#   and subscale score; a data manager's note column.
# `id` is the deposit's identification number (Go, unique). Five blank rows
#   at the end of the sheet are dropped.
#
# Item text: NOT SHIPPED. The codebook PDF has the English wording of every
#   item (study-authored, CC0); not built in this batch.

import io
import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ssh.datastations.nl/api/access/datafile/20884"
RAW = os.environ.get("VICENS_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
TABLES = {"pss": (r"t1_\d+i?", 14, range(0, 5), "TOTAL PSS"),
          "hads": (r"[AD]\di?", 14, range(0, 4), None),
          "bis11": (r"t3_\d+i?", 30, range(1, 5), "T3_TOTAL"),
          "erq": (r"t4_\d+", 10, range(1, 8), None)}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name="Petrovid_15-05-2020")


def convert():
    df = load()
    assert df.shape == (1612, 106), df.shape
    print(f"PII screen: {len(df.columns)} columns examined; town, postal code and distance not carried")
    df = df[df["Go"].notna()].rename(columns={"t3-12i": "t3_12i"}).reset_index(drop=True).copy()
    assert len(df) == 1607 and df["Go"].is_unique
    df["id"] = df["Go"].astype(int)
    df["cov_sex"] = df["sex"].map({0: "male", 1: "woman"})
    assert df["cov_sex"].notna().all()
    assert (df["age"] < 0).sum() == 4
    df["cov_age"] = df["age"].where(df["age"] >= 0).astype("Int64")
    covs = ["cov_sex", "cov_age"]
    for sub, total in (("A", "A_TOTAL"), ("D", "D_TOTAL")):  # HADS subscales, stored direction = scoring
        cols = [c for c in df if re.fullmatch(sub + r"\di?", c)]
        ok = df[total].notna()
        assert len(cols) == 7 and (df.loc[ok, cols].sum(axis=1) == df.loc[ok, total]).all(), sub
    for name, (pat, n, perm, total) in TABLES.items():
        items = [c for c in df.columns if re.fullmatch(pat, c)]
        assert len(items) == n, (name, items)
        if total:  # stored direction = scoring direction
            ok = df[total].notna()
            assert (df.loc[ok, items].sum(axis=1) == df.loc[ok, total]).all(), name
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"vicens_2021_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
