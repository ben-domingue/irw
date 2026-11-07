#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0342922
# DOI: 10.1371/journal.pone.0342922
# Paper: Abeck F, Heinen I, Heidrich I, Kott J, Sommer R, Blome C, et al.
#   (2026). Testing undergraduate medical students' ability to correctly
#   identify skin conditions in skin of color -- A pre-post-study at a medical
#   school in Germany. PLoS One 21(2): e0342922.
# Data: PLOS Supporting Information S1 File (journal.pone.0342922.s001, "Data
#   set", sheet "Tabelle1"), 142 fourth-year medical students, University of
#   Hamburg, October 2024 - February 2025. The sheet's first row under the
#   header is a legend ("1 = correct / 0 = false" on every diagnosis column,
#   "0 = female / 1 = male / 2 = diverse" on sex) and is dropped. Sheet "Tabelle2" is
#   a summary table and is not read.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (rank 19; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# ONE output table: abeck_2026_soc_diagnosis -- a multiple-choice test of eight
#   clinical images of skin conditions in skin of color, given at the start
#   (wave 1) and the end (wave 2) of the seminar. resp = 1 if the image was
#   diagnosed correctly, 0 if not. Items diagnosis_1..diagnosis_8, the
#   deposit's own numbering (pre_test_diagnosis_k / post_test_diagnosis_k, two
#   of them with a trailing space in the header); the same eight conditions
#   at both waves, with different photos in the seminar itself. Which
#   condition is which number is not stated in the deposit.
# Covariates: age, sex (the deposit's legend: 0 female, 1 male, 2 diverse),
#   semester, prior dermatology experience (0/1).
# Dropped: declaration of consent (constant 1); year of birth (age carries
#   it); the five single-item self-ratings (knowledge of skin type scales,
#   knowledge of anatomy, diagnostic-ability self-assessment, each pre and
#   post, plus dermatology interest) -- each is one question, not a scale;
#   Knowledge_Scales (0/1) and the two free-text follow-ups
#   (Knowledge_Scales_text, Dermatology_Experience_text: short answers naming
#   a scale or a placement, max 47 characters; not carried in any form).
# `id` is the deposit's participant number (1..142, unique).
#
# Item text: NOT SHIPPED. The items are clinical photographs with
#   multiple-choice diagnoses; the images and options are not in the deposit
#   or the article text.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0342922.s001&type=supplementary"
RAW = os.environ.get("ABECK_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SEX = {0: "female", 1: "male", 2: "diverse"}
DROPPED = ["declaration of consent", "year of birth", "pre_test_knowledge_scales", "pre_test_knowledge_anatomy",
           "pre_test_diagnostic_abilitiy_self_assesment", "Knowledge_Scales", "Knowledge_Scales_text",
           "Dermatology_Interest", "Dermatology_Experience_text", "post_test_knowledge_scales",
           "post_test_knowledge_anatomy", "post_test_diagnostic_ability_self_assesment"]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name="Tabelle1")


def convert():
    df = load()
    df.columns = [c.strip() for c in df.columns]
    assert len(df) == 143
    legend = df["sex"].astype(str).str.contains("female")
    assert legend.sum() == 1 and legend.iloc[0]
    assert "1 = correct" in str(df["pre_test_diagnosis_1"].iloc[0])
    df = df[~legend].reset_index(drop=True)
    assert len(df) == 142 and df["participants"].nunique() == 142
    # the legend row forced every column to object; re-infer now it is gone
    for c in df.columns:
        num = pd.to_numeric(df[c], errors="coerce")
        if num.notna().sum() == df[c].notna().sum():
            df[c] = num
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"Knowledge_Scales_text", "Dermatology_Experience_text"}
    df["id"] = df["participants"].astype(int)
    df["cov_age"] = pd.to_numeric(df["age"])
    df["cov_sex"] = pd.to_numeric(df["sex"]).map(SEX)
    assert df["cov_sex"].notna().all()
    df["cov_semester"] = pd.to_numeric(df["semester"])
    df["cov_dermatology_experience"] = pd.to_numeric(df["Dermatology_Experience"])
    covs = ["cov_age", "cov_sex", "cov_semester", "cov_dermatology_experience"]
    used = {"participants", "age", "sex", "semester", "Dermatology_Experience"} | set(DROPPED)
    parts = []
    for wave, prefix in [(1, "pre_test_diagnosis_"), (2, "post_test_diagnosis_")]:
        cols = [f"{prefix}{k}" for k in range(1, 9)]
        used |= set(cols)
        p = df[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        p["item"] = p["item"].str.replace(prefix, "diagnosis_", regex=False)
        p["wave"] = wave
        parts.append(p)
    assert used == set(df.columns) - {"id"} - set(covs), set(df.columns) - used
    long = pd.concat(parts, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"])
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {0, 1}
    long = long[["id", "item", "resp", "wave"] + covs]
    assert not long.duplicated(["id", "item", "wave"]).any()
    items = sorted(long["item"].unique())
    checks = run_qc(long, permitted_values={c: [0, 1] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "abeck_2026_soc_diagnosis.csv"), index=False)
    print(f"abeck_2026_soc_diagnosis: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"waves={sorted(long['wave'].unique())}")


if __name__ == "__main__":
    convert()
