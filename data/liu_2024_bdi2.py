#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/27211653
# DOI: 10.6084/m9.figshare.27211653.v1 (data; no paper DOI on the record)
#   Liu, L., Jia, H., Qiu, B., et al. (2024). "The Relationship Between
#   Mindfulness and Depression: Examining the Chain Mediating Role of Shyness
#   and Core Self-evaluation" [dataset]. figshare.
# Data: one .sav, 646 Chinese college students; columns A1-A21 (BDI-II-C),
#   B1-B13 (Revised Cheek and Buss Shyness Scale), c1-c10 (CSES), d1-d39
#   (FFMQ), plus sums. No SPSS labels; the instruments are named in the
#   figshare description, which also says reverse-keyed items were already
#   recoded.
# License: CC BY 4.0 (figshare record).
# Codebook: none (instrument list in the record description only).
#
# Item text: not shipped -- codes only; BDI-II is a licensed instrument.
#
# Tables (one per instrument):
#   liu_2024_bdi2, A1-A21, 0-3. The deposit's `depression` column is
#     asserted equal to the item sum (so it includes the bad cells below).
#     A21 holds value(s) above 3 on a 0-3 item -- a data-entry error isolated
#     to one item; those cells are dropped.
#   liu_2024_rcbs, B1-B13 (Revised Cheek and Buss Shyness Scale), 1-5; the
#     item sum equals `shyness`. One B12 = 6 and one B13 = 0 are isolated
#     out-of-range cells and are dropped.
#   liu_2024_cses, c1-c10 (Core Self-Evaluations Scale), 1-5; the item sum
#     equals `CE`.
#   liu_2024_ffmq, the 39 FFMQ items (d1..d39; the deposit names items 35
#     and 39 d35_1 and d39_1, kept as named), 1-5; the facet sums equal the
#     deposit's five facet totals. 70 cells hold the item's column mean
#     (one non-integer value per column, e.g. 2.765672 on d10): mean
#     imputation, so those cells are dropped. One d33 = 8 is dropped as an
#     isolated out-of-range cell.
# Reverse keying: the figshare description says reverse-keyed items were
#   already recoded before deposit, and which ones is not recorded. The
#   RCBS, CSES and FFMQ ship as deposited; check direction before scoring.
#   Every RCBS and CSES item correlates positively with the rest of its
#   scale; in the FFMQ several items correlate near zero or negatively with
#   the rest of the 39 (d29 -0.31, d4 -0.16, d35_1 -0.09), so its
#   reversal state is mixed or unknown.
# Covariates: cov_age only (gender, residence etc. are unlabelled codes).
#   id = row index.

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/49748337"
TABLE = "liu_2024_bdi2"
ITEMS = [f"A{i}" for i in range(1, 22)]
ALLOWED = {0, 1, 2, 3}
FFMQ = ["d1", "d6", "d11", "d15", "d20", "d26", "d31", "d36",
        "d2", "d7", "d12", "d16", "d22", "d27", "d32", "d37",
        "d5", "d8", "d13", "d18", "d23", "d28", "d34", "d38",
        "d3", "d10", "d14", "d17", "d25", "d30", "d35_1", "d39_1",
        "d4", "d9", "d19", "d21", "d24", "d29", "d33"]
FFMQ_FACETS = {"观察总分": FFMQ[0:8], "描述总分": FFMQ[8:16], "觉知地行动总分": FFMQ[16:24],
               "不判断总分": FFMQ[24:32], "不行动总分": FFMQ[32:39]}
# (table, items, permitted values, the deposit's total column(s), items allowed to hold
#  isolated out-of-range cells)
OTHER = [("liu_2024_rcbs", [f"B{i}" for i in range(1, 14)], {1, 2, 3, 4, 5}, {"shyness": None}, {"B12", "B13"}),
         ("liu_2024_cses", [f"c{i}" for i in range(1, 11)], {1, 2, 3, 4, 5}, {"CE": None}, set()),
         ("liu_2024_ffmq", FFMQ, {1, 2, 3, 4, 5}, FFMQ_FACETS, {"d33"})]


def write(long, table, permitted, items):
    long = long[["id", "item", "resp", "cov_age"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: permitted for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {table}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        d, _ = pyreadstat.read_sav(tmp.name)
    assert d.shape == (646, 101), d.shape
    assert (d[ITEMS].sum(axis=1) == d["depression"]).all()
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["年龄"]
    long = d.melt(id_vars=["id", "cov_age"], value_vars=ITEMS,
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    bad = ~long["resp"].isin(ALLOWED)
    assert set(long.loc[bad, "item"]) <= {"A21"}, set(long.loc[bad, "item"])
    print(f"[drop] {int(bad.sum())} out-of-range A21 cells")
    long = long[~bad].copy()
    long["resp"] = long["resp"].astype(int)
    write(long, TABLE, ALLOWED, ITEMS)

    for table, items, permitted, totals, odd_ok in OTHER:
        for tot, cols in totals.items():
            cols = cols or items
            assert ((d[cols].sum(axis=1) - d[tot]).abs() < 1e-6).all(), (table, tot)
        long = d.melt(id_vars=["id", "cov_age"], value_vars=items,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        imputed = long["resp"] % 1 != 0
        if table == "liu_2024_ffmq":
            # mean imputation: each column's non-integer cells all hold one value, the column mean
            per_col = long[imputed].groupby("item")["resp"].apply(lambda v: v.round(6).nunique())
            assert (per_col == 1).all(), per_col
            print(f"[drop] {int(imputed.sum())} mean-imputed FFMQ cells")
        else:
            assert not imputed.any(), table
        long = long[~imputed].copy()
        bad = ~long["resp"].isin(permitted)
        assert set(long.loc[bad, "item"]) <= odd_ok, (table, set(long.loc[bad, "item"]))
        assert bad.sum() <= len(odd_ok), (table, int(bad.sum()))
        print(f"[drop] {table}: {int(bad.sum())} isolated out-of-range cells")
        long = long[~bad].copy()
        long["resp"] = long["resp"].astype(int)
        write(long, table, permitted, items)

if __name__ == "__main__":
    main()
