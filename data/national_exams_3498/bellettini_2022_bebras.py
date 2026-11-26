#!/usr/bin/env python3
# Italian Bebras challenge, November 2021 (computational thinking tasks), one table per
# age category. Tables: bellettini_2022_bebras_<kilo|mega|giga|tera|peta>
#
# Source data: Bellettini, Lonati, Monga & Morpurgo (2022), "Replication Data for: How is
#   two better than one? An observational study on the impact of working in pairs when
#   solving Bebras tasks", UNIMI Dataverse V1, https://doi.org/10.13130/RD_UNIMI/WT9NHU
#   (bebras2021.csv, datafile 12139). Licence: CC BY 4.0. Producer: ALaDDIn, Università
#   degli Studi di Milano, which runs the Italian Bebras challenge.
# Paper: ISSEP 2022, LNCS 13488, https://doi.org/10.1007/978-3-031-15851-3_5
# Built from: italia_bebras_20261113.zip, national exams collection v1 by Santiago
#   Rivadeneira Quintero (irw#3498), rebuilt cell by cell from bebras2021.csv.
# Changes from the source (as CC BY asks): converted to long IRW format, one table per
#   age category; teams renumbered 1..N in order of first appearance; a penalized wrong
#   answer (source score -1) is scored 0 in resp and kept as -1 in resp_raw; team size
#   0 or inconsistent with the team mode set to missing.
#
# Design:
#   id           a TEAM, not a person: in 2021 students entered alone (single) or in
#                pairs (double). Unique across the five tables.
#   item         the Italian task id (Q01-Q28). A task that appears in two neighbouring
#                categories can carry a different maximum there; tables are separate.
#                Bebras international ids are in the source README (e.g. Q01 = 2021-HR-03).
#   resp         points, 0 to the task maximum (2, 4 or 6); 12 tasks give half credit.
#   resp_raw     the source score: equal to resp except -1 = a penalized wrong answer in
#                the 9 multiple-choice tasks with a penalty. In those tasks resp 0 with
#                resp_raw 0 means not solved; elsewhere 0 means wrong or not solved.
#   cluster_id   the teacher who entered the team (pseudo-anonymous; 751 teachers, some
#                with teams in several categories).
#   cov_double   1 = team of two, 0 = single (the registered mode).
#   cov_n_members  1 or 2 as the source gives it; missing where the source says 0 or
#                contradicts the mode.
# Caveats: voluntary entry, not a sample; 143 more teams than the organizers' official
#   count (mostly total score 0), not identifiable, kept. No sex variable. Task texts are
#   Bebras copyright and are not included.

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
ZIP = os.path.join(PKG, "italia_bebras_20261113.zip")
RAW_SHA256 = "a35ac8486db50ff2bb638aef0b27cf254e60156b5aea5441c7b5c055bfd629d9"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "italia_bebras/"
CATEGORIES = ["kilo", "mega", "giga", "tera", "peta"]


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
        assert set(man.sha256_crudo) == {RAW_SHA256}, "raw file differs from the one checked"
        teams = read_pkg(z, "extra/equipos.csv")
        assert teams.id.is_unique
        data = {c: read_pkg(z, f"data/it_bebras_2021_g00_{c}_f1.csv.gz", dtype={"opcion": str})
                for c in CATEGORIES}
    teams["cov_double"] = (teams.modalidad == "double").astype(int)
    ok = ((teams.modalidad == "single") & (teams.n_componentes == 1)) | \
         ((teams.modalidad == "double") & (teams.n_componentes.isin([1, 2])))
    teams["cov_n_members"] = teams.n_componentes.where(ok).astype("Int64")
    os.makedirs(OUT_DIR, exist_ok=True)
    for c, d in data.items():
        assert not d.duplicated(["id", "item"]).any()
        assert set(d.opcion.dropna()) <= {"-1"} and (d.loc[d.opcion == "-1", "resp"] == 0).all()
        d = d.merge(teams[["id", "docente", "cov_double", "cov_n_members"]], on="id",
                    how="left", validate="many_to_one")
        assert d.docente.notna().all()
        out = pd.DataFrame({
            "id": d.id,
            "item": d.item,
            "resp": d.resp.astype(int),
            "resp_raw": d.resp.where(d.opcion != "-1", -1).astype(int),
            "cluster_id": d.docente,
            "cov_double": d.cov_double,
            "cov_n_members": d.cov_n_members,
        }).sort_values(["id", "item"])
        name = f"bellettini_2022_bebras_{c}"
        qc(out, name)
        out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(name, len(out), "rows", out.id.nunique(), "teams", out.item.nunique(), "items;",
              int((out.resp_raw == -1).sum()), "penalized;",
              int(out.drop_duplicates("id").cov_n_members.isna().sum()), "teams size missing")


if __name__ == "__main__":
    convert()
