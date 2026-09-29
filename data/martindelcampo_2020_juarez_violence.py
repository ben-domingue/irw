#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7335500
# DOI: 10.7717/peerj.9162
#   "Contextual violence and its link to social aggression: a study of
#   community violence in Juárez" (Martín Del Campo-Ríos & Cruz-Torres, 2020),
#   PeerJ 8:e9162.
# Data: Supplemental File peerj-08-9162-s001.sav (298 x 160), fetched from the
#       Europe PMC supplementaryFiles zip. Undergraduates at the Autonomous
#       University of Ciudad Juárez, Mexico. s002-s004 are AMOS model files,
#       s005.xlsx a model summary.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. Checked both .sav label levels. Variable labels carry
#   an English rendering of every item stem (e.g. PTSD3 "I constantly have
#   thoughts that remind me of the unpleasant situation ..."); value labels
#   give anchors for TIPI (all 7), CVCV (all 5), and only the endpoints for
#   AQ and AVS. The PTSD value labels ("1 Yes, 2 No") are stale -- the item
#   uses a 4-point agreement scale (paper). The instruments were administered
#   in Spanish (Mexican validations cited in the paper) and the Spanish
#   wording is not in the deposit, so shipping would be the
#   translated_substitute route; deferred to an item text pass.
#
# Tables (instruments and formats from the paper's "Instruments"):
#   martindelcampo_2020_cvcv   Contextual Victimization by Community Violence,
#                              CVCV1-34, 1-5 (never .. very frequently)
#   martindelcampo_2020_aq     Aggression Questionnaire (Buss & Perry; Mexican
#                              version), AQ1-29, 1-5
#   martindelcampo_2020_ptsd   Checklist for PTSD Traits (Pineda et al. 2002),
#                              PTSD1-24, 1-4 agreement
#   martindelcampo_2020_avs    Acceptance of Violence Scale, SAV1-14, 1-4. The
#                              file's value labels put 1 = strongly agree and
#                              4 = strongly disagree (the paper's text says the
#                              reverse); codes are kept as deposited.
#   martindelcampo_2020_tipi   Ten-Item Personality Inventory, TIPI1-10, 1-7
#                              (raw; the BF*r columns are reverse-coded copies)
# Skipped: CVCV35 (one global insecurity rating, outside the 34-item scale),
#   CVCV36 (free-text list of activities given up), SAV15 (attention check:
#   "mark strongly disagree"), BF*r reverse-coded copies, all factor/total
#   scores, the free-text major (Career), and the psychiatric-history and
#   drug-use yes/no columns (not needed as covariates).
# id: Folio (unique). Covariates: sex, age (0 -> missing), years living in
#   Juárez, semester. No PII. No two respondents share all 114 item answers.

import io
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7335500/"
           "supplementaryFiles")
FNAME = "peerj-08-9162-s001.sav"

SCALES = {
    "martindelcampo_2020_cvcv": ([f"CVCV{i}" for i in range(1, 35)], range(1, 6)),
    "martindelcampo_2020_aq": ([f"AQ{i}" for i in range(1, 30)], range(1, 6)),
    "martindelcampo_2020_ptsd": ([f"PTSD{i}" for i in range(1, 25)], range(1, 5)),
    "martindelcampo_2020_avs": ([f"SAV{i}" for i in range(1, 15)], range(1, 5)),
    "martindelcampo_2020_tipi": ([f"TIPI{i}" for i in range(1, 11)], range(1, 8)),
}
COVS = {"Sex": "cov_sex", "Age": "cov_age", "YearsJC": "cov_years_in_juarez",
        "Semester": "cov_semester"}


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
    assert d.shape == (298, 160), d.shape
    items_all = [c for its, _ in SCALES.values() for c in its]
    used = set(items_all) | set(COVS) | {"Folio"}
    assert used <= set(d.columns)
    print(f"  skip {d.shape[1] - len(used)} columns (see header)")
    assert d["Folio"].is_unique
    assert not d[items_all].duplicated().any()

    d = d.rename(columns={"Folio": "id", **COVS})
    d["id"] = d["id"].astype(int)
    d.loc[d["cov_age"] == 0, "cov_age"] = np.nan
    cov_cols = list(COVS.values())
    names = []
    for table, (items, rng) in SCALES.items():
        assert table not in names
        names.append(table)
        allowed = set(rng)
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        n_na = int(long["resp"].isna().sum())
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        bad = set(long["resp"]) - allowed
        assert not bad, (table, bad)
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
              f"items={long['item'].nunique()} (blank {n_na}) "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
