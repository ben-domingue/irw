#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264357
# DOI: 10.1371/journal.pone.0264357
# Paper: Nurnberger P, von Lewinski D, Rothenhausler H-B, Braun C, Reinbacher P,
#   Kolesnik E, et al. (2022). A biopsychosocial model of severe fear of
#   COVID-19. PLoS ONE 17(2): e0264357.
# Data: PLOS Supporting Information S1 File (journal.pone.0264357.s002,
#   "CoronastudieDatenPlos", SPSS .sav), an online survey of adults in Austria.
#   422 rows, of which 48 hold no item responses at all and are dropped,
#   leaving 374. No fractional values in any item cell.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# NINE output tables, item codes the deposit's own (the first item of each
# block carries the instrument name as a suffix, e.g. BAI1_becksanxietyinventory;
# it is shortened to BAI1 and so on):
#   nurnberger_2022_bai               Beck Anxiety Inventory, BAI1-21, 0-3
#   nurnberger_2022_who5              WHO-5 Well-being Index, WHO1-5, 0-5
#   nurnberger_2022_ias               Illness Attitude Scales, 28 items as
#                                     deposited (IAS19, 24 and 28 are not in the
#                                     file), 0-4; IAS23 holds 0/1 only
#   nurnberger_2022_spq_fear          Specific Phobia Questionnaire, fear
#                                     ratings: the ODD columns SPQ1, SPQ3, ...,
#                                     SPQ99, 0-4
#   nurnberger_2022_spq_interference  SPQ interference ratings: the EVEN columns
#                                     SPQ2, ..., SPQ100, 0-4
#     The deposit stores the SPQ as 100 columns: 50 stimuli, each rated for fear
#     and for interference in adjacent columns (adjacent-pair correlation 0.79
#     against about 0.22 otherwise). Which is which is fixed by the deposit's
#     own composites: spq_vomiting_fear is exactly the mean of SPQ33 and SPQ49,
#     and spq_vomiting_influence exactly the mean of SPQ34 and SPQ50.
#   nurnberger_2022_sss               Social Support Survey (MOS), SSS1-18, 1-5
#   nurnberger_2022_stai_state        STAI state anxiety, STAI1-20, 1-4
#   nurnberger_2022_stai_trait        STAI trait anxiety, STAI21-40, 1-4
#   nurnberger_2022_whiteley          Whiteley Index, WI1-14, 0/1
#   All stored as deposited; no reverse-keyed item is recoded.
# Covariates: gender (value labels), age.
# Dropped: SSS19 (free text, a short "other" answer); the remaining
#   demographic, social-media, job and somatic-risk single items (bare codes
#   with no value labels); every derived total, group and subscale column
#   (BAI_total, who_total, ias_*, spq_*, sss_total, staig_*, wi_*, covid_*,
#   tabelle_*).
# `id` is the row index of the 374 kept rows (the deposit has no id column).
#
# Item text: NOT SHIPPED. No variable labels on any item and no value labels
#   on any item (both levels checked); all nine are published instruments.

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0264357.s002&type=supplementary"
RAW = os.environ.get("NURNBERGER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=300)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        src = os.path.join(OUT_DIR, "_nurnberger_tmp.sav")
        open(src, "wb").write(r.content)
    df, meta = pyreadstat.read_sav(src)
    if not RAW:
        os.remove(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (422, 310), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["SSS19"]
    df = df.rename(columns={c: re.sub(r"^([A-Z]+\d+)_.*$", r"\1", c) for c in df.columns
                            if re.match(r"^(BAI|WHO|IAS|SPQ|SSS|STAI|WI)1_", c)})
    blk = lambda p: [c for c in df.columns if re.fullmatch(p + r"\d+", c) and c != "SSS19"]
    spq = blk("SPQ")
    assert spq == [f"SPQ{i}" for i in range(1, 101)]
    # the composites fix the parity: odd = fear, even = interference
    assert (df[["SPQ33", "SPQ49"]].mean(axis=1) - df["spq_vomiting_fear"]).abs().max() < 1e-9
    assert (df[["SPQ34", "SPQ50"]].mean(axis=1) - df["spq_vomiting_influence"]).abs().max() < 1e-9
    stai = blk("STAI")
    assert stai == [f"STAI{i}" for i in range(1, 41)]
    tables = {
        "bai": (blk("BAI"), range(0, 4)), "who5": (blk("WHO"), range(0, 6)), "ias": (blk("IAS"), range(0, 5)),
        "spq_fear": (spq[0::2], range(0, 5)), "spq_interference": (spq[1::2], range(0, 5)),
        "sss": (blk("SSS"), range(1, 6)), "stai_state": (stai[:20], range(1, 5)),
        "stai_trait": (stai[20:], range(1, 5)), "whiteley": (blk("WI"), range(0, 2)),
    }
    assert [len(v[0]) for v in tables.values()] == [21, 5, 28, 50, 50, 18, 20, 20, 14]
    all_items = [c for v in tables.values() for c in v[0]]
    keep = df[all_items].notna().any(axis=1)
    assert (~keep).sum() == 48
    df = df[keep].reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_gender"] = df["gender"].map(meta.variable_value_labels["gender"])
    df["cov_age"] = df["age"]
    covs = ["cov_gender", "cov_age"]
    total = 0
    for key, (items, perm) in tables.items():
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), (key, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        out = f"nurnberger_2022_{key}"
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        total += len(long)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
