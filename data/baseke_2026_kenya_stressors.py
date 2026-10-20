#!/usr/bin/env python3
# Source: https://osf.io/f9ybp/  ("Emerging Stressors and Adolescent Depression
#   and Anxiety in Kenya", Osborn, Coon, Kamau, Baseke, Musonye & Wasanga;
#   Shamiri Institute / Kenyatta University)
# Data: data/survey_d_deidentified.csv and data/survey_e_deidentified.csv
# DOI: the underlying dataset is documented in Baseke et al. (2026), Data in
#   Brief, https://doi.org/10.1016/j.dib.2026.112513; this OSF node holds the
#   analysis project that redistributes it.
# License: CC BY-NC-SA 4.0, as stated on the OSF node (public node, checked
#   2026-10-19 via api.osf.io). NC proceeds under datastandard.md "Before you
#   start" (ruled 2026-10-01); Derived_License carries the NC through.
#
# Two cross-sectional school-based surveys, May-June 2023, 74 secondary schools
# across Nairobi, Kiambu, Machakos and Makueni counties: survey D (2,865
# adolescents) and survey E (2,727). PHQ-8 and GAD-7 were administered in BOTH
# and ship as one table each with cov_study naming the survey, per
# datastandard.md's "same instrument administered to multiple samples" rule --
# the codebooks give the two surveys' stems word for word and they are the same
# items on the same 0-3 scale. Survey E's ids are offset by 100000 so no id
# collides with survey D's.
#
#   baseke_2026_phq8    PHQ_1-8     0-3  both surveys
#   baseke_2026_gad7    GAD_1-7     0-3  both surveys
#   baseke_2026_ccas    CCAS_1-10   1-5  survey D
#   baseke_2026_css11   CSS_1-11    see CAVEAT below, survey D
#   baseke_2026_smd9    SMD_1-9     0/1  survey E
#   baseke_2026_epv7    EPV_1-7     0-2  survey E
#
# CSS-11 CAVEAT (an issues-page entry is owed if this table ships): the paper
#   and the deposit's own codebook both document five options, "rated from 0
#   (not stressful at all) to 4 (extremely stressful)". The shared data holds
#   only THREE distinct values on every one of the 11 items, coded 1, 3 and 5.
#   The values are shipped exactly as recorded -- the direction is documented
#   and unambiguous, but which anchors the three codes correspond to is not,
#   so nothing is rescaled or relabelled here.
# NOT shipped, and why:
#   PHQ_Functioning / GAD_Functioning -- the instruments' functional-impairment
#     follow-up ("how difficult have they made it ..."), one question on a
#     different response format (0 not difficult ... 3 extremely difficult).
#     Folding it into the symptom scale would distort the scale and it cannot
#     be a table on its own (no single-item tables).
#   GAD_Check -- an embedded attention check ("If you read this question,
#     respond 'Not at all'"), not an item. The paper's sensitivity analysis
#     excludes respondents who failed it; this table keeps every respondent and
#     does not carry the check.
#   MEIS_9 / MEIS_12 (the paper's OAC-2 online-appearance-comparison pair) and
#     BESAA1 / BESAA5 / BESAA12 (its BESAA-3 appearance items) -- two- and
#     three-item scales. Deferred with the rest of the corpus's 3-4 item
#     candidates pending a ruling on table thinness, not rejected: both are
#     clean and the codebook gives their stems.
#   MEIS_Accounts (has social media y/n) and MEIS_Time (daily use band) are
#     single screening questions and ship as covariates.
# Covariates: study, age, gender, form, religion, county, surviving parents,
#   parents dead, father's/mother's education, co-curricular involvement,
#   sports team, perceived academic performance, interview interest, and (for
#   survey E) social-media account and daily-use band.
#   cov_religion carries the deposit's RAW codes: the codebook gives two rival
#   schemes, "for storage in database" (1-8, Hindu present) and "for analysis"
#   (1-7, Hindu absent), and the data's range 1-8 identifies the storage one.
# cluster_id = school_name (the sampling unit; 36 schools in D, 38 in E).
# date = todays_date as Unix seconds, kept ONLY where it falls in the
#   documented May-June 2023 window. The field is interviewer-typed and the
#   year is frequently mistyped (2013, 2020, 2027, 2028, 2033, 2073, 2823,
#   2883, one literal "invalid"); blanking those is more honest than shipping a
#   date 800 years out. survey D is dd/mm/yyyy and survey E is m/d/yyyy -- the
#   two files disagree, and the script asserts which is which.
# id is the row index within each survey (the files carry no id column; one row
#   is one respondent, and the deposit is already de-identified).
# Item text: CHEAP AND OWED -- both codebooks (.docx, in data/) give every stem
#   with its code explicitly ("1. Little interest or pleasure in doing things?
#   -> PHQ_1") and every response option with its value. Not shipped in this
#   commit; it is the next step for this batch. The instruments are PHQ-8,
#   GAD-7, the Climate Change Anxiety Scale (Clayton & Karazsia 2020), the
#   COVID-19 Stressors Scale, the Social Media Disorder Scale (van den Eijnden
#   et al. 2016) and an EPV index adapted from the Political Life Events scale
#   -- all third-party instruments, so each needs its rights-register row read
#   before its text ships.

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SURVEYS = {
    "survey_d": ("https://osf.io/download/vpgsd/", "%d/%m/%Y", 0),
    "survey_e": ("https://osf.io/download/6a4c299d2b4e3ad2847ccf28/", "%m/%d/%Y", 100000),
}
WINDOW = ("2023-05-01", "2023-06-30")

