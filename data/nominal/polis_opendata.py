#!/usr/bin/env python3
"""Nominal companions of the 19 Polis core tables (built by data/polis_opendata.py,
PR #3512), one per conversation, named <core table>_nom:
  polis_2014_seattle_min_wage_nom
  polis_2015_football_concussions_nom
  polis_2015_vtaiwan_uberx_nom
  polis_2016_canada_electoral_reform_nom
  polis_2017_brexit_consensus_nom
  polis_2017_scoop_freshwater_nom
  polis_2017_scoop_housing_nom
  polis_2017_scoop_ubi_nom
  polis_2018_bowling_green_nom
  polis_2018_march_on_nom
  polis_2018_scoop_taxes_nom
  polis_2019_scoop_biodiversity_nom
  polis_2021_san_juan_land_use_nom
  polis_2022_klimarat_energy_nom
  polis_2022_klimarat_food_land_use_nom
  polis_2022_klimarat_housing_nom
  polis_2022_klimarat_mobility_nom
  polis_2022_klimarat_production_nom
  polis_2025_bowling_green_2050_nom

Source: The Computational Democracy Project, Polis open data,
github.com/compdemocracy/openData, CC BY 4.0 with the attribution recorded in
the core tables' dictionary rows; see the core script's header for the export
format and every coding decision. Licence as recorded for the core tables.

Why a companion. Polis offers three buttons on every statement: agree,
disagree and pass/unsure. The core tables score agree 1 / disagree 0 and store
a pass as a non-response (resp empty, resp_raw = "pass"), which suits a binary
IRT model. Here all three buttons are categories of a nominal response, so a
pass is an observed choice rather than a missing score.

Built as the nominal standard describes (datastandard.md, "The raw response
(`resp_raw`) and the nominal family"): a rename of the core table's resp_raw to
`text` and nothing more. resp is kept as the core table's score (1 / 0 / empty
for pass), every other column (date, itemcov_*) is carried as is, and every
row is kept, so ids, items, repeated id x item rows and dates are the core
table's exactly; the script asserts that. text: agree / disagree / pass, never
empty.

It reads the core table rather than rebuilding from the openData export, as
the other lifts in data/nominal/ do (enem.R, nomt_hooper_2024_study2.R): by
default the published core table via irw.fetch, or, before the core tables are
released, the core CSVs the core script wrote, from a directory given as the
first argument (this is how the first build was made, from the #3512 staging
CSVs).

Naming: the core tables' polis_<year>_<topic> form awaits a ruling (#3512).
STEM below is the one place the source name lives; if it changes, change it
here and the list of names above.

Usage: python3 polis_opendata.py [core_csv_dir] [out_dir]
"""
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

STEM = "polis"
CONVERSATIONS = [
    "2014_seattle_min_wage",
    "2015_football_concussions",
    "2015_vtaiwan_uberx",
    "2016_canada_electoral_reform",
    "2017_brexit_consensus",
    "2017_scoop_freshwater",
    "2017_scoop_housing",
    "2017_scoop_ubi",
    "2018_bowling_green",
    "2018_march_on",
    "2018_scoop_taxes",
    "2019_scoop_biodiversity",
    "2021_san_juan_land_use",
    "2022_klimarat_energy",
    "2022_klimarat_food_land_use",
    "2022_klimarat_housing",
    "2022_klimarat_mobility",
    "2022_klimarat_production",
    "2025_bowling_green_2050",
]
## core table -> nominal table
TABLES = {f"{STEM}_{c}": f"{STEM}_{c}_nom" for c in CONVERSATIONS}
SCORE = {"agree": 1.0, "disagree": 0.0, "pass": float("nan")}


def load_core(name, core_dir):
    if core_dir is not None:
        ## as text, so every value is written back exactly as the core CSV has it
        return pd.read_csv(core_dir / f"{name}.csv", dtype=str, keep_default_na=False)
    import irw
    df = pd.DataFrame(irw.fetch(name))
    df["resp"] = df["resp"].to_numpy(dtype=float, na_value=float("nan"))
    return df


def to_nominal(core, name):
    assert "resp_raw" in core.columns and "text" not in core.columns, name
    raw = core["resp_raw"]
    assert raw.isin(list(SCORE)).all(), raw.value_counts(dropna=False)
    ## resp must be the score of the label, row for row (blank <-> empty)
    expect = raw.map(SCORE)
    resp = pd.to_numeric(core["resp"].replace("", None), errors="raise").astype(float)
    assert ((resp == expect) | (resp.isna() & expect.isna())).all(), name
    df = core.rename(columns={"resp_raw": "text"})
    cols = ["id", "item", "resp", "text"] + [c for c in df.columns
                                             if c not in ("id", "item", "resp", "text")]
    return df[cols]


def main():
    core_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, nom in TABLES.items():
        core = load_core(name, core_dir)
        df = to_nominal(core, name)
        ## same rows, same order, same ids/items/dates as the core table
        assert len(df) == len(core)
        for c in [c for c in core.columns if c != "resp_raw"]:
            assert df[c].equals(core[c]), (name, c)
        qc = df.copy()
        for c in ("id", "item", "resp"):
            qc[c] = pd.to_numeric(qc[c].replace("", None)).astype(float)
        checks = run_qc(qc, permitted_values={i: {0, 1} for i in qc["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = out_dir / f"{nom}.csv"
        df.to_csv(out, index=False)
        print(out.name, len(df), df["id"].nunique(), df["item"].nunique(),
              df["text"].value_counts().to_dict())


if __name__ == "__main__":
    main()
