#!/usr/bin/env python3
# Source: https://zenodo.org/records/23157249
# DOI: 10.5281/zenodo.23157249 (data); paper preprint 10.31234/osf.io/e5hma_v1
#   Ribar, M., Lazarevic, L., Razum, J., & Milas, G. (2026). "Beyond the Big
#   Five: Disintegration as a Predictor of Daily Depression, Anxiety, and
#   Rumination." PsyArXiv.
# Data: Zenodo 23157249, data.delt.rum.csv (916 diary rows x 92 columns; 156
#   Croatian psychology students, up to 7 daily diary entries each). The
#   person-level questionnaires (BFI-2, DELTA) are repeated on every diary row
#   of a person, identically (asserted), so they are read once per person.
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Checked against the preprint: 156 students, 916 observations (both match).
#
# Item text: not shipped -- no wording in the deposit (the R script names the
#   BFI-2 facets only). BFI-2 (Soto & John 2017, Croatian adaptation) and the
#   DELTA disintegration scale (Knezevic et al.) are published third-party
#   instruments; wording would come from their publications.
#
# Tables:
#   ribar_2026_bfi2   BFI-2, bfi1..bfi60, 1-5, as answered. The deposit is raw:
#                     its analysis script builds the reversed copies itself
#                     (6 - x on the BFI-2's published reverse-keyed items).
#   ribar_2026_delta  DELTA (Disintegration), delta1..delta20, 1-5.
#
# Dropped, with reasons:
#   SIFRA_FINAL        self-generated participant code -> replaced by a
#                      person index
#   gen                1/2/3 codes, unlabelled anywhere in the deposit
#   completed_questionnaires  count of diary entries (not a response)
#   dphq1-2, dgad1-2   daily PHQ-2 / GAD-2: 2 items each, under the 3-item floor
#   drum1-3            daily rumination, 3 items x up to 7 days: the deposit has
#                      no day index (rows are in an unstated order, 62 rows are
#                      exact repeats of another row of the same person), so
#                      `wave` cannot be assigned from the source. Not shipped.
# Covariates: cov_age (years).

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
DATA_URL = ("https://zenodo.org/api/records/23157249/files/"
            "data.delt.rum.csv/content")
SCALES = {
    "ribar_2026_bfi2": [f"bfi{i}" for i in range(1, 61)],
    "ribar_2026_delta": [f"delta{i}" for i in range(1, 21)],
}
ALLOWED = {1, 2, 3, 4, 5}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), encoding="cp1252")
    assert d.shape == (916, 92), d.shape
    assert d["SIFRA_FINAL"].nunique() == 156

    person_cols = ["age"] + [c for cols in SCALES.values() for c in cols]
    g = d.groupby("SIFRA_FINAL", sort=False)
    assert (g[person_cols].nunique(dropna=False) <= 1).all().all(), \
        "person-level columns vary within person"
    p = g[person_cols].first().reset_index(drop=True)
    p.insert(0, "id", p.index + 1)
    p["cov_age"] = p["age"]

    used = set(person_cols) | {"SIFRA_FINAL"}
    dropped = [c for c in d.columns if c not in used]
    print(f"[drop] {dropped}")

    for table, cols in SCALES.items():
        long = p.melt(id_vars=["id", "cov_age"], value_vars=cols,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        bad = set(long["resp"]) - ALLOWED
        assert not bad, (table, bad)
        long = long[["id", "item", "resp", "cov_age"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: ALLOWED for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
