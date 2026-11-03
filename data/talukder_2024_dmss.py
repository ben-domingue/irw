#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0315009
# DOI: 10.1371/journal.pone.0315009
# Paper: Talukder MS, Islam QT, Karim Z, et al. (2024). Facilitators and
#   inhibitors of attitude and word-of-mouth intention toward adoption of
#   digital municipal service systems: A stimulus-organism-response approach.
#   PLOS ONE 19(12): e0315009.
# Data: S1 Data (journal.pone.0315009.s003, "Dataset_PLOS ONE"), 353 citizens
#   of Bangladesh. The questionnaire is S1 Questionnaire (.s004); its item codes
#   match the sheet's column names.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# TEN output tables, one per construct whose codes match the questionnaire
# one-for-one, every item 1-7 agreement ("Please rate the degree to which you
# agree with the following statement"; inhibitor items UB/RB/TB are negatively
# worded by design and kept as answered):
#   talukder_2024_dmss_quality_value      QV1-4   quality value
#   talukder_2024_dmss_social_value       SV1-3
#   talukder_2024_dmss_epistemic_value    EPV1-3
#   talukder_2024_dmss_conditional_value  CV1-3
#   talukder_2024_dmss_convenience_value  COV1-3
#   talukder_2024_dmss_inclusion_value    INV1-3
#   talukder_2024_dmss_usage_barrier      UB1-4
#   talukder_2024_dmss_risk_barrier       RB1-3
#   talukder_2024_dmss_tradition_barrier  TB1-4
#   talukder_2024_dmss_word_of_mouth      WOM1-3
# NOT SHIPPED: ATT1-4 and IB1-2. The questionnaire has three ATT items and
#   four UI (use intention) items and no IB block, while the sheet has four ATT
#   columns, two IB columns and no UI -- the codes cannot be tied to wording.
# Covariates: gender, age band, education -- decoded from S2 Appendix
#   (journal.pone.0315009.s002), whose frequencies match the codes exactly:
#   gender 1 male (189) / 2 female (164); age 1 18-25 (117), 2 26-35 (108),
#   3 36-45 (111), 4 46-55 (15), 5 56+ (2); education 1 high school (25),
#   2 bachelor's (205), 3 master's (123). (The printed questionnaire lists
#   Female first and different age bands; the appendix counts are what the
#   codes reproduce.)
# `id` is the row index.
#
# Item text: NOT SHIPPED. English stems for the shipped codes are in S1
#   Questionnaire (journal.pone.0315009.s004) and S1 Appendix (.s001); not
#   attempted because the administration language in Bangladesh is not stated
#   and the items are adapted from published value/barrier scales with no
#   rights reading yet. Column codes only in the sheet (no labels).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("TALUKDER_RAW", "journal.pone.0315009.s003.xlsx")
BLOCKS = {
    "quality_value": ("QV", 4), "social_value": ("SV", 3), "epistemic_value": ("EPV", 3),
    "conditional_value": ("CV", 3), "convenience_value": ("COV", 3), "inclusion_value": ("INV", 3),
    "usage_barrier": ("UB", 4), "risk_barrier": ("RB", 3), "tradition_barrier": ("TB", 4),
    "word_of_mouth": ("WOM", 3),
}
NOT_SHIPPED = ["ATT1", "ATT2", "ATT3", "ATT4", "IB1", "IB2"]
AGE = {1: "18-25", 2: "26-35", 3: "36-45", 4: "46-55", 5: "56+"}
EDU = {1: "high school", 2: "bachelor's degree", 3: "master's degree"}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (353, 42), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    df["id"] = range(1, len(df) + 1)
    assert df["Gender"].value_counts().to_dict() == {1: 189, 2: 164}
    assert df["Education level"].value_counts().to_dict() == {2: 205, 3: 123, 1: 25}
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_age_band"] = df["Age"].map(AGE)
    df["cov_education"] = df["Education level"].map(EDU)
    covs = ["cov_gender", "cov_age_band", "cov_education"]
    assert df[covs].notna().all().all()
    used = {"Gender", "Age", "Education level"} | set(NOT_SHIPPED)
    names, total = [], 0
    for block, (pfx, k) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(range(1, 8))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"talukder_2024_dmss_{block}"
        names.append(name)
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert len(set(names)) == len(names)
    assert used | {"id"} | set(covs) == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; not shipped: {NOT_SHIPPED}")


if __name__ == "__main__":
    convert()
