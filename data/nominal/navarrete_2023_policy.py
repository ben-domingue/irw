#!/usr/bin/env python3
"""navarrete_2023_policy_{france,brazil}_nom: nominal companions of the core
tables navarrete_2023_policy_approval_{france,brazil} (built by
data/navarrete_2023_policy.py, PR #3511).

Naming: the core name + "_nom" would be 41 characters, over the 40-character
cap (datastandard.md), so the construct label drops "approval". The names live
in TABLES below and nowhere else in this script.

Source: Navarrete et al., Harvard Dataverse doi:10.7910/DVN/8E0EA4 (CC0 1.0);
see the core script's header for the deposit, the screens and every coding
decision. Licence as recorded for the core tables.

Why a companion. The approval screen offered three buttons: approve, disapprove
and "blank" (fr "blanc"). The core tables score approve 1 / disapprove 0 and
store a blank as a non-response (resp empty, resp_raw = "blank"), which suits a
binary IRT model. Here all three buttons are categories of a nominal response,
so a blank is an observed choice rather than a missing score.

Built as the nominal standard describes (datastandard.md, "The raw response
(`resp_raw`) and the nominal family"): a rename of the core table's resp_raw to
`text` and nothing more. resp is kept as the core table's score (1 / 0 / empty
for blank), every other column (date, cov_*) is carried as is, and every row is
kept, so ids, items, repeated id x item rows and dates are the core table's
exactly; the script asserts that. text: approve / disapprove / blank, never
empty.

It reads the core table rather than rebuilding from the Dataverse files, as the
other lifts in data/nominal/ do (enem.R, nomt_hooper_2024_study2.R): by default
the published core table via irw.fetch, or, before the core tables are released,
the core CSVs the core script wrote, from a directory given as the first
argument (this is how the first build was made, from the #3511 staging CSVs).

Usage: python3 navarrete_2023_policy.py [core_csv_dir] [out_dir]
"""
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

## core table -> nominal table
TABLES = {
    "navarrete_2023_policy_approval_france": "navarrete_2023_policy_france_nom",
    "navarrete_2023_policy_approval_brazil": "navarrete_2023_policy_brazil_nom",
}
SCORE = {"approve": 1.0, "disapprove": 0.0, "blank": float("nan")}


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
