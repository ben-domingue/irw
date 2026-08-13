#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11892457
# DOI: 10.7717/peerj.19057
#
# Allen MT, Interian A, Reddy V, Rodriguez K, Myers CE (2025), "Self-reported
# history of head injury is associated with cognitive impulsivity on a delay
# discounting task." PeerJ. CC BY 4.0.
#
# Supplementary file peerj-13-19057-s001.xlsx, sheet "questionnaire_scoring",
# holds one row per subject with several raw-item instruments plus their
# pre-computed subscale totals (e.g. BDI-II, BAS_*, MCQ_geomean_k, ATQ_total,
# UPPS_*) -- the totals are excluded as aggregates per datastandard.md.
# Three raw-item instruments are extracted here as separate IRW files:
#   - mc1..mc27: Monetary Choice Questionnaire (Kirby delay-discounting task)
#     binary choices, 1=smaller-sooner, 2=larger-later (Kaplan et al. 2016
#     scoring). -> allen_2025_delaydiscount.csv
#   - bi1..bi16: short Barratt Impulsiveness items (0-3). -> allen_2025_bis.csv
#   - u1..u20: UPPS-P impulsive behavior items (1-4). -> allen_2025_upps.csv
# Missing cells are coded "." in the raw file. Rows with ok_to_use=="test_only"
# are pilot/test administrations, not real participants, and are dropped.
# The "be"/"bb"/"ba"/"a" (BDI-II, BAS/BIS composite item pools, ATQ) prefixes
# have ~54% missingness (only administered to a subset) and are left out of
# this script; could be added later if that subset is independently useful.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11892457/supplementaryFiles"
MEMBER = "peerj-13-19057-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def load_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    summary = pd.read_excel(io.BytesIO(zf.read(MEMBER)), sheet_name="summary")
    qs = pd.read_excel(io.BytesIO(zf.read(MEMBER)), sheet_name="questionnaire_scoring")

    # "id" and "SubjID" are duplicate columns in the raw file with identical
    # values; keep "id" and drop the redundant one. IDs are a mix of plain
    # integers and cohort-coded strings (e.g. "001SP23") -- per
    # datastandard.md, keep as string rather than forcing numeric coercion.
    qs = qs[qs["SubjID"].notna()].drop(columns=["SubjID"]).copy()
    qs["id"] = qs["id"].astype(str).str.strip()
    qs = qs[qs["id"] != "."]

    # drop pilot/test-only administrations
    test_ids = set(
        summary.loc[summary["ok_to_use"] == "test_only", "SubjID"].astype(str).str.strip()
    )
    qs = qs[~qs["id"].isin(test_ids)].reset_index(drop=True)
    assert qs["id"].nunique() == len(qs)
    return qs


def make_scale(df: pd.DataFrame, items: list[str], out_name: str):
    items = [c for c in items if c in df.columns]
    long = df[["id"] + items].melt(id_vars=["id"], value_vars=items,
                                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].replace(".", pd.NA)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / out_name
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_raw()

    mc_items = [f"mc{i}" for i in range(1, 28)]
    bi_items = [f"bi{i}" for i in range(1, 17)]
    u_items = [f"u{i}" for i in range(1, 21)]

    make_scale(df, mc_items, "allen_2025_delaydiscount.csv")
    make_scale(df, bi_items, "allen_2025_bis.csv")
    make_scale(df, u_items, "allen_2025_upps.csv")


if __name__ == "__main__":
    convert()
