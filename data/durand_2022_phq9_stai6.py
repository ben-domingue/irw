#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8784014
# DOI: 10.7717/peerj.12836
#   "Exploring the relationship between ADHD, its common comorbidities, and
#   their relationship to organizational skills" (Durand & Arbone, 2022),
#   PeerJ 10:e12836.
# Data: PeerJ supplementary file peerj-10-12836-s001.sav (407 x 107), fetched
#       from the Europe PMC supplementaryFiles zip. One row per respondent.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. No variable labels on the item columns (bare
#   PHQ_1..PHQ_9, STAI_1..STAI_6). Both instruments are published: PHQ-9
#   (Kroenke, Spitzer & Williams 2001) and the six-item STAI state short form
#   (Marteau & Bekker 1992).
#
# Tables:
#   durand_2022_phq9   PHQ-9, 9 items, 0-3 (paper: "4-point scale (0 = not at
#                      all, 3 = ...)")
#   durand_2022_stai6  STAI-6, 6 items, 1-4, as deposited. STAI_Total equals the
#                      plain sum of the six columns on every row, so the three
#                      anxiety-absent items are stored in whatever direction the
#                      authors scored them; not recoded here.
#
# SAME PEOPLE AS durand_2020_*. These 407 rows are exactly `Study == 1` of the
# Durand, Arbone & Wharton 2020 deposit (10.7717/peerj.9844): each row matches
# one and only one 2020 row on age + all 38 DOSQ + 18 ASRS items (asserted
# below). DOSQ and ASRS therefore ship once, in durand_2020_dosq/_asrs, and are
# skipped here. `id` is the 2020 table's id (its 1-based row number), so the
# PHQ-9/STAI-6 tables join onto the DOSQ/ASRS tables by id.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP22 = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8784014/supplementaryFiles"
SUPP20 = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7485505/supplementaryFiles"

DOSQ = [f"DOSQ_{i}" for i in range(1, 39)]
ASRS = [f"ASRS_{i}" for i in range(1, 19)]
PHQ = [f"PHQ_{i}" for i in range(1, 10)]
STAI = [f"STAI_{i}" for i in range(1, 7)]
SCALES = {
    "durand_2022_phq9": (PHQ, [0, 1, 2, 3]),
    "durand_2022_stai6": (STAI, [1, 2, 3, 4]),
}
COV = {
    "Language": "cov_language",          # 1 English 2 Spanish 3 French 4 other
    "Education": "cov_education",        # 17-level code (SPSS value labels)
    "Student": "cov_student",            # 1 yes, 2 no
    "Sex": "cov_sex",                    # 1 male, 2 female
    "Relationship": "cov_relationship",  # 1 single 2 casual 3 serious 4 rather not say
    "Location": "cov_location",
    "Ethnicity": "cov_ethnicity",
    "ADHDdiagnosis": "cov_adhd_diagnosis",       # 1 yes, 2 no
    "Depressiondiagnosis": "cov_depression_diagnosis",
    "Anxietydiagnosis": "cov_anxiety_diagnosis",
    "unlisteddiagnosis": "cov_other_diagnosis",
    "nodiagnosis": "cov_no_diagnosis",
    "Age": "cov_age",
    "ADHDmeds": "cov_adhd_meds",
    "ADHDtime": "cov_adhd_time_since_dx",
    "ADHDtherapy": "cov_adhd_therapy",
}
SKIP = {
    **{c: "shipped in durand_2020_dosq/_asrs (same respondents)" for c in DOSQ + ASRS},
    "Language_R": "collapse of Language",
    "Education_R": "collapse of Education",
    **{c: "subscale/total score (composite)" for c in [
        "DOSQ_work_organization", "DOSQ_communication_clarity",
        "DOSQ_punctuality", "DOSQ_goal_oriented", "DOSQ_assiduity",
        "DOSQ_workspace_organization", "DOSQ_strategies", "DOSQ_attentiveness",
        "DOSQ_Total", "ASRS_Total", "ASRS_PartA", "ASRS_inattention",
        "ASRS_hyperimpuls", "PHQ_Total", "STAI_Total"]},
    **{c: "cut-point classification of a total score" for c in [
        "PHQ_Diagnosis", "LowHighSTAIMean", "LowHighASRS"]},
}


def read_sav(url, member):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(z.read(member))
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


def convert():
    d = read_sav(SUPP22, "peerj-10-12836-s001.sav")
    assert d.shape == (407, 107), d.shape
    cols = set(d.columns)
    accounted = set(PHQ) | set(STAI) | set(COV) | set(SKIP)
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert (d[PHQ].sum(axis=1) == d["PHQ_Total"]).all()
    assert (d[STAI].sum(axis=1) == d["STAI_Total"]).all()

    # link onto the 2020 deposit's numbering (id = 1-based row number there)
    a = read_sav(SUPP20, "peerj-08-9844-s001.sav").reset_index(drop=True)
    a["id"] = a.index + 1
    key = ["Age"] + DOSQ + ASRS
    assert not a.duplicated(subset=key).any()
    d = d.merge(a[key + ["id", "Study"]], on=key, how="left", validate="1:1")
    assert d["id"].notna().all() and d["id"].is_unique
    assert (d["Study"] == 1).all()
    print("  linked 407/407 rows onto durand_2020 Study 1 ids")
    d["id"] = d["id"].astype(int)
    d = d.rename(columns=COV)
    covs = list(COV.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (cols_, pv) in SCALES.items():
        long = d.melt(id_vars=["id"] + covs, value_vars=cols_,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert long["resp"].isin(pv).all()
        long = long[["id", "item", "resp"] + covs].reset_index(drop=True)
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            long, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
