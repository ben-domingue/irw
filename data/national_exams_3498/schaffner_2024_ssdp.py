#!/usr/bin/env python3
# Nepal SSDP secondary teacher training evaluation: mathematics and science tests.
# Tables: schaffner_2024_ssdp_math, schaffner_2024_ssdp_science
#
# Source data: Schaffner, Glewwe & Sharma, "Replication Data for: Why Programs Fail:
#   Lessons for Improving Public Service Quality from a Mixed-Methods Evaluation of an
#   Unsuccessful Teacher Training Program in Nepal", Harvard Dataverse V4,
#   https://doi.org/10.7910/DVN/PBVH1F (Grade08baseline.dta, Grade09baseline.dta and the
#   four *_endline_IRT.dta files). Licence: CC0 1.0.
#   NOT the 3ie copy (doi:10.7910/DVN/8V9I67, CC BY-NC-SA).
# Paper: The World Bank Economic Review 39(2), 473-496, https://doi.org/10.1093/wber/lhae028
# Built from: nepal_ssdp_20261115.zip, national exams collection v1 by Santiago
#   Rivadeneira Quintero (irw#3498). That package was rebuilt cell by cell from the .dta
#   files, and all six raw-file SHA-256s were matched to the live deposit on 2026-11-25
#   (oneoff/national-exams-3498/PILOT_PROVENANCE.md).
#
# Design (one table per subject; two cohorts, two rounds):
#   wave       1 = baseline (Aug 2017 - Jan 2018), 2 = endline (Feb - Mar 2019).
#   id         the same id is the same student in both rounds (authors' student code).
#              Cohort A: grade 8 at baseline, grade 9 at endline (ids from 800001);
#              cohort B: grade 9 at baseline, grade 10 at endline (ids from 900001).
#   cov_baseline_grade  8 or 9 (the cohort); grade at endline is one higher.
#   item       the authors' item bank code (Math_007, Sci_089a), the same in both rounds
#              and both cohorts, so anchor items link across waves.
#   resp       item score. Baseline sections B and C are open-ended with partial credit;
#              on items with half points the score is doubled to stay integer, as in the
#              authors' panel files. Endline items are 0/1. Omitted items are 0 in the
#              source and cannot be told apart. No chosen option exists in the deposit.
#   treat      1 = either training arm, 0 = control. The trial has three arms;
#              treat_arm keeps them: 1 = Training Only, 2 = Training with VA, 3 = Control
#              (the authors' codes).
#   cluster_id school (the unit of randomisation; 203 schools).
#   treat, treat_arm, cluster_id and block_id are per row: the school the student sat
#              that test in, and its arm. 13 student-subject panels change school between
#              rounds, and 9 of them also change arm (6 in mathematics, 3 in science).
#              These are transfers or false links in the authors' student code; the
#              source cannot tell which. Drop those ids for an intention-to-treat analysis.
#   block_id   randomisation stratum (2).
#   cov_female missing where the source does not give sex, or where the two rounds
#              disagree (39 students per subject).
# Endline booklets: versions A and B share 12-16 items; version C is a misprinted copy of
#   A (mathematics only). Items are scored by bank code, so all three are in one table.
# Kept: 187 within-school groups of identical response vectors (likely copying), listed in
#   the package's extra/np_ssdp_vectores_repetidos.csv.

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
ZIP = os.path.join(PKG, "nepal_ssdp_20261115.zip")
RAW_SHA256 = {
    "Grade08baseline.dta": "a09acaa3d44eb04132a3c894b71d629f1da53363ebebddc270215d527b852548",
    "Grade09baseline.dta": "19e42dd87d9a496db0ea84dd48bbdd99f4fad16bbddf3770bf30ba0dc16e4070",
    "Math09_endline_IRT.dta": "756b7daeebcac9cadfde23f0b06da88fdcd91eff8d50b14e9e3abccd7f94296c",
    "Sci09_endline_IRT.dta": "3f4dbcfc7a4a7353be2f9ea28b7504e900d9df93e72fac7d567570f3aa6bd5e9",
    "Math10_endline_IRT.dta": "094f2ed5659c55f38ca9c490ec7baedf63a689ba3d0927be78c5cbee0bde7c10",
    "Sci10_endline_IRT.dta": "648baf3fed64a5af7b2b1dc408ef66f90a710eb0ed0aa472797cd76999eb753d",
}
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "automated_finding", "irw_output")
ROOT = "nepal_ssdp/"


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
        for f, h in zip(man.fichero_crudo, man.sha256_crudo):
            assert RAW_SHA256[f] == h, f"raw file differs from the CC0 deposit: {f}"
        grp = read_pkg(z, "extra/np_ssdp_grupo.csv")
        tables = {"mat": [], "sci": []}
        for test in man.test:
            _, _, year, grade, subj, _ = test.split("_")
            d = read_pkg(z, f"data/{test}.csv.gz")
            p = read_pkg(z, f"data/{test}_personas.csv", dtype={"sexo": str})
            assert not d.duplicated(["id", "item"]).any()
            assert d.opcion.isna().all()
            d["wave"] = {"2017": 1, "2019": 2}[year]
            d["test"] = test
            d = d.merge(p[["id", "sexo"]], on="id", how="left", validate="many_to_one")
            d = d.merge(grp.loc[grp.test == test, ["id", "escuela", "grupo_codigo", "estrato"]],
                        on="id", how="left", validate="many_to_one")
            assert d.grupo_codigo.notna().all()
            tables[subj].append(d)
    for subj, name in {"mat": "schaffner_2024_ssdp_math",
                       "sci": "schaffner_2024_ssdp_science"}.items():
        d = pd.concat(tables[subj], ignore_index=True)
        assert not d.duplicated(["id", "item", "wave"]).any()
        # sex: kept only when the rounds agree; missing when they conflict
        nsex = d.dropna(subset=["sexo"]).groupby("id").sexo.nunique()
        n_conflict = (nsex > 1).sum()
        sex = d.dropna(subset=["sexo"]).groupby("id").sexo.first()[nsex == 1]
        # treat/cluster_id/block_id are per row: the school the student sat that test in.
        n_arm = (d.groupby("id").grupo_codigo.nunique() > 1).sum()
        n_school = (d.groupby("id").escuela.nunique() > 1).sum()
        out = pd.DataFrame({
            "id": d.id,
            "item": d.item,
            "resp": d.resp.astype(int),
            "wave": d.wave,
            "treat": (d.grupo_codigo != 3).astype(int),
            "treat_arm": d.grupo_codigo.astype(int),
            "cluster_id": d.escuela,
            "block_id": d.estrato,
            "cov_baseline_grade": (d.id // 100000).astype(int),
            "cov_female": d.id.map(sex).map({"F": 1, "M": 0}).astype("Int64"),
        }).sort_values(["id", "wave", "item"])
        assert set(out.cov_baseline_grade) == {8, 9}
        os.makedirs(OUT_DIR, exist_ok=True)
        qc(out, name)
        out.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(name, len(out), "rows", out.id.nunique(), "students", out.item.nunique(),
              "items; between rounds,", n_school, "students change school and", n_arm,
              "change arm; sex conflicts (set missing) for", n_conflict)


if __name__ == "__main__":
    convert()
