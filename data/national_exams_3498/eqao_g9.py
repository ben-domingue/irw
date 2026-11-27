#!/usr/bin/env python3
# EQAO Grade 9 Assessment of Mathematics (Ontario, Canada), school years 2006-2007 to 2018-2019.
# Tables: canada_eqao_g09_math_academic and canada_eqao_g09_math_applied (the two grade 9
#   mathematics programs, two different tests), each stacking 13 years, English and French,
#   and the winter and spring sittings.
#
# Original source of the data: EQAO, the Education Quality and Accountability Office of Ontario.
#   Student-level item results (files D) provided by EQAO on request (data request application,
#   delivered 2026-11-24). Licence: EQAO's written permission to redistribute through the IRW
#   (email from Data@EQAO.com, 2026-11-25), on condition that every table clearly acknowledges
#   EQAO as the original source; EQAO asks to be told if the scope of use changes from the
#   application (irw/licenseinfo/emails/eqao_2026-11-25.txt).
# Built from: eqao_g9_20261126.zip, national exams collection v2 by Santiago Rivadeneira
#   Quintero (irw#3498): long format, option marked and key, checked cell by cell against an
#   independent rebuild from EQAO's files.
#
# Layout (Ben's ruling for the collection: one table per study and subject, with `wave`):
#   wave      year of the sitting (the second year of the school year: 2018-2019 is 2019).
#   session   winter (January, first-semester course) or spring (June); package c1 / c2.
#   cov_language  en or fr (different test versions; item codes do not link across them).
#   id        2 * 10^10 + year * 10^6 + the package id (2 marks this package: each EQAO
#             package draws its own permutation, so ids do not link across packages).
#             The package id is a random permutation within
#             a year, the same across that year's eight tests, so a student who sat both
#             programs (or both sittings) in a year has the same id in both tables. It does not
#             link across years: EQAO's student ID is not in the package on purpose (linking
#             years or programs goes beyond the application, PACKAGE.md).
#   item      <year>_<lang>_<w|s>_<column>: EQAO item columns are positions and do not link
#             across years, languages or programs. The questions EQAO's definitions mark as the
#             same in winter and spring (misma_en_c1_c2, 2010-2019) share one code,
#             <year>_<lang>_ws_<winter column>. Shared questions in 2007-2009 are not marked
#             in the source and stay separate.
#   resp      score: multiple choice 0/1, open response 1-4 (0 only from a code below).
#   resp_raw  option marked (1-4) for multiple choice; codes with resp 0: -9 blank,
#             -6 several marks, -7 illegible/irrelevant (2007-2015), -8 unrelated/unengaged
#             (2016-2019). No row = missing, excluded or dropped.
#   item_family  strand and expectation from EQAO's definitions (e.g. N:NAV.01).
#   A student who sat the same program in winter and spring has two rows for a shared
#   question, one per session.

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
ZIP = os.path.join(PKG, "eqao_g9_20261126.zip")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
PKG_DIGIT = 2
ROOT = "eqao_g9/"
PROGRAMS = {"acad": "academic", "app": "applied"}
SESSION = {"c1": "winter", "c2": "spring"}


def read_pkg(z, name, **kw):
    with z.open(ROOT + name) as fh:
        return pd.read_csv(fh, compression="gzip" if name.endswith(".gz") else None, **kw)


def check_sums(z):
    for line in filter(None, z.read(ROOT + "SHA256SUMS").decode().split("\n")):
        h, f = line.split(maxsplit=1)
        f = f.lstrip("*")
        assert hashlib.sha256(z.read(ROOT + f)).hexdigest() == h, f"checksum fails: {f}"


def shared_codes(defs):
    """(winter test, column) and (spring test, column) -> the shared item suffix."""
    m = defs[defs.misma_en_c1_c2.notna()]
    out = {}
    for _, r in m.iterrows():
        other_test, other_col = r.misma_en_c1_c2.split(":")
        winter_col = r.columna_origen if r.test.endswith("_c1") else other_col
        assert r.test[:-3] == other_test[:-3] and r.test != other_test
        out[(r.test, r.columna_origen)] = "ws_" + winter_col
    return out


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP) as z:
        check_sums(z)
        man = read_pkg(z, "manifiesto.csv", dtype=str)
        defs = read_pkg(z, "items_definiciones.csv", dtype=str)
        shared = shared_codes(defs)
        man["lang"] = man.prueba.str[6:8]
        man["prog"] = man.prueba.str[8:]
        assert set(man.lang) == {"en", "fr"} and set(man.prog) == set(PROGRAMS)
        assert set(man.forma) == set(SESSION)
        for prog, label in PROGRAMS.items():
            name = f"canada_eqao_g09_math_{label}"
            path = os.path.join(OUT_DIR, name + ".csv")
            if os.path.exists(path):
                os.remove(path)
            rows = persons = 0
            items = set()
            for year, yrows in man[man.prog == prog].groupby("anno", sort=True):
                parts = []
                for _, r in yrows.sort_values(["lang", "forma"]).iterrows():
                    d = read_pkg(z, f"data/{r.test}.csv.gz", dtype={"opcion": str, "item": str})
                    it = read_pkg(z, f"data/{r.test}_items.csv", dtype=str)
                    assert not d.duplicated(["id", "item"]).any()
                    assert d.id.nunique() == int(r.personas) and len(d) == int(r.celdas)
                    assert (it.item == it.columna_origen).all()
                    assert d.id.max() < 1_000_000
                    d = d.merge(it[["item", "grupo"]], on="item", how="left",
                                validate="many_to_one")
                    adm = "w" if r.forma == "c1" else "s"
                    code = {i: shared.get((r.test, i), f"{adm}_{i}") for i in it.item}
                    parts.append(pd.DataFrame({
                        "id": d.id.astype("int64") + int(year) * 1_000_000 + PKG_DIGIT * 10_000_000_000,
                        "item": f"{year}_{r.lang}_" + d["item"].map(code),
                        "resp": d.resp.astype(int),
                        "resp_raw": d.opcion,
                        "wave": int(year),
                        "session": SESSION[r.forma],
                        "cov_language": r.lang,
                        "item_family": d.grupo,
                    }))
                out = pd.concat(parts, ignore_index=True)
                assert not out.duplicated(["id", "item", "session"]).any()
                out = out.sort_values(["id", "item", "session"])
                qc(out, f"{name} {year}")
                out.to_csv(path, mode="a", header=rows == 0, index=False)
                rows += len(out)
                persons += out.id.nunique()
                items |= set(out.item)
                print(f"  {name} {year}: {len(out)} rows", flush=True)
            print(name, rows, "rows", persons, "persons", len(items), "items", flush=True)


if __name__ == "__main__":
    convert()
