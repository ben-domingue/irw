#!/usr/bin/env python3
# Source: https://zenodo.org/records/23452364
# DOI: 10.5281/zenodo.23452364 (data; no paper DOI on the record)
#   Dostiyarova A, Akhmedov E (2026). Multidimensional Creativity Profiles in
#   Kazakhstan's Higher Education: Dataset and Analysis Code. Zenodo.
# Data: Multidimensional_Creativity_Kazakhstan_Zenodo_Dataset.xlsx, sheet
#   "Data" (288 x 54); sheets "README" and "Codebook" in the same workbook.
# License: CC BY 4.0 (Zenodo record).
# Codebook: the workbook's Codebook sheet (item wording, domain, 1-5 coding).
#
# Counts: 288 rows = the README/description's 288 complete responses.
# Instrument: Kaufman Domains of Creativity Scale (K-DOCS, Kaufman 2012), 50
#   items, 1 = much less creative .. 5 = much more creative: Self/Everyday
#   SE01-SE11, Scholarly SCH01-SCH11, Performance PERF01-PERF10,
#   Mechanical/Scientific MS01-MS09, Artistic ART01-ART09 (the published
#   11/11/10/9/9 structure). One table, one instrument; codes as deposited.
# id = the file's ID (1-288, unique).
# Covariates: age group, gender, occupation (text categories as deposited).
# Item text: not shipped -- the Codebook sheet carries every K-DOCS stem, but
#   the instrument has no rights-register row; left for an itemtext pass.

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = ("https://zenodo.org/api/records/23452364/files/"
            "Multidimensional_Creativity_Kazakhstan_Zenodo_Dataset.xlsx/content")
TABLE = "dostiyarova_2026_kdocs"
COVS = {"age_group": "cov_age_group", "gender": "cov_gender",
        "occupation": "cov_occupation"}
DOMAINS = {"SE": 11, "SCH": 11, "PERF": 10, "MS": 9, "ART": 9}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Data")
    assert d.shape == (288, 54), d.shape
    assert d["ID"].is_unique
    items = [c for c in d.columns if re.fullmatch(r"(SE|SCH|PERF|MS|ART)\d\d", c)]
    for k, n in DOMAINS.items():
        assert sum(re.fullmatch(rf"{k}\d\d", c) is not None for c in items) == n, k
    assert set(d.columns) == {"ID"} | set(COVS) | set(items)
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    allowed = set(range(1, 6))
    long = d[["id"] + items + covs].melt(
        id_vars=["id"] + covs, var_name="item", value_name="resp"
    ).dropna(subset=["resp"])
    assert not set(long["resp"]) - allowed
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: allowed for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {TABLE} {c.name}: {c.detail[:120]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
