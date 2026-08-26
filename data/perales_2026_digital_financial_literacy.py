"""Perales Leonardo, Pérez Saldaña & Puicán Rodríguez (2026), figshare --
digital financial literacy and financial resilience among gastronomic
entrepreneurs in Chiclayo, Peru.

Source: https://doi.org/10.6084/m9.figshare.33312225.v1
DOI: 10.6084/m9.figshare.33312225
License: CC BY 4.0

179 restaurant owners rating two 12-item instruments on a 1-5 scale.

Tables written
--------------
perales_2026_digital_financial_literacy   179 x 12 items, 1-5
perales_2026_financial_resilience         179 x 12 items, 1-5

Coding notes
------------
* Two tables: the workbook labels the first block "IV. Digital Financial
  Literacy" and the second "DV. Financial Resilience" -- an independent and a
  dependent construct, not one scale.
* **The workbook has three header rows** -- construct, dimension, item code --
  above the data, and the item block is repeated after a demographics block
  with its own copy of the respondent code. All three are read explicitly;
  taking row 1 as the header (the default) yields `Unnamed: 9`-style columns
  and silently treats the two remaining header rows as respondents.
* The dimension row is forward-filled into `itemcov_dimension`: digital
  payments / digital budgeting / online risk assessment / comparison of
  financial products, and liquidity / adjustment capacity / operational
  continuity / recovery from losses -- three items each.
* `id` is the workbook's own respondent code (`E1`..`E179`); the demographics
  block and the item block carry it independently and they are asserted to
  agree row by row.
* `TOTAL` is the row sum over both blocks.
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

ARTICLE = 33312225
DOI = "10.6084/m9.figshare.33312225"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
COVS = ["Age", "Gender", "Educational level", "Business tenure",
        "Formality status"]
COV_NAMES = {"Age": "cov_age_band", "Gender": "cov_gender",
             "Educational level": "cov_education",
             "Business tenure": "cov_business_tenure",
             "Formality status": "cov_formality_status"}
BLOCKS = [("digital_financial_literacy", "IV. Digital Financial Literacy"),
          ("financial_resilience", "DV. Financial Resilience")]


def main():
    s = requests.Session()
    s.headers.update(UA)
    art = s.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                timeout=120).json()
    assert art["license"]["name"].startswith("CC BY"), art["license"]
    hit = [f for f in art["files"] if f["name"].lower().endswith(".xlsx")]
    assert len(hit) == 1, [f["name"] for f in art["files"]]
    raw = s.get(hit[0]["download_url"], timeout=600)
    raw.raise_for_status()
    book = pd.read_excel(io.BytesIO(raw.content), header=None)

    construct = book.iloc[0].ffill()
    dimension = book.iloc[1].ffill()
    code = book.iloc[2]
    body = book.iloc[3:].reset_index(drop=True)

    idcols = [j for j in body.columns
              if str(construct[j]) == "Gastronomic entrepreneurs"]
    assert len(idcols) == 2, idcols
    assert (body[idcols[0]] == body[idcols[1]]).all()
    ids = body[idcols[0]].astype(str)
    assert ids.is_unique and len(ids) == 179, (len(ids), ids.is_unique)

    # the raw dimension row, not the forward-filled one: the spacer column
    # after "Formality status" would otherwise inherit that name and win.
    raw_dim = book.iloc[1]
    covcols = {str(raw_dim[j]): j for j in body.columns
               if str(construct[j]) == "Control variables"
               and str(raw_dim[j]) in COVS}
    assert set(covcols) == set(COVS), covcols

    os.makedirs(OUTDIR, exist_ok=True)
    shipped, total = set(), 0
    for suffix, label in BLOCKS:
        cols = [j for j in body.columns if str(construct[j]) == label]
        assert len(cols) == 12, (suffix, len(cols))
        shipped.update(cols)

        frame = pd.DataFrame({"id": ids})
        for name, j in covcols.items():
            frame[COV_NAMES[name]] = body[j].values
        item_of, dim_of = {}, {}
        for j in cols:
            item_of[j] = str(code[j])
            dim_of[str(code[j])] = str(dimension[j])
            frame[str(code[j])] = body[j].values

        long = frame.melt(id_vars=["id"] + list(COV_NAMES.values()),
                          value_vars=list(dim_of), var_name="item",
                          value_name="resp")
        long["itemcov_dimension"] = long["item"].map(dim_of)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "itemcov_dimension"]
                    + list(COV_NAMES.values())]

        assert long["resp"].between(1, 5).all()
        assert not long.duplicated(["id", "item"]).any()
        assert long.groupby("item")["resp"].nunique().min() > 1
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (suffix, [(c.name, c.detail) for c in bad])

        name = f"perales_2026_{suffix}"
        path = os.path.join(OUTDIR, f"{name}.csv")
        assert not os.path.exists(path), name
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        total += len(long)
        print(f"{path}: {n_id} entrepreneurs x {n_it} items = {len(long)} "
              f"responses, density {len(long) / (n_id * n_it):.3f}, "
              f"dimensions "
              f"{long.groupby('itemcov_dimension')['item'].nunique().to_dict()}")

    for j in body.columns:
        if j in shipped or j in idcols or j in covcols.values():
            continue
        if str(construct[j]) == "TOTAL":
            print("  skip TOTAL: row sum over both blocks")
        elif body[j].isna().all():
            print(f"  skip column {j}: empty spacer")
        else:
            raise AssertionError(f"unaccounted column {j}: {construct[j]}")
    print(f"\n{len(BLOCKS)} tables, {total:,} responses")


if __name__ == "__main__":
    main()
