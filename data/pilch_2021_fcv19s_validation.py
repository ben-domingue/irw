#!/usr/bin/env python3
# Source: https://peerj.com/articles/11263/
# DOI: 10.7717/peerj.11263
# "Experiencing fear during the pandemic: validation of the fear of COVID-19
# scale in Polish" (Pilch, Kurasz & Turska-Kawa, 2021), PeerJ.
# Data: peerj-09-11263-s001.xlsx (Supporting Information), fetched via the
#       Europe PMC supplementaryFiles endpoint for PMC8083179.
# License: CC BY 4.0 (PeerJ; confirmed on the article page and in the Europe
#          PMC core record). The data file is article-attached Supporting
#          Information, so the article licence is the source licence here --
#          no separate deposit is involved.
#
# Item text: shipped for three of the four tables (the deposit's own
#   "Materials" sheet carries every item in the administered Polish plus an
#   English translation, and the response anchors for each block).
#   NOT shipped for the FCV-19S itself: the Fear of COVID-19 Scale (Ahorsu
#   et al., 2020) has no entry in itemtext/instrument_rights_register.csv, and
#   the wording is the instrument's rather than these authors'. The text is in
#   hand -- Materials sheet rows 23-37, Polish + English + the five anchors --
#   so this is one rights call away, not a re-derivation. Flagged in TODO.md.
#
# ---------------------------------------------------------------------------
# WHAT IS *NOT* SHIPPED HERE, AND WHY -- read before adding a fifth table.
#
# The deposit has two sheets of respondents. Sample 1 (n=383) is ALREADY IN
# THE IRW: it is the same sample as PLOS ONE 10.1371/journal.pone.0258606,
# which entered the corpus as pilch_2021_fear_covid19 / _coping_behavior /
# _protection_motivation / _personality_ipip20 via data/pilch_2021_coping_covid.py.
# Checked rather than assumed, by comparing the FCV-19S responses themselves:
#
#     distinct fear1-7 response patterns   PLOS 207 | Sample 1 206
#     patterns in Sample 1 also in PLOS    206 of 206
#     item means, PLOS  [2.592 2.421 1.532 1.956 2.408 1.494 1.548]
#     item means, Smp1  [2.595 2.423 1.525 1.953 2.413 1.486 1.540]
#
# Sample 1 is the PLOS file minus its 4 FCV-19S-incomplete rows. So Sample 1's
# fear1-7 is NOT shipped -- it would be a second copy of a live table, which
# is the duplication class that #1779/#1842 spent two months unwinding.
#
# Sample 2 (n=325) is a genuinely different sample: zero shared IPIP response
# patterns with the PLOS file (370 vs 311 distinct, intersection empty) and
# visibly different item means. Its blocks ship.
#
# Sample 1's Preventive1-4 block also ships: it is a DIFFERENT instrument from
# anything in the PLOS deposit (4 items on a 1-5 agreement scale, vs that
# file's BEH1-10 on 1-7), so it is new data about an already-present sample,
# not a duplicate. The ids therefore do NOT link to the live pilch_2021_*
# tables -- IRW ids are per-table row indices, and no cross-table person key
# is claimed.
# ---------------------------------------------------------------------------

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
from irw_validate.compat import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8083179/supplementaryFiles"
XLSX = "peerj-09-11263-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Covariates the Codebook sheet documents. Sex/Health_situation are 1/2 codes,
# Age is years, Vulnerability is the 0-100 susceptibility slider (a SINGLE
# item, so it is a covariate here and never a one-item table of its own).
BASE_COV = {
    "Sex": "cov_sex",
    "Age": "cov_age",
    "Employment": "cov_employment",
    "Health_situation": "cov_health_situation",
    "Vulnerability": "cov_vulnerability",
}
# Education and Marital status are documented by the Codebook sheet for
# Sample 1 only (Education 1-3, Marital 1-2). Sample 2 carries Education 2-6
# and Marital 1-3, which the codebook does not describe, so for Sample 2 they
# ship as uninterpreted raw codes and the dictionary Notes says so. They are
# not dropped -- the values are as deposited -- but nothing here claims to
# know what a 6 means.
S1_COV = {**BASE_COV, "Education": "cov_education", "Marital status": "cov_marital_status"}
S2_COV = {**BASE_COV, "Education": "cov_education", "Marital status": "cov_marital_status"}


