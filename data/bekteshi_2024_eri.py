#!/usr/bin/env python3
# Source: https://zenodo.org/records/11149861
# DOI: 10.26641/2307-0404.2025.3.340583
#   Pjetri, E., Shabani, Z., Shala, I., & Bekteshi, A. (2025). "Psychometric
#   properties of the Albanian version of the effort-reward imbalance model
#   in a sample of healthcare workers in Shkodra, Albania hospital."
#   Medicni perspektivi, 30(3), 41-49.
#   (CC BY 4.0; same N = 219 / 270 nurses, 23-item ERI, Shkodra Regional
#   Hospital, Nov-Dec 2023.)
#   Data: Bekteshi, A. (2024). "Data ERI questionnaire." Zenodo.
# Data: Zenodo 11149861, Data_ERI.xlsx (219 rows x 35 columns; nurses and
#       midwives of the Regional Hospital of Shkodra, Albania).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: not shipped. The xlsx has plain headers only (P1-P23; no label
#   levels exist in an xlsx). The deposit's ERI_questionnaire.docx prints
#   all 23 statements, English and Albanian side by side, numbered 1-23,
#   with no response options; tying statement k to Pk is positional, so it
#   needs a verify_<table>.R. The paper's Table 1 gives the six anchors.
#
# Tables (item codes are the source column names). The paper (Methods,
#   Table 1): all 23 items on a modified 6-point scale, 1 = don't agree at
#   all, 2 = moderately disagree, 3 = disagree, 4 = agree, 5 = moderately
#   agree, 6 = strongly agree; effort 6 items, reward 11, overcommitment 6.
#   bekteshi_2024_eri_effort          P1-P6   (Effort = their sum, asserted)
#   bekteshi_2024_eri_reward          P7-P17  (Reward = their sum, asserted;
#       items stored as answered, not reverse-coded)
#   bekteshi_2024_eri_overcommitment  P18-P23 (Over-commitment = their sum,
#       asserted)
#
# Dropped:
#   - Effort, Reward, Over-commitment, Effort-reward ratio (composites).
#   - Nr.: row number; replaced by the row index.
#   - Hospital: constant "Shkoder".
#   - 3 rows that duplicate another row in every column but Nr. (Nr. 188,
#     45, 199 repeat Nr. 37, 41, 97 -- age, years, department and all 23
#     answers equal); the later copy is dropped, leaving 216.
# id: row index.
# Covariates: cov_gender (F/M; two lower-case "m" upper-cased),
#   cov_education (Bachelor/Master), cov_age, cov_working_years,
#   cov_department, cov_position (Nurse/Midwife).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/11149861/files/Data_ERI.xlsx/content"


def p(a, b):
    return [f"P{i}" for i in range(a, b + 1)]


TABLES = {
    "bekteshi_2024_eri_effort": (p(1, 6), "Effort"),
    "bekteshi_2024_eri_reward": (p(7, 17), "Reward"),
    "bekteshi_2024_eri_overcommitment": (p(18, 23), "Over-commitment"),
}
COVS = {"Gender": "cov_gender", "Education": "cov_education",
        "Age": "cov_age", "Working years": "cov_working_years",
        "Department": "cov_department", "Positon": "cov_position"}
DROPPED = {"Nr.", "Hospital", "Effort-reward ratio"} | \
    {t for _, t in TABLES.values()}
ALLOWED = {1, 2, 3, 4, 5, 6}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (219, 35), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | set(COVS) | DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    for its, total in TABLES.values():
        assert (d[its].sum(axis=1) == d[total]).all(), total
    assert (d["Hospital"] == "Shkoder").all() and d["Nr."].is_unique
    assert not d[sorted(items)].isna().any().any()

    dup = d.drop(columns="Nr.").duplicated()
    assert sorted(d.loc[dup, "Nr."]) == [45, 188, 199]
    d = d[~dup].reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d["Gender"] = d["Gender"].str.upper()
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, _) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - ALLOWED
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() == 216
        assert long["item"].nunique() == len(its)
        pv = {i: ALLOWED for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