COVS = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Form": "cov_form",
    "Religion": "cov_religion",
    "County": "cov_county",
    "Surviving_Parents": "cov_surviving_parents",
    "Parents_Dead": "cov_parents_dead",
    "Fathers_Education": "cov_fathers_education",
    "Mothers_Education": "cov_mothers_education",
    "Co_Curricular": "cov_co_curricular",
    "Sports": "cov_sports",
    "Percieved_Academic_Abilities": "cov_academic_self_rating",
    "interview_ok": "cov_interview_interest",
    "MEIS_Accounts": "cov_social_media_accounts",
    "MEIS_Time": "cov_social_media_time",
}
# table -> (item columns, surveys it was administered in, permitted values)
SCALES = {
    "baseke_2026_phq8": ([f"PHQ_{i}" for i in range(1, 9)],
                         ["survey_d", "survey_e"], {0, 1, 2, 3}),
    "baseke_2026_gad7": ([f"GAD_{i}" for i in range(1, 8)],
                         ["survey_d", "survey_e"], {0, 1, 2, 3}),
    "baseke_2026_ccas": ([f"CCAS_{i}" for i in range(1, 11)],
                         ["survey_d"], {1, 2, 3, 4, 5}),
    "baseke_2026_css11": ([f"CSS_{i}" for i in range(1, 12)],
                          ["survey_d"], {1, 3, 5}),
    "baseke_2026_smd9": ([f"SMD_{i}" for i in range(1, 10)],
                         ["survey_e"], {0, 1}),
    "baseke_2026_epv7": ([f"EPV_{i}" for i in range(1, 8)],
                         ["survey_e"], {0, 1, 2}),
}
DROPPED = {
    "PHQ_Functioning": "functional-impairment follow-up, different format",
    "GAD_Functioning": "functional-impairment follow-up, different format",
    "GAD_Check": "embedded attention check, not an item",
    "MEIS_9": "OAC-2, a 2-item scale -- deferred on thinness",
    "MEIS_12": "OAC-2, a 2-item scale -- deferred on thinness",
    "BESAA1": "BESAA-3, a 3-item scale -- deferred on thinness",
    "BESAA5": "BESAA-3, a 3-item scale -- deferred on thinness",
    "BESAA12": "BESAA-3, a 3-item scale -- deferred on thinness",
}