def load() -> dict:
    # Europe PMC serves this endpoint a transient HTML 500 under load -- seen
    # on the very request after a successful one. Retry rather than treat it
    # as a dead source; an unretried stub here would look exactly like a
    # missing deposit. peerj.com's own SI URL is not a usable fallback: it
    # 403s to non-browser clients.
    blob = b""
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=180)
        if r.ok and r.content[:2] == b"PK":
            blob = r.content
            break
        time.sleep(5 * (attempt + 1))
    else:
        raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")
    with zipfile.ZipFile(BytesIO(blob)) as z:
        name = next(n for n in z.namelist() if n.endswith(XLSX))
        with z.open(name) as fh:
            xl = pd.ExcelFile(BytesIO(fh.read()))
    return {s: xl.parse(s) for s in xl.sheet_names}


def build(df, id_col, item_cols, cov_map, rename=None):
    """Wide -> long, dropping only rows where the response itself is missing."""
    keep = [id_col] + list(cov_map) + list(item_cols)
    d = df[keep].copy()
    d = d.rename(columns={id_col: "id", **cov_map})
    long = d.melt(id_vars=["id"] + list(cov_map.values()),
                  var_name="item", value_name="resp")
    if rename:
        long["item"] = long["item"].map(lambda c: rename.get(c, c))
    long = long.dropna(subset=["resp"])
    return long


def finish(long, table, lo, hi, n_items, continuous=False):
    cov_cols = sorted(c for c in long.columns if c.startswith("cov_"))
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    if not continuous:
        long["resp"] = long["resp"].astype(int)
    long["resp"] = long["resp"].astype(float)

    assert long["resp"].between(lo, hi).all(), f"{table}: resp outside {lo}-{hi}"
    assert not long.duplicated(["id", "item"]).any(), f"{table}: duplicate id/item"
    assert long["id"].nunique() >= 100, f"{table}: below the 100-id floor"
    assert long["item"].nunique() == n_items, f"{table}: expected {n_items} items"
    assert long["item"].nunique() > 1, f"{table}: single-item table"
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{table}.csv", index=False)
    print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():g}-{long['resp'].max():g}")


def convert() -> None:
    sheets = load()
    s1, s2 = sheets["Data_Sample_1"], sheets["Data_Sample_2"]

    fear = [f"fear{i}" for i in range(1, 8)]
    prev = [f"Preventive{i}" for i in range(1, 5)]
    ipip = [f"IPIP_IPIP{i}" for i in range(1, 21)]
    beh = [f"Beh{i}" for i in range(1, 4)]

    # Column bookkeeping: every source column is either shipped, carried as a
    # covariate, or skipped for a printed reason. Silence here is what let an
    # earlier build lose 1.0M responses without the totals moving.
    shipped = set(fear) | set(prev) | set(ipip) | set(beh) | set(S1_COV) | set(S2_COV)
    for sheet, df in (("Sample 1", s1), ("Sample 2", s2)):
        for c in df.columns:
            if c in shipped or c in ("ID1", "ID2"):
                continue
            print(f"  [skip] {sheet}.{c}: not an item or documented covariate")

    # 1. FCV-19S, Sample 2 ONLY. Sample 1 is already live -- see header.
    finish(build(s2, "ID2", fear, S2_COV),
           "pilch_2021_fcv19s_validation", 1, 5, 7)

    # 2. IPIP-BFM-20, Sample 2. 14 respondents skipped the block entirely;
    #    those are real non-responses, dropped rather than imputed.
    finish(build(s2, "ID2", ipip, S2_COV,
                 rename={f"IPIP_IPIP{i}": f"IPIP{i}" for i in range(1, 21)}),
           "pilch_2021_ipip20_validation", 1, 5, 20)

    # 3. Preventive behaviour, Sample 1, 1-5 agreement. A different instrument
    #    from the PLOS deposit's BEH1-10 -- see header.
    finish(build(s1, "ID1", prev, S1_COV),
           "pilch_2021_preventive_behavior", 1, 5, 4)

    # 4. Preventive behaviour, Sample 2, 0-100 visual-analogue slider. Kept as
    #    a float: datastandard.md admits continuous responses, and these are
    #    per-item answers, not a composite.
    finish(build(s2, "ID2", beh, S2_COV),
           "pilch_2021_preventive_vas", 0, 100, 3, continuous=True)


if __name__ == "__main__":
    convert()
