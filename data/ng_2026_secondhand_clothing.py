#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0356518
# DOI: 10.1371/journal.pone.0356518
# Paper: Ng, S.-L. (2026). Determinants of secondhand clothing consumption in
#   Hong Kong: an extended Knowledge-Attitude-Practice (KAP) model.
#   PLOS ONE 21(9): e0356518.
# Data: Zenodo 10.5281/zenodo.20838473, "PLOS KAP NG.csv", 545 rows x 20 cols.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on Zenodo, which reports license {"id": "cc-by-4.0"} and
# access_right "open".
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables, 14 items, 7,628 responses. 545 Hong Kong respondents,
# online snowball sample in 2021, skewed young and lower-income. The paper:
# five points, 1 "strongly disagree" to 5 "strongly agree".
#
# THE CONSTRUCT NAMES ARE INFERRED AND SAID TO BE. The article never defines
# KW, AT, PS, SCP or BH. What it does give is its model -- an extended
# Knowledge-Attitude-Practice model with knowledge, attitude, practice, price
# consciousness and perceived risk -- and the prefixes line up with four of
# those five initial-for-initial. Perceived risk has no block in the deposit
# at all, so one of the paper's five constructs is simply absent from the
# data. The mapping ships as an inference, not as the paper's own label.
#
# PS IS MISSING ITS THIRD ITEM IN THE SOURCE: the columns are PS1, PS2, PS4.
# No PS3 exists anywhere in the file. Three items still clears the floor, and
# the gap is left visible in the item codes rather than renumbered -- PS4
# stays PS4.
#
# TWO CELLS OF PS2 HOLD A 6 ON A DOCUMENTED 5-POINT SCALE and are dropped as
# data-entry errors. Exactly two, asserted, so a genuinely 6-point block
# would fail here instead of quietly shipping. Same treatment as
# huang_2025_school_climate's single stray 5 earlier in this batch.
#
# `BH` IS NOT SHIPPED. It is a single column on its own 5-level scale and the
# article describes a purchase-frequency item whose anchors it does not
# state. One item is not a table, and folding a frequency item into an
# agreement battery would put two response formats on one `resp`.
#
# THREE COVARIATES SHIP LABELLED AND ONE PARTLY. Every published distribution
# was checked:
#   gender   214 / 331 = 39.3% / 60.7% against "female 60.8%, male 39.2%"
#            -> 1 male, 2 female
#   age      106/274/73/46/37/9 against 19.4/50.2/13.4/8.4/6.7/1.7 -- all six
#            exact -> 1 under 18, 2 18-22, 3 23-29, 4 30-39, 5 40-49,
#            6 50-59
#   income   304/165/63/8/5 against 55.8/30.1/11.7/1.5/0.9 -- all five exact
#            -> 1 under HK$10,000 rising to 5 HK$40,000-49,999
#   education partly: code 2 = 202 = 37.1% is the paper's "secondary" and
#            code 3 = 69 = 12.7% its "post-secondary (higher diploma or
#            associate degree)", both exact. Codes 4, 5 and 6 together are
#            the paper's single "college or higher" band, which it reports as
#            48.3% against their combined 50.3%, so the collapse is not
#            exact and the three degree levels are NOT individually labelled.
#            The column ships as an ordered band index with the two pinned
#            levels named in the description.
#
# `id` is the deposit's `SampleNo`, 1..545, verified unique.
#
# Item text: NOT SHIPPED. The deposit holds bare prefixes and the article's
# Table 1, which lists the constructs and their question items, is published
# only as an image.
#
# PII: screened over all 20 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NG_RAW", "PLOS KAP NG.csv")

N_ROWS = 545
LO, HI = 1, 5
N_STRAY = 2

CONSTRUCTS = {
    "KW": ("ng_2026_shc_knowledge", 4, "Knowledge (inferred from the prefix)"),
    "AT": ("ng_2026_shc_attitude", 4, "Attitude (inferred)"),
    "PS": ("ng_2026_shc_price_sensitivity", 3,
           "Price sensitivity / consciousness (inferred; PS3 absent from the "
           "source)"),
    "SCP": ("ng_2026_shc_purchase_practice", 3,
            "Secondhand clothing purchase practice (inferred)"),
}
COVS = {"Gender": "cov_gender", "Age": "cov_age_band",
        "Education": "cov_education_band", "Income": "cov_income_band"}
DROP = {"BH": "a single column on its own 5-level frequency scale -- one "
               "item is not a table and its anchors are unstated"}
PINNED = {"Gender": [214, 331], "Age": [106, 274, 73, 46, 37, 9],
          "Income": [304, 165, 63, 8, 5]}


def convert():
    df = pd.read_csv(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    blocks = {}
    for c in df.columns:
        m = re.fullmatch(r"([A-Z]+)(\d+)", str(c).strip())
        if m and m.group(1) in CONSTRUCTS:
            blocks.setdefault(m.group(1), []).append(str(c))
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"block counts are {got}, expected {want}"
    assert sorted(blocks["PS"]) == ["PS1", "PS2", "PS4"], sorted(blocks["PS"])
    print("PS is PS1, PS2, PS4 -- no PS3 exists anywhere in the file; the "
          "gap stays visible in the item codes rather than being renumbered")

    accounted = {"SampleNo"} | set(COVS) | set(DROP) | \
        {c for v in blocks.values() for c in v}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print("not shipped: " + "; ".join(f"{k} ({v})" for k, v in DROP.items()))

    for col, counts in PINNED.items():
        g = df[col].value_counts().sort_index().tolist()
        assert g == counts, (f"{col} is {g}, not the published {counts}")
    assert int((df["Education"] == 2).sum()) == 202 and \
        int((df["Education"] == 3).sum()) == 69, "education no longer pinned"
    print("covariates pinned: gender 2=female (60.7% vs 60.8%), all six age "
          "bands exact, all five income bands exact, education 2=secondary "
          "(37.1%) and 3=post-secondary (12.7%) exact -- codes 4-6 are the "
          "paper's single 'college or higher' band and are NOT individually "
          "labelled")

    stray = int((df["PS2"] == 6).sum())
    assert stray == N_STRAY, (
        f"PS2 holds {stray} values of 6 on a documented 5-point scale, not "
        f"the {N_STRAY} this script treats as data-entry errors; if the "
        f"block is genuinely 6-point, stop and re-derive")
    df["PS2"] = df["PS2"].mask(df["PS2"] == 6)
    print(f"dropped {stray} PS2 cells holding a 6 on a documented 5-point "
          f"scale, as data-entry errors")

    assert df["SampleNo"].nunique() == len(df), "SampleNo is not unique"
    df = df.rename(columns={"SampleNo": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
        stacked = df[cols].stack().dropna()
        vals = pd.to_numeric(stacked, errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:135]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={n} resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label[:44]}]")

    assert total == 14 * N_ROWS - N_STRAY, total
    print(f"4 tables, {total} responses (14 items x {N_ROWS} respondents, "
          f"less {N_STRAY} dropped stray cells)")


if __name__ == "__main__":
    convert()
