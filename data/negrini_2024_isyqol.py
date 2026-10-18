#!/usr/bin/env python3
# Source: https://zenodo.org/records/10534309
# DOI: none recorded on the deposit (no related identifiers). The ISYQOL
#   instrument itself is Caronni, A., Zaina, F., & Negrini, S. (2014),
#   "Improving the measurement of health-related quality of life in
#   adolescent with idiopathic scoliosis: the ISYQOL questionnaire", Eur J
#   Phys Rehabil Med 50(6), PMID 24955762 -- cited as the instrument, not as
#   the source of these data.
#   Negrini, S. (2024). "ISYQOL Cross cultural." Zenodo.
# Data: Zenodo 10534309, "ISYQOL Cross cultural, db.xlsx", sheet 'Foglio1'
#       (550 rows x 22 columns; adolescents with idiopathic scoliosis across
#       seven countries).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped. The data file is a plain spreadsheet whose headers
#   are positional ("item_1".."item_20") -- no variable labels and no value
#   labels, since .xlsx carries neither level, and the deposit ships no
#   codebook or questionnaire file (the record holds this one .xlsx). The
#   wording of the 20 ISYQOL items is in the published instrument
#   (Caronni/Zaina/Negrini 2014 and its validated translations), which is a
#   multi-hop citation away and differs per nation -- the deposit does not
#   record which translation each `nation` received. That is where the text
#   is.
#
# Tables:
#   negrini_2024_isyqol  item_1-item_20, ISYQOL health-related quality of
#       life, 0-2 per item. One table: one instrument, one response format,
#       with the country as a covariate rather than seven files.
#
# Sentinel: items 14-20 arrive as text because they carry "*" for missing;
#   "*" is mapped to NA and the columns cast to integer. Items 1-13 are
#   already numeric (no "*" occurs in them).
# Dropped: ID (replaced by itself as `id`), nation -> cov_nation. Nothing
#   else is in the file; there is no composite score.
# id: the deposit's own ID column (1..550, one row per respondent).
# Covariates: cov_nation (integer country code 1-7; the deposit does not
#   name the countries, so the codes are carried as given).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://zenodo.org/api/records/10534309/files/"
            "ISYQOL%20Cross%20cultural%2C%20db.xlsx/content")

TABLE = "negrini_2024_isyqol"
ITEMS = [f"item_{i}" for i in range(1, 21)]
ALLOWED = {0, 1, 2}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=180)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Foglio1")
    assert d.shape == (550, 22), d.shape

    # Balance the books: every source column is an item, the id or a covariate.
    known = set(ITEMS) | {"ID", "nation"}
    assert set(d.columns) == known, set(d.columns) ^ known
    print(f"[cols] {len(ITEMS)} items, id=ID, cov_nation=nation; none dropped")

    assert d["ID"].is_unique and d["ID"].notna().all()
    d = d.rename(columns={"ID": "id", "nation": "cov_nation"})

    # "*" is this file's missing code, and it is why items 14-20 read as text.
    star = 0
    for c in ITEMS:
        if d[c].dtype == object or str(d[c].dtype).startswith("string"):
            s = d[c].astype(str).str.strip()
            star += int((s == "*").sum())
            d[c] = pd.to_numeric(s.where(s != "*"), errors="raise")
    print(f"[sentinel] {star} '*' cell(s) read as missing")

    long = d.melt(id_vars=["id", "cov_nation"], value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long["cov_nation"] = long["cov_nation"].astype("Int64")

    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)

    long = long[["id", "item", "resp", "cov_nation"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() == 20
    assert long["id"].nunique() == 550

    checks = run_qc(long, permitted_values={i: ALLOWED for i in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail}")

    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    print(f"[write] {out.name}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
