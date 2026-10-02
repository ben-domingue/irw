#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC9083527
# DOI: 10.7717/peerj.13368
#   "Excessive alcohol consumption and binge drinking in college students"
#   (Herrero-Montes, Alonso-Blanco, Paz-Zulueta, Pellico-Lopez, Ruiz-Azcona,
#   Sarabia-Cobo, Boixadera-Planas & Parás-Bravo, 2022), PeerJ 10:e13368.
# Data: Supplemental File peerj-10-13368-s001.xlsx (142 x 21), fetched from the
#       Europe PMC supplementaryFiles zip. s002.docx is the codebook. Spanish
#       university students (Cantabria).
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. It is cheap -- the deposit's codebook s002.docx gives
#   every AUDIT item's English stem and every option label with its code --
#   but irw-validate's rights register lists AUDIT as "ship_with_note":
#   response data may ship, wording may not without a ruling. Held for that
#   ruling. (Administered in Spanish; the Spanish wording is not deposited.)
#
# Table: herreromontes_2022_audit -- the 10 AUDIT items as coded in the
#   codebook: items 1-8 are 0-4, items 9-10 are 0/2/4 ("No" / "Yes, but not in
#   the last year" / "Yes, during the last year"). Item sums equal
#   AUDIT TOTAL on 141 of 142 rows (printed); the domain scores and total are
#   skipped as composites.
# id: the source ID (e.g. "B322") is not unique -- B322 appears twice with
#   different ages and answers, so these are two people -- and ids are
#   alphanumeric, so the row index is used instead.
# Covariates: age, gender (codebook: 0 = female, 1 = male; one row carries an
#   undocumented 2, kept as coded), residence, maternal and paternal education,
#   BD (binge drinking yes/no, a derived classification kept as a covariate).
# 5 rows repeat another row on everything but ID; all are near-floor AUDIT
#   patterns in a 142-person sample of young women, read as chance. No PII.

import io
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9083527/"
           "supplementaryFiles")
FNAME = "peerj-10-13368-s001.xlsx"
TABLE = "herreromontes_2022_audit"
ITEMS = [f"AUDIT_{i}" for i in range(1, 11)]
COVS = {"Age": "cov_age", "Gender": "cov_gender",
        "Place of residence": "cov_residence",
        "Maternal level of studies": "cov_mother_education",
        "Paternal level of studies": "cov_father_education",
        "BD": "cov_binge_drinking"}
SKIP = {"ID": "not unique (B322 twice) and alphanumeric; row index used",
        "AUDIT_DOM1": "domain score", "AUDIT_DOM2": "domain score",
        "AUDIT_DOM3": "domain score", "AUDIT TOTAL": "total score"}
PV = {**{f"AUDIT_{i}": {0, 1, 2, 3, 4} for i in range(1, 9)},
      "AUDIT_9": {0, 2, 4}, "AUDIT_10": {0, 2, 4}}


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
        d = pd.read_excel(io.BytesIO(z.read(FNAME)))
    assert d.shape == (142, 21), d.shape
    acc = set(ITEMS) | set(COVS) | set(SKIP)
    assert set(d.columns) == acc and len(d.columns) == len(acc)
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    match = (d[ITEMS].sum(axis=1) == d["AUDIT TOTAL"]).sum()
    print(f"  item sum == AUDIT TOTAL on {match}/{len(d)} rows")
    assert match >= 140
    assert not d.duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    for i, allowed in PV.items():
        bad = set(long.loc[long["item"] == i, "resp"]) - allowed
        assert not bad, (i, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100

    checks = run_qc(long, permitted_values=PV)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": PV})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
