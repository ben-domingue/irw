#!/usr/bin/env python3
# EQAO Primary and Junior assessments (Ontario, Canada), grades 3 and 6, reading, writing and
#   mathematics, school years 2006-2007 to 2018-2019 (spring, on paper, census).
# Tables: canada_eqao_g<03|06>_<read|write|math>, six tables, each stacking 13 years and the
#   English-language, French-language and (grade 3 mathematics) French immersion versions.
#
# Original source of the data: EQAO, the Education Quality and Accountability Office of Ontario.
#   Student-level item results (files D) provided by EQAO on request (data request application,
#   delivered 2026-11-24). Licence: EQAO's written permission to redistribute through the IRW
#   (email from Data@EQAO.com, 2026-11-25), on condition that every table clearly acknowledges
#   EQAO as the original source; EQAO asks to be told if the scope of use changes from the
#   application (irw/licenseinfo/emails/eqao_2026-11-25.txt).
# Built from: eqao_pj_20261126.zip, national exams collection v2 by Santiago Rivadeneira
#   Quintero (irw#3498): long format, option marked and key, checked cell by cell against an
#   independent rebuild from EQAO's files.
#
# Layout (Ben's ruling for the collection: one table per study and subject, with `wave`):
#   wave      year (the second year of the school year: 2018-2019 is 2019).
#   cov_language  en (English-language schools), fr (French-language schools, own booklets and
#             keys), fr_immersion (grade 3 students of English-language schools writing
#             mathematics in French).
#   id        1 * 10^10 + year * 10^6 + the package id (1 marks this package: each EQAO
#             package draws its own permutation, so ids do not link across packages).
#             The package id is a random permutation within
#             a year, the same in all 13 tests of that year, so the same student links across
#             the reading, writing and mathematics tables of a grade within a year. It does not
#             link across years: EQAO's student ID is not in the package on purpose (linking
#             years goes beyond the application, PACKAGE.md).
#   item      <year>_<en|fr|fi>_<EQAO column>: columns are positions of a fixed template that do
#             not link across years, grades or languages.
#   resp      score: multiple choice 0/1; open response EQAO's 1-4 scale (writing conventions
#             1-3, writing topic development 1-6 in 2007, 2010, 2011); 0 only from a code below.
#   resp_raw  option marked (1-4) for multiple choice; codes with resp 0: -9 blank, -6 several
#             marks (multiple choice), -8 illegible/irrelevant/off topic (open response). No row
#             = missing, excluded, dropped or mark not available.
#   item_family  reading skill or mathematics strand from EQAO's definitions; for writing, the
#             task (its topic development T and conventions V scores), <year>_<lang>_<task>.
# Caveats (PACKAGE.md): 2015 English is small (labour disruption), 2016 lacks the Toronto
#   Catholic board, 2017 reading misses about 7,000 English students per grade.

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
ZIP = os.path.join(PKG, "eqao_pj_20261126.zip")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
PKG_DIGIT = 1
ROOT = "eqao_pj/"
LANG = {"eqaopjen": "en", "eqaopjfr": "fr", "eqaopjenfi": "fi"}
LANG_LABEL = {"en": "en", "fr": "fr", "fi": "fr_immersion"}


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
        assert set(man.prueba) == set(LANG) and (man.forma == "f1").all()
        man["lang"] = man.prueba.map(LANG)
        for (grade, subj), trows in man.groupby(["curso", "materia"], sort=True):
            name = f"canada_eqao_{grade}_{subj}"
            path = os.path.join(OUT_DIR, name + ".csv")
            if os.path.exists(path):
                os.remove(path)
            rows = persons = 0
            items = set()
            for year, yrows in trows.groupby("anno", sort=True):
                parts = []
                for _, r in yrows.sort_values("lang").iterrows():
                    d = read_pkg(z, f"data/{r.test}.csv.gz", dtype={"opcion": str, "item": str})
                    it = read_pkg(z, f"data/{r.test}_items.csv", dtype=str)
                    assert not d.duplicated(["id", "item"]).any()
                    assert d.id.nunique() == int(r.personas) and len(d) == int(r.celdas)
                    assert d.id.max() < 1_000_000
                    pre = f"{year}_{r.lang}_"
                    fam = it.grupo.copy()
                    task = it.parte_de.notna() & it.grupo.isna()
                    fam[task] = pre + it.parte_de[task]
                    it = it.assign(fam=fam)
                    d = d.merge(it[["item", "fam"]], on="item", how="left",
                                validate="many_to_one")
                    parts.append(pd.DataFrame({
                        "id": d.id.astype("int64") + int(year) * 1_000_000 + PKG_DIGIT * 10_000_000_000,
                        "item": pre + d["item"],
                        "resp": d.resp.astype(int),
                        "resp_raw": d.opcion,
                        "wave": int(year),
                        "cov_language": LANG_LABEL[r.lang],
                        "item_family": d.fam,
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
