#!/usr/bin/env python3
# Source: https://zenodo.org/records/24193363
# DOI: 10.5281/zenodo.24193363 (data)
#   Cunha M, Santos C, Monteiro B, Galhardo A (2026). Dataset for the Validation of the European
#   Portuguese Artificial Intelligence Anxiety Scale (AIAS) [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: AIAS_Data_Anonymized.csv, 302 rows (the record describes 299 adults aged 18-70; three rows
#   answer the PHQ-4 only, so they are in cunha_2026_phq4 and absent from the other two tables).
# Tables (item = the deposit's column name):
#   cunha_2026_aias    -- AIAS_1..AIAS_21, Artificial Intelligence Anxiety Scale (Wang & Wang), 1-7
#   cunha_2026_psyflex -- Psyflex_1..6, PsyFlex psychological flexibility, 1-5
#   cunha_2026_phq4    -- PHQ4_1..4, Patient Health Questionnaire-4, 0-3
#   For every complete row the deposit's TOT_AIAS / TOT_PSY / TOT_PHQ4 equal the plain sums of the
#   stored items, so the items are stored as scored (no reversals in these three instruments).
# Covariate: cov_age. Not carried: Sex, Education, Field, AI_Freq (numeric codes with no key in the
#   deposit); subscale and total scores.
# Item text: not shipped -- the CSV has codes only; the Portuguese AIAS wording is in the authors'
#   validation paper, not in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/24193363/files/AIAS_Data_Anonymized.csv/content"
SCALES = {"cunha_2026_aias": ("AIAS_", 21, "TOT_AIAS", (1, 7)),
          "cunha_2026_psyflex": ("Psyflex_", 6, "TOT_PSY", (1, 5)),
          "cunha_2026_phq4": ("PHQ4_", 4, "TOT_PHQ4", (0, 3))}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 302
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["Age"]
    covs = ["cov_age"]
    for name, (pre, k, tot, (lo, hi)) in SCALES.items():
        items = [f"{pre}{i}" for i in range(1, k + 1)]
        full = d[items].notna().all(axis=1)
        assert (d.loc[full, items].sum(axis=1) == d.loc[full, tot]).all(), name
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all() and (t["resp"] % 1 == 0).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
