#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355477
# DOI: 10.1371/journal.pone.0355477
# Paper: Humayun S, Saleem S, Hussain MA, Shabbir R (2026). "I" calling in
#   group: How collaborative crafting and LMX augment team performance.
#   PLOS ONE 21(8): e0355477.
# Data: S1 File (CSV, "Dataset"), 198 rows x 22 columns, attached to the
#   article itself. No codebook in the deposit; column meanings come from the
#   paper's Measures section.
# License: CC BY 4.0 (the article's licence covers its SI file).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format).
#
# Design (paper, "Sample and procedure"): 198 employees in 49 teams of eight
# Pakistani manufacturing firms. Members rated living a calling at T1 and
# collaborative crafting and team performance four weeks later at T2; team
# LEADERS rated LMX at T1. The deposit's `id` column is the TEAM (49 values,
# 3-7 rows each), not the person: the seven LMX columns are constant within
# every team (asserted below), consistent with one leader rating per team.
#
# THREE output tables, member-rated, 198 respondents each:
#   humayun_2026_living_calling  -- C1-C6, Living a Calling Scale (Duffy et al.,
#       paper ref 19), 6 items, 1-5 strongly disagree..strongly agree. The paper
#       says a 'Not applicable' option was also offered; no such code occurs in
#       the deposit (every cell is 1-5), so none is shipped.
#   humayun_2026_collab_crafting -- CC1-CC3, collaborative crafting (Leana et
#       al., ref 16), 3 items, 1 = not at all .. 5 = a great deal.
#   humayun_2026_team_performance -- TP1-TP5, team performance, 5 items,
#       five-point Likert scale of Makikangas et al. (paper ref 48), member-
#       rated ("Living a calling, collaborative crafting and team performance
#       were rated by the subordinates").
# NOT SHIPPED: LMX1-LMX7 (Graen & Uhl-Bien LMX-7). It is a leader rating, one
#   per team, so its true N is 49 raters -- below the N>=100 floor. Its
#   columns are dropped, not carried as covariates.
#
# Item codes are the deposit's own headers.
# Covariates: cov_team (the deposit's team `id`, 1-49).
# `id`: the deposit has no person identifier; the row index (1-198) is used.
#
# Imputation: none stated ("imput" absent from the article); every cell is an
#   integer 1-5, no missing values (asserted).
#
# Item text: not shipped -- the deposit's headers are positional (C1, CC1,
#   TP1); the Living a Calling items are in Duffy et al. (paper ref 19), the
#   collaborative crafting stems are quoted in the paper's Measures section
#   (Leana et al., ref 16), team performance in Makikangas et al. (ref 48). No register rows checked for either, since the stems
#   are not in hand for all items.
#
# PII: no string columns at all (all 22 columns integer); asserted.

import os
import socket
import sys
import tempfile

import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = ("https://journals.plos.org/plosone/article/file?type=supplementary"
       "&id=10.1371/journal.pone.0355477.s001")
RAW = os.environ.get("HUMAYUN_RAW", "")

N_ROWS, N_TEAMS = 198, 49
LO, HI = 1, 5
TABLES = {
    "humayun_2026_living_calling": [f"C{i}" for i in range(1, 7)],
    "humayun_2026_collab_crafting": [f"CC{i}" for i in range(1, 4)],
    "humayun_2026_team_performance": [f"TP{i}" for i in range(1, 6)],
}
LMX = [f"LMX{i}" for i in range(1, 8)]


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "humayun_s1.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def convert():
    df = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert df.shape == (N_ROWS, 22), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
               or df[c].dtype == object]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s): {strings}")
    assert len(df.columns) > 0 and strings == []
    assert df["id"].nunique() == N_TEAMS
    # LMX is a leader rating: constant within team
    assert (df.groupby("id")[LMX].nunique() == 1).all().all()
    df = df.rename(columns={"id": "cov_team"})
    df.insert(0, "id", range(1, N_ROWS + 1))

    os.makedirs(OUT_DIR, exist_ok=True)
    shipped = []
    total = 0
    for name, cols in TABLES.items():
        assert len(name) <= 40, name
        shipped += cols
        assert int(df[cols].isna().sum().sum()) == 0
        assert df[cols].isin(range(LO, HI + 1)).all().all(), name
        long = df.melt(id_vars=["id", "cov_team"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert not long.duplicated(["id", "item"]).any()
        long = long[["id", "item", "resp", "cov_team"]]
        checks = run_qc(long, permitted_values=list(range(LO, HI + 1)))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")

    accounted = set(shipped) | set(LMX) | {"id", "cov_team"}
    assert accounted == set(df.columns), set(df.columns) ^ accounted
    print(f"skipped (leader-rated, 49 raters < 100): {LMX}")
    assert total == 14 * N_ROWS, total
    print(f"3 tables, {total} responses; all source columns accounted for")


if __name__ == "__main__":
    convert()
