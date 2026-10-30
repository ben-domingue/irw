#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0292459
# DOI: 10.1371/journal.pone.0292459
# Paper: Robles-Marinos, R., Alvarado, G. F., Maguina, J. L., &
#   Bazo-Alvarez, J. C. (2023). The short-form of the Cyberchondria Severity
#   Scale (CSS-12): adaptation and validation of the Spanish version in young
#   Peruvian students. PLOS ONE 18(10): e0292459.
# Data: Zenodo "CSS-12 Dataset Peru", concept DOI 10.5281/zenodo.7066850,
#   version 10.5281/zenodo.7066851 -- S4_Base1.xlsx, 657 rows x 42 columns.
# License: CC BY 4.0, verified on the Zenodo deposit itself, which reports
#   license {"id": "cc-by-4.0"} and access_right "open". The data is hosted
#   off-site, so the article's own CC BY does not reach it and was not relied
#   on. (Note the record id: the concept DOI 7066850 resolves to record 7066851
#   -- query api/records/7066850 and you get the version record back, which is
#   the one carrying the licence.)
# 657 second- to sixth-year medical students at a private Peruvian university.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# TWO output tables, 30 items, 19,710 responses, zero missing cells.
#
# THE DEPOSIT IS A WALL OF `v1`..`v41` WITH NO CODEBOOK, and the article's
# Table 1 is published only as an image. So nothing here is taken on trust:
# every column that ships was pinned against a number the deposit or the paper
# publishes, and every column that could not be was dropped.
#
# THE FOUR DERIVED TOTALS ARE WHAT IDENTIFY THE BLOCKS. v38..v41 are sums, and
# matching each against every candidate block resolves the whole file at once:
#   v38 == sum(v8..v25)   on 657/657 rows -> SHAI total, 18 items
#   v39 == sum(v8..v21)   on 657/657      -> SHAI illness-likelihood, 14 items
#   v40 == sum(v22..v25)  on 657/657      -> SHAI negative-consequences, 4
#   v41 == sum(v26..v37)  on 657/657      -> CSS-12 total, 12 items
# These agree with the article item for item: "Short Health Anxiety Inventory
# (SHAI): 18 items in two sections, 14 on perceived likelihood of illness and
# 4 on negative consequences, each scored 0-3" and "CSS-12: 12 items".
# All four totals are DROPPED -- they are derived, not responses.
#
# NOTE WHAT THIS DOES AND DOES NOT PROVE. A sum is invariant to permuting its
# terms, so the reconstruction pins BLOCK MEMBERSHIP exactly (which columns are
# the SHAI, which are the CSS-12, and which 14/4 split the SHAI's two sections)
# and says NOTHING about the order of items within a block. That is why the
# items keep the deposit's own v-numbers rather than being renamed CSS12_01..12:
# renaming would assert an order nothing here establishes. Also why no item
# text ships -- see below.
#
# v7 LOOKS LIKE A SHAI ITEM AND IS NOT. It sits immediately before the SHAI
# block and shares its 0-3 range, which is exactly how an off-by-one block
# boundary happens. The totals rule it out: the SHAI total is sum(v8..v25), not
# sum(v7..v25). Its correlations agree -- v7 against the 14-item subtotal is
# -0.09 while genuine SHAI items run 0.4-0.5. So v7 is some other 4-level
# variable, unidentifiable without a codebook, and is dropped.
#
# TWO COVARIATES SHIP, FIVE DO NOT, and the two that do were each pinned
# against a published statistic rather than guessed:
#   v2 -> cov_age. Observed mean 21.32, SD 2.24 against the paper's "mean age
#     was 21.3 years (SD = 2.2)". Range 18-37.
#   v1 -> cov_sex. 396 of the 657 take the value 0, and the paper reports
#     "396 (60.3%) were women", so 0 = woman and 1 = man. Asserted at 396 so
#     the mapping fails loudly if the file ever changes.
#   v3, v4, v5, v6, v7 are DROPPED. Each is a small-integer code whose meaning
#     appears only in the article's Table 1, which is an image. Their marginals
#     (419/216/22; 172/133/187/73/92; 173/484; 187/470; 19/123/273/242) match
#     no statistic in the readable text, so there is nothing to pin them to. A
#     covariate whose direction and categories are unknown is worse than no
#     covariate -- the same rule applied to diop_2019's GENDER and to
#     lin_2024_escooter's columns named `1`..`9` earlier in this batch.
#
# THE CSS-12 SHIPS 0-4 AND THE PAPER SAYS 1-5. The deposit is zero-indexed:
# v26..v37 run 0-4 and their sum reproduces v41 exactly, so 0-4 is the coding
# the deposit's own total was built on and is what ships. The published
# anchors are "never (1)" to "always (5)", so deposited code = published code
# minus one, and the published 12-60 total range corresponds to the deposit's
# 0-48. Said in the table description rather than silently re-based: re-basing
# would break agreement with the deposit's own total column.
#
# THE TEST-RETEST FILE IS NOT SHIPPED. S5_Base2.xlsx is 60 rows -- 30
# participants measured twice, seven days apart -- and its five value columns
# are the four CSS-12 domain scores plus the total, not item responses. Two
# independent reasons to withhold it: it holds no items, and 30 respondents is
# far below the 100-id floor.
#
# Item text: NOT SHIPPED, and the blocker is mapping rather than rights. The
# authors' own Spanish CSS-12 is published as the article's S2 File under its
# CC BY licence, so the wording is distributable. But nothing ties a printed
# item to a specific v-column: the only route the deposit offers is the total,
# which is permutation-invariant. Registered as the CSS-12 family with the
# reason recorded, so whoever revisits it does not re-derive the rights
# question when the real blocker is a key.
#
# PII: screened over all 42 columns. Every one is numeric; the finest-grained
# variable is age in years, which is not a date of birth.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ROBLES_RAW", "S4_Base1.xlsx")

