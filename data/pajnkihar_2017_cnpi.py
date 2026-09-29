#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5299993
# DOI: 10.7717/peerj.2940
#   "The concept of Watson's carative factors in nursing and their
#   (dis)harmony with patient satisfaction" (Pajnkihar, Štiglic & Vrbnjak,
#   2017), PeerJ 5:e2940.
# Data: Supplemental File peerj-05-2940-s002.sav ("questionnaire part 2a",
#       613 x 72), fetched from the Europe PMC supplementaryFiles zip. Nurses
#       and nursing assistants in four Slovenian hospitals, August 2012. The
#       authors' own R script (s003.r) reads columns 4:73 of this file as the
#       70 items and groups them into Watson's ten carative factors.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: not shipped. It is in the deposit: both .sav label levels are
#   populated -- the variable labels are the Slovenian item stems as
#   administered (C01 "Individualno obravnavam paciente ..."), the value labels
#   the Slovenian anchors (1 Nikoli, 2 Redko, 3 Včasih, 4 Večinoma, 5 Vedno).
#   Shipping needs the English _translated fields, which the deposit does not
#   have (the English CNPI is Cossette et al. 2005); deferred.
#
# Table: pajnkihar_2017_cnpi -- Caring Nurse-Patient Interactions Scale, nurse
#   version, 70 items C01-C70, 1-5 (never .. always).
# Cleaning:
#   * 22 rows answered none of the 70 items and are dropped (591 remain).
#   * Two cells hold 55 (C07, C27), a double keystroke on a 1-5 scale; dropped.
#   * 50 rows repeat another row on all 70 items. 40 of them are straight-line
#     patterns (one value throughout, nearly all "always"), expected on a
#     ceiling-heavy caring scale. The other 10 form 5 exact-copy pairs, two of
#     them adjacent (rows 209/210, 215/216). Following the 2026-09-26 ruling
#     on Csibra 2025 ("drop duplicate rows"), the later row of each
#     non-straight-line pair is dropped (5 rows; asserted), leaving 586.
# id: row index (SN, "Zaporedna številka", has 147 values over 613 rows; it
#   is a per-ward sequence, not a person id). Covariate: hospital/ward
#   location (Lokacija_2). Not shipped: s001.sav ("part 1"), whose other
#   blocks (T01-T54, S3xx, S4xx, S5xx) the paper does not describe. No PII.

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
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5299993/"
           "supplementaryFiles")
FNAME = "peerj-05-2940-s002.sav"
TABLE = "pajnkihar_2017_cnpi"
ITEMS = [f"C{i:02d}" for i in range(1, 71)]


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
    assert d.shape == (613, 72), d.shape
    assert list(d.columns) == ["SN", "Lokacija_2"] + ITEMS
    print("  skip SN: per-ward sequence number, not unique")

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    empty = d[ITEMS].isna().all(axis=1)
    assert int(empty.sum()) == 22
    d = d[~empty].copy()
    n55 = int((d[ITEMS] == 55).sum().sum())
    assert n55 == 2
    d[ITEMS] = d[ITEMS].where(d[ITEMS] != 55, np.nan)

    straight = d[ITEMS].nunique(axis=1) <= 1
    later_copy = d[ITEMS].duplicated(keep="first") & ~straight
    assert int(later_copy.sum()) == 5, int(later_copy.sum())
    print(f"  drop later row of 5 exact-copy pairs: ids "
          f"{d.loc[later_copy, 'id'].tolist()}")
    d = d[~later_copy]
    assert len(d) == 586

    d = d.rename(columns={"Lokacija_2": "cov_location"})
    long = d.melt(id_vars=["id", "cov_location"], value_vars=ITEMS,
                  var_name="item", value_name="resp")
    n_na = int(long["resp"].isna().sum())
    long = long.dropna(subset=["resp"])
    assert (long["resp"] % 1 == 0).all()
    assert not set(long["resp"]) - {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "cov_location"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    print(f"  dropped {n_na} blank cells")

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
