"""Democratic Health Questionnaire (DHQ), school version.

Source: Ristic Dedic, Jokic & Matic Bojic (2025), Zenodo
10.5281/zenodo.15341219, CC BY 4.0. 834 schools x 102 columns.

The instrument is 30 statements about democratic practice in schools, each
rated on THREE separate 0-100 sliders:

  importance    how important the practice is
  currentstate  how far it is currently realised
  expectation   what is expected of it

Those are three different response frames over one statement set, so they ship
as three tables sharing the same 30 item codes -- one item text table joins to
all three. Pooling them would make `resp` mean three different things in one
column.

`resp` is continuous 0-100, which `datastandard.md` permits: these are slider
responses as collected, not scores derived from anything.

`id` is the school, not a person. The DHQ school version is answered once per
institution by a school representative, so the school is the focal unit being
measured -- the case `datastandard.md` covers with "typically a person, but
sometimes another entity". The 12 non-item columns are school attributes and
ship as covariates.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 15341219
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

FACETS = {"importance": "risticdedic_2025_dhq_importance",
          "currentstate": "risticdedic_2025_dhq_currentstate",
          "expectation": "risticdedic_2025_dhq_expectation"}

COVARIATES = {
    "country": "cov_country",
    "qnt_language": "cov_questionnaire_language",
    "public_private": "cov_public_private",
    "location": "cov_school_location",
    "learners_number": "cov_n_students",
    "financing_education": "cov_financing",
    "learners_percent_diff_language": "cov_pct_different_first_language",
    "learners_percent_ed_needs": "cov_pct_additional_needs",
    "learners_percent_dis_socecon": "cov_pct_disadvantaged",
}
# qnt_type and education_target_group are constant across all 834 schools
# (this is the single school-version file), so they carry no information.
CONSTANT = ["qnt_type", "education_target_group"]

FACET_RE = re.compile(r"^(?P<stem>.+)_(?P<facet>importance|currentstate|expectation)$")


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, _meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)

    by_facet = {f: [] for f in FACETS}
    for c in df.columns:
        m = FACET_RE.match(c)
        if m:
            by_facet[m.group("facet")].append(c)

    stems = {f: sorted(FACET_RE.match(c).group("stem") for c in cols)
             for f, cols in by_facet.items()}
    assert len(set(map(tuple, stems.values()))) == 1, \
        "the three facets do not cover the same statement set"
    assert len(stems["importance"]) == 30, \
        f"expected 30 statements, found {len(stems['importance'])}"

    for c in CONSTANT:
        assert df[c].nunique(dropna=True) == 1, f"{c} is not constant after all"

    accounted = set(sum(by_facet.values(), [])) | set(COVARIATES) \
        | set(CONSTANT) | {"ID"}
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = list(COVARIATES.values())
    df["id"] = df["ID"].astype(int)
    assert df["id"].is_unique, "ID is not one row per school"

    os.makedirs(OUT_DIR, exist_ok=True)
    for facet, table in FACETS.items():
        cols = by_facet[facet]
        long = (df.melt(id_vars=["id"] + covs, value_vars=cols,
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        # Item code is the statement, shared across the three facet tables so
        # one item text table joins to all of them.
        long["item"] = long["item"].str.replace(f"_{facet}$", "", regex=True)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == 30, table
        assert long["resp"].between(0, 100).all(), f"{table}: expected 0-100"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
