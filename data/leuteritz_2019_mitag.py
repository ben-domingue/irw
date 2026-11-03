#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0224485
# DOI: 10.1371/journal.pone.0224485
# Paper: Leuteritz J-P, Navarro J, Berger R (2019). Validation of the group
#   tasks uncertainty model (MITAG) in a German sample. PLOS ONE 14(11):
#   e0224485.
# Data: S1 File (journal.pone.0224485.s002, sample 1, 501 team members) and S2
#   File (journal.pone.0224485.s003, sample 2, 104 team leaders), .sav, staff
#   of a German research organisation, online survey.
# License: CC BY 4.0 (the article; the data is its Supporting Information).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 3, BATCH_LOG.md).
#
# Three output tables, the deposit's own item codes throughout. Every item is
# AS ADMINISTERED: codes ending _nr carry "[n.r.]" in their label and are the
# reverse-keyed items, stored unreversed (MITAG_3_nr correlates -.54 with its
# mirror MITAG_9).
#   leuteritz_2019_mitag     MITAG_1..MITAG_18, the German MITAG (task
#       uncertainty: multiplicity, ambiguity, instability, ...). 1 gar nicht,
#       2 eher nicht, 3 teilweise, 4 weitgehend, 5 vollkommen. BOTH samples:
#       members (sample 1) and leaders (sample 2) answered the identical 18
#       items on the identical scale, so they are one table with
#       cov_role = member / leader; leaders' ids are offset past the members'.
#   leuteritz_2019_afa_wma   AFA_WMA_1..3, knowledge of work methods, members
#       only. 1 Stimme ueberhaupt nicht zu .. 7 Stimme voellig zu.
#   leuteritz_2019_jds       JDS_AUT_1..3 (autonomy) and JDS_FJ_1..3 (feedback
#       from the job), German Job Diagnostic Survey, members only, 1-7. Items
#       _1 are behaviourally anchored (1 very little .. 7 very much); items _2
#       and _3 run 1 Voellig unzutreffend .. 7 Stimmt voellig.
# cluster_id = the team (u_teamident); 80 of the 104 leaders' teams also
#   appear among the members.
# Covariates: gender (value labels), task type (value labels, German), role.
# Dropped: lfdn (a running number; `id` is a row index).
#
# Item text: NOT SHIPPED. Both label levels are complete in the .sav (German
#   stems as variable labels, anchors as value labels), and S1 Appendix
#   (journal.pone.0224485.s001) gives the MITAG in English, German and Spanish.
#   Not shipped on rights: the MITAG is the authors' German adaptation of a
#   Spanish instrument (Navarro et al.), the aguilar_latorre_2022 shape (an
#   openly licensed adaptation of an original whose terms are unestablished),
#   and AFA/JDS are third-party -- HELD 2026-11-02, register rows written.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW1 = os.environ.get("LEUTERITZ_RAW1", "journal.pone.0224485.s002.sav")
RAW2 = os.environ.get("LEUTERITZ_RAW2", "journal.pone.0224485.s003.sav")
MITAG = [f"MITAG_{i}{'_nr' if i in (2, 3, 6, 10, 11, 13, 15, 17, 18) else ''}" for i in range(1, 19)]
AFA = [f"AFA_WMA_{i}" for i in range(1, 4)]
JDS = ["JDS_AUT_1", "JDS_AUT_2", "JDS_AUT_3_nr", "JDS_FJ_1", "JDS_FJ_2", "JDS_FJ_3_nr"]


def emit(name, df, items, cov_cols, permitted):
    long = df[["id", "cluster_id"] + cov_cols + items].melt(id_vars=["id", "cluster_id"] + cov_cols,
                                                            var_name="item", value_name="resp")
    long = long[long["resp"].notna()]
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted)
    long = long[["id", "item", "resp", "cluster_id"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    return name


def load(path, role, n, ncol):
    df, meta = pyreadstat.read_sav(path)
    assert df.shape == (n, ncol)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen ({role}): {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert txt == ["u_teamident"]
    assert df["u_teamident"].str.fullmatch(r"[A-Z][0-9]+(-[0-9A-Z])?").all()
    vl = meta.variable_value_labels
    df["cov_gender"] = df["u_gender"].map(vl["u_gender"])
    df["cov_task_type"] = df["u_tasktype"].map(vl["u_tasktype"])
    df["cov_role"] = role
    df["cluster_id"] = df["u_teamident"]
    return df, meta


def convert():
    m, mm = load(RAW1, "member", 501, 31)
    lead, lm = load(RAW2, "leader", 104, 22)
    assert set(mm.column_names) == set(MITAG + AFA + JDS) | {"u_gender", "u_teamident", "u_tasktype", "lfdn"}
    assert set(lm.column_names) == set(MITAG) | {"u_gender", "u_teamident", "u_tasktype", "lfdn"}
    m["id"] = range(1, len(m) + 1)
    lead["id"] = range(len(m) + 1, len(m) + len(lead) + 1)
    cov_cols = ["cov_gender", "cov_task_type", "cov_role"]
    both = pd.concat([m, lead], ignore_index=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    names = [emit("leuteritz_2019_mitag", both, MITAG, cov_cols, [1, 2, 3, 4, 5]),
             emit("leuteritz_2019_afa_wma", m, AFA, cov_cols, list(range(1, 8))),
             emit("leuteritz_2019_jds", m, JDS, cov_cols, list(range(1, 8)))]
    assert len(set(names)) == len(names)
    print("dropped: lfdn (running number)")


if __name__ == "__main__":
    convert()
