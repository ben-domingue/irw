#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0281119
# DOI: 10.1371/journal.pone.0281119
# Paper: Wang, Y., Zhao, R., Yan, Z., Wang, M., Pan, Y., & Wu, R. (2023). A
#   comparative study of environmental responsibility behavior in ecotourism
#   from the perceptions of residents and tourists: a case of Qilian Mountains
#   National Park in China. PLOS ONE 18(2): e0281119.
# Data: journal.pone.0281119.s001 (S1 File, residents, 335 rows x 23 cols) AND
#   .s002 (S2 File, tourists, 541 rows x 23 cols).
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 876 valid questionnaires collected around Qilian Mountains National Park,
# January-February 2022.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# THREE output tables, 20 distinct items, 15,768 responses, zero missing cells
# among the items each group was asked.
#
# THE TRAP IN THIS DEPOSIT, AND THE REASON TO READ THIS HEADER: the two files
# number their items 1..18 each, and FIVE OF THOSE NUMBERS MEAN DIFFERENT
# ITEMS IN THE TWO FILES. The resident questionnaire and the tourist
# questionnaire overlap on 16 items but each carries two the other does not,
# and because the extra items sit in the middle of the tourist form the
# numbering slips:
#     resident 12 == tourist 14   "Tourists protect the ecological environment
#                                  during the tour"
#     resident 13 == tourist 15, resident 14 == tourist 16,
#     resident 15 == tourist 17, resident 16 == tourist 18
#     resident-only: 17 "Tourists will participate in environmental protection
#       activities in ecological scenic spots", 18 "The uncivilized behavior of
#       tourists will seriously affect the ecological environment"
#     tourist-only: 12 "Residents will take the initiative to clean up the
#       garbage in the ecological scenic area", 13 "Residents will discourage or
#       stop tourists from non-environmentally friendly behavior"
# A merge on the item NUMBER -- the obvious thing to do with two files of
# identical shape -- would silently pool five pairs of different questions and
# would be invisible to every range, count and missingness check afterwards.
# So items are keyed by their WORDING, which the deposit puts in the column
# headers, and the script ASSERTS the five slips and the two-and-two
# exclusives so the join fails loudly if a corrected deposit ever changes them.
#
# PLANNED MISSINGNESS BY GROUP, not item nonresponse. Every respondent
# answered every item on their own form, and the four group-specific items are
# absent for the other group by design. Stated here because a reader seeing
# per-item n of 335 or 541 inside an 876-respondent table should not read it
# as attrition. Same shape as bock_2021's rotated booklets earlier in the
# batch, asserted rather than assumed.
#
# THREE TABLES, SPLIT BY TARGET, WHICH THE WORDING ITSELF STATES:
#   wang_2023_eco_perception      7 items, both groups -- perceptions of
#     ecotourism's effects and of the park's protection, development, policy
#     and law
#   wang_2023_eco_resident_erb    6 items -- residents' environmentally
#     responsible behaviour (4 asked of both groups, 2 of tourists only)
#   wang_2023_eco_tourist_erb     7 items -- tourists' environmentally
#     responsible behaviour (5 asked of both groups, 2 of residents only)
# The paper's own finer split -- it describes separate sections for overall
# ecotourism perception, policy perception and park perception -- is in Table
# 1, which is published only as an image, and its item codes (A3, C1-C3, TD1,
# QD1 ...) do not correspond to the deposit's numbers at all. So the
# seven perception items are kept as one table rather than divided on a guess,
# and that limit is stated in the description.
#
# `id` IS PREFIXED BY GROUP. Both files number respondents from 1, so a bare
# `No.` would collide 335 times. ids ship as R1..R335 and T1..T541, with the
# group also kept as cov_respondent_type.
#
# THE SCALE DIRECTION IS NOT CONFIRMED. The article never states the number of
# points or the anchors; its interpretation bands ("1 < mean < 2.5 is low ...
# 3.5 < mean <= 5 is high") imply 1-5 and the observed range is exactly 1-5.
# resp ships as deposited, and the description says the direction is
# unconfirmed -- the same treatment as li_2024_vr_* in this batch.
#
# COVARIATES: age and education ship as ordered band indices; gender (1/2) and
# occupation (7 nominal codes) are dropped, because Table 4 is an image and the
# article's text gives no percentages to pin any of them against.
#
# Item text: SHIPPED for all 20 items, read off the column headers. See
# wang_2023_ecotourism_itemtext.py.
#
# PII: screened over all 46 columns of the two files. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_R = os.environ.get("WANGECO_RES", "journal.pone.0281119_S1_File.xlsx")
RAW_T = os.environ.get("WANGECO_TOU", "journal.pone.0281119_S2_File.xlsx")

