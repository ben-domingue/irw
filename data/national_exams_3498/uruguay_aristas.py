#!/usr/bin/env python3
# Aristas, Uruguay's national sample-based assessment (INEEd), 2017-2023: six editions.
# Tables: uruguay_<year>_aristas_g<grade>_<lec|mat> and
#   uruguay_2018_aristasrural_g09_<lec|mat> (rural lower-secondary census), 18 tables.
#
# Source data: Instituto Nacional de Evaluación Educativa (INEEd), Aristas databases,
#   https://www.ineed.edu.uy/bases-de-datos-de-aristas/ (primary 2017, 2020, 2023, grades 3
#   and 6; lower secondary 2018 and 2022, grade 9; rural lower secondary 2018). Technical
#   reports: https://www.ineed.edu.uy/publicaciones/informes-y-reportes-de-aristas/
#   Licence: INEEd permission to redistribute, by email 2026-11-13 ("Las bases de datos son
#   públicas, por lo cual no tenemos inconveniente en que las redistribuyan"); cite INEEd as
#   the primary source (irw/licenseinfo/emails/ineed_uruguay_aristas_2026-11-13.txt).
# Built from: uruguay_20261126.zip, national exams collection v2 by Santiago Rivadeneira
#   Quintero (irw#3498): long format, checked cell by cell against an independent rebuild.
#
# Layout: the package already has one test per edition and subject, so one table each.
#   id        INEEd's anonymous student id; the same student in reading and mathematics of
#             an edition (not across editions).
#   item      INEEd item code. Codes are shared across some editions, but the source does not
#             flag anchors, so links across tables are not asserted.
#   resp      scored response: 0/1, a few constructed-response items 0-2. No option or key.
#             A 0 may include omission (the 2022 dictionaries say omitted = 0); no row = not
#             administered or not reached.
#   cov_booklet  booklet (response pattern) reconstructed by the package.
#   cov_female   from the source's sex field.
#   item_family  block, reconstructed from the data (booklets of two blocks in a closed chain).
# Changes in the package (PACKAGE.md): lower secondary 2018 leaves out the 215 rows of the
#   free private schools census, which INEEd says must not be used for national analyses;
#   partial credit in 2017, 2018 and 2020 follows INEEd's calibration decision per item.

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
ZIP = os.path.join(PKG, "uruguay_20261126.zip")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "uruguay/"


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
        assert (man.forma == "f1").all()
        for _, r in man.iterrows():
            d = read_pkg(z, f"data/{r.test}.csv.gz", dtype={"opcion": str, "item": str})
            it = read_pkg(z, f"data/{r.test}_items.csv", dtype=str)
            p = read_pkg(z, f"data/{r.test}_personas.csv", dtype=str)
            assert not d.duplicated(["id", "item"]).any()
            assert d.id.nunique() == int(r.personas) and len(d) == int(r.celdas)
            assert d.opcion.isna().all()
            d = d.merge(it[["item", "grupo"]], on="item", how="left", validate="many_to_one")
            d = d.merge(p[["id", "sexo", "forma"]].astype({"id": int}), on="id", how="left",
                        validate="many_to_one")
            out = pd.DataFrame({
                "id": d.id.astype(int),
                "item": d["item"],
                "resp": d.resp.astype(int),
                "cov_booklet": d.forma,
                "cov_female": d.sexo.map({"F": 1, "M": 0}).astype("Int64"),
                "item_family": d.grupo,
            })
            for c in ("cov_female", "item_family"):
                if out[c].isna().all():
                    out = out.drop(columns=c)
            out = out.sort_values(["id", "item"])
            _, study, year, grade, subj, _ = r.test.split("_")
            name = f"uruguay_{year}_{study}_{grade}_{subj}"
            qc(out, name)
            out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
            print(name, len(out), "rows", out.id.nunique(), "persons", out.item.nunique(), "items")


if __name__ == "__main__":
    convert()
