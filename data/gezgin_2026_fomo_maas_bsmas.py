#!/usr/bin/env python3
# Source: https://zenodo.org/records/21794626
# DOI: 10.5281/zenodo.21794626 (data; no paper or description on the record)
#   Gezgin, D. M. (2026). "Mindfulness & Well-being." Zenodo.
# Data: data_farkindalik.xls (an old BIFF .xls, read with xlrd), 863 Turkish
#   university students; demographics, social-media use questions and item
#   blocks PIO1-7, FoMO1-10, AT1-33, BF1-15, SMBergen1-6, with the deposit's
#   per-scale means (Toplam*).
# License: CC BY 4.0 (Zenodo record).
# Codebook: none.
#
# Item text: not shipped -- codes only.
#
# Tables (only the blocks whose instrument the column names identify):
#   gezgin_2026_fomo    FoMO1-FoMO10, Fear of Missing Out scale
#                       (Przybylski et al. 2013), 1-5
#   gezgin_2026_maas    BF1-BF15 ("Bilincli Farkindalik", the Turkish name of
#                       the Mindful Attention Awareness Scale: 15 items, 1-6)
#   gezgin_2026_bsmas   SMBergen1-6, Bergen Social Media Addiction Scale, 1-5
#   Each block's deposited mean (ToplamFoMO, ToplamBF, ToplamSMBergen) is
#   asserted equal to the mean of the items as deposited.
# Not shipped: PIO1-7 and AT1-AT33 -- the deposit does not name these
#   instruments, and there is no paper or codebook to (datastandard item 4).
# Covariates: cov_age where the typed age is 17-70 (values such as 2 and 124
#   are entry errors -> NA). Gender, class and faculty are unlabelled codes
#   and are not carried; free-text answers (eye colour, platform, reasons) are
#   not carried. id = row index.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = ("https://zenodo.org/api/records/21794626/files/"
            "data_fark%C4%B1ndal%C4%B1k.xls/content")
SPEC = {
    "gezgin_2026_fomo": ("FoMO", 10, "ToplamFoMO", range(1, 6)),
    "gezgin_2026_maas": ("BF", 15, "ToplamBF", range(1, 7)),
    "gezgin_2026_bsmas": ("SMBergen", 6, "ToplamSMBergen", range(1, 6)),
}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), engine="xlrd")
    assert d.shape == (863, 88), d.shape
    age_col = d.columns[1]
    assert str(age_col).startswith("Ya")
    age = pd.to_numeric(d[age_col], errors="coerce")
    d["cov_age"] = age.where(age.between(17, 70)).astype("Int64")
    d["id"] = range(1, len(d) + 1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (p, n, total, vals) in SPEC.items():
        allowed = set(vals)
        items = [f"{p}{i}" for i in range(1, n + 1)]
        comp = d.dropna(subset=items)
        assert ((comp[items].mean(axis=1) - comp[total]).abs() < 1e-9).all()
        long = d.melt(id_vars=["id", "cov_age"], value_vars=items,
                      var_name="item", value_name="resp").dropna(
                          subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - allowed, table
        long = long[["id", "item", "resp", "cov_age"]]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
