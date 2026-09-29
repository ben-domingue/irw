#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5546178
# DOI: 10.7717/peerj.3576
#   "Psychopathological symptoms, defense mechanisms and time perspectives
#   among subjects with alcohol dependence (AD) presenting different patterns
#   of coping with stress" (Iwanicka, Gerhant & Olajossy, 2017), PeerJ 5:e3576.
# Data: Supplemental File peerj-05-3576-s001.xlsx, sheet Arkusz1 (120 x 524),
#       fetched from the Europe PMC supplementaryFiles zip. Polish adults in
#       inpatient alcohol-dependence therapy.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. The workbook has bare codes only (dsq1.., cis1..);
#   the Polish adaptations named in the paper (CISS: Strelau et al.; DSQ-40:
#   Bogutyn et al. 1999; SCL-90: Brodziak 1981; SZPTI-PL: Cybis et al. 2012)
#   hold the wording. None of it is in the deposit.
#
# Tables (scales and anchors from the paper's Methods):
#   iwanicka_2017_dsq40   Defense Style Questionnaire, 40 items, 1-9
#   iwanicka_2017_ciss    Coping Inventory for Stressful Situations, 48, 1-5
#   iwanicka_2017_scl90   Symptom Checklist-90, 90 items, 0-4 ("slc52" is a
#                         typo for scl52 in the header and is renamed)
#   iwanicka_2017_szpti   Short Zimbardo Time Perspective Inventory, 15, 1-5
# Out-of-range cells are dropped, per item: DSQ 0 and 11 (a few rows carry 0 on
#   every DSQ/CISS item, i.e. not administered), CISS 0 and 6, SCL-90 values
#   8-44 on six items (single-cell entry errors), SZPTI 0/55 on item 7. Each is
#   counted and printed.
# Not shipped: ACL1-ACL300, a 300-adjective checklist coded 1/2 that the paper
#   never mentions, so the meaning of the codes is undocumented. The 31
#   leading columns are demographics/treatment history; the stable ones are
#   carried as covariates (age 0 -> missing), the rest dropped.
# No PII: no names, dates or contact data. No exact-duplicate rows.

import io
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5546178/"
           "supplementaryFiles")
FNAME = "peerj-05-3576-s001.xlsx"

SCALES = {
    "iwanicka_2017_dsq40": ([f"dsq{i}" for i in range(1, 41)], range(1, 10)),
    "iwanicka_2017_ciss": ([f"cis{i}" for i in range(1, 49)], range(1, 6)),
    "iwanicka_2017_scl90": ([f"scl{i}" for i in range(1, 91)], range(0, 5)),
    "iwanicka_2017_szpti": ([f"szpti{i}" for i in range(1, 16)], range(1, 6)),
}
COVS = {"sex": "cov_sex", "age": "cov_age",
        "place_of_residence": "cov_residence", "education": "cov_education",
        "marital_status": "cov_marital_status",
        "source_ of_ income": "cov_income_source",
        "age_of_ alcohol_ use_ initation": "cov_age_first_alcohol"}


def fetch_zip() -> bytes:
    for attempt in range(6):
        try:
            r = requests.get(ZIP_URL, headers=UA, timeout=300)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(20 * (attempt + 1))


def convert() -> None:
    with zipfile.ZipFile(io.BytesIO(fetch_zip())) as z:
        d = pd.read_excel(io.BytesIO(z.read(FNAME)), sheet_name="Arkusz1")
    assert d.shape == (120, 524), d.shape
    d = d.rename(columns={"slc52": "scl52"})
    cols = list(d.columns)
    acl = [f"ACL{i}" for i in range(1, 301)]
    lead = cols[:31]
    items_all = [c for its, _ in SCALES.values() for c in its]
    acc = set(lead) | set(acl) | set(items_all)
    assert set(cols) == acc and len(cols) == len(acc), set(cols) ^ acc
    assert set(COVS) <= set(lead)
    print(f"  skip ACL1-ACL300: undocumented adjective checklist")
    print(f"  skip {len(lead) - len(COVS)} treatment-history/other lead columns")
    assert not d.duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d.loc[d["cov_age"] == 0, "cov_age"] = np.nan
    cov_cols = list(COVS.values())
    names = []
    for table, (items, rng) in SCALES.items():
        assert table not in names
        names.append(table)
        allowed = set(rng)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        n_na = int(long["resp"].isna().sum())
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        oob = ~long["resp"].isin(allowed)
        print(f"  {table}: dropped {n_na} blank and {int(oob.sum())} "
              f"out-of-range cells {sorted(long.loc[oob, 'resp'].unique())}")
        long = long[~oob].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        pv = {i: allowed for i in items}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            (table, [(f.check, f.message) for f in rep.errors])
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
