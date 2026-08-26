"""Dalichaouche (2026), figshare -- COVID-19 knowledge, attitudes and
practices among Algerian university students.

Source: https://figshare.com/articles/dataset/_/31851586
DOI: 10.6084/m9.figshare.31851586
Data: Base de donnee_KAP_etudiant COVID-19.xlsx
License: CC BY 4.0

300 Algerian university students answering a knowledge-attitudes-practices
questionnaire about COVID-19. Recovered 2026-08-25 from the candidate pool
that had been unintentionally blocklisted by `googlesheet_humaneye.csv`.

Tables written
--------------
dalichaouche_2026_covid_knowledge   6 items, 0-1
dalichaouche_2026_covid_attitudes   5 items, 0-2
dalichaouche_2026_covid_practices   6 items, 0-2

Coding notes
------------
* The three blocks are shipped separately because their response formats
  differ: knowledge items are scored right/wrong (0-1) while the attitude and
  practice items are 3-point (0-2). Every block is homogeneous within itself,
  with no constant items and no out-of-range values.
* `N°` is not usable as an identifier -- it repeats -- so `id` is the row
  position (one row is one respondent).
* The file also carries symptom checkboxes (`Fievre`, `Toux`, `Fatigue`, ...)
  and infection-history questions. Those are individual clinical questions
  rather than a scored instrument, and are not exported -- the same call made
  for `senyurt_2023_burnout`'s yes/no pandemic questions.
* `Wilaya` (province) is carried as a covariate; `autre wilaya` is free text
  and is not.
"""

import io
import os
import re

import pandas as pd
import requests

FILES_API = "https://api.figshare.com/v2/articles/31851586/files"
OUTDIR = "irw_output"
UA = {"User-Agent": "Mozilla/5.0 (IRW-research)"}

BLOCKS = [("C", "covid_knowledge", 6, (0, 1)),
          ("A", "covid_attitudes", 5, (0, 2)),
          ("P", "covid_practices", 6, (0, 2))]

COVS = {"Spécialité": "cov_speciality", "Niveau d'étude": "cov_study_level",
        "Age": "cov_age", "Sexe": "cov_sex", "Wilaya": "cov_province"}


def _load() -> pd.DataFrame:
    files = requests.get(FILES_API, timeout=60, headers=UA).json()
    xl = [f for f in files if f["name"].lower().endswith((".xlsx", ".xls"))]
    assert len(xl) == 1, [f["name"] for f in files]
    raw = requests.get(xl[0]["download_url"], timeout=300, headers=UA)
    raw.raise_for_status()
    return pd.read_excel(io.BytesIO(raw.content))


def main():
    d = _load()
    assert d["N°"].duplicated().any(), "N° is unique after all -- use it as id"
    d = d.reset_index(drop=True).copy()
    d["id"] = range(1, len(d) + 1)
    present = {k: v for k, v in COVS.items() if k in d.columns}
    d = d.rename(columns=present)
    cov_cols = list(present.values())

    os.makedirs(OUTDIR, exist_ok=True)
    for prefix, suffix, n_expected, (lo, hi) in BLOCKS:
        items = [c for c in d.columns if re.match(rf"^{prefix}\d+$", str(c))]
        assert len(items) == n_expected, (suffix, len(items))

        long = d.melt(id_vars=["id"] + cov_cols, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        assert long["resp"].between(lo, hi).all(), (
            suffix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"dalichaouche_2026_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
