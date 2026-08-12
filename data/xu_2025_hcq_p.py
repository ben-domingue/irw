#!/usr/bin/env python3
# Source: https://peerj.com/articles/19562/ (PMC12164812)
# DOI: 10.7717/peerj.19562
#
# Xu et al. (2025), "Adaptation and validation of the Chinese version of
# the Hospice Comfort Questionnaire-Patient (HCQ-P)." PeerJ. CC BY 4.0.
# N=360. 49-item HCQ-P, 1-6 Likert. Found via irw_discover_pmc.py (Europe
# PMC "Satisfaction with Life Scale" query against PeerJ -- a full-text
# match, not a title match).
#
# QC note: the archive has two candidate data files -- s001.xlsx and
# s002.xlsx. s002.xlsx (id + 49 items only) is what irw_discover_pmc.py's
# auto-triage picked (it reads the first tabular file in the zip's own
# order, not the "best" one). s001.xlsx has the SAME 49 items PLUS 12
# demographic/clinical covariates and is used here instead -- do not
# switch back to s002.xlsx, it's a strict subset. Two rows have a
# non-numeric "year" (age) value (one stray digit-string, one garbage
# "z w") -- coerced to NaN via pd.to_numeric rather than dropped, since a
# bad covariate value shouldn't cost the row's item responses. A free-text
# cancer-diagnosis column ("diag-eng", e.g. "Cervical Cancer Surgery") is
# dropped rather than kept as a covariate -- too heterogeneous/free-form to
# be a clean covariate; the coded diag/oper/chem/radio columns already
# capture the clinically relevant categories.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

OUT_NAME = "xu_2025_hcq_p"
SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12164812/supplementaryFiles"
MEMBER = "peerj-13-19562-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "sex": "cov_gender",
    "year": "cov_age",
    "edu": "cov_education",
    "marry": "cov_marital_status",
    "cons": "cov_medical_expenses",
    "long": "cov_disease_duration",
    "oper": "cov_operation_history",
    "chem": "cov_chemotherapy_history",
    "radio": "cov_radiotherapy_history",
    "lied": "cov_life_education",
    "work": "cov_occupation_type",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())
    for c in cov_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    item_cols = [c for c in df.columns if c.startswith("Q")]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
