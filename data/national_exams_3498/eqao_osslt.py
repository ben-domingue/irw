#!/usr/bin/env python3
# EQAO Ontario Secondary School Literacy Test (OSSLT; in French, TPCL), 2007 to 2019: the reading
#   and writing test every Ontario student must pass for the secondary school diploma, written in
#   grade 10 (first-time eligible) and again later by those who did not pass (previously eligible).
# Table: canada_eqao_g10_osslt, stacking 13 years, English and French, first-time and
#   previously eligible students (reading and writing are one test with one pass mark).
#
# Original source of the data: EQAO, the Education Quality and Accountability Office of Ontario.
#   Student-level item results provided by EQAO on request (data request application, delivered
#   2026-11-24). Licence: EQAO's written permission to redistribute through the IRW (email from
#   Data@EQAO.com, 2026-11-25), on condition that every table clearly acknowledges EQAO as the
#   original source; EQAO asks to be told if the scope of use changes from the application
#   (irw/licenseinfo/emails/eqao_2026-11-25.txt).
# Built from: eqao_osslt_20261126.zip, national exams collection v2 by Santiago Rivadeneira
#   Quintero (irw#3498): long format, option marked and key, checked cell by cell against an
#   independent rebuild from EQAO's files.
#
# Layout (Ben's ruling for the collection: one table per study and subject, with `wave`):
#   wave      year (the second year of the school year: 2018-2019 is 2019).
#   cov_language  en or fr (different tests).
#   cov_eligibility  first_time (grade 10) or previously_eligible (rewriting).
#   id        3 * 10^10 + year * 10^6 + the package id (3 marks this package: each EQAO package
#             draws its own permutation, so ids do not link across packages), + 500,000 for
#             previously eligible students. The package id is a random permutation within a
#             year; the 3 students in both groups in one year appear as two persons. It does
#             not link across years: EQAO's student ID is not in the package on purpose.
#   item      <year>_<en|fr>_<EQAO column>; 2013 had two administrations (April, May) with
#             different items: <year>_<lang>_<c1|c2>_<column>. First-time and previously eligible
#             students took the same test, so their codes are shared; columns are positions and
#             do not link across years or languages.
#   resp      score: multiple choice 0/1; reading open response and short writing 1-3
#             (conventions 1-2); long writing is scored in half points, so resp = 2 x EQAO's
#             score (topic 2-12, conventions 2-8). 0 only from a code below.
#   resp_raw  option marked (1-4) for multiple choice; codes with resp 0: -9 blank, -7 several
#             marks (multiple choice); for open response the blank, illegible, off-topic,
#             inadequate and insufficient codes. No row = dropped, excluded or missing.
#   item_family  EQAO strand and skill (R1-R3 reading, W1-W4 writing).
# Caveats (PACKAGE.md): 2017 is the March paper re-administration after the 2016 online trial
#   was disrupted (8.4% fewer English first-time students than EQAO's count).

import hashlib
import os
import sys
import zipfile

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402


def qc(df, name):
    """Refuse to write a table that fails any validator check; print the warnings."""
    checks = run_qc(df)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (name, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")


PKG = os.environ.get(
    "IRW_NATEXAMS_DIR",
    os.path.expanduser("~/Dropbox/projects/irw/oneoff/national-exams-3498/raw"))
ZIP = os.path.join(PKG, "eqao_osslt_20261126.zip")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
PKG_DIGIT = 3
ROOT = "eqao_osslt/"
ELIG = {"fte": "first_time", "pe": "previously_eligible"}
PE_OFFSET = 500_000


def read_pkg(z, name, **kw):
    with z.open(ROOT + name) as fh:
        return pd.read_csv(fh, compression="gzip" if name.endswith(".gz") else None, **kw)


def check_sums(z):
    for line in filter(None, z.read(ROOT + "SHA256SUMS").decode().split("\n")):
        h, f = line.split(maxsplit=1)
        f = f.lstrip("*")
        assert hashlib.sha256(z.read(ROOT + f)).hexdigest() == h, f"checksum fails: {f}"


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP) as z:
        check_sums(z)
        man = read_pkg(z, "manifiesto.csv", dtype=str)
        man["lang"] = man.prueba.str[9:11]
        man["elig"] = man.prueba.str[11:]
        assert set(man.lang) == {"en", "fr"} and set(man.elig) == set(ELIG)
        assert set(man.forma) == {"f1", "c1", "c2"}
        assert set(man[man.forma != "f1"].anno) == {"2013"}
        name = "canada_eqao_g10_osslt"
        path = os.path.join(OUT_DIR, name + ".csv")
        if os.path.exists(path):
            os.remove(path)
        rows = persons = 0
        items = set()
        for year, yrows in man.groupby("anno", sort=True):
            parts = []
            for _, r in yrows.sort_values(["lang", "elig", "forma"]).iterrows():
                d = read_pkg(z, f"data/{r.test}.csv.gz", dtype={"opcion": str, "item": str})
                it = read_pkg(z, f"data/{r.test}_items.csv", dtype=str)
                assert not d.duplicated(["id", "item"]).any()
                assert d.id.nunique() == int(r.personas) and len(d) == int(r.celdas)
                assert d.id.max() < PE_OFFSET
                d = d.merge(it[["item", "grupo"]], on="item", how="left", validate="many_to_one")
                pre = f"{year}_{r.lang}_" + ("" if r.forma == "f1" else f"{r.forma}_")
                parts.append(pd.DataFrame({
                    "id": (d.id.astype("int64") + int(year) * 1_000_000
                           + PKG_DIGIT * 10_000_000_000 + (PE_OFFSET if r.elig == "pe" else 0)),
                    "item": pre + d["item"],
                    "resp": d.resp.astype(int),
                    "resp_raw": d.opcion,
                    "wave": int(year),
                    "cov_language": r.lang,
                    "cov_eligibility": ELIG[r.elig],
                    "item_family": d.grupo,
                }))
                del d
            out = pd.concat(parts, ignore_index=True)
            del parts
            assert not out.duplicated(["id", "item"]).any()
            out = out.sort_values(["id", "item"])
            qc(out, f"{name} {year}")
            out.to_csv(path, mode="a", header=rows == 0, index=False)
            rows += len(out)
            persons += out.id.nunique()
            items |= set(out.item)
            print(f"  {name} {year}: {len(out)} rows", flush=True)
        print(name, rows, "rows", persons, "persons", len(items), "items", flush=True)


if __name__ == "__main__":
    convert()
