#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0196020
# DOI: 10.1371/journal.pone.0196020
# Paper: Capacci, S., Mazzocchi, M., & Brasini, S. (2018). Estimation of
#   unobservable selection effects in on-line surveys through propensity
#   score matching: An application to public acceptance of healthy eating
#   policies. PLOS ONE 13(4): e0196020.
# Data: journal.pone.0196020.s002 (S1 Dataset, "SPSS data", .sav), 1,001
#   adults in the UK (500) and Italy (501), EATWELL project survey; in each
#   country half by telephone (CATI, random-digit dialling) and half by web
#   panel (CAWI), 250/250 and 250/251.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# THREE output tables (study-authored EATWELL questionnaire):
#   capacci_2018_policy_support   q29_1-9 + q30_01-11 (20 items): agreement
#       with healthy-eating policy measures (advertising bans, labelling,
#       fat taxes, subsidies, school-meal regulation, ...), 1 strongly
#       disagree .. 5 strongly agree. "Don't know" (code 6) is already blank
#       in the deposit for every one of these columns.
#   capacci_2018_personal_risk    q23_1-6 (6 items): how serious a risk to
#       your own health -- your weight, eating, drinking, smoking, local
#       pollution, stress; 1 "Not at all serious" .. 7 "Very serious".
#       Code 8 "Not applicable" (e.g. smoking, for a non-smoker) dropped.
#   capacci_2018_societal_risk    q27_1-9 (9 items): how serious a problem
#       for society -- cancer, AIDS, heart disease, diabetes, smoking, heavy
#       drinking, obesity, depression, influenza; 1 "Very serious problem"
#       .. 5 "Not a serious problem at all" (NOTE the direction: 1 is the
#       MOST serious). Code 6 "Don't know" dropped.
# The deposit's derived recodes of the same 20 policy items
# (AdvertChildren .. VATmeasures: not supportive/neutral/supportive/DK)
# and socrisk are dropped.
#
# Covariates: country (UK / Italy), administration mode (CATI / CAWI -- the
# paper's object of study), gender, age, marital status, harmonised
# education (low/medium/high), self-rated health (q03), all with the .sav's
# own value labels. uniq_id is the deposit's serial number, kept as `id`.
# Not carried: the survey weight w_fac and the rest of the questionnaire
# (internet use, household, physical activity, eating-out frequency, the
# two q28 government-role items, chronic conditions, finances, income).
#
# Item text: NOT SHIPPED. Every stem is in the .sav's variable labels and
#   every option in its value labels (both levels complete, study-authored,
#   CC BY), but the labels are English while half the sample (Italy) was
#   administered in Italian, and the Italian wording is not in the deposit.
#   The UK half's wording is one hop away in this .sav.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CAPACCI_RAW", "journal.pone.0196020.s002.sav")
N_ROWS = 1001

TABLES = {
    "policy_support": ([f"q29_{i}" for i in range(1, 10)] + [f"q30_{i:02d}" for i in range(1, 12)],
                       range(1, 6), ()),
    "personal_risk": ([f"q23_{i}" for i in range(1, 7)], range(1, 8), (8,)),
    "societal_risk": ([f"q27_{i}" for i in range(1, 10)], range(1, 6), (6,)),
}
COVS = {"country": "cov_country", "type": "cov_mode", "q01": "cov_gender", "r_age": "cov_age",
        "q06": "cov_marital_status", "edu_int": "cov_education", "q03": "cov_self_rated_health"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 125 and txt == []
    vl = meta.variable_value_labels
    assert df["uniq_id"].is_unique
    df["id"] = df["uniq_id"].astype(int)
    for src, dst in COVS.items():
        df[dst] = df[src] if src == "r_age" else df[src].map(vl[src])
        assert df[dst].notna().sum() == df[src].notna().sum(), src
    df["cov_mode"] = df["cov_mode"].str.replace(" (Short)", "", regex=False)
    cov_cols = list(COVS.values())
    names, total = [], 0
    for suffix, (items, scale, na_codes) in TABLES.items():
        long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
        long = long[long["resp"].notna() & ~long["resp"].isin(na_codes)]
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(scale), (suffix, set(long["resp"]))
        long = long[["id", "item", "resp"] + cov_cols]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(scale) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {suffix} {c.name}: {c.detail[:160]}")
        name = f"capacci_2018_{suffix}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    shipped = {c for items, _, _ in TABLES.values() for c in items} | set(COVS) | {"uniq_id"}
    print(f"total responses {total}; {len(set(meta.column_names) - shipped)} source columns not "
          "carried (see header)")


if __name__ == "__main__":
    convert()
