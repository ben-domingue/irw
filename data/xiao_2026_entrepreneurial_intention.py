from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0352807
# DOI: 10.1371/journal.pone.0352807
# Xiao et al. (2026), "Linking entrepreneurial spirit and entrepreneurial
# environment perception to entrepreneurial intention: Moderation by
# entrepreneurial role models". S2 File, sheet "Raw Data" (header on row
# 2). CC BY 4.0. N=1389, all items 1-5 Likert. 40 items across 6
# constructs: innovativeness (Inn1-4), proactiveness (Pro1-5), perceived
# policy support (PPS1-7), perceived access to finance (PAF1-8),
# perceived entrepreneurship education (PEE1-10), entrepreneurial role
# models (RM1-2), entrepreneurial intention (In1-4). Two blocks in the
# same raw file (IC1-7, CS1-11) are excluded -- they have no entry in the
# accompanying Variable Codebook sheet, so their construct/scale is
# undocumented.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0352807.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Gender": "cov_gender",
    "Academic_Year": "cov_academic_year",
    "Education_Level": "cov_education_level",
    "Major_Group": "cov_major_group",
    "Family_Location": "cov_family_location",
    "Only_Child": "cov_only_child",
    "Household_Income": "cov_household_income",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Raw Data", header=1)
    df = df.rename(columns={"Respondent_ID": "id", **COV_COLS})

    # Explicit allowlist rather than prefix matching, since "In1-4"
    # (intention) would otherwise also swallow "Inn1-4" (innovativeness).
    item_cols = ([f"Inn{i}" for i in range(1, 5)]
                 + [f"Pro{i}" for i in range(1, 6)]
                 + [f"PPS{i}" for i in range(1, 8)]
                 + [f"PAF{i}" for i in range(1, 9)]
                 + [f"PEE{i}" for i in range(1, 11)]
                 + [f"RM{i}" for i in range(1, 3)]
                 + [f"In{i}" for i in range(1, 5)])
    missing = [c for c in item_cols if c not in df.columns]
    assert not missing, f"missing expected item columns: {missing}"

    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "xiao_2026_entrepreneurial_intention.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
