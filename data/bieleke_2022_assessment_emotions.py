#!/usr/bin/env python3
# Source: https://osf.io/3pmr4/
# DOI: 10.1371/journal.pone.0272443
# Paper: Bieleke M, Schwarzkopf J-M, Goetz T, Haag L (2022). The agonizing
#   effects of uncertainty: Effects of announced vs. unannounced performance
#   assessments on emotions and achievement. PLOS ONE 17(8): e0272443.
# Data: OSF node 3pmr4, one file data/dataset.xlsx (one sheet), 414 rows x 52
#   columns. No codebook in the deposit; the paper's Methods and Table 1
#   document the scales and the four time points.
# License: CC BY 4.0, set on node 3pmr4 by Maik Bieleke after an IRW ask of
#   2026-11-09 (verified via the OSF API on 2026-11-18; licence object
#   563c1cf88c5e4a3877f9e96a = "CC-By Attribution 4.0 International"). Logged
#   in processing_notes/outreach/outreach_log.csv.
#
# Found by the PLOS monthly run of 2026-11-09 (licence-blocked then, see
# automated_finding/license_blocked_candidates.csv).
#
# Sample (paper, Participants): 414 students (53.4% female) in 11 lower-level
# classes (grades 8-10) and 8 upper-level classes (grade 11) of one Gymnasium in
# Hamburg, Germany, in economics, geography, and politics/society/business.
# Paper-and-pencil questionnaires in German, given by the teacher in class.
# Age was not collected.
#
# Design (paper, Procedure): the same questionnaire four times per student.
#   wave 1  two weeks before an UNANNOUNCED performance assessment (students
#           were told one would come at some point in the half-year)
#   wave 2  on the day of the unannounced assessment, just before the test
#   wave 3  two weeks before an ANNOUNCED assessment, on the day it was announced
#   wave 4  on the day of the announced assessment, just before the test
# Assessment type is fixed by the wave (1-2 unannounced, 3-4 announced) for
# every student, so it is not a separate `treat` column: nothing was assigned.
#
# TWO output tables, each with `wave` 1-4:
#   bieleke_2022_assess_enjoyment  3 enjoyment items, 1-4 (1 strongly disagree
#       .. 4 strongly agree). Source columns jo{k}{t}: item k (1-3), time point
#       t (1-4); shipped as item jo{k}, wave t.
#   bieleke_2022_assess_anxiety    6 anxiety items, same 1-4 scale. Source
#       columns dx{k}{t} and ta{k}{t} (k 1-3), shipped as items dx{k} / ta{k},
#       wave t. The paper treats all six as one anxiety measure (alpha .75-.84
#       "across all time points"), and the deposit's own composite ax{t} is the
#       plain mean of all six (asserted), so one table. The paper does not say
#       what the dx/ta prefixes stand for; item codes are the source's. Its
#       two anxiety sources are the German PISA 2003 report (ref. 31) and the
#       Angstfragebogen fuer Schueler (AFS, ref. 32), so dx/ta may mark which
#       items came from which, but that is not documented and the validator's
#       multi_scale warning is answered by the paper's one six-item scale.
#   Item scale (paper, Instruments): "The corresponding statements were rated
#   on a four-point Likert scale ranging from 1 (strongly disagree) to, 4
#   (strongly agree)." Every stored value is 1, 2, 3, 4 or blank (asserted).
#   Direction: shipped as stored. The deposit's composites equal plain item
#   means, and the time-point means reproduce the paper's Table 1 exactly
#   (enjoyment 3.06/2.59/3.05/2.85, anxiety 2.08/2.57/1.56/1.91; asserted).
#   Missing: whole time points are blank for 7-13 students each (a student
#   absent that day); blank responses are dropped, not imputed. "imput" is
#   absent from the article.
#
# NOT SHIPPED: composites jo1-jo4 and ax1-ax4 (note jo1..jo4 are the per-wave
#   enjoyment MEANS, three characters, not items; items are four characters).
#
# `id`: the deposit's ID, "<class>_<student-within-class>" (unique, asserted).
#   Not personal: Student is a 1..29 index within each class.
# `cluster_id`: Class (1-19), the class the student sits in. Every class is
#   one track level and one subject (asserted).
#
# Covariates:
#   cov_sex        female / male (source: weiblich / maennlich; 53.4% female,
#                  as in the paper, asserted).
#   cov_track      lower (source "Mittelstufe", grades 8-10) / upper
#                  ("Oberstufe", grade 11).
#   cov_subject    economics ("Wirtschaft"), geography ("Geographie"),
#                  politics_society_business ("PGW", Politik/Gesellschaft/
#                  Wirtschaft).
#   cov_perf_t2    grade on the unannounced assessment (taken at wave 2), and
#   cov_perf_t4    on the announced one (wave 4), AS STORED: the negated German
#                  grade, -1 (very good) to -6 (insufficient), in thirds for
#                  +/- grades, so higher = better. The paper describes them as
#                  inverted grades; its Table 1 means (3.06, 2.46) equal the
#                  stored means in absolute value. Blank for 12 / 11 students.
#
# Item text: not shipped -- no wording in the deposit, and the paper quotes
#   one example item per construct only. Enjoyment items follow the paper's
#   ref. 30 (Jerusalem et al. 2009), anxiety refs. 31-32 (PISA 2003, AFS).
#
# PII: string columns are ID (class_student index), Sex, Grade, Subject -- all
#   categorical. No names, emails, dates, locations or free text.

