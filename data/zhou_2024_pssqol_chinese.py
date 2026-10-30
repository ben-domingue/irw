#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0313839
# DOI: 10.1371/journal.pone.0313839
# Paper: Zhou, Y., Zhuang, L., He, X., Xu, L., He, Q., & Li, X. (2024).
#   Cross-cultural adaptation and validation of the Chinese version of the
#   PSS-QoL questionnaire. PLOS ONE 19(12): e0313839.
# Data: journal.pone.0313839.s002 (S2 File, .xls), six sheets.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 135 patients with primary Sjogren's syndrome.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables, 59 items, 7,964 responses, from a SIX-SHEET workbook of
# which three sheets are shipped and three are not:
#   PSS-QoL      135 patients -> TWO tables (see below)
#   SF-12        135 patients -> one table, 12 items
#   ESSPRI       135 patients -> one table, 3 items
#   Expert consultation   5 experts  -> NOT shipped, far below the 100-id floor
#   Baseline data1        15 patients -> NOT shipped, same reason
#   Retest data 2         15 patients -> NOT shipped, same reason
# The last two are the test-retest subsample and would have made a `wave`
# table between them, but 15 respondents is 15.
#
# THE PSS-QoL SHEET HOLDS TWO SCALES AND SHIPS AS TWO TABLES. Its items run
# 7 to 31 in one numbered sequence, but they are not one response format:
#   items 8 to 17.3 are THIRTY BINARY symptom-presence items (dry mouth, dry
#     eyes, dry skin, dry nose, vaginal dryness and their sub-symptoms), 0/1
#   items 18 to 31 are FOURTEEN impact statements on an 0-4 scale
# Putting a yes/no symptom and a five-point impact rating on one `resp` is
# exactly what the one-scale-per-file rule exists to prevent, so they are two
# tables. Item 7 ("How severe was your pain?", a 0-10 numeric rating) is a
# single item on a third scale and is NOT shipped: one item is not a table.
#
# ONE STRAY 3 ON A BINARY ITEM is dropped: column 13.2 ("Trouble speaking")
# holds a single 3 where every other value in all thirty symptom columns is
# 0 or 1. Asserted as exactly one cell, so a genuinely polytomous item would
# fail here rather than ship.
#
# THE SF-12'S ITEMS DO NOT SHARE A RESPONSE FORMAT, AND THAT IS THE
# INSTRUMENT, NOT A DEFECT. Items 2 and 3 run 1-3 (the physical-limitation
# pair) and the other ten run 1-5. The SF-12 is a single published
# instrument with deliberately heterogeneous options, so it ships as one
# table with per-item permitted values rather than being split -- splitting
# would invent two instruments where the literature has one.
#
# ESSPRI IS THREE 0-10 NUMERIC RATING SCALES (pain, fatigue, dryness), the
# EULAR Sjogren's Syndrome Patient Reported Index. Exactly at the three-item
# floor. The deposit misspells the first as "Pian"; it ships as `pain`.
#
# `id` is each sheet's `Number`, 1..135, verified unique and verified
# IDENTICAL ACROSS THE THREE SHIPPED SHEETS, so a user can join the four
# tables on `id` and get the same patient. Asserted.
#
# COVARIATES come from the PSS-QoL sheet and are carried onto all four
# tables: sex, occupation, marriage, education (integer codes with no legend
# anywhere in the readable article, so they ship as codes and the
# description says so) and disease duration in years, which is a genuine
# continuous covariate.
#
# Item text: SHIPPED for the two PSS-QoL tables and for ESSPRI, read off the
# column headers. NOT for the SF-12, which is QualityMetric's proprietary
# instrument -- the deposit calls its columns "Item 1".."Item 12" and carries
# no wording anyway.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHOU_RAW", "journal.pone.0313839_S2_File.xls")

N_ROWS = 135
COVS = {"2.Sex": "cov_sex", "3.Occupation": "cov_occupation",
        "4.Marriage": "cov_marriage", "5.Education": "cov_education",
        "6.Disease duration": "cov_disease_duration_years"}
PAIN_NRS = "7.How severe was your pain?"
SKIPPED_SHEETS = {"Expert consultation": 5, "Baseline data1": 15,
                  "Retest data 2": 15}
HEAD = re.compile(r"^(\d+(?:\.\d+)?)\.?(.*)$")


def item_code(header):
    """'13.2Burning sensation...' -> 'Q13_2'. The number is the deposit's."""
    m = HEAD.match(str(header).strip())
    assert m, header
    return "Q" + m.group(1).replace(".", "_")


