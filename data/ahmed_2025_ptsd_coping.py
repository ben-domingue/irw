#!/usr/bin/env python3
# Source: https://zenodo.org/records/15849532
# DOI: none found. The deposit has no related identifiers and a Crossref /
#   Europe PMC search (title, authors, "Sudan PTSD coping") found no paper as
#   of 2026-10-02.
#   Ahmed, W. M. M., Abdallah, W. E. A., Mohamed, M., & Elbadawi, M. H.
#   (2025). Data: PTSD and coping in Sudan's war [Data set]. Zenodo.
#   https://doi.org/10.5281/zenodo.15849532
# Data: SPSS data.sav (716 rows x 55 columns; adults 18-70 affected by the
#       war in Sudan).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels are populated: every P* and C*
#   column carries its full English stem as the variable label and its
#   anchors as value labels. Not built because the administered language is
#   undocumented (a Sudanese sample, very possibly answered in Arabic, so the
#   English may be a translated substitute) and there is no paper to settle
#   it. PCL-5 is ship_with_note in the rights register; the coping scale is
#   unidentified. Cheap once the language is known.
#
# Tables (item codes are the source column names):
#   ahmed_2025_pcl5  P1-P8, P10-P21: the 20 PCL-5 items, 0 "Not at all" ..
#       4 "Extremely" (value labels). The source numbering skips P9; P10 is
#       PCL-5 item 9 ("strong negative beliefs about yourself..."), so the
#       codes are offset by one from item 10 on but all 20 PCL-5 stems are
#       present, in order (checked against the variable labels). PTSD.scale
#       equals their sum (asserted).
#   ahmed_2025_coping  C1-C13: a 13-item coping scale ("I spend time trying
#       to understand what happened", "I try to see the humor in it", ...),
#       1 "Not true about me" .. 4 "Mostly true about me" (value labels).
#       The deposit does not name the instrument. Coping.scale equals the
#       sum (asserted).
#
# Dropped:
#   - Totals and derived: PTSD.scale, Coping.scale, PTSD.diagnosis,
#     Current.residency.analysis.chi (a collapsed recode of
#     Current.residency), and the regression diagnostics COO_1, LEV_1, MAH_1,
#     COO_2, COO_3, LEV_3.
#   - 2 rows that repeat another row in all 54 non-ID columns (IDs 226 and
#     147, duplicating 217 and 144; the second pair is straight-lined at the
#     maximum of both scales). Treated as repeated submissions, so 714 remain.
# id: row index. "ID" (1-716) is a study sequence number and is not shipped.
# No free text, dates or identifiers are in the file.
# Covariates (codes per the value labels): cov_age (years), cov_gender
#   (1 male, 2 female), cov_marital (1 single .. 5 divorced),
#   cov_time_in_conflict_area (1 <1 month .. 4), cov_displacement (0 not,
#   1 internally, 2 externally displaced), cov_residence_type (1 city,
#   2 village, 3 refugee camp, 4 other), cov_family_members,
#   cov_current_state (1-14, Sudanese state), cov_income (1-4 bands, SDG),
#   cov_employment (0 unemployed .. 4), cov_living_with (1 alone .. 4).

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/15849532/files/"
       "SPSS%20data.sav/content")

PCL = [f"P{i}" for i in range(1, 22) if i != 9]
COPE = [f"C{i}" for i in range(1, 14)]
TABLES = {"ahmed_2025_pcl5": PCL, "ahmed_2025_coping": COPE}
LABELS = {
    "ahmed_2025_pcl5": {0.0: "Not at all", 1.0: "A little bit",
                        2.0: "Moderately", 3.0: "Quite a bit",
                        4.0: "Extremely"},
    "ahmed_2025_coping": {1.0: "Not true about me",
                          2.0: "A little true about me",
                          3.0: "Somewhat true about me",
                          4.0: "Mostly true about me"},
}
DROPPED = {"ID", "PTSD.scale", "Coping.scale", "PTSD.diagnosis",
           "Current.residency.analysis.chi", "COO_1", "LEV_1", "MAH_1",
           "COO_2", "COO_3", "LEV_3"}
COVS = {"Age": "cov_age", "Gender": "cov_gender",
        "Marital.status": "cov_marital",
        "Period.conflict": "cov_time_in_conflict_area",
        "Dsiplacement": "cov_displacement",
        "Type.residency": "cov_residence_type",
        "N.family.members": "cov_family_members",
        "Current.residency": "cov_current_state", "Income": "cov_income",
        "Employment": "cov_employment", "living.with": "cov_living_with"}


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
    assert d.shape == (716, 55), d.shape

    known = set(PCL) | set(COPE) | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["ID"].is_unique
    assert (d[PCL].sum(axis=1) == d["PTSD.scale"]).all()
    assert (d[COPE].sum(axis=1) == d["Coping.scale"]).all()
    assert "negative beliefs" in meta.column_names_to_labels["P10"]
    assert "Trouble remembering" in meta.column_names_to_labels["P8"]
    for table, its in TABLES.items():
        for c in its:
            assert meta.variable_value_labels[c] == LABELS[table], c

    rest = d.drop(columns=["ID"])
    dup = rest.duplicated(keep="first")
    assert sorted(d.loc[dup, "ID"]) == [147.0, 226.0], d.loc[dup, "ID"]
    d = d[~dup].reset_index(drop=True)
    assert len(d) == 714
    assert not d[PCL + COPE].T.duplicated().any()

    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = {int(k) for k in LABELS[table]}
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
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
