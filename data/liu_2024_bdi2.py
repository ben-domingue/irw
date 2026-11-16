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
# Table: liu_2024_bdi2, A1-A21, 0-3. The deposit's `depression` column is
#   asserted equal to the item sum (so it includes the bad cells below).
#   A21 holds value(s) above 3 on a 0-3 item -- a data-entry error isolated
#   to one item; those cells are dropped.
# Not shipped (memory: pre-scored reversals): the shyness scale and CSES, which
#   have reverse-keyed items stored already recoded with no record of which;
#   the FFMQ for the same reason, and it also carries mean-imputed
#   non-integer cells.
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
    long = long[["id", "item", "resp", "cov_age"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: ALLOWED for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
