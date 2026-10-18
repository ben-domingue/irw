#!/usr/bin/env python3
# Source: https://zenodo.org/records/12619790
# DOI: 10.5281/zenodo.12619790 (this deposit). The SAME file is also
#   deposited at Mendeley, 10.17632/txm4zf982j, titled "Effects of Wages on
#   the Well-being of University Teachers in China" -- which is where the
#   author name comes from: the Zenodo record's creator field holds only "/".
#   Both keys were unworked `good` keys on the repos ledger (irw#3077); this
#   script ships the deposit once and the Mendeley key is statused as the
#   duplicate it is.
#   Yang, Z. (2024). "Effects of Wages on the Well-being of University
#   Teachers in China." Zenodo / Mendeley Data.
# Data: Zenodo 12619790, "work well-being dataset.sav" (283 rows x 21
#       columns; university teachers in China).
# License: CC BY 4.0 (Zenodo record metadata, API; the Mendeley twin reports
#       cc-by-4.0 through DataCite as well).
#
# Item text: NOT shipped, and BOTH label levels were checked -- which is the
#   point worth recording. pyreadstat gives:
#     - column_names_to_labels: Q1-Q5 carry real Chinese stems ("我的性别是：",
#       "我的高校教龄是："), but Q6-Q20 -- every shipped item -- carry only the
#       variable name back ("Q6" -> "Q6"). So the item STEMS are absent.
#     - variable_value_labels: present for all 20 Qs, and for Q6-Q20 they are
#       the five Chinese agreement anchors (1 不同意 .. 5 同意).
#   So this file has the response OPTIONS but not the questions. Shipping
#   option_text with no item_text is exactly what irw#1770 forbids when the
#   stems exist one hop away, and here they do: the wording is in the paper
#   behind the Mendeley title. That is where the text is.
#
# Tables:
#   yang_2024_teacher_wellbeing  Q6-Q20, 15 items, 1-5 (1 不同意 disagree ..
#       5 同意 agree per the file's own value labels).
#
# Dropped, with reasons:
#   ID        -> becomes `id`
#   Q1-Q5     demographics, not items -> cov_* (gender, years teaching,
#             highest degree, academic title, after-tax annual salary band),
#             named from their Chinese variable labels
# id: the file's own ID column (2..308, not contiguous -- carried as given).
# Covariates: cov_gender, cov_teaching_years, cov_education,
#   cov_academic_title, cov_salary_band. These are coded integers whose
#   value labels are Chinese and live only in the .sav, so this script is one
#   of the batch's covariate_labels harvest targets.

import io
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/12619790/files/"
            "work%20well-being%20dataset.sav/content")
TABLE = "yang_2024_teacher_wellbeing"
ITEMS = [f"Q{i}" for i in range(6, 21)]
ALLOWED = {1, 2, 3, 4, 5}
COVS = {"Q1": "cov_gender", "Q2": "cov_teaching_years",
        "Q3": "cov_education", "Q4": "cov_academic_title",
        "Q5": "cov_salary_band"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as fh:
        fh.write(r.content)
        tmp = fh.name
    d, meta = pyreadstat.read_sav(tmp, apply_value_formats=False)
    assert d.shape == (283, 21), d.shape

    # Both label levels, recorded rather than assumed.
    lab = meta.column_names_to_labels
    stemless = [c for c in ITEMS if (lab.get(c) or "").strip() in ("", c)]
    print(f"[labels] variable labels: {len(ITEMS) - len(stemless)}/"
          f"{len(ITEMS)} items carry a stem; value labels: "
          f"{sum(1 for c in ITEMS if meta.variable_value_labels.get(c))}"
          f"/{len(ITEMS)} items carry options")
    assert len(stemless) == len(ITEMS), "some item gained a stem -- re-check item text"

    known = set(ITEMS) | set(COVS) | {"ID"}
    assert set(d.columns) == known, set(d.columns) ^ known
    for c in ["ID"] + list(COVS):
        print(f"[drop-as-non-item] {c} -> "
              f"{'id' if c == 'ID' else COVS[c]}")

    assert d["ID"].is_unique and d["ID"].notna().all()
    d = d.rename(columns={"ID": "id", **COVS})
    d["id"] = d["id"].astype(int)
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() == 15 and long["id"].nunique() == 283

    checks = run_qc(long, permitted_values={i: ALLOWED for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
