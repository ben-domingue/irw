#!/usr/bin/env python3
# Source: https://www.sciencedirect.com/science/article/pii/S2405844024126514 (PMC11385760)
# DOI: 10.1016/j.heliyon.2024.e36620
#
# Sun W, Tohirovich Dedahanov A, Li WP, Young Shin H. (2024). "Sanctions
# and opportunities: Factors affecting China's high-tech SMEs adoption of
# artificial intelligence computing leasing business." Heliyon. CC BY 4.0.
# N=281. Found via irw_discover_pmc.py (Europe PMC "attachment style"
# query against Heliyon -- a full-text match, not a title match).
#
# QC note: the single supplementary file bundles 6 distinct 3-item
# constructs (a classic technology-adoption/UTAUT-style survey structure)
# -- split here into 6 IRW files per datastandard.md's one-scale-per-file
# rule, rather than shipped as one 18-item table. All 18 items share the
# same 1-7 scale. No covariates or PII in the source file.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11385760/supplementaryFiles"
MEMBER = "mmc1.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "sun_2024_innovation": ["innovation1", "innovation2", "innovation3"],
    "sun_2024_risk": ["Risk1", "Risk2", "Risk3"],
    "sun_2024_performance_expectancy": ["PerformanceE1", "PerformanceE2", "PerformanceE3"],
    "sun_2024_price_value": ["Pricevalue1", "Pricevalue2", "Pricevalue3"],
    "sun_2024_task_tech_fit": ["TTF1", "TTF2", "TTF3"],
    "sun_2024_usage": ["Usage1", "Usage2", "Usage3"],
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"NO": "id"})

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
