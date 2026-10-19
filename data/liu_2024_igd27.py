#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/25123145
# DOI: 10.6084/m9.figshare.25123145
#   Liu, S. (2024). Assessing the Diagnostic Precision of the Internet Gaming
#   Disorder Scale (IGD-27) Using Diagnostic Classification Models: An
#   Exploratory Study [Dataset]. figshare.
# Data: "dat_igd_27.csv" -- 8,662 Chinese college students answering a 27-item
#   dichotomous Internet Gaming Disorder pool, and "IGD_Q.csv", the study's own
#   27 x 9 Q-MATRIX mapping each item to the DSM-5 IGD criteria it measures.
# License: CC BY 4.0 (verified on the figshare record, 2026-10-19).
# Item text: NOT shipped. No wording is deposited at any level -- the response
#   file is 27 bare `ItemN` columns and the Q-matrix is 27 x 9 of 0/1 -- so
#   there is nothing to extract. Note also that the rights register blocks the
#   IGDS9-SF (9 items); this is a 27-item pool across the nine DSM-5 criteria
#   and its wording is not in the deposit either way.
#
#   THE REGISTER'S VERDICT DOES NOT STOP THIS TABLE, and that is worth stating
#   because this deposit sat deferred on exactly that worry. `irw_validate`'s
#   rights gate says it in as many words -- "Response data from this instrument
#   can ship; its wording cannot" -- and the 2026-10-18 ERQ withdrawal under
#   the scoped-use ruling removed ITEM TEXT tables from `irw_text_2`, not
#   response tables. A `block` is a wording verdict.
#
# ONE table, 8,662 respondents x 27 items, 0/1, complete (233,874 responses).
#
# THE Q-MATRIX SHIPS WITH IT, which is the point of this deposit: `qmatrix1`
#   through `qmatrix9` carry the deposit's own 27 x 9 matrix, joined to the
#   items BY ROW ORDER, because that is the only correspondence the deposit
#   provides -- IGD_Q.csv has no item column, 27 rows, and `Dim1`..`Dim9`
#   headers, and dat_igd_27.csv has Item1..Item27 in that order. The script
#   asserts both shapes before relying on it. Each attribute is one DSM-5 IGD
#   criterion; every item loads on exactly one, which the script also checks,
#   so the matrix is a clean single-attribute partition of the 27 items.
#
# id: the row index. The deposit carries no respondent id column.
# Covariates: none -- the file is items only, with no demographics at all.
import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "25123145" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE = 25123145
RESP_FILE, QMATRIX_FILE = "dat_igd_27.csv", "IGD_Q.csv"
N_ITEMS, N_ATTR, N_RESP = 27, 9, 8662
SCALE = {0, 1}
TABLE = "liu_2024_igd27"


def fetch(name: str) -> Path:
    p = RAW_DIR / name
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == name][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch(RESP_FILE))
    q = pd.read_csv(fetch(QMATRIX_FILE))
    items = [f"Item{i}" for i in range(1, N_ITEMS + 1)]
    assert list(df.columns) == items, list(df.columns)
    assert len(df) == N_RESP, len(df)
    assert not df.isna().any().any(), "the response file is complete"
    assert {v for c in items for v in df[c].unique()} <= SCALE

    # The Q-matrix joins by row order, and nothing else is on offer: assert
    # the shape this depends on rather than trusting it.
    assert list(q.columns) == [f"Dim{i}" for i in range(1, N_ATTR + 1)], list(q.columns)
    assert len(q) == N_ITEMS, len(q)
    assert q.isin([0, 1]).all().all()
    per_item = q.sum(axis=1)
    assert (per_item == 1).all(), \
        f"an item loads on other than one attribute: {per_item.tolist()}"
    per_attr = q.sum(axis=0)
    assert (per_attr == 3).all(), \
        f"the 27 items are not 3 per criterion: {per_attr.tolist()}"
    print(f"Q-matrix: {N_ITEMS} items x {N_ATTR} DSM-5 criteria, "
          f"{int(per_attr.iloc[0])} items per criterion, single-attribute")

    qmap = {item: row for item, row in zip(items, q.to_numpy())}
    df["id"] = range(1, len(df) + 1)
    t = (df[["id", *items]]
         .melt(id_vars=["id"], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    assert set(t["resp"]) <= SCALE
    for a in range(N_ATTR):
        t[f"qmatrix{a + 1}"] = t["item"].map(lambda i, a=a: int(qmap[i][a]))
    qcols = [f"qmatrix{a + 1}" for a in range(N_ATTR)]
    t = t[["id", "item", "resp", *qcols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == N_RESP and t["item"].nunique() == N_ITEMS
    assert len(t) == N_RESP * N_ITEMS
    # Every item's Q-matrix row is constant across respondents, by construction.
    assert (t.groupby("item")[qcols].nunique() == 1).all().all()

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()} "
          f"qmatrix cols={len(qcols)}")


if __name__ == "__main__":
    main()
