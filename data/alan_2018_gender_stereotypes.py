"""Alan, Ertac & Mumcu (2018), Harvard Dataverse -- gender stereotypes in the
classroom, Turkish primary schools.

Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/FGBZCK
DOI: 10.7910/DVN/FGBZCK
License: CC0 1.0
Paper: Review of Economics and Statistics 100(5), 876-890.

3,855 grade 3/4 students taught by 145 teachers. Both the students and their
teachers answered short attitude batteries; the deposit is a
one-row-per-student file, so the teacher batteries are repeated once per
student and have to be collapsed to the teacher before melting.

Tables written
--------------
alan_2018_student_gender_attitudes    3,855 students x  7 items, 1-4
alan_2018_teacher_gender_attitudes      145 teachers x  9 items, 1-4
alan_2018_teacher_growth_mindset        145 teachers x  5 items, 1-4
alan_2018_teacher_modern_teaching       145 teachers x  6 items, 1-4
alan_2018_teacher_warmth                145 teachers x  4 items, 1-4
alan_2018_teacher_extrinsic_motivation  145 teachers x  4 items, 1-4

Coding notes
------------
* **Two units of observation, so two id spaces.** `id` in the student table is
  the deposit's `ID`; `id` in the five teacher tables is `newid`, the deposit's
  own `group(teachername)`. They are not comparable and the tables must not be
  stacked. That every `ts_*` value is constant within `newid` is asserted, not
  assumed -- it is what licenses the collapse.
* Each battery is its own table: they are separate named constructs (the
  variable labels name them), even though all six share a 1-4 scale.
* `ss_gms_1`/`ss_gms_2` (student growth mindset) are only two items and are
  not shipped -- see the skip accounting printed by the build.
* `ts_6` ("boys are better in maths") is a single item on a 1-3 scale and is
  likewise not shipped.
* Covariates come from the same row: student sex/SES/grade/home background on
  the student table, teacher sex/experience/tenure/degree on the teacher ones.
* The deposit carries no item text; the Stata variable labels are one-word
  cues ("soccer", "nurse", "sewing"), kept as the item ids so the published
  instrument can join later.
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

BASE = "https://dataverse.harvard.edu"
DOI = "10.7910/DVN/FGBZCK"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"

STUDENT_COVS = {"male": "cov_male", "ses": "cov_ses", "grade": "cov_grade",
                "working_mom": "cov_working_mother",
                "computer": "cov_owns_computer",
                "age_m_mean": "cov_age_months"}
TEACHER_COVS = {"tmale": "cov_male", "ts_2": "cov_years_experience",
                "ts_3": "cov_tenured", "ts_4": "cov_degree",
                "qual": "cov_qualification"}

# (table suffix, unit, source prefix, number of items)
BLOCKS = [
    ("student_gender_attitudes",   "student", "ss_gender_", 7),
    ("teacher_gender_attitudes",   "teacher", "ts_gender_", 9),
    ("teacher_growth_mindset",     "teacher", "ts_gms_",    5),
    ("teacher_modern_teaching",    "teacher", "ts_modern_", 6),
    ("teacher_warmth",             "teacher", "ts_warmth_", 4),
    ("teacher_extrinsic_motivation", "teacher", "ts_ext_",  4),
]


def qc(df, name):
    checks = run_qc(df)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, (name, [(c.name, c.detail) for c in bad])
    for c in checks:
        if c.status == "warn":
            print(f"    [warn] {name}: {c.name}: {c.detail}")


def main():
    s = requests.Session()
    s.headers.update(UA)
    meta = s.get(f"{BASE}/api/datasets/:persistentId/",
                 params={"persistentId": f"doi:{DOI}"}, timeout=120
                 ).json()["data"]["latestVersion"]
    hit = [f["dataFile"] for f in meta["files"]
           if f["dataFile"]["filename"] == "gstyping.tab"]
    assert len(hit) == 1, [f["dataFile"]["filename"] for f in meta["files"]]
    raw = s.get(f"{BASE}/api/access/datafile/{hit[0]['id']}",
                params={"format": "original"}, timeout=600)
    raw.raise_for_status()
    d = pd.read_stata(io.BytesIO(raw.content), convert_categoricals=False)

    # the teacher batteries repeat once per student; collapsing them is only
    # legitimate if they really are constant within teacher.
    tcols = [c for c in d.columns
             if c.startswith("ts_") or c in TEACHER_COVS]
    varying = [c for c in tcols
               if d.groupby("newid")[c].nunique(dropna=False).max() > 1]
    assert not varying, varying
    teachers = d.drop_duplicates("newid").reset_index(drop=True)

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for suffix, unit, prefix, n_expected in BLOCKS:
        src = d if unit == "student" else teachers
        idcol, covs = (("ID", STUDENT_COVS) if unit == "student"
                       else ("newid", TEACHER_COVS))
        items = [c for c in src.columns if c.startswith(prefix)]
        assert len(items) == n_expected, (suffix, sorted(items))
        shipped.update(items)

        long = src.melt(id_vars=[idcol] + list(covs),
                        value_vars=items, var_name="item", value_name="resp")
        long = long.rename(columns={idcol: "id", **covs})
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["item"] = long["item"].str.replace(prefix, "", regex=False)
        long["item"] = prefix.rstrip("_") + "_" + long["item"]
        long = long[["id", "item", "resp"] + [covs[c] for c in covs]]

        assert long["resp"].between(1, 4).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        qc(long, suffix)

        name = f"alan_2018_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), f"duplicate table name {name}"
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} {unit}s x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long) / (n_id * n_it):.3f}")

    # balance the books: every source column is shipped, a covariate, or
    # skipped for a printed reason.
    accounted = set(shipped) | set(STUDENT_COVS) | set(TEACHER_COVS) | {
        "ID", "newid", "teachername"}
    skips = {
        "ss_gms_1": "student growth mindset -- only 2 items",
        "ss_gms_2": "student growth mindset -- only 2 items",
        "ts_6": "single item, 1-3 scale",
        "ts_1": "count of terms with the class, not a rating",
        "ts_5": "count of volunteer activities, not a rating",
        "tt_train": "count of training programmes, not a rating",
        "tss_no_teach": "count of terms teaching the student",
        "tss_behavior": "single teacher rating of the student",
        "tss_grade_tr": "teacher-assigned school grade, not an item",
        "tss_grade_math": "teacher-assigned school grade, not an item",
        "hhgender": "single family-composition question",
        "pterm": "unlabelled administrative code",
        "raven_std": "standardised test score, not item-level",
        "turkish_std": "standardised test score, not item-level",
        "math_std": "standardised test score, not item-level",
        "conf": "derived confidence index",
        "proximity": "school id",
        "district": "school-level covariate",
    }
    for c in d.columns:
        if c in accounted:
            continue
        if c in skips:
            print(f"  skip {c}: {skips[c]}")
        elif c.startswith(("prox", "qual", "educ")):
            print(f"  skip {c}: dummy expansion of a covariate")
        else:
            raise AssertionError(f"unaccounted source column: {c}")

    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
