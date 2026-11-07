#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0338543
# DOI: 10.1371/journal.pone.0338543
# Paper: Ou Q, Wu S, Jiang Y, He Z, Luo H (2025). From training to practice: A
#   multi-group analysis of factors influencing K-12 teachers' integration of
#   Digital Educational Resources (DERs). PLoS One 20(12): e0338543.
# Data: PLOS Supporting Information S1 Data (journal.pone.0338543.s001, "Raw
#   data of this study"), 3,878 K-12 teachers in the 2024 Guangxi online
#   digital-literacy training programme, China. No missing cells.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 3.
#
# The questionnaire, per the paper: part 2, four questions on teachers'
# experience with digital technology (DET); part 3, UTAUT constructs adapted
# from Venkatesh et al. (17 items); part 4, a 28-item scale built on the
# "Industry Standard for Digital Literacy of Chinese Teachers" (administered,
# not analysed in the paper). All items 1-5, "Strongly Disagree" to
# "Strongly Agree". Item codes are the deposit's own.
#
# SEVEN output tables:
#   ou_2025_det               DET1-4, digital technology experience
#   ou_2025_utaut_pe          PE1-3, performance expectancy
#   ou_2025_utaut_ee          EE1-3, effort expectancy
#   ou_2025_utaut_si          SI1-3, social influence
#   ou_2025_utaut_fc          FC1-3, facilitating conditions
#   ou_2025_utaut_bi          BI1-3, behavioural intention
#   ou_2025_digital_literacy  the 28-item digital-literacy scale: DA1-5,
#                             DTKS1-3, DAP1-10, DSR1-5, PD1-5
# Dropped: UB1-2 (use behaviour, two items, under the 3-item floor); the
#   serial number's companion "time taken"; and all eight demographic columns
#   (gender, age group, teaching experience, education, title, subject,
#   school location, school level) -- bare codes the paper does not label.
# `id` is the deposit's serial number (1..3878, unique).
#
# Item text: NOT SHIPPED. Header codes only; the article does not list the
#   adapted wording.

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
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0338543.s001"
RAW = os.environ.get("OU_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLES = {"det": r"DET\d", "utaut_pe": r"PE\d", "utaut_ee": r"EE\d", "utaut_si": r"SI\d", "utaut_fc": r"FC\d",
          "utaut_bi": r"BI\d", "digital_literacy": r"(DA|DTKS|DAP|DSR|PD)\d+"}
N = {"det": 4, "utaut_pe": 3, "utaut_ee": 3, "utaut_si": 3, "utaut_fc": 3, "utaut_bi": 3, "digital_literacy": 28}
DEMOG = ["The time taken", "gender", "Age group", "years of teaching experience", "educational background",
         "professional title", "The subject(s) you teach", "The geographical location of school",
         "The educational level"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    df.columns = [str(c).strip() for c in df.columns]
    assert df.shape == (3878, 59), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    items = {k: [c for c in df.columns if re.fullmatch(p, c)] for k, p in TABLES.items()}
    assert {k: len(v) for k, v in items.items()} == N, {k: len(v) for k, v in items.items()}
    used = {"serial number", "UB1", "UB2"} | set(DEMOG) | {c for v in items.values() for c in v}
    assert used == set(df.columns), set(df.columns) ^ used
    assert df["serial number"].nunique() == len(df)
    df = df.copy()
    df["id"] = df["serial number"].astype(int)
    for key, cols in items.items():
        long = df[["id"] + cols].melt(id_vars=["id"], var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        out = f"ou_2025_{key}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
