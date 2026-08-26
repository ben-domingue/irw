"""Aiquipa Tello, Caycho Caja & Pajares Del Aguila (2026), Mendeley Data --
validation of the Dispositional Greed Scale (DGS) in Peruvian adults.

Source: https://data.mendeley.com/datasets/w5f55333p4/2
DOI: 10.17632/w5f55333p4.2
License: CC BY 4.0

Two independent Peruvian samples (308 and 498 adults) completing the same
7-item Dispositional Greed Scale on the same 1-5 response format.

Tables written
--------------
aiquipa_2026_dgs   806 respondents x 7 items, 1-5

Coding notes
------------
* **One table, not two.** The two workbook sheets are different samples given
  the identical instrument -- same seven `COD` items, same 1-5 scale -- so
  they are pooled with `cov_study` recording which sample a respondent is
  from, rather than split into two files.
* `id` is assigned across the pooled file; neither sheet carries an
  identifier column.
* Sheet 2 additionally carries `Codicia`, `Envidia`, `Maquiavelismo`,
  `Psicopatía` and `Narcisismo` -- scored totals whose items are not
  deposited (only `Codicia` is the DGS total, recomputable from the items).
* The two sheets spell the education column differently
  (`Niveldeinstrucción` vs `Nieldeinstrucciónalcanzado`, a typo in one); both
  map to `cov_education`.
"""

import io
import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

DOI = "10.17632/w5f55333p4.2"
DATASET, VERSION = "w5f55333p4", 2
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}
OUTDIR = "irw_output"
TABLE = "aiquipa_2026_dgs"
ITEMS = [f"COD{i}" for i in range(1, 8)]
COVS = {"Género": "cov_gender", "Edad": "cov_age",
        "Departamentoyprovinciaderesidencia": "cov_region",
        "Niveldeinstrucción": "cov_education",
        "Nieldeinstrucciónalcanzado": "cov_education",
        "Ocupación": "cov_occupation",
        "Nivelsocioeconómicopercibido": "cov_ses",
        "NivelSocioeconómicopercibido": "cov_ses"}
SKIP = {"Codicia": "DGS total, recomputable from the items",
        "Envidia": "scored total; its items are not deposited",
        "Maquiavelismo": "scored total; its items are not deposited",
        "Psicopatía": "scored total; its items are not deposited",
        "Narcisismo": "scored total; its items are not deposited"}


def main():
    s = requests.Session()
    s.headers.update(UA)
    listing = s.get(f"https://data.mendeley.com/public-api/datasets/"
                    f"{DATASET}/files?folder_id=root&version={VERSION}",
                    timeout=120).json()
    hit = [f for f in listing if f["filename"].lower().endswith(".xlsx")]
    assert len(hit) == 1, [f["filename"] for f in listing]
    raw = s.get(hit[0]["content_details"]["download_url"], timeout=600)
    raw.raise_for_status()
    book = pd.ExcelFile(io.BytesIO(raw.content))
    assert len(book.sheet_names) == 2, book.sheet_names

    frames, offset = [], 0
    for n, sheet in enumerate(book.sheet_names, start=1):
        d = book.parse(sheet)
        assert set(ITEMS) <= set(d.columns), (sheet, list(d.columns))
        d = d.rename(columns=COVS)
        d["id"] = range(offset + 1, offset + len(d) + 1)
        offset += len(d)
        d["cov_study"] = n
        for c in book.parse(sheet).columns:
            if c in ITEMS or c in COVS:
                continue
            assert c in SKIP, f"unaccounted column in {sheet}: {c}"
            print(f"  skip {sheet}/{c}: {SKIP[c]}")
        keep = ["id", "cov_study"] + sorted(set(COVS.values()))
        frames.append(d[keep + ITEMS])

    d = pd.concat(frames, ignore_index=True)
    long = d.melt(id_vars=[c for c in d.columns if c not in ITEMS],
                  value_vars=ITEMS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]
                + [c for c in long.columns if c.startswith("cov_")]]

    assert long["resp"].between(1, 5).all()
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long)
    bad = [c for c in checks if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    n_id, n_it = long["id"].nunique(), long["item"].nunique()
    print(f"\n{path}: {n_id} respondents x {n_it} items = {len(long)} "
          f"responses, density {len(long) / (n_id * n_it):.3f}, "
          f"samples {long.groupby('cov_study')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    main()
