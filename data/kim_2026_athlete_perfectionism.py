#!/usr/bin/env python3
# Source: https://yorksj.figshare.com/articles/dataset/Perfectionism_Excellencism_and_Personal_Best_Performance_in_Track_and_Field_Athletics_Data_and_Code_/32961659/1
# DOI: 10.25421/yorksj.32961659 (data; no paper DOI on the record)
#   Kim H (2026). Perfectionism, Excellencism, and Personal Best Performance in
#   Track and Field Athletics (Data and Code). York St John University figshare.
# Data: SPSS.sav (263 track and field athletes x 61 columns).
# License: CC BY 4.0 (figshare record).
# Codebook: none; SPSS variable labels.
#
# IMPUTATION: every item column is labelled "SMEAN(<item>)" -- SPSS series-mean
#   replacement of missing cells; the original columns are not in the file.
#   Series-mean cells are non-integer, so every non-integer cell is dropped
#   (0-3 per item, 32 in all); integer cells are the respondents' answers.
#   (SKILL "A fractional value in a Likert column is an imputation".)
# Instruments, identified from the codes and the published item counts (no
#   paper or codebook names them):
#   kim_2026_pps_s  Performance Perfectionism Scale for Sport, self-oriented
#                   SOPP1-4 and socially prescribed SPPP1-4, 1-7 (8 items)
#   kim_2026_mips   Multidimensional Inventory of Perfectionism in Sport,
#                   striving for perfection SFP1-5 and negative reactions to
#                   imperfection NRI1-5, 1-5 (10 items)
#   kim_2026_smps2  Sport-MPS-2, personal standards PST1-7 and concern over
#                   mistakes COM1-8, 1-5 (15 items)
#   kim_2026_spes   Scale of Perfectionism-Excellencism, excellencism EX1-11
#                   and perfectionism PE1-11, 1-7 (22 items)
#   Item codes drop the "_1" SMEAN suffix (SOPP1_1 -> SOPP1).
# id = row index. Covariates: age, sex (Q2), years competing (Q3), training
#   hours per week (Q4), main event (Q5), IAAF points of the personal best.
#   Q3 and Q4 are free numeric answers as deposited.
# Item text: not shipped -- variable labels are the SMEAN formulas only.

import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/66512693"
SPEC = {
    "kim_2026_pps_s": ([("SOPP", 4), ("SPPP", 4)], range(1, 8)),
    "kim_2026_mips": ([("SFP", 5), ("NRI", 5)], range(1, 6)),
    "kim_2026_smps2": ([("PST", 7), ("COM", 8)], range(1, 6)),
    "kim_2026_spes": ([("EX", 11), ("PE", 11)], range(1, 8)),
}
COVS = {"Q1": "cov_age", "Q2": "cov_sex", "Q3": "cov_years_competing",
        "Q4": "cov_training_hours", "Q5": "cov_main_event", "IAAF": "cov_iaaf_points"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert d.shape == (263, 61), d.shape
    lab = meta.column_names_to_labels
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total_dropped = 0
    for table, (blocks, vals) in SPEC.items():
        allowed = set(vals)
        ren = {}
        for pre, n in blocks:
            for i in range(1, n + 1):
                src = f"{pre}{i}_1"
                assert lab[src] == f"SMEAN({pre}{i})", src
                ren[src] = f"{pre}{i}"
        cols = list(ren.values())
        long = d[["id"] + list(ren) + covs].rename(columns=ren).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        frac = long["resp"] % 1 != 0
        total_dropped += int(frac.sum())
        long = long[~frac]
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
    print(f"[drop] {total_dropped} SMEAN-imputed (non-integer) cells")


if __name__ == "__main__":
    main()