import hashlib
import os
import sys
import tempfile

import numpy as np
import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/ypdbr/"
SHA256 = "49ca58e2176fe524b7290673caae6c6f764570c082e70fb4cc9a7ca0c0c168c4"
RAW = os.environ.get("BIELEKE_RAW", "")
N_ROWS = 414
WAVES = (1, 2, 3, 4)

ENJOY = ["jo1", "jo2", "jo3"]
ANX = ["dx1", "dx2", "dx3", "ta1", "ta2", "ta3"]
TABLES = {
    "bieleke_2022_assess_enjoyment": ENJOY,
    "bieleke_2022_assess_anxiety": ANX,
}
# Paper Table 1, per-wave scale means.
PAPER_MEANS = {"jo": [3.06, 2.59, 3.05, 2.85], "ax": [2.08, 2.57, 1.56, 1.91]}

TRACK = {"Mittelstufe": "lower", "Oberstufe": "upper"}
SUBJECT = {"Wirtschaft": "economics", "Geographie": "geography",
           "PGW": "politics_society_business"}


def src(item, t):
    """Source column for item code (e.g. 'jo2', 'ta3') at time point t."""
    return f"{item}{t}"


def fetch():
    if RAW:
        path = RAW
    else:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"},
                         timeout=120)
        r.raise_for_status()
        path = os.path.join(tempfile.mkdtemp(), "dataset.xlsx")
        with open(path, "wb") as fh:
            fh.write(r.content)
    with open(path, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == SHA256, "raw changed"
    return path


def convert():
    df = pd.read_excel(fetch())
    assert df.shape == (N_ROWS, 52), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert sorted(strings) == ["Grade", "ID", "Sex", "Subject"]

    assert df["ID"].is_unique
    assert (df["ID"] == df["Class"].astype(str) + "_"
            + df["Student"].astype(str)).all()
    assert (df.groupby("Class")[["Grade", "Subject"]].nunique() == 1).all().all()

    items = [src(i, t) for i in ENJOY + ANX for t in WAVES]
    vals = pd.unique(df[items].to_numpy().ravel())
    assert set(v for v in vals if v == v) == {1, 2, 3, 4}, vals
    for t in WAVES:
        jo = df[[src(i, t) for i in ENJOY]].mean(axis=1)
        ax = df[[src(i, t) for i in ANX]].mean(axis=1)
        assert np.allclose(jo, df[f"jo{t}"], equal_nan=True), t
        assert np.allclose(ax, df[f"ax{t}"], equal_nan=True), t
        assert round(jo.mean(), 2) == PAPER_MEANS["jo"][t - 1], t
        assert round(ax.mean(), 2) == PAPER_MEANS["ax"][t - 1], t

    sex = df["Sex"].map(lambda s: "female" if s == "weiblich"
                        else "male" if s.startswith("m") and s.endswith("nnlich")
                        else None)
    assert sex.notna().all()
    assert round((sex == "female").mean(), 3) == 0.534  # paper: 53.4% female
    base = pd.DataFrame({
        "id": df["ID"],
        "cluster_id": df["Class"].astype(int),
        "cov_sex": sex,
        "cov_track": df["Grade"].map(TRACK),
        "cov_subject": df["Subject"].map(SUBJECT),
        "cov_perf_t2": df["mark2"],
        "cov_perf_t4": df["mark4"],
    })
    assert base.drop(columns=["cov_perf_t2", "cov_perf_t4"]).notna().all().all()
    for c in ("cov_perf_t2", "cov_perf_t4"):
        assert base[c].dropna().between(-6, -0.5).all(), c
    cov_cols = [c for c in base.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, codes in TABLES.items():
        assert len(name) <= 40, name
        parts = []
        for t in WAVES:
            sub = df[[src(i, t) for i in codes]].copy()
            sub.columns = codes
            sub.insert(0, "id", df["ID"])
            long = sub.melt(id_vars=["id"], var_name="item", value_name="resp")
            long["wave"] = t
            parts.append(long)
        long = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long.merge(base, on="id", how="left", validate="many_to_one")
        long = long[["id", "item", "resp", "wave", "cluster_id"] + cov_cols]
        assert not long.duplicated(["id", "item", "wave"]).any()
        # a time point is all-or-nothing per student
        per = long.groupby(["id", "wave"]).size()
        assert (per == len(codes)).all(), name
        checks = run_qc(long, permitted_values=[1, 2, 3, 4])
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} waves={sorted(long['wave'].unique())} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    print(f"{len(TABLES)} tables, {total} responses")


if __name__ == "__main__":
    convert()
