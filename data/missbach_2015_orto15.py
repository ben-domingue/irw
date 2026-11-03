#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0135772
# DOI: 10.1371/journal.pone.0135772
# Paper: Missbach, B., Hinterbuchinger, B., Dreiseitl, V., Zellhofer, S.,
#   Kurz, C., & Koenig, J. (2015). When eating right, is measured wrong! A
#   validation and critical examination of the ORTO-15 questionnaire in
#   German. PLOS ONE 10(8): e0135772.
# Data: figshare 10.6084/m9.figshare.1451279 ("PLoS_dataset", Missbach),
#   file dataset_PLoS.sav, 1,029 German-speaking adults (online survey).
# License: CC BY 4.0, verified on the DEPOSIT (api.figshare.com/v2/articles/
#   1451279: license "CC BY 4.0"); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, missbach_2015_orto15: Ortho1..Ortho15, the German
# ORTO-15 (Donini et al. 2005), 1 "immer" (always), 2 "oft" (often),
# 3 "manchmal" (sometimes), 4 "nie" (never) -- the .sav's own value labels.
# As deposited: ORTO-15's scoring assigns 1 or 4 to the orthorexic answer
# item by item; nothing is re-keyed here.
#
# Covariates: sex (value labels), age, BMI (the deposit's own derived
# column), and three diet flags (vegan, vegetarian, mixed; 0 nein / 1 ja).
# Dropped: height and weight (BMI carries them; height holds a 1078 cm
# entry error), maximum_weight / minimum_weight (-66 sentinels, lifetime
# recall, not needed).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. Both label levels are complete in the .sav (German
#   stems as variable labels; immer/oft/manchmal/nie as value labels), but
#   the ORTO-15 is a named third-party instrument (Donini, Marsili, Graziani,
#   Imbriale & Cannella 2005) with no grant in the register -- HELD
#   2026-11-02, register row written.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("MISSBACH_RAW", "dataset_PLoS.sav")
NAME = "missbach_2015_orto15"
N_ROWS = 1029


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 25 and txt == []
    vl = meta.variable_value_labels
    items = [f"Ortho{i}" for i in range(1, 16)]
    assert all(vl[c] == {1.0: "immer", 2.0: "oft", 3.0: "manchmal", 4.0: "nie"} for c in items)
    df["id"] = range(1, N_ROWS + 1)
    df["cov_sex"] = df["sex"].map(vl["sex"])
    df["cov_age"] = df["age"]
    df["cov_bmi"] = df["bmi"].round(2)
    for c in ["vegan_diet", "vegetarian_diet", "mixed_diet"]:
        df["cov_" + c] = df[c]
    cov_cols = ["cov_sex", "cov_age", "cov_bmi", "cov_vegan_diet", "cov_vegetarian_diet", "cov_mixed_diet"]
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    accounted = set(items) | {"sex", "age", "bmi", "vegan_diet", "vegetarian_diet", "mixed_diet",
                              "height", "weight", "maximum_weight", "minimum_weight"}
    assert set(meta.column_names) == accounted
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; "
          "dropped height, weight, maximum_weight, minimum_weight")


if __name__ == "__main__":
    convert()
