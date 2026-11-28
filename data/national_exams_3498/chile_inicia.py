#!/usr/bin/env python3
# Evaluación Inicia (Chile), 2010-2012: exit examination of teacher-education graduates.
# Tables: chile_<year>_inicia_<test>, one per year and test: 15 tables. Biología, Física and
#   Química 2012 (80, 65 and 49 persons) are under the 100-person floor and not written.
#
# Source data: Ministerio de Educación de Chile, Centro de Perfeccionamiento,
#   Experimentación e Investigaciones Pedagógicas (CPEIP), Evaluación Inicia 2010, 2011 y
#   2012, bases de registros de respuesta individuales. Datos Abiertos Mineduc,
#   https://datosabiertos.mineduc.cl/evaluacion-inicia/ (<year>-Inicia.zip).
#   Licence: public-use data. Mineduc confirmed by email (2026-11-16) that portal files may
#   be redistributed without asking, citing the Ministry as the source
#   (irw/licenseinfo/emails/mineduc_chile_inicia_2026-11-16.txt).
# Built from: chile_inicia_20261126.zip, national exams collection v2 by Santiago
#   Rivadeneira Quintero (irw#3498): long format, option marked and key, checked cell by
#   cell against an independent rebuild from the three portal zips.
#
# Layout (Ben's ruling for the collection: one table per study and subject, not per form):
#   The two forms (A = f1, B = f2) of a test are one table.
#   id        form 1 persons keep the package id + 10000, form 2 + 20000: the package numbers
#             persons within each form, and the forms are different people. A person who
#             took two tests in a year is not linked across tables (the source does not
#             link them).
#   item      2012: the package item code, which is the same in both forms for a common
#             question. 2010 and 2011: item codes do not link across forms, so they carry
#             the form: f1_<item>, f2_<item>.
#   resp      score (0/1; constructed response 0-2 in 2011, 0-4 in 2010).
#   resp_raw  option marked, as the source codes it. 2011: 9 is in practice the omission;
#             2012: 8 = omitted, 9 = double mark; 2010: empty = omitted or invalid. All 0.
#   cov_form  1 or 2.  cov_female  from the source's sex field (none in 2012).
#   item_family  the source block or shared stimulus, where the package gives one.
# Not included: tests the package did not prepare (PCP 2010, PCD Naturaleza and Sociedad
#   2010, PCE, TIC; 2009, 2014, 2015 have no item responses).

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
ZIP = os.path.join(PKG, "chile_inicia_20261126.zip")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "chile_inicia/"


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
        man["group"] = man.test.str.replace(r"_f\d+$", "", regex=True)
        for group, rows in man.groupby("group", sort=True):
            year = int(rows.anno.iloc[0])
            parts = []
            keys = {}
            for _, r in rows.iterrows():
                form = int(r.forma[1:])
                d = read_pkg(z, f"data/{r.test}.csv.gz", dtype={"opcion": str, "item": str})
                it = read_pkg(z, f"data/{r.test}_items.csv", dtype=str)
                p = read_pkg(z, f"data/{r.test}_personas.csv", dtype=str)
                assert not d.duplicated(["id", "item"]).any()
                assert len(p) == int(r.personas) and d.id.nunique() == int(r.personas)
                for _, i in it.iterrows():
                    k = (i["clave"] if isinstance(i["clave"], str) else "", i["max_puntos"])
                    if year == 2012:
                        assert keys.setdefault(i["item"], k) == k, (group, i["item"], "key differs across forms")
                d = d.merge(it[["item", "grupo"]], on="item", how="left", validate="many_to_one")
                d = d.merge(p[["id", "sexo"]].astype({"id": int}), on="id", how="left",
                            validate="many_to_one")
                item = d["item"] if year == 2012 else f"f{form}_" + d["item"]
                fam = d["grupo"] if year == 2012 else d["grupo"].where(d["grupo"].isna(), f"f{form}_" + d["grupo"].astype(str))
                parts.append(pd.DataFrame({
                    "id": d.id.astype(int) + 10000 * form,
                    "item": item,
                    "resp": d.resp.astype(int),
                    "resp_raw": d.opcion,
                    "cov_form": form,
                    "cov_female": d.sexo.map({"F": 1, "M": 0}).astype("Int64"),
                    "item_family": fam,
                }))
            out = pd.concat(parts, ignore_index=True)
            assert out.id.max() < 30000 and not out.duplicated(["id", "item"]).any()
            for c in ("cov_female", "item_family"):
                if out[c].isna().all():
                    out = out.drop(columns=c)
            out = out.sort_values(["id", "item"])
            name = "chile_{}_inicia_{}".format(year, group.split("_g00_")[1])
            if out.id.nunique() < 100:  # datastandard.md sample floor
                print(name, "SKIPPED:", out.id.nunique(), "persons, under the floor of 100")
                continue
            qc(out, name)
            out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
            print(name, len(out), "rows", out.id.nunique(), "persons", out.item.nunique(), "items")


if __name__ == "__main__":
    convert()
