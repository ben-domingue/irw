#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210161
# DOI: 10.1371/journal.pone.0210161
# Paper: Drain, P. K., Hong, T., Hajat, A., Krows, M., Govere, S., Thulare, H.,
#   Moosa, M.-Y. S., Bassett, I., & Celum, C. (2019). Integrating hypertension
#   screening at the time of voluntary HIV testing among adults in South
#   Africa. PLOS ONE 14(2): e0210161.
# Data: journal.pone.0210161.s001 (S1 Data, "A dataset for the study cohort",
#   .xlsx), 5,618 adults presenting for voluntary HIV testing at an ambulatory
#   clinic in KwaZulu-Natal, South Africa (baseline questionnaire administered
#   before HIV testing).
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# THREE output tables, the three instruments the Methods name:
#   drain_2019_gad7   gad_1..7   GAD-7
#   drain_2019_phq9   phq_1..9   PHQ-9
#   drain_2019_hfias  food_1..9  HFIAS occurrence questions, 0 = no, 1 = yes
#
# GAD-7 / PHQ-9 CODING -- SHIPPED AS DEPOSITED, 1-4, AND THE SCALE RUNS
# BACKWARDS: 4 = "not at all", 1 = the most frequent option ("nearly every
# day"). Higher resp = FEWER symptoms. ben-domingue, 2026-11-02, in-session:
# "you can leave it in original form" (the first build had shipped 4 - code).
# The deposit codes both 1-4 with no labels; the direction is inferred, and the
# evidence is: on the paper's analytic sample (the 5,428 with a blood-pressure
# reading), sum(4 - code) >= 15 on the PHQ-9 gives 6.08%, against the paper's
# "6.2% had moderate or severe depression (PHQ-9 >= 15)"; the forward reading
# (code - 1) gives 92.7%. 4 is also the modal code on every item (31,338 of
# 37,940 GAD cells), as "not at all" is in a general clinic population.
# Caveat, stated in the description: the paper's "26.6% had anxiety (GAD-7 >=
# 10)" does not reproduce under EITHER reading (7.3% reversed, 93.4% forward),
# so the GAD direction rests on the PHQ match, the shared layout and the modal
# code. To score on the instruments' 0-3 scale, use 4 - resp.
#
# HFIAS. Each of the nine occurrence questions (food_N, 0/1) has a frequency
# follow-up (food_Na, 1-3) asked only when the answer was yes; the crosstab
# confirms the skip on 5,612 of 5,618 rows per item. Only the occurrence
# items are shipped: the frequency codes carry no labels in the deposit and
# the paper does not state their direction, so the standard HFIAS 0-3 item
# score cannot be built without guessing which end is "often".
#
# Covariates: age, sex (1 = female: 2,681 of 5,428 = 49.4% in the analytic
# sample, exactly the paper's "2,681 (49.4%) were female") and HIV test
# result (0/1, 35.1% positive in the paper; 1,905 of 5,428 here).
#
# Not shipped: travel, the nine food_Na follow-ups, employment, income,
# education, children, marital status (unlabelled codes, no codebook); the
# eight substance-use frequency items (cigarettes .. ecstasy, 1-4, no labels
# and no named instrument); blood pressure, anthropometrics, pulse, glucose,
# pregnancy, CD4, follow-up time (clinical measurements).
#
# `id` is the row index; `anonymized_id` (unique) is not used.
#
# Item text: NOT SHIPPED. No stems or labels anywhere in the deposit (both
#   are a bare .xlsx with column names only); GAD-7/PHQ-9 are registered
#   `ship` and HFIAS is the FANTA public indicator guide, but nothing here
#   records the isiZulu/English wording actually administered.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DRAIN_RAW", "journal.pone.0210161.s001.xlsx")
N_ROWS = 5618

BLOCKS = {
    "drain_2019_gad7": ([f"gad_{i}" for i in range(1, 8)], "as_deposited", 1, 4),
    "drain_2019_phq9": ([f"phq_{i}" for i in range(1, 10)], "as_deposited", 1, 4),
    "drain_2019_hfias": ([f"food_{i}" for i in range(1, 10)], None, 0, 1),
}


def convert():
    df = pd.read_excel(RAW).copy()
    assert len(df) == N_ROWS and df["anonymized_id"].is_unique
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 69 and txt == ["glucose"]
    assert pd.to_numeric(df["glucose"].dropna(), errors="coerce").notna().mean() > 0.95  # lab values

    analytic = df["systolic_ra"].notna()
    assert analytic.sum() == 5428
    assert int((df.loc[analytic, "sex"] == 1).sum()) == 2681
    phq = df.loc[analytic, BLOCKS["drain_2019_phq9"][0]]
    assert abs(((4 - phq).sum(axis=1) >= 15).mean() - 0.062) < 0.005
    for i in range(1, 10):   # frequency follow-up asked only after a yes
        assert ((df[f"food_{i}"] == 1) == df[f"food_{i}a"].notna()).mean() > 0.998

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_age": df["age"],
        "cov_sex": df["sex"].map({1: "female", 2: "male"}),
        "cov_hiv_positive": df["hiv_status"].astype(int),
    })
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    used, total = set(), 0
    for name, (cols, recode, lo, hi) in BLOCKS.items():
        used |= set(cols)
        wide = df[["id"] + cols].copy()
        if recode == "as_deposited":   # 1-4, 4 = "not at all"; NOT reversed (see header)
            assert set(wide[cols].stack().dropna().unique()) == {1, 2, 3, 4}
        long = wide.melt(id_vars=["id"], value_vars=cols, var_name="item",
                         value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) == set(range(lo, hi + 1)), name
        long = long.merge(cov, on="id", how="left")[["id", "item", "resp"] + cov_cols]
        assert long["item"].nunique() == len(cols) and not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(lo, hi + 1)) for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={len(cols)} resp={lo}-{hi}")

    cov_src = {"age", "sex", "hiv_status"}
    dropped = [c for c in df.columns if c not in used | cov_src | {"id"}]
    print(f"{len(used)} item columns shipped; dropped {len(dropped)}: {dropped}")
    assert len(dropped) == 69 - 25 - 3
    print(f"TOTAL responses: {total}")


if __name__ == "__main__":
    convert()
