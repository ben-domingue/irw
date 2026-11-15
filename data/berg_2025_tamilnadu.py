#!/usr/bin/env python3
# Source: Zenodo 10.5281/zenodo.17119441, "Replication package for: The
#   productivity of public and private preschools (and schools): Evidence from
#   India" (Romero, Singh, Berg; 2025-09-15).
# Paper: Berg P, Romero M, Singh A (2025). The Productivity of Public and
#   Private Preschools (and Schools): Evidence from India. The Economic
#   Journal. doi:10.1093/ej/ueaf089
# License: Zenodo record says CC BY 4.0; the package README.pdf says the raw
#   survey data are CC BY-NC. Abhijeet Singh gave written permission to include
#   the data in IRW (email to Santiago Rivadeneira, 2026-11-13). IRW labels the
#   tables CC BY 4.0 as on Zenodo, pending the authors' word otherwise.
#
# Children aged 3-10 (11 in 2023) in 215 villages of four rural Tamil Nadu
# districts, tested individually at home in Tamil, with age-specific booklets
# whose items overlap across ages and rounds (the authors link them with a
# pooled 2PL). Two waves:
#   wave 1 = 2022 baseline (fielded Dec 2021 - 2022). From
#     child_level_tnece_tnll_assmt_appended.csv, rows with project_round =
#     TNLL (the Stata code's `keep if project_round==2`; the TNECE rows are an
#     earlier project and carry no tq_/mq_ booklet).
#   wave 2 = 2023 endline. From Compiled_scores_2022and2023.csv, rows with a
#     phase_2023. That file carries no member id, so, as the authors do, it is
#     joined to the 2023 household roster
#     (HHsurvey_reshaped_data_completed_forms.csv) on household + child age.
#     Unlike the authors' `duplicates drop ..., force`, which keeps an
#     arbitrary row, a household with two tested children of the same age is
#     DROPPED from wave 2 rather than guessed at (counts asserted below).
#     The authors also drop 2023 11-year-olds ("no information about their
#     test booklets yet"); IRW keeps them, since their items are scored 0/1
#     like everyone else's. Filter cov_age < 11 to match the paper.
#
# THREE output tables, the authors' own split (code/data_construction/
# 1_data_construction.do renames tq_1-4 and tq_10-17 to eq_* as executive
# function, and fits separate IRT models for math and Tamil):
#   berg_2025_tamilnadu_math   mq_* items
#   berg_2025_tamilnadu_tamil  tq_* items other than the EF ones
#   berg_2025_tamilnadu_ef     tq_1-4, tq_10-17 (item codes kept as tq_*)
# Item codes are the deposit's; TNLL_TNECE_consolidated_itemmap.xlsx (in the
# package) maps them to item text, competency and source. resp is 0/1; an item
# not in a child's booklet is absent, not 0.
#
# id: one integer per child (household id + member id), shared by the three
#   tables and both waves, so a child links across waves. Household ids are
#   NOT published: ids are assigned in order of a salted hash.
# cluster_id: the village (deposit site_code, recoded to an integer).
# date: survey date, Unix seconds (day resolution in the source).
# Covariates: cov_age (years, at that wave), cov_gender (male/female),
#   cov_district, cov_grade (class at that wave: below_lkg, lkg, ukg, 1-12,
#   not_enrolled, no_school; "don't know" -> NA), cov_school_type
#   (government, government_residential, private, anganwadi; "don't know" ->
#   NA). Household SES items are not carried.
#
# Usage: python3 berg_2025_tamilnadu.py <data_raw dir> <output dir>

import hashlib
import os
import sys

import numpy as np
import pandas as pd

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

EF = {f"tq_{i}" for i in list(range(1, 5)) + list(range(10, 18))}
GRADE = {1: "below_lkg", 2: "lkg", 3: "ukg", **{k: str(k - 3) for k in range(4, 16)},
         16: "not_enrolled", 17: "no_school"}
SCHOOL = {1: "government", 2: "government_residential", 3: "private", 4: "anganwadi"}
GENDER = {1: "male", 2: "female"}


def read_dta(name):
    return pd.read_stata(os.path.join(RAW, name), convert_categoricals=False)


# ---- wave 1: 2022 ----------------------------------------------------------
a = read_dta("child_level_tnece_tnll_assmt_appended.dta")
a = a[a.project_round == 2].copy()
assert len(a) == 27089, len(a)
# 9 exact (household, member) repeats, as the authors' comment says.
assert a.duplicated(["awc_hh_id_tnece", "mb_id"]).sum() == 9
a = a.drop_duplicates(["awc_hh_id_tnece", "mb_id"], keep="first")
items1 = [c for c in a.columns if c.startswith(("tq_", "mq_"))]
w1 = pd.DataFrame({
    "hhid": a.awc_hh_id_tnece, "mb_id": a.mb_id, "wave": 1,
    "date": pd.to_datetime(a.submissiondate, format="%b %d, %Y %I:%M:%S %p").dt.normalize(),
    "site": a.sitecode.astype("Int64").astype(str), "cov_district": a.district.str.lower(),
    "cov_age": a.i02_q13_age_yrs, "cov_gender": a.i02_q12_gender.map(GENDER),
    "cov_grade": a.class_tnll.map(GRADE), "cov_school_type": a.tnll_q19_school_type.map(SCHOOL),
})
w1 = pd.concat([w1, a[items1]], axis=1)

