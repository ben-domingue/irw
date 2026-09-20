"""Fan et al. (2026), family caregivers of haematopoietic stem cell transplant
patients -- PeerJ 14:e21527, CC BY 4.0.

Two instruments reach IRW from the deposited raw file, both with full English
item labels in the column names:

  * Simplified Coping Style Questionnaire (SCSQ), 20 items, 0-3
  * Caregiver Burden Inventory (CBI, Novak & Guest 1989), 24 items, 0-4

The file's third block, `social_support_01..32`, is NOT a 32-item scale and is
deliberately left out. It is the Social Support Rating Scale (SSRS), whose 10
questions are expanded here into one column per response option: items 01-10
are 1-4 ratings, 20-29 are 0/1 checkbox columns of a single multi-select
question, and `social_support_20_any_emotional_support` is constant. Melting
that block would put four different response scales in one table and invent 22
items that the instrument does not have.
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

DOI = "10.7717/peerj.21527"
PMCID = "PMC13398390"
MEMBER = "peerj-14-21527-s001.xlsx"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

COV_COLS = {
    "caregiver_gender": "cov_gender",
    "caregiver_education_level": "cov_education",
    "caregiver_marital_status": "cov_marital_status",
    "caregiver_employment_status": "cov_employment",
    "caregiver_relationship_to_patient": "cov_relationship",
    "caregiving_duration_months": "cov_caregiving_months",
    "daily_care_hours": "cov_daily_care_hours",
    "caregiver_self_rated_health": "cov_self_rated_health",
    "patient_diagnosis": "cov_patient_diagnosis",
}

SCALES = {
    # Simplified Coping Style Questionnaire, 20 items, 0 (never) - 3 (often)
    "fan_2026_coping": ("coping_", (0, 3)),
    # Caregiver Burden Inventory (CBI), 24 items, 0 (never) - 4 (nearly always)
    "fan_2026_care_burden": ("care_burden_", (0, 4)),
}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        with z.open(MEMBER) as fh:
            return pd.read_excel(io.BytesIO(fh.read()), sheet_name="Raw_Data")


def convert() -> None:
    raw = fetch()
    raw = raw.rename(columns={"record_id": "id"})

    # `caregiver_birth_ym` and `patient_birth_ym` are deposited birth
    # year-months and are left out rather than republished.
    cov = raw[["id"] + list(COV_COLS)].rename(columns=COV_COLS)
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (prefix, (lo, hi)) in SCALES.items():
        item_cols = [c for c in raw.columns if c.startswith(prefix)]
        wide = raw[["id"] + item_cols].merge(cov, on="id")
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        # item names keep the source's descriptive labels, which are the only
        # item identifiers the deposit carries.
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
