"""Aziz et al. (2020), beliefs about antihypertensive medication and adherence
-- PeerJ 8:e8286, CC BY 4.0.

Two instruments, each its own table:

  * BMQ (Beliefs about Medicines Questionnaire), 18 items, 1-5
  * MMAS-8 medication adherence, 8 items, 0-4

The sheet interleaves the authors' own subscale totals with the items
(`Specific Necessity` after B29, `General Harm` after B8, `Adherence Level`
after C8); those are composites and are excluded. The B block is not in
numerical order in the file and is not renumbered here -- each item keeps its
source number so it stays matchable to the published BMQ.

The deposit has no respondent identifier, so row position is the id.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

from irw_validate.compat import run_qc

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7717/peerj.8286"
PMCID = "PMC7075362"
MEMBER = "peerj-08-8286-s007.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {"aziz_2020_bmq": ("B", (1, 5)), "aziz_2020_adherence": ("C", (0, 4))}

COV_COLS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Ethnicity": "cov_ethnicity",
    "Educational_level": "cov_education",
    "Monthly_income": "cov_monthly_income",
    "Marital_status": "cov_marital_status",
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), sheet_name="Sheet1")


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)

    cov = raw[["id"] + list(COV_COLS)].rename(columns=COV_COLS)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (letter, (lo, hi)) in SCALES.items():
        item_cols = [c for c in raw.columns
                     if str(c).startswith(letter) and str(c)[1:].isdigit()]
        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        assert long["resp"].between(lo, hi).all(), table
        assert not long.duplicated(["id", "item"]).any(), table
        assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, [(c.name, c.detail) for c in bad]

        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