# ---- wave 2: 2023 ----------------------------------------------------------
b = read_dta("Compiled_scores_2022and2023.dta")
b = b[b.phase_2023.notna() & (b.survey_status == 1)].copy()
b = b.rename(columns={"awc_hh_id_tnece": "hhid", "q10_child_age": "age"})
b["age"] = b.age.astype(int)
h = read_dta("HHsurvey_reshaped_data_completed_forms.dta")
h = h.rename(columns={"awc_hh_id_tnece": "hhid"})
h = h.drop_duplicates(["hhid", "mb_id"])
h["age"] = pd.to_numeric(h.child_age_, errors="coerce")
h = h[h.age.notna()]
h["age"] = h.age.astype(int)

n_b = len(b)
amb_b = b.duplicated(["hhid", "age"], keep=False)
amb_h = h.duplicated(["hhid", "age"], keep=False)
b, h = b[~amb_b], h[~amb_h]
m = b.merge(h, on=["hhid", "age"], how="inner", suffixes=("", "_hh"), validate="1:1")
print(f"wave 2: {n_b} tests; {amb_b.sum()} dropped (two tests share household+age); "
      f"{amb_h.sum()} roster rows ambiguous; {len(m)} linked to a member id")

items2 = [c for c in b.columns if c.startswith(("tq_", "mq_"))]
num = lambda s: pd.to_numeric(s, errors="coerce")
w2 = pd.DataFrame({
    "hhid": m.hhid, "mb_id": m.mb_id, "wave": 2,
    "date": pd.to_datetime(m.date, format="%d%b%Y"),
    "site": num(m.site_code).astype("Int64").astype(str), "cov_district": m.district.str.lower(),
    "cov_age": m.age, "cov_gender": num(m.child_gender_).map(GENDER),
    "cov_grade": num(m.child_grade_).map(GRADE), "cov_school_type": num(m.child_school_type_).map(SCHOOL),
})
w2 = pd.concat([w2, m[items2]], axis=1)

wide = pd.concat([w1, w2], ignore_index=True)

# ids: salted-hash order, so household ids cannot be read back from id order.
salt = "irw-berg-2025-tamilnadu"
key = wide.hhid.astype(str) + "|" + wide.mb_id.astype(str)
h8 = key.map(lambda k: hashlib.sha256((salt + k).encode()).hexdigest())
order = {k: i + 1 for i, k in enumerate(sorted(h8.unique()))}
wide["id"] = h8.map(order)
sites = sorted(wide.site.unique(), key=lambda s: hashlib.sha256((salt + s).encode()).hexdigest())
wide["cluster_id"] = wide.site.map({s: i + 1 for i, s in enumerate(sites)})
wide["date"] = (wide.date - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)

assert not wide.duplicated(["id", "wave"]).any()
print("children:", wide.id.nunique(), "| in both waves:",
      (wide.groupby("id").wave.nunique() == 2).sum(), "| villages:", wide.cluster_id.nunique())

COV = ["cov_age", "cov_gender", "cov_district", "cov_grade", "cov_school_type"]
allitems = sorted(set(items1) | set(items2), key=lambda c: (c[:2], int(c.split("_")[1])))
long = wide.melt(id_vars=["id", "wave", "date", "cluster_id"] + COV, value_vars=allitems,
                 var_name="item", value_name="resp")
long = long[long.resp.notna()]
assert set(long.resp.unique()) <= {0, 1}
long["resp"] = long.resp.astype(int)

tables = {
    "berg_2025_tamilnadu_math": long[long.item.str.startswith("mq_")],
    "berg_2025_tamilnadu_tamil": long[long.item.str.startswith("tq_") & ~long.item.isin(EF)],
    "berg_2025_tamilnadu_ef": long[long.item.isin(EF)],
}
for name, t in tables.items():
    t = t[["id", "item", "resp", "wave", "date", "cluster_id"] + COV]
    t = t.sort_values(["wave", "id", "item"])
    t.to_csv(os.path.join(OUT, name + ".csv"), index=False)
    print(f"{name}: {len(t)} rows, {t.id.nunique()} children, {t.item.nunique()} items, "
          f"waves {t.groupby('wave').id.nunique().to_dict()}")
