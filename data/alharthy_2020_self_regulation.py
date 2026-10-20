#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/98326d8m8r
# DOI: 10.17632/98326d8m8r.1
#   Al Harthy, Ibrahim; Al Kalbani, Amal (2020). "Self-Regulation Failure and
#   Academic Achievement: A Profile Model". Mendeley Data (2020-05-14).
# Data: "Self-Regulation Failure and Academic Achievement Data.sav" --
#       221 students x 38 columns: 26 self-regulation-failure items
#       (Q1..Q36 with gaps, 5-point Likert), School/Gender/GPA, and eight
#       Dim1-Dim8 subscale columns.
# License: CC BY 4.0 (Mendeley Data record, data_licence CC BY 4.0).
#
# Item text: not shipped. The .sav carries no variable labels and no value
#   labels at all (checked: column_labels is None for every column,
#   variable_value_labels is empty), and the deposit holds only this one file
#   -- no questionnaire or codebook. The item codes Q1..Q36 are the source's
#   own, kept verbatim, so text can be joined later if the authors publish the
#   instrument.
#
# One table: alharthy_2020_self_regulation -- the 26 retained items, 1-5.
# NOT shipped: Dim1-Dim8 are subscale MEANS (fractional values such as
#   1.3333 = 4/3 and 1.25, i.e. sums over 3- and 4-item facets divided by the
#   facet length), which are composites, not responses.
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = Path(os.environ.get(
    "IRW_OUT_DIR", REPO_ROOT / "automated_finding" / "irw_output"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://data.mendeley.com/public-files/datasets/98326d8m8r/"
            "files/8f0faaa3-b551-4aca-a755-6c2842008e9c/file_downloaded")

COVS = {"School": "cov_school", "Gender": "cov_gender", "GPA": "cov_gpa"}
NAME = "alharthy_2020_self_regulation"


def main() -> None:
    raw = Path(os.environ.get("IRW_RAW_DIR", "/tmp")) / "alharthy_2020.sav"
    if not raw.exists():
        r = requests.get(DATA_URL, headers=UA, timeout=300)
        r.raise_for_status()
        raw.write_bytes(r.content)
    d, _meta = pyreadstat.read_sav(raw, apply_value_formats=False)

    items = [c for c in d.columns if c.startswith("Q")]
    dims = [c for c in d.columns if c.startswith("Dim")]
    assert len(items) == 26 and len(dims) == 8, (items, dims)
    accounted = {"tool#"} | set(COVS) | set(items) | set(dims)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c in dims:
        print(f"  skipped {c}: subscale mean (fractional), a composite")

    assert d["tool#"].nunique() == len(d)
    d = d.rename(columns={"tool#": "id", **COVS})
    covs = sorted(COVS.values())

    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp -> imputation?"
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all(), sorted(t["resp"].unique())
    t["id"] = t["id"].astype(int)
    t = t[["id", "item", "resp"] + covs].reset_index(drop=True)

    assert len(NAME) <= 40
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 3
    checks = run_qc(t, permitted_values={i: [1, 2, 3, 4, 5] for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:180]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
