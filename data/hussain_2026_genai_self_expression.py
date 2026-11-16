#!/usr/bin/env python3
# Source: https://zenodo.org/records/23231886
# DOI: 10.5281/zenodo.23231886 (data; no paper DOI on the record)
#   Hussain D, Li S, Shahzad Y (2026). Dataset for "More Scaffold Than Mirror:
#   How Outsourcing Self-Expression to Generative AI Relates to Self-Concept
#   Clarity and Digital Flourishing". Zenodo.
# Data: "Numeric data.xlsx", sheets Data (484 x 22) and Codebook.
# License: CC BY 4.0 (Zenodo record).
# Codebook: the workbook's Codebook sheet (demographic codes; every item block
#   "Five-point Likert scale (1-5)", constructs not named).
#
# Counts: 484 rows; no N on the record to compare.
# Tables (1-5, codes as deposited), the three constructs the title names:
#   hussain_2026_ai_self_expression  ASO1-3, outsourcing self-expression to
#                                    generative AI
#   hussain_2026_self_concept_clarity  SCC1-3
#   hussain_2026_digital_flourishing   DF1-4
# Not shipped: SRAR1-3 and PASI1-3. Neither construct is named in the deposit
#   or the title, the codebook calls the second block "ASI1-ASI3" while the data
#   say PASI, and no paper was found; held out rather than shipped under a
#   guessed name.
# id = row index. Covariates: gender, age band, education, current activity,
#   generative-AI use frequency, use orientation (codes; labels in Codebook).
# Item text: not shipped -- none in the deposit.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://zenodo.org/api/records/23231886/files/Numeric%20data.xlsx/content"
SPEC = {
    "hussain_2026_ai_self_expression": ["ASO1", "ASO2", "ASO3"],
    "hussain_2026_self_concept_clarity": ["SCC1", "SCC2", "SCC3"],
    "hussain_2026_digital_flourishing": ["DF1", "DF2", "DF3", "DF4"],
}
NOT_SHIPPED = ["SRAR1", "SRAR2", "SRAR3", "PASI1", "PASI2", "PASI3"]
COVS = {"Gender": "cov_gender", "Age": "cov_age_band", "Education": "cov_education",
        "Current_activity": "cov_current_activity", "AI_usage": "cov_ai_use",
        "Use_orientation": "cov_use_orientation"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Data")
    assert d.shape == (484, 22), d.shape
    used = set(COVS) | set(NOT_SHIPPED)
    for cols in SPEC.values():
        used |= set(cols)
    assert used == set(d.columns), set(d.columns) ^ used
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    allowed = set(range(1, 6))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, cols in SPEC.items():
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
