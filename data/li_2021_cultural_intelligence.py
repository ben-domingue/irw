#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0250878
# DOI: 10.1371/journal.pone.0250878
# Supporting Information: https://doi.org/10.1371/journal.pone.0250878.s002
#
# The raw file bundles four scales: Sustainable Innovation Behavior
# (SIB1-6), Cultural Intelligence (CQ1-12), Knowledge Sharing (KS1-4), and
# Organizational Cultural Diversity (OCD1-9), all 1-7. Per the IRW standard
# (one scale per file), this produces four output files.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0250878.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "SEX": "cov_sex", "AGE": "cov_age", "ED": "cov_education",
    "YEAE": "cov_years_experience", "GRADE": "cov_grade", "JOB": "cov_job",
    "FIRM": "cov_firm", "IND": "cov_industry", "SIZE": "cov_firm_size",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()

    sib_cols = [c for c in df.columns if c.startswith("SIB")]
    cq_cols = [c for c in df.columns if c.startswith("CQ")]
    ks_cols = [c for c in df.columns if c.startswith("KS")]
    ocd_cols = [c for c in df.columns if c.startswith("OCD")]

    melt_scale(df, sib_cols, "li_2021_sustainable_innov_behav.csv")
    melt_scale(df, cq_cols, "li_2021_cultural_intelligence.csv")
    melt_scale(df, ks_cols, "li_2021_knowledge_sharing.csv")
    melt_scale(df, ocd_cols, "li_2021_org_cultural_diversity.csv")


if __name__ == "__main__":
    convert()
