#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12857561
# DOI: 10.7717/peerj.20724
#   "The relationship between physical activity and smartphone addiction in
#   Chinese college students -- a latent profile analysis" (Tao, Chen, Jiang,
#   Chen, Lu & Yan, 2026), PeerJ 14:e20724.
# Data: Supplemental File peerj-14-20724-s001.sav (9,485 x 161), fetched from the
#       Europe PMC supplementaryFiles zip. s002.docx is the variable key.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. Checked both .sav label levels: no variable labels on
#   any item column, no value labels on M1-M17. s002.docx only says
#   "M1-M17_Smartphone addiction". The paper names the instrument (Leung's
#   2008 17-item scale, Chinese revision; 5-point Likert, higher = more
#   dependent) but prints no items; the wording is Leung (2008) / the Chinese
#   revision it cites.
#
# Table: tao_2026_mpai -- M1..M17, the 17-item smartphone addiction scale
#   of Leung (2008) -- the Mobile Phone Addiction Index (MPAI) -- Chinese
#   version, 1-5. The paper calls it the "Smartphone Addiction Scale (SAS)";
#   the table is named mpai to keep it apart from the Zung SAS. Its sum equals ZM for every row
#   (asserted), so these are the raw scored items.
# Not shipped: X1-X26 (1-7), S1-S20 (-2/0/2) and Z1-Z18 (mixed ranges) are not
#   named in s002.docx or described in the paper, so their instruments are
#   unknown. T1-T27 are IPAQ frequencies/minutes (quantities), and the rest
#   are totals, z-scores, MET sums and filters.
# Covariates: school category (ST), gender (XB), ethnicity (MZ), age, grade,
#   major. XH (serial number) becomes id after a uniqueness check; SJ (answer
#   time) is dropped. No PII.
# Duplicates: 535 rows repeat another row on the 17 items + covariates; 96% of
#   the rows involved are straight-line patterns (one value on all 17 items),
#   and no two rows agree on all 159 non-id columns, so this is low-variance
#   responding in a 9,485-person sample, not copied records.

import io
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12857561/"
           "supplementaryFiles")
FNAME = "peerj-14-20724-s001.sav"
TABLE = "tao_2026_mpai"
ITEMS = [f"M{i}" for i in range(1, 18)]
COVS = {"ST": "cov_school_type", "XB": "cov_gender", "MZ": "cov_ethnicity",
        "AGE": "cov_age", "grade": "cov_grade", "major": "cov_major"}


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


def load() -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(fetch_zip())) as z:
        blob = z.read(FNAME)
    with tempfile.NamedTemporaryFile(suffix=".sav") as tf:
        tf.write(blob)
        tf.flush()
        d, _ = pyreadstat.read_sav(tf.name)
    return d


def convert() -> None:
    d = load()
    assert d.shape == (9485, 161), d.shape
    cols = list(d.columns)
    used = {"XH"} | set(ITEMS) | set(COVS)
    skipped = [c for c in cols if c not in used]
    assert len(skipped) + len(used) == len(cols)
    print(f"  skip {len(skipped)} columns: undocumented X/S/Z blocks, IPAQ "
          f"quantities, totals, z-scores, filters, SJ (answer time)")
    assert (d[ITEMS].sum(axis=1) == d["ZM"]).all()
    assert d["XH"].is_unique
    n_dup = int(d[ITEMS + list(COVS)].duplicated().sum())
    print(f"  {n_dup} rows repeat another row on items+covariates "
          f"(17 items x 5 points, 9,485 people: expected by chance on floor "
          f"patterns)")

    d = d.rename(columns={"XH": "id", **COVS})
    d["id"] = d["id"].astype(int)
    cov_cols = list(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    assert long["resp"].notna().all() and (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for c in cov_cols:
        long[c] = long[c].astype(int)
    assert not set(long["resp"]) - {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100

    pv = {i: {1, 2, 3, 4, 5} for i in ITEMS}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
