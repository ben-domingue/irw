#!/usr/bin/env python3
# Source: https://zenodo.org/records/11270872
# DOI: 10.5281/zenodo.11270872 (data)
#   Castagnetto J, Vivanco L (2024). Data for the article "Professionalism, emotional wellbeing, and
#   dropout intention in health professions students during the pandemic" [Data set]. Zenodo.
#   Paper: Castagnetto JM, Hancco-Monrroy DE, Caballero-Apaza LM et al. (2025). Sci Data 12, 1259.
#   https://doi.org/10.1038/s41597-025-05508-5
# License: CC BY 4.0 (Zenodo record metadata, cc-by-4.0)
# Data: E255-PE-data.csv, 1,707 Peruvian medicine and nursing students (online survey 2020-07-24 to
#   2021-04-16). Codebook: E255-PE-data-dictionary.csv in the same deposit (levels and ranges for
#   every variable).
#
# Tables (item = the deposit's variable name):
#   castagnetto_2024_jse      -- Jefferson Scale of Empathy, 20 items, 1-7
#   castagnetto_2024_jsapnc   -- Jefferson Scale of Attitudes toward Physician-Nurse Collaboration, 15 items, 1-4
#   castagnetto_2024_jeffspll -- Jefferson Scale of Physician Lifelong Learning, 14 items, 1-4
#   castagnetto_2024_selsa    -- Social and Emotional Loneliness Scale for Adults (short), 15 items, 1-7
#   castagnetto_2024_swls     -- Satisfaction with Life Scale, 5 items, 1-5
#   castagnetto_2024_phq4     -- GAD-2 (gad_01, gad_02) + PHQ-2 (phq_01, phq_02), 0-3: together the PHQ-4
# KEYED, not as answered: items whose name ends in "r" are the codebook's "reversed scale" items and
#   are stored reversed -- for every scale the deposited total equals the plain sum of the stored items
#   in all 1,707 rows. Item names keep the "r" so the keying is visible.
# Covariates: cov_sex, cov_age, cov_university (anonymised A-D), cov_university_sector, cov_program
#   (medicine/nursing), cov_academic_year, cov_academic_stage, cov_prior_anxiety_dx, cov_prior_depression_dx.
# Not carried: reg (region geolocated from the respondent's IP address -- dropped, geographic),
#   survey_date and the regional epidemic rates keyed to it, single-item career questions, totals.
# Item text: not shipped -- the codebook names the instrument only ("Item from the Jefferson Scale of
#   Empathy (JSE)"); variable labels n/a (CSV); the wording is in the published instruments
#   (Jefferson scales are licensed by Thomas Jefferson University).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/11270872/files/E255-PE-data.csv/content"
SCALES = {  # table: (prefixes, total columns, (lo, hi))
    "castagnetto_2024_jse": (["jse"], ["jse"], (1, 7)),
    "castagnetto_2024_jsapnc": (["jsapnc"], ["jsapnc"], (1, 4)),
    "castagnetto_2024_jeffspll": (["jeffspll"], ["jeffspll"], (1, 4)),
    "castagnetto_2024_selsa": (["selsa"], ["selsa"], (1, 7)),
    "castagnetto_2024_swls": (["swls"], ["swls"], (1, 5)),
    "castagnetto_2024_phq4": (["gad", "phq"], ["gad", "phq"], (0, 3)),
}


def items_of(d, prefix):
    return [c for c in d.columns if c.startswith(prefix + "_") and c[len(prefix) + 1:].rstrip("r").isdigit()]


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 1707
    d["id"] = range(1, len(d) + 1)
    cov = {"sex": "cov_sex", "age": "cov_age", "uni": "cov_university", "uni_sec": "cov_university_sector",
           "prof": "cov_program", "acad_year": "cov_academic_year", "acad_stage": "cov_academic_stage",
           "anxi_prev": "cov_prior_anxiety_dx", "depre_prev": "cov_prior_depression_dx"}
    d = d.rename(columns=cov)
    covs = list(cov.values())
    for name, (prefixes, totals, (lo, hi)) in SCALES.items():
        items = []
        for p, tot in zip(prefixes, totals):
            it = items_of(d, p)
            assert (d[it].sum(axis=1) == d[tot]).all(), name  # stored items are the keyed scores
            items += it
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
