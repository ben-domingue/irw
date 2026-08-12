#!/usr/bin/env python3
# Source: https://www.nature.com/articles/s41598-024-84829-8 (PMC11729910)
# DOI: 10.1038/s41598-024-84829-8
#
# Lopez-Gomez et al. (2025), "Psychometric study of the Maslach Burnout
# Inventory-Student Survey on Thai university students." Scientific
# Reports. CC BY 4.0. N=432. Standard MBI-SS, 15 items across its 3
# canonical subscales, each treated as its own IRW file per
# datastandard.md's "subscale treated as a distinct construct" rule:
# Exhaustion (5 items), Cynicism (4 items), Professional Efficacy (6
# items). All items share the same 0-6 frequency scale ("Never" to
# "Every day"). Found via irw_discover_pmc.py (Europe PMC "Strengths and
# Difficulties Questionnaire" query against Scientific Reports -- a
# full-text match, not a title match; this paper isn't about the SDQ, the
# term just appears somewhere in its body text); supplementary file
# fetched through Europe PMC's supplementaryFiles endpoint (PMC11729910).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11729910/supplementaryFiles"
MEMBER = "41598_2024_84829_MOESM1_ESM.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "lopezgomez_2025_mbi_exhaustion": ["EX1", "EX2", "EX3", "EX4", "EX5"],
    "lopezgomez_2025_mbi_cynicism": ["CY1", "CY2", "CY3", "CY4"],
    "lopezgomez_2025_mbi_efficacy": ["PE1", "PE2", "PE3", "PE4", "PE5", "PE6"],
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"ID": "id"})

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"]]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
