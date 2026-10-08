#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.vhhmgqnpv (Zenodo mirror: https://zenodo.org/records/4995859)
# DOI: 10.5061/dryad.vhhmgqnpv (dataset; no paper DOI on the record)
#   Kermen, Umut (2019). "Anxiety, self-efficacy, and self-regulation in high school
#   students: The mediating role of attentional control" [data set], Dryad.
# Data: ogrenmesonveriler.sav: 334 high-school students (Zeytinburnu, Istanbul) x 154
#       columns: sira (row number), gender, grade, age; raw item blocks b1-17, c1-16,
#       e1-20, d1-20; four scale sums; and a SMEAN()-imputed copy of every item
#       (suffix _1, variable label "SMEAN(b1)" etc.). No codebook.
# License: CC0 1.0 (Dryad record).
#
# Item text: not shipped. Levels checked: .sav variable labels (blank on every raw item;
#   only the imputed copies carry "SMEAN(x)"), value labels (only on gender and grade).
#   Wording is in the Turkish adaptations of the published scales.
#
# Blocks -> scales (the record names four instruments; blocks matched by item count, range
#   and the deposit's Turkish sum names):
#   kermen_2019_self_efficacy        b1-17  1-5  General Self-Efficacy Scale (17 items;
#                                                sum "ozyeterlik")
#   kermen_2019_self_regulation      c1-16  1-5  Perceived Self-Regulation Scale (16
#                                                items; sum "ozduzenleme")
#   kermen_2019_attentional_control  e1-20  1-4  Attentional Control Scale (20 items; sum
#                                                "dikkat"). The "y" suffix marks e1, 2, 3,
#                                                6, 7, 8, 11, 12, 15, 16, 20 -- exactly the
#                                                ACS's reverse-keyed items -- and they are
#                                                STORED REVERSED: the sum equals the plain
#                                                sum of the stored values and the y items
#                                                correlate positively with the others.
#                                                Codes kept (e1y, ...).
#   kermen_2019_anxiety              d1-20  0-3  anxiety, STAI per the record (20 items;
#                                                sum "kaygi"), coded 0-3 in the file
# Raw (pre-imputation) columns are used; the 80 SMEAN copies and four sums are skipped.
# Dropped cells (isolated out-of-range values): c6 = 6 and c7 = 6 (one each on a 1-5
#   scale), e9 = 22 and e18 = 32 (typos on a 1-4 scale).
# Covariates: cov_gender (1 erkek, 2 kiz, .sav value labels), cov_grade (9-12), cov_age.

import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "kermen_2019"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/4995859/files/ogrenmesonveriler.sav/content"

ACS_REV = {1, 2, 3, 6, 7, 8, 11, 12, 15, 16, 20}
ACS = [f"e{i}{'y' if i in ACS_REV else ''}" for i in range(1, 21)]
TABLES = {
    "kermen_2019_self_efficacy": ([f"b{i}" for i in range(1, 18)], range(1, 6), "ozyeterlik"),
    "kermen_2019_self_regulation": ([f"c{i}" for i in range(1, 17)], range(1, 6), "ozduzenleme"),
    "kermen_2019_attentional_control": (ACS, range(1, 5), "dikkat"),
    "kermen_2019_anxiety": ([f"d{i}" for i in range(1, 21)], range(0, 4), "kaygi"),
}
COVS = {"cinsiyet": "cov_gender", "sinif": "cov_grade", "yas": "cov_age"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, meta = pyreadstat.read_sav(fetch())
    assert d.shape == (334, 154), d.shape
    items = [c for its, _, _ in TABLES.values() for c in its]
    sums = [s for _, _, s in TABLES.values()]
    imputed = [f"{c}_1" for c in items]
    assert all(meta.column_names_to_labels[c] == f"SMEAN({c[:-2]})" for c in imputed)
    assert set(d.columns) == {"sira"} | set(COVS) | set(items) | set(sums) | set(imputed)
    print("  skip 80 SMEAN-imputed copies (*_1) and 4 scale sums")
    for its, _, s in TABLES.values():  # sums are of the imputed copies, as stored
        assert (d[[f"{c}_1" for c in its]].sum(axis=1) - d[s]).abs().max() < 1e-9
    assert d["sira"].is_unique
    d = d.rename(columns={"sira": "id", **COVS})
    d["id"] = d["id"].astype(int)
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng, _) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        bad = ~t["resp"].isin(list(rng))
        for (it, v), n in t[bad].groupby(["item", "resp"]).size().items():
            print(f"    {name}: drop {it}={v:g} x{n}")
        assert bad.sum() <= 2, name
        t = t[~bad].copy()
        t["resp"] = t["resp"].astype(int)
        for c in covs:
            t[c] = t[c].astype("Int64")
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
