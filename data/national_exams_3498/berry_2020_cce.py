#!/usr/bin/env python3
# Haryana CCE evaluation, upper primary NCERT tests (grade 7 in 2011, grade 8 in 2013).
# Tables: berry_2020_cce_hindi, berry_2020_cce_math
#
# Source data: Berry, Kannan, Mukherji & Shotland, "Replication Data for: Failure of
#   Frequent Assessment: An Evaluation of India's Continuous and Comprehensive Evaluation
#   Program", Harvard Dataverse, https://doi.org/10.7910/DVN/KLJBHE, file
#   upperprimary_cleaned.dta (datafile 3557398). Licence: CC0 1.0.
#   NOT the 3ie copy (doi:10.7910/DVN/IS7YLY, CC BY-NC-SA), which gilbert_meta_31 uses.
# Paper: Berry et al. (2020), Journal of Development Economics 143, 102406,
#   https://doi.org/10.1016/j.jdeveco.2019.102406
# Built from: india_haryana_cce_20261115.zip, national exams collection v1 by Santiago
#   Rivadeneira Quintero (irw#3498). That package was rebuilt cell by cell from the .dta,
#   and its raw-file SHA-256 was matched to the live deposit on 2026-11-25
#   (oneoff/national-exams-3498/PILOT_PROVENANCE.md).
#
# Design (one table per subject, both rounds):
#   wave       1 = baseline 2011 (grade 7), 2 = endline 2013 (grade 8). Same id = same student.
#   item       f<version>_q<nn>. The three versions have different keys, so items never
#              link across versions; within a version they link across the two waves.
#   resp       1 if the chosen option equals the key. The key is recovered from the
#              authors' scores (unique; see PACKAGE.md), not published.
#   resp_raw   option marked, 1-4; -222 and -889 are undocumented source codes (probably
#              blank and invalid mark), scored 0 as the authors do.
#   treat      1 = CCE, 0 = control.
#   cluster_id super_school_id: the campus, the unit of randomisation (96 campuses,
#              100 schools; treat is constant within it).
#   block_id   randomisation stratum (26).
#   cov_female endline gender, used for both rounds.
# Kept: 15 groups of identical response vectors (likely copying), listed in the
#   package's extra/vectores_repetidos.csv. The primary school tests in the same deposit
#   are left out: they are already in the IRW as gilbert_meta_68/69.

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
ZIP = os.path.join(PKG, "india_haryana_cce_20261115.zip")
RAW_SHA256 = "f01c8540218fb44e948ff265b3051bab5a3aad9bab9ee2e0182a8f7322837b26"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "india_haryana_cce/"


def read_pkg(z, name, **kw):
    with z.open(ROOT + name) as fh:
        return pd.read_csv(fh, compression="gzip" if name.endswith(".gz") else None, **kw)


def check_sums(z):
    sums = z.read(ROOT + "SHA256SUMS").decode().split("\n")
    for line in filter(None, sums):
        h, f = line.split(maxsplit=1)
        f = f.lstrip("*")
        assert hashlib.sha256(z.read(ROOT + f)).hexdigest() == h, f"checksum fails: {f}"


def convert():
    with zipfile.ZipFile(ZIP) as z:
        check_sums(z)
        man = read_pkg(z, "manifiesto.csv", dtype=str)
        assert set(man.sha256_crudo) == {RAW_SHA256}, "raw file differs from the CC0 deposit"
        grp = read_pkg(z, "extra/grupos_tratamiento.csv")
        tables = {"hin": [], "mat": []}
        for test in man.test:
            _, _, year, grade, subj, form = test.split("_")
            d = read_pkg(z, f"data/{test}.csv.gz", dtype={"opcion": str})
            p = read_pkg(z, f"data/{test}_personas.csv", dtype=str)
            assert not d.duplicated(["id", "item"]).any()
            d["wave"] = {"2011": 1, "2013": 2}[year]
            d["item"] = form + "_" + d["item"]
            d = d.merge(p[["id", "sexo"]].astype({"id": int}), on="id", how="left",
                        validate="many_to_one")
            tables[subj].append(d)
    g = grp[["id", "treatment", "super_school_id", "stratum"]]
    assert g.id.is_unique
    for subj, name in {"hin": "berry_2020_cce_hindi", "mat": "berry_2020_cce_math"}.items():
        d = pd.concat(tables[subj], ignore_index=True)
        d = d.merge(g, on="id", how="left", validate="many_to_one")
        assert d.treatment.notna().all()
        assert not d.duplicated(["id", "item", "wave"]).any()
        out = pd.DataFrame({
            "id": d.id,
            "item": d.item,
            "resp": d.resp.astype(int),
            "resp_raw": d.opcion,
            "wave": d.wave,
            "treat": (d.treatment == 2).astype(int),  # 2 = CCE, 1 = control
            "cluster_id": d.super_school_id,
            "block_id": d.stratum,
            "cov_female": d.sexo.map({"F": 1, "M": 0}).astype("Int64"),
        }).sort_values(["id", "wave", "item"])
        os.makedirs(OUT_DIR, exist_ok=True)
        qc(out, name)
        out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(name, len(out), "rows", out.id.nunique(), "students", out.item.nunique(), "items")


if __name__ == "__main__":
    convert()
