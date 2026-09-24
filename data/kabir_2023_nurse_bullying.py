#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10480219
# DOI: 10.1038/s41598-023-41594-4
# "Association of workplace bullying and burnout with nurses' suicidal
# ideation in Bangladesh" (Kabir, Chowdhury, Roy, Chowdhury, Islam, Chomon,
# Akter & Hossain, 2023), Scientific Reports 13:14641.
# Data: 41598_2023_41594_MOESM2_ESM.csv (Supplementary file 2, "Data of the
#       study"), fetched via the Europe PMC supplementaryFiles endpoint for
#       PMC10480219. The other supplement (MOESM1_ESM.docx) is Tables S1-S2
#       (regression output by collection mode); the rest are figure images.
# License: CC BY 4.0 (article licence in the Europe PMC full-text record).
#          The data are article-attached SI, so the article licence governs.
#
# Item text: not shipped -- item labels are positional (snaq_1..9, bms_1..10,
#   sidas_1..5) and neither the paper nor its supplements print the item
#   wording; it lives in the published instruments (S-NAQ: Notelaers et al.
#   2019; BMS-10: Malach-Pines 2005; SIDAS: van Spijker et al. 2014). The CSV
#   has no variable or value labels at all (plain CSV, both levels empty).
#
# Multi-scale split, per the paper's "Measurement tools" section (three
# instruments, administered on successive pages of one questionnaire):
#   - S-NAQ-9 workplace bullying, 9 items, 1 never .. 5 daily
#   - BMS-10 Burnout Measure short version, 10 items, 1 never .. 7 always
#   - SIDAS-5 suicidal ideation attributes, 5 items, 0..10; item 2
#     (controllability) is reverse-scored in the paper's total. The raw
#     sidas_2 ships; sidas_2_reverse (= 10 - sidas_2) is dropped as a recode.
#     No skip rule was applied in the file: respondents with sidas_1 = 0
#     still answered items 2-5 with varied values, so those are responses.
# All three tables carry the same covariates and the same row-index id, so
# respondents link across them.
#
# Three pairs of rows are identical on all 47 columns (including a one-decimal
# age and all 24 items); these are double entries and the second copy of each
# is dropped (1264 -> 1261 respondents). The paper reports 1264 analysed.
# Some items carry 2-10 NAs despite the paper's "excluded missing data"; they
# are dropped at the response level. No fractional item values anywhere.
# Data collection mode (online/offline) is not in the file.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10480219/supplementaryFiles"
CSV = "41598_2023_41594_MOESM2_ESM.csv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV = {
    "Gender": "cov_gender",
    "Age_cont": "cov_age",                       # years (one decimal as recorded)
    "Marital_status_new": "cov_marital_status",
    "Educational_degree": "cov_education",
    "Income_cat_new": "cov_income_bdt",          # monthly, banded
    "Smoking_status": "cov_smoking",
    "Type_of_job_new": "cov_job_type",           # government / private
    "Level_of_hospital_new": "cov_hospital_level",
    "Division_of_job_center": "cov_division",    # administrative division of workplace
    "Department_new": "cov_department",
    "Working_hours_cat": "cov_weekly_hours",     # banded
    "Total_experience_cat": "cov_experience",    # banded
    "Sufficient_equipment": "cov_sufficient_equipment",
}
SNAQ = [f"snaq_{i}" for i in range(1, 10)]
BMS = [f"bms_{i}" for i in range(1, 11)]
SIDAS = [f"sidas_{i}" for i in range(1, 6)]
SKIP = {
    "SNAQ_total_score": "S-NAQ sum score (composite)",
    "SNAQ_cat": "S-NAQ cut-off category (derived)",
    "BMS_total_score": "BMS sum score (composite)",
    "BMS_mean_score": "BMS mean score (composite)",
    "Burnout_bi": "BMS >= 4 dichotomy (derived)",
    "sidas_2_reverse": "10 - sidas_2 (reverse-scored recode)",
    "SIDAS_total_score": "SIDAS sum score (composite)",
    "H_Ideation_bi": "SIDAS >= 21 dichotomy (derived)",
    "Age_cat": "banding of Age_cont (derived)",
    "Division_of_work_place": "4-level collapse of Division_of_job_center (derived)",
}

TABLES = [
    ("kabir_2023_snaq", SNAQ, set(range(1, 6)), "workplace bullying"),
    ("kabir_2023_bms10", BMS, set(range(1, 8)), "burnout"),
    ("kabir_2023_sidas", SIDAS, set(range(0, 11)), "suicidal ideation"),
]


def load() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            break
        time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")
    with zipfile.ZipFile(BytesIO(r.content)) as z:
        return pd.read_csv(BytesIO(z.read(next(n for n in z.namelist() if n.endswith(CSV)))))


def finish(d, items, table, permitted, construct):
    covs = list(COV.values())
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs,
                                        var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all(), f"{table}: fractional resp (imputation?)"
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + sorted(covs)]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert set(long["resp"]).issubset(permitted), f"{table}: resp off-scale"
    assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    assert long["item"].nunique() == len(items) > 1, f"{table}: item count"
    report = irw_validate.validate_frame(
        long, label=table, profile="upload",
        context={"permitted_values": {i: permitted for i in items},
                 "item_constructs": {i: construct for i in items}})
    print(report)
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert() -> None:
    df = load()
    assert len(df) == 1264, len(df)
    used = set(COV) | set(SNAQ) | set(BMS) | set(SIDAS) | set(SKIP)
    unaccounted = [c for c in df.columns if c not in used]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    assert set(df.columns) - set(SKIP) == set(COV) | set(SNAQ) | set(BMS) | set(SIDAS)
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert ((df["sidas_2"] + df["sidas_2_reverse"]).dropna() == 10).all()

    dup = df.duplicated()
    assert dup.sum() == 3, dup.sum()
    print(f"  [drop] {dup.sum()} exact duplicate rows (double entries)")
    df = df[~dup].reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    d = df.rename(columns=COV)

    names = [t for t, _, _, _ in TABLES]
    assert len(names) == len(set(names)), "duplicate output filenames"
    for table, items, permitted, construct in TABLES:
        finish(d, items, table, permitted, construct)


if __name__ == "__main__":
    convert()
