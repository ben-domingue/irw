"""Three Peruvian-sample instruments: MEIM-R, self-esteem and SDO.

Source: Apaza Arapa, M. A. & Turpo Chaparro, J. E. (2026), Zenodo
10.5281/zenodo.22117910, CC BY 4.0 -- study data for "Psychometric properties
of the Multigroup Ethnic Identity Measure-Revised". 356 respondents.

Three instruments, three tables -- three different response formats, so
pooling them would put 1-4, 1-5 and 1-7 responses in one `resp` column:

  apaza_2026_meim_r        6 items  (Id_Exp1-3 exploration, Id_Com1-3 commitment), 1-5
  apaza_2026_self_esteem  10 items  (Auto1-5, Auto_r6-10), 1-4
  apaza_2026_sdo          14 items  (SDO_Dom1-7, SDO_Opos_r1-7), 1-7

The `_r` in a column name marks a reverse-keyed item. The suffix is kept in
the item code rather than stripped, so the keying stays visible in the item
set; the values themselves are the raw responses, not recodes -- the reversed
and non-reversed items share the same observed range in each instrument.
"""
import os
import re

import pandas as pd
import requests

RECORD = 22117910
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {
    "apaza_2026_meim_r": (r"^Id_(Exp|Com)\d+$", 6, (1, 5)),
    "apaza_2026_self_esteem": (r"^Auto(_r)?\d+$", 10, (1, 4)),
    "apaza_2026_sdo": (r"^SDO_(Dom|Opos_r)\d+$", 14, (1, 7)),
}
COVARIATES = {"Sexo": "cov_sex", "Edad": "cov_age",
              "Tipo_Univ": "cov_university_type",
              "Procedencia": "cov_origin"}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"]
             if x["key"].lower().endswith((".xlsx", ".xls", ".csv")))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    p = fetch_raw(path)
    df = pd.read_csv(p) if p.lower().endswith(".csv") else pd.read_excel(p)

    item_cols = {}
    for table, (pat, n, _rng) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    accounted = set(sum(item_cols.values(), [])) | set(COVARIATES) | {"ID"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (_pat, n, (lo, hi)) in SCALES.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=item_cols[table],
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == n, table
        assert long["resp"].between(lo, hi).all(), f"{table}: expected {lo}-{hi}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
