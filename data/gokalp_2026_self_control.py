#!/usr/bin/env python3
# Source: https://zenodo.org/records/19292962
# DOI: 10.3389/fpsyg.2026.1829371
#   Gokalp, Uztemur & Cengelci Kose (2026). "Psychometric properties, Rasch
#   analysis, and measurement invariance of the Turkish Brief Self-Control
#   Scale in early adolescents: exploring the mediating role of
#   responsibility in the self-control and patience association." Frontiers
#   in Psychology. (PMC13183628)
# Data: Zenodo 19292962, "oz denetim dfa 351 tmm.sav" (351 rows x 36 columns;
#       Turkish secondary-school students aged 10-14, paper-and-pencil,
#       2024-25). The deposit's .xlsx is the same data.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. Both label levels checked: no variable labels on
#   any item; value labels on sor*/sab* carry the four Turkish anchors
#   ("bana hic uygun degil" .. "bana tamamen uygun"), self* have none. The
#   stems are in the published instruments: Turkish BSCS (paper Appendix A),
#   Responsibility Scale (Gokalp 2021), Patience Scale (Gokalp 2022).
#
# Tables (item codes are the source column names):
#   gokalp_2026_bscs            13 items, 1-5  Brief Self-Control Scale
#                               (Tangney et al. 2004, Turkish). Paper: 5-point
#                               (1 = not at all suitable for me .. 5 = very
#                               suitable). The paper reverse-codes nine items;
#                               the file holds the codes AFTER that recode
#                               (every inter-item correlation is positive,
#                               and selfC tracks the item mean, r = .94), so
#                               these are keyed toward self-control, not raw.
#   gokalp_2026_responsibility   7 items, 1-4  Responsibility Scale (paper:
#                               4-point, 1 = does not describe me at all ..
#                               4 = describes me completely).
#   gokalp_2026_patience         6 items, 1-4  Patience Scale (same anchors).
#
# Cleaning:
#   - Two respondents are coded 0 on all 13 responsibility/patience items.
#     0 is not an option on either scale; these are skipped blocks -> NA.
#   - 29 BSCS cells across 6 respondents hold non-integer values (e.g.
#     3.7276), i.e. mean-imputed fills, not answers. Dropped; the paper
#     says nothing about imputation. One respondent's whole BSCS block is
#     imputed, so bscs has 350 ids.
#
# Dropped: respon, patient, selfC (scale scores).
# id: row index (the file has no respondent id).
# Covariates: cov_school (school_id, 5 schools), cov_gender (1 girl, 2 boy),
#   cov_grade (5-8), cov_age, cov_parents_together (1 yes, 2 no),
#   cov_mom_edu, cov_dad_edu (1 primary .. 4).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/records/19292962/files/"
       "%C3%B6z%20denetim%20dfa%20351%20tmm.sav?download=1")

TABLES = {
    "gokalp_2026_bscs": ([f"self{i}" for i in range(1, 14)], range(1, 6)),
    "gokalp_2026_responsibility": ([f"sor{i}" for i in range(1, 8)],
                                   range(1, 5)),
    "gokalp_2026_patience": ([f"sab{i}" for i in range(1, 7)], range(1, 5)),
}
COMPOSITES = {"respon", "patient", "selfC"}
COVS = {"school_id": "cov_school", "gender": "cov_gender",
        "class": "cov_grade", "age": "cov_age",
        "parents": "cov_parents_together", "mom_edu": "cov_mom_edu",
        "dad_edu": "cov_dad_edu"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (351, 36), d.shape

    # Balance the books: every column is an item, a covariate or a composite.
    items = {c for its, _ in TABLES.values() for c in its}
    assert set(d.columns) == items | COMPOSITES | set(COVS), \
        set(d.columns) ^ (items | COMPOSITES | set(COVS))

    # class is value-labelled 1..4 -> grades 5..8.
    grade = meta.variable_value_labels["class"]
    d["class"] = d["class"].map(lambda v: int(grade[v]) if v in grade else v)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    rp = [c for c in d.columns if c.startswith(("sor", "sab"))]
    zero = d[rp].eq(0)
    assert zero.sum().sum() == 26 and zero.all(axis=1).sum() == 2
    d[rp] = d[rp].mask(zero)

    bs = TABLES["gokalp_2026_bscs"][0]
    frac = d[bs].notna() & (d[bs] % 1 != 0)
    assert frac.sum().sum() == 29 and frac.any(axis=1).sum() == 6
    d[bs] = d[bs].mask(frac)

    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - set(allowed)
            assert not bad, (table, it, bad)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        pv = {i: set(allowed) for i in its}
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
