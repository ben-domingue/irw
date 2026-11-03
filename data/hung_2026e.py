#!/usr/bin/env python3
# Source: https://zenodo.org/records/23164084
# DOI: 10.5281/zenodo.23164084 (dataset; the record names no published paper)
# Deposit: Hung (2026). Mirror Images: Growth and Fixed Mindsets in Academic
#   Procrastination [Data set]. Zenodo.
# Data: SPSS.sav (545 rows x 48 columns)
#   sha256 1525c950120cad00b34fb104918f3352dc168686bd36efc5fde198b89d18f96f
# Codebook: none as a separate file. The .sav carries an English variable label
#   (the full item stem) on every item and value labels naming the 7-point
#   anchors on every block except SDRS.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (worth_retrying: "confirm the
# id column"). Confirmed: `ID` is unique over all 545 rows (values 1-574, so
# some numbers were dropped before deposit) and is the person id.
#
# FIVE output tables, one per instrument, all 1-7:
#   hung_2026e_mindset              GM4 GM5 GM6 GM8 FM1 FM2 FM3 FM7  8 items
#       growth (GM) and fixed (FM) implicit-theory-of-intelligence statements;
#       the item numbers are the source's. FM items are NOT reverse-scored in
#       the file (they correlate about -0.3 with GM), shipped as recorded.
#   hung_2026e_fomo                 TFoMO1-5 (trait), SFoMO6-12 (state) 12 items
#   hung_2026e_problematic_video    PSVU1-6, short-video use frequency over the
#       past six weeks, 1 Never .. 7 Always                              6 items
#   hung_2026e_procrastination      AP1-5, academic procrastination      5 items
#   hung_2026e_social_desirability  SDRS1 SDRS2R SDRS3R SDRS4R SDRS5     5 items
#       The R items are stored ALREADY REVERSED: all five intercorrelate
#       positively (0.41-0.49) although 2-4 are negatively worded. The SDRS
#       block has no value labels in the .sav; its 1-7 range is inferred from
#       the data and from every other block in the file being 1-7.
# Agreement blocks: 1 Strongly Disagree, 2 Disagree, 3 Somewhat Disagree,
#   4 Neutral, 5 Somewhat Agree, 6 Agree, 7 Strongly Agree (value labels).
# Every cell is filled (no NA anywhere in the file).
#
# NOT the same sample as the earlier Hung deposits. Against hung_2026d
#   (zenodo 22240547, 681 x the same 12 FoMO codes on 1-7) the 12-item FoMO
#   response vectors share 0 of 527 distinct patterns; against
#   hung_2026_short_form_video (zenodo 19784064, 582 respondents) the 13
#   shared FoMO+PSVU columns share 4 of 538. Hence the new prefix hung_2026e;
#   ids are not comparable across deposits.
#
# Dropped: GMaverage FMaverage TFoMOaverage SFoMOaverage PSVUaverage
#   APaverage -- the depositor's scale means, not items.
# Covariates: cov_gender (0 male, 1 female), cov_age, cov_residence (hometown:
#   0 rural, 1 urban), cov_father_education (PEL) and cov_mother_education
#   (MEL), both 1 primary school or below .. 6 graduate degree. PEL/MEL are
#   read as paternal/maternal education level from their codes; the .sav gives
#   them value labels but no variable labels.
#
# Item text: NOT shipped. The English stems are in the .sav variable labels
#   for all 36 items (explicit, not positional), so extraction is solved. Held
#   on rights, as for hung_2026d: FoMO (TFoMO1 is Przybylski et al. item 1) and
#   SDRS-5 (Hays) are register BLOCK rows; GM/FM is Dweck's implicit theories of
#   intelligence scale, AP reads as the short Academic Procrastination Scale,
#   PSVU is a short-video adaptation of a Bergen-style addiction scale -- none
#   of those three was cleared in this pass.
#
# PII: none possible -- every column is numeric (asserted below), so there is
#   no text column to screen.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
# Self-contained like hung_2026d: fetches and caches the deposit file when
# HUNG_E_RAW is unset, so metadata/covariate_labels/harvest.py can re-run it
# in a fresh checkout.
_URL = "https://zenodo.org/api/records/23164084/files/SPSS.sav/content"
_SHA256 = "1525c950120cad00b34fb104918f3352dc168686bd36efc5fde198b89d18f96f"


def _raw():
    override = os.environ.get("HUNG_E_RAW")
    if override:
        return override
    cache = os.path.join(REPO_ROOT, "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, "hung_2026e_SPSS.sav")
    if not os.path.exists(dest):
        import hashlib
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r:
            blob = r.read()
        assert hashlib.sha256(blob).hexdigest() == _SHA256, "deposit file changed"
        with open(dest, "wb") as fh:
            fh.write(blob)
    return dest


LIKERT7 = [1, 2, 3, 4, 5, 6, 7]
TABLES = {
    "hung_2026e_mindset": ["GM4", "GM5", "GM6", "GM8",
                           "FM1", "FM2", "FM3", "FM7"],
    "hung_2026e_fomo": [f"TFoMO{i}" for i in range(1, 6)]
                       + [f"SFoMO{i}" for i in range(6, 13)],
    "hung_2026e_problematic_video": [f"PSVU{i}" for i in range(1, 7)],
    "hung_2026e_procrastination": [f"AP{i}" for i in range(1, 6)],
    "hung_2026e_social_desirability": ["SDRS1", "SDRS2R", "SDRS3R",
                                       "SDRS4R", "SDRS5"],
}
COVS = {"gender": "cov_gender", "age": "cov_age", "hometown": "cov_residence",
        "PEL": "cov_father_education", "MEL": "cov_mother_education"}
DROP = ["GMaverage", "FMaverage", "TFoMOaverage", "SFoMOaverage",
        "PSVUaverage", "APaverage"]


def convert():
    df, _ = pyreadstat.read_sav(_raw())
    assert df.shape == (545, 48), df.shape
    items = [c for cols in TABLES.values() for c in cols]
    accounted = set(items) | set(COVS) | set(DROP) | {"ID"}
    assert set(df.columns) == accounted, set(df.columns) ^ accounted
    assert all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns), \
        "a non-numeric column appeared -- screen it for PII before shipping"
    assert df["ID"].is_unique
    assert df.notna().all().all()

    df = df.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    for c in ["id"] + items + covs:
        df[c] = df[c].astype(int)

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, cols in TABLES.items():
        long = df.melt(id_vars=["id"] + covs, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert long["resp"].isin(LIKERT7).all()
        assert long["id"].nunique() >= 100

        checks = run_qc(long, permitted_values={i: LIKERT7 for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
