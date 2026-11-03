#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0277062
# DOI: 10.1371/journal.pone.0277062
# Paper: Schoultz M, McGrogan C, Beattie M, et al. (2022). Uptake and effects of
#   psychological first aid training for healthcare workers' wellbeing in
#   nursing homes: A UK national survey. PLOS ONE 17(11): e0277062.
# Data: OSF node tnr83 ("Quantitative Data"), file "Survey Data_final.savMS.sav",
#   388 staff of UK care, nursing and residential homes, online survey.
# License: CC0 1.0, verified on the DEPOSIT (api.osf.io/v2/nodes/tnr83: public,
#   license 563c1cf88c5e4a3877f9e96c = "CC0 1.0 Universal"); the article is
#   CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# PII screen: 9 text columns, all "If you selected Other, please specify"
#   follow-ups (regions, a training description, ethnicity, partner status,
#   transport). None holds a name, email or identifier; all are dropped.
#   The region columns Q7_a..Q7_d (and their _i free text) are geographic
#   codes and are dropped under the 2026-10-20 ruling.
#
# ONE output table, schoultz_2022_pfa_wellbeing: the five Psychological First
# Aid element items (PFA_Safe, PFA_Calm, PFA_Hopeful, PFA_Connected,
# PFA_Accomplished; "In the last month, I have felt safe" etc.), 1 never ..
# 5 very often (the .sav's own value labels).
#
# NOT SHIPPED, both on coding defects in the deposit:
#   PSS14_1..14 (Perceived Stress Scale-14). Value labels run 1 never .. 5
#     very often, but not one of 5,117 responses is a 5, and the deposit's
#     PSS_14 total is the raw sum with no reverse-keying. "Very often" never
#     chosen on fourteen stress items by 388 care workers mid-pandemic reads
#     as a lost code, not as data. (PSS is also registered `block`.)
#   CSE_1..26 (Coping Self-Efficacy Scale, 0-10). Coded 1..11, but codes 6
#     (the labelled midpoint) and 11 (the labelled top) never occur in 8,301
#     responses while every other code does, so the stored codes cannot be
#     mapped back to the 11-point scale the paper describes.
# Covariates: UK nation (Country; coarse, kept), age group, gender, ethnicity,
#   education (all value labels), and PFA training completed (PFA_Group;
#   self-selected, not randomised).
# Dropped: the five consent items, Carehome_Type (constant), region codes and
#   all free-text follow-ups, Q8, Marital_Status, the Health/Q14_*,
#   Domestic_Care/Q15_*, Childcare, Q17, Job_Title_*, Q19_*, Q20 multi-response
#   indicators, and the two derived totals.
# `id` is the row index (the deposit has no id column).
#
# Item text: SHIPPED (data_labels + study_materials) for all five items, to
#   automated_finding/itemtext_output/schoultz_2022_pfa_wellbeing__items.csv:
#   stems are the .sav variable labels, anchors the value labels (both levels
#   present on every item). instrument: stems searched verbatim, match no
#   published scale -- the five PFA elements (safety, calm, hope,
#   connectedness, efficacy) written as items by the authors; rights:
#   study-authored under the deposit's CC0.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
ITEMTEXT_DIR = os.path.join(REPO_ROOT, "automated_finding", "itemtext_output")
RAW = os.environ.get("SCHOULTZ_RAW", "Survey Data_final.savMS.sav")
NAME = "schoultz_2022_pfa_wellbeing"
ITEMS = ["PFA_Safe", "PFA_Calm", "PFA_Hopeful", "PFA_Connected", "PFA_Accomplished"]
COVMAP = {"Country": "cov_uk_nation", "Age": "cov_age_group", "Gender": "cov_gender", "Ethnicity": "cov_ethnicity",
          "Education": "cov_education", "PFA_Group": "cov_pfa_training_completed"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (388, 95), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and len(txt) == 9 and all(c.endswith(("_i", "_a")) for c in txt)
    vl, lab = meta.variable_value_labels, meta.column_names_to_labels
    # the two coding defects that keep PSS-14 and the CSE out
    pss = pd.concat([df[f"PSS14_{i}"] for i in range(1, 15)]).dropna()
    cse = pd.concat([df[f"CSE_{i}"] for i in range(1, 27)]).dropna()
    assert (pss == 5).sum() == 0 and set(cse) == {1, 2, 3, 4, 5, 7, 8, 9, 10}
    df["id"] = range(1, len(df) + 1)
    covs = []
    for src, cov in COVMAP.items():
        df[cov] = df[src].map(vl[src])
        assert df[cov].notna().sum() == df[src].notna().sum(), src
        covs.append(cov)
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    not_shipped = [c for c in df.columns if c not in ITEMS and c not in COVMAP and c != "id" and c not in covs]
    assert set(ITEMS) | set(COVMAP) | set(not_shipped) | {"id"} | set(covs) == set(df.columns)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; "
          f"{len(not_shipped)} columns not shipped")

    # item text, from the .sav's own labels (no positional step: item = column name)
    rows = []
    for it in ITEMS:
        assert vl[it] == {1.0: "Never", 2.0: "Almost Never", 3.0: "Sometimes", 4.0: "Fairly Often",
                          5.0: "Very Often"}, vl[it]
        for code, opt in vl[it].items():
            rows.append({"table": NAME, "section_id": f"{NAME}_1", "item": it,
                         "instrument": "Psychological First Aid element items (Schoultz et al. 2022)",
                         "instructions": None, "section_prompt": None, "item_text": lab[it],
                         "correct_response": None, "option_text": opt, "resp": int(code)})
    os.makedirs(ITEMTEXT_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(os.path.join(ITEMTEXT_DIR, NAME + "__items.csv"), index=False)
    print(f"{NAME}__items: {len(rows)} rows")


if __name__ == "__main__":
    convert()
