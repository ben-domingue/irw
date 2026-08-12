#!/usr/bin/env python3
# Source: https://peerj.com/articles/18709/ (PMC11670754)
# DOI: 10.7717/peerj.18709
#
# Altahla et al. (2024), "Quality of life and subjective well-being
# comparison between traumatic, nontraumatic chronic spinal cord injury,
# and healthy individuals in China." PeerJ. CC BY 4.0. N=189. Found via
# irw_discover_pmc.py (Europe PMC "Satisfaction with Life Scale" query
# against PeerJ).
#
# QC note: the single supplementary file bundles WHOQOL-BREF (26 items,
# verbatim item wording, 1-5 scale) and the Satisfaction with Life Scale
# (5 items, verbatim wording, 1-7 scale) back-to-back in one sheet, plus
# 13 demographic/clinical columns that irw_discover_pmc.py's auto-triage
# counted as items rather than covariates -- split into 2 IRW files here
# per datastandard.md's one-scale-per-file rule, with the 13 columns moved
# to cov_*. Item columns use the source's own verbatim question text as
# header, which is why they're renamed here to whoqol_N / swls_N
# (sequential, in the source's own item order) rather than kept verbatim
# -- full sentences make poor item identifiers.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11670754/supplementaryFiles"
MEMBER = "peerj-12-18709-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "cov_1": "cov_gender",
    "cov_2": "cov_married",
    "cov_3": "cov_age_group",
    "cov_4": "cov_education",
    "cov_5": "cov_employed",
    "cov_6": "cov_injury_duration",
    "cov_7": "cov_age_at_injury",
    "cov_8": "cov_injury_type",
    "cov_9": "cov_ais_severity",
    "cov_10": "cov_injury_level",
    "cov_11": "cov_paralysis_type",
    "cov_12": "cov_injury_cause",
    "cov_13": "cov_injury_state",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))

    cols = list(df.columns)
    id_col, whoqol_cols, swls_cols, cov_source_cols = (
        cols[0], cols[1:27], cols[27:32], cols[32:45])
    assert len(whoqol_cols) == 26 and len(swls_cols) == 5 and len(cov_source_cols) == 13

    df = df.rename(columns={id_col: "id"})
    df = df.rename(columns={c: f"cov_{i+1}" for i, c in enumerate(cov_source_cols)})
    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())
    for c in cov_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    scales = {
        "altahla_2024_whoqol_bref": {c: f"whoqol_{i+1}" for i, c in enumerate(whoqol_cols)},
        "altahla_2024_swls": {c: f"swls_{i+1}" for i, c in enumerate(swls_cols)},
    }

    for out_name, item_rename in scales.items():
        d = df.rename(columns=item_rename)
        item_cols = list(item_rename.values())
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