def convert():
    x = pd.ExcelFile(RAW)
    for sheet, n in SKIPPED_SHEETS.items():
        assert len(x.parse(sheet)) == n, (sheet, len(x.parse(sheet)))
    print("not shipped: " + "; ".join(
        f"{s} ({n} respondents, far below the 100-id floor)"
        for s, n in SKIPPED_SHEETS.items()))

    p = x.parse("PSS-QoL")
    sf = x.parse("SF-12")
    es = x.parse("ESSPRI")
    for t, nm in ((p, "PSS-QoL"), (sf, "SF-12"), (es, "ESSPRI")):
        assert len(t) == N_ROWS, (nm, len(t))
        assert t["Number"].nunique() == N_ROWS, (nm, "Number is not unique")
        strings = [c for c in t.columns if pd.api.types.is_string_dtype(t[c])]
        assert not strings, (nm, strings)
    assert set(p["Number"]) == set(sf["Number"]) == set(es["Number"]), (
        "the three sheets no longer share one set of patient numbers, so the "
        "four output tables cannot be joined on `id`")
    print(f"PII screen: 0 string columns across the three shipped sheets; "
          f"`Number` is identical across all three, so the tables join on id")

    sym = [c for c in p.columns
           if HEAD.match(str(c)) and
           str(c) not in COVS and str(c) != PAIN_NRS and
           float(HEAD.match(str(c)).group(1)) < 18]
    imp = [c for c in p.columns
           if HEAD.match(str(c)) and
           str(c) not in COVS and
           float(HEAD.match(str(c)).group(1)) >= 18]
    assert len(sym) == 30 and len(imp) == 14, (len(sym), len(imp))
    left_out = [c for c in p.columns if c not in
                set(COVS) | set(sym) | set(imp) | {"Number", PAIN_NRS}]
    assert not left_out, f"unaccounted PSS-QoL columns: {left_out}"
    print(f"PSS-QoL splits into {len(sym)} binary symptom items and "
          f"{len(imp)} impact items on an 0-4 scale; item 7, a lone 0-10 pain "
          f"rating, is not shipped (one item is not a table)")

    stray = int((p[sym] > 1).sum().sum())
    assert stray == 1, (
        f"{stray} symptom cells exceed 1 on a binary battery, not the single "
        f"stray this script drops; if the items are polytomous, stop")
    p[sym] = p[sym].mask(p[sym] > 1)
    print("dropped 1 stray cell holding a 3 on a binary symptom item")

    cov_cols = sorted(COVS.values())
    covs = p[["Number"] + list(COVS)].rename(
        columns={"Number": "id", **COVS})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0

    def emit(name, frame, cols, ren, permitted, label):
        nonlocal total
        d = frame.rename(columns={"Number": "id", **ren})
        d = d.merge(covs, on="id", how="left")
        codes = list(ren.values())
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=codes,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == len(codes)
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]
        checks = run_qc(long, permitted_values=permitted)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:130]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={len(codes)} resp={long['resp'].min()}-"
              f"{long['resp'].max()}  [{label}]")

    ren_s = {c: item_code(c) for c in sym}
    emit("zhou_2024_pssqol_symptoms", p[["Number"] + sym], sym, ren_s,
         {v: [0, 1] for v in ren_s.values()},
         "PSS-QoL binary symptom-presence items")
    ren_i = {c: item_code(c) for c in imp}
    emit("zhou_2024_pssqol_impact", p[["Number"] + imp], imp, ren_i,
         {v: [0, 1, 2, 3, 4] for v in ren_i.values()},
         "PSS-QoL impact items, 0-4")
    sf_cols = [c for c in sf.columns if c != "Number"]
    ren_f = {c: "SF" + re.sub(r"\D", "", str(c)) for c in sf_cols}
    perm = {ren_f[c]: sorted(int(v) for v in sf[c].dropna().unique())
            for c in sf_cols}
    emit("zhou_2024_sf12", sf, sf_cols, ren_f, perm,
         "SF-12, per-item options as the instrument defines them")
    ren_e = {"Pian": "pain", "Fatigue": "fatigue", "Dryness": "dryness"}
    emit("zhou_2024_esspri", es, list(ren_e), ren_e,
         {v: list(range(0, 11)) for v in ren_e.values()},
         "ESSPRI, three 0-10 numeric rating scales")

    assert total == 30 * N_ROWS - 1 + 14 * N_ROWS + 12 * N_ROWS + 3 * N_ROWS, \
        total
    print(f"4 tables, {total} responses from {N_ROWS} patients with primary "
          f"Sjogren's syndrome")


if __name__ == "__main__":
    convert()