N_RES, N_TOU = 335, 541
LO, HI = 1, 5

COVS = {"Age": "cov_age_band", "Educational level": "cov_education_band"}
DROP = {"Gender:": "1/2 with no published percentages to pin which is which",
        "Occupational ": "7 nominal occupation codes, no legend anywhere"}

# the five number collisions the join must survive -- asserted, not trusted
KNOWN_SLIPS = {12: 14, 13: 15, 14: 16, 15: 17, 16: 18}   # resident -> tourist
RES_ONLY = ["Tourists will participate in environmental protection activities "
            "in ecological scenic spots",
            "The uncivilized behavior of tourists will seriously affect the "
            "ecological environment"]
TOU_ONLY = ["Residents will take the initiative to clean up the garbage in "
            "the ecological scenic area",
            "Residents will discourage or stop tourists from "
            "non-environmentally friendly behavior"]

# target -> (table, code prefix); membership is read off the wording
TABLES = [("wang_2023_eco_perception", "ECO",
           "Perception of the ecotourism environment and its governance"),
          ("wang_2023_eco_resident_erb", "RES",
           "Residents' environmentally responsible behaviour"),
          ("wang_2023_eco_tourist_erb", "TOU",
           "Tourists' environmentally responsible behaviour")]


def item_columns(df):
    """number -> (column, wording). The wording is the real identity."""
    out = {}
    for c in df.columns:
        m = re.match(r"^\s*(\d+)\s*\.\s*(.+)$", str(c))
        if m:
            out[int(m.group(1))] = (c, re.sub(r"\s+", " ", m.group(2)).strip())
    return out


def target_of(text):
    """Which table an item belongs to, from its own wording."""
    t = text.lower()
    if t.startswith("tourists "):
        return "TOU"
    if t.startswith("residents ") or t.startswith("some residents"):
        return "RES"
    if "uncivilized behavior of tourists" in t:
        return "TOU"
    if "uncivilized behavior of residents" in t:
        return "RES"
    return "ECO"


def load():
    res, tou = pd.read_excel(RAW_R), pd.read_excel(RAW_T)
    assert (len(res), len(tou)) == (N_RES, N_TOU), (len(res), len(tou))
    for df, nm in ((res, "residents"), (tou, "tourists")):
        strings = [c for c in df.columns
                   if pd.api.types.is_string_dtype(df[c])]
        assert not strings, f"{nm}: unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns across both files "
          f"({len(res.columns) + len(tou.columns)} columns)")

    ir, it = item_columns(res), item_columns(tou)
    assert len(ir) == 18 and len(it) == 18, (len(ir), len(it))
    tr = {text: n for n, (_, text) in ir.items()}
    tt = {text: n for n, (_, text) in it.items()}

    # the trap, asserted
    slips = {n: tt[text] for n, (_, text) in ir.items()
             if text in tt and tt[text] != n}
    assert slips == KNOWN_SLIPS, (
        f"the resident->tourist number slips are now {slips}, not "
        f"{KNOWN_SLIPS}; the two files key the SAME wording to DIFFERENT "
        f"numbers, so stop and re-derive before joining")
    assert sorted(set(tr) - set(tt)) == sorted(RES_ONLY), \
        sorted(set(tr) - set(tt))
    assert sorted(set(tt) - set(tr)) == sorted(TOU_ONLY), \
        sorted(set(tt) - set(tr))
    print(f"item-number slips asserted: resident {sorted(KNOWN_SLIPS)} are "
          f"tourist {[KNOWN_SLIPS[k] for k in sorted(KNOWN_SLIPS)]} -- a merge "
          f"on the NUMBER would pool five pairs of different questions")
    print(f"  {len(set(tr) & set(tt))} items shared, 2 resident-only, "
          f"2 tourist-only; {len(set(tr) | set(tt))} distinct items")
    return res, tou, ir, it


