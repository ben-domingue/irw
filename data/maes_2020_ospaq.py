#!/usr/bin/env python3
# Source: https://bmcpublichealth.biomedcentral.com/articles/10.1186/s12889-020-09180-9
# DOI: 10.1186/s12889-020-09180-9
# "The occupational sitting and physical activity questionnaire (OSPAQ): a
# validation study with accelerometer-assessed measures in Belgian office
# workers" (Maes, Ketels, Van Dyck & Clays, 2020), BMC Public Health.
# Data: 12889_2020_9180_MOESM2_ESM.xlsx, via Europe PMC supplementaryFiles
#       for PMC7339490.
# License: CC BY 4.0 (BMC; article-attached Additional file, so the article
#          licence is the source licence -- no separate deposit).
#
# Item text: NOT shipped. The column headers ("OSPAQ (% sitting)", ...) name
#   the four postures but are LABELS, not the administered stems -- the OSPAQ
#   asks a full question ("During the last 7 days, what percentage of your
#   time at work did you spend ...") that appears nowhere in the deposit.
#   Writing the posture name into item_text would be inventing a stem, which
#   the standard forbids. The real wording is in the published instrument
#   (Chau et al., the OSPAQ validation paper) -- one citation hop away, with
#   its own rights question, so it is a later pass and not the cheap case.
#
# The OSPAQ asks a worker to apportion their work time across four postures,
# so `resp` is a PERCENTAGE, not an ordinal category. datastandard.md admits
# continuous responses, and these are genuine per-item answers rather than a
# composite, so they ship as floats.
#
# Two source quirks handled here:
#   - 999 is a sentinel missing code (it appears in three of the four item
#     columns and nowhere makes sense as a percentage). Treated as missing,
#     not shipped as a response of 999.
#   - the four percentages are supposed to total 100, and for 28 respondents
#     they do not (one totals 2,997 before the sentinel is removed; others
#     total 90 or 110). Those are respondents' own arithmetic, which is a fact
#     about the data and not a defect to silently "fix" -- the responses ship
#     as given and nothing is rescaled. The sum-to-100 constraint is recorded
#     in the dictionary Notes instead.
#
# The accelerometer columns are DEVICE measurements of the same four postures,
# not self-reported responses -- the whole point of the paper is to compare
# them against the questionnaire. They ship as covariates, never as items.

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
import irw_validate  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7339490/supplementaryFiles"
XLSX = "12889_2020_9180_MOESM2_ESM.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
TABLE = "maes_2020_ospaq"
SENTINEL = 999

ITEMS = {
    "OSPAQ (% sitting)": "sitting",
    "OSPAQ (% standing)": "standing",
    "OSPAQ (% walking)": "walking",
    "OSPAQ (%heavy physical demading tasks)": "heavy_physical_tasks",
}
COVS = {
    "Job type (1= physical active job; 2= sedentary job)": "cov_job_type",
    "Accelerometers (% sitting)": "cov_accel_sitting",
    "Accelerometers (% standing)": "cov_accel_standing",
    "Accelerometers (% walking)": "cov_accel_walking",
    "Accelerometers (% MVPA)": "cov_accel_mvpa",
}


def load():
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(XLSX))
                with z.open(name) as fh:
                    return pd.ExcelFile(BytesIO(fh.read())).parse("Blad1")
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


def convert() -> None:
    d = load()
    for c in d.columns:
        if c not in ITEMS and c not in COVS:
            print(f"  [skip] {c}: not an OSPAQ item or a covariate")

    d = d.rename(columns={**ITEMS, **COVS})
    d["id"] = range(1, len(d) + 1)

    item_cols = list(ITEMS.values())
    n_sent = int((d[item_cols] == SENTINEL).sum().sum())
    d[item_cols] = d[item_cols].mask(d[item_cols] == SENTINEL)
    print(f"  [sentinel] {n_sent} cell(s) of {SENTINEL} treated as missing")

    cov_cols = sorted(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(float)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    assert long["resp"].between(0, 100).all(), "resp outside 0-100"
    assert not long.duplicated(["id", "item"]).any(), "duplicate id/item"
    assert long["item"].nunique() == 4, "expected 4 OSPAQ items"
    assert long["item"].nunique() > 1, "single-item table"
    assert long["id"].nunique() >= 100, "below the 100-id floor"
    # The upload profile is the gate an upload actually faces; compat.run_qc
    # is the older triage behaviour and the two can disagree.
    report = irw_validate.validate_frame(long, label=TABLE,
                                         profile="upload")
    assert report.conforms and not report.errors, \
        [(f.name, f.detail) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():g}-"
          f"{long['resp'].max():g}")


if __name__ == "__main__":
    convert()
