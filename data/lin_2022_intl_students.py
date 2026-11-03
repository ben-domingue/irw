#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267081
# DOI: 10.1371/journal.pone.0267081
# Paper: Lin, C., Tong, Y., Bai, Y., Zhao, Z., Quan, W., Liu, Z., Wang, J.,
#   Song, Y., Tian, J., & Dong, W. (2022). Prevalence and correlates of
#   depression and anxiety among Chinese international students in US
#   colleges during the COVID-19 pandemic: A cross-sectional study. PLOS ONE
#   17(4): e0267081.
# Data: journal.pone.0267081.s002 (S1 Dataset, .xlsx), 1,881 Chinese
#   international students at US colleges, online snowball survey, 2020.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# THREE output tables (table names carry "cis" -- Chinese international
# students -- because lin_2022_* is already taken by an unrelated deposit):
#   lin_2022_cis_gad7  GAD1..7  0-3   deposit's GADtotal reproduces on 100% of rows
#   lin_2022_cis_phq9  PHQ1..9  0-3   deposit's PHQtotal reproduces on 100% of rows;
#                                     PHQ >= 10 gives 24.5%, the paper's figure
#   lin_2022_cis_isi   ISI11, ISI12, ISI13, ISI2..ISI5, 0-4: the 7-item Insomnia
#                      Severity Index (items 1a-1c then 2-5). The deposit's
#                      ISItotal is the sum of ISI2..ISI5 only (reproduces on
#                      100% of rows) -- a 4-item partial total, not shipped.
#
# Not shipped: the Social Support Rating Scale (SSRS1..11 with sub-items
# SSRS61-63): its items mix 1-4 ratings with SSRS7/SSRS8, which are COUNTS of
# support sources (0-9), and the paper uses an adapted 11-item version whose
# scoring is not given -- not one response format, not a clean battery. The
# self-constructed single questions (Tuition .. RemoteAcareer, helpseek,
# knowPSY, supportPSY) are one-off items, not a scale. All totals and cutoff
# flags are derived.
#
# Covariates: gender (2 = female: 905, exactly the paper's "female n = 905")
# and age. Edu Level, AoS, CurLocat, TraEvent are unlabelled codes and are
# dropped.
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Column names only, no labels or codebook in the
#   deposit; GAD-7/PHQ-9 are registered `ship` but the Chinese wording
#   administered is not here, and the ISI is registered `block`.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIN_RAW", "journal.pone.0267081.s002.xlsx")
N_ROWS = 1881

BLOCKS = {
    "lin_2022_cis_gad7": ([f"GAD{i}" for i in range(1, 8)], 0, 3),
    "lin_2022_cis_phq9": ([f"PHQ{i}" for i in range(1, 10)], 0, 3),
    "lin_2022_cis_isi": (["ISI11", "ISI12", "ISI13", "ISI2", "ISI3", "ISI4", "ISI5"], 0, 4),
}


def convert():
    df = pd.read_excel(RAW).copy()
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 62 and txt == []
    assert (df[BLOCKS["lin_2022_cis_gad7"][0]].sum(axis=1) == df["GADtotal"]).all()
    assert (df[BLOCKS["lin_2022_cis_phq9"][0]].sum(axis=1) == df["PHQtotal"]).all()
    assert (df[["ISI2", "ISI3", "ISI4", "ISI5"]].sum(axis=1) == df["ISItotal"]).all()
    assert int((df["Gender"] == 2).sum()) == 905
    assert int((df["PHQtotal"] >= 10).sum()) == 460

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({"id": df["id"], "cov_gender": df["Gender"].map({1: "male", 2: "female"}),
                        "cov_age": df["Age"]})
    cov_cols = ["cov_gender", "cov_age"]
    os.makedirs(OUT_DIR, exist_ok=True)
    assert len(set(BLOCKS)) == len(BLOCKS)
    used, total = set(), 0
    for name, (cols, lo, hi) in BLOCKS.items():
        used |= set(cols)
        long = df[["id"] + cols].melt(id_vars=["id"], var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), name
        long = long.merge(cov, on="id")[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS and not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(cols)} resp={lo}-{hi}")

    ssrs = [c for c in df.columns if c.startswith("SSRS") and c != "SSRStotal"]
    single = ["Tuition", "FamilyR", "PandemicFinance", "fSM_L", "fSM_F", "fActivity", "WorkLoad",
              "fRemote", "RemoteRelation", "RemoteAcareer", "helpseek", "knowPSY", "supportPSY"]
    derived = ["SSRStotal", "ISItotal", "GADtotal", "PHQtotal", "insominaClin", "GAD≧10", "PHQ≧10"]
    codes = ["Edu Level", "AoS", "CurLocat", "TraEvent"]
    accounted = used | set(ssrs) | set(single) | set(derived) | set(codes) | {"Gender", "Age", "id"}
    assert set(df.columns) == accounted, set(df.columns) ^ accounted
    print(f"not shipped: SSRS {len(ssrs)} cols, {len(single)} single items, {len(derived)} derived, "
          f"{len(codes)} unlabelled codes")
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