def code_map(ir, it):
    """Stable item codes from the wording, numbered within target."""
    texts = []
    for n in sorted(ir):
        texts.append(ir[n][1])
    for n in sorted(it):
        if it[n][1] not in texts:
            texts.append(it[n][1])
    counters, codes = {}, {}
    for text in texts:
        tgt = target_of(text)
        counters[tgt] = counters.get(tgt, 0) + 1
        codes[text] = f"{tgt}{counters[tgt]:02d}"
    return codes, counters


def long_frame(df, items, codes, group, prefix):
    cols = {col: codes[text] for _, (col, text) in items.items()}
    d = df.rename(columns={**cols, **COVS})
    d["id"] = prefix + d["No."].astype(int).astype(str)
    assert d["id"].nunique() == len(d), f"{group}: No. is not unique"
    d["cov_respondent_type"] = group
    keep = ["id", "cov_respondent_type"] + sorted(COVS.values())
    long = d.melt(id_vars=keep, value_vars=list(cols.values()),
                  var_name="item", value_name="resp")
    assert long["resp"].notna().all(), f"{group}: a missing item response"
    return long


def convert():
    res, tou, ir, it = load()
    codes, counters = code_map(ir, it)
    assert counters == {"ECO": 7, "RES": 6, "TOU": 7}, counters

    for df, nm in ((res, "residents"), (tou, "tourists")):
        accounted = {"No."} | set(COVS) | set(DROP) | \
            {col for col, _ in (v for v in (ir if nm == "residents"
                                            else it).values())}
        left_out = [c for c in df.columns if c not in accounted]
        assert not left_out, f"{nm}: unaccounted source columns: {left_out}"
    print("dropped 2 covariates: " +
          "; ".join(f"{k.strip()} ({v})" for k, v in DROP.items()))

    long = pd.concat([long_frame(res, ir, codes, "resident", "R"),
                      long_frame(tou, it, codes, "tourist", "T")],
                     ignore_index=True)
    long["resp"] = long["resp"].astype(int)
    assert long["resp"].between(LO, HI).all(), sorted(long["resp"].unique())
    assert long["id"].nunique() == N_RES + N_TOU
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, prefix, label in TABLES:
        sub = long[long["item"].str.startswith(prefix)].reset_index(drop=True)
        n_items = sub["item"].nunique()
        assert n_items == counters[prefix], (name, n_items)
        # planned missingness: a group either answered an item or never saw it
        per = sub.pivot_table(index="item", columns="cov_respondent_type",
                              values="resp", aggfunc="count").fillna(0)
        for grp, n in (("resident", N_RES), ("tourist", N_TOU)):
            if grp in per:
                bad = per[grp][(per[grp] != 0) & (per[grp] != n)]
                assert bad.empty, (
                    f"{name}: {grp} answered {bad.to_dict()} -- not all-or-"
                    f"nothing, so this is item nonresponse, not the planned "
                    f"group design the description claims")
        assert len(name) <= 40, name
        sub = sub[["id", "item", "resp", "cov_respondent_type"] +
                  sorted(COVS.values())]

        checks = run_qc(sub, permitted_values={i: list(range(LO, HI + 1))
                                               for i in sub["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        sub.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(sub)
        shape = {g: int(v) for g, v in
                 sub.groupby("cov_respondent_type")["item"].nunique().items()}
        print(f"{name}: rows={len(sub)} ids={sub['id'].nunique()} "
              f"items={n_items} (asked: {shape}) "
              f"resp={sub['resp'].min()}-{sub['resp'].max()}  [{label}]")

    assert total == 15768, total
    print(f"3 tables, {total} responses, 20 distinct items, "
          f"{N_RES + N_TOU} respondents in two groups")


if __name__ == "__main__":
    convert()