def load() -> dict:
    out = {}
    for name, (url, fmt, offset) in SURVEYS.items():
        r = requests.get(url, headers=UA, timeout=180)
        r.raise_for_status()
        d = pd.read_csv(BytesIO(r.content))
        assert not d.duplicated().any(), name
        d = d.reset_index(drop=True)
        d["id"] = d.index + 1 + offset

        # The two files disagree on date order; prove which reading is right
        # rather than trusting the column.
        here = pd.to_datetime(d["todays_date"], format=fmt, errors="coerce")
        other = "%m/%d/%Y" if fmt == "%d/%m/%Y" else "%d/%m/%Y"
        there = pd.to_datetime(d["todays_date"], format=other, errors="coerce")
        in_win = here.between(*WINDOW).sum()
        assert in_win > there.between(*WINDOW).sum(), (name, fmt)
        assert in_win > 0.8 * len(d), (name, in_win, len(d))
        keep = here.between(*WINDOW)
        # Plain float64 with NaN, not the nullable Float64: the validator reads
        # the written column's dtype and an extension dtype reads as non-numeric.
        d["date"] = (here.where(keep).astype("int64", errors="ignore")
                     .astype("float64") / 10 ** 9)
        d.loc[~keep, "date"] = float("nan")
        out[name] = d
        print(f"  {name}: {len(d)} rows, {keep.sum()} dates inside "
              f"{WINDOW[0]}..{WINDOW[1]}, {len(d) - keep.sum()} blanked")
    return out


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load()

    # Balance the books across both files.
    claimed = set(DROPPED) | {"id", "date", "school_name", "todays_date"} | set(COVS)
    for cols, _, _ in SCALES.values():
        claimed |= set(cols)
    for name, d in data.items():
        unaccounted = set(d.columns) - claimed
        assert not unaccounted, (name, unaccounted)
    for col, why in DROPPED.items():
        where = [n for n, d in data.items() if col in d.columns]
        print(f"  dropped {col} ({', '.join(where)}): {why}")

    for name, (items, surveys, pv_set) in SCALES.items():
        parts = []
        for s in surveys:
            d = data[s]
            missing = [c for c in items if c not in d.columns]
            assert not missing, (name, s, missing)
            cov_cols = [c for c in COVS if c in d.columns]
            long = d.melt(
                id_vars=["id", "date", "school_name"] + cov_cols,
                value_vars=items, var_name="item", value_name="resp")
            long = long.rename(columns={**COVS, "school_name": "cluster_id"})
            long["cov_study"] = s
            parts.append(long)
        t = pd.concat(parts, ignore_index=True)
        t["resp"] = pd.to_numeric(t["resp"], errors="coerce")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)

        cov_cols = sorted(c for c in t.columns if c.startswith("cov_"))
        t = t[["id", "item", "resp", "date", "cluster_id"] + cov_cols]
        t = t.sort_values(["id", "item"]).reset_index(drop=True)

        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100, t["id"].nunique()
        assert t["item"].nunique() == len(items)
        assert set(t["resp"].unique()) <= pv_set, \
            (name, sorted(set(t["resp"].unique()) - pv_set))
        if len(surveys) == 2:
            assert t.groupby("cov_study")["id"].nunique().min() >= 100
            assert t["id"].nunique() == sum(
                t.loc[t["cov_study"] == s, "id"].nunique() for s in surveys)

        pv = {i: pv_set for i in items}
        cl = {i: name.replace("baseke_2026_", "") for i in items}
        fails = [(c.name, c.detail) for c in
                 run_qc(t, permitted_values=pv, item_constructs=cl) if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": pv, "item_constructs": cl})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()} "
              f"schools={t['cluster_id'].nunique()} studies={','.join(surveys)}")


if __name__ == "__main__":
    convert()
