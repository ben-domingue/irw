#!/usr/bin/env python3
# Lecdis: diagnostic test of disciplinary academic reading, Universidad de Las Américas
# (Chile), March 2022. Table: cabrerapommiez_2023_lecdis
#
# Source data: Cabrera-Pommiez, Monge-Rogel, Bargetto & Córdova-León (2023), "Análisis
#   estadístico de datos de la prueba Lecdis: Evaluación diagnóstica de la lectura
#   académica disciplinar en el nivel universitario", Mendeley Data, V1,
#   https://doi.org/10.17632/5h99xn33r5.1 (data_LECDIS.xlsx, claves_lecdis.csv).
#   Licence: CC BY 4.0. Changes from the source are listed below, as the licence asks.
# Built from: chile_lecdis_20261115.zip, national exams collection v1 by Santiago
#   Rivadeneira Quintero (irw#3498). That package was rebuilt cell by cell from the xlsx,
#   and its raw-file SHA-256 was matched to the live deposit on 2026-11-25
#   (oneoff/national-exams-3498/PILOT_PROVENANCE.md).
#
# Design: 1,233 health-science students, 40 four-option items on five anatomy texts
#   (8 per text), answered in a Google Form.
#   item         q01-q40, the question number in the form.
#   resp         1 if the chosen option equals the published key (the key the form scored
#                with; each person's sum equals the form's own score).
#   resp_raw     option chosen, a-d; "." = left blank (29 cells, items 35-36), scored 0
#                as the form does.
#   item_family  texto1-texto5: the reading passage (testlet).
#   cov_female   from the form's sex question.
# Changes from the source: option letters taken from the text of the chosen option;
#   responses scored with the key; the 30 rows of the 2021 pilot form and one repeated
#   submission dropped; degree program, campus, age and timestamp not included.
# Caveats: the key is weak on items 4, 8, 26 and 27 (a distractor out-correlates it);
#   5 pairs of persons with all 40 answers identical are kept (see PACKAGE.md).

import hashlib
import os
import zipfile

import pandas as pd

PKG = os.environ.get(
    "IRW_NATEXAMS_DIR",
    os.path.expanduser("~/Dropbox/projects/irw/oneoff/national-exams-3498/raw"))
ZIP = os.path.join(PKG, "chile_lecdis_20261115.zip")
RAW_SHA256 = "7ab75cf510821c521f6a4b22e0a5ee116533c891538c8c4bfdaea2471fda4e9a"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "chile_lecdis/"
TEST = "cl_lecdis_2022_g00_lectura_f1"


def read_pkg(z, name, **kw):
    with z.open(ROOT + name) as fh:
        return pd.read_csv(fh, compression="gzip" if name.endswith(".gz") else None, **kw)


def check_sums(z):
    for line in filter(None, z.read(ROOT + "SHA256SUMS").decode().split("\n")):
        h, f = line.split(maxsplit=1)
        f = f.lstrip("*")
        assert hashlib.sha256(z.read(ROOT + f)).hexdigest() == h, f"checksum fails: {f}"


def convert():
    with zipfile.ZipFile(ZIP) as z:
        check_sums(z)
        man = read_pkg(z, "manifiesto.csv", dtype=str)
        assert list(man.sha256_crudo) == [RAW_SHA256], "raw file differs from the deposit"
        d = read_pkg(z, f"data/{TEST}.csv.gz", dtype={"opcion": str})
        it = read_pkg(z, f"data/{TEST}_items.csv")
        p = read_pkg(z, f"data/{TEST}_personas.csv", dtype=str)
    assert not d.duplicated(["id", "item"]).any()
    d = d.merge(it[["item", "grupo"]], on="item", how="left", validate="many_to_one")
    d = d.merge(p[["id", "sexo"]].astype({"id": int}), on="id", how="left",
                validate="many_to_one")
    out = pd.DataFrame({
        "id": d.id,
        "item": "q" + d.item.astype(int).map("{:02d}".format),
        "resp": d.resp.astype(int),
        "resp_raw": d.opcion,
        "cov_female": d.sexo.map({"F": 1, "M": 0}).astype("Int64"),
        "item_family": d.grupo,
    }).sort_values(["id", "item"])
    os.makedirs(OUT_DIR, exist_ok=True)
    name = "cabrerapommiez_2023_lecdis"
    out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(name, len(out), "rows", out.id.nunique(), "persons", out.item.nunique(), "items")


if __name__ == "__main__":
    convert()
