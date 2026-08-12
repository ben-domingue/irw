#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10100826
# DOI: 10.7717/peerj.15053
#
# Gizaw et al. (2023), "Change in depression during the COVID-19
# pandemic among healthcare providers in Addis Ababa." PeerJ. CC BY 4.0.
# 2-wave PHQ-9 (Time: 1=first wave n=300, 2=second wave n=277). The
# deferred-candidate note assumed `hw_id` was a real per-person key
# linking the same respondent across waves, but that does NOT survive
# datastandard.md's uniqueness check: `hw_id` collides across clearly
# different people even *within* a single wave (e.g. hw_id==1 in wave 1
# has three rows with different ages -- 43, 42, 62 -- for the same
# nominal id), so it cannot be trusted to identify a single person, let
# alone the same person across waves. Falling back to the row index as
# `id` per datastandard.md's "Missing person ID" rule -- this ships the
# two waves as two effectively cross-sectional PHQ-9 samples rather than
# a linked panel (duplicate id+item pairs are not created, since id is
# unique per row). PHQ9_depressioneffect/DepressionEff/DepressionScore/
# DepScore_cat/Depression are pre-computed aggregate/derived columns,
# excluded. No PII (Age/Agegroup/Sex/Profession/etc. are ordinary
# covariates).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10100826/supplementaryFiles"
MEMBER = "peerj-11-15053-s001.dta"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PHQ_ITEMS = [f"PHQ{i}" for i in range(1, 10)]

COV_RENAME = {
    "Age": "cov_age",
    "Agegroup": "cov_age_group",
    "Sex": "cov_sex",
    "COVIDconcern": "cov_covid_concern",
    "Perceivedrisk": "cov_perceived_risk",
    "COV19Test": "cov_covid_test",
    "PrimaryWP": "cov_primary_workplace",
    "Profession": "cov_profession",
    "COVID19Training": "cov_covid_training",
    "COVID19WPGuidance": "cov_covid_wp_guidance",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".dta") as tmp:
        tmp.write(zf.read(MEMBER))
        tmp.flush()
        df = pd.read_stata(tmp.name)

    # hw_id fails the uniqueness check (collides across different people
    # within a single wave) -- use row index instead.
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns={"Time": "wave"})
    df["wave"] = pd.to_numeric(df["wave"], errors="coerce")

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=PHQ_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]

    out_cols = ["id", "item", "resp", "wave"] + cov_cols
    long = long[out_cols]

    out_path = OUT_DIR / "gizaw_2023_phq9.csv"
    long.to_csv(out_path, index=False)
    print(f"gizaw_2023_phq9: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
