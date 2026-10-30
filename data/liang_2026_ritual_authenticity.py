#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0358987
# DOI: 10.1371/journal.pone.0358987
# Paper: Liang, W., & Song, H. (2026). Ritualized experiences and perceived
#   authenticity in shaping tourists' willingness to support intangible
#   cultural heritage inheritance. PLOS ONE 21(9): e0358987.
# Data: figshare 10.6084/m9.figshare.33150737, one .xlsx, 390 rows x 36 cols.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on figshare. api.figshare.com/v2/articles/33150737 reports
# CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, 27 items, 10,530 responses, zero missing cells. The
# paper: seven points, 1 "strongly disagree" to 7 "strongly agree". 390
# tourists interviewed on site after a Shehuo performance in Yongdeng County,
# Tongwei County and Tianshui, 18 November 2025 - 8 January 2026.
#
# THE EIGHT DERIVED COLUMNS CONFIRM THE EIGHT BLOCKS. Alongside the 27 item
# columns the deposit carries eight bare-named columns -- unq, com, cer, nf,
# oa, ca, ea, ii -- and each is its own block's mean ROUNDED TO TWO DECIMALS,
# which the script asserts before dropping them. Rounding is why a naive
# equality test fails on five of the eight: the 3-item blocks produce thirds
# (3.33, 3.67) that only match once the comparison is rounded too. Worth
# recording, because "the derived column is not the mean" is the wrong
# conclusion to draw from that.
#
# SEVEN PREFIXES ARE THE PAPER'S OWN ABBREVIATIONS AND ONE IS INFERRED.
# Uniqueness (4), commitment (3), ceremoniality (4) and non-functionality (3)
# are the paper's four ritualized-experience dimensions; objective (3),
# constructive (3) and existential (3) authenticity are its three authenticity
# dimensions. Those seven match prefix for prefix and count for count. `ii` is
# NOT a transparent abbreviation of "willingness to support ICH inheritance",
# but it is the only remaining block and the only remaining construct, and its
# 4 items match -- so the identification is by exhaustion, and said so rather
# than presented as the paper's own label.
#
# `id` is the deposit's `id`, verified unique over all 390 rows. The deposit
# carries no covariates: the article's Table 1 demographics are not in the
# file.
#
# Item text: NOT SHIPPED. The article prints no wording and attributes the
# scales to Yan et al. (ritualized experience), Park et al. and others
# (authenticity) and Ruan et al. (willingness), translated and back-translated
# by these authors. Third-party instruments with no published wording.
#
# PII: screened over all 36 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LIANG_RAW", "figshare_33150737.xlsx")

N_ROWS = 390
LO, HI = 1, 7

CONSTRUCTS = {
    "unq": ("liang_2026_ich_uniqueness", 4, "Uniqueness (ritualized experience)"),
    "com": ("liang_2026_ich_commitment", 3, "Commitment (ritualized experience)"),
    "cer": ("liang_2026_ich_ceremoniality", 4,
            "Ceremoniality (ritualized experience)"),
    "nf": ("liang_2026_ich_non_functionality", 3,
           "Non-functionality (ritualized experience)"),
    "oa": ("liang_2026_ich_objective_auth", 3, "Objective authenticity"),
    "ca": ("liang_2026_ich_constructive_auth", 3, "Constructive authenticity"),
    "ea": ("liang_2026_ich_existential_auth", 3, "Existential authenticity"),
    "ii": ("liang_2026_ich_willingness", 4,
           "Willingness to support ICH inheritance (prefix identified by "
           "exhaustion, not by the paper)"),
}


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    blocks = {}
    for c in df.columns:
        m = re.fullmatch(r"([a-z]+)(\d+)", str(c).strip())
        if m:
            blocks.setdefault(m.group(1), []).append(str(c))
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"block counts are {got}, expected {want}"

    # each bare-named column is its block's mean ROUNDED TO 2dp -- the
    # rounding is why a plain equality test fails on the 3-item blocks
    derived = []
    for prefix, cols in blocks.items():
        assert prefix in df.columns, f"no derived column for {prefix}"
        m = df[sorted(cols)].mean(axis=1)
        assert (m.round(2) == df[prefix].round(2)).all(), (
            f"the `{prefix}` column is no longer the 2dp mean of {sorted(cols)} "
            f"-- the block membership rests on it, so stop")
        derived.append(prefix)
    print(f"all {len(derived)} bare-named columns reproduce as their own "
          f"block's mean rounded to 2 decimals, which confirms the block "
          f"membership; dropped")

    accounted = {"id"} | set(derived) | {c for v in blocks.values() for c in v}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert df["id"].nunique() == len(df), "id is not unique"

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"], value_vars=cols, var_name="item",
                       value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"]]

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
              f"[{label[:46]}]")

    assert total == 27 * N_ROWS, total
    print(f"8 tables, {total} responses (27 items x {N_ROWS} tourists)")


if __name__ == "__main__":
    convert()