N_ROWS = 657
N_WOMEN = 396          # paper: "396 (60.3%) were women"
AGE_MEAN, AGE_SD = 21.3, 2.2

def v(a, b):
    return [f"v{i}" for i in range(a, b)]

SHAI = v(8, 26)        # 18 items, 0-3
SHAI_LIKELIHOOD = v(8, 22)   # 14
SHAI_CONSEQUENCE = v(22, 26)  # 4
CSS = v(26, 38)        # 12 items, 0-4
TOTALS = {"v38": SHAI, "v39": SHAI_LIKELIHOOD, "v40": SHAI_CONSEQUENCE,
          "v41": CSS}
DROP_OPAQUE = ["v3", "v4", "v5", "v6", "v7"]

TABLES = [
    ("robles_marinos_2023_shai18", SHAI, 0, 3,
     "Short Health Anxiety Inventory, 18 items"),
    ("robles_marinos_2023_css12", CSS, 0, 4,
     "Cyberchondria Severity Scale short form (CSS-12), Spanish version"),
]


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}")
    assert not strings, f"unexpected string column(s) -- screen them: {strings}"
    print("  every column is numeric; the finest-grained variable is age in "
          "years (v2), which is not a date of birth. No names, emails, dates, "
          "free text or geography")


def identify_blocks(df):
    """The derived totals are what identify the blocks -- see the header."""
    for total, cols in TOTALS.items():
        agree = (df[cols].sum(axis=1) == df[total]).mean()
        assert agree == 1.0, (
            f"{total} no longer equals sum({cols[0]}..{cols[-1]}) on every row "
            f"({agree:.1%}); the block identification in the header rests on "
            f"this, so stop and re-derive rather than shipping")
        print(f"  {total} == sum({cols[0]}..{cols[-1]}) on all {len(df)} rows "
              f"({len(cols)} items)")
    # v7 is NOT a SHAI item: the total excludes it, and it does not behave
    # like one either
    r = df["v7"].corr(df["v39"])
    rs = [df[c].corr(df["v39"]) for c in SHAI_LIKELIHOOD]
    assert abs(r) < min(abs(x) for x in rs), (
        f"v7 now correlates {r:.2f} with the 14-item subtotal, inside the "
        f"range of genuine items -- recheck the block boundary")
    print(f"  v7 excluded from the SHAI: r={r:.2f} with the 14-item subtotal "
          f"against {min(rs):.2f}-{max(rs):.2f} for the items themselves")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)
    identify_blocks(df)

    accounted = set(["id", "v1", "v2"]) | set(DROP_OPAQUE) | set(TOTALS)
    for _, cols, *_ in TABLES:
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    # the two covariates that a published statistic pins
    assert round(df["v2"].mean(), 1) == AGE_MEAN and \
        round(df["v2"].std(), 1) == AGE_SD, (
            f"v2 is mean {df['v2'].mean():.2f} SD {df['v2'].std():.2f}, no "
            f"longer the paper's {AGE_MEAN} ({AGE_SD}) -- do not ship it as age")
    assert int((df["v1"] == 0).sum()) == N_WOMEN, (
        f"{int((df['v1'] == 0).sum())} rows have v1=0, not the paper's "
        f"{N_WOMEN} women -- the sex coding is no longer pinned")
    print(f"cov_age: mean {df['v2'].mean():.2f} SD {df['v2'].std():.2f} "
          f"(paper: {AGE_MEAN}, {AGE_SD}); cov_sex: {N_WOMEN} rows at 0 = the "
          f"paper's 396 women, so 0=woman 1=man")
    print(f"dropped {len(DROP_OPAQUE)} opaque covariates ({', '.join(DROP_OPAQUE)}) "
          f"and {len(TOTALS)} derived totals ({', '.join(TOTALS)})")

    assert df["id"].nunique() == len(df), "id is not unique"
    df = df.rename(columns={"v1": "cov_sex", "v2": "cov_age"})
    cov_cols = ["cov_age", "cov_sex"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols, lo, hi, label in TABLES:
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "a non-numeric response")
        assert vals.between(lo, hi).all(), (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()
        assert len(long) == len(cols) * N_ROWS, (name, len(long))
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:145]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 30 * N_ROWS, total
    print(f"2 tables, {total} responses (30 items x {N_ROWS} respondents). "
          f"S5_Base2.xlsx not shipped: 30 participants, domain scores not items")


if __name__ == "__main__":
    convert()
