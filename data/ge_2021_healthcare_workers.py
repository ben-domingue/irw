"""Ge et al. (2021), effort-reward imbalance, job satisfaction and work
engagement among healthcare workers in Sichuan -- BMC Public Health 21:195,
CC BY 4.0. Data are the Sichuan subsample (n = 1,327) of the Chinese Sixth
National Health and Services Survey, 2018.

Three instruments, each its own table:

  * ERI, Effort-Reward Imbalance scale, 16 items, 1-4
  * Job satisfaction, 10 items, 1-6 (a scale built for the survey)
  * UWES-17, Utrecht Work Engagement Scale (Chinese version), 17 items, 0-6

The authors' composites (`Effort`, `Reward`, `ERR`, `Overcommitment`, `JS`,
`WE`, `Vigor`, `Dedication`, `Absorption`) are excluded. Each is an exact sum
of its items (ERR is Effort / (Reward * 3/7)), which is how the item-to-subscale
map below was recovered -- the paper does not give it:

  * ERI: B1-B3 effort, B4-B9 overcommitment, B10-B16 reward. The file does NOT
    follow the paper's effort/reward/overcommitment listing order.
  * UWES: vigour D1 D4 D8 D12 D15 D17, dedication D2 D5 D7 D10 D13,
    absorption D3 D6 D9 D11 D14 D16 -- the standard UWES-17 order.

Every ERI item enters its subscale sum with weight +1, so any negatively
worded reward items were already recoded in the deposit (or were worded
positively in this version). Direction is not recoverable from the file.

Job satisfaction items keep their source names C1-C10. The paper's Table 2
gives a per-item mean for each named aspect, but not in the column order.

`A2.1` (age band) is derived from `A2` and is dropped. `E` is self-rated
health, a single item and the paper's outcome; it is carried as a covariate.
Every covariate code below was checked against the counts in Table 2.

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

DOI = "10.1186/s12889-021-10233-w"
PMCID = "PMC7821543"
MEMBER = "12889_2021_10233_MOESM1_ESM.xls"
SUPPL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/"
         "{pmcid}/supplementaryFiles?includeInlineImage=false")
UA = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "ge_2021_eri": ("B", 16, (1, 4)),
    "ge_2021_job_satisfaction": ("C", 10, (1, 6)),
    "ge_2021_uwes": ("D", 17, (0, 6)),
}

COV_COLS = {
    "A1": ("cov_gender", {1: "male", 2: "female"}),
    "A2": ("cov_age", None),
    "A3": ("cov_marital_status", {1: "single, divorced or widowed",
                                  2: "married"}),
    "A4": ("cov_education", {1: "junior college or below", 2: "bachelor",
                             3: "master or above"}),
    "A5": ("cov_specialty", {1: "public health professional", 2: "nurse",
                             3: "physician"}),
    "A6": ("cov_technical_title", {1: "none", 2: "primary", 3: "middle",
                                   4: "vice-senior or above"}),
    "A7": ("cov_service_years", {1: "<5", 2: "5-9", 3: "10-19", 4: "20-29",
                                 5: ">=30"}),
    "A8": ("cov_weekly_hours", {1: "<=40", 2: ">40"}),
    "A9": ("cov_night_shifts_per_month", {1: "none", 2: "1-7", 3: ">=8"}),
    "A10": ("cov_institution_grade", {1: "community or township",
                                      2: "second-class or above"}),
    "E": ("cov_self_rated_health", None),
}

COMPOSITES = {"Effort": ["B1", "B2", "B3"],
              "Overcommitment": [f"B{i}" for i in range(4, 10)],
              "Reward": [f"B{i}" for i in range(10, 17)],
              "JS": [f"C{i}" for i in range(1, 11)],
              "WE": [f"D{i}" for i in range(1, 18)]}


def fetch() -> pd.DataFrame:
    raw = requests.get(SUPPL.format(pmcid=PMCID), headers=UA, timeout=120)
    raw.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(raw.content)) as z:
        return pd.read_excel(io.BytesIO(z.read(MEMBER)), sheet_name="Database")


def convert() -> None:
    raw = fetch().reset_index(drop=True)
    assert len(raw) == 1327, len(raw)
    for total, items in COMPOSITES.items():
        assert (raw[items].sum(axis=1) == raw[total]).all(), total
    raw.insert(0, "id", raw.index + 1)

    cov = raw[["id"]].copy()
    for src, (name, labels) in COV_COLS.items():
        cov[name] = raw[src].map(labels) if labels else raw[src]
        assert cov[name].notna().all(), name
    cov_cols = [c for c in cov.columns if c != "id"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (letter, n_items, (lo, hi)) in SCALES.items():
        item_cols = [f"{letter}{i}" for i in range(1, n_items + 1)]
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
